# MCP/mcp_server_bosque.py

from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
from datetime import datetime
try:
    import google.generativeai as genai
except Exception:  # ImportError or module not available in this env
    genai = None

# Inicializa el servidor
mcp = FastMCP("servidor_bosque")

if genai is not None:
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    except Exception:
        # fallthrough: keep genai enabled but configuration failed; model calls will handle errors
        pass

PDFS = {
    "filosofia_fungi": "pdfs/Filosofia_fungi.pdf",
    "margullis": "pdfs/Margullis.pdf",
    "hongo_planta": "pdfs/Hongo_planta.pdf",
    "donna": "pdfs/donna.pdf",
    "un bosque en un metro": "pdfs/Un_bosque_en_un_metro.pdf",
}

# Fuentes fijas
FUENTES = {
    "pot": "https://bogota.gov.co/bog/pot-2022-2035/",
    "biomimética": "https://asknature.org/",
    "suelo": "https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2019.02872/full",
    "briofitas": "https://stri.si.edu/es/noticia/briofitas",
}

def log_uso(fuente, tipo):
    """Guarda registro de cada fuente usada."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Usando {tipo}: {fuente}", flush=True)

@mcp.tool()
def leer_pagina(url: str) -> str:
    """Lee y devuelve texto de una página web."""
    log_uso(url, "página web")
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text[:4000]

@mcp.tool()
def explorar_pdf(tema: str) -> str:
    """
    Explora un los archivos que estan en PDFS, busca los temas asociados y genera
    un conjunto de preguntas reflexivas basadas en filosofía de la biología, simbiosis,
    concepto de individuo y asociaciones.Usa el modelo Gemini para formularlas.
    """
    tema = tema.lower().strip()
    if tema not in PDFS:
        return f"No hay un PDF registrado para el tema '{tema}'."

    ruta_pdf = PDFS[tema]
    if not os.path.exists(ruta_pdf):
        return f"No se encontró el archivo: {ruta_pdf}"

    log_uso(ruta_pdf, "PDF")

    # Extraer texto del PDF
    texto = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()

    texto_corto = texto[:6000]  # limitar el texto para el modelo

    # Crear prompt reflexivo
    prompt = f"""
    Eres un asistente reflexivo especializado en filosofía de la biología.
    A partir del siguiente fragmento del texto, genera un breve resumen
    (máximo 5 líneas) y luego 1 a 3 preguntas filosóficas o reflexivas
    relacionadas con temas como:
    - simbiosis
    - concepto de individuo
    - cooperación y asociaciones biológicas
    - límites entre especies
    - vida y relaciones ecológicas
    - el humano como parte del ecosistema

    Texto:
    \"\"\"{texto_corto}\"\"\"
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        salida = response.text.strip()
    except Exception as e:
        salida = f"Error al generar preguntas con Gemini: {e}"

    resultado = (
        f"📄 Fuente PDF: {ruta_pdf}\n\n"
        f"💬 Resultado generado por IA:\n\n{salida}"
    )
    return resultado

@mcp.tool()
def explorar(tema: str) -> str:
    """
    Busca información sobre un tema combinando PDFs y fuentes web.
    """
    tema = tema.lower().strip()
    respuesta = ""

    # Intentar con PDF
    if tema in PDFS:
        respuesta += explorar_pdf(tema) + "\n\n"

    # Buscar fuente web
    for clave, link in FUENTES.items():
        if clave in tema:
            log_uso(link, "fuente web")
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            resumen = text[:1500]
            respuesta += f"🌐 Fuente web: {link}\n\n{resumen}\n\n"

    if not respuesta.strip():
        respuesta = f"No encontré información registrada para el tema '{tema}'."

    return respuesta

@mcp.tool()
def inferir_especies(descripcion: str) -> str:
    """
    Analiza las condiciones descritas por el usuario (temperatura, humedad, luz, suelo, sonido etc.)
    y sugiere grupos de organismos que podrían estar activos o visibles.
    Ejemplo de entrada:
    "Hace frío, pero hay mucha luz y el suelo está seco."
    """

    descripcion = descripcion.lower()

    # Diccionarios de palabras clave
    condiciones = {
        "temperatura": {
            "frío": "baja",
            "helado": "baja",
            "calor": "alta",
            "cálido": "alta",
            "templado": "media"
        },
        "humedad": {
            "húmedo": "alta",
            "mojado": "alta",
            "charcos": "alta",
            "llovido": "alta",
            "rocío":"media",
            "seco": "baja",
            "árido": "baja"
        },
        "luz": {
            "mucha luz": "alta",
            "soleado": "alta",
            "nublado":"medio",
            "oscuro": "baja",
            "sombra": "baja",
            "noche": "baja"
        },
        "sonido": {
            "mucha ruido": "alta",
            "tránsito": "alta",
            "silencio": "baja",
            "pasos": "baja",
        }
    }

    # Interpretar condiciones
    interpretacion = {"temperatura": None, "humedad": None, "luz": None, "sonido": None}

    for cat, palabras in condiciones.items():
        for palabra, nivel in palabras.items():
            if palabra in descripcion:
                interpretacion[cat] = nivel

    # Reglas ecológicas simples
    posibles = []

    if interpretacion["luz"] == "alta":
        posibles.append("Araneidae - arañas de telas orbiculares, pone sus telas en sitios luminosos")
        posibles.append("Micrathena bogota - araña espinosa")
        posibles.append("Chrysomelidae - escarabajos de las hojas")
        posibles.append("Ichneumonidae - avispas parasitoides")
        posibles.append("Syrphidae - moscas de las flores")
        posibles.append("Bombus hortulanus - abejorro")
        posibles.append("Eurema - mariposas amarillas")
        posibles.append("Cladonia -Líquen")
        posibles.append("Lecanora caesiorubella -Líquen")
        posibles.append("Flavopunctelia flaventior -Líquen")
        posibles.append("Teloschistes exilis -Líquen")
        posibles.append("Taraxacum officinale - diente de león")
        posibles.append("Trifolium repens - trébol blanco")
        posibles.append("Trébol morado")


    if interpretacion["humedad"] == "alta":
        posibles.append("Aphididae (áfidos)")
        posibles.append("Ascalapha odorata (polilla bruja)")
        posibles.append("Sphagnum, Fissidens, Campylopus, Plagiochila, Plagiochila,Metzgeria - musgo")
        posibles.append("Usnea - Líquen")  
        posibles.append("Cora - Líquen")
        posibles.append(" Pseudomonas - Bacterias del suelo")
        posibles.append("Pedomicrobium - Bacterias del suelo")
        posibles.append("Coprinellus - Hongo")
        posibles.append("Lactarius - Hongo")
    

    if interpretacion["temperatura"] == "alta":
        posibles.append("Chrysomelidae (escarabajos de las hojas)")
        posibles.append("Bombus hortulanus (abejorro)")
        posibles.append("Eurema (mariposas amarillas)") 
        posibles.append("Taraxacum officinale (diente de león)") 
           

    if interpretacion["luz"] == "media":
        posibles.append("Aphididae (áfidos)")
        posibles.append("Curculionidae (escarabajos picudos)") 
        posibles.append("Compsus canescens (gorgojos)")  
        posibles.append("Eurema (mariposas amarillas)") 
        posibles.append("Campylopus  musgo") 
        posibles.append("Sphagnum musgo") 
        posibles.append("Cora liquen") 
        posibles.append("Ganoderma") 
        posibles.append("Lactarius") 

    if interpretacion["humedad"] == "media":
        posibles.append("Chrysomelidae (escarabajos de las hojas)")
        posibles.append("Curculionidae (escarabajos picudos)")  
        posibles.append("Ichneumonidae (avispas parasitoides)") 
        posibles.append("Syrphidae (moscas de las flores)") 
        posibles.append("Compsus canescens (gorgojos)") 
        posibles.append("Bombus hortulanus (abejorro)") 
        posibles.append("Eurema (mariposas amarillas)") 
        posibles.append("Cladonia Líquen") 
        posibles.append("Lecanora caesiorubella Líquen") 
        posibles.append("Flavopunctelia flaventiorLíquen") 
        posibles.append("Teloschistes exilis Líquen") 
        posibles.append("Glomus (hongos micorrízicos)") 
        posibles.append("Acaulospora (micorrízico)") 
        posibles.append("Ganoderma Hongos") 
        posibles.append("Phellinus Hongos")
        posibles.append("Taraxacum officinale (diente de león)")
        posibles.append("Trifolium repens (trébol blanco)")
        posibles.append("Trébol morado")
    

    if interpretacion["temperatura"] == "media":
        posibles.append("Aphididae (áfidos)")
        posibles.append("Curculionidae (escarabajos picudos)")  
        posibles.append("Ichneumonidae (avispas parasitoides)") 
        posibles.append("Syrphidae (moscas de las flores)") 
        posibles.append("Ascalapha odorata (polilla bruja)") 
        posibles.append("Compsus canescens (gorgojos)") 
        posibles.append("Cora Líquenes") 
        posibles.append("Usnea Líquenes") 
        posibles.append("Cladonia Líquenes") 
        posibles.append("Lecanora caesiorubella Líquenes") 
        posibles.append("Flavopunctelia flaventior Líquenes") 
        posibles.append("Teloschistes exilisLíquenes") 
        posibles.append("Pseudomonas - Bacteria") 
        posibles.append("Acinetobacter Bacteria") 
        posibles.append("Pedomicrobium Bacteria") 
        posibles.append("Glomus (hongos micorrízicos)") 
        posibles.append("Acaulospora (micorrízico)") 
        posibles.append("Coprinellus Hongos") 
        posibles.append("Ganoderma Hongos") 
        posibles.append("Lactarius Hongos")
        posibles.append("Phellinus Hongos")
        posibles.append("Trifolium repens (trébol blanco)")
        posibles.append("Trébol morado")

 
    if interpretacion["luz"] == "baja":
        posibles.append("Sclerosomatidae (opiliones)")
        posibles.append("Ascalapha odorata (polilla bruja)")  
        posibles.append("Fissidens Briófita")  
        posibles.append("Plagiochila Briófita")  
        posibles.append("Metzgeria Briófita")  
        posibles.append("Glomus (hongos micorrízicos)")  
        posibles.append("Acaulospora (micorrízico)")
        posibles.append("Coprinellus Hongos")
        posibles.append("Phellinus Hongos")


    
    if interpretacion["sonido"] == "baja":
        posibles.append("Ascalapha odorata (polilla bruja) - Sensible a sonidos fuertes ")
        
    if interpretacion["temperatura"] == "baja":
        posibles.append(" Campylopus Briofitas")
        posibles.append("Fissidens Briofitas")  
        posibles.append("Sphagnum Briofitas")
        posibles.append("Plagiochila Briofitas")
        posibles.append("Metzgeria Briofitas")


    # Redacción 
    if posibles:
        salida = (
            "Basado en tu descripción, es posible que observes:\n\n- "
            + "\n- ".join(posibles)
            + "\n\nCada uno responde de manera distinta a las condiciones ambientales descritas."
        )
    else:
        salida = "No pude inferir condiciones claras a partir de tu descripción."

    return salida

# CRÍTICO: Cambiar el if __name__ == "__main__" por esto
if __name__ == "__main__":
    import sys
    import asyncio
    
    # Usar el método correcto para ejecutar el servidor
    asyncio.run(mcp.run())