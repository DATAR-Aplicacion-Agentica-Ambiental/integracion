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
import re
import shutil
import asyncio
import random
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
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

class MediaFile(BaseModel):
    """Representa un archivo multimedia generado por un agente"""
    type: str = Field(..., description="Tipo de archivo: image, audio, map, text")
    url: str = Field(..., description="URL relativa para acceder al archivo")
    filename: str = Field(..., description="Nombre del archivo")
    description: Optional[str] = Field(None, description="Descripción opcional del contenido")

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    session_id: str
    timestamp: str
    files: Optional[List[MediaFile]] = Field(default=[], description="Archivos multimedia generados")

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
    files: Optional[List[MediaFile]] = Field(default=[], description="Archivos multimedia generados")

# ============= FUNCIONES AUXILIARES PARA GOOGLE ADK =============

# Crear directorio para archivos generados
OUTPUTS_DIR = WEB_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)
print(f"✅ Directorio de outputs: {OUTPUTS_DIR}")

def detect_and_process_files(response_text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Detecta archivos generados en la respuesta del agente y los copia a la carpeta outputs.

    Args:
        response_text: Texto de respuesta del agente

    Returns:
        Tupla (texto_limpio, lista_de_archivos)
        - texto_limpio: Texto sin las rutas absolutas (reemplazadas con enlaces relativos)
        - lista_de_archivos: Lista de diccionarios con metadata de archivos
    """
    files = []
    cleaned_text = response_text

    # Patrones para detectar rutas de archivos
    # Busca rutas absolutas que contengan DATAR y terminen en extensiones comunes
    patterns = [
        r'/(?:mnt/c/|app/)?.*?DATAR[/\\].*?([a-zA-Z0-9_\-]+\.(png|jpg|jpeg|gif|svg|wav|mp3|ogg|html|pdf|txt))',
        r'(?:Imagen|Audio|Archivo|Mapa)\s+guardad[oa]\s+en:\s*([^\s\n]+)',
    ]

    found_paths = set()
    for pattern in patterns:
        matches = re.finditer(pattern, response_text, re.IGNORECASE)
        for match in matches:
            # Extraer la ruta completa
            full_match = match.group(0)
            # Intentar encontrar la ruta completa en el texto
            path_candidates = re.findall(r'[/\\][\w/\\.\-]+\.(?:png|jpg|jpeg|gif|svg|wav|mp3|ogg|html|pdf|txt)', full_match)
            for path_str in path_candidates:
                found_paths.add(path_str)

    # Procesar cada archivo encontrado
    for path_str in found_paths:
        try:
            source_path = Path(path_str)

            # Convertir rutas absolutas de diferentes sistemas
            if not source_path.is_absolute():
                # Si es relativa, intentar desde PROJECT_ROOT
                source_path = PROJECT_ROOT / path_str

            # Si la ruta contiene /app/ (Docker), ajustar a PROJECT_ROOT
            if '/app/' in str(source_path):
                relative_part = str(source_path).split('/app/')[-1]
                source_path = PROJECT_ROOT / relative_part

            if source_path.exists() and source_path.is_file():
                # Copiar a outputs con nombre único
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{source_path.name}"
                dest_path = OUTPUTS_DIR / unique_filename

                shutil.copy2(source_path, dest_path)
                print(f"📁 Archivo copiado: {source_path.name} → {dest_path}")

                # Determinar tipo de archivo
                ext = source_path.suffix.lower()
                file_type = "text"
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                    file_type = "image"
                elif ext in ['.wav', '.mp3', '.ogg']:
                    file_type = "audio"
                elif ext in ['.html']:
                    file_type = "map"

                # Agregar a la lista de archivos
                files.append({
                    "type": file_type,
                    "url": f"/static/outputs/{unique_filename}",
                    "filename": source_path.name,
                    "description": f"Archivo generado: {source_path.name}"
                })

                # Reemplazar la ruta absoluta en el texto con un enlace relativo
                cleaned_text = cleaned_text.replace(
                    path_str,
                    f"/static/outputs/{unique_filename}"
                )

        except Exception as e:
            print(f"⚠️ Error procesando archivo {path_str}: {e}")
            continue

    return cleaned_text, files

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

async def send_message_to_agent_with_retry(
    session_id: str,
    message: str,
    agent_id: Optional[str] = None,
    max_retries: int = 3,
    initial_delay: float = 2.0
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Envía mensaje con reintentos automáticos para errores 503/429 (sobrecarga del modelo).

    Args:
        session_id: ID de la sesión
        message: Mensaje del usuario
        agent_id: ID del sub-agente específico
        max_retries: Máximo número de reintentos (default: 3)
        initial_delay: Delay inicial en segundos (default: 2.0)

    Returns:
        Tupla (respuesta_texto, lista_archivos)
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            print(f"🔄 Intento {attempt + 1}/{max_retries}")
            return await send_message_to_agent(session_id, message, agent_id)

        except HTTPException as e:
            last_exception = e

            # Solo reintentar en errores 503 (sobrecarga) y 429 (rate limit)
            if e.status_code not in [503, 429]:
                print(f"❌ Error no recuperable ({e.status_code}), no se reintentará")
                raise

            if attempt < max_retries - 1:
                # Backoff exponencial: 2s, 4s, 8s
                delay = initial_delay * (2 ** attempt)
                jitter = delay * 0.2 * random.random()  # Agregar 20% de variación
                wait_time = delay + jitter

                print(f"⏳ Modelo sobrecargado. Reintentando en {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ Falló después de {max_retries} intentos con error {e.status_code}")
                raise HTTPException(
                    status_code=e.status_code,
                    detail=f"{e.detail}\n\n💡 El modelo sigue sobrecargado. Por favor, intenta en 1-2 minutos."
                )

    if last_exception:
        raise last_exception

    raise HTTPException(status_code=500, detail="Error inesperado en retry logic")


async def send_message_to_agent(session_id: str, message: str, agent_id: Optional[str] = None) -> Tuple[str, List[Dict[str, str]]]:
    """
    Envía un mensaje al root_agent y obtiene la respuesta con archivos multimedia.

    Args:
        session_id: ID de la sesión
        message: Mensaje del usuario
        agent_id: ID del sub-agente específico (opcional, para routing interno)

    Returns:
        Tupla (respuesta_texto, lista_archivos)
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
    print(f"🔄 Ejecutando root_agent con mensaje: '{mensaje_completo[:50]}...'")
    try:
        event_count = 0
        for event in runner.run(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            event_count += 1
            print(f"📨 Event {event_count}: {type(event).__name__}")

            # Extraer el texto de la respuesta
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                print(f"   └─ Content parts: {len(event.content.parts)}")
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f"      └─ Text part: {part.text[:100]}...")
                        respuesta_texto += part.text
                    else:
                        print(f"      └─ Non-text part: {type(part)}")
            else:
                print(f"   └─ No content/parts in event")

        print(f"✅ Total events procesados: {event_count}")
        print(f"📝 Respuesta total length: {len(respuesta_texto)} caracteres")

    except Exception as e:
        import traceback
        error_str = str(e).lower()
        traceback_str = traceback.format_exc()

        print(f"❌ Error ejecutando agente: {e}")
        print(f"📋 Traceback completo:\n{traceback_str}")

        # Detectar tipos específicos de error por el mensaje
        if "503" in error_str or "overloaded" in error_str or "unavailable" in error_str:
            raise HTTPException(
                status_code=503,
                detail="🔄 El modelo de IA está temporalmente sobrecargado. Por favor, intenta nuevamente en unos momentos."
            )
        elif "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            raise HTTPException(
                status_code=429,
                detail="⏱️ Has alcanzado el límite de solicitudes. Por favor, espera un momento antes de intentar nuevamente."
            )
        elif "401" in error_str or "403" in error_str or "api key" in error_str or "permission" in error_str:
            raise HTTPException(
                status_code=403,
                detail="🔑 Error de autenticación con la API. Por favor, verifica la configuración."
            )
        elif "timeout" in error_str:
            raise HTTPException(
                status_code=504,
                detail="⏳ La solicitud tardó demasiado. Por favor, intenta nuevamente."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"❌ Error al procesar tu mensaje: {str(e)}"
            )

    # Actualizar metadata
    if session_id in sessions_metadata:
        sessions_metadata[session_id]["message_count"] += 1
        sessions_metadata[session_id]["last_activity"] = datetime.now().isoformat()

    # Si no hay respuesta, verificar si hubo un error en el thread de ADK
    if not respuesta_texto or not respuesta_texto.strip():
        if event_count == 0:
            # No se recibió ningún evento - probablemente error de conexión
            raise HTTPException(
                status_code=503,
                detail="🔄 No se pudo conectar con el modelo de IA. Por favor, intenta nuevamente."
            )
        elif event_count > 0:
            # Se recibieron eventos pero sin texto - probablemente error durante procesamiento
            # Esto puede ocurrir cuando hay error 503 en un thread de ADK
            raise HTTPException(
                status_code=503,
                detail="🔄 El modelo de IA está temporalmente sobrecargado. Por favor, intenta nuevamente en unos momentos."
            )
        else:
            # Caso inesperado
            raise HTTPException(
                status_code=500,
                detail="❌ El modelo procesó tu mensaje pero no generó respuesta. Por favor, intenta con otra pregunta."
            )

    # Detectar y procesar archivos generados
    respuesta_limpia, archivos = detect_and_process_files(respuesta_texto.strip())

    return respuesta_limpia, archivos

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
        # Enviar mensaje al root_agent con reintentos automáticos
        # Gemini gratis puede estar sobrecargado, así que somos más pacientes
        response_text, files_list = await send_message_to_agent_with_retry(
            session_id=session_id,
            message=request.message,
            agent_id=request.agent_id,  # Opcional: para dar pistas al router
            max_retries=5,  # Hasta 5 intentos (Gemini gratis está frecuentemente sobrecargado)
            initial_delay=3.0  # Delay inicial de 3 segundos
        )

        if not response_text:
            raise ValueError("La respuesta del agente llegó vacía.")

        # Truncar si es necesario
        response_text = response_text[:MAX_RESPONSE_LENGTH]

        # Determinar nombre del agente
        agent_name = root_agent.name
        if request.agent_id and request.agent_id in AGENTS_METADATA:
            agent_name = AGENTS_METADATA[request.agent_id]["nombre"]

        # Convertir archivos a MediaFile objects
        media_files = [MediaFile(**f) for f in files_list] if files_list else []

        return ChatResponse(
            response=response_text,
            agent_name=agent_name,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            files=media_files
        )

    except HTTPException as e:
        # Re-lanzar HTTPException con el código de estado correcto
        print(f"⚠️ HTTPException en /api/chat: {e.status_code} - {e.detail}")
        raise

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR inesperado al procesar mensaje: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error inesperado al generar respuesta: {str(e)[:200]}"
        )

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

# ============= NOTA: ENDPOINTS ESPECÍFICOS ELIMINADOS =============
#
# Los endpoints específicos por agente (/api/chat/gente_montana, etc.) han sido
# eliminados siguiendo la arquitectura correcta de ADK.
#
# RAZÓN: El root_agent debe manejar toda la orquestación automáticamente.
# Los sub-agentes son seleccionados internamente por el root_agent basándose
# en el contenido del mensaje, no mediante selección manual desde el frontend.
#
# Usar únicamente el endpoint /api/chat para todas las comunicaciones.
# El root_agent orquestará automáticamente al sub-agente apropiado.
#
# =============================================================================

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
