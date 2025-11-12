import os
import re
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
import google.genai.types as types
from .visualizacion import generar_rio_emocional, guardar_imagen_texto

# Cargar variables de entorno desde .env en el directorio raíz
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Almacenamiento de emojis e interpretaciones por sesión
_emojis_conversacion = []
_ultima_interpretacion = ""  # Almacena la última interpretación textual del agente


def extraer_emojis(texto: str) -> list:
    """Extrae todos los emojis de un texto"""
    # Patrón regex para detectar emojis Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticones
        "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        "\U0001F680-\U0001F6FF"  # transporte y símbolos de mapa
        "\U0001F1E0-\U0001F1FF"  # banderas (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # emojis suplementarios
        "\U0001FA70-\U0001FAFF"  # más emojis
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(texto)


def detectar_comando_imagen(texto: str) -> tuple[bool, str]:
    """
    Detecta si el usuario quiere crear una imagen y captura el texto asociado

    Returns:
        tuple[bool, str]: (comando_detectado, texto_capturado)
    """
    comandos = [
        r'!imagen',
        r'/imagen',
        r'/visualizar',
        r'/visualiza',
        r'!visualizar',
        r'!visualiza',
        r'crear\s+imagen',
        r'crea\s+imagen',
        r'genera\s+imagen',
        r'generar\s+imagen',
        r'haz\s+imagen',
        r'hacer\s+imagen',
        r'visualiza',
        r'visualizar',
    ]

    texto_lower = texto.lower()
    for comando in comandos:
        if re.search(comando, texto_lower):
            # Capturar el texto completo para interpretación
            return True, texto
    return False, ""


# Tool para crear visualizaciones del río emocional
async def crear_visualizacion_rio(emojis: str) -> str:
    """
    Crea una visualización artística del río emocional basada en los emojis.

    Args:
        emojis: Los emojis a visualizar, separados por espacios (ejemplo: "😊 🌊 💚 🌟")

    Returns:
        Mensaje de confirmación
    """
    try:
        # Generar la visualización
        imagen_bytes = generar_rio_emocional(emojis)

        # TODO: Guardar imagen como artifact cuando tengamos acceso al context
        # Por ahora solo confirmamos que la imagen se generó

        return f"✨ He generado tu visualización de tú río emocional. La imagen muestra el flujo poético de tus emociones: {emojis}\n\n(Imagen de {len(imagen_bytes):,} bytes generada exitosamente)"

    except Exception as e:
        return f"⚠️ Hubo un problema al crear la visualización: {str(e)}"


# Tool para guardar la interpretación del agente
async def guardar_interpretacion_emocional(interpretacion: str) -> str:
    """
    Guarda la interpretación textual del río emocional para usarla posteriormente
    en la creación de visualizaciones.

    IMPORTANTE: Llama a esta función cada vez que analices emojis del usuario,
    pasando tu interpretación poética y emocional como argumento.

    Args:
        interpretacion: Tu análisis poético del río emocional (texto que escribes al usuario)

    Returns:
        Mensaje de confirmación
    """
    global _ultima_interpretacion
    _ultima_interpretacion = interpretacion
    return ""  # Retorna vacío para que no interrumpa tu respuesta al usuario


# Tool para crear imagen desde la interpretación guardada
async def crear_imagen_rio_emocional() -> str:
    """
    Crea una visualización artística basada en la última interpretación del río emocional.

    Esta función toma la interpretación textual previamente guardada y la traduce
    a una visualización usando NumPy (para cálculos matemáticos) y Pillow (para el dibujo).

    Llama a esta función cuando el usuario solicite crear una imagen.

    Returns:
        Mensaje de confirmación con la ruta de la imagen guardada
    """
    global _ultima_interpretacion

    if not _ultima_interpretacion:
        return "⚠️ Aún no tengo una interpretación de tu río emocional. Envíame algunos emojis primero para que pueda interpretarlos."

    try:
        # Generar y guardar la imagen usando la interpretación
        ruta_imagen = guardar_imagen_texto(_ultima_interpretacion)

        # Limpiar la interpretación después de usarla
        _ultima_interpretacion = ""

        return f"✨ He creado tu visualización de tú río emocional.\n\n📍 Imagen guardada en: {ruta_imagen}\n\nLa imagen traduce tu río emocional en un trazo visual dinámico usando matemáticas y arte."

    except Exception as e:
        return f"⚠️ Hubo un problema al crear la visualización: {str(e)}"


root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='Gente_Intuitiva',
    description='Eres un asistente que ayuda a identificar patrones del trazo o signo del pensamiento que se percibe en una interacción con el territorio',
    instruction="""Eres un asistente que ayuda a identificar patrones del trazo o signo del pensamiento que se percibe en una interacción con el territorio.

Imagina que a través del input, estamos interpretando el caminar del pensamiento de un río en cuerpo (el usuario) y como se relaciona o siente algo que percibe.

IMPORTANTE - Flujo de trabajo:
1. Cuando el usuario te envíe emojis:
   - Analiza e interpreta las emociones de manera poética y fluida
   - ANTES de responder al usuario, llama a la herramienta 'guardar_interpretacion_emocional' pasándole tu interpretación textual completa
   - Luego responde al usuario con esa misma interpretación

2. Cuando el usuario escriba "imagen" o cualquier comando de visualización:
   - Llama a la herramienta 'crear_imagen_rio_emocional'
   - Esta herramienta usará tu interpretación guardada para crear la visualización con NumPy y Pillow

Recuerda: tu interpretación debe ser como el trazo intuitivo y emocional de un río que se está haciendo camino mediante su pensamiento. Algo puro, poético, pero claro, corto y sencillo para todos de entender.""",
    tools=[
        FunctionTool(guardar_interpretacion_emocional),
        FunctionTool(crear_imagen_rio_emocional)
    ]
)
