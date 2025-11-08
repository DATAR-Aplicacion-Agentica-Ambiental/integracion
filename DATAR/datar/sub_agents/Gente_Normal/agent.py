from google.adk.agents.llm_agent import Agent
from google.adk.agents import ParallelAgent, SequentialAgent
from google.genai import types

from .utils import leer_instrucciones

# Definición de los agentes individuales
agente_normal = Agent(
    model='gemini-2.5-flash',
    name='GenteNormal',
    description=(
        'Un asistente presto a ayudar e informar '
        'con datos ambientales de Bogotá'
    ),
    instruction=leer_instrucciones(),
    output_key='normal_response',
)

# Agente especializado en interpretar respuestas usando solo emojis
agente_interprete_emojis = Agent(
    model='gemini-2.5-flash',
    name='GenteInterpreteDeEmojis',
    description=(
        'Recibe la solicitud del usuario y retorna una '
        'interpretación con sólo emojis'
    ),
    instruction=leer_instrucciones("ins_emoji_agent.md"),
    output_key='emoji_response',
    generate_content_config=types.GenerateContentConfig(
        temperature=1.6
    )
)

# Agente que ejecuta los agentes en paralelo
agente_paralelizador = ParallelAgent(
    name='GenteParalelizador',
    description='Corre múltiples agentes en paralelo.',
    sub_agents=[agente_normal, agente_interprete_emojis],
)

# Agente que combina las respuestas de los agentes paralelos
agente_fusionador = Agent(
    model='gemini-2.5-flash',
    name='GenteFusionador',
    description=(
        'Recibe las respuestas de múltiples agentes '
        'y las combina en una sola respuesta coherente.'
    ),
    instruction=leer_instrucciones("ins_merger_agent.md"),
)

# Agente secuencial que primero ejecuta los agentes 
# en paralelo y luego combina sus respuestas
agente_encauzador_secuencial = SequentialAgent(
    name="GenteEncauzador",
    sub_agents=[agente_paralelizador, agente_fusionador],
    description="Coordina agentes en paralelo y luego combina sus respuestas."
)

# Agente raíz que se utilizará para interactuar
root_agent = agente_encauzador_secuencial