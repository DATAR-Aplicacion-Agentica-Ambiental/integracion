#!/bin/bash
# Script de Deploy para DATAR en Google Cloud Run
# Uso: ./deploy.sh

set -e  # Salir si hay errores

echo "=============================================="
echo "🌱 DATAR - Deploy a Google Cloud Run"
echo "=============================================="
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI no está instalado"
    echo ""
    echo "Por favor instala gcloud CLI:"
    echo "  https://cloud.google.com/sdk/docs/install"
    echo ""
    exit 1
fi

echo "✅ gcloud CLI encontrado"

# Verificar que el usuario esté autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ No has iniciado sesión en gcloud"
    echo ""
    echo "Por favor ejecuta: gcloud auth login"
    echo ""
    exit 1
fi

ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo "✅ Autenticado como: $ACCOUNT"

# Obtener el proyecto configurado
PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT" ]; then
    echo ""
    echo "❌ No hay un proyecto configurado"
    echo ""
    echo "Por favor ejecuta: gcloud config set project TU_PROYECTO"
    echo ""
    exit 1
fi

echo "✅ Proyecto configurado: $PROJECT"
echo ""

# Preguntar por la API key si no está configurada
echo "📝 Configuración de Variables de Entorno"
echo ""
read -p "Ingresa tu GOOGLE_API_KEY (de https://aistudio.google.com/app/apikey): " GOOGLE_API_KEY

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ La GOOGLE_API_KEY es obligatoria"
    exit 1
fi

# Preguntar por OpenRouter (opcional)
read -p "¿Tienes una OPENROUTER_API_KEY? (opcional, presiona Enter para omitir): " OPENROUTER_API_KEY

# Región
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-datar}

echo ""
echo "=============================================="
echo "📦 Configuración del Deploy"
echo "=============================================="
echo "Proyecto: $PROJECT"
echo "Región: $REGION"
echo "Servicio: $SERVICE_NAME"
echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:10}..."
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:0:10}..."
else
    echo "OPENROUTER_API_KEY: (no configurada)"
fi
echo "=============================================="
echo ""

read -p "¿Continuar con el deploy? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploy cancelado"
    exit 0
fi

echo ""
echo "🚀 Iniciando deploy..."
echo ""

# Construir el comando de deploy
DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=\"$GOOGLE_API_KEY\" \
  --set-env-vars API_ENV=production \
  --set-env-vars API_HOST=0.0.0.0 \
  --memory 1Gi \
  --timeout 300"

# Agregar OpenRouter si existe
if [ -n "$OPENROUTER_API_KEY" ]; then
    DEPLOY_CMD="$DEPLOY_CMD --set-env-vars OPENROUTER_API_KEY=\"$OPENROUTER_API_KEY\""
fi

# Ejecutar deploy
eval $DEPLOY_CMD

echo ""
echo "=============================================="
echo "✅ Deploy completado exitosamente"
echo "=============================================="
echo ""
echo "Tu aplicación está disponible en:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo "🌐 URL del servicio: $SERVICE_URL"
echo "🎨 Frontend: $SERVICE_URL/static/index.html"
echo "📚 API Docs: $SERVICE_URL/docs"
echo ""
echo "Para ver los logs en tiempo real:"
echo "  gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo ""
echo "=============================================="
