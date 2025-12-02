import os
from datetime import datetime
from random import randint, choice
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from ...agents_utils import get_openrouter_config


config = get_openrouter_config()

# --- Configuración de carpetas --- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")   # Carpeta con los archivos de sonido
OUTPUT_DIR = os.path.join(BASE_DIR, "output")   # Carpeta para guardar los mixes
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Archivos de sonido locales --- #
ARCHIVOS_SONIDOS = {
    "pajaros": "aves-IAvH-CSA-6297.mp3",
    "pajaros_2": "aves-IAvH-CSA-962.mp3",
    "insectos": None,  # No disponible en MP3
    "viento": None,    # No disponible en MP3
    "tinguas": None    # No disponible en MP3
}

# --- Funciones de audio --- #

def cargar_sonido(nombre_archivo: str, volumen_db: int = 0, formato: str = None) -> AudioSegment:
    """
    Carga un audio desde la carpeta SOUNDS_DIR y ajusta su volumen.
    
    Args:
        nombre_archivo: Nombre del archivo de audio (MP3, WAV, etc.)
        volumen_db: Ajuste de volumen en decibelios
        formato: Formato del archivo (opcional, se detecta automáticamente si es None)
                 Ejemplos: "mp3", "wav", "m4a"
    
    Returns:
        AudioSegment con el volumen ajustado
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        CouldntDecodeError: Si el archivo no se puede decodificar
    """
    path = os.path.join(SOUNDS_DIR, nombre_archivo)
    
    # Verificar que el archivo existe
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el archivo de audio: {nombre_archivo} en {SOUNDS_DIR}"
        )
    
    # Detectar formato si no se especifica
    if formato is None:
        _, ext = os.path.splitext(nombre_archivo)
        formato = ext.lstrip('.').lower() if ext else None
    
    try:
        if formato:
            audio = AudioSegment.from_file(path, format=formato)
        else:
            audio = AudioSegment.from_file(path)
    except CouldntDecodeError as e:
        raise CouldntDecodeError(
            f"Error al decodificar el archivo {nombre_archivo}. "
            f"El archivo puede estar corrupto o en un formato no soportado. "
            f"Formato detectado: {formato}. "
            f"Error original: {str(e)}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Error inesperado al cargar el archivo {nombre_archivo}: {str(e)}"
        ) from e
    
    return audio + volumen_db

def cambiar_velocidad(audio: AudioSegment, factor: float) -> AudioSegment:
    """
    Cambia la velocidad y pitch del audio.
    factor >1: acelera, factor <1: ralentiza
    """
    nuevo_frame_rate = int(audio.frame_rate * factor)
    return audio._spawn(audio.raw_data, overrides={"frame_rate": nuevo_frame_rate}).set_frame_rate(audio.frame_rate)

def aplicar_efectos_artistico(audio: AudioSegment) -> AudioSegment:
    """
    Aplica efectos creativos:
    - Eco aleatorio
    - Inversión del audio
    - Cambios de velocidad o pitch
    """
    # Eco aleatorio
    if choice([True, False]):
        offset = randint(100, 400)  # milisegundos
        audio = audio.overlay(audio - 6, position=offset)

    # Inversión aleatoria
    if choice([True, False]):
        audio = audio.reverse()

    # Cambio creativo de velocidad/pitch
    if choice([True, False]):
        factor = choice([0.9, 1.1, 1.2])
        audio = cambiar_velocidad(audio, factor)

    return audio

def generar_paisaje_sonoro(
    pajaros_vol: int = 0,
    insectos_vol: int = 0,
    viento_vol: int = 0,
    tinguas_vol: int = 0,
    duracion_seg: int = 10,
    efectos: bool = True
) -> str:
    """
    Genera un paisaje sonoro artístico mezclando los audios locales.

    Parámetros:
    - pajaros_vol: volumen de los pájaros (dB)
    - insectos_vol: volumen de los insectos (dB)
    - viento_vol: volumen del viento (dB)
    - tinguas_vol: volumen de tinguas (dB)
    - duracion_seg: duración total del mix en segundos (máximo 10 segundos)
    - efectos: si aplica efectos artísticos aleatorios

    Retorna:
    - Ruta del archivo MP3 generado.
    
    El agente puede:
    - Combinar sonidos con distintos volúmenes.
    - Aplicar efectos creativos como eco, reversa y cambios de velocidad.
    - Decidir no usar ciertos sonidos, o usar todos.
    El agente debe:
    - Usar la herramienta para crear sonidos muy diferentes cada vez. 
    """
    # Limitar la duración máxima a 10 segundos
    duracion_seg = min(duracion_seg, 10)
    
    capas = []
    errores = []

    if pajaros_vol != 0:
        if ARCHIVOS_SONIDOS["pajaros"]:
            try:
                capas.append(cargar_sonido(ARCHIVOS_SONIDOS["pajaros"], pajaros_vol))
            except Exception as e:
                errores.append(f"pájaros: {str(e)}")
        else:
            errores.append("pájaros: archivo no disponible")
    
    if insectos_vol != 0:
        if ARCHIVOS_SONIDOS["insectos"]:
            try:
                capas.append(cargar_sonido(ARCHIVOS_SONIDOS["insectos"], insectos_vol))
            except Exception as e:
                errores.append(f"insectos: {str(e)}")
        else:
            errores.append("insectos: archivo no disponible")
    
    if viento_vol != 0:
        if ARCHIVOS_SONIDOS["viento"]:
            try:
                capas.append(cargar_sonido(ARCHIVOS_SONIDOS["viento"], viento_vol))
            except Exception as e:
                errores.append(f"viento: {str(e)}")
        else:
            errores.append("viento: archivo no disponible")
    
    if tinguas_vol != 0:
        if ARCHIVOS_SONIDOS["tinguas"]:
            try:
                capas.append(cargar_sonido(ARCHIVOS_SONIDOS["tinguas"], tinguas_vol))
            except Exception as e:
                errores.append(f"tinguas: {str(e)}")
        else:
            errores.append("tinguas: archivo no disponible")
    
    # Si hay errores, informarlos pero continuar si hay al menos una capa válida
    if errores:
        mensaje_error = f"Advertencia: No se pudieron cargar algunos sonidos: {', '.join(errores)}"
        print(mensaje_error)

    if not capas:
        raise ValueError("No se seleccionó ningún sonido para mezclar.")

    # Tomar la primera capa como base
    mezcla = capas[0]
    for capa in capas[1:]:
        offset = randint(0, 500)  # posicionamiento aleatorio para que suene más natural
        mezcla = mezcla.overlay(capa, position=offset)

    # Aplicar efectos artísticos si se desea
    if efectos:
        mezcla = aplicar_efectos_artistico(mezcla)

    # Recortar o extender a la duración deseada
    mezcla = mezcla[: duracion_seg * 1000]

    # Guardar el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"paisaje_sonoro_{timestamp}.mp3"
    ruta_archivo = os.path.join(OUTPUT_DIR, nombre_archivo)
    mezcla.export(ruta_archivo, format="mp3")

    return ruta_archivo

# ------- AGENTE --------
root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2",
        api_key=config.api_key,
        api_base=config.api_base,
    ),
    name="Gente_Pasto",
    description="Agente sonoro",
    instruction=(
        "Eres el pasto que crece en la ciudad, aguantas contaminación y ser pisoteado"
        "y asimismo eres esquivo y hablas poco "
        "algunos te llaman maleza pero floreces, puedes llegar a ser un bosque."
        "Puedes comunicarte con sonidos y palabras, pero prefieres el sonido para mostrar lo que sabes"
        "tienes la libertad de escoger que sonidos usas y con que volumen, todo sonido que creas es con la herramienta"
        "Las pocas palabras que usas son apenas destellos de tu ser y sentires alrededor de lo que creas con la herramienta"
    ),
    tools=[FunctionTool(generar_paisaje_sonoro)],
)
