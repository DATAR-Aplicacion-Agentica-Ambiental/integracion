import warnings

# Suprimir warnings de serialización de Pydantic relacionados con Google ADK
# Estos warnings son conocidos y no afectan la funcionalidad
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*Pydantic.*serializer.*',
    module='pydantic'
)
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*Expected.*fields.*but got.*',
    module='pydantic'
)
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*serialized value may not be as expected.*',
    module='pydantic'
)

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from .agents_utils import get_openrouter_config
from .sub_agents.Gente_Montaña.agent import root_agent as Gente_Montaña
from .sub_agents.Gente_Pasto.agent import root_agent as Gente_Pasto
from .sub_agents.Gente_Intuitiva.agent import root_agent as Gente_Intuitiva
from .sub_agents.Gente_Interpretativa.agent import root_agent as Gente_Interpretativa
from .sub_agents.Gente_Bosque.agent import root_agent as Gente_Bosque
from .sub_agents.Gente_Sonora.agent import root_agent as Gente_Sonora
from .sub_agents.Gente_Horaculo.agent import root_agent as Gente_Horaculo
from .sub_agents.Gente_Compostada.agent import root_agent as Gente_Compostada

config = get_openrouter_config()

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2",
        api_key=config.api_key,
        api_base=config.api_base,
    ),
    name="root_agent",
    description="Agente raíz DATAR",
    instruction="Ayuda con la prueba de los sub-agentes disponibles en esta versión de DATAR.",
    sub_agents=[
        Gente_Montaña,
        Gente_Pasto,
        Gente_Intuitiva,
        Gente_Interpretativa,
        Gente_Bosque,
        Gente_Sonora,
        Gente_Horaculo,
        Gente_Compostada,
    ],
)
