from google.adk.agents.llm_agent import Agent
from google.adk.agents import ParallelAgent, SequentialAgent
from google.genai import types

from .utils import leer_instrucciones

# Definición de los agentes individuales
normal_agent = Agent(
    model='gemini-2.5-flash',
    name='normal_agent',
    description=(
        'Un asistente presto a ayudar e informar '
        'con datos ambientales de Bogotá'
    ),
    instruction=leer_instrucciones(),
    output_key='normal_response',
)

# Agente especializado en interpretar respuestas usando solo emojis
emoji_agent = Agent(
    model='gemini-2.5-flash',
    name='EmojiInterpretingAgent',
    description=(
        'Recibe la solicitud del usuario y retorna una '
        'interpretación con sólo emojis'
    ),
    instruction=leer_instrucciones("ins_emoji_agent.txt"),
    output_key='emoji_response',
    generate_content_config=types.GenerateContentConfig(
        temperature=1.6
    )
)

# Agente que ejecuta los agentes en paralelo
parallel_agent = ParallelAgent(
    name='ParallelInstructionAgent',
    description='Corre múltiples agentes en paralelo.',
    sub_agents=[normal_agent, emoji_agent],
)

# Agente que combina las respuestas de los agentes paralelos
merger_agent = Agent(
    model='gemini-2.5-flash',
    name='MergerAgent',
    description=(
        'Recibe las respuestas de múltiples agentes '
        'y las combina en una sola respuesta coherente.'
    ),
    instruction=leer_instrucciones("ins_merger_agent.txt"),
)

# Agente secuencial que primero ejecuta los agentes 
# en paralelo y luego combina sus respuestas
sequential_pipeline_agent = SequentialAgent(
    name="SequentialPipelineAgent",
    sub_agents=[parallel_agent, merger_agent],
    description="Coordina agentes en paralelo y luego combina sus respuestas."
)

# Agente raíz que se utilizará para interactuar
root_agent = sequential_pipeline_agent