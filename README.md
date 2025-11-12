# DATAR - Sistema Agéntico Ambiental

> Aplicación agéntica para la exploración e interpretación de la Estructura Ecológica Principal de Bogotá

DATAR es un sistema de agentes autónomos diseñado para facilitar la comprensión y exploración sensorial de ecosistemas urbanos, utilizando inteligencia artificial para generar experiencias interactivas que conectan a las personas con su entorno natural.

## 🌱 Descripción

DATAR integra múltiples agentes especializados que ofrecen diferentes perspectivas para entender y experimentar ecosistemas urbanos:

- **Exploración sensorial** de bosques y humedales
- **Interpretación emocional** del territorio
- **Composición sonora** de ambientes naturales
- **Visualización de datos** ecológicos
- **Cartografías emocionales** interactivas

## 🏗️ Arquitectura

El proyecto está organizado en tres componentes principales:

```
integracion/
├── DATAR/          # Sistema de orquestación de agentes
│   └── datar/
│       ├── agent.py              # Agente raíz (root_agent)
│       └── sub_agents/           # 8 agentes especializados
│           ├── Gente_Bosque/     # Exploración forestal
│           ├── Gente_Interpretativa/  # Interpretación con emojis
│           ├── Gente_Sonora/     # Composición sonora
│           ├── Gente_Intuitiva/  # Visualización de datos
│           ├── Gente_Pasto/      # Ecosistemas de pastizal
│           ├── Gente_Montaña/    # Ambientes montañosos
│           ├── Gente_Horaculo/   # Predicciones ecológicas
│           └── Gente_Compostada/ # Procesos de descomposición
├── API/            # Backend FastAPI
│   ├── server.py   # Servidor principal
│   └── config.py   # Configuración
└── WEB/            # Frontend web estático
    ├── index.html
    └── js/app.js
```

### Tecnologías Principales

- **Google ADK (Agent Development Kit)**: Orquestación de agentes
- **LiteLLM**: Integración multi-modelo (OpenRouter, Gemini)
- **FastAPI**: API REST backend
- **Python 3.13**: Lenguaje principal
- **Docker**: Contenedorización
- **Google Cloud Run**: Despliegue en producción

## 🚀 Instalación

### Prerrequisitos

- Python 3.13+
- pip
- Git
- (Opcional) Docker para containerización

### Instalación Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/integracion.git
cd integracion
```

2. **Instalar dependencias:**
```bash
cd DATAR
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
cd ../API
cp .env.example .env
# Editar .env y agregar tu OPENROUTER_API_KEY o GOOGLE_API_KEY
```

4. **Ejecutar el servidor:**
```bash
python server.py
```

El servidor estará disponible en `http://localhost:8000`

## 🔑 Configuración

### API Keys Requeridas

Necesitas **al menos una** de estas API keys:

- **OPENROUTER_API_KEY** (recomendado): Para usar MiniMax en el agente raíz
  - Obtener en: https://openrouter.ai/

- **GOOGLE_API_KEY** / **GEMINI_API_KEY**: Para usar Gemini
  - Obtener en: https://aistudio.google.com/app/apikey

### Variables de Entorno

Archivo `API/.env`:

```env
# API Keys (mínimo una requerida)
OPENROUTER_API_KEY=sk-or-v1-...
GOOGLE_API_KEY=AIza...

# Configuración del servidor
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development
```

## 📚 Uso

### API Endpoints

#### Obtener información del sistema
```bash
GET /
GET /health
```

#### Listar agentes disponibles
```bash
GET /api/agents
```

#### Chatear con los agentes
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Describe el bosque que te rodea",
  "session_id": "opcional-uuid",
  "agent_id": "Gente_Bosque"  // opcional
}
```

#### Gestionar sesiones
```bash
GET /api/sessions              # Listar sesiones
GET /api/sessions/{id}         # Obtener historial
DELETE /api/sessions/{id}      # Eliminar sesión
```

### Ejemplo de Uso con curl

```bash
# Chat con el sistema
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué especies puedo encontrar en un bosque húmedo?"
  }'
```

### Frontend Web

Accede a la interfaz web en:
```
http://localhost:8000/static/index.html
```

## 🎭 Agentes Especializados

### 🌳 Gente Bosque
Guía de exploración forestal basada en percepciones sensoriales. Genera cartografías emocionales del territorio.

**Características:**
- Inferencia de especies según condiciones ambientales
- Preguntas reflexivas sobre simbiosis y cooperación
- Mapas emocionales con prettymaps
- Integración MCP para herramientas extendidas

### 🔄 Gente (Re)Interpretativa
Interpreta el entorno usando emojis y texto en bucles de orquestación paralela.

**Características:**
- Orquestación secuencial y paralela de sub-agentes
- Interpretación dual: emojis + texto
- Fusión de perspectivas múltiples
- Re-interpretación final personalizada

### 🎵 Gente Sonora
Crea composiciones sonoras inmersivas de ambientes naturales.

**Características:**
- Síntesis de sonidos ambientales
- Generación de paisajes sonoros
- Visualización de ondas y espectros
- Exportación de archivos de audio

### 📊 Gente Intuitiva
Visualización de datos ecológicos con artifacts generativos.

### 🌾 Otros Agentes
- **Gente Pasto**: Ecosistemas de pastizal y humedal
- **Gente Montaña**: Ambientes de montaña
- **Gente Horaculo**: Predicciones y análisis temporal
- **Gente Compostada**: Ciclos de descomposición

## 🐳 Docker

### Construir la imagen
```bash
docker build -t datar:latest .
```

### Ejecutar el contenedor
```bash
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY="tu-api-key" \
  -e API_ENV="production" \
  datar:latest
```

## ☁️ Despliegue en Google Cloud

### Cloud Run (Recomendado)

```bash
# Autenticar
gcloud auth login
gcloud config set project tu-proyecto-id

# Desplegar
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY="tu-clave"
```

Más detalles en `DEPLOY.example.md`

### Costos Estimados

- **Desarrollo/Pruebas**: $0-5 USD/mes (escala a cero)
- **Producción baja**: $10-30 USD/mes
- **Producción media**: $30-100 USD/mes

## 🧪 Testing

```bash
# Ejecutar tests (si existen)
pytest

# Verificar salud del servidor
curl http://localhost:8000/health
```

## 📁 Estructura de Archivos Generados

Los agentes pueden generar archivos durante la interacción:

```
WEB/outputs/                           # Archivos generados accesibles vía web
DATAR/.../Gente_Bosque/cartografias/  # Mapas emocionales HTML
DATAR/.../Gente_Intuitiva/imagenes_generadas/  # Visualizaciones PNG
DATAR/.../Gente_Sonora/output/        # Audio y gráficos
```

Estos archivos están excluidos de Git (`.gitignore`) y se crean en runtime.

## 🤝 Contribución

Este proyecto es parte de la investigación sobre sistemas agénticos ambientales.

### Guías de Contribución

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

### Estructura de Commits

```
feat: Agrega nuevo agente para X
fix: Corrige error en Y
docs: Actualiza documentación de Z
refactor: Mejora estructura de W
```

## 🔒 Seguridad

**⚠️ IMPORTANTE**: Nunca subas archivos con API keys al repositorio.

Archivos protegidos en `.gitignore`:
- `API/.env`
- `app.yaml`
- `DEPLOY.md`

Usa los archivos `.example` como templates.

## 📄 Licencia

Ver archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- **MangleRojo ORG**: Orquestación de agentes
- **Laboratoristas**:
```
      1. Angie Catalina Quintero Rivera
      2. Juan Pablo Roa Paez
      3. Lina María González Rodríguez
      4. Lina Duarte Tovar
      5. Diego Alejandro Rojas Merchán
      6. Lina Sofía Puerto Rojas
      7. Julián Felipe González Sanchez
      8. Johan Camilo Méndez Castro
      9. Linda Ximena Torres Gutiérrez
      10. Diana Catalina Charry Mesa
      11. Victor Manuel Jaramillo
      12. Nicolás Gaitán Albarracín
      13. Laura Carolina Triana Martínez
      14. Daniel Panche
      15. Javier Camilo Guevara Rodríguez
  ```
- [**cdavidbm**:](https://github.com/cdavidbm) Desarrollo API y Web

## 📞 Contacto

Para preguntas o colaboraciones, abre un issue en el repositorio.

---

**Hecho con 🌱 para conectar personas con naturaleza a través de IA**
