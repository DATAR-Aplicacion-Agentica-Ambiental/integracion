Espacio para la orquestación de agentes (responsable MangleRojo ORG)

## DATAR - Sistema de agentes

Este paquete contiene la **aplicación DATAR** (usando la clase `App` de Google ADK) y sus sub-agentes temáticos (`Gente_*`), cada uno con un rol específico relacionado con territorios, ecologías y experiencias sensibles.

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

- **app**: Aplicación principal DATAR que orquesta todos los sub-agentes `Gente_*` usando la clase `App` de Google ADK.
- **Gente_Montaña**: agente sencillo que siempre saluda desde la montaña.
- **Gente_Pasto**: agente sonoro que compone paisajes sonoros con audios locales.
- **Gente_Intuitiva**: explora y visualiza el "río emocional" a partir de emojis e interpretaciones.
- **Gente_Interpretativa**: coordina múltiples agentes en paralelo y en bucle para reinterpretar interacciones.
- **Gente_Bosque**: guía para despertar curiosidad sobre organismos y cartografías emocionales del bosque.
- **Gente_Sonora**: agente especializado en sonidos de la naturaleza y visualizaciones sonoras.
- **Gente_Horaculo**: oráculo ambiental narrativo basado en memorias y mitologías del territorio.
- **Gente_Compostada**: integra percepciones sobre compostaje, residuos y territorios urbanos como el Parkway.

### Uso básico

#### Ejecutar con ADK CLI

Para ejecutar la aplicación de forma interactiva usando `adk run`:

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1/DATAR
adk run datar
```

Esto iniciará una sesión interactiva con la aplicación `app` y todos sus sub-agentes disponibles.

#### Importar desde Python

Ejemplo de cómo importar la aplicación desde Python:

```python
from DATAR.datar import app

# La aplicación está lista para usar con Runner o API Server
# Ejemplo con Runner:
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()
runner = InMemoryRunner(app=app)
response = await runner.run("Hola, ¿con qué agente puedo explorar hoy?")
```

### Despliegue en Cloud Run

DATAR está optimizado para despliegue en Google Cloud Run usando el API Server nativo de Google ADK.

#### Requisitos previos

1. **Google Cloud Project**: Tener un proyecto de Google Cloud configurado
2. **Autenticación**: Estar autenticado con `gcloud auth login`
3. **Variables de entorno**: Configurar las siguientes variables:
   - `OPENROUTER_API_KEY`: Clave de API para OpenRouter (configurar como Secret en Cloud Run)
   - `GOOGLE_CLOUD_PROJECT`: ID del proyecto de Google Cloud
   - `GOOGLE_CLOUD_LOCATION`: Región de despliegue (ej: `us-central1`)

#### Comando de despliegue

El despliegue se realiza con un solo comando usando `adk deploy cloud_run`:

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  DATAR
```

#### Opciones de despliegue

- `--api`: Despliega el API Server de ADK (habilitado por defecto)
- `--webui`: Despliega la UI de desarrollo de ADK (opcional, útil para testing)
- `--a2a`: Habilita comunicación Agent2Agent (opcional)
- `--allow-unauthenticated`: Permite acceso público (por defecto requiere autenticación)

Ejemplo con UI habilitada:

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --webui \
  DATAR
```

#### API Server automático

Una vez desplegado, el API Server de ADK expone automáticamente los siguientes endpoints REST:

- `GET /list-apps`: Listar aplicaciones disponibles
- `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}`: Crear o actualizar sesiones
- `POST /run_sse`: Ejecutar agentes con soporte para streaming (Server-Sent Events)

#### Testing después del despliegue

**1. UI Testing (si se desplegó con `--webui`)**

Accede a la URL de Cloud Run proporcionada después del despliegue en tu navegador. La UI permite interactuar con los agentes, gestionar sesiones y ver detalles de ejecución.

**2. API Testing con curl**

Primero, configura la URL de tu servicio:

```bash
export APP_URL="https://tu-servicio-abc123xyz.a.run.app"
```

Si el servicio requiere autenticación, obtén un token:

```bash
export TOKEN=$(gcloud auth print-identity-token)
```

Listar aplicaciones disponibles:

```bash
curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
```

Crear o actualizar una sesión:

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/datar_integraciones/users/user_123/sessions/session_abc \
    -H "Content-Type: application/json" \
    -d '{"preferred_language": "es", "visit_count": 1}'
```

Ejecutar el agente:

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "datar_integraciones",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "Hola, ¿con qué agente puedo explorar hoy?"
        }]
    },
    "streaming": false
    }'
```

Para recibir respuestas en streaming, establece `"streaming": true` en la petición anterior.

#### Estructura del proyecto para Cloud Run

El proyecto está estructurado para cumplir con los requisitos de `adk deploy cloud_run`:

- ✅ El código del agente está en `DATAR/datar/agent.py`
- ✅ La variable `app` está definida en `agent.py`
- ✅ `DATAR/datar/__init__.py` contiene `from . import agent`
- ✅ El directorio `DATAR` tiene un nombre claro para el despliegue

### Variables de entorno para Cloud Run

Las siguientes variables de entorno deben configurarse en Cloud Run:

- **`OPENROUTER_API_KEY`**: Clave de API para acceder al modelo `openrouter/minimax/minimax-m2` (requerida)
  - Se recomienda configurarla como Secret en Google Cloud Secret Manager
  - Referencia en Cloud Run: `OPENROUTER_API_KEY:projects/PROJECT_ID/secrets/OPENROUTER_API_KEY:latest`
- **`GOOGLE_CLOUD_PROJECT`**: ID del proyecto de Google Cloud (requerida para servicios de Google Cloud)
- **`GOOGLE_CLOUD_LOCATION`**: Región de despliegue (ej: `us-central1`)

### Buenas prácticas de configuración y seguridad

- No compartas ni subas tu `OPENROUTER_API_KEY` a repositorios públicos.
- Usa siempre un `.env` local para desarrollo y Secrets de Google Cloud para producción.
- Si la clave no está definida, los agentes lanzarán un error de configuración claro (`ConfigError`), para evitar fallos silenciosos.
- En Cloud Run, usa Secret Manager para gestionar claves de API de forma segura.
