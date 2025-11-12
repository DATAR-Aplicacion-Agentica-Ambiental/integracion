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
from .sub_agents.Gente_Compostada.agent import root_agent as Gente_Compostada

# Metadata de los agentes para el API
AGENTS_METADATA = {
    "gente_montana": {
        "nombre": "Gente Montaña",
        "descripcion": "Guía de ecosistemas montañosos y cerros orientales de Bogotá",
        "color": "#8B4513",
        "emoji": "⛰️"
    },
    "gente_pasto": {
        "nombre": "Gente Pasto",
        "descripcion": "Especialista en ecosistemas de pastizales y áreas abiertas",
        "color": "#90EE90",
        "emoji": "🌾"
    },
    "gente_intuitiva": {
        "nombre": "Gente Intuitiva",
        "descripcion": "Interpreta patrones emocionales a través de emojis y visualizaciones",
        "color": "#FFB6C1",
        "emoji": "💭"
    },
    "gente_interpretativa": {
        "nombre": "Gente Interpretativa",
        "descripcion": "Asistente de interpretación textual y fusión de perspectivas",
        "color": "#DDA0DD",
        "emoji": "📖"
    },
    "gente_bosque": {
        "nombre": "Gente Bosque",
        "descripcion": "Despierta curiosidad sobre vida forestal, plantas, hongos e insectos",
        "color": "#228B22",
        "emoji": "🌳"
    },
    "gente_sonora": {
        "nombre": "Gente Sonora",
        "descripcion": "Crea sonidos, gráficos y composiciones de paisajes sonoros naturales",
        "color": "#4169E1",
        "emoji": "🎵"
    },
    "gente_horaculo": {
        "nombre": "Gente Horáculo",
        "descripcion": "Ofrece perspectivas temporales y predictivas sobre el ambiente",
        "color": "#9370DB",
        "emoji": "🔮"
    },
    "gente_compostada": {
        "nombre": "Gente Compostada",
        "descripcion": "Especialista en descomposición, suelos y ciclos de nutrientes",
        "color": "#8B4726",
        "emoji": "🍂"
    }
}

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='root_agent',
    description='Agente raíz DATAR',
    instruction='Ayuda con la prueba de los sub-agentes disponibles en esta versión de DATAR.',
    sub_agents=[
        Gente_Montaña,
        Gente_Pasto,
        Gente_Intuitiva,
        Gente_Interpretativa,
        Gente_Bosque,
        Gente_Sonora,
        Gente_Horaculo,
        Gente_Compostada
    ],
)
