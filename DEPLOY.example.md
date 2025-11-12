# Guía de Despliegue en Google Cloud

Proyecto: **[TU-PROYECTO-ID]**

## Prerrequisitos

1. Tener Google Cloud SDK instalado ([Descargar aquí](https://cloud.google.com/sdk/docs/install))
2. Tener tus API keys listas:
   - `OPENROUTER_API_KEY` (recomendado) o
   - `GOOGLE_API_KEY` / `GEMINI_API_KEY`

## Paso 1: Autenticación y Configuración

```bash
# Autenticarse en Google Cloud
gcloud auth login

# Configurar el proyecto
gcloud config set project [TU-PROYECTO-ID]

# Verificar que estás en el proyecto correcto
gcloud config get-value project
```

## Paso 2: Configurar API Keys

### Para Cloud Run (Recomendado):

```bash
# Desplegar con variables de entorno
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY="tu-clave-aqui",API_HOST="0.0.0.0",API_ENV="production"
```

### Para App Engine:

1. Copia `app.yaml.example` a `app.yaml`
2. Edita `app.yaml` y agrega tus API keys reales
3. Despliega: `gcloud app deploy`

## Paso 3: Verificar el Despliegue

```bash
# Ver servicios de Cloud Run
gcloud run services list

# Ver logs
gcloud run services logs read datar --region=us-central1

# Abrir en el navegador
gcloud run services describe datar --region=us-central1 --format="value(status.url)"
```

## Comandos Útiles

```bash
# Ver todas las versiones
gcloud run revisions list --service=datar --region=us-central1

# Ver logs en tiempo real
gcloud run services logs tail datar --region=us-central1

# Eliminar servicio
gcloud run services delete datar --region=us-central1
```

## Solución de Problemas

### Error: Container failed to start
- Verifica que el puerto coincida con la variable PORT de Cloud Run
- Revisa los logs: `gcloud run services logs read`

### Error: API key not configured
- Verifica las variables de entorno del servicio
- Asegúrate de que la API key sea válida

---

**Nota**: Este es un archivo de ejemplo. Crea tu propio `DEPLOY.md` con información específica de tu proyecto (sin subirlo a git).
