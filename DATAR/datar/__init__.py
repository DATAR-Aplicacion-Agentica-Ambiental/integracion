from .agent import root_agent

# Metadatos de los agentes para la API
AGENTS_METADATA = {
    "gente_montana": {
        "nombre": "Gente Montaña",
        "descripcion": "Un agente que siempre saluda desde la Montaña - Cerros Orientales",
        "color": "#8B4513",
        "emoji": "🏔️"
    },
    "gente_pasto": {
        "nombre": "Gente Pasto",
        "descripcion": "Agente especializado en pastos y vegetación de Bogotá",
        "color": "#90EE90",
        "emoji": "🌿"
    },
    "gente_intuitiva": {
        "nombre": "Gente Intuitiva",
        "descripcion": "Crea visualizaciones intuitivas y diarios emocionales",
        "color": "#FF69B4",
        "emoji": "📔"
    },
    "gente_interpretativa": {
        "nombre": "Gente Interpretativa",
        "descripcion": "Pipeline interpretativo con respuestas paralelas y reinterpretación",
        "color": "#FFD700",
        "emoji": "🥒"
    },
    "gente_bosque": {
        "nombre": "Gente Bosque",
        "descripcion": "Especialista en ecosistemas forestales con herramientas MCP",
        "color": "#228B22",
        "emoji": "🌲"
    },
    "gente_sonora": {
        "nombre": "Gente Sonora",
        "descripcion": "Genera representaciones biocéntricas: Turtle, ASCII/Morse, NumPy audio",
        "color": "#4169E1",
        "emoji": "🎵"
    },
    "gente_horaculo": {
        "nombre": "Gente Horáculo",
        "descripcion": "Oráculo ambiental con perspectivas profundas sobre Bogotá",
        "color": "#9370DB",
        "emoji": "🔮"
    }
}

__all__ = ['root_agent', 'AGENTS_METADATA']
