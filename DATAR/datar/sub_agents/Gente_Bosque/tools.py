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
            "Insectos: Polilla bruja (Ascalapha odorata)",
            "Arácnidos: opiliones ",
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
    Genera un mapa emocional del Bosque La Macarena (Bogotá) utilizando PrettyMaps. 
    A partir de una descripción textual, detecta una emoción o sensación asociada y aplica una 
    paleta de colores contrastante para representar visualmente ese estado emocional.

    Emociones o sensaciones principales:
    
    - serenidad: calma, paz, tranquilidad, silencio reconfortante, conexión armónica con el entorno
    - curiosidad: exploración activa, preguntas, investigar, intriga, deseo de descubrir
    - contemplacion: reflexión profunda, observación sin prisa, introspección, pensamiento pausado
    - melancolia: nostalgia, tristeza reflexiva, melancolía, pérdida, belleza dolorosa, memoria
    - vitalidad: energía, vida abundante, movimiento, biodiversidad visible, entusiasmo
    - frescura: humedad, rocío, bruma, niebla, lluvia, tierra mojada, ambiente húmedo
    - asombro: sorpresa intensa, "wow", descubrimiento impactante, maravilla, lo inesperado
    - alegria: felicidad pura, celebración, gozo, contento, bienestar emocional
    """
    import os
    from datetime import datetime
    import prettymaps
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI para servidor

    # Coordenadas fijas del Bosque de La Macarena (lat, lon)
    coordenadas = (4.614773, -74.063173)

    # Estilos PrettyMaps por emoción
    estilos_emocionales = {
        "serenidad": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#CDE8E5",
                "ec": "#2C6E49",
                "lw": 1.5,
                "zorder": 3
            },
            "building": {
                "palette": ["#A7C7E7", "#CDE8E5", "#2C6E49"],
                "ec": "#2C6E49",
                "lw": 0.5,
                "zorder": 4
            },
            "background": "#CDE8E5"
        },
        "asombro": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#FFF1C1",
                "ec": "#8713D4",
                "lw": 2,
                "zorder": 3
            },
            "building": {
                "palette": ["#73D2DE", "#FFF1C1", "#8713D4"],
                "ec": "#8713D4",
                "lw": 0.8,
                "zorder": 4
            },
            "background": "#FFF1C1"
        },
        "curiosidad": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#FAF3DD",
                "ec": "#0B6E4F",
                "lw": 1.5,
                "zorder": 3
            },
            "building": {
                "palette": ["#3ABEFF", "#FAF3DD", "#0B6E4F"],
                "ec": "#0B6E4F",
                "lw": 0.6,
                "zorder": 4
            },
            "background": "#FAF3DD"
        },
        "contemplacion": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#E0CFCB",
                "ec": "#BB9DD6",
                "lw": 1.2,
                "zorder": 3
            },
            "building": {
                "palette": ["#A7A6BA", "#E0CFCB", "#BB9DD6"],
                "ec": "#BB9DD6",
                "lw": 0.5,
                "zorder": 4
            },
            "background": "#E0CFCB"
        },
        "melancolia": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#C3B1E1",
                "ec": "#3A3D5C",
                "lw": 1.5,
                "zorder": 3
            },
            "building": {
                "palette": ["#6C91BF", "#C3B1E1", "#3A3D5C"],
                "ec": "#3A3D5C",
                "lw": 0.7,
                "zorder": 4
            },
            "background": "#C3B1E1"
        },
        "vitalidad": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#FFE066",
                "ec": "#148D04",
                "lw": 2,
                "zorder": 3
            },
            "building": {
                "palette": ["#0077B6", "#FFE066", "#148D04"],
                "ec": "#148D04",
                "lw": 0.8,
                "zorder": 4
            },
            "background": "#FFE066"
        },
        "frescura": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#C0FDFB",
                "ec": "#00A896",
                "lw": 1.5,
                "zorder": 3
            },
            "building": {
                "palette": ["#028090", "#C0FDFB", "#00A896"],
                "ec": "#00A896",
                "lw": 0.6,
                "zorder": 4
            },
            "background": "#C0FDFB"
        },
        "alegria": {
            "perimeter": {"fill": False, "lw": 0, "zorder": 0},
            "streets": {
                "fc": "#FFF5B7",
                "ec": "#FF7B00",
                "lw": 2,
                "zorder": 3
            },
            "building": {
                "palette": ["#F8DF00", "#FFF5B7", "#FF7B00"],
                "ec": "#FF7B00",
                "lw": 0.8,
                "zorder": 4
            },
            "background": "#FFF5B7"
        }
    }

    # Palabras clave asociadas a emociones
    claves = {
        # Serenidad
        "tranquilidad": "serenidad", "calma": "serenidad", "paz": "serenidad", "silencio": "serenidad",
        # Curiosidad
        "curiosidad": "curiosidad", "exploracion": "curiosidad", "descubrir": "curiosidad", "pregunta": "curiosidad",
        # Contemplacion
        "reflexion": "contemplacion", "observar": "contemplacion", "pensamiento": "contemplacion", "introspeccion": "contemplacion",
        # Melancolia
        "nostalgia": "melancolia", "tristeza": "melancolia", "melancolia": "melancolia", "recuerdo": "melancolia",
        # Vitalidad
        "energia": "vitalidad", "vida": "vitalidad", "entusiasmo": "vitalidad", "movimiento": "vitalidad",
        # Frescura
        "humedad": "frescura", "rocío": "frescura", "niebla": "frescura", "lluvia": "frescura", "bruma": "frescura",
        # Asombro
        "sorpresa": "asombro", "wow": "asombro", "maravilla": "asombro", "impactante": "asombro",
        # Alegría
        "felicidad": "alegria", "gozo": "alegria", "jubilo": "alegria", "contento": "alegria"
    }

    descripcion_lower = descripcion.lower()

    emocion_detectada = next(
        (emo for palabra, emo in claves.items() if palabra in descripcion_lower),
        None
    )

    if not emocion_detectada:
        return (
            "[NECESITA_MAS_INFO]\n"
            "No fue posible identificar emociones en la descripción.\n"
            "Incluya palabras como: calma, curiosidad, nostalgia, energía, lluvia, sorpresa, felicidad, etc."
        )

    estilo = estilos_emocionales[emocion_detectada]

    try:
        # Crear directorio de cartografías si no existe
        base_dir = os.path.join(os.path.dirname(__file__), "cartografias")
        os.makedirs(base_dir, exist_ok=True)

        # Generar mapa con PrettyMaps
        # Radio de ~1000 metros alrededor del Bosque La Macarena
        plot = prettymaps.plot(
            coordenadas,
            radius=1000,
            figsize=(12, 12),
            style=estilo,
            layers={
                "perimeter": {},
                "streets": {
                    "width": {
                        "primary": 5,
                        "secondary": 4,
                        "tertiary": 3.5,
                        "residential": 3,
                        "pedestrian": 2.5,
                        "footway": 2,
                        "path": 2
                    }
                },
                "building": {
                    "tags": {"building": True}
                }
            }
        )

        # Configurar color de fondo
        plot.fig.patch.set_facecolor(estilo["background"])
        
        # Agregar título con la emoción
        plot.ax.set_title(
            f'Bosque La Macarena - {emocion_detectada.capitalize()}',
            font='serif',
            size=24,
            pad=20
        )

        # Guardar como PNG
        filename = f"mapa_emocional_{emocion_detectada}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(base_dir, filename)
        
        plot.fig.savefig(
            filepath,
            dpi=150,
            bbox_inches='tight',
            facecolor=estilo["background"]
        )

        # Cerrar la figura para liberar memoria
        import matplotlib.pyplot as plt
        plt.close(plot.fig)

        return (
            f"Lugar: Bosque La Macarena (Bogotá)\n"
            f"Emoción interpretada: {emocion_detectada}\n"
            f"Archivo generado: {filepath}"
        )

    except Exception as e:
        return f"Error al generar la cartografía emocional: {e}"
