Espacio para la orquestación de agentes (responsable MangleRojo ORG)

## DATAR - Sistema de agentes

Este paquete contiene el **agente raíz de DATAR** y sus sub-agentes temáticos (`Gente_*`), cada uno con un rol específico relacionado con territorios, ecologías y experiencias sensibles.

### Requisitos

- Python 3.11 o superior
- Dependencias instaladas:

```bash
pip install -r requirements.txt
```

- Variable de entorno para el modelo:
  - `OPENROUTER_API_KEY`: clave de API para acceder al modelo `openrouter/minimax/minimax-m2`.

### Configuración de entorno

Se recomienda usar un archivo `.env` en la raíz del proyecto (`DATAR/.env`, por ejemplo):

```env
OPENROUTER_API_KEY=tu_clave_de_openrouter_aqui
```

Las utilidades de `DATAR/datar/agents_utils.py` se encargan de:

- Cargar el `.env` automáticamente si existe.
- Validar que `OPENROUTER_API_KEY` esté definida.
- Entregar una configuración consistente a todos los agentes.

### Agentes disponibles

- **root_agent**: orquestador de todos los sub-agentes `Gente_*`.
- **Gente_Montaña**: agente sencillo que siempre saluda desde la montaña.
- **Gente_Pasto**: agente sonoro que compone paisajes sonoros con audios locales.
- **Gente_Intuitiva**: explora y visualiza el “río emocional” a partir de emojis e interpretaciones.
- **Gente_Interpretativa**: coordina múltiples agentes en paralelo y en bucle para reinterpretar interacciones.
- **Gente_Bosque**: guía para despertar curiosidad sobre organismos y cartografías emocionales del bosque.
- **Gente_Sonora**: agente especializado en sonidos de la naturaleza y visualizaciones sonoras.
- **Gente_Horaculo**: oráculo ambiental narrativo basado en memorias y mitologías del territorio.
- **Gente_Compostada**: integra percepciones sobre compostaje, residuos y territorios urbanos como el Parkway.

### Uso básico

#### Ejecutar con ADK CLI

Para ejecutar el agente raíz de forma interactiva usando `adk run`:

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1/DATAR
adk run datar
```

Esto iniciará una sesión interactiva con el `root_agent` y todos sus sub-agentes disponibles.

#### Importar desde Python

Ejemplo de cómo importar el agente raíz desde Python:

```python
from DATAR.datar import root_agent

response = root_agent.generate_response("Hola, ¿con qué agente puedo explorar hoy?")
print(response)
```

La forma exacta de invocar los agentes puede variar según la integración (CLI, API web, etc.), pero todos comparten la misma configuración de modelo a través de `agents_utils.py`.

### Buenas prácticas de configuración y seguridad

- No compartas ni subas tu `OPENROUTER_API_KEY` a repositorios públicos.
- Usa siempre un `.env` local para tus claves.
- Si la clave no está definida, los agentes lanzarán un error de configuración claro (`ConfigError`), para evitar fallos silenciosos.
