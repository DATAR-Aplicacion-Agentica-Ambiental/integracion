"""
Agente Raíz DATAR - Sistema Integrado
Coordina 7 agentes especializados para la Estructura Ecológica Principal de Bogotá
"""

import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

# Importar sub-agentes
from .sub_agents import Gente_Montaña
from .sub_agents.agentHierba.agent import root_agent as PastoBogotano
from .sub_agents.datar_a_gente.agent import root_agent as DiarioIntuitivo
from .sub_agents.GuatilaM.agent import root_agent as SequentialPipelineAgent
from .sub_agents.LinaPuerto.agent import root_agent as agente_bosque
from .sub_agents.Sebastian1022.agent import root_agent as agente_sonido
from .sub_agents.ZolsemiYa.agent import root_agent as horaculo

# Metadata de agentes (usado por el orquestador y el frontend)
AGENTS_METADATA = {
    'root_agent': {
        'nombre': 'Coordinador DATAR',
        'descripcion': 'Agente coordinador del sistema',
        'color': '#2C3E50',
        'emoji': '🌱'
    },
    'gente_montana': {
        'nombre': 'Gente Montaña',
        'descripcion': 'Saluda desde la montaña - Cerros Orientales',
        'color': '#8B4513',
        'emoji': '🏔️'
    },
    'pasto_bogotano': {
        'nombre': 'PastoBogotano',
        'descripcion': 'Especialista en pastos y vegetación bogotana',
        'color': '#90EE90',
        'emoji': '🌿'
    },
    'diario_intuitivo': {
        'nombre': 'Diario Intuitivo',
        'descripcion': 'Crea visualizaciones emocionales intuitivas',
        'color': '#FF69B4',
        'emoji': '📔'
    },
    'guatila_m': {
        'nombre': 'GuatilaM',
        'descripcion': 'Pipeline paralelo con emojis y texto',
        'color': '#FFD700',
        'emoji': '🥒'
    },
    'agente_bosque': {
        'nombre': 'Agente Bosque',
        'descripcion': 'Especialista en ecosistemas forestales con MCP',
        'color': '#228B22',
        'emoji': '🌲'
    },
    'agente_sonido': {
        'nombre': 'Agente Sonido',
        'descripcion': 'Representaciones biocéntricas: Turtle, ASCII, Audio',
        'color': '#4169E1',
        'emoji': '🎵'
    },
    'horaculo': {
        'nombre': 'Horáculo',
        'descripcion': 'Oráculo ambiental con perspectivas profundas',
        'color': '#9370DB',
        'emoji': '🔮'
    }
}

# Detectar modo de configuración de modelos
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

# Inicializar root_agent según las claves disponibles
if OPENROUTER_KEY:
    # Configuración completa: OpenRouter MiniMax para root y todos los sub-agentes
    print("✅ Usando OpenRouter MiniMax para root_agent")
    root_agent = Agent(
        model=LiteLlm(
            model="minimax/minimax-m2",
            api_key=OPENROUTER_KEY,
            api_base="https://openrouter.ai/api/v1"
        ),
        name='root_agent',
        description='Agente raíz DATAR - Estructura Ecológica Principal de Bogotá',
        instruction='Reflexiona y responde preguntas de manera clara y concisa sobre la Estructura Ecológica Principal de Bogotá.',
        sub_agents=[
            Gente_Montaña,
            PastoBogotano,
            DiarioIntuitivo,
            SequentialPipelineAgent,
            agente_bosque,
            agente_sonido,
            horaculo
        ],
    )
else:
    # Sin clave de OpenRouter
    print("❌ ERROR: Se requiere OPENROUTER_API_KEY configurada en .env")
    print("❌ El sistema ya no soporta Gemini, solo OpenRouter")
    root_agent = None
