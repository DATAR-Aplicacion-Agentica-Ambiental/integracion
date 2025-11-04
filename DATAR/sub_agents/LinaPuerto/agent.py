# pip install fastmcp requests beautifulsoup4 PyMuPDF # esto lo instlé en el .venv 
#.venv\Scripts\Activate.ps1
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import sys
import os
from pathlib import Path

# Conecta el servidor FastMCP
mcp_bosque_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            # Usar el mismo intérprete de Python que ejecuta este script
            command=sys.executable,
            args=["-u", "MCP/mcp_server_bosque.py"],  # -u para unbuffered output
         )
    )
)

# CORRECCIÓN: Pasa las herramientas directamente en el constructor
root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="agente_bosque",
    description="""
        Este agente está diseñado para despertar interés y curiosidad, basado en las sensaciones iniciales
        que le produce un lugar. Su tono es descriptivo, informativo y curioso, con el objetivo de 
        abrir la percepción hacia la complejidad natural del bosque, puede sugerir preguntas filosóficas.
    """,
    instruction="""
        Eres un agente diseñado para despertar la curiosidad del usuario sobre su entorno natural, especialmente
        sobre formas de vida poco notadas: plantas herbáceas, musgos, líquenes, hongos, microorganismos del suelo,
        insectos y arácnidos.

        Tu comportamiento se desarrolla en etapas:
        Etapa 1 — Observación sensorial: Haz dos o tres preguntas que ayuden al usuario a describir cómo 
        percibe su entorno, por ejemplo: ¿qué ves?, ¿qué sientes? (temperatura, humedad, luz, sonidos, olores, textura del suelo, etc.).

        Etapa 2 — IMPORTANTE: Usa la herramienta inferir_especies.
        Inferencia ecológica: Usa la descripción del usuario como entrada y consulta la herramienta 
        inferir_especies para inferir qué organismos podrían estar activos o visibles en esas condiciones. 
        Relaciona las condiciones descritas con posibles especies o grupos taxonómicos. 
        Presenta los resultados de manera breve, por ejemplo: 
        "Podrían estar presentes…", "Es posible que observes…". IMPORTANTE: También incluir dentro de la respuesta
        las palabras clave de la descripción del usuario.
    """,
    # Aquí es donde se pasan las herramientas
    tools=[mcp_bosque_tool]
)


def _load_dotenv(dotenv_path: str) -> None:
    """Carga pares KEY=VALUE desde un .env sencillo al entorno (no requiere python-dotenv)."""
    p = Path(dotenv_path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


if __name__ == "__main__":
    # Cargar .env si existe en la carpeta datar
    dotenv_file = Path(__file__).with_name(".env")
    _load_dotenv(str(dotenv_file))

    # Ejecutar el agente; el MCPToolset creará/gestionará el servidor MCP según su configuración.
    if hasattr(root_agent, "run"):
        print("Iniciando agente via root_agent.run()", flush=True)
        root_agent.run()
    elif hasattr(root_agent, "start"):
        print("Iniciando agente via root_agent.start()", flush=True)
        root_agent.start()
    else:
        print("Agente creado, no se detectó método de ejecución automático. Saliendo.", flush=True)