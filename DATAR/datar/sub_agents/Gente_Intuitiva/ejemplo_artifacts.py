"""
Ejemplo de cómo usar artifacts en tu agente
Este es un archivo de referencia, no se ejecuta directamente
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
import google.genai.types as types

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Tool para guardar un registro de emojis como artifact
async def guardar_historia_emojis(context, emojis: str) -> str:
    """Guarda la historia de emojis en un artifact"""

    # Crear contenido de texto
    contenido = f"Historia de emojis:\n{emojis}\n\nFecha: {context.timestamp}"

    # Guardar como artifact
    artifact = types.Part.from_text(contenido)
    version = await context.save_artifact(
        filename="historia_emojis.txt",
        artifact=artifact
    )

    return f"Historia guardada (versión {version})"

# Tool para cargar la historia previa
async def cargar_historia_emojis(context) -> str:
    """Carga la historia de emojis guardada"""

    artifact = await context.load_artifact(filename="historia_emojis.txt")

    if artifact and artifact.text:
        return f"Historia previa:\n{artifact.text}"
    else:
        return "No hay historia previa guardada"

# Tool para guardar una imagen/visualización
async def guardar_visualizacion(context, imagen_bytes: bytes) -> str:
    """Guarda una visualización como imagen PNG"""

    artifact = types.Part.from_bytes(
        data=imagen_bytes,
        mime_type="image/png"
    )

    version = await context.save_artifact(
        filename="visualizacion_emociones.png",
        artifact=artifact
    )

    return f"Visualización guardada (versión {version})"

# Crear agente con tools
agente_con_artifacts = Agent(
    model='gemini-2.5-flash',
    name='diario_con_memoria',
    description='Agente que recuerda tu historia emocional a través de emojis',
    instruction='Analiza emojis y guarda la historia emocional del usuario',
    tools=[
        FunctionTool(guardar_historia_emojis),
        FunctionTool(cargar_historia_emojis),
        FunctionTool(guardar_visualizacion),
    ]
)

# Para usar artifacts con scope de usuario (persiste en todas las sesiones):
# filename="user:historia_emocional.txt"
