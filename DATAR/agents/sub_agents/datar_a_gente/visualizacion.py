"""
Herramienta para generar visualizaciones del río emocional
"""
import io
import os
from datetime import datetime
from pathlib import Path as FilePath
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np
import google.genai.types as types


# Mapeo de emojis a colores emocionales
EMOJI_COLORES = {
    # Alegría y positividad
    '😊': '#FFD700', '😃': '#FFA500', '😄': '#FFB347', '🥰': '#FF69B4',
    '😍': '#FF1493', '🤗': '#FF6B9D', '😁': '#FFDB58', '🌟': '#FFD700',
    '✨': '#E6E6FA', '💖': '#FF69B4', '💕': '#FFB6C1', '❤️': '#DC143C',
    '🌸': '#FFB7C5', '🌺': '#FF6B9D', '🌼': '#FFDB58',

    # Calma y serenidad
    '😌': '#87CEEB', '😇': '#B0E0E6', '🌊': '#4682B4', '💙': '#1E90FF',
    '💚': '#3CB371', '🌿': '#90EE90', '🍃': '#98FB98', '🌱': '#32CD32',
    '☁️': '#E0E0E0', '🌙': '#F0E68C', '⭐': '#FFFACD',

    # Tristeza y melancolía
    '😢': '#4169E1', '😭': '#0000CD', '😔': '#6495ED', '💔': '#8B0000',
    '🌧️': '#778899', '☔': '#696969', '💧': '#ADD8E6',

    # Energía y pasión
    '🔥': '#FF4500', '⚡': '#FFFF00', '💥': '#FF6347', '🌋': '#DC143C',

    # Naturaleza y crecimiento
    '🌳': '#228B22', '🌲': '#006400', '🌴': '#00FF00', '🪴': '#3CB371',

    # Misterio y profundidad
    '🌑': '#2F4F4F', '🖤': '#000000', '💜': '#8B008B', '🔮': '#9370DB',

    # Neutral
    'default': '#A9A9A9'
}


def obtener_color_emoji(emoji):
    """Obtiene el color asociado a un emoji"""
    return EMOJI_COLORES.get(emoji, EMOJI_COLORES['default'])


def generar_rio_emocional(emojis_texto: str) -> bytes:
    """
    Genera una visualización artística del río emocional

    Args:
        emojis_texto: String con los emojis separados por espacios

    Returns:
        bytes: Imagen PNG del río emocional
    """
    # Extraer emojis individuales
    emojis = emojis_texto.split()
    if not emojis:
        emojis = ['❓']

    # Configurar la figura
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#F5F5F5')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Título poético
    ax.text(5, 9.5, 'El Río de tu Pensamiento',
            fontsize=24, ha='center', va='top',
            weight='bold', color='#2C3E50')

    # Generar el flujo del río
    num_emojis = len(emojis)
    x_positions = np.linspace(1, 9, num_emojis)

    # Crear una onda sinusoidal para el río
    x_river = np.linspace(0, 10, 200)
    y_base = 5

    # Dibujar el río con colores que fluyen
    for i in range(len(emojis)):
        if i < len(emojis) - 1:
            x_start = x_positions[i]
            x_end = x_positions[i + 1]

            # Seleccionar puntos del río en este segmento
            mask = (x_river >= x_start) & (x_river <= x_end)
            x_segment = x_river[mask]

            # Crear ondas suaves
            y_wave = y_base + 0.3 * np.sin(2 * np.pi * x_segment / 2)

            # Color del segmento basado en el emoji
            color = obtener_color_emoji(emojis[i])

            # Dibujar el segmento del río con degradado
            for j in range(len(x_segment) - 1):
                alpha = 0.6 + 0.4 * (j / len(x_segment))
                ax.plot(x_segment[j:j+2], y_wave[j:j+2],
                       color=color, linewidth=15, alpha=alpha,
                       solid_capstyle='round')

    # Dibujar círculos con los emojis
    for i, (emoji, x_pos) in enumerate(zip(emojis, x_positions)):
        color = obtener_color_emoji(emoji)

        # Posición en la onda
        y_pos = y_base + 0.3 * np.sin(2 * np.pi * x_pos / 2)

        # Círculo de fondo
        circle = plt.Circle((x_pos, y_pos), 0.4,
                           color=color, alpha=0.7, zorder=10)
        ax.add_patch(circle)

        # Emoji en el centro
        ax.text(x_pos, y_pos, emoji,
               fontsize=32, ha='center', va='center', zorder=11)

        # Pequeña etiqueta con número de secuencia
        ax.text(x_pos, y_pos - 0.7, f'{i+1}',
               fontsize=12, ha='center', va='top',
               color='#555', weight='bold')

    # Agregar texto poético al final
    num_total = len(emojis)
    texto_poético = f'Un camino de {num_total} {"paso" if num_total == 1 else "pasos"} emocionales'
    ax.text(5, 1.5, texto_poético,
           fontsize=14, ha='center', va='center',
           style='italic', color='#555')

    # Agregar línea de horizonte sutil
    ax.axhline(y=10, color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(y=0, color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)

    # Guardar en bytes
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='#F5F5F5')
    plt.close(fig)

    buf.seek(0)
    return buf.read()


async def crear_visualizacion(emojis: str) -> str:
    """
    Tool del agente para crear y guardar visualización del río emocional

    Args:
        emojis: String con los emojis a visualizar (ej: "😊 🌊 💚 🌟")

    Returns:
        str: Mensaje de confirmación
    """
    try:
        # Generar la visualización
        imagen_bytes = generar_rio_emocional(emojis)

        # Crear artifact
        artifact = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type="image/png"
        )

        # Guardar (esto requiere context, se configurará en el agente)
        return f"✨ He creado una visualización de tu río emocional con los emojis: {emojis}"

    except Exception as e:
        return f"⚠️ Hubo un problema al crear la visualización: {str(e)}"


#---- Aquí empezó la prueba usando Numpy/Pillow  ----#
#---- Aquí empezó la prueba usando Numpy/Pillow  ----#
#---- Aquí empezó la prueba usando Numpy/Pillow  ----#

def interpretar_texto_a_parametros(texto: str) -> dict:
    """
    Interpreta un texto de manera abstracta y lo convierte en parámetros matemáticos

    Args:
        texto: El texto a interpretar

    Returns:
        dict: Diccionario con parámetros matemáticos interpretados
    """
    # Análisis básico del texto
    longitud = len(texto)
    vocales = sum(1 for c in texto.lower() if c in 'aeiouáéíóú')
    consonantes = sum(1 for c in texto.lower() if c.isalpha() and c not in 'aeiouáéíóú')
    espacios = texto.count(' ')
    palabras = len(texto.split())

    # Calcular "intensidad emocional" basada en puntuación
    signos_exclamacion = texto.count('!')
    signos_pregunta = texto.count('?')
    signos_puntos = texto.count('.')

    # Crear semilla única basada en el texto para reproducibilidad
    semilla = sum(ord(c) for c in texto) % 10000

    return {
        'longitud': longitud,
        'vocales': vocales,
        'consonantes': consonantes,
        'espacios': espacios,
        'palabras': palabras,
        'intensidad': signos_exclamacion * 1.5 + signos_pregunta * 0.8, # Más peso a exclamación
        'calma': signos_puntos * 0.7, # Más puntos = más calma
        'frecuencia_onda': max(0.5, vocales / 7),  # Más vocales = más ondas base
        'amplitud_onda': max(0.1, consonantes / 15),  # Más consonantes = más amplitud base
        'num_puntos': max(300, longitud * 15),  # Más texto = más puntos totales para detalle
        'semilla': semilla,
    }


def generar_puntos_numpy(parametros: dict, img_width: int, img_height: int) -> list[tuple[int, int]]:
    """
    Genera puntos usando NumPy basándose en los parámetros interpretados,
    dividido en fases narrativas con lógica ajustada a la emoción.

    Args:
        parametros: Diccionario con parámetros matemáticos
        img_width (int): Ancho del canvas para límites.
        img_height (int): Alto del canvas para límites.

    Returns:
        list: Una lista de tuplas (x, y) con las coordenadas del trazo principal.
    """
    np.random.seed(parametros['semilla'])

    # Normalizar intensidad y calma para que estén en un rango manejable (0-1)
    # Ajustar estos valores máximos según la escala esperada de tus parámetros
    max_intensidad = 10 # Si la intensidad calculada puede llegar a 10
    max_calma = 5    # Si la calma calculada puede llegar a 5

    norm_intensidad = np.clip(parametros['intensidad'] / max_intensidad, 0, 1)
    norm_calma = np.clip(parametros['calma'] / max_calma, 0, 1)

    # --- Configuración global del trazo ---
    num_puntos_total = parametros['num_puntos']
    
    # Punto de inicio completamente aleatorio en el canvas, con variación emocional
    start_x = np.random.randint(50, img_width - 50) + int(norm_intensidad * 50 - norm_calma * 20)
    start_y = np.random.randint(50, img_height - 50) + int(norm_calma * 50 - norm_intensidad * 20)
    current_x, current_y = start_x, start_y

    all_main_trace_points = [] # Puntos principales del trazo

    # --- Definición de Fases ---
    # Los coeficientes son "mágicos" y ajustados para dar el efecto deseado
    
    # Fase 1: Acelera con decisión (🏃🏼‍♀️)
    # Impulso mayor con intensidad, menor con calma. Amplitud más cerrada con intensidad (fuerte=cerrada). Frecuencia mayor con intensidad.
    num_puntos_fase1 = int(num_puntos_total * (0.25 + norm_intensidad * 0.1 - norm_calma * 0.05))
    num_puntos_fase1 = np.clip(num_puntos_fase1, 30, num_puntos_total // 2)
    
    # Impulso: Aumenta con intensidad, disminuye con calma
    avance_x1 = (2 + norm_intensidad * 3) * (1 - norm_calma * 0.5)
    avance_y1 = (-3 - norm_intensidad * 3) * (1 - norm_calma * 0.5) # Negativo para ir hacia arriba por defecto
    # Amplitud: Cerrada con intensidad, abierta con calma
    amplitud_onda1 = parametros['amplitud_onda'] * (1 - norm_intensidad * 0.7) + norm_calma * 15 # + norm_calma para asegurar algo de apertura
    # Frecuencia: Mayor con intensidad (ansiedad)
    frecuencia_onda1 = parametros['frecuencia_onda'] * (1 + norm_intensidad * 0.8) * (1 - norm_calma * 0.4)
    ruido_aleatorio1 = (10 + norm_intensidad * 10) * (1 - norm_calma * 0.5)


    # Fase 2: Estallido de alegría (🎉) / Expansión, dispersión
    # Amplitud muy abierta con calma, más cerrada pero dispersa con intensidad. Frecuencia mucho mayor con intensidad.
    num_puntos_fase2 = int(num_puntos_total * (0.35 + norm_intensidad * 0.2 - norm_calma * 0.1))
    num_puntos_fase2 = np.clip(num_puntos_fase2, 30, num_puntos_total // 2)

    avance_x2 = (1.5 + norm_intensidad * 2) * (1 - norm_calma * 0.3)
    avance_y2 = (-2.5 - norm_intensidad * 2) * (1 - norm_calma * 0.3)
    amplitud_onda2 = parametros['amplitud_onda'] * (1 - norm_intensidad * 0.3) + norm_calma * 30 # Muy abierta con calma, más contenida con intensidad
    frecuencia_onda2 = parametros['frecuencia_onda'] * (1 + norm_intensidad * 1.5) * (1 - norm_calma * 0.2)
    ruido_aleatorio2 = (25 + norm_intensidad * 30) * (1 + (1 - norm_calma) * 0.5)


    # Fase 3: Se contrae con delicadeza / Incertidumbre (🤏🏽)
    # Impulso bajo. Amplitud muy cerrada con intensidad, más abierta con calma. Frecuencia alta con incertidumbre.
    num_puntos_fase3 = num_puntos_total - num_puntos_fase1 - num_puntos_fase2
    num_puntos_fase3 = max(10, num_puntos_fase3)

    avance_x3 = (0.5 + (1 - norm_calma) * 1.5) * (1 - norm_intensidad * 0.3) # Más errático sin calma
    avance_y3 = (-0.5 - (1 - norm_calma) * 1.5) * (1 - norm_intensidad * 0.3)
    amplitud_onda3 = parametros['amplitud_onda'] * (1 - norm_intensidad * 0.9) + (1 - norm_calma) * 10 # Muy cerrada con intensidad, abierta y zigzagueante con incertidumbre
    frecuencia_onda3 = parametros['frecuencia_onda'] * (1 + (1 - norm_calma) * 2 + norm_intensidad * 0.5)
    ruido_aleatorio3 = (15 + (1 - norm_calma) * 20) * (1 + norm_intensidad * 0.5)


    # --- Generación de Puntos por Fases ---
    phases_params = [
        (num_puntos_fase1, avance_x1, avance_y1, amplitud_onda1, frecuencia_onda1, ruido_aleatorio1),
        (num_puntos_fase2, avance_x2, avance_y2, amplitud_onda2, frecuencia_onda2, ruido_aleatorio2),
        (num_puntos_fase3, avance_x3, avance_y3, amplitud_onda3, frecuencia_onda3, ruido_aleatorio3),
    ]

    wave_offset = 0 # Para un desplazamiento continuo de la onda

    for i_phase, (n_puntos, av_x, av_y, amp_onda, freq_onda, ruido) in enumerate(phases_params):
        for i in range(n_puntos):
            # Frecuencia base aleatoria, influenciada por la emoción
            random_freq_factor = (0.8 + np.random.rand() * 0.4) # Variación aleatoria
            current_freq_x = freq_onda * 0.05 * random_freq_factor
            current_freq_y = freq_onda * 0.03 * random_freq_factor

            onda_x = amp_onda * np.sin((i + wave_offset) * current_freq_x)
            onda_y = amp_onda * np.cos((i + wave_offset) * current_freq_y)

            dx = av_x + np.random.normal(0, ruido / 10) + onda_x
            dy = av_y + np.random.normal(0, ruido / 10) + onda_y

            current_x += dx
            current_y += dy
            
            # Asegurar que el trazo permanezca dentro de límites razonables
            current_x = np.clip(current_x, 20, img_width - 20) # Ajuste de clip para más margen
            current_y = np.clip(current_y, 20, img_height - 20)

            all_main_trace_points.append((int(current_x), int(current_y)))
        
        wave_offset += n_puntos # Para que la onda siga desde donde quedó

    return all_main_trace_points


def generar_imagen_texto(texto: str) -> Image.Image:
    """
    Genera una imagen interpretativa del texto usando Pillow,
    con el trazo dividido en fases narrativas y grosor dinámico,
    y múltiples estilos de trazo.

    Args:
        texto: El texto a visualizar

    Returns:
        Image: Imagen PIL generada
    """
    # Interpretar el texto
    parametros = interpretar_texto_a_parametros(texto)

    # Crear canvas
    width, height = 1000, 700
    imagen = Image.new('RGB', (width, height), color='#F5F5F5')
    draw = ImageDraw.Draw(imagen)

    # Normalizar intensidad y calma para el grosor y estilo del trazo
    max_intensidad = 10
    max_calma = 5
    norm_intensidad = np.clip(parametros['intensidad'] / max_intensidad, 0, 1)
    norm_calma = np.clip(parametros['calma'] / max_calma, 0, 1)

    # Generar puntos del trazo principal
    main_trace_points = generar_puntos_numpy(parametros, width, height)

    # --- Título ---
    titulo = "Trazo del Pensamiento"
    try:
        from PIL import ImageFont
        font_path = "arial.ttf" # Asegúrate de que esta fuente exista o usa una por defecto
        try:
            font = ImageFont.truetype(font_path, 24)
            font_small = ImageFont.truetype(font_path, 12)
        except IOError:
            font = ImageFont.load_default() # Fallback
            font_small = ImageFont.load_default()
    except ImportError:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((width // 2, 30), titulo, fill="#000000", anchor='mm', font=font)


    # --- Selección de Estilo de Trazo y Dibujo ---
    if not main_trace_points or len(main_trace_points) < 2:
        print("No hay suficientes puntos para dibujar el trazo.")
        draw.text((width // 2, height // 2), "No se pudo generar el trazo", fill="#FF0000", anchor='mm', font=font)
        return imagen

    # Lógica de selección de estilo de trazo
    if norm_intensidad > 0.8 and norm_calma < 0.2:
        # Estilo "Disperso" / "Nube de Puntos": Para caos, confusión
        print("Estilo de trazo: Disperso")
        # Dibuja puntos pequeños alrededor de la trayectoria
        for x, y in main_trace_points:
            num_dots = np.random.randint(5, 15) # Más puntos si es más intenso
            for _ in range(num_dots):
                dx = np.random.normal(0, 10 + norm_intensidad * 20) # Mayor dispersión
                dy = np.random.normal(0, 10 + norm_intensidad * 20)
                dot_x, dot_y = int(x + dx), int(y + dy)
                draw.ellipse([dot_x-2, dot_y-2, dot_x+2, dot_y+2], fill="black", outline="black")

    elif norm_calma > 0.7 and norm_intensidad < 0.3:
        # Estilo "Solitario" / "Fino": Para reflexión, sutileza
        print("Estilo de trazo: Solitario")
        # Una sola línea muy fina, quizás con opacidad variable
        base_width = 1
        color = (0, 0, 0, int(255 * (0.3 + norm_calma * 0.7))) # Más opaco con calma
        
        # Para dibujar una línea con opacidad se necesita un Image.RGBA y luego combinar
        temp_img = Image.new('RGBA', (width, height), (0,0,0,0))
        temp_draw = ImageDraw.Draw(temp_img)
        for i in range(len(main_trace_points) - 1):
            temp_draw.line([main_trace_points[i], main_trace_points[i + 1]], fill=color, width=base_width, joint="curve")
        imagen = Image.alpha_composite(imagen.convert('RGBA'), temp_img).convert('RGB')
        draw = ImageDraw.Draw(imagen) # Actualizar el objeto draw
        
    elif norm_intensidad > 0.5 and norm_calma > 0.4:
        # Estilo "Sólido" / "Marcado": Determinación, firmeza
        print("Estilo de trazo: Sólido")
        # Un trazo más grueso y continuo
        dynamic_width = int(5 + norm_intensidad * 8 - norm_calma * 2) # Más grueso con intensidad
        dynamic_width = max(2, dynamic_width) # Grosor mínimo
        
        for i in range(len(main_trace_points) - 1):
            # Reducción de grosor al final si hay poca calma
            current_width = dynamic_width
            if i > len(main_trace_points) * 0.8 and norm_calma < 0.5:
                reduction_factor = (1 - (i - len(main_trace_points) * 0.8) / (len(main_trace_points) * 0.2))
                current_width = int(current_width * reduction_factor)
            draw.line([main_trace_points[i], main_trace_points[i + 1]], fill="black", width=max(1, current_width), joint="curve")

    elif norm_intensidad > 0.3 and norm_calma < 0.5 and parametros['signos_pregunta'] > 0: # Añadir signo de pregunta como factor
        # Estilo "Fragmentado" / "Interrumpido": Indecisión, interrupción
        print("Estilo de trazo: Fragmentado")
        segment_length_base = 15 + norm_intensidad * 10
        gap_length_base = 5 + (1 - norm_calma) * 10

        i = 0
        while i < len(main_trace_points) - 1:
            segment_length = int(segment_length_base * (0.8 + np.random.rand() * 0.4))
            gap_length = int(gap_length_base * (0.8 + np.random.rand() * 0.4))
            
            end_segment = min(i + segment_length, len(main_trace_points) -1)
            if i < end_segment:
                draw.line(main_trace_points[i:end_segment+1], fill="black", width=2, joint="curve")
            
            i = end_segment + gap_length # Salta el "gap"
            
    else:
        # Estilo "Básico Orgánico" (similar al original, pero una sola línea fluida)
        print("Estilo de trazo: Básico Orgánico")
        base_width = 2
        # El grosor del trazo principal varía con la intensidad
        dynamic_width_factor = 1 + norm_intensidad * 3 - norm_calma * 1.5
        
        for i in range(len(main_trace_points) - 1):
            current_width = int(base_width * dynamic_width_factor)
            # Reducir el grosor hacia el final si hay baja calma (incertidumbre)
            if i > len(main_trace_points) * 0.7:
                 reduction_factor = (1 - (i - len(main_trace_points) * 0.7) / (len(main_trace_points) * 0.3))
                 current_width = int(current_width * reduction_factor * (1 + (1 - norm_calma) * 2))

            draw.line([main_trace_points[i], main_trace_points[i + 1]], fill="black", width=max(1, current_width), joint="curve")



    # Fecha y hora de creación en la parte inferior
    fecha_hora = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    draw.text((width // 2, height - 20), fecha_hora, fill='#555', anchor='mm', font=font_small)

    return imagen

#---- Aquí terminó la prueba usando Numpy/Pillow  ----#
#---- Aquí terminó la prueba usando Numpy/Pillow  ----#
#---- Aquí terminó la prueba usando Numpy/Pillow  ----#



def guardar_imagen_texto(texto: str) -> str:
    """
    Genera y guarda una imagen interpretativa del texto

    Args:
        texto: El texto a visualizar

    Returns:
        str: Ruta donde se guardó la imagen
    """
    # Generar la imagen
    imagen = generar_imagen_texto(texto)

    # Crear nombre de archivo único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"trazo_{timestamp}.png"

    # Determinar ruta de guardado
    proyecto_root = FilePath(__file__).parent.parent
    carpeta_imagenes = proyecto_root / "imagenes_generadas"
    carpeta_imagenes.mkdir(exist_ok=True)

    ruta_completa = carpeta_imagenes / nombre_archivo

    # Guardar imagen
    imagen.save(ruta_completa, 'PNG')

    return str(ruta_completa)
