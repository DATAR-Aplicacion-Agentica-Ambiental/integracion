#!/bin/bash
# Script de Deploy INMEDIATO para DATAR
# Uso: ./deploy-now.sh

set -e

echo "🚀 DEPLOY INMEDIATO DE DATAR"
echo "============================="
echo ""

# Variables
PROJECT="datar-476419"
REGION="us-central1"
SERVICE="datar"
OPENROUTER_KEY="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"

echo "📋 Configuración:"
echo "  Proyecto: $PROJECT"
echo "  Región: $REGION"
echo "  Servicio: $SERVICE"
echo "  Modelo: minimax/minimax-01"
echo ""

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI no instalado"
    exit 1
fi

echo "🔨 Desplegando a Cloud Run..."
echo ""

# Deploy con configuración completa
gcloud run deploy $SERVICE \
  --source . \
  --region $REGION \
  --project $PROJECT \
  --set-env-vars OPENROUTER_API_KEY=$OPENROUTER_KEY \
  --set-env-vars API_ENV=production \
  --set-env-vars LOG_LEVEL=INFO \
  --port 8080 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --quiet

echo ""
echo "✅ DEPLOYMENT COMPLETADO"
echo ""

# Obtener URL
URL=$(gcloud run services describe $SERVICE --region $REGION --project $PROJECT --format="value(status.url)" 2>/dev/null)

echo "============================="
echo "🎉 DATAR EN PRODUCCIÓN"
echo "============================="
echo ""
echo "🌐 URL Principal: $URL"
echo "🎨 Frontend: $URL/static/index.html"
echo "📚 API Docs: $URL/docs"
echo "💬 Chat API: $URL/api/chat"
echo ""
echo "📊 Ver logs en tiempo real:"
echo "  gcloud run services logs tail $SERVICE --region $REGION --project $PROJECT"
echo ""
echo "============================="
