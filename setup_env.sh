#!/bin/bash
# Script para configurar el archivo .env de DATAR

echo "🔧 Configurador de DATAR - Setup .env"
echo "======================================"
echo ""

# Verificar si ya existe .env
if [ -f ".env" ]; then
    echo "⚠️  El archivo .env ya existe."
    read -p "¿Deseas sobrescribirlo? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Cancelado"
        exit 1
    fi
fi

echo ""
echo "📝 Por favor, ingresa tu información:"
echo ""

# Pedir API keys
read -p "🔑 OpenRouter API Key (sk-or-v1-...): " OPENROUTER_KEY
read -p "🔑 Google Gemini API Key (opcional, presiona Enter para saltar): " GOOGLE_KEY

# Crear archivo .env
cat > .env << EOF
# OpenRouter Configuration
OPENROUTER_API_KEY=$OPENROUTER_KEY

# Google Gemini (opcional)
GOOGLE_API_KEY=$GOOGLE_KEY

# Server Configuration
API_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Agent Configuration
AGENT_MODEL=gemini-2.5-flash
AGENT_NAME=root_agent
EOF

echo ""
echo "✅ Archivo .env creado exitosamente"
echo ""
echo "📋 Contenido:"
echo "---"
cat .env
echo "---"
echo ""
echo "⚠️  Nota: El archivo .env está en .gitignore y no será commiteado"

