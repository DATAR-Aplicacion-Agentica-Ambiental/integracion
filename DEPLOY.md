# Guía de Despliegue en Google Cloud

Proyecto: **datar-476419**

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
gcloud config set project datar-476419

# Verificar que estás en el proyecto correcto
gcloud config get-value project
```

## Paso 2: Eliminar Despliegue Anterior

```bash
# Ver las versiones desplegadas actualmente
gcloud app versions list

# Detener y eliminar todas las versiones anteriores
# Reemplaza VERSION_ID con cada versión que quieras eliminar
gcloud app versions delete VERSION_ID --quiet

# O eliminar todo el servicio default (cuidado: esto elimina todo)
gcloud app services delete default --quiet
```

**Alternativa más simple** (si solo quieres reemplazar):
```bash
# Simplemente despliega - la nueva versión reemplazará la anterior
# No necesitas eliminar nada, App Engine gestiona las versiones
```

## Paso 3: Configurar API Keys

**Opción A - Variables de entorno en app.yaml** (más simple pero menos seguro):

Edita el archivo `app.yaml` y agrega tus API keys:

```yaml
env_variables:
  OPENROUTER_API_KEY: "tu-clave-real-aqui"
  # o
  GOOGLE_API_KEY: "tu-clave-real-aqui"
```

**Opción B - Secret Manager** (más seguro, recomendado para producción):

```bash
# Habilitar Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Crear secretos
echo -n "tu-openrouter-api-key" | gcloud secrets create openrouter-api-key --data-file=-
echo -n "tu-google-api-key" | gcloud secrets create google-api-key --data-file=-

# Dar acceso a App Engine
PROJECT_NUMBER=$(gcloud projects describe datar-476419 --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding openrouter-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Si usas Secret Manager, modifica `app.yaml` así:
```yaml
env_variables:
  OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
```

Y crea un archivo `app.yaml` con beta features (App Engine Flex).

## Paso 4: Desplegar la Aplicación

```bash
# Desde el directorio raíz del proyecto (integracion/)
gcloud app deploy --quiet

# Espera 5-10 minutos mientras se despliega
```

## Paso 5: Verificar el Despliegue

```bash
# Ver el estado
gcloud app describe

# Abrir la aplicación en el navegador
gcloud app browse

# Ver logs en tiempo real
gcloud app logs tail -s default
```

Tu aplicación estará disponible en: `https://datar-476419.uc.r.appspot.com/`

## Comandos Útiles Post-Despliegue

```bash
# Ver todas las versiones
gcloud app versions list

# Cambiar tráfico entre versiones (si tienes múltiples)
gcloud app services set-traffic default --splits VERSION_ID=1

# Ver logs de errores
gcloud app logs read --service=default --level=error

# Escalar manualmente (si es necesario)
gcloud app instances list
```

## Solución de Problemas Comunes

### Error: "API key not configured"
- Verifica que las API keys estén correctamente configuradas en `app.yaml`
- Revisa los logs: `gcloud app logs tail -s default`

### Error: "Module not found"
- Asegúrate de que `DATAR/requirements.txt` incluye todas las dependencias
- Ejecuta localmente primero para verificar

### El servidor no responde
- Verifica el health check: `curl https://datar-476419.uc.r.appspot.com/health`
- Revisa los logs: `gcloud app logs tail -s default`

### Tiempo de inicio muy largo
- Es normal en la primera petición (cold start)
- Considera usar `min_instances: 1` en `app.yaml` para mantener una instancia siempre activa

## Actualizar la Aplicación

Para actualizar después de hacer cambios:

```bash
# Hacer commit de tus cambios
git add .
git commit -m "Descripción de cambios"

# Redesplegar
gcloud app deploy --quiet
```

## Eliminar Todo (Deshacer Despliegue)

```bash
# Eliminar la versión actual
gcloud app versions delete VERSION_ID --service=default

# Para eliminar completamente App Engine (irreversible)
# Nota: No se puede eliminar completamente, solo deshabilitar
gcloud app services delete default --quiet
```

---

**Importante**: Después del primer despliegue, la URL de tu aplicación será:
- API: `https://datar-476419.uc.r.appspot.com/`
- Docs: `https://datar-476419.uc.r.appspot.com/docs`
- Frontend: `https://datar-476419.uc.r.appspot.com/static/index.html`
