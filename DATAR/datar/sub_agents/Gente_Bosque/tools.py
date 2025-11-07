# tools.py - Herramientas para el Agente Bosque

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def log_uso(fuente, tipo):
    """Guarda registro de cada fuente usada."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Usando {tipo}: {fuente}", flush=True)

def leer_pagina(url: str) -> str:
    """
    Lee y devuelve texto de una página web.

    Args:
        url: URL de la página web a leer

    Returns:
        Texto extraído de la página (hasta 4000 caracteres)
    """
    log_uso(url, "página web")
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:4000]
    except Exception as e:
        return f"Error al leer la página: {str(e)}"

def explorar_pdf(tema: str) -> str:
    """
    Explora temas relacionados con filosofía de la biología, simbiosis,
    concepto de individuo y asociaciones.

    Args:
        tema: Tema a explorar (filosofia_fungi, margullis, hongo_planta, donna)

    Returns:
        Información filosófica sobre el tema
    """
    tema = tema.lower().strip()

    # Respuestas predefinidas sobre temas filosóficos
    respuestas = {
        "filosofia_fungi": """
📄 Tema: Filosofía de los hongos

Resumen: Los hongos desafían nuestra noción tradicional de individualidad.
No son ni plantas ni animales, sino una forma de vida que cuestiona los límites
entre organismos. Un hongo puede extenderse por kilómetros como un solo organismo,
o puede existir en simbiosis con las raíces de los árboles.

Preguntas reflexivas:
- ¿Dónde termina un individuo y comienza otro en un bosque interconectado por redes fúngicas?
- ¿Qué significa ser un "individuo" si tu supervivencia depende completamente de otros organismos?
- ¿Podemos aplicar conceptos de cooperación fúngica a nuestras propias sociedades humanas?
        """,
        "margullis": """
📄 Tema: Teoría de la endosimbiosis de Lynn Margulis

Resumen: Margulis propuso que las células eucariotas se originaron por simbiosis entre
diferentes organismos procarióticos. Las mitocondrias y cloroplastos fueron alguna vez
bacterias independientes. Esto implica que la cooperación, no solo la competencia,
es fundamental para la evolución.

Preguntas reflexivas:
- Si nuestras células son el resultado de antiguas simbiosis, ¿somos realmente individuos o ecosistemas ambulantes?
- ¿Qué papel juega la cooperación en la evolución de la vida compleja?
- ¿Cómo cambia nuestra relación con la naturaleza si reconocemos que llevamos otros organismos dentro de nosotros?
        """,
        "hongo_planta": """
📄 Tema: Simbiosis entre hongos y plantas

Resumen: Las micorrizas son asociaciones simbióticas entre hongos y raíces de plantas.
El hongo ayuda a la planta a absorber nutrientes del suelo, mientras la planta
proporciona carbohidratos al hongo. Esta relación es tan antigua y fundamental
que permitió a las plantas colonizar la tierra hace 450 millones de años.

Preguntas reflexivas:
- ¿Dónde está el límite entre el hongo y la planta en una micorriza?
- ¿Pueden existir identidades separadas cuando dos organismos son completamente interdependientes?
- ¿Qué nos enseña la micorriza sobre las relaciones humanas y la interdependencia?
        """,
        "donna": """
📄 Tema: Pensamiento multiespecie (Donna Haraway)

Resumen: Haraway propone que debemos pensar más allá del antropocentrismo y
reconocer que vivimos en un mundo de "compañeros de especies". Los humanos no están
separados de la naturaleza, sino que somos parte de una red de relaciones con otros seres.

Preguntas reflexivas:
- ¿Cómo cambia nuestra percepción del mundo si nos vemos como parte de una red multiespecie?
- ¿Qué responsabilidades tenemos hacia otros seres con los que compartimos el planeta?
- ¿Puede el concepto de "individuo humano" sostenerse cuando dependemos de billones de microbios?
        """
    }

    if tema in respuestas:
        return respuestas[tema]
    else:
        return f"No se encontró información específica sobre '{tema}'. Temas disponibles: {', '.join(respuestas.keys())}"

def inferir_especies(descripcion: str) -> str:
    """
    Infiere posibles especies presentes según las condiciones ambientales descritas.

    Args:
        descripcion: Descripción de las condiciones del entorno (humedad, temperatura, etc.)

    Returns:
        Lista de especies que podrían estar presentes
    """
    desc_lower = descripcion.lower()
    especies_sugeridas = []

    # Análisis de condiciones
    condiciones = {
        "humedo": ("humedad" in desc_lower or "mojad" in desc_lower or "lluvia" in desc_lower or "charcos" in desc_lower or "llovido" in desc_lower or "rocío" in desc_lower),
        "seco": ("seco" in desc_lower or "árido" in desc_lower),
        "sombra": ("sombr" in desc_lower or "nublado" in desc_lower),
        "noche": ("anochecer" in desc_lower or "oscur" in desc_lower or "atardecer" in desc_lower),
        "sol": ("sol" in desc_lower or "luz" in desc_lower or "brillante" in desc_lower),
        "frio": ("frí" in desc_lower or "helad" in desc_lower),
        "calor": ("calor" in desc_lower or "caliente" in desc_lower  or "cálido" in desc_lower),
        #"agua": ("agua" in desc_lower or "río" in desc_lower or "quebrada" in desc_lower)
    }

    # Sugerencias según condiciones
    if condiciones["humedo"] and condiciones["sombra"]:
        especies_sugeridas.extend([
            "Musgos y hepáticas: Campylopus, Fissidens, Sphagnum, Plagiochila, Metzgeria  ",
            "Microorganismos del suelo - Bacterias (Pseudomonas, Acinetobacter,Pedomicrobium), hongos (Glomus, Acaulospora), protozoos (amebas,Chlamidomonas, Euglen )",
            "Hongos saprofitos: Phellinus, Coprinellus, Ganoderma, Lactarius  ",
            "Insectos: áfidos (Aphididae), escarabajos picudos (Curculionidae)",
            "Arácnidos: opiliones (Sclerosomatidae)",
            "Líquenes: Cora, Usnea"
    
       
        ])
    if condiciones["noche"]:
        especies_sugeridas.extend([
            "Insectos: Polilla bruja (Ascalapha odorata)"
            "Arácnidos: opiliones "
            "Microorganismos del suelo - Bacterias (Pseudomonas, Acinetobacter,Pedomicrobium), hongos (Glomus, Acaulospora), protozoos (amebas,Chlamidomonas, Euglen )",

        
        ])   

#    if condiciones["agua"]:
#        especies_sugeridas.extend([
#            "Briofitas acuáticas - Musgos que crecen en rocas húmedas",
#            "Insectos acuáticos - Larvas de libélulas, efímeras",
#            "Anfibios - Ranas y salamandras"
#        ])

    if condiciones["sol"]:
        especies_sugeridas.extend([
            "Herbáceas: Diente de león (Taraxacum officinale), trébol blanco (Trifolium repens), morado",
            "Líquenes: Cladonia, Lecanora caesiorubella, Flavopunctelia flaventior,Teloschistes exilis ",
            "Insectos: Escarabajos de hojas (Chrysomelidae), Avispas parasitoides (Ichneumonidae), moscas de las flores (Syrphidae), abejorro (Bombus hortulanus), mariposas amarillas (Eurema)",
            "Arañas de telas orbiculares (Araneidae), Araña espinosa (Micrathena bogota)"
        ])

    if condiciones["frio"]:
        especies_sugeridas.extend([
          
            "Musgos y hepáticas adaptados al frío como Campylopus, Fissidens, Sphagnum, Plagiochila, Metzgeria  ",
            "Líquenes - Resistentes a condiciones extremas"
        ])

    
    especies_sugeridas.extend([
        "Microorganismos del suelo - Bacterias (Pseudomonas, Acinetobacter,Pedomicrobium), hongos (Glomus, Acaulospora), protozoos (amebas,Chlamidomonas, Euglen )",
        "Colémbolos - Pequeños artrópodos del suelo",
        "Ácaros - Arácnidos microscópicos",
        "Arañas fantasma(Anyphaenidae)",
        "Gorgojos (Compsus canescens)",
    ])

    if especies_sugeridas:
        salida = "🌿 Basándome en tu descripción, estas especies podrían estar presentes:\n\n"
        for i, especie in enumerate(especies_sugeridas[:8], 1):
            salida += f"{i}. {especie}\n"
        salida += "\n💡 Estas son solo algunas posibilidades basadas en las condiciones que describiste."
    else:
        salida = "No pude inferir condiciones claras a partir de tu descripción."

    return salida

def explorar(termino: str) -> str:
    """
    Busca información sobre un término en fuentes predefinidas.

    Args:
        termino: Término a buscar

    Returns:
        Información encontrada
    """
    fuentes = {
        "pot": "https://bogota.gov.co/bog/pot-2022-2035/",
        "biomimética": "https://asknature.org/",
        "suelo": "https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2019.02872/full",
        "briofitas": "https://stri.si.edu/es/noticia/briofitas",
    }

    termino_lower = termino.lower().strip()

    if termino_lower in fuentes:
        return leer_pagina(fuentes[termino_lower])
    else:
        return f"Término '{termino}' no encontrado. Fuentes disponibles: {', '.join(fuentes.keys())}"

def crear_mapa_emocional(descripcion: str) -> str:
    """
    Esta función genera un mapa emocional del Bosque La Macarena (Bogotá) utilizando la librería `prettymaps`. 
    A partir de una descripción textual, detecta una emoción asociada y aplica una paleta de colores 
    contrastante para representar visualmente ese estado emocional en un mapa del área.
    """
    import os
    from datetime import datetime
    import matplotlib
    matplotlib.use('Agg')  # Se configura matplotlib para generar gráficos sin interfaz gráfica.
    import matplotlib.pyplot as plt
    from prettymaps import plot
    import colorsys

    # Coordenadas fijas del cosque de La Macarena.
    coordenadas = (4.614773, -74.063173)

    # Paletas de colores predefinidas, cada una asociada a una emoción distinta.
    # Se eligen combinaciones contrastantes para que los mapas sean visualmente diferenciables.
    paletas = {
        "serenidad":  {"background": "#d8f3dc", "forest": "#1b4332", "water": "#95d5b2"},
        "asombro":    {"background": "#fff8b5", "forest": "#289e4b", "water": "#9bf6ff"},
        "nostalgia":  {"background": "#e0b1cb", "forest": "#5e548e", "water": "#9a8c98"},
        "vitalidad":  {"background": "#D3D156", "forest": "#f3722c", "water": "#0755ff"},
        "humedad":    {"background": "#a9def9", "forest": "#4cc9f0", "water": "#4361ee"},
        "incomodidad":{"background": "#575455", "forest": "#f48c06", "water": "#9d0208"},
        "gratitud":   {"background": "#fefae0", "forest": "#606c38", "water": "#283618"},
    }

    # Diccionario que relaciona palabras clave con emociones.
    # Permite interpretar una descripción y asignarle una categoría emocional.
    claves = {
        "tranquilo": "serenidad", "calma": "serenidad", "paz": "serenidad",
        "brillante": "asombro", "sorpresa": "asombro", "claro": "asombro",
        "oscuro": "nostalgia", "gris": "nostalgia", "melancolico": "nostalgia",
        "vivo": "vitalidad", "alegre": "vitalidad", "intenso": "vitalidad",
        "humedo": "humedad", "lluvia": "humedad", "frio": "humedad",
        "tenso": "incomodidad", "estres": "incomodidad", "ruido": "incomodidad",
        "agradecido": "gratitud", "calido": "gratitud", "acogedor": "gratitud"
    }

    # Se convierte la descripción a minúsculas para facilitar la detección de palabras clave.
    descripcion_lower = descripcion.lower()

    # Se identifica la primera emoción asociada a una palabra presente en la descripción.
    emocion_detectada = next((emo for palabra, emo in claves.items() if palabra in descripcion_lower), None)

    # Si no se encuentra ninguna emoción, se solicita una descripción más detallada.
    if not emocion_detectada:
        return (
            "[NECESITA_MAS_INFO]\n"
            "No fue posible identificar emociones en la descripción.\n"
            "Incluya palabras como: tranquilo, húmedo, luminoso, nostálgico, cálido, etc."
        )

    # Se selecciona la paleta de colores correspondiente a la emoción detectada.
    paleta = paletas[emocion_detectada]

    # Función auxiliar que ajusta la luminosidad de un color hexadecimal.
    def ajustar_color(hex_color, factor=1.2):
        rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
        h, l, s = colorsys.rgb_to_hls(*rgb)
        l = max(0, min(1, l * factor))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    try:
        # Se crea una figura y un eje para el mapa, con el color de fondo de la emoción seleccionada.
        fig, ax = plt.subplots(figsize=(10, 10), facecolor=paleta["background"])

        # Se generan colores derivados para acentuar contraste entre elementos urbanos y naturales.
        street_color = ajustar_color(paleta["forest"], 0.6)
        building_color = ajustar_color(paleta["background"], 0.8)
        edge_color = ajustar_color(paleta["forest"], 0.4)
        text_color = ajustar_color(paleta["forest"], 0.3)

        # Se define el estilo visual de cada categoría de elementos cartográficos.
        style = {
            "background": {"fc": paleta["background"]},
            "perimeter": {"ec": edge_color, "lw": 1.2, "fc": paleta["background"]},
            "streets": {"fc": street_color, "ec": edge_color, "lw": 0.9},
            "buildings": {"fc": building_color, "ec": edge_color, "lw": 0.4},
            "green": {"fc": paleta["forest"], "ec": edge_color, "lw": 0.4},
            "forest": {"fc": paleta["forest"], "ec": edge_color, "lw": 0.4},
            "water": {"fc": paleta["water"], "ec": edge_color, "lw": 0.6},
        }

        # Se genera el mapa centrado en las coordenadas del Bosque La Macarena.
        plot(coordenadas, radius=800, ax=ax, style=style)

        # Se define la ruta base hacia la carpeta del agente Gente_Bosque
        base_dir = os.path.join(os.path.dirname(__file__), "Gente_Bosque", "cartografias")

        # Se crea la carpeta para guardar los mapas dentro de Gente_Bosque, si aún no existe.
        os.makedirs(base_dir, exist_ok=True)

        # Se define un nombre de archivo único que incluye la emoción y la fecha.
        filename = f"mapa_emocional_{emocion_detectada}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(base_dir, filename)

        # Se guarda el mapa como imagen PNG y se cierra la figura.
        plt.savefig(filepath, dpi=250, bbox_inches="tight")
        plt.close(fig)


        # Se devuelve información sobre el resultado del proceso.
        return (
            f"Lugar: Bosque La Macarena (Bogotá)\n"
            f"Emoción interpretada: {emocion_detectada}\n"
        )

    except Exception as e:
        # En caso de error, se captura la excepción y se devuelve un mensaje informativo.
        return f"Error al generar la cartografía emocional: {e}"
