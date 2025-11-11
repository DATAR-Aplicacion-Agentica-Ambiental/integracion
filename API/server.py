"""
Servidor FastAPI para DATAR - Proyecto Integrado
Sistema Agéntico Ambiental - Estructura Ecológica Principal de Bogotá

Integra:
- Agentes actualizados de adk-prueba-main
- Orquestador para gestión de agentes
- Endpoints específicos por cada agente
- Interfaz web estática
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from litellm import completion
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Configurar path para importar DATAR y orchestrator
API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración
from config import (
    API_HOST, API_PORT, ALLOWED_ORIGINS,
    MAX_MESSAGE_LENGTH, MAX_RESPONSE_LENGTH,
    OPENROUTER_API_KEY, GOOGLE_API_KEY, DATAR_DIR, WEB_DIR
)

# Importar el agente raíz y metadata
from DATAR import root_agent, AGENTS_METADATA

# Importar el orquestador
from orchestrator import get_orchestrator

# Validar que root_agent está inicializado
if not root_agent:
    raise RuntimeError("❌ root_agent no pudo ser inicializado. Verifica tus API keys.")

print(f"✅ root_agent inicializado: {root_agent.name}")

# ============= GESTIÓN DE SESIONES =============

sessions_store: Dict[str, Dict[str, Any]] = {}

# Inicializar el orquestador de agentes
orchestrator = get_orchestrator()

# ============= APLICACIÓN FASTAPI =============

app = FastAPI(
    title="DATAR API - Proyecto Integrado",
    description="Sistema Agéntico para la Estructura Ecológica Principal de Bogotá",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
    print(f"✅ Sirviendo frontend desde {WEB_DIR}")
else:
    print(f"⚠️  Directorio WEB no encontrado - Frontend no disponible")

# ============= MODELOS PYDANTIC =============

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agent_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    session_id: str
    timestamp: str

class AgentInfo(BaseModel):
    id: str
    nombre: str
    descripcion: str
    color: str
    emoji: str

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_activity: str
    message_count: int

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    message_count: int

class SelectAgentRequest(BaseModel):
    agent_id: str

class SimpleMessageRequest(BaseModel):
    """Modelo simple para mensajes a agentes específicos"""
    message: str = Field(
        ...,
        description="Mensaje de texto para enviar al agente",
        example="hola"
    )

class AgentResponse(BaseModel):
    """Respuesta de un agente específico"""
    response: str = Field(..., description="Respuesta del agente")
    agent_name: str = Field(..., description="Nombre del agente que respondió")
    agent_id: str = Field(..., description="ID del agente")

# ============= FUNCIONES AUXILIARES =============

def _as_serializable_dict(obj: Any) -> Any:
    """Convierte objetos con métodos de serialización en dicts simples."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass
    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj

def _flatten_content(content: Any) -> str:
    """Normaliza contenido potencialmente estructurado a texto plano."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                parts.append(str(text))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)

def _resolve_litellm_params() -> Dict[str, Any]:
    """Obtiene la configuración del modelo LiteLLM."""
    params: Dict[str, Any] = {}

    agent_model = getattr(root_agent, "model", None)
    if agent_model is not None:
        for attr in ("model", "api_key", "api_base", "temperature", "max_tokens"):
            value = getattr(agent_model, attr, None)
            if value is not None:
                key = "model" if attr == "model" else attr
                params[key] = value

    if "model" not in params:
        params["model"] = "openrouter/minimax/minimax-m2:free"

    if "api_key" not in params:
        params["api_key"] = OPENROUTER_API_KEY

    if "api_base" not in params:
        params["api_base"] = "https://openrouter.ai/api/v1"

    return {k: v for k, v in params.items() if v is not None}

def _build_conversation(session_id: str) -> List[Dict[str, str]]:
    """Construye el historial de mensajes en formato compatible con LiteLLM."""
    conversation: List[Dict[str, str]] = []

    system_instruction = getattr(root_agent, "instruction", None)
    if system_instruction:
        conversation.append({"role": "system", "content": system_instruction})

    session_data = sessions_store.get(session_id)
    if session_data and session_data.get("messages"):
        for msg in session_data["messages"]:
            if msg.get("role") in ("user", "assistant"):
                conversation.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

    return conversation

def _extract_text_from_response(model_response: Any) -> str:
    """Extrae el texto de la primera respuesta del modelo LiteLLM."""
    if model_response is None:
        return "Sin respuesta del modelo"

    if isinstance(model_response, str):
        text = model_response.strip()
        return text if text else "Sin respuesta del modelo"

    response_obj = _as_serializable_dict(model_response)
    choices = []

    if isinstance(response_obj, dict):
        choices = response_obj.get("choices") or []
    else:
        choices = getattr(model_response, "choices", []) or []

    if not choices and hasattr(model_response, "model_dump"):
        try:
            dumped = model_response.model_dump()
            choices = dumped.get("choices", []) if isinstance(dumped, dict) else []
        except Exception:
            pass

    if not choices:
        if hasattr(model_response, "content"):
            content = getattr(model_response, "content", "")
            if content:
                return _flatten_content(content).strip()
        return str(model_response).strip()

    first_choice = choices[0]
    first_choice = _as_serializable_dict(first_choice)

    if isinstance(first_choice, dict):
        message = first_choice.get("message")
        message = _as_serializable_dict(message)
        if isinstance(message, dict):
            content = message.get("content")
            if content:
                return _flatten_content(content).strip()

        fallback_text = first_choice.get("text") or first_choice.get("content")
        if fallback_text:
            return _flatten_content(fallback_text).strip()

    if hasattr(model_response, "content") and model_response.content:
        return _flatten_content(model_response.content).strip()

    if hasattr(model_response, "text") and model_response.text:
        return _flatten_content(model_response.text).strip()

    return "Sin respuesta del modelo"

async def _generate_agent_reply(session_id: str) -> str:
    """Invoca el agente de forma no bloqueante y retorna el texto de respuesta."""

    # Detectar si estamos usando Gemini nativo o LiteLLM
    agent_model = getattr(root_agent, "model", None)
    is_native_gemini = isinstance(agent_model, str)

    if is_native_gemini:
        # Usar Google Genai API directamente
        return await _generate_reply_with_gemini(session_id, agent_model)
    else:
        # Usar LiteLLM
        return await _generate_reply_with_litellm(session_id)

async def _generate_reply_with_gemini(session_id: str, model_name: str) -> str:
    """Genera respuesta usando Google Genai API directamente."""
    from google import genai
    from google.genai import types
    from google.genai.errors import ClientError, ServerError

    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY no configurada para usar Gemini nativo.")

    client = genai.Client(api_key=GOOGLE_API_KEY)
    messages = _build_conversation(session_id)

    # Convertir formato para Gemini
    contents = []
    system_instruction = None

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
            continue
        contents.append(types.Content(
            role="user" if msg["role"] == "user" else "model",
            parts=[types.Part(text=msg["content"])]
        ))

    try:
        response = await run_in_threadpool(
            client.models.generate_content,
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=1.0,
            )
        )

        if response and response.text:
            return response.text.strip()
        return "Sin respuesta del modelo"

    except ClientError as e:
        error_code = e.args[0] if e.args else 0
        if error_code == 429:
            raise RuntimeError("Cuota de Google Gemini excedida. Espera o verifica tu cuota.")
        elif error_code == 404:
            raise RuntimeError(f"Modelo '{model_name}' no encontrado.")
        elif error_code == 503:
            raise RuntimeError(f"Modelo '{model_name}' sobrecargado. Intenta de nuevo.")
        else:
            raise RuntimeError(f"Error de Google Gemini API ({error_code}): {str(e)}")
    except ServerError as e:
        raise RuntimeError(f"Error del servidor de Google. Intenta de nuevo.")

async def _generate_reply_with_litellm(session_id: str) -> str:
    """Genera respuesta usando LiteLLM."""
    params = _resolve_litellm_params()

    if not params.get("model"):
        raise RuntimeError("Modelo de LiteLLM no configurado.")

    if not params.get("api_key"):
        raise RuntimeError("No se encontró una API key válida para LiteLLM.")

    messages = _build_conversation(session_id)

    raw_response = await run_in_threadpool(
        completion,
        messages=messages,
        **params,
    )

    response_text = _extract_text_from_response(raw_response)
    return response_text.strip()

# ============= ENDPOINTS GENERALES =============

@app.get("/")
async def root():
    """Endpoint raíz - Información del API"""
    return {
        "nombre": "DATAR API - Proyecto Integrado",
        "descripcion": "Sistema Agéntico para la Estructura Ecológica Principal de Bogotá",
        "version": "2.0.0",
        "agente_principal": root_agent.name,
        "endpoints": {
            "raiz": "/",
            "salud": "/health",
            "agentes": "/api/agents",
            "chat": "/api/chat",
            "sesiones": "/api/sessions",
            "docs": "/docs",
            "frontend": "/static/index.html"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "message": "DATAR está operativo",
        "agente_activo": root_agent.name,
        "version": "2.0.0"
    }

@app.get("/api/agents", response_model=List[AgentInfo])
async def list_agents():
    """Lista todos los agentes disponibles"""
    agents_list = []

    for agent_id, meta in AGENTS_METADATA.items():
        agents_list.append(AgentInfo(
            id=agent_id.replace('_', '_'),  # Normalize IDs
            nombre=meta['nombre'],
            descripcion=meta['descripcion'],
            color=meta['color'],
            emoji=meta.get('emoji', '🤖')
        ))

    return agents_list

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Envía un mensaje al agente y recibe una respuesta."""

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    if len(request.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"El mensaje no puede exceder {MAX_MESSAGE_LENGTH} caracteres"
        )

    # Usar orquestador si se especifica agent_id
    target_agent_id = request.agent_id or (orchestrator.obtener_agente_activo() or {}).get('id')

    if target_agent_id:
        try:
            respuesta_orq = await orchestrator.procesar_mensaje(
                mensaje=request.message,
                agente_id=target_agent_id
            )

            if respuesta_orq.get("exitoso"):
                return ChatResponse(
                    response=respuesta_orq['mensaje'],
                    agent_name=respuesta_orq['agente'],
                    session_id=request.session_id or str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"⚠️  Error en orquestador: {e}, usando root_agent")

    # Fallback: usar root_agent
    session_id = request.session_id or str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    if session_id not in sessions_store:
        sessions_store[session_id] = {
            "created_at": timestamp,
            "messages": [],
            "last_activity": timestamp
        }

    sessions_store[session_id]["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": timestamp
    })

    try:
        response_text = await _generate_agent_reply(session_id)
        if not response_text:
            raise ValueError("La respuesta del agente llegó vacía.")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR en _generate_agent_reply: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {str(e)}")

    assistant_timestamp = datetime.now().isoformat()

    sessions_store[session_id]["messages"].append({
        "role": "assistant",
        "content": response_text,
        "timestamp": assistant_timestamp
    })
    sessions_store[session_id]["last_activity"] = assistant_timestamp

    response_text = response_text[:MAX_RESPONSE_LENGTH]

    return ChatResponse(
        response=response_text,
        agent_name=root_agent.name,
        session_id=session_id,
        timestamp=assistant_timestamp
    )

@app.get("/api/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """Lista todas las sesiones activas"""
    sessions = []
    for session_id, data in sessions_store.items():
        sessions.append(SessionInfo(
            session_id=session_id,
            created_at=data["created_at"],
            last_activity=data["last_activity"],
            message_count=len(data["messages"])
        ))
    return sessions

@app.get("/api/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """Obtiene el historial completo de una sesión"""
    if session_id not in sessions_store:
        return SessionHistoryResponse(
            session_id=session_id,
            messages=[],
            created_at="",
            message_count=0
        )

    session_data = sessions_store[session_id]
    return SessionHistoryResponse(
        session_id=session_id,
        messages=session_data["messages"],
        created_at=session_data["created_at"],
        message_count=len(session_data["messages"])
    )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Elimina una sesión específica"""
    if session_id in sessions_store:
        del sessions_store[session_id]
        return {"message": f"Sesión {session_id} eliminada exitosamente"}
    return {"message": f"Sesión {session_id} no encontrada"}

@app.post("/api/select-agent")
async def select_agent(request: SelectAgentRequest):
    """Selecciona un agente específico para la conversación"""
    try:
        resultado = orchestrator.seleccionar_agente(request.agent_id)
        if not resultado.get("exitoso"):
            raise HTTPException(status_code=404, detail=resultado.get("error"))
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al seleccionar agente: {str(e)}")

# ============= ENDPOINTS ESPECÍFICOS POR AGENTE =============

@app.post(
    "/api/chat/gente_montana",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🏔️ Chat con Gente Montaña"
)
async def chat_gente_montana(request: SimpleMessageRequest):
    """Chatea directamente con Gente Montaña - Cerros Orientales"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="gente_montana"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="gente_montana"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/pasto_bogotano",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🌿 Chat con PastoBogotano"
)
async def chat_pasto_bogotano(request: SimpleMessageRequest):
    """Chatea con PastoBogotano - Especialista en vegetación"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="pasto_bogotano"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="pasto_bogotano"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/diario_intuitivo",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="📔 Chat con Diario Intuitivo"
)
async def chat_diario_intuitivo(request: SimpleMessageRequest):
    """Chatea con Diario Intuitivo - Visualizaciones emocionales"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="diario_intuitivo"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="diario_intuitivo"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/guatila_m",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🥒 Chat con GuatilaM"
)
async def chat_guatila_m(request: SimpleMessageRequest):
    """Chatea con GuatilaM - Pipeline paralelo con emojis"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="guatila_m"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="guatila_m"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/agente_bosque",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🌲 Chat con Agente Bosque"
)
async def chat_agente_bosque(request: SimpleMessageRequest):
    """Chatea con Agente Bosque - Ecosistemas forestales con MCP"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="agente_bosque"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="agente_bosque"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/agente_sonido",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🎵 Chat con Agente Sonido"
)
async def chat_agente_sonido(request: SimpleMessageRequest):
    """Chatea con Agente Sonido - Representaciones biocéntricas"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="agente_sonido"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="agente_sonido"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/horaculo",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🔮 Chat con Horáculo"
)
async def chat_horaculo(request: SimpleMessageRequest):
    """Chatea con Horáculo - Oráculo ambiental"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="horaculo"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="horaculo"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Servir frontend
@app.get("/static/index.html")
async def serve_frontend():
    """Sirve el frontend"""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend no encontrado")

# ============= PUNTO DE ENTRADA =============

if __name__ == "__main__":
    print("🌱 Iniciando DATAR - Sistema Agéntico Ambiental Integrado")
    print(f"📍 Agente Principal: {root_agent.name}")
    print(f"🌐 Servidor: http://{API_HOST}:{API_PORT}")
    print(f"📚 Documentación: http://localhost:{API_PORT}/docs")
    if WEB_DIR.exists():
        print(f"🎨 Frontend: http://localhost:{API_PORT}/static/index.html")

    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        reload=False
    )
