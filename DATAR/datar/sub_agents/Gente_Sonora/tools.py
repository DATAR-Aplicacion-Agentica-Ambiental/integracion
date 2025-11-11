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
    Genera una composición de sonido con numpy basada en especificaciones.
    
    Args:
        especificaciones: Especificaciones del sonido (p.ej., "frecuencia: 440, duración: 2")
    
    Returns:
        Información sobre la composición de sonido generada
    """
    log_uso(especificaciones, "composición de sonido")
    
    try:
        # Parámetros por defecto
        sample_rate = 44100  # Hz
        duracion = 2  # segundos
        frecuencia = 440  # Hz (La4)
        
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
                    duracion = float(match.group(1))
            except:
                pass
        
        # Generar forma de onda
        tiempo = np.linspace(0, duracion, int(sample_rate * duracion), False)
        onda = np.sin(2 * np.pi * frecuencia * tiempo)
        
        # Normalizar
        onda = onda * 32767 / np.max(np.abs(onda))
        onda = onda.astype(np.int16)
        
        salida = f"""
🎼 Composición de sonido generada:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Especificaciones:
   • Frecuencia: {frecuencia} Hz
   • Duración: {duracion} segundos
   • Sample Rate: {sample_rate} Hz
   • Forma de onda: Senoidal

🔊 Propiedades de la onda:
   • Amplitud máxima: {np.max(np.abs(onda))} (normalizado)
   • Número de muestras: {len(onda)}
   • RMS: {np.sqrt(np.mean(onda**2)):.2f}

✅ Composición lista para reproducción o guardado
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

