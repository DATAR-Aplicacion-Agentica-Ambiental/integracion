from google.adk.agents.llm_agent import Agent
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent
from google.genai import types
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext

from .utils import leer_instrucciones

def cambiar_respuesta_emojis(callback_context: CallbackContext, llm_response: LlmResponse):
    """
    Función para guardar respuesta del LLM en una variable de 
    contexto y modificar la respuesta del agente al usuario para que no se imprima nada. 
    """
    # Asignar respuesta del modelo a una variable en estado
    callback_context.state['respuesta_emojis'] = llm_response.content.parts[0].text

    # Modificar respuesta al usuario para que no se imprima nada
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text='')])
    )

def cambiar_respuesta_textual(callback_context: CallbackContext, llm_response: LlmResponse):
    """
    Función para guardar respuesta del LLM en una variable de 
    contexto y modificar la respuesta del agente al usuario para que no se imprima nada. 
    """
    # Asignar respuesta del modelo a una variable en estado
    callback_context.state['respuesta_textual'] = llm_response.content.parts[0].text

    # Modificar respuesta al usuario para que no se imprima nada
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text='Procesando...')])
    )

def cambiar_respuesta_fusionadora(callback_context: CallbackContext, llm_response: LlmResponse):
    """
    Función para guardar respuesta del LLM en una variable de 
    contexto y modificar la respuesta del agente al usuario para que no se imprima nada. 
    """
    # Asignar respuesta del modelo a una variable en estado
    callback_context.state['respuesta_fusionadora'] = llm_response.content.parts[0].text

    # Modificar respuesta al usuario para que no se imprima nada
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text='')])
    )

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
    generate_content_config=types.GenerateContentConfig(
        temperature=1.8
    ),
    after_model_callback=cambiar_respuesta_emojis
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
    model='gemini-2.5-flash',
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
    model='gemini-2.5-flash',
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