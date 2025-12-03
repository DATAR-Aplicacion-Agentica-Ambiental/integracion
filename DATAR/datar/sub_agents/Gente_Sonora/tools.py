# tools.py - Herramientas para el Agente de Sonidos

import numpy as np
import os
from datetime import datetime
from typing import Dict, List

# Importar matplotlib solo si está disponible
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sin interfaz gráfica
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Importar scipy solo si está disponible
try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

def log_uso(funcion, tipo):
    """Guarda registro de cada función usada."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Usando {tipo}: {funcion}", flush=True)

def _generar_ascii_grafico(descripcion: str) -> str:
    """Genera representación ASCII de un gráfico (fallback sin matplotlib)."""
    desc_lower = descripcion.lower()
    
    if "agua" in desc_lower or "río" in desc_lower:
        return """
🌊 AGUA / RÍO
━━━━━━━━━━━━━━━━━━━━━━━━━━
  ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈
  ∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽
  ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈
  ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿
  ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈
"""
    elif "bosque" in desc_lower or "árbol" in desc_lower:
        return """
🌳 BOSQUE
━━━━━━━━━━━━━━━━━━━━━━━━━━
        ▲
       ▲▲▲
      ▲▲▲▲▲
     ▲▲▲▲▲▲▲
        ║║
        ║║
       
      ▲        ▲
     ▲▲▲      ▲▲▲
    ▲▲▲▲▲    ▲▲▲▲▲
   ▲▲▲▲▲▲▲  ▲▲▲▲▲▲▲
      ║║        ║║
"""
    elif "humedal" in desc_lower:
        return """
🦆 HUMEDAL CONEJERA
━━━━━━━━━━━━━━━━━━━━━━━━━━
    🦆           🦆
  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
  │││││││││││││││││││││││
  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
  │││││││││││││││││││││││
  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
        🦆
"""
    else:
        return """
🌿 ECOSISTEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━
        ☀️
    
    ▲        ▲        ▲
   ▲▲▲      ▲▲▲      ▲▲▲
  ▲▲▲▲▲    ▲▲▲▲▲    ▲▲▲▲▲
━━━━━━━━━━━━━━━━━━━━━━━━━━
  🦋  🐝  🦗  🐛  🕷️  🦌
"""

def generar_grafico_turtle(descripcion: str) -> str:
    """
    Genera un gráfico basado en la descripción y lo guarda como archivo (si matplotlib disponible).
    
    Args:
        descripcion: Descripción del gráfico a generar (p.ej., "bosque", "agua", "humedal")
    
    Returns:
        Confirmación del gráfico generado y ruta del archivo
    """
    log_uso(descripcion, "gráfico")
    
    # Si matplotlib no está disponible, usar ASCII art
    if not MATPLOTLIB_AVAILABLE:
        ascii_grafico = _generar_ascii_grafico(descripcion)
        return ascii_grafico
    
    try:
        # Crear directorio de salida si no existe
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(8, 8), facecolor='white')
        ax.set_xlim(-200, 200)
        ax.set_ylim(-200, 200)
        ax.set_aspect('equal')
        ax.axis('off')
        
        desc_lower = descripcion.lower()
        
        if "agua" in desc_lower or "río" in desc_lower:
            # Dibujar agua
            ax.set_title("🌊 Agua", fontsize=16, fontweight='bold')
            for i in range(5):
                y = 150 - i * 60
                x = np.linspace(-150, 150, 100)
                wave = 20 * np.sin(x / 50)
                ax.plot(x, y + wave, color='blue', linewidth=2)
            ax.fill_between(np.linspace(-150, 150, 100), -200, -100, color='lightblue', alpha=0.5)
            
        elif "bosque" in desc_lower or "árbol" in desc_lower:
            # Dibujar árbol
            ax.set_title("🌳 Bosque", fontsize=16, fontweight='bold')
            # Tronco
            ax.add_patch(plt.Rectangle((-20, -100), 40, 150, color='brown', alpha=0.7))
            # Copa
            circle = plt.Circle((0, 80), 100, color='green', alpha=0.7)
            ax.add_patch(circle)
            circle2 = plt.Circle((-50, 40), 70, color='darkgreen', alpha=0.6)
            ax.add_patch(circle2)
            circle3 = plt.Circle((50, 40), 70, color='darkgreen', alpha=0.6)
            ax.add_patch(circle3)
            
        elif "humedal" in desc_lower:
            # Dibujar humedal
            ax.set_title("🦆 Humedal", fontsize=16, fontweight='bold')
            # Agua
            ax.fill_between(np.linspace(-150, 150, 100), -200, 0, color='cyan', alpha=0.4)
            # Juncos
            for x_pos in np.linspace(-150, 150, 12):
                for y_pos in [-50, -30, -10]:
                    ax.plot([x_pos, x_pos + np.sin(y_pos/30)*5], [y_pos, y_pos+20], 
                           color='green', linewidth=2, alpha=0.7)
            # Aves
            ax.plot([-100, -90], [100, 110], marker='^', markersize=8, color='darkblue')
            ax.plot([100, 110], [100, 110], marker='^', markersize=8, color='darkblue')
            
        else:
            # Patrón genérico
            ax.set_title("🌿 Ecosistema", fontsize=16, fontweight='bold')
            # Cielo
            ax.fill_between(np.linspace(-200, 200, 100), 0, 200, color='lightyellow', alpha=0.3)
            # Tierra
            ax.fill_between(np.linspace(-200, 200, 100), -200, -50, color='saddlebrown', alpha=0.3)
            # Plantas genéricas
            for x in np.linspace(-150, 150, 8):
                ax.plot([x, x], [-50, -50 + np.random.randint(30, 80)], 
                       color='green', linewidth=3, alpha=0.6)
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grafico_{descripcion.replace(' ', '_')[:20]}_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        return f"✅ Gráfico '{descripcion}' generado exitosamente\n📁 Guardado en: {filepath}"
    
    except Exception as e:
        # Si matplotlib falla, usar ASCII art como fallback
        ascii_grafico = _generar_ascii_grafico(descripcion)
        return f"⚠️ Usando representación ASCII (matplotlib no disponible):\n{ascii_grafico}"

def generar_ascii_morse(sonido: str) -> str:
    """
    Genera representación ASCII y código morse para representar sonidos.
    
    Args:
        sonido: Tipo de sonido (p.ej., "viento", "agua", "pajaro")
    
    Returns:
        Representación ASCII y morse del sonido
    """
    log_uso(sonido, "ASCII/Morse")
    
    # Mapeo de sonidos a patrones ASCII
    patrones_ascii = {
        "viento": """
        ∿∿∿∿∿∿∿∿∿∿∿∿∿∿
        ≈≈≈≈≈≈≈≈≈≈≈≈≈≈
        ∿∿∿∿∿∿∿∿∿∿∿∿∿∿
        """,
        "agua": """
        ≋≋≋≋≋≋≋≋≋≋≋≋
        ∽∽∽∽∽∽∽∽∽∽∽∽
        ≋≋≋≋≋≋≋≋≋≋≋≋
        """,
        "pajaro": """
        ◯◯◯◯  ~~ ^^
        ◯◯◯◯ ~  ~~
        ◯◯◯◯  ~~~
        """,
        "insecto": """
        ⚬⚬⚬⚬  ∴∴
        ⚬⚬⚬⚬ ∴ ∴
        ⚬⚬⚬⚬  ∴∴
        """,
    }
    
    # Mapeo a código morse (simplificado)
    morse_map = {
        "viento": "...- .. . -. - .",
        "agua": ".- --. ..- .-",
        "pajaro": ".--. .- .--- .- .-.",
        "insecto": "..- -. --- ..",
    }
    
    sonido_lower = sonido.lower().strip()
    
    salida = f"🎵 Representación de sonido: {sonido}\n\n"
    
    if sonido_lower in patrones_ascii:
        salida += "ASCII:\n" + patrones_ascii[sonido_lower] + "\n"
    else:
        salida += f"ASCII: [Patrón para '{sonido}' no disponible]\n"
    
    if sonido_lower in morse_map:
        salida += f"\nCódigo Morse:\n{morse_map[sonido_lower]}\n"
    else:
        salida += f"\nCódigo Morse: [Morse para '{sonido}' no disponible]\n"
    
    return salida

def generar_composicion_sonido(especificaciones: str) -> str:
    """
    Genera una composición de sonido con numpy basada en especificaciones y la guarda como archivo MP3.
    Crea composiciones ricas con múltiples capas de sonido (fondo ambiental, aves, variaciones).
    Requiere pydub y ffmpeg para generar archivos MP3.
    
    Args:
        especificaciones: Especificaciones del sonido (p.ej., "frecuencia: 440, duración: 2, tipo: humedal")
                        Tipos soportados: "humedal", "bosque", "agua", "viento", o "simple" para tono básico
    
    Returns:
        Información sobre la composición de sonido generada y ruta del archivo guardado
    """
    log_uso(especificaciones, "composición de sonido")
    
    try:
        # Parámetros por defecto
        sample_rate = 44100  # Hz
        duracion = 10  # segundos
        frecuencia = 440  # Hz (La4)
        tipo_sonido = "humedal"  # Tipo por defecto: composición rica
        
        # Limitar duración máxima a 10 segundos
        duracion_maxima = 10
        
        # Intentar extraer parámetros de la especificación
        spec_lower = especificaciones.lower()
        if "frecuencia" in spec_lower:
            # Extraer número después de "frecuencia"
            try:
                import re
                match = re.search(r'frecuencia[:\s]*(\d+)', spec_lower)
                if match:
                    frecuencia = int(match.group(1))
            except:
                pass
        
        if "duración" in spec_lower or "duracion" in spec_lower:
            try:
                import re
                match = re.search(r'duraci[óo]n[:\s]*(\d+\.?\d*)', spec_lower)
                if match:
                    duracion = min(float(match.group(1)), duracion_maxima)  # Limitar a máximo 10 segundos
            except:
                pass
        
        # Detectar tipo de sonido
        if "tipo:" in spec_lower:
            import re
            match = re.search(r'tipo[:\s]*(\w+)', spec_lower)
            if match:
                tipo_sonido = match.group(1).lower()
        elif any(tipo in spec_lower for tipo in ["humedal", "bosque", "agua", "viento", "simple"]):
            for tipo in ["humedal", "bosque", "agua", "viento", "simple"]:
                if tipo in spec_lower:
                    tipo_sonido = tipo
                    break
        
        # Generar tiempo
        tiempo = np.linspace(0, duracion, int(sample_rate * duracion), False)
        
        # Generar composición según el tipo
        if tipo_sonido == "simple":
            # Tono simple (comportamiento original)
            onda = np.sin(2 * np.pi * frecuencia * tiempo)
            audio_data = onda
        else:
            # Composiciones ricas con múltiples capas
            audio_data = np.zeros_like(tiempo)
            
            if tipo_sonido == "humedal":
                # Fondo de agua suave (amplitudes aumentadas)
                water_noise = np.random.normal(0, 0.15, tiempo.shape) * np.exp(-tiempo/duracion * 0.3)
                water_hum = 0.15 * np.sin(2 * np.pi * 30 * tiempo)
                # Filtro simple paso bajo
                filtered_noise = np.zeros_like(water_noise)
                for i in range(1, len(water_noise)):
                    filtered_noise[i] = 0.05 * water_noise[i] - 0.95 * filtered_noise[i-1]
                audio_data += water_hum + filtered_noise * 0.5
                
                # Sonidos de aves (múltiples llamadas) - amplitudes aumentadas
                num_birds = max(2, int(duracion / 2))
                for i in range(num_birds):
                    start_time = np.random.uniform(0.3, duracion - 0.5)
                    duration_bird = np.random.uniform(0.2, 0.4)
                    idx_start = int(start_time * sample_rate)
                    idx_end = min(int((start_time + duration_bird) * sample_rate), len(tiempo))
                    if idx_end > idx_start:
                        bird_freq = np.random.uniform(800, 2000)
                        mod_freq = np.random.uniform(3, 8)
                        t_bird = tiempo[idx_start:idx_end]
                        freq_modulated = bird_freq + 200 * np.sin(2 * np.pi * mod_freq * t_bird)
                        bird_sound = 0.4 * np.sin(2 * np.pi * freq_modulated * t_bird)
                        # Envolvente hanning
                        envelope = np.hanning(len(bird_sound))
                        audio_data[idx_start:idx_end] += bird_sound * envelope
                
                # Croar de rana ocasional - amplitudes aumentadas
                if duracion > 2:
                    num_croaks = max(1, int(duracion / 3))
                    for _ in range(num_croaks):
                        start_time = np.random.uniform(0.5, duracion - 0.3)
                        idx_start = int(start_time * sample_rate)
                        idx_end = min(int((start_time + 0.2) * sample_rate), len(tiempo))
                        if idx_end > idx_start:
                            frog_sound = 0.3 * np.sin(2 * np.pi * 300 * tiempo[idx_start:idx_end])
                            envelope = np.hanning(len(frog_sound))
                            audio_data[idx_start:idx_end] += frog_sound * envelope
                            
            elif tipo_sonido == "bosque":
                # Fondo de viento en hojas - amplitudes aumentadas
                wind_noise = np.random.normal(0, 0.12, tiempo.shape) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * tiempo))
                audio_data += wind_noise
                
                # Pájaros del bosque (trinos más complejos) - amplitudes aumentadas
                num_birds = max(2, int(duracion / 1.5))
                for i in range(num_birds):
                    start_time = np.random.uniform(0.2, duracion - 0.6)
                    duration_bird = np.random.uniform(0.4, 0.8)
                    idx_start = int(start_time * sample_rate)
                    idx_end = min(int((start_time + duration_bird) * sample_rate), len(tiempo))
                    if idx_end > idx_start:
                        base_freq = np.random.uniform(1000, 3000)
                        t_bird = tiempo[idx_start:idx_end]
                        # Trino con múltiples frecuencias
                        bird_sound = (0.35 * np.sin(2 * np.pi * base_freq * t_bird) +
                                    0.15 * np.sin(2 * np.pi * base_freq * 2 * t_bird) +
                                    0.1 * np.sin(2 * np.pi * base_freq * 3 * t_bird))
                        envelope = np.hanning(len(bird_sound))
                        audio_data[idx_start:idx_end] += bird_sound * envelope
                        
            elif tipo_sonido == "agua":
                # Agua corriente - amplitudes aumentadas
                water_noise = np.random.normal(0, 0.2, tiempo.shape)
                water_tone = 0.2 * np.sin(2 * np.pi * 50 * tiempo)
                # Filtro paso bajo más pronunciado
                filtered_water = np.zeros_like(water_noise)
                for i in range(1, len(water_noise)):
                    filtered_water[i] = 0.08 * water_noise[i] - 0.92 * filtered_water[i-1]
                audio_data += water_tone + filtered_water * 0.7
                
            elif tipo_sonido == "viento":
                # Viento variable - amplitudes aumentadas
                wind_base = np.random.normal(0, 0.15, tiempo.shape)
                wind_modulation = 0.15 * np.sin(2 * np.pi * 0.2 * tiempo)
                # Variación de intensidad
                intensity = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * tiempo)
                audio_data += (wind_base + wind_modulation) * intensity
        
        # Normalizar el audio con volumen adecuado
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            # Normalizar a un rango audible (0.8 para dejar algo de headroom)
            audio_data = audio_data / max_val * 0.8
        else:
            # Si no hay audio, generar un tono de prueba para evitar silencio
            audio_data = 0.3 * np.sin(2 * np.pi * 440 * tiempo)
        
        # Crear directorio de salida si no existe
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear directorio temporal para archivos WAV temporales
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = f"composicion_sonido_{timestamp}"
        
        # Guardar el archivo de audio
        ruta_archivo = None
        
        if not SCIPY_AVAILABLE:
            return "❌ Error: Se requiere 'scipy' para guardar archivos de audio. Instala con: pip install scipy"
        
        try:
            # Asegurar que el audio esté en el rango correcto [-1, 1]
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            # Convertir a int16 para WAV temporal (rango: -32768 a 32767)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Exportar a MP3 usando pydub (requerido)
            try:
                from pydub import AudioSegment
            except ImportError:
                return "❌ Error: Se requiere 'pydub' para generar archivos MP3. Instala con: pip install pydub\nNota: También necesitas tener ffmpeg instalado en tu sistema."
            
            # Primero guardar como WAV temporal en directorio separado
            archivo_wav_temp = os.path.join(temp_dir, f"{nombre_base}_temp.wav")
            wavfile.write(archivo_wav_temp, sample_rate, audio_int16)
            
            # Convertir WAV a MP3
            audio_segment = AudioSegment.from_wav(archivo_wav_temp)
            ruta_archivo = os.path.join(output_dir, f"{nombre_base}.mp3")
            audio_segment.export(ruta_archivo, format="mp3", bitrate="192k")
            
            # Eliminar archivo temporal
            os.remove(archivo_wav_temp)
                
        except Exception as e:
            return f"❌ Error al guardar archivo de audio: {str(e)}"
        
        tipo_display = tipo_sonido.capitalize() if tipo_sonido != "simple" else "Tono simple"
        
        salida = f"""
🎼 Composición de sonido generada:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Especificaciones:
   • Tipo: {tipo_display}
   • Duración: {duracion} segundos
   • Sample Rate: {sample_rate} Hz
   {"   • Frecuencia base: " + str(frecuencia) + " Hz" if tipo_sonido == "simple" else "   • Múltiples capas de sonido"}

🔊 Propiedades del audio:
   • Amplitud máxima: {np.max(np.abs(audio_data)):.4f} (normalizado)
   • Número de muestras: {len(audio_data)}
   • RMS: {np.sqrt(np.mean(audio_data**2)):.4f}

✅ Archivo guardado exitosamente
📁 Ruta: {ruta_archivo}
        """
        
        return salida.strip()
    
    except Exception as e:
        return f"❌ Error al generar composición: {str(e)}"

def explorar_especies_sonoras(ubicacion: str) -> str:
    """
    Explora especies sonoras comunes en una ubicación específica.
    
    Args:
        ubicacion: Ubicación a explorar (p.ej., "humedal conejera", "bogotá")
    
    Returns:
        Lista de especies sonoras encontradas
    """
    log_uso(ubicacion, "exploración de especies sonoras")
    
    # Especies sonoras de Bogotá y alrededores
    especies_por_lugar = {
        "humedal conejera": [
            "🦆 Tinguas (Aramides): Sonidos guturales, croadores",
            "🐦 Chirlobirlos (Tachycineta albiventer): Trinos agudos",
            "🦢 Garzas: Graznidos profundos",
            "🐸 Ranas: Croidos estridentes",
            "🪳 Insectos acuáticos: Zumbidos y chasquidos",
            "💨 Viento en juncos: Susurros rítmicos"
        ],
        "bogotá": [
            "🦅 Águilas: Silbidos penetrantes",
            "🦜 Loros: Chillidos variados",
            "🌳 Pájaros bosque nublado: Trinos complejos",
            "🐸 Anfibios: Croidos característicos",
            "🪲 Insectos: Zumbidos y chirridos",
            "💨 Viento páramo: Sonidos silbantes"
        ],
        "bosque": [
            "🦅 Rapaces: Silbidos agudos",
            "🐦 Pájaros cantores: Melodías complejas",
            "🦎 Insectos: Chirridos y zumbidos",
            "🦇 Murciélagos: Ecolocalización (ultrasónica)",
            "🌿 Hojas al viento: Susurros suave",
            "💧 Agua corriente: Murmullos constantes"
        ]
    }
    
    ubicacion_lower = ubicacion.lower().strip()
    
    salida = f"🎵 Especies sonoras de: {ubicacion}\n"
    salida += "━" * 50 + "\n\n"
    
    encontrado = False
    for lugar, especies in especies_por_lugar.items():
        if lugar in ubicacion_lower:
            for especie in especies:
                salida += f"{especie}\n"
            encontrado = True
            break
    
    if not encontrado:
        # Retornar especies genéricas si no se encuentra la ubicación
        salida += "Especies sonoras generales:\n"
        for especies_lista in especies_por_lugar.values():
            for especie in especies_lista[:3]:
                salida += f"{especie}\n"
    
    return salida

