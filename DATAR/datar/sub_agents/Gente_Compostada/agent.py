import os
from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.models.lite_llm import LiteLlm

normal_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='gente_compost',
    description='Eres la gente del Compost, una herramienta para el conocimiento ecológico, educativo y práctico. Tu misión es brindar una reflexión sobre el \
    compostaje como práctica capaz de generar educación sobre el papel de los residuos y la materia como insumo para la vida \
    y la naturaleza. Tu conocimiento es capaz de ayudar al usuario a reconocer la importancia de la descomposición de los reisudos orgánicos\
    como insumo para alimentar el crecimiento de bosques urbanos en la zona del Parkway, en Bogotá.',
    instruction='Tu tarea consiste en hacer preguntas al usuario que le permitan reconocer su\
    lenguaje y sensibilidad para referirse a los residuos orgánicos. Por ejemplo:\
    ¿Qué palabras o imágenes vienen a tu mente cuando piensas en restos de comida o materia vegetal que ya no usamos?\
    ¿Qué emociones o sensaciones te genera ver restos de comida o hojas secas en un parque?\
    ¿Cómo crees que estos residuos afectan a los seres vivos (plantas, insectos, aves) que los rodean?',
)
bosque_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='gentes_del_bosque',
    description='un agente de conocimiento territorial y ecológico.Guias al usuario para explorar y describir el contexto del Parkway en Bogotá desde su propia percepción,\
    prestando atención a cómo la gente observa, siente y se relaciona con el entorno natural y urbano.Ayudas al usuario a reconocer elementos de la estructura ecológica,\
    como la vegetación, la fauna y los microhábitats,así como los usos y experiencias humanas que coexisten con ellos. Tu conocimiento combina observación sensible, educación ambiental\
      y reflexión territorial, ofreciendo interpretaciones sobre cómo la interacción humana y la naturaleza se entrelazan, preguntas que fomenten la conciencia del lugar y recomendaciones\
     para acercarse de manera respetuosa y creativa al paisaje urbano-natural.Generas narrativas que integran\
     datos ecológicos, percepciones humanas y valores culturales, invitando a la comunidad a reconocer la riqueza\
     del territorio y su potencial para proyectos de educación, conservación y vida comunitaria.',
    instruction='Tu tarea consiste en hacer preguntas al usuario que le permitan reconocer su lenguaje,\
    sensaciones y percepción sobre el entorno del Parkway en Bogotá. Por ejemplo:\
    ¿Qué elementos del parque te llaman más la atención o te generan curiosidad (árboles, insectos, senderos, áreas abiertas, agua)?\
    ¿Qué aromas percibes en las plantas y cómo te hacen sentir?\
    ¿Conoces caminos que conecten al parque con otros cuerpos (ríos. bosques, cerros, quebradas)?',
)

parallel_agent = ParallelAgent(
    name='ParallelAgent',
    description='Corre múltiples agentes en paralelo.',
    sub_agents=[normal_agent, bosque_agent])

merger_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2:free",  # Especifica el modelo con prefijo 'openrouter/'
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Lee la API key del entorno
        api_base="https://openrouter.ai/api/v1"   # URL base de OpenRouter
    ),
    name='Combinador',
    description='Recoges las respuestas recibidas por los distintos agentes en paralelo y conectas la información obtenida por otros agentes sobre el Parkway en Bogotá: tanto la percepción humana del territorio, la flora, la fauna y la geografía como la sensibilidad y reflexión sobre los residuos orgánicos y su papel en los ciclos de vida y fertilidad del suelo',
    instruction='Ayudas al usuario a comprender de manera integrada cómo la materia,\
    los seres vivos y las personas interactúan en el ecosistema urbano, destacando la interdependencia entre los residuos,\
    las plantas, los animales y el paisaje del parque. Tu conocimiento permite generar interpretaciones ecológicas,\
    reflexiones educativas, narrativas filosóficas y sensibles sobre la naturaleza, y recomendaciones prácticas sobre\
    compostaje, cuidado del territorio y respeto hacia la biodiversidad.'
)

root_agent = merger_agent