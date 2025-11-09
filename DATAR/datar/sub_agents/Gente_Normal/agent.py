from google.adk.agents.llm_agent import Agent
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent
from google.genai import types

from .utils import leer_instrucciones

# ==========
# Agentes paralelos
# ==========

# Agente especializado en interpretar respuestas usando solo emojis
agente_interprete_emojis = Agent(
    model='gemini-2.5-flash',
    name='GenteInterpreteDeEmojis',
    description=(
        'Recibe una interacción y retorna una '
        'interpretación con sólo emojis'
    ),
    instruction=leer_instrucciones("ins_emoji_agent.md"),
    output_key='respuesta_emojis',
    generate_content_config=types.GenerateContentConfig(
        temperature=1.8
    ),
)

# Agente especializado en responder con narrativas, 
# dando su perspectiva en texto invitando a interpretar 
# y generando preguntas.
agente_interprete_textual = Agent(
    model='gemini-2.5-flash',
    name='GenteInterpreteDeTexto',
    description=(
        'Recibe una interacción y retorna una '
        'interpretación invitando a interpretar su respuesta e '
        'generando preguntas a su interlocutor.'
    ),
    instruction=leer_instrucciones("ins_agente_textual.md"),
    output_key='respuesta_textual',
    generate_content_config=types.GenerateContentConfig(
        temperature=1.6
    ),
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
    model='gemini-2.5-flash',
    name='GenteFusionador',
    description=(
        'Recibe las respuestas de múltiples agentes '
        'y las combina en una sola respuesta coherente.'
    ),
    instruction=leer_instrucciones("ins_merger_agent.md"),
    output_key='respuesta_fusionadora',
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
agente_re_interpretativo = Agent(
    model='gemini-2.5-flash',
    name='GenteReInterpretativo',
    description=(
        'Un asistente presto a ayudar e informar '
        'con datos ambientales de Bogotá'
    ),
    instruction=leer_instrucciones("ins_re_interpretativo.md"),
    output_key='normal_response',
)

# Agente secuencial que primero ejecuta los agentes 
# en paralelo y luego combina sus respuestas
agente_encauzador_secuencial = SequentialAgent(
    name="GenteEncauzador",
    sub_agents=[agente_bucle, agente_re_interpretativo],
    description="Coordina agentes en paralelo y luego combina sus respuestas."
)

# Agente raíz que se utilizará para interactuar
root_agent = agente_encauzador_secuencial