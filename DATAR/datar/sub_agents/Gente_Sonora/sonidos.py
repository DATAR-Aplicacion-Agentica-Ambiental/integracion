import os
import random
from pydub import AudioSegment
from pydub.playback import play


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
carpeta_sonidos = os.path.join(BASE_DIR, "/Users/sebastianlopezospina/Documents/githubprojects/dataradk/datarsebas/sonidoss")


print(f"Buscando sonidoss en: {carpeta_sonidos}")

# Cargar archivos .m4a
archivos = [f for f in os.listdir(carpeta_sonidos) if f.endswith(".m4a")]

if not archivos:
    print("⚠️ No hay archivos .m4a en la carpeta 'sonidoss'")
else:
    while True:
        archivo_aleatorio = random.choice(archivos)
        ruta = os.path.join(carpeta_sonidos, archivo_aleatorio)
        print(f"🎵 Reproduciendo: {archivo_aleatorio}")
        sonido = AudioSegment.from_file(ruta, format="m4a")
        play(sonido)
