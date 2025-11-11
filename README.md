# {DATAR} - Sistema Agéntico Ambiental Integrado

**Datos Ambientales Territoriales Abiertos Relacionados**

Sistema integrado de agentes autónomos para la exploración de la Estructura Ecológica Principal de Bogotá, combinando los mejores elementos de tres proyectos colaborativos.

---

## 📋 Descripción

DATAR es un laboratorio de experimentación transdisciplinar que utiliza **7 agentes autónomos** impulsados por LLMs para generar una comprensión más situada y vivencial de la Estructura Ecológica Principal (EEP) de Bogotá.

### Origen de la Integración

Este proyecto **unifica el trabajo de múltiples colaboradores**:

- **adk-prueba-main** → Agentes actualizados, orquestador, API completa
- **demoDatar-main** → Referencia funcional y buenas prácticas
- **integracion-main** → Estructura organizativa y estilo visual

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
integracion/
├── API/                          # Backend FastAPI
│   ├── orchestrator/             # Orquestador de agentes
│   │   ├── orchestrator.py       # Lógica de orquestación
│   │   └── __init__.py
│   ├── server.py                 # Servidor principal con endpoints
│   ├── config.py                 # Configuración centralizada
│   ├── .env.example              # Plantilla de variables de entorno
│   ├── .env                      # Variables de entorno (NO SUBIR A GIT)
│   └── requirements.txt          # Dependencias (en raíz)
│
├── DATAR/                        # Orquestación de Agentes
│   ├── agents/
│   │   ├── root_agent.py         # Agente coordinador
│   │   └── sub_agents/           # 7 agentes especializados
│   │       ├── agent.py          # Gente_Montaña
│   │       ├── agentHierba/      # PastoBogotano
│   │       ├── datar_a_gente/    # DiarioIntuitivo
│   │       ├── GuatilaM/         # SequentialPipelineAgent
│   │       ├── LinaPuerto/       # agente_bosque (MCP)
│   │       ├── Sebastian1022/    # agente_sonido
│   │       └── ZolsemiYa/        # horaculo
│   └── __init__.py
│
├── WEB/                          # Frontend
│   ├── index.html                # Interfaz principal
│   ├── css/
│   │   └── styles.css            # Estilos
│   ├── js/
│   │   └── app.js                # Lógica del cliente
│   └── imagen_fondo.jpg          # Imagen de fondo
│
├── run.py                        # Script de inicio rápido
├── requirements.txt              # Dependencias del proyecto
├── .gitignore                    # Archivos ignorados por Git
└── README.md                     # Este archivo
```

### Características Clave

✅ **7 Agentes Especializados** con endpoints dedicados
✅ **Orquestador Inteligente** para gestión de conversaciones
✅ **Dual Model Support**: OpenRouter MiniMax + Gemini o solo Gemini
✅ **Endpoints RESTful** específicos por agente
✅ **Interfaz Web Responsiva** con diseño limpio
✅ **Session Management** in-memory
✅ **API Interactiva** con documentación Swagger

---

## 🚀 Inicio Rápido

### Requisitos Previos

- **Python 3.9+**
- **pip** (gestor de paquetes Python)
- **AL MENOS UNA API Key:**
  - [Google API Key](https://aistudio.google.com/app/apikey) (GRATIS - recomendado) **O**
  - [OpenRouter API Key](https://openrouter.ai/) (opcional - más modelos)

### Instalación

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd integracion

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp API/.env.example API/.env
# Editar API/.env y agregar tu(s) API key(s)
```

### Configuración de API Keys

Edita `API/.env` y agrega **AL MENOS UNA** de estas claves:

```env
# Opción A: Solo Google (más fácil para pruebas)
GOOGLE_API_KEY=tu_api_key_aqui
OPENROUTER_API_KEY=

# Opción B: Con ambas (acceso completo)
GOOGLE_API_KEY=tu_google_key
OPENROUTER_API_KEY=tu_openrouter_key
```

### Ejecución

```bash
# Modo producción
python run.py

# Modo desarrollo (auto-reload)
python run.py --dev

# Cambiar puerto
python run.py --port 9000

# Ver ayuda
python run.py --help
```

El servidor iniciará en:
- **API**: http://localhost:8000
- **Documentación Interactiva**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000/static/index.html

---

## 🤖 Agentes Disponibles

El sistema cuenta con **7 agentes especializados** coordinados por un agente raíz:

### 1. Gente Montaña 🏔️
**ID**: `gente_montana`
**Endpoint**: `POST /api/chat/gente_montana`

Saluda desde la montaña - Perspectiva de los Cerros Orientales de Bogotá.

**Modelo**: Gemini 2.5 Flash

---

### 2. PastoBogotano 🌿
**ID**: `pasto_bogotano`
**Endpoint**: `POST /api/chat/pasto_bogotano`

Especialista en pastos y vegetación bogotana.

**Modelo**: Gemini 2.5 Flash

---

### 3. Diario Intuitivo 📔
**ID**: `diario_intuitivo`
**Endpoint**: `POST /api/chat/diario_intuitivo`

Crea visualizaciones emocionales e intuitivas basadas en emojis.

**Funcionalidades**:
- Interpretación emocional de emojis
- Generación de imágenes PNG con NumPy/Pillow
- Dos pasos: enviar emojis → decir "imagen"

**Modelo**: Gemini 2.5 Flash

---

### 4. GuatilaM 🥒
**ID**: `guatila_m`
**Endpoint**: `POST /api/chat/guatila_m`

Pipeline paralelo y secuencial que combina respuestas de texto y emojis.

**Arquitectura**:
1. **Parallel**: `normal_agent` + `emoji_agent` (simultáneos)
2. **Sequential**: `merger_agent` combina las respuestas

**Modelo**: Gemini 2.5 Flash (temperatura 1.6 para creatividad)

---

### 5. Agente Bosque 🌲
**ID**: `agente_bosque`
**Endpoint**: `POST /api/chat/agente_bosque`

Especialista en ecosistemas forestales de Bogotá usando **MCP (Model Context Protocol)**.

**Herramientas MCP**:
- `inferir_especies`: Mapeo de condiciones ambientales → especies
- `explorar_pdf`: Preguntas filosóficas sobre ecología
- `explorar` y `leer_pagina`: Web scraping

**Modelo**: Gemini 2.5 Flash

---

### 6. Agente Sonido 🎵
**ID**: `agente_sonido`
**Endpoint**: `POST /api/chat/agente_sonido`

Genera representaciones biocéntricas de especies del Humedal La Conejera.

**Formatos alternantes**:
1. **Turtle Graphics**: Visualizaciones con Python Turtle
2. **ASCII/Morse**: Representaciones sonoras de especies
3. **Audio NumPy**: Composiciones con NumPy + SoundDevice

**Modelo**: Gemini 2.5 Flash
**Especialidad**: Comunicación no antropocéntrica

---

### 7. Horáculo 🔮
**ID**: `horaculo`
**Endpoint**: `POST /api/chat/horaculo`

Oráculo ambiental con perspectivas profundas sobre ecología y naturaleza.

**Modelo**: Gemini 2.5 Flash

---

## 📡 API Endpoints

### Endpoints Generales

#### Información del Sistema
```
GET /                    # Información general del API
GET /health              # Estado del servidor
GET /docs                # Documentación interactiva (Swagger)
```

#### Gestión de Agentes
```
GET  /api/agents         # Lista todos los agentes disponibles
POST /api/select-agent   # Selecciona un agente específico
```

#### Chat General
```
POST /api/chat           # Envía mensaje al agente (usa orquestador)
```

**Request Body**:
```json
{
  "message": "Hola, ¿cómo estás?",
  "session_id": "opcional_session_id",
  "agent_id": "opcional_agent_id"
}
```

**Response**:
```json
{
  "response": "Respuesta del agente...",
  "agent_name": "Nombre del Agente",
  "session_id": "session_abc123",
  "timestamp": "2025-11-10T12:34:56"
}
```

#### Gestión de Sesiones
```
GET    /api/sessions           # Lista todas las sesiones
GET    /api/sessions/{id}      # Obtiene historial de sesión
DELETE /api/sessions/{id}      # Elimina sesión
```

### Endpoints Específicos por Agente

**Ventajas de endpoints específicos**:
- ✅ Sin selección previa necesaria
- ✅ Sin gestión de sesiones
- ✅ Comunicación directa con el agente
- ✅ RESTful: Un recurso = Un endpoint

#### Formato de Request (todos los agentes)

```bash
POST /api/chat/{agent_id}
Content-Type: application/json

{
  "message": "tu mensaje aquí"
}
```

#### Formato de Response (todos los agentes)

```json
{
  "response": "respuesta del agente",
  "agent_name": "Nombre del Agente",
  "agent_id": "agent_id"
}
```

#### Lista de Endpoints

```
POST /api/chat/gente_montana     # 🏔️ Gente Montaña
POST /api/chat/pasto_bogotano     # 🌿 PastoBogotano
POST /api/chat/diario_intuitivo   # 📔 Diario Intuitivo
POST /api/chat/guatila_m          # 🥒 GuatilaM
POST /api/chat/agente_bosque      # 🌲 Agente Bosque
POST /api/chat/agente_sonido      # 🎵 Agente Sonido
POST /api/chat/horaculo           # 🔮 Horáculo
```

#### Ejemplo de Uso

```bash
# Usando cURL
curl -X POST http://localhost:8000/api/chat/gente_montana \
  -H "Content-Type: application/json" \
  -d '{"message": "hola"}'

# Usando Python
import requests

response = requests.post(
    'http://localhost:8000/api/chat/pasto_bogotano',
    json={'message': '¿Qué pastos hay en Bogotá?'}
)
print(response.json()['response'])

# Usando JavaScript/Fetch
const response = await fetch('http://localhost:8000/api/chat/agente_bosque', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: '¿Qué árboles nativos hay?'})
});
const data = await response.json();
console.log(data.response);
```

---

## 🛠️ Desarrollo

### Agregar un Nuevo Agente

1. **Crear directorio del agente**:
```bash
mkdir -p DATAR/agents/sub_agents/nuevo_agente
```

2. **Crear `agent.py`**:
```python
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='nuevo_agente',
    description='Descripción del agente',
    instruction='Instrucciones del sistema para el agente',
    tools=[],  # Opcional: herramientas
)
```

3. **Registrar en `root_agent.py`**:
```python
from .sub_agents.nuevo_agente.agent import root_agent as nuevo_agente

# Agregar a sub_agents
sub_agents=[
    ...,
    nuevo_agente
]

# Agregar metadata
AGENTS_METADATA = {
    ...
    ,
    'nuevo_agente': {
        'nombre': 'Nombre Amigable',
        'descripcion': 'Descripción breve',
        'color': '#HEXCOLOR',
        'emoji': '🆕'
    }
}
```

4. **Registrar en orquestador** (`API/orchestrator/orchestrator.py`):
```python
from DATAR.agents.sub_agents.nuevo_agente.agent import root_agent as nuevo_agente

AGENTES = {
    ...
    ,
    "nuevo_agente": {
        "nombre": "Nombre Amigable",
        "descripcion": "Descripción breve",
        "agente": nuevo_agente,
        "color": "#HEXCOLOR",
        "emoji": "🆕"
    }
}
```

5. **Agregar endpoint específico** (`API/server.py`):
```python
@app.post("/api/chat/nuevo_agente", response_model=AgentResponse)
async def chat_nuevo_agente(request: SimpleMessageRequest):
    """Chatea con Nuevo Agente"""
    try:
        respuesta = await orchestrator.procesar_mensaje(
            mensaje=request.message,
            agente_id="nuevo_agente"
        )
        if respuesta.get("exitoso"):
            return AgentResponse(
                response=respuesta["mensaje"],
                agent_name=respuesta["agente"],
                agent_id="nuevo_agente"
            )
        else:
            raise HTTPException(status_code=500, detail=respuesta.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### Estructura de un Agente

```python
from google.adk.agents.llm_agent import Agent
from google.adk import tools  # Si usa herramientas

# Definir herramientas (opcional)
def mi_herramienta(parametro: str) -> str:
    """Descripción de la herramienta para el LLM"""
    return f"Resultado: {parametro}"

# Crear agente
root_agent = Agent(
    model='gemini-2.5-flash',  # O 'gemini-2.5-pro'
    name='mi_agente',
    description='Descripción corta del agente',
    instruction='''
    Eres un agente especializado en X.
    Tu objetivo es Y.
    Siempre Z.
    ''',
    tools=[mi_herramienta],  # Opcional
    temperature=1.0,  # 0.0 - 2.0 (creatividad)
)
```

### Patrones Avanzados de Agentes

#### Parallel + Sequential (GuatilaM)

```python
from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent

# Agentes que corren en paralelo
normal_agent = LlmAgent(...)
emoji_agent = LlmAgent(...)

# Agente que combina resultados
merger_agent = LlmAgent(...)

# Combinación
root_agent = SequentialAgent(
    name="pipeline",
    description="Pipeline secuencial",
    sub_agents=[
        ParallelAgent(sub_agents=[normal_agent, emoji_agent]),
        merger_agent
    ]
)
```

#### MCP Integration (Agente Bosque)

```python
from google.adk.integrations import MCPToolset, StdioConnectionParams

# MCP Toolset
mcp_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command="python",
        args=["ruta/al/mcp_server.py"]
    )
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agente_mcp',
    description='Agente con MCP',
    instruction='...',
    tools=mcp_tools.get_tools()
)
```

### Frontend

#### Modificar Interfaz

- **HTML**: `WEB/index.html`
- **CSS**: `WEB/css/styles.css`
- **JavaScript**: `WEB/js/app.js`

Los cambios en frontend son inmediatos (recargar navegador).

#### Conectar con Nuevos Endpoints

Edita `WEB/js/app.js`:

```javascript
async function sendMessage() {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: userInput,
            session_id: sessionId,
            agent_id: selectedAgent.id  // Nuevo parámetro
        })
    });
    const data = await response.json();
    // Procesar respuesta...
}
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

Edita `API/.env`:

```env
# Modelos
AGENT_MODEL=gemini-2.5-flash

# Servidor
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development  # development, production, testing

# Límites
MAX_MESSAGE_LENGTH=2000
MAX_RESPONSE_LENGTH=10000

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Configuración de Modelos

**OpenRouter + Google** (configuración completa):
```env
OPENROUTER_API_KEY=sk-or-v1-xxx
GOOGLE_API_KEY=AIzaSy...
```
- root_agent: MiniMax (gratis en OpenRouter)
- sub-agentes: Gemini 2.5 Flash

**Solo Google** (configuración simplificada):
```env
OPENROUTER_API_KEY=
GOOGLE_API_KEY=AIzaSy...
```
- root_agent: Gemini 2.5 Flash
- sub-agentes: Gemini 2.5 Flash

### CORS

Modifica `API/config.py`:

```python
ALLOWED_ORIGINS: List[str] = [
    "https://mi-dominio.com",
    "https://www.mi-dominio.com",
]
```

---

## 🐛 Solución de Problemas

### Error: "root_agent no pudo ser inicializado"

**Causa**: Falta API key

**Solución**:
1. Verifica `API/.env`
2. Asegúrate de tener `GOOGLE_API_KEY` o `OPENROUTER_API_KEY`
3. Reinicia el servidor

### Error: "No module named 'google.adk'"

**Causa**: Google ADK no instalado

**Solución**:
```bash
pip install google-adk
# o
pip install git+https://github.com/google/adk-toolkit.git
```

### Error: "Error al cargar agentes"

**Causa**: Servidor no está corriendo

**Solución**:
1. Verifica que el servidor esté en http://localhost:8000
2. Abre consola del navegador (F12) para ver errores específicos
3. Verifica que `API_HOST` y `API_PORT` en `.env` coincidan con la URL

### Audio no se genera (agente_sonido)

**Causa**: Falta FFmpeg o dependencias de audio

**Solución**:
```bash
# Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows
# Descargar de https://ffmpeg.org/

# Instalar dependencias Python
pip install pydub sounddevice numpy
```

### MCP Server no responde (agente_bosque)

**Causa**: Servidor MCP no inicia correctamente

**Solución**:
1. Verifica que `python` esté en PATH
2. Prueba ejecutar manualmente:
   ```bash
   python DATAR/agents/sub_agents/MCP/mcp_server_bosque.py
   ```
3. Verifica logs del servidor para ver errores de MCP

---

## 📚 Recursos

### Documentación de Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/)
- [Google ADK](https://github.com/google/adk-toolkit)
- [LiteLLM](https://docs.litellm.ai/)
- [OpenRouter](https://openrouter.ai/docs)
- [Google Gemini](https://ai.google.dev/)

### Proyectos de Referencia

- **adk-prueba-main**: Agentes actualizados y API completa
- **demoDatar-main**: Experiencias guiadas y frontend avanzado
- **integracion-main**: Estructura base y estilo visual

---

## 🤝 Contribuciones

Este proyecto es **colaborativo**. Cada agente fue desarrollado por un participante diferente:

- **Gente Montaña**: Contribuidor original
- **PastoBogotano**: Contribuidor original
- **DiarioIntuitivo** (M4r1l1): Contribuidor original
- **GuatilaM**: Contribuidor original
- **agente_bosque** (LinaPuerto): Contribuidor original
- **agente_sonido** (Sebastian1022): Contribuidor original
- **horaculo** (ZolsemiYa): Contribuidor original

Al modificar agentes, **respetar la estructura y aportes existentes** de cada participante.

---

## 📝 Notas Importantes

### Gestión de Sesiones

Las sesiones se almacenan **en memoria** (`sessions_store` dict). Al reiniciar el servidor, se pierden todas las sesiones.

**Para producción**, implementar almacenamiento persistente:
- Base de datos (PostgreSQL, MongoDB)
- Redis para sesiones temporales
- Sistema de archivos con serialización

### Seguridad

⚠️ **IMPORTANTE**:
- **NO** compartir tu `.env` con API keys
- **NO** subir `.env` a Git (ya está en `.gitignore`)
- En producción, cambiar `allow_origins=["*"]` a dominios específicos
- Implementar autenticación si el sistema es público
- Usar HTTPS en producción

### Modelos y Costos

**OpenRouter MiniMax** (root_agent): **GRATIS** con límites razonables
**Gemini 2.5 Flash** (sub-agentes): **GRATIS** hasta 1500 requests/día

Para producción con alto tráfico, considerar modelos de pago o self-hosted.

---

## 📄 Licencia

[Especificar licencia del proyecto]

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar esta documentación
2. Verificar logs del servidor: consola donde ejecutaste `python run.py`
3. Consultar documentación de Google ADK
4. Revisar issues del repositorio (si aplica)

---

**{DATAR}** - Estructura Ecológica Principal de Bogotá · 2025
