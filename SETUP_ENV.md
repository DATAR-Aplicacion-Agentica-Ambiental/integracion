# 🔧 Configuración de Variables de Entorno - DATAR

## Problema Actual

El error que ves es porque **no existe un archivo `.env`** con tu clave API de OpenRouter:

```
litellm.exceptions.AuthenticationError: OpenrouterException - {"error":{"message":"User not found.","code":401}}
```

## Solución

### Opción 1: Usando el script automatizado (RECOMENDADO)

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1
chmod +x setup_env.sh
./setup_env.sh
```

Luego ingresa:
1. Tu clave API de OpenRouter (obtenla de https://openrouter.ai)
2. Tu clave de Google Gemini (opcional)

### Opción 2: Crear el archivo manualmente

1. Abre una terminal en el directorio del proyecto:
```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1
```

2. Crea el archivo `.env`:
```bash
cat > .env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-TU_CLAVE_AQUI
GOOGLE_API_KEY=TU_CLAVE_GEMINI_AQUI
API_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
AGENT_MODEL=gemini-2.5-flash
AGENT_NAME=root_agent
EOF
```

3. Reemplaza `TU_CLAVE_AQUI` con tu clave real.

## Obtener tu OpenRouter API Key

1. Ve a https://openrouter.ai
2. Registrate o inicia sesión
3. Ve a la sección de "API Keys" en tu panel
4. Crea una nueva clave API
5. Cópiala completamente (comienza con `sk-or-v1-`)

## Verificar que funcione

Después de crear `.env`, intenta ejecutar tu agente:

```bash
cd /Users/manglerojo/Desarollo/DATAR/integracion-1/DATAR
adk run root_agent
```

Si ves un mensaje de bienvenida, ¡está funcionando! ✅

## Seguridad

- El archivo `.env` está en `.gitignore` - **NUNCA será commiteado**
- Tus claves API están protegidas
- No compartas tu `.env` con nadie

## Cambios hechos en el código

Se mejoró `DATAR/datar/agent.py` para:
1. ✅ Cargar automáticamente el `.env`
2. ✅ Validar que exista `OPENROUTER_API_KEY`
3. ✅ Dar un error claro si falta la configuración

## Dudas o problemas

Si aún tienes problemas después de crear el `.env`:
- Verifica que tu API key sea válida
- Verifica que tu cuenta en OpenRouter tenga créditos
- Verifica que el formato sea: `sk-or-v1-xxxxx`

