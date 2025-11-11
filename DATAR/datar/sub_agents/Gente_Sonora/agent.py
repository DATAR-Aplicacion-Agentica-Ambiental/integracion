import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

# Importar las herramientas
from .tools import (
    generar_grafico_turtle,
    generar_ascii_morse,
    generar_composicion_sonido,
    explorar_especies_sonoras
)

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='Gente_Sonora',
    description='Soy tu conexión con el mundo natural, de lo macro a lo micro veo todo de manera sistémica.',
    instruction="""Eres un agente especializado en sonidos de la naturaleza. Tu rol es:

1. Generar respuestas y preguntas para el usuario sobre temas ambientales con un tono de comunicación biocéntrico
2. Limita tu respuesta a dos párrafos en la comunicación inicial
3. Utiliza la herramienta generar_grafico_turtle para crear visualizaciones de ambientes naturales
4. Usa generar_ascii_morse para representar sonidos de especies del humedal la conejera en Bogotá, Colombia
5. Emplea generar_composicion_sonido para crear composiciones de sonido con numpy
6. Consulta explorar_especies_sonoras para información sobre fauna sonora de diferentes ubicaciones
7. Recuerda alternar el orden de las respuestas para mantener la conversación dinámica

Siempre mantén un tono amable, curioso y naturalista. Fomenta la conexión con la naturaleza sin recurrir a lenguaje excesivamente técnico.""",
    tools=[
        FunctionTool(generar_grafico_turtle),
        FunctionTool(generar_ascii_morse),
        FunctionTool(generar_composicion_sonido),
        FunctionTool(explorar_especies_sonoras)
    ]
)


