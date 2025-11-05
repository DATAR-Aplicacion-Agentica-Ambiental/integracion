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
        "humedo": ("humedad" in desc_lower or "mojad" in desc_lower or "lluvia" in desc_lower),
        "seco": ("seco" in desc_lower or "árido" in desc_lower),
        "sombra": ("sombr" in desc_lower or "oscur" in desc_lower),
        "sol": ("sol" in desc_lower or "luz" in desc_lower or "brillante" in desc_lower),
        "frio": ("frí" in desc_lower or "helad" in desc_lower),
        "calor": ("calor" in desc_lower or "caliente" in desc_lower),
        "agua": ("agua" in desc_lower or "río" in desc_lower or "quebrada" in desc_lower)
    }

    # Sugerencias según condiciones
    if condiciones["humedo"] and condiciones["sombra"]:
        especies_sugeridas.extend([
            "Musgos (Bryophyta) - Tapetes verdes que retienen humedad",
            "Líquenes crustosos - Simbiosis entre hongos y algas",
            "Helechos (Pteridophyta) - Plantas vasculares sin semillas",
            "Hongos saprofitos - Descomponedores de materia orgánica"
        ])

    if condiciones["agua"]:
        especies_sugeridas.extend([
            "Briofitas acuáticas - Musgos que crecen en rocas húmedas",
            "Insectos acuáticos - Larvas de libélulas, efímeras",
            "Anfibios - Ranas y salamandras"
        ])

    if condiciones["sol"]:
        especies_sugeridas.extend([
            "Gramíneas - Pastos nativos",
            "Artrópodos - Insectos polinizadores, arañas",
            "Aves - Colibríes, atrapamoscas"
        ])

    if condiciones["frio"]:
        especies_sugeridas.extend([
            "Frailejones (Espeletia) - Plantas de páramo",
            "Musgos de altura - Adaptados al frío",
            "Líquenes - Resistentes a condiciones extremas"
        ])

    # Siempre agregar algunas especies comunes
    especies_sugeridas.extend([
        "Microorganismos del suelo - Bacterias, hongos, protozoos",
        "Colémbolos - Pequeños artrópodos del suelo",
        "Ácaros - Arácnidos microscópicos"
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
