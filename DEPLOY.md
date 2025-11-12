## PASO 1: Preparar tu API Key de Google

Antes de empezar, necesitas una API key de Google AI Studio (es **GRATIS**):

1. Ve a: https://aistudio.google.com/app/apikey
2. Haz clic en "Create API Key"
3. Copia la key que empieza con `AIzaSy...`
4. **Guárdala en un lugar seguro**

---

## PASO 2: Crear una cuenta en Google Cloud

1. Ve a: https://console.cloud.google.com
2. Inicia sesión con tu cuenta de Google
3. Acepta los términos y condiciones

---

## PASO 3: Crear un Proyecto en Google Cloud

1. En la consola de Google Cloud, haz clic en el menú desplegable de proyectos (arriba a la izquierda)
2. Haz clic en "NEW PROJECT" (Proyecto Nuevo)
3. Dale un nombre, por ejemplo: `datar-bogota`
4. Haz clic en "CREATE" (Crear)
5. Espera unos segundos y selecciona el proyecto recién creado

---

## PASO 4: Instalar Google Cloud CLI

Necesitas instalar el comando `gcloud` en tu computadora:

### Windows:
1. Descarga el instalador: https://cloud.google.com/sdk/docs/install
2. Ejecuta el instalador y sigue las instrucciones
3. Abre una nueva terminal (PowerShell o CMD)

### macOS:
```bash
# Instalar usando Homebrew
brew install google-cloud-sdk
```

### Linux/WSL:
```bash
# Instalar gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Verificar instalación:
```bash
gcloud --version
```

Deberías ver algo como: `Google Cloud SDK 450.0.0`

---

## PASO 5: Iniciar Sesión y Configurar

Abre tu terminal y ejecuta:

```bash
# 1. Iniciar sesión
gcloud auth login
```
Se abrirá tu navegador. Inicia sesión con tu cuenta de Google.

```bash
# 2. Configurar el proyecto (reemplaza 'datar-bogota' con el nombre de tu proyecto)
gcloud config set project datar-bogota
```

```bash
# 3. Habilitar los servicios necesarios
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

Este último comando puede tardar 1-2 minutos. Es normal.

---

## PASO 6: Navegar a la carpeta del proyecto

En tu terminal, ve a la carpeta donde está DATAR:

```bash
cd "/mnt/c/Users/chris/OneDrive/Documents/DATAR FIN INTEGRADO/integracion"
```

Verifica que estás en la carpeta correcta:
```bash
ls
```

Deberías ver: `API/`, `DATAR/`, `WEB/`, `Dockerfile`, etc.

---

## PASO 7: Hacer el Deploy

Ahora viene la magia. Ejecuta este comando:

```bash
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="TU_API_KEY_AQUI" \
  --set-env-vars API_ENV=production \
  --memory 1Gi \
  --timeout 300
```

⚠️ **IMPORTANTE**: Reemplaza `TU_API_KEY_AQUI` con tu API key de Google (la del PASO 1).

**¿Qué hace este comando?**
- `--source .`: Usa el código de la carpeta actual
- `--region us-central1`: Ubicación del servidor (Estados Unidos central)
- `--allow-unauthenticated`: Permite acceso público sin login
- `--set-env-vars`: Configura las variables de entorno (API keys)
- `--memory 1Gi`: Asigna 1GB de RAM
- `--timeout 300`: Tiempo máximo de respuesta: 5 minutos

**Tiempo estimado**: 5-10 minutos la primera vez.

Durante el proceso verás:
```
Building using Dockerfile...
✓ Creating Container Registry
✓ Uploading sources
✓ Building image
✓ Deploying to Cloud Run
```

---

## PASO 8: ¡Listo! Obtener la URL

Cuando termine, verás algo como:

```
Service [datar] revision [datar-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://datar-xxxxx-uc.a.run.app
```

**¡Esa es tu URL pública!** Copia esa URL.

---

## PASO 9: Probar tu aplicación

Abre tu navegador y ve a:

```
https://datar-xxxxx-uc.a.run.app/static/index.html
```

Deberías ver el frontend de DATAR.

También puedes probar:
- **API Docs**: `https://datar-xxxxx-uc.a.run.app/docs`
- **Health Check**: `https://datar-xxxxx-uc.a.run.app/health`
- **Lista de agentes**: `https://datar-xxxxx-uc.a.run.app/api/agents`

---

## PASO 10: Configurar Variables de Entorno Adicionales (Opcional)

Si también quieres usar OpenRouter (para el modelo MiniMax del root_agent):

```bash
gcloud run services update datar \
  --region us-central1 \
  --set-env-vars OPENROUTER_API_KEY="tu_openrouter_key_aqui"
```

---

## Comandos Útiles

### Ver logs en tiempo real:
```bash
gcloud run services logs tail datar --region us-central1
```

### Ver información del servicio:
```bash
gcloud run services describe datar --region us-central1
```

### Actualizar el código (después de hacer cambios):
```bash
gcloud run deploy datar \
  --source . \
  --region us-central1
```

### Eliminar el servicio (si quieres darlo de baja):
```bash
gcloud run services delete datar --region us-central1
```

---

## Solución de Problemas

### Error: "API not enabled"
Ejecuta:
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### Error: "Permission denied"
Asegúrate de haber hecho login:
```bash
gcloud auth login
```

### Error: "GOOGLE_API_KEY not found"
Verifica que configuraste la variable:
```bash
gcloud run services describe datar --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

### La aplicación no responde
1. Verifica los logs:
   ```bash
   gcloud run services logs read datar --region us-central1 --limit 50
   ```
2. Verifica que la API key sea correcta
3. Asegúrate de que el servicio esté en estado "READY"

### Error de memoria o timeout
Aumenta recursos:
```bash
gcloud run services update datar \
  --region us-central1 \
  --memory 2Gi \
  --timeout 600
```

---

## Costos Estimados

Cloud Run tiene una **capa gratuita generosa**:

- **2 millones** de solicitudes por mes: GRATIS
- **360,000** GB-segundos de memoria: GRATIS
- **180,000** vCPU-segundos: GRATIS

Para DATAR (con uso moderado), probablemente **permanecerás en la capa gratuita**.

Si excedes, el costo es aprox. **$0.40 USD por millón de solicitudes adicionales**.

Puedes ver tus costos en: https://console.cloud.google.com/billing

---

## Próximos Pasos (Avanzado)

Una vez que tu app esté funcionando, puedes:

1. **Configurar un dominio personalizado**
   - En Cloud Run, ve a "Manage Custom Domains"
   - Conecta tu propio dominio (ej: `datar.tudominio.com`)

2. **Configurar CI/CD con GitHub**
   - Conecta tu repositorio de GitHub
   - Deploy automático en cada push

3. **Agregar una base de datos**
   - Cloud SQL para persistencia de sesiones
   - Firestore para almacenar conversaciones

4. **Configurar monitoreo**
   - Cloud Monitoring para métricas
   - Alertas cuando algo falla

---

## Recursos Adicionales

- 📚 **Documentación de Cloud Run**: https://cloud.google.com/run/docs
- 🎓 **Tutorial oficial**: https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service
- 💬 **Soporte de Google Cloud**: https://cloud.google.com/support
- 📖 **Documentación de DATAR**: Ver `CLAUDE.md` en este proyecto

---

## Resumen de Comandos

```bash
# Setup inicial (solo una vez)
gcloud auth login
gcloud config set project datar-bogota
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Deploy
cd "/ruta/a/integracion"
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="TU_API_KEY"

# Ver logs
gcloud run services logs tail datar --region us-central1

# Actualizar
gcloud run deploy datar --source . --region us-central1
```

---

## ¿Necesitas Ayuda?

Si tienes problemas:

1. Revisa los logs: `gcloud run services logs read datar --region us-central1 --limit 50`
2. Verifica la documentación de Cloud Run
3. Consulta la documentación del proyecto en `CLAUDE.md`
4. Abre un issue en el repositorio del proyecto

---

**¡Felicidades!** 🎉 Has desplegado DATAR en Google Cloud Run.
