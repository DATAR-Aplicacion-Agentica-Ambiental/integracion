"""
Servidor web personalizado con interceptor de comandos
Este servidor detecta comandos especiales ANTES de pasar mensajes al agente
"""
import asyncio
import re
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runner import run
from google.adk.sessions import InMemorySession
import google.genai.types as types

# Importar el agente y funciones
from datar_a_gente.agent import _internal_agent, crear_visualizacion_rio, extraer_emojis, detectar_comando_imagen

app = FastAPI()

# Almacenamiento de emojis por sesión
_sesiones_emojis = {}


async def procesar_mensaje_con_interceptor(session_id: str, mensaje: str, context):
    """
    Intercepta el mensaje y detecta comandos antes de pasar al agente
    """
    # Inicializar lista de emojis para esta sesión si no existe
    if session_id not in _sesiones_emojis:
        _sesiones_emojis[session_id] = []

    # Extraer emojis del mensaje
    emojis_mensaje = extraer_emojis(mensaje)
    if emojis_mensaje:
        _sesiones_emojis[session_id].extend(emojis_mensaje)

    # Detectar comando de imagen
    if detectar_comando_imagen(mensaje):
        if not _sesiones_emojis[session_id] and not emojis_mensaje:
            return "⚠️ No he detectado emojis en la conversación. Envíame algunos emojis primero y luego usa el comando para crear la imagen."

        # Usar emojis almacenados
        emojis_para_visualizar = _sesiones_emojis[session_id] if _sesiones_emojis[session_id] else emojis_mensaje
        emojis_str = " ".join(emojis_para_visualizar)

        # Llamar directamente a la herramienta
        resultado = await crear_visualizacion_rio(context, emojis_str)

        # Limpiar emojis después de crear imagen
        _sesiones_emojis[session_id] = []

        return resultado

    # Si no es comando, pasar al agente normal
    response = await _internal_agent.process(context, mensaje)
    return response


@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Endpoint principal de chat
    """
    data = await request.json()
    mensaje = data.get("mensaje", "")
    session_id = data.get("session_id", "default")

    # Crear contexto simulado (en producción usar el real de ADK)
    class MockContext:
        async def save_artifact(self, filename, artifact):
            # Aquí iría la lógica real de guardar
            return 1

    context = MockContext()

    # Procesar mensaje con interceptor
    respuesta = await procesar_mensaje_con_interceptor(session_id, mensaje, context)

    return JSONResponse({"respuesta": respuesta})


@app.get("/")
async def root():
    return {
        "mensaje": "Servidor personalizado de Diario Intuitivo",
        "comandos": [
            "/imagen", "!imagen", "visualiza", "crea imagen", "genera imagen"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Servidor personalizado iniciando en http://localhost:8000")
    print("📝 Comandos disponibles: /imagen, !imagen, visualiza, crea imagen")
    print("\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
