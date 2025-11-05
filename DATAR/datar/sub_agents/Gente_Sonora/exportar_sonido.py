import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import os
from datetime import datetime

# Parámetros de audio
samplerate = 44100  # Frecuencia de muestreo en Hz
duration = 10        # Duración total en segundos

def generar_sonido_humedal(exportar=True, reproducir=True):
    """
    Genera una composición sonora evocando el Humedal La Conejera.
    Incluye sonidos de agua, aves y un ambiente general.
    
    Args:
        exportar (bool): Si es True, exporta el audio a MP3
        reproducir (bool): Si es True, reproduce el audio
    
    Returns:
        numpy.ndarray: Los datos de audio generados
    """
    t = np.linspace(0, duration, int(samplerate * duration), False)

    # 1. Fondo de agua suave (ruido blanco de baja frecuencia y sine wave sutil)
    water_noise = np.random.normal(0, 0.05, t.shape) * np.exp(-t/duration * 0.5)
    
    # Onda de baja frecuencia para el murmullo del agua
    water_hum = 0.03 * np.sin(2 * np.pi * 30 * t) 
    
    # Filtrar el ruido para hacerlo más "acuático" (simple paso bajo)
    b, a = np.array([0.05]), np.array([1, -0.95])
    filtered_water_noise = np.zeros_like(water_noise)
    for i in range(1, len(water_noise)):
        filtered_water_noise[i] = b[0] * water_noise[i] - a[1] * filtered_water_noise[i-1]
    
    background = water_hum + filtered_water_noise * 0.5

    # 2. Sonido de ave (ej. Tingua Azul o similar) - chirrido/graznido
    bird_call1 = np.zeros_like(t)
    start_time_bird1 = 1.5
    end_time_bird1 = start_time_bird1 + 0.3
    idx_start1 = int(start_time_bird1 * samplerate)
    idx_end1 = int(end_time_bird1 * samplerate)
    if idx_end1 <= len(t):
        freq_bird1 = 1200 + 400 * np.sin(2 * np.pi * 5 * t[idx_start1:idx_end1])
        bird_call1[idx_start1:idx_end1] = 0.15 * np.sin(2 * np.pi * freq_bird1 * t[idx_start1:idx_end1]) * np.hanning(idx_end1 - idx_start1)

    # 3. Segundo sonido de ave/insecto
    bird_call2 = np.zeros_like(t)
    start_time_bird2 = 4.0
    end_time_bird2 = start_time_bird2 + 0.2
    idx_start2 = int(start_time_bird2 * samplerate)
    idx_end2 = int(end_time_bird2 * samplerate)
    if idx_end2 <= len(t):
        freq_bird2 = 2000
        bird_call2[idx_start2:idx_end2] = 0.1 * np.sin(2 * np.pi * freq_bird2 * t[idx_start2:idx_end2]) * np.hanning(idx_end2 - idx_start2)

    # 4. Croar de rana - Pulsos de baja frecuencia
    frog_croak = np.zeros_like(t)
    frog_freq = 300
    croak_duration = 0.2
    croak_starts = [0.8, 2.5, 5.0]
    for start in croak_starts:
        idx_start_croak = int(start * samplerate)
        idx_end_croak = int((start + croak_duration) * samplerate)
        if idx_end_croak <= len(t):
            croak_wave = 0.1 * np.sin(2 * np.pi * frog_freq * t[idx_start_croak:idx_end_croak]) * np.hanning(idx_end_croak - idx_start_croak)
            frog_croak[idx_start_croak:idx_end_croak] += croak_wave

    # Combinar todos los elementos
    audio_data = background + bird_call1 + bird_call2 + frog_croak

    # Normalizar el audio para evitar saturación
    audio_data = audio_data / np.max(np.abs(audio_data)) * 0.6

    # Exportar a archivo MP3
    if exportar:
        exportar_audio(audio_data, samplerate)

    # Reproducir el audio
    if reproducir:
        print(f"Generando sonido del Humedal La Conejera por {duration} segundos...")
        sd.play(audio_data, samplerate)
        sd.wait()
        print("Sonido finalizado.")
    
    return audio_data


def exportar_audio(audio_data, samplerate):
    """
    Exporta el audio generado a formato MP3 en el escritorio.
    Si pydub no está disponible, exporta a WAV.
    
    Args:
        audio_data (numpy.ndarray): Datos de audio a exportar
        samplerate (int): Frecuencia de muestreo
    """
    # Obtener la ruta del escritorio
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Si Desktop no existe (en español), intentar con Escritorio
    if not os.path.exists(escritorio):
        escritorio = os.path.join(os.path.expanduser("~"), "Escritorio")
    
    # Si ninguno existe, usar el directorio home
    if not os.path.exists(escritorio):
        escritorio = os.path.expanduser("~")
        print(f"Advertencia: No se encontró el escritorio. Guardando en: {escritorio}")
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = f"humedal_conejera_{timestamp}"
    
    # Convertir audio a int16 para guardarlo
    audio_int16 = np.int16(audio_data * 32767)
    
    try:
        # Intentar exportar a MP3 usando pydub
        from pydub import AudioSegment
        
        # Primero guardar como WAV temporal
        archivo_wav_temp = os.path.join(escritorio, f"{nombre_base}_temp.wav")
        wavfile.write(archivo_wav_temp, samplerate, audio_int16)
        
        # Convertir WAV a MP3
        audio_segment = AudioSegment.from_wav(archivo_wav_temp)
        archivo_mp3 = os.path.join(escritorio, f"{nombre_base}.mp3")
        audio_segment.export(archivo_mp3, format="mp3", bitrate="192k")
        
        # Eliminar archivo temporal
        os.remove(archivo_wav_temp)
        
        print(f"✓ Audio exportado exitosamente a: {archivo_mp3}")
        
    except ImportError:
        # Si pydub no está disponible, guardar como WAV
        archivo_wav = os.path.join(escritorio, f"{nombre_base}.wav")
        wavfile.write(archivo_wav, samplerate, audio_int16)
        
        print(f"✓ Audio exportado como WAV (instala 'pydub' y 'ffmpeg' para MP3): {archivo_wav}")
        print("  Instalación: pip install pydub")
        print("  FFmpeg: https://ffmpeg.org/download.html")
        
    except Exception as e:
        print(f"✗ Error al exportar audio: {e}")


# Ejecutar la función con exportación automática
if __name__ == "__main__":
    generar_sonido_humedal(exportar=True, reproducir=True)