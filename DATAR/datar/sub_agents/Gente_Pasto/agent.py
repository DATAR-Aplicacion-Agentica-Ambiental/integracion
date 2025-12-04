import os
from datetime import datetime
from random import randint, choice
import numpy as np
from scipy.io import wavfile
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
    "pajaros": "aves-IAvH-CSA-6297.wav",
    "pajaros_2": "aves-IAvH-CSA-962.wav",
    "insectos": None,  # No disponible
    "viento": None,    # No disponible
    "tinguas": None    # No disponible
}

# --- Funciones de audio usando scipy/numpy --- #

def db_to_linear(db: int) -> float:
    """Convierte decibelios a factor lineal de ganancia."""
    return 10 ** (db / 20.0)

def cargar_sonido_wav(nombre_archivo: str, volumen_db: int = 0) -> tuple[np.ndarray, int]:
    """
    Carga un archivo WAV desde la carpeta SOUNDS_DIR y ajusta su volumen.
    
    Args:
        nombre_archivo: Nombre del archivo de audio WAV
        volumen_db: Ajuste de volumen en decibelios
    
    Returns:
        Tupla (audio_data, sample_rate) donde audio_data es un array numpy normalizado [-1, 1]
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        RuntimeError: Si hay error al leer el archivo
    """
    path = os.path.join(SOUNDS_DIR, nombre_archivo)
    
    # Verificar que el archivo existe
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el archivo de audio: {nombre_archivo} en {SOUNDS_DIR}"
        )
    
    try:
        # Leer archivo WAV
        sample_rate, audio_data = wavfile.read(path)
        
        # Convertir a float32 normalizado [-1, 1]
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483648.0
        elif audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            # Ya está en float, solo asegurar que esté en [-1, 1]
            audio_data = np.clip(audio_data.astype(np.float32), -1.0, 1.0)
        else:
            # Convertir genéricamente
            if audio_data.dtype.kind == 'i':
                max_val = np.iinfo(audio_data.dtype).max
                audio_data = audio_data.astype(np.float32) / max_val
            else:
                audio_data = audio_data.astype(np.float32)
        
        # Manejar audio estéreo (convertir a mono si es necesario)
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Aplicar ajuste de volumen
        if volumen_db != 0:
            ganancia = db_to_linear(volumen_db)
            audio_data = audio_data * ganancia
            # Asegurar que no se sature
            audio_data = np.clip(audio_data, -1.0, 1.0)
        
        return audio_data, sample_rate
        
    except Exception as e:
        raise RuntimeError(
            f"Error al cargar el archivo {nombre_archivo}: {str(e)}"
        ) from e

def cambiar_velocidad(audio_data: np.ndarray, sample_rate: int, factor: float) -> np.ndarray:
    """
    Cambia la velocidad del audio (y por tanto el pitch).
    factor > 1: acelera, factor < 1: ralentiza
    """
    # Redimensionar el array usando interpolación lineal
    indices = np.linspace(0, len(audio_data) - 1, int(len(audio_data) / factor))
    return np.interp(indices, np.arange(len(audio_data)), audio_data)

def aplicar_eco(audio_data: np.ndarray, sample_rate: int, offset_ms: int, atenuacion_db: int = -6) -> np.ndarray:
    """
    Aplica un efecto de eco al audio.
    
    Args:
        audio_data: Array de audio normalizado
        sample_rate: Frecuencia de muestreo
        offset_ms: Retardo del eco en milisegundos
        atenuacion_db: Atenuación del eco en decibelios
    """
    offset_samples = int((offset_ms / 1000.0) * sample_rate)
    eco = audio_data * db_to_linear(atenuacion_db)
    
    # Crear array de salida más largo para acomodar el eco
    resultado = np.zeros(len(audio_data) + offset_samples, dtype=np.float32)
    resultado[:len(audio_data)] = audio_data
    resultado[offset_samples:offset_samples + len(eco)] += eco
    
    # Recortar al tamaño original
    return resultado[:len(audio_data)]

def aplicar_efectos_artistico(audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Aplica efectos creativos aleatorios:
    - Eco aleatorio
    - Inversión del audio
    - Cambios de velocidad o pitch
    """
    resultado = audio_data.copy()
    
    # Eco aleatorio
    if choice([True, False]):
        offset = randint(100, 400)  # milisegundos
        resultado = aplicar_eco(resultado, sample_rate, offset, -6)
    
    # Inversión aleatoria
    if choice([True, False]):
        resultado = np.flip(resultado)
    
    # Cambio creativo de velocidad/pitch
    if choice([True, False]):
        factor = choice([0.9, 1.1, 1.2])
        resultado = cambiar_velocidad(resultado, sample_rate, factor)
    
    return resultado

def mezclar_audios(audios: list[tuple[np.ndarray, int]], duracion_seg: int) -> tuple[np.ndarray, int]:
    """
    Mezcla múltiples audios en uno solo.
    
    Args:
        audios: Lista de tuplas (audio_data, sample_rate)
        duracion_seg: Duración deseada en segundos
    
    Returns:
        Tupla (audio_mezclado, sample_rate)
    """
    if not audios:
        raise ValueError("No hay audios para mezclar")
    
    # Usar el sample_rate del primer audio
    sample_rate = audios[0][1]
    
    # Calcular tamaño del array de salida
    tamanio_objetivo = int(sample_rate * duracion_seg)
    
    # Crear array de mezcla
    mezcla = np.zeros(tamanio_objetivo, dtype=np.float32)
    
    for audio_data, sr in audios:
        # Resamplear si es necesario
        if sr != sample_rate:
            # Interpolación simple para cambiar sample rate
            indices = np.linspace(0, len(audio_data) - 1, int(len(audio_data) * sample_rate / sr))
            audio_resampleado = np.interp(indices, np.arange(len(audio_data)), audio_data)
        else:
            audio_resampleado = audio_data
        
        # Recortar o repetir si es necesario
        if len(audio_resampleado) < tamanio_objetivo:
            # Repetir el audio si es más corto
            repeticiones = int(np.ceil(tamanio_objetivo / len(audio_resampleado)))
            audio_resampleado = np.tile(audio_resampleado, repeticiones)
        
        # Aplicar offset aleatorio para que suene más natural
        offset = randint(0, min(500, int(sample_rate * 0.5)))  # máximo 0.5 segundos
        
        # Recortar al tamaño objetivo
        audio_resampleado = audio_resampleado[:tamanio_objetivo]
        
        # Mezclar con offset
        if offset > 0:
            audio_con_offset = np.zeros(tamanio_objetivo, dtype=np.float32)
            audio_con_offset[offset:offset + len(audio_resampleado[:tamanio_objetivo - offset])] = audio_resampleado[:tamanio_objetivo - offset]
            mezcla += audio_con_offset
        else:
            mezcla += audio_resampleado[:tamanio_objetivo]
    
    # Normalizar para evitar saturación
    max_val = np.max(np.abs(mezcla))
    if max_val > 1.0:
        mezcla = mezcla / max_val * 0.95  # Dejar algo de headroom
    
    return mezcla, sample_rate

def exportar_wav(audio_data: np.ndarray, sample_rate: int, ruta_archivo: str):
    """
    Exporta audio a archivo WAV.
    
    Args:
        audio_data: Array de audio normalizado [-1, 1]
        sample_rate: Frecuencia de muestreo
        ruta_archivo: Ruta donde guardar el archivo
    """
    # Asegurar que esté en el rango correcto
    audio_data = np.clip(audio_data, -1.0, 1.0)
    
    # Convertir a int16
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Guardar WAV
    wavfile.write(ruta_archivo, sample_rate, audio_int16)

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
    - Ruta del archivo WAV generado.
    
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
                audio_data, sample_rate = cargar_sonido_wav(ARCHIVOS_SONIDOS["pajaros"], pajaros_vol)
                capas.append((audio_data, sample_rate))
            except Exception as e:
                errores.append(f"pájaros: {str(e)}")
        else:
            errores.append("pájaros: archivo no disponible")
    
    if insectos_vol != 0:
        if ARCHIVOS_SONIDOS["insectos"]:
            try:
                audio_data, sample_rate = cargar_sonido_wav(ARCHIVOS_SONIDOS["insectos"], insectos_vol)
                capas.append((audio_data, sample_rate))
            except Exception as e:
                errores.append(f"insectos: {str(e)}")
        else:
            errores.append("insectos: archivo no disponible")
    
    if viento_vol != 0:
        if ARCHIVOS_SONIDOS["viento"]:
            try:
                audio_data, sample_rate = cargar_sonido_wav(ARCHIVOS_SONIDOS["viento"], viento_vol)
                capas.append((audio_data, sample_rate))
            except Exception as e:
                errores.append(f"viento: {str(e)}")
        else:
            errores.append("viento: archivo no disponible")
    
    if tinguas_vol != 0:
        if ARCHIVOS_SONIDOS["tinguas"]:
            try:
                audio_data, sample_rate = cargar_sonido_wav(ARCHIVOS_SONIDOS["tinguas"], tinguas_vol)
                capas.append((audio_data, sample_rate))
            except Exception as e:
                errores.append(f"tinguas: {str(e)}")
        else:
            errores.append("tinguas: archivo no disponible")
    
    # Si hay errores, informarlos pero continuar si hay al menos una capa válida
    if errores:
        mensaje_error = f"Advertencia: No se pudieron cargar algunos sonidos: {', '.join(errores)}"
        print(mensaje_error)

    if not capas:
        raise ValueError(
            "No se seleccionó ningún sonido para mezclar o no se pudieron cargar los archivos. "
            "Asegúrate de que los archivos de audio existen en formato WAV en la carpeta sounds/."
        )

    # Mezclar todos los audios
    mezcla, sample_rate = mezclar_audios(capas, duracion_seg)

    # Aplicar efectos artísticos si se desea
    if efectos:
        mezcla = aplicar_efectos_artistico(mezcla, sample_rate)

    # Guardar el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"paisaje_sonoro_{timestamp}.wav"
    ruta_archivo = os.path.join(OUTPUT_DIR, nombre_archivo)
    exportar_wav(mezcla, sample_rate, ruta_archivo)

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
