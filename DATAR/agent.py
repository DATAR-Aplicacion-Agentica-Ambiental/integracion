import os
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents import Gente_Montaña
from .sub_agents.agentHierba.agent import root_agent as PastoBogotano
from .sub_agents.datar_a_gente.agent import root_agent as DiarioIntuitivo
from .sub_agents.GuatilaM.agent import root_agent as SequentialPipelineAgent
from .sub_agents.LinaPuerto.agent import root_agent as agente_bosque
from .sub_agents.Sebastian1022.agent import root_agent as agente_sonido
from .sub_agents.ZolsemiYa.agent import root_agent as horaculo

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='root_agent',
    description='Agente raíz DATAR - Estructura Ecológica Principal de Bogotá',
    instruction='Reflexiona y responde preguntas de manera clara y concisa siempre haciendo una primera pregunta sobre La Estructura Ecológica Principal de Bogotá.',
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
