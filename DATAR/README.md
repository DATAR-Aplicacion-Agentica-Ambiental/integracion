Espacio para la orquestación de agentes (responsable MangleRojo ORG)

## DATAR - Sistema de agentes

Este paquete contiene la **aplicación DATAR** (usando la clase `App` de Google ADK) y sus sub-agentes temáticos (`Gente_*`), cada uno con un rol específico relacionado con territorios, ecologías y experiencias sensibles.

### Requisitos

- Python 3.11 o superior
- Dependencias instaladas:

```bash
# Desde el directorio DATAR/
pip install -r datar/requirements.txt
```

**Nota**: El archivo `requirements.txt` está ubicado en `DATAR/datar/requirements.txt` para que `adk deploy cloud_run` lo detecte correctamente cuando se usa `AGENT_PATH="datar"`.

- Variable de entorno para el modelo:
  - `OPENROUTER_API_KEY`: clave de API para acceder al modelo `openrouter/minimax/minimax-m2`.

### Configuración de entorno

Se recomienda usar un archivo `.env` en la raíz del proyecto (`DATAR/.env`):

```env
# Clave de API para OpenRouter (requerida)
OPENROUTER_API_KEY=tu_clave_de_openrouter_aqui

# Variables de Google Cloud (requeridas para despliegue en Cloud Run)
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
GOOGLE_CLOUD_LOCATION=southamerica-east1
```

Las utilidades de `DATAR/datar/agents_utils.py` se encargan de:

- Cargar el `.env` automáticamente si existe (siempre desde `DATAR/.env`).
- Validar que `OPENROUTER_API_KEY` esté definida.
- Entregar una configuración consistente a todos los agentes.

**Nota**: Las variables `GOOGLE_CLOUD_PROJECT` y `GOOGLE_CLOUD_LOCATION` son necesarias para el despliegue en Cloud Run, pero no son requeridas para ejecución local con `adk run`.

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
3. **Variables de entorno locales**: Configurar en tu `.env`:
   - `OPENROUTER_API_KEY`: Clave de API para OpenRouter
   - `GOOGLE_CLOUD_PROJECT`: ID del proyecto de Google Cloud
   - `GOOGLE_CLOUD_LOCATION`: Región de despliegue (ej: `southamerica-east1`)

#### Configurar Secretos en Google Cloud Secret Manager (Recomendado)

**⚠️ IMPORTANTE**: Crea los secretos ANTES del despliegue inicial. Si ya desplegaste el servicio, puedes crear los secretos y luego actualizar el servicio (ver sección "Configurar Secretos después del despliegue").

Para producción, es recomendable usar Secret Manager en lugar de pasar variables de entorno directamente. Sigue estos pasos:

**1. Crear el secreto para OPENROUTER_API_KEY:**

```bash
# Asegúrate de estar en el directorio DATAR/ o ajusta la ruta del .env
cd DATAR

# Opción A: Desde el archivo .env (recomendado)
gcloud secrets create OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --data-file=<(echo -n "$(grep OPENROUTER_API_KEY .env | cut -d '=' -f2)")

# Opción B: Desde una variable de entorno
export OPENROUTER_API_KEY=$(grep OPENROUTER_API_KEY .env | cut -d '=' -f2)
echo -n "$OPENROUTER_API_KEY" | gcloud secrets create OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --data-file=-

# Opción C: Ingresar manualmente (te pedirá el valor)
gcloud secrets create OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --replication-policy="automatic"
```

**2. Dar permisos al servicio de Cloud Run para acceder al secreto:**

Primero, obtén el número de proyecto:

```bash
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format="value(projectNumber)")
```

Luego, otorga permisos:

```bash
gcloud secrets add-iam-policy-binding OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Nota**: Si el secreto ya existe, puedes actualizarlo con:

```bash
echo -n "nueva-clave-aqui" | gcloud secrets versions add OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --data-file=-
```

#### Comando de despliegue

**Importante**: 
- El comando `adk deploy cloud_run` detecta automáticamente el objeto `app` o `root_agent` en tu código.
- **Secretos**: 
  - Si creaste secretos en Secret Manager ANTES del despliegue, puedes configurarlos durante el despliegue o después.
  - Si creaste secretos DESPUÉS del despliegue, deberás actualizar el servicio (ver sección "Configurar Secretos después del despliegue" más abajo).
  - Si no usas Secret Manager, configura `OPENROUTER_API_KEY` como variable de entorno después del despliegue.

El despliegue se realiza con un solo comando usando `adk deploy cloud_run`:

**Importante**: Ejecuta el comando desde el directorio `DATAR/`:

```bash
export APP_NAME="datar_integraciones"
export AGENT_PATH="datar"  # El subdirectorio que contiene agent.py

adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=datar-integraciones \
  --app_name=$APP_NAME \
  --with_ui \
  $AGENT_PATH
```

**Nota sobre AGENT_PATH**: 
- Si ejecutas desde `DATAR/`, usa `AGENT_PATH="datar"` (el subdirectorio)
- El `--app_name` debe coincidir con el `name` del objeto `App` en tu código (`datar_integraciones`)
- El `requirements.txt` debe estar en `DATAR/datar/requirements.txt` para que se instalen las dependencias correctamente

#### Opciones de despliegue

- `--service_name` o `-s`: Nombre del servicio en Cloud Run (por defecto: `adk-default-service-name`)
- `--app_name`: Nombre de la aplicación (opcional, por defecto usa el nombre del directorio del agente)
- `--api`: Despliega el API Server de ADK (habilitado por defecto)
- `--webui` o `--with_ui`: Despliega la UI de desarrollo de ADK (opcional, útil para testing)
- `--a2a`: Habilita comunicación Agent2Agent (opcional, habilitado por defecto)
- `--allow-unauthenticated`: Permite acceso público (por defecto requiere autenticación)

**Nota sobre el nombre del servicio**: El nombre debe cumplir con las reglas de Cloud Run:
- Solo letras minúsculas, números y guiones
- Máximo 63 caracteres
- Debe comenzar con letra

Ejemplo completo con todas las opciones (desde el directorio `DATAR/`):

```bash
export APP_NAME="datar_integraciones"
export AGENT_PATH="datar"

adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=datar-integraciones \
  --app_name=$APP_NAME \
  --with_ui \
  $AGENT_PATH
```

#### Configurar Secretos después del despliegue

Si creaste secretos en Secret Manager DESPUÉS del despliegue inicial, debes configurar las referencias en el servicio de Cloud Run:

```bash
# Actualizar el servicio para usar el secreto
gcloud run services update datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest
```

**Nota**: Si el servicio ya tiene una variable de entorno `OPENROUTER_API_KEY` configurada directamente, el comando anterior la reemplazará con la referencia al secreto.

**Alternativa: Usar variables de entorno directamente** (menos seguro para producción):

Si prefieres no usar Secret Manager (solo para desarrollo/testing):

```bash
# Obtener la clave desde .env
cd DATAR
export OPENROUTER_API_KEY=$(grep OPENROUTER_API_KEY .env | cut -d '=' -f2)

# Configurar como variable de entorno en Cloud Run
gcloud run services update datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --set-env-vars="OPENROUTER_API_KEY=$OPENROUTER_API_KEY"
```

**Recomendación**: 
- ✅ **Producción**: Usa Secret Manager (más seguro, permite rotación de claves)
- ⚠️ **Desarrollo/Testing**: Variables de entorno directas son aceptables, pero menos seguras

#### API Server automático

Una vez desplegado, el API Server de ADK expone automáticamente los siguientes endpoints REST:

##### Endpoints principales

- **`GET /list-apps`**: Listar todas las aplicaciones disponibles

- **`POST /run`**: Ejecutar un agente y devolver eventos (sin streaming)
  - Cuerpo: `{"app_name": "DATAR", "user_id": "...", "session_id": "...", "new_message": {...}, "streaming": false}`
  - Respuesta: Array JSON de eventos

- **`POST /run_sse`**: Ejecutar un agente con Server-Sent Events (streaming)
  - Cuerpo: Igual que `/run` pero con `"streaming": true`
  - Respuesta: Flujo SSE de eventos en tiempo real

##### Gestión de sesiones

- **`GET /apps/{app_name}/users/{user_id}/sessions`**: Listar todas las sesiones de un usuario
- **`POST /apps/{app_name}/users/{user_id}/sessions`**: Crear una nueva sesión
- **`GET /apps/{app_name}/users/{user_id}/sessions/{session_id}`**: Obtener detalles de una sesión específica
- **`POST /apps/{app_name}/users/{user_id}/sessions/{session_id}`**: Crear o actualizar una sesión específica
- **`DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}`**: Eliminar una sesión

##### Gestión de artefactos

- **`GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts`**: Listar todos los artefactos de una sesión
- **`GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}`**: Obtener un artefacto específico
- **`DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}`**: Eliminar un artefacto
- **`GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions`**: Listar versiones de un artefacto
- **`GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/{version_id}`**: Obtener una versión específica de un artefacto

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
    $APP_URL/apps/DATAR/users/test_user/sessions/test_session \
    -H "Content-Type: application/json" \
    -d '{"preferred_language": "es", "visit_count": 1}'
```

Ejecutar el agente (sin streaming):

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "DATAR",
    "user_id": "test_user",
    "session_id": "test_session",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "Hola, ¿con qué agente puedo explorar hoy?"
        }]
    },
    "streaming": false
    }'
```

Ejecutar el agente con streaming (SSE):

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "DATAR",
    "user_id": "test_user",
    "session_id": "test_session",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "Hola, ¿con qué agente puedo explorar hoy?"
        }]
    },
    "streaming": true
    }'
```

Listar sesiones de un usuario:

```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/DATAR/users/test_user/sessions
```

Obtener detalles de una sesión:

```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/DATAR/users/test_user/sessions/test_session
```

Listar artefactos de una sesión:

```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/DATAR/users/test_user/sessions/test_session/artifacts
```

**Nota**: Reemplaza `DATAR` con el nombre de aplicación que obtuviste de `/list-apps` si es diferente.

#### Estructura del proyecto para Cloud Run

El proyecto está estructurado para cumplir con los requisitos de `adk deploy cloud_run`:

- ✅ El código del agente está en `DATAR/datar/agent.py`
- ✅ La variable `app` está definida en `agent.py`
- ✅ `DATAR/datar/__init__.py` contiene `from . import agent`
- ✅ El archivo `requirements.txt` está en `DATAR/datar/requirements.txt` (requerido para que `adk deploy cloud_run` instale las dependencias)
- ✅ El comando se ejecuta desde `DATAR/` con `AGENT_PATH="datar"`

### Variables de entorno para Cloud Run

Las siguientes variables de entorno deben configurarse en Cloud Run:

- **`OPENROUTER_API_KEY`**: Clave de API para acceder al modelo `openrouter/minimax/minimax-m2` (requerida)
  - **Recomendado**: Configurarla como Secret en Google Cloud Secret Manager (ver sección "Configurar Secretos" arriba)
  - **Alternativa**: Configurarla como variable de entorno directamente (menos seguro)
  - Referencia a Secret: `OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest` (cuando se usa Secret Manager)
- **`GOOGLE_CLOUD_PROJECT`**: ID del proyecto de Google Cloud (se configura automáticamente en el despliegue)
- **`GOOGLE_CLOUD_LOCATION`**: Región de despliegue (se configura automáticamente en el despliegue)

### Buenas prácticas de configuración y seguridad

- No compartas ni subas tu `OPENROUTER_API_KEY` a repositorios públicos.
- Usa siempre un `.env` local para desarrollo y Secrets de Google Cloud para producción.
- Si la clave no está definida, los agentes lanzarán un error de configuración claro (`ConfigError`), para evitar fallos silenciosos.
- En Cloud Run, usa Secret Manager para gestionar claves de API de forma segura.
