#!/bin/bash
# Script de Deploy Rápido para DATAR
# Uso: ./deploy-quick.sh

set -e

echo "🚀 Deploy Rápido de DATAR"
echo "=========================="
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI no está instalado"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ No has iniciado sesión en gcloud"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi

# Variables
PROJECT="datar-476419"
REGION="us-central1"
SERVICE="datar"

echo "📋 Configuración:"
echo "  Proyecto: $PROJECT"
echo "  Región: $REGION"
echo "  Servicio: $SERVICE"
echo ""

# Verificar que estemos en el directorio correcto
if [ ! -f "Dockerfile" ]; then
    echo "❌ ERROR: No se encuentra Dockerfile"
    echo "Asegúrate de estar en el directorio raíz del proyecto"
    exit 1
fi

echo "🔨 Iniciando deploy..."
echo ""

# Deploy rápido (reutiliza configuración previa)
gcloud run deploy $SERVICE \
  --source . \
  --region $REGION \
  --project $PROJECT \
  --quiet

echo ""
echo "✅ Deploy completado"
echo ""

# Obtener URL
URL=$(gcloud run services describe $SERVICE --region $REGION --project $PROJECT --format="value(status.url)" 2>/dev/null)

echo "=========================="
echo "🎉 DATAR Actualizado"
echo "=========================="
echo ""
echo "🌐 URL: $URL"
echo "🎨 Frontend: $URL/static/index.html"
echo "📚 API Docs: $URL/docs"
echo ""
echo "📊 Ver logs:"
echo "  gcloud run services logs tail $SERVICE --region $REGION --project $PROJECT"
echo ""
echo "=========================="
