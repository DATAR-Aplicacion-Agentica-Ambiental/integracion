"""
Utilidades para GenteInterpretativa.
"""
from pathlib import Path
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def obtener_path_instrucciones():
    """
    Obtiene el path absoluto de la carpeta 'instrucciones'.
    """
    path_agentes = Path(__file__).parent
    return path_agentes / "instrucciones"

def leer_instrucciones(archivo: str = "ins_defecto.md"):
    """
    Lee el contenido de un archivo de instrucciones 
    ubicado en la carpeta 'instrucciones'.

    Args:
        archivo (str): Nombre del archivo de instrucciones. 
        Por defecto es 'ins_defecto.md'.
        
    Returns:
        str: Contenido del archivo de instrucciones.
    """

    path_archivo = obtener_path_instrucciones() / archivo

    with open(path_archivo, "r") as a:
        instrucciones = a.read()
 
    return instrucciones

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