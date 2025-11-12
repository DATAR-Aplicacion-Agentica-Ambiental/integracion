"""
Agente Raíz DATAR - Sistema Integrado (Nueva Estructura)
Coordina 7 agentes especializados para la Estructura Ecológica Principal de Bogotá
"""

import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.Gente_Montaña.agent import root_agent as Gente_Montaña
from .sub_agents.Gente_Pasto.agent import root_agent as Gente_Pasto
from .sub_agents.Gente_Intuitiva.agent import root_agent as Gente_Intuitiva
from .sub_agents.Gente_Interpretativa.agent import root_agent as Gente_Interpretativa
from .sub_agents.Gente_Bosque.agent import root_agent as Gente_Bosque
from .sub_agents.Gente_Sonora.agent import root_agent as Gente_Sonora
from .sub_agents.Gente_Horaculo.agent import root_agent as Gente_Horaculo

# Detectar modo de configuración de modelos
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Lista de sub-agentes
SUB_AGENTS = [
    Gente_Montaña,
    Gente_Pasto,
    Gente_Intuitiva,
    Gente_Interpretativa,
    Gente_Bosque,
    Gente_Sonora,
    Gente_Horaculo
]

# Inicializar root_agent según las claves disponibles
if OPENROUTER_KEY:
    # Configuración: OpenRouter con MiniMax (API verificada)
    print("✅ Usando OpenRouter MiniMax para root_agent")
    root_agent = Agent(
        model=LiteLlm(
            model="minimax/minimax-01",
            api_key=OPENROUTER_KEY,
            api_base="https://openrouter.ai/api/v1"
        ),
        name='root_agent',
        description='Agente raíz DATAR - Estructura Ecológica Principal de Bogotá',
        instruction='Coordina y dirige consultas a los agentes especializados del sistema DATAR para responder sobre la Estructura Ecológica Principal de Bogotá.',
        sub_agents=SUB_AGENTS,
    )
elif GOOGLE_KEY:
    # Solo Google: usar Gemini para todo
    print("⚠️ Solo GOOGLE_API_KEY disponible, usando Gemini 2.5 Flash para root_agent")
    root_agent = Agent(
        model='gemini-2.5-flash',
        name='root_agent',
        description='Agente raíz DATAR - Estructura Ecológica Principal de Bogotá',
        instruction='Coordina y dirige consultas a los agentes especializados del sistema DATAR para responder sobre la Estructura Ecológica Principal de Bogotá.',
        sub_agents=SUB_AGENTS,
    )
else:
    # Sin API keys disponibles
    print("❌ ERROR: No hay API keys configuradas (OPENROUTER_API_KEY o GOOGLE_API_KEY)")
    root_agent = None
