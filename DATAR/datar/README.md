## DATAR – Despliegue privado en Cloud Run con bucket de medios y `adk deploy cloud_run`

Este README describe el flujo de **despliegue en Cloud Run (privado)** usando `adk deploy cloud_run` desde código fuente, y cómo se integran:
- El **bucket de medios** en Cloud Storage (para `.wav` y `.png` generados por los agentes `Gente_*`).
- Los **secretos** (especialmente `OPENROUTER_API_KEY`).
- La **autenticación** con tokens de identidad para acceder al servicio privado.

La estructura ya cumple con la guía oficial de ADK para Cloud Run en Python:  
`https://google.github.io/adk-docs/deploy/cloud-run/`

---

### 1. Variables de entorno locales

Desde el directorio `DATAR/`:

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1/DATAR

export GOOGLE_CLOUD_PROJECT="TU_PROYECTO"
export GOOGLE_CLOUD_LOCATION="southamerica-east1"

# Nombre de bucket único (ajusta el sufijo para tu entorno)
export MEDIA_BUCKET_NAME="datar-integraciones-media-dev"
```

En `DATAR/.env` define al menos:

```env
OPENROUTER_API_KEY=tu_clave_de_openrouter
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
GOOGLE_CLOUD_LOCATION=southamerica-east1
```

Los agentes suben archivos a rutas como:
- `gente_sonora/audio/...`
- `gente_pasto/audio/...`
- `gente_bosque/cartografias/...`
- `gente_intuitiva/imagenes/...`

---

### 2. Crear y configurar el bucket de medios en Cloud Storage

```bash
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Crear bucket regional
gcloud storage buckets create gs://$MEDIA_BUCKET_NAME \
  --project=$GOOGLE_CLOUD_PROJECT \
  --location=$GOOGLE_CLOUD_LOCATION \
  --uniform-bucket-level-access

# Permitir lectura pública de objetos (para Discord / web‑app)
gcloud storage buckets add-iam-policy-binding gs://$MEDIA_BUCKET_NAME \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

Así las URLs del tipo  
`https://storage.googleapis.com/$MEDIA_BUCKET_NAME/...`  
son legibles por navegador, Discord, etc.

Más adelante puedes quitar el acceso público y usar **URLs firmadas** desde tu backend, sin cambiar el contrato de los agentes (siguen devolviendo una URL HTTP).

---

### 3. Secretos en Secret Manager

Solo guardamos como secreto lo sensible: **`OPENROUTER_API_KEY`**.

**Primero, carga la variable desde tu `.env`:**

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1/DATAR

# Cargar OPENROUTER_API_KEY desde .env
export OPENROUTER_API_KEY=$(grep OPENROUTER_API_KEY .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")

# Verificar que se cargó (no debe estar vacío)
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "ERROR: OPENROUTER_API_KEY no está definida en .env"
  exit 1
fi

echo "✓ OPENROUTER_API_KEY cargada (longitud: ${#OPENROUTER_API_KEY} caracteres)"
```

**Luego, crear o actualizar el secreto:**

```bash
# Crear el secreto (si no existe) o agregar una nueva versión (si ya existe)
echo -n "$OPENROUTER_API_KEY" | gcloud secrets create OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --data-file=- 2>/dev/null || \
echo -n "$OPENROUTER_API_KEY" | gcloud secrets versions add OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --data-file=-
```

Dar permisos a la service account por defecto de Cloud Run:

```bash
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT \
  --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding OPENROUTER_API_KEY \
  --project=$GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

El resto de valores (`MEDIA_BUCKET_NAME`, etc.) se mantienen como **variables de entorno normales**.

---

### 4. Despliegue privado con `adk deploy cloud_run` desde código fuente

Requisitos de estructura (ya cumplidos):
- `datar/agent.py` define el objeto `app`.
- `datar/__init__.py` importa `agent`.
- `datar/requirements.txt` contiene las dependencias (incluye `google-adk`, `google-cloud-storage`, etc.).

Desde `DATAR/`:

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1/DATAR

export APP_NAME="datar_integraciones"
export AGENT_PATH="datar"  # subdirectorio donde está agent.py

adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=datar-integraciones \
  --app_name=$APP_NAME \
  --with_ui \
  $AGENT_PATH
```

**⚠️ IMPORTANTE**: Durante el despliegue, `adk` puede preguntar:

```
Allow unauthenticated invocations to [datar-integraciones] (y/N)?
```

**Responde `N` (No)** para mantener el servicio **privado** y requerir autenticación con tokens de identidad.

Este comando:
- Construye una imagen a partir del código fuente + `requirements.txt`.
- Despliega un servicio de Cloud Run **privado** (requiere autenticación).
- Expone la **UI de ADK** (`--with_ui`) para pruebas internas (también requiere autenticación).

Al final verás una URL como:

```text
https://datar-integraciones-xxxxx-uc.a.run.app
```

Guárdala como `APP_URL`.

---

### 5. Configuración de entorno en el servicio de Cloud Run

**Primero, configura la región por defecto para evitar preguntas interactivas:**

```bash
gcloud config set run/region $GOOGLE_CLOUD_LOCATION
```

1. **Permisos de Storage para la service account de Cloud Run**:

```bash
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT \
  --format="value(projectNumber)")
CLOUDRUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud storage buckets add-iam-policy-binding gs://$MEDIA_BUCKET_NAME \
  --member="serviceAccount:${CLOUDRUN_SA}" \
  --role=roles/storage.objectAdmin
```

2. **Conectar el secreto `OPENROUTER_API_KEY` al servicio**:

```bash
gcloud run services update datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest
```

3. **Configurar variables de entorno en el servicio**:

```bash
gcloud run services update datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --set-env-vars="MEDIA_BUCKET_NAME=$MEDIA_BUCKET_NAME,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION"
```

**Nota**: Si el servicio ya tiene estas variables configuradas, puedes combinarlas con el secreto en un solo comando:

```bash
gcloud run services update datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest \
  --set-env-vars="MEDIA_BUCKET_NAME=$MEDIA_BUCKET_NAME,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION"
```

Opcional:

```bash
--set-env-vars="MEDIA_PUBLIC_BASE_URL=https://storage.googleapis.com/$MEDIA_BUCKET_NAME"
```

si quieres fijar explícitamente la base URL pública usada por los helpers.

---

### 6. Probar el servicio privado con `curl` + token de identidad

El servicio es privado: solo responde a peticiones con un **token de identidad** válido.

**Dar permisos a tu cuenta de gcloud para invocar el servicio (si es necesario):**

```bash
# Obtener tu email de gcloud
export YOUR_EMAIL=$(gcloud config get-value account)

# Dar permiso de invocador a tu cuenta
gcloud run services add-iam-policy-binding datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --member="user:${YOUR_EMAIL}" \
  --role="roles/run.invoker"
```

**Obtener la URL correcta del servicio:**

```bash
# Obtener la URL del servicio desplegado
export APP_URL=$(gcloud run services describe datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --format="value(status.url)")

echo "URL del servicio: $APP_URL"
```

**Obtener token de identidad:**

```bash
# Para testing manual desde tu cuenta de gcloud
export TOKEN=$(gcloud auth print-identity-token)

# Nota: Este token funciona porque tu cuenta de gcloud tiene permisos.
# Para un backend con service account, usa las librerías de Google Cloud
# para obtener el token con la audiencia correcta ($APP_URL).
```

**Probar el endpoint raíz primero (para verificar que el servicio responde):**

```bash
curl -v -X GET \
  -H "Authorization: Bearer $TOKEN" \
  "$APP_URL/"
```

**Interpretación de respuestas:**

- **307 Redirect con `location: /dev-ui/`**: ✅ **El servicio está funcionando correctamente**. Esto significa que:
  - El servicio responde y acepta tu token de autenticación.
  - La UI de desarrollo de ADK está habilitada (porque se desplegó con `--with_ui`).
  - Los endpoints de API están disponibles en `/run`, `/list-apps`, etc.
- **200 OK con HTML**: El servicio está funcionando y muestra la UI de ADK.
- **200 OK con JSON**: El servicio responde correctamente con datos JSON.
- **401 Unauthorized**: El token no es válido o no tienes permisos. Verifica:
  - Que ejecutaste `gcloud run services add-iam-policy-binding` para tu cuenta.
  - Que el token se generó correctamente: `echo $TOKEN | head -c 50`.
- **404 Not Found**: El endpoint no existe. Puede ser normal si ADK no expone un endpoint raíz; prueba `/list-apps` directamente.
- **403 Forbidden**: Tu cuenta no tiene permisos para invocar el servicio privado.

**Si obtienes 307 Redirect a `/dev-ui/`**, el servicio está funcionando correctamente y puedes proceder a probar los endpoints de API.

**Listar apps disponibles:**

Ahora que confirmaste que el servicio responde (307 a `/dev-ui/`), prueba los endpoints de API:

```bash
curl -v -X GET \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$APP_URL/list-apps" | jq .
```

**Nota**: El flag `-v` muestra headers HTTP útiles para debugging. `jq .` formatea la salida JSON (instala con `brew install jq` si no lo tienes).

**Respuesta esperada**: Deberías ver un JSON con la lista de aplicaciones disponibles, por ejemplo:

```json
["datar_integraciones"]
```

**Si `/list-apps` da 404**, prueba estos endpoints alternativos que ADK puede exponer:

```bash
# Probar diferentes rutas posibles
curl -H "Authorization: Bearer $TOKEN" "$APP_URL/api/list-apps"
curl -H "Authorization: Bearer $TOKEN" "$APP_URL/v1/list-apps"
curl -H "Authorization: Bearer $TOKEN" "$APP_URL/apps"
```

**Acceder a la UI desde el navegador (servicio privado):**

Como el servicio es **privado**, no puedes acceder directamente desde el navegador sin autenticación. Tienes dos opciones:

**Opción 1: Usar el proxy de gcloud (recomendado para desarrollo y testing):**

```bash
# Esto crea un túnel autenticado en localhost:8080
gcloud run services proxy datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --port=8080
```

Luego abre en tu navegador: `http://localhost:8080/dev-ui/`

**Si interrumpiste el proxy o no carga:**

1. **Verificar si el proceso sigue corriendo:**
   ```bash
   # Ver procesos de gcloud proxy en el puerto 8080
   lsof -i :8080
   # O buscar procesos de gcloud
   ps aux | grep "gcloud run services proxy"
   ```

2. **Matar el proceso si está corriendo:**
   ```bash
   # Opción A: Matar por puerto
   kill -9 $(lsof -t -i:8080)
   
   # Opción B: Matar por nombre de proceso
   pkill -f "gcloud run services proxy"
   ```

3. **Usar un puerto diferente si 8080 está ocupado:**
   ```bash
   gcloud run services proxy datar-integraciones \
     --project=$GOOGLE_CLOUD_PROJECT \
     --region=$GOOGLE_CLOUD_LOCATION \
     --port=8081  # Cambiar a otro puerto
   ```
   Luego abre: `http://localhost:8081/dev-ui/`

4. **Reiniciar el proxy limpiamente:**
   ```bash
   # Asegúrate de que no hay procesos anteriores
   pkill -f "gcloud run services proxy"
   
   # Espera un segundo
   sleep 1
   
   # Inicia el proxy de nuevo
   gcloud run services proxy datar-integraciones \
     --project=$GOOGLE_CLOUD_PROJECT \
     --region=$GOOGLE_CLOUD_LOCATION \
     --port=8080
   ```

**✅ Perfecto para probar el despliegue real en la nube:**
- Estás probando el **servicio real** desplegado en Cloud Run (no una versión local).
- Puedes verificar que los agentes funcionan correctamente en producción.
- Puedes probar que los archivos `.wav` y `.png` se suben correctamente a Cloud Storage.
- Puedes verificar que las URLs de Cloud Storage se generan y devuelven correctamente.
- El servicio sigue siendo **privado** (no lo expones públicamente).
- Ideal para testing antes de conectar tu backend o bot de Discord.

**¿Cómo funciona el proxy?**

El proxy de `gcloud` se ejecuta **localmente** en tu máquina y actúa como intermediario:

1. **Se ejecuta localmente**: El comando `gcloud run services proxy` inicia un servidor HTTP en tu máquina (por defecto en `localhost:8080`).

2. **Maneja la autenticación automáticamente**: 
   - Usa las credenciales de tu cuenta de `gcloud` (las mismas que usas con `gcloud auth login`).
   - Obtiene tokens de identidad automáticamente cuando es necesario.
   - Los tokens se renuevan automáticamente cuando expiran.

3. **Reenvía peticiones a Cloud Run**:
   - Cuando tu navegador hace una petición a `http://localhost:8080/dev-ui/`, el proxy:
     - Obtiene un token de identidad válido usando tus credenciales de gcloud.
     - Reenvía la petición a `https://datar-integraciones-xxx.a.run.app/dev-ui/` con el header `Authorization: Bearer <TOKEN>`.
     - Devuelve la respuesta de Cloud Run a tu navegador.

4. **Ventajas**:
   - No necesitas manejar tokens manualmente.
   - Tu navegador ve `localhost` (sin problemas de CORS ni autenticación compleja).
   - El servicio Cloud Run sigue siendo privado (solo accesible vía proxy o con tokens).
   - Funciona con cualquier herramienta HTTP (navegador, curl, Postman, etc.).

**Flujo completo**:
```
Tu máquina local                    Internet / Google Cloud
─────────────────                  ────────────────────────
                                    
Navegador                          
    │                                
    ↓                                
localhost:8080                      
(proxy local)                       
    │                                
    │ [añade token automáticamente]  
    ↓                                
    ────────────────────────────────→  https://datar-integraciones-xxx.a.run.app
                                        (Cloud Run en la nube)
                                        │
                                        │ [procesa petición]
                                        │
    ←────────────────────────────────  [devuelve respuesta]
    │
    ↓
Navegador recibe respuesta
```

**Puntos clave**:
- ✅ El proxy **SÍ se comunica con Cloud Run en la nube** (no es solo local).
- ✅ El proxy corre **localmente** en tu máquina (`localhost:8080`).
- ✅ El servicio Cloud Run sigue corriendo **en Google Cloud** (no se mueve a local).
- ✅ El proxy actúa como **puente autenticado** entre tu navegador local y el servicio en la nube.

**Nota**: El proxy debe seguir ejecutándose mientras lo uses. Presiona `Ctrl+C` para detenerlo.

**Opción 2: Hacer el servicio público temporalmente (solo para testing):**

```bash
# Permitir acceso público temporalmente
gcloud run services add-iam-policy-binding datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --member="allUsers" \
  --role="roles/run.invoker"
```

Luego puedes abrir `$APP_URL/dev-ui/` directamente en el navegador.

**⚠️ IMPORTANTE**: Recuerda volver a hacer el servicio privado después de testing:

```bash
# Remover acceso público
gcloud run services remove-iam-policy-binding datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --member="allUsers" \
  --role="roles/run.invoker"
```

**Para producción**, usa siempre la Opción 1 (proxy) o accede solo vía API desde tu backend autenticado.

**Nota**: Si obtienes un 404, verifica:
1. Que la URL del servicio sea correcta (debe terminar en `.a.run.app`).
2. Que tu cuenta de gcloud tenga permisos para invocar el servicio (rol `roles/run.invoker`).
3. Que el servicio esté completamente desplegado (puede tardar unos minutos después del deploy).
4. Que el endpoint `/list-apps` exista (puede que ADK exponga los endpoints en otra ruta base).

**Para verificar los logs del servicio:**

```bash
gcloud run services logs read datar-integraciones \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --limit=50
```

**Ejecutar el agente (ejemplo simple):**

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$APP_URL/run" \
  -d '{
    "app_name": "datar_integraciones",
    "user_id": "test_user",
    "session_id": "test_session",
    "new_message": {
      "role": "user",
      "parts": [{
        "text": "Quiero que Gente_Pasto me genere un paisaje sonoro corto"
      }]
    },
    "streaming": false
  }'
```

La respuesta incluirá:
- Texto generado por DATAR (por ejemplo, a través de Gente_Pasto/Sonora/Bosque/Intuitiva).
- Rutas locales y **URLs HTTP de Cloud Storage** (`https://storage.googleapis.com/$MEDIA_BUCKET_NAME/...`) para `.wav` y `.png`.

Esas URLs se pueden usar directamente en:
- `<audio src="...">` o `<img src="...">` en una web‑app.
- Mensajes y adjuntos de un bot de Discord.

---

### 7. Esquema de integración con backend (para Discord / web‑app)

Manteniendo Cloud Run **privado**, el patrón recomendado es:

- Un **backend propio** (otro Cloud Run, GKE, etc.) con su propia service account:
  - Tiene rol `roles/run.invoker` sobre el servicio `datar-integraciones`.
  - Obtiene un **identity token** con audiencia `aud = APP_URL`.
  - Llama a `POST $APP_URL/run` (o `/run_sse`) con:
    - `Authorization: Bearer <TOKEN>`.
- Ese backend expone sus propios endpoints a:
  - Un **bot de Discord** (solo ve el backend, no GCP directamente).
  - Una **web‑app** (frontend) que habla con el backend.

Flujo típico:
1. Discord o la web‑app hacen una petición a tu backend (por ejemplo `/datar/gente-pasto`).
2. El backend construye el `new_message` para la app DATAR y llama a Cloud Run con token de identidad.
3. Recibe del agente:
   - Texto.
   - URLs de Cloud Storage (.wav/.png).
4. El backend devuelve eso al bot o al frontend, que ahora puede:
   - Mostrar imágenes con `<img>`.
   - Reproducir audio con `<audio>`.
   - Compartir directamente las URLs en Discord.

Con estos pasos tienes el flujo completo para:
- Ejecutar **DATAR** en Cloud Run de forma **privada**.
- Guardar y servir los medios desde **Cloud Storage**.
- Integrarte con bots de Discord y web‑apps a través de un backend propio.


