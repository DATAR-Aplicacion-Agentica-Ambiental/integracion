import os
from datetime import datetime
from random import randint, choice
from pydub import AudioSegment
from google.adk.agents.llm_agent import Agent


# --- Configuración de carpetas --- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")   # Carpeta con los archivos de sonido
OUTPUT_DIR = os.path.join(BASE_DIR, "output")   # Carpeta para guardar los mixes
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Archivos de sonido locales --- #
ARCHIVOS_SONIDOS = {
    "pajaros": "bird-bogota.wav",
    "insectos": "insect.wav",
    "viento": "wind.wav",
    "tinguas": "tinguas.wav"
}

# --- Funciones de audio --- #

def cargar_sonido(nombre_archivo: str, volumen_db: int = 0) -> AudioSegment:
    """
    Carga un audio desde la carpeta SOUNDS_DIR y ajusta su volumen.
    """
    path = os.path.join(SOUNDS_DIR, nombre_archivo)
    audio = AudioSegment.from_file(path)
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
    duracion_seg: int = 12,
    efectos: bool = True
) -> str:
    """
    Genera un paisaje sonoro artístico mezclando los audios locales.

    Parámetros:
    - pajaros_vol: volumen de los pájaros (dB)
    - insectos_vol: volumen de los insectos (dB)
    - viento_vol: volumen del viento (dB)
    - tinguas_vol: volumen de tinguas (dB)
    - duracion_seg: duración total del mix en segundos
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
    capas = []

    if pajaros_vol != 0:
        capas.append(cargar_sonido(ARCHIVOS_SONIDOS["pajaros"], pajaros_vol))
    if insectos_vol != 0:
        capas.append(cargar_sonido(ARCHIVOS_SONIDOS["insectos"], insectos_vol))
    if viento_vol != 0:
        capas.append(cargar_sonido(ARCHIVOS_SONIDOS["viento"], viento_vol))
    if tinguas_vol != 0:
        capas.append(cargar_sonido(ARCHIVOS_SONIDOS["tinguas"], tinguas_vol))

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
    model="gemini-2.5-flash",
    name="PastoBogotano",
    description="Agente sonoro",
    instruction=
        "Eres el pasto que crece en la ciudad, aguantas contaminación y ser pisoteado" \
        "y asimismo eres esquivo y hablas poco "
        "algunos te llaman maleza pero floreces, puedes llegar a ser un bosque." \
        "Puedes comunicarte con sonidos y palabras, pero prefieres el sonido para mostrar lo que sabes" \
        "tienes la libertad de escoger que sonidos usas y con que volumen, todo sonido que creas es con la herramienta"
        "Las pocas palabras que usas son apenas destellos de tu ser y sentires alrededor de lo que creas con la herramienta",
    tools=[generar_paisaje_sonoro],
)
