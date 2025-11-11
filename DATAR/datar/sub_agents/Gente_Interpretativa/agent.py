"""
Agente re-interpretativa que utiliza agentes paralelos y en bucle
para generar respuestas enriquecidas.
"""
import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent
from google.genai import types

from .utils import (
    leer_instrucciones, cambiar_respuesta_emojis, 
    cambiar_respuesta_textual, cambiar_respuesta_fusionadora
)

# ==========
# Agentes paralelos
# ==========

# Agente especializado en interpretar respuestas usando solo emojis
agente_interprete_emojis = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='GenteInterpreteDeEmojis',
    description=(
        'Recibe una interacción y retorna una '
        'interpretación con sólo emojis'
    ),
    instruction=leer_instrucciones("ins_emoji_agent.md"),
    generate_content_config=types.GenerateContentConfig(
        temperature=1.8
    ),
    after_model_callback=cambiar_respuesta_emojis
)

# Agente especializado en responder con narrativas, 
# dando su perspectiva en texto invitando a interpretar 
# y generando preguntas.
agente_interprete_textual = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='GenteInterpreteDeTexto',
    description=(
        'Recibe una interacción y retorna una '
        'interpretación invitando a interpretar su respuesta e '
        'generando preguntas a su interlocutor.'
    ),
    instruction=leer_instrucciones("ins_agente_textual.md"),
    generate_content_config=types.GenerateContentConfig(
        temperature=1.6
    ),
    after_model_callback=cambiar_respuesta_textual
)

# ==========
# Agentes en bucle
# ==========

# Agente que ejecuta los agentes en paralelo
agente_paralelizador = ParallelAgent(
    name='GenteParalelizador',
    description='Corre múltiples agentes en paralelo.',
    sub_agents=[agente_interprete_emojis, agente_interprete_textual],
)

# Agente que combina las respuestas de los agentes paralelos
agente_fusionador = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='GenteFusionador',
    description=(
        'Recibe las respuestas de múltiples agentes '
        'y las combina en una sola respuesta coherente.'
    ),
    instruction=leer_instrucciones("ins_merger_agent.md"),
    after_model_callback=cambiar_respuesta_fusionadora
)

# Agente que crea un bucle de interpretación paralela 
# y reinterpretación fusionadora.
agente_bucle = LoopAgent(
    name="GenteBucle",
    sub_agents=[agente_paralelizador, agente_fusionador],
    max_iterations=2,
    description="Crea un bucle de interpretación y reinterpretación",
)

# =======
# Agente de interacción
# =======

# Definir un agente normal que interactúe con lxs usuarixs
# y les defina una forma de interactuar
agente_re_interpretativa = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='GenteReInterpretativa',
    description=(
        'Un asistente presto a ayudar e informar '
        'con datos ambientales de Bogotá'
    ),
    instruction=leer_instrucciones("ins_re_interpretativa.md"),
)

# Agente secuencial que primero ejecuta los agentes 
# en paralelo y luego combina sus respuestas
agente_interpretativa_secuencial = SequentialAgent(
    name="GenteInterpretativa",
    sub_agents=[agente_bucle, agente_re_interpretativa],
    description="Coordina agentes en paralelo y luego combina sus respuestas."
)

# Agente raíz que se utilizará para interactuar
root_agent = agente_interpretativa_secuencial