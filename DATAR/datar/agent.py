import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.Gente_Montaña.agent import root_agent as Gente_Montaña
from .sub_agents.Gente_Pasto.agent import root_agent as Gente_Pasto
from .sub_agents.Gente_Intuitiva.agent import root_agent as Gente_Intuitiva
from .sub_agents.Gente_Normal.agent import root_agent as SequentialPipelineAgent
from .sub_agents.Gente_Bosque.agent import root_agent as Gente_Bosque
from .sub_agents.Gente_Sonora.agent import root_agent as Gente_Sonora
from .sub_agents.Gente_Horaculo.agent import root_agent as Gente_Horaculo

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
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
        SequentialPipelineAgent,
        Gente_Bosque,
        Gente_Sonora,
        Gente_Horaculo
    ],
)
