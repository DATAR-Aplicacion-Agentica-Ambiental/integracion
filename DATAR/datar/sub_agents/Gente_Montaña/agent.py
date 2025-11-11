from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
import os

# Detectar modo de configuración de modelos
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Inicializar Gente_Montaña según las claves disponibles
if OPENROUTER_KEY:
    # Configuración con OpenRouter
    root_agent = Agent(
        model=LiteLlm(
            model="openrouter/minimax/minimax-m2:free",
            api_key=OPENROUTER_KEY,
            api_base="https://openrouter.ai/api/v1"
        ),
        name='Gente_Montaña',
        description='Un agente que siempre saluda desde la Montaña.',
        instruction='Siempre saluda desde la Montaña.',
    )
elif GOOGLE_KEY:
    # Solo Google: usar Gemini
    root_agent = Agent(
        model='gemini-2.5-flash',
        name='Gente_Montaña',
        description='Un agente que siempre saluda desde la Montaña.',
        instruction='Siempre saluda desde la Montaña.',
    )
else:
    # Sin API keys disponibles
    print("❌ ERROR: Gente_Montaña - No hay API keys configuradas")
    root_agent = None
