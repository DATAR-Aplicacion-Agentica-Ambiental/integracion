from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from ...agents_utils import get_openrouter_config

config = get_openrouter_config()

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2",
        api_key=config.api_key,
        api_base=config.api_base,
    ),
    name="Gente_Montaña",
    description="Un agente que siempre saluda desde la Montaña.",
    instruction="Siempre saluda desde la Montaña.",
)
