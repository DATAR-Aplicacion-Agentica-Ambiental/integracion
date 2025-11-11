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

# Importar el agente raíz y metadata desde la nueva estructura
from DATAR.datar import root_agent, AGENTS_METADATA
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, Content

# Validar que root_agent está inicializado
if not root_agent:
    raise RuntimeError("❌ root_agent no pudo ser inicializado. Verifica tus API keys.")

print(f"✅ root_agent inicializado: {root_agent.name}")
print(f"   Sub-agentes disponibles: {len(root_agent.sub_agents) if hasattr(root_agent, 'sub_agents') else 0}")

# ============= GESTIÓN DE SESIONES CON GOOGLE ADK =============

# Crear runner para el root_agent
runner = InMemoryRunner(agent=root_agent)
print(f"✅ Runner inicializado para {root_agent.name}")

# Almacén de sesiones por usuario/session_id
sessions_store: Dict[str, Any] = {}  # Sesiones de Google ADK
sessions_metadata: Dict[str, Dict[str, Any]] = {}  # Metadata adicional (timestamps, etc.)

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

# ============= FUNCIONES AUXILIARES PARA GOOGLE ADK =============

async def get_or_create_session(session_id: str) -> Any:
    """
    Obtiene o crea una sesión de Google ADK para el ID dado.

    Args:
        session_id: ID de la sesión

    Returns:
        Objeto de sesión de Google ADK
    """
    if session_id not in sessions_store:
        # Crear nueva sesión con Google ADK
        try:
            session = await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id="default_user"
            )
            sessions_store[session_id] = session
            sessions_metadata[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0
            }
            print(f"📝 Sesión creada: {session_id}")
        except Exception as e:
            print(f"❌ Error creando sesión: {e}")
            raise RuntimeError(f"Error al crear sesión: {str(e)}")

    # Actualizar última actividad
    if session_id in sessions_metadata:
        sessions_metadata[session_id]["last_activity"] = datetime.now().isoformat()

    return sessions_store[session_id]

async def send_message_to_agent(session_id: str, message: str, agent_id: Optional[str] = None) -> str:
    """
    Envía un mensaje al root_agent y obtiene la respuesta.

    Args:
        session_id: ID de la sesión
        message: Mensaje del usuario
        agent_id: ID del sub-agente específico (opcional, para routing interno)

    Returns:
        Respuesta del agente como texto
    """
    session = await get_or_create_session(session_id)

    # Preparar el mensaje
    # Si se especifica un agent_id, podemos incluirlo en el mensaje para routing
    mensaje_completo = message
    if agent_id:
        # El root_agent decidirá qué sub-agente usar basándose en el mensaje
        # Podemos darle una pista incluyendo el nombre del agente
        agent_meta = AGENTS_METADATA.get(agent_id)
        if agent_meta:
            mensaje_completo = f"[Dirigido a {agent_meta['nombre']}]: {message}"

    # Crear contenido del mensaje
    content = Content(parts=[Part(text=mensaje_completo)], role="user")

    # Ejecutar el agente y recolectar respuesta
    respuesta_texto = ""
    try:
        for event in runner.run(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            # Extraer el texto de la respuesta
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        respuesta_texto += part.text
    except Exception as e:
        print(f"❌ Error ejecutando agente: {e}")
        raise RuntimeError(f"Error al ejecutar el agente: {str(e)}")

    # Actualizar metadata
    if session_id in sessions_metadata:
        sessions_metadata[session_id]["message_count"] += 1
        sessions_metadata[session_id]["last_activity"] = datetime.now().isoformat()

    # Si no hay respuesta, usar mensaje por defecto
    if not respuesta_texto or not respuesta_texto.strip():
        respuesta_texto = f"[{root_agent.name}] procesó tu mensaje, pero no generó una respuesta de texto."

    return respuesta_texto.strip()

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
    """
    Envía un mensaje al root_agent y recibe una respuesta.
    El root_agent automáticamente dirigirá el mensaje al sub-agente apropiado.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    if len(request.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"El mensaje no puede exceder {MAX_MESSAGE_LENGTH} caracteres"
        )

    # Generar session_id si no se proporciona
    session_id = request.session_id or str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    try:
        # Enviar mensaje al root_agent usando Google ADK
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=request.agent_id  # Opcional: para dar pistas al router
        )

        if not response_text:
            raise ValueError("La respuesta del agente llegó vacía.")

        # Truncar si es necesario
        response_text = response_text[:MAX_RESPONSE_LENGTH]

        # Determinar nombre del agente
        agent_name = root_agent.name
        if request.agent_id and request.agent_id in AGENTS_METADATA:
            agent_name = AGENTS_METADATA[request.agent_id]["nombre"]

        return ChatResponse(
            response=response_text,
            agent_name=agent_name,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR al procesar mensaje: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {str(e)}")

@app.get("/api/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """Lista todas las sesiones activas"""
    sessions = []
    for session_id, metadata in sessions_metadata.items():
        sessions.append(SessionInfo(
            session_id=session_id,
            created_at=metadata["created_at"],
            last_activity=metadata["last_activity"],
            message_count=metadata["message_count"]
        ))
    return sessions

@app.get("/api/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """
    Obtiene el historial completo de una sesión desde Google ADK.
    Nota: El historial se mantiene en el runner de Google ADK.
    """
    if session_id not in sessions_store:
        return SessionHistoryResponse(
            session_id=session_id,
            messages=[],
            created_at="",
            message_count=0
        )

    try:
        session = sessions_store[session_id]
        metadata = sessions_metadata.get(session_id, {})

        # Obtener historial desde Google ADK
        history = await runner.session_service.get_history(
            user_id=session.user_id,
            session_id=session.id
        )

        # Convertir el historial de Google ADK a formato de mensajes
        messages = []
        if history and hasattr(history, 'turns'):
            for turn in history.turns:
                if hasattr(turn, 'user_message') and turn.user_message:
                    messages.append({
                        "role": "user",
                        "content": turn.user_message.parts[0].text if turn.user_message.parts else "",
                        "timestamp": metadata.get("last_activity", "")
                    })
                if hasattr(turn, 'model_message') and turn.model_message:
                    messages.append({
                        "role": "assistant",
                        "content": turn.model_message.parts[0].text if turn.model_message.parts else "",
                        "timestamp": metadata.get("last_activity", "")
                    })

        return SessionHistoryResponse(
            session_id=session_id,
            messages=messages,
            created_at=metadata.get("created_at", ""),
            message_count=len(messages)
        )
    except Exception as e:
        print(f"⚠️ Error obteniendo historial de sesión: {e}")
        return SessionHistoryResponse(
            session_id=session_id,
            messages=[],
            created_at="",
            message_count=0
        )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Elimina una sesión específica"""
    deleted = False
    if session_id in sessions_store:
        del sessions_store[session_id]
        deleted = True
    if session_id in sessions_metadata:
        del sessions_metadata[session_id]
        deleted = True

    if deleted:
        return {"message": f"Sesión {session_id} eliminada exitosamente"}
    return {"message": f"Sesión {session_id} no encontrada"}

@app.post("/api/select-agent")
async def select_agent(request: SelectAgentRequest):
    """
    Retorna información sobre un agente específico.
    Nota: Con el nuevo sistema, el root_agent maneja el routing automáticamente.
    Este endpoint se mantiene por compatibilidad con el frontend.
    """
    if request.agent_id not in AGENTS_METADATA:
        raise HTTPException(
            status_code=404,
            detail=f"Agente '{request.agent_id}' no encontrado. Agentes disponibles: {', '.join(AGENTS_METADATA.keys())}"
        )

    agent_meta = AGENTS_METADATA[request.agent_id]
    mensaje_bienvenida = f"¡Hola! Soy {agent_meta['nombre']}. {agent_meta['descripcion']}. ¿En qué puedo ayudarte?"

    return {
        "exitoso": True,
        "agente": agent_meta["nombre"],
        "agente_id": request.agent_id,
        "descripcion": agent_meta["descripcion"],
        "mensaje": mensaje_bienvenida,
        "color": agent_meta["color"],
        "emoji": agent_meta.get("emoji", "🤖")
    }

# ============= ENDPOINTS ESPECÍFICOS POR AGENTE =============

@app.post(
    "/api/chat/gente_montana",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🏔️ Chat con Gente Montaña"
)
async def chat_gente_montana(request: SimpleMessageRequest):
    """Chatea directamente con Gente Montaña - Cerros Orientales"""
    agent_id = "gente_montana"
    session_id = str(uuid.uuid4())  # Cada llamada directa usa una sesión única

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/gente_pasto",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🌿 Chat con Gente Pasto"
)
async def chat_gente_pasto(request: SimpleMessageRequest):
    """Chatea con Gente Pasto - Especialista en vegetación"""
    agent_id = "gente_pasto"
    session_id = str(uuid.uuid4())

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/gente_intuitiva",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="📔 Chat con Gente Intuitiva"
)
async def chat_gente_intuitiva(request: SimpleMessageRequest):
    """Chatea con Gente Intuitiva - Visualizaciones emocionales"""
    agent_id = "gente_intuitiva"
    session_id = str(uuid.uuid4())

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/gente_interpretativa",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🥒 Chat con Gente Interpretativa"
)
async def chat_gente_interpretativa(request: SimpleMessageRequest):
    """Chatea con Gente Interpretativa - Pipeline interpretativo"""
    agent_id = "gente_interpretativa"
    session_id = str(uuid.uuid4())

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/gente_bosque",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🌲 Chat con Gente Bosque"
)
async def chat_gente_bosque(request: SimpleMessageRequest):
    """Chatea con Gente Bosque - Ecosistemas forestales con MCP"""
    agent_id = "gente_bosque"
    session_id = str(uuid.uuid4())

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/gente_sonora",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🎵 Chat con Gente Sonora"
)
async def chat_gente_sonora(request: SimpleMessageRequest):
    """Chatea con Gente Sonora - Representaciones biocéntricas"""
    agent_id = "gente_sonora"
    session_id = str(uuid.uuid4())

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post(
    "/api/chat/gente_horaculo",
    response_model=AgentResponse,
    tags=["Agentes Específicos"],
    summary="🔮 Chat con Gente Horáculo"
)
async def chat_gente_horaculo(request: SimpleMessageRequest):
    """Chatea con Gente Horáculo - Oráculo ambiental"""
    agent_id = "gente_horaculo"
    session_id = str(uuid.uuid4())

    try:
        response_text = await send_message_to_agent(
            session_id=session_id,
            message=request.message,
            agent_id=agent_id
        )
        return AgentResponse(
            response=response_text,
            agent_name=AGENTS_METADATA[agent_id]["nombre"],
            agent_id=agent_id
        )
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
