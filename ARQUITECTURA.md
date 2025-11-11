# Principios Arquitectónicos

### 1. Separation of Concerns (SoC)
Cada capa tiene responsabilidades claramente definidas sin solapamiento:
- **WEB/**: Interfaz de usuario y presentación
- **API/**: Lógica de aplicación, HTTP, sesiones
- **DATAR/**: Lógica de dominio, agentes AI

### 2. Layered Architecture
```
┌─────────────────────────────────────────┐
│         Capa de Presentación            │
│              (WEB/)                     │
│  HTML5, CSS3, Vanilla JavaScript        │
└─────────────────────────────────────────┘
                    ↓ HTTP/REST
┌─────────────────────────────────────────┐
│       Capa de Aplicación (API/)         │
│  FastAPI, Orchestrator, Sessions        │
│  • Routing HTTP                         │
│  • Gestión de sesiones                  │
│  • Validación de entrada                │
│  • Formateo de respuestas               │
└─────────────────────────────────────────┘
                    ↓ Function Calls
┌─────────────────────────────────────────┐
│      Capa de Dominio (DATAR/)           │
│  Google ADK Agents                      │
│  • Lógica de agentes                    │
│  • Coordinación jerárquica              │
│  • Procesamiento LLM                    │
└─────────────────────────────────────────┘
```

### 3. Agent Orchestration Pattern
- **root_agent**: Coordinador central con 7 sub-agentes
- **Orchestrator**: Gestiona selección y enrutamiento de agentes
- **InMemoryRunner**: Ejecuta agentes ADK con gestión de estado

---

## Estructura de Capas

```
integracion/
│
├── WEB/                         # CAPA DE PRESENTACIÓN
│   ├── index.html               # Interfaz principal
│   ├── css/
│   │   └── styles.css           # Estilos responsivos
│   └── js/
│       └── app.js               # Lógica del cliente
│
├── API/                         # CAPA DE APLICACIÓN
│   ├── server.py                # FastAPI server + endpoints
│   ├── config.py                # Configuración centralizada
│   ├── .env                     # Variables de entorno
│   └── orchestrator/            # Orquestación de agentes
│       └── orchestrator.py      # AgentOrchestrator class
│
├── DATAR/                       # CAPA DE DOMINIO
│   ├── __init__.py              # Exports: root_agent, AGENTS_METADATA
│   └── agents/
│       ├── root_agent.py        # Agente coordinador ADK
│       └── sub_agents/          # 7 agentes especializados
│           ├── agent.py         # Gente_Montaña
│           ├── agentHierba/     # PastoBogotano
│           ├── datar_a_gente/   # DiarioIntuitivo
│           ├── GuatilaM/        # SequentialPipelineAgent
│           ├── LinaPuerto/      # agente_bosque (MCP)
│           ├── Sebastian1022/   # agente_sonido
│           └── ZolsemiYa/       # horaculo
│
├── run.py                       # Script de inicio unificado
├── requirements.txt             # Dependencias Python
└── ARQUITECTURA.md              # Este documento
```

## Separación de Responsabilidades

### Pregunta Crítica: ¿Por qué `orchestrator.py` está en `API/` y no en `DATAR/`?

Esta es una decisión arquitectónica fundamental que respeta el principio de **Separation of Concerns**.

#### DATAR/agents/root_agent.py
**Rol**: Capa de Dominio - Agentes e Inteligencia

```python
# ¿QUÉ hacen los agentes?
# Define la LÓGICA de los agentes: coordinación, sub-agentes, instrucciones

root_agent = Agent(
    model=...,
    sub_agents=[...],
    instruction="Reflexiona sobre la EEP de Bogotá"
)
```

**Responsabilidades**:
- Definir comportamiento de agentes (instrucciones, personalidad)
- Configurar modelos LLM
- Establecer jerarquías de agentes (root → sub-agentes)
- Implementar lógica de herramientas (MCP, funciones)
- **Agnóstico al protocolo**: No sabe de HTTP, sesiones web, JSON

**Puede ser usado en**:
- CLI (línea de comandos)
- Desktop app
- Otro framework web (Django, Flask)
- Scripts de testing

#### API/orchestrator/orchestrator.py
**Rol**: Capa de Aplicación - Interfaz Web

```python
# ¿CÓMO se exponen los agentes al usuario web?
# Gestiona sesiones HTTP, routing, runners ADK

class AgentOrchestrator:
    def __init__(self):
        self.runners: Dict[str, InMemoryRunner] = {}  # Runners ADK
        self.sessions: Dict[str, Any] = {}             # Sesiones HTTP
        self.agente_activo = None                      # Estado web

    async def procesar_mensaje(self, mensaje: str, agente_id: str):
        # Lógica de aplicación web
        runner = self.runners[agente_id]
        session = self.sessions[agente_id]
        # Ejecutar agente + formatear respuesta
```

**Responsabilidades**:
- Gestionar **sesiones HTTP** (identificación de usuarios)
- **Enrutamiento** de mensajes al agente correcto
- **Crear runners ADK** (`InMemoryRunner`) para ejecución
- **Formatear respuestas** para API REST (JSON, status codes)
- **Error handling** para contexto web
- Mantener **estado de aplicación** (agente_activo, historial)

**Específico a**:
- Interfaz web FastAPI
- Protocolo HTTP
- Gestión de múltiples usuarios concurrentes

### Diagrama Comparativo

```
┌─────────────────────────────────────────────────────────────────┐
│                      Usuario Web                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓ HTTP POST /api/chat
┌─────────────────────────────────────────────────────────────────┐
│                    API/server.py (FastAPI)                      │
│  • Validación de entrada (Pydantic)                             │
│  • Rate limiting                                                │
│  • CORS headers                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓ orchestrator.procesar_mensaje()
┌─────────────────────────────────────────────────────────────────┐
│              API/orchestrator/orchestrator.py                   │
│                                                                 │
│  RESPONSABILIDADES DE APLICACIÓN WEB:                           │
│  ✓ Gestionar sesiones HTTP (session_id ↔ user)                 │
│  ✓ Seleccionar agente según agente_id                          │
│  ✓ Crear/recuperar InMemoryRunner                              │
│  ✓ Formatear respuesta como JSON                               │
│  ✓ Manejar errores HTTP (404, 500)                             │
│  ✓ Mantener historial de conversación                          │
│                                                                 │
│  HEREDA DE DATAR:                                               │
│  • Importa agentes ya definidos                                │
│  • Usa InMemoryRunner de ADK                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓ runner.run(user_prompt, session_id)
┌─────────────────────────────────────────────────────────────────┐
│                  DATAR/agents/root_agent.py                     │
│                                                                 │
│  RESPONSABILIDADES DE DOMINIO:                                  │
│  ✓ Definir COMPORTAMIENTO de agentes                           │
│  ✓ Configurar modelos LLM (Gemini, OpenRouter)                 │
│  ✓ Establecer jerarquía (root → 7 sub-agentes)                 │
│  ✓ Coordinar delegación entre agentes                          │
│  ✓ Implementar instrucciones (system prompts)                  │
│                                                                 │
│  AGNÓSTICO A:                                                   │
│  • HTTP, REST, JSON                                            │
│  • Sesiones web                                                │
│  • Múltiples usuarios                                          │
│  • Error handling web                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓ LLM API Calls
┌─────────────────────────────────────────────────────────────────┐
│              Gemini / OpenRouter APIs                           │
└─────────────────────────────────────────────────────────────────┘
```

### Ventajas de Esta Separación

#### 1. Reutilización de Código
```python
# Escenario 1: Interfaz CLI
from DATAR import root_agent
response = root_agent.run("¿Qué especies hay en los cerros?")

# Escenario 2: Aplicación de escritorio (PyQt)
from DATAR.agents.sub_agents.agentHierba import root_agent as pasto
response = pasto.run("Describe los pastos")

# Escenario 3: API Web (ACTUAL)
from DATAR import root_agent
from API.orchestrator import get_orchestrator
orchestrator = get_orchestrator()
response = await orchestrator.procesar_mensaje(...)
```

#### 2. Testing Independiente
```python
# Test de agentes (sin servidor web)
def test_gente_montana():
    from DATAR.agents.sub_agents import Gente_Montaña
    response = Gente_Montaña.run("Hola")
    assert "Saludos desde la Montaña" in response

# Test de orchestrator (sin agentes reales - mocks)
def test_orchestrator_routing():
    orchestrator = AgentOrchestrator()
    assert "gente_montana" in orchestrator.agentes
```

#### 3. Mantenibilidad
- Cambiar de FastAPI a Flask → Solo modificas `API/`
- Agregar autenticación → Solo modificas `API/`
- Cambiar modelo LLM → Solo modificas `DATAR/`
- Agregar nuevo agente → Solo modificas `DATAR/`

#### 4. Claridad Conceptual
- Desarrolladores de **frontend/backend** trabajan en `API/`
- Desarrolladores de **IA/agentes** trabajan en `DATAR/`
- Separación de expertise y responsabilidades

---

## Flujo de Datos

### Flujo Completo de una Petición

```
1. Usuario escribe mensaje en WEB/index.html
      ↓
2. JavaScript (WEB/js/app.js) hace POST a /api/chat
   Body: {
     "message": "¿Qué especies hay en los cerros?",
     "agent_id": "gente_montana",
     "session_id": "uuid-1234-5678"
   }
      ↓
3. FastAPI (API/server.py) recibe request
   • Valida entrada con Pydantic
   • Verifica session_id existe
      ↓
4. Llama a orchestrator.procesar_mensaje()
   (API/orchestrator/orchestrator.py)
   • Selecciona runner para "gente_montana"
   • Recupera/crea sesión ADK
      ↓
5. runner.run(user_prompt, session_id)
   • InMemoryRunner ejecuta agente ADK
   • Si es root_agent, puede delegar a sub-agentes
      ↓
6. Agente procesa con LLM
   (DATAR/agents/sub_agents/agent.py)
   • Gente_Montaña genera respuesta
   • Prefija con "Saludos desde la Montaña"
      ↓
7. Runner retorna eventos (async generator)
   • orchestrator extrae texto de event.content.parts
      ↓
8. orchestrator retorna dict:
   {
     "exitoso": true,
     "mensaje": "Saludos desde la Montaña...",
     "agente": "Gente Montaña"
   }
      ↓
9. FastAPI formatea como AgentResponse
   {
     "response": "Saludos desde la Montaña...",
     "agent_name": "Gente Montaña",
     "agent_id": "gente_montana",
     "session_id": "uuid-1234-5678"
   }
      ↓
10. JavaScript recibe JSON y muestra en chat
```

### Flujo de Datos - Diagrama de Secuencia

```
Usuario    WEB/js      API/server      API/orchestrator    DATAR/agents    LLM API
  │           │             │                  │                 │             │
  │─Escribe──→│             │                  │                 │             │
  │           │─POST───────→│                  │                 │             │
  │           │  /api/chat  │                  │                 │             │
  │           │             │─procesar_mensaje→│                 │             │
  │           │             │                  │─get runner────→ │             │
  │           │             │                  │                 │             │
  │           │             │                  │─run(prompt)────→│             │
  │           │             │                  │                 │─LLM call───→│
  │           │             │                  │                 │←──response──│
  │           │             │                  │←─events─────────│             │
  │           │             │←─dict response─  │                 │             │
  │           │←─JSON───────│                  │                 │             │
  │←─Display─ │             │                  │                 │             │
```

---

## Componentes Principales

### 1. WEB/ - Interfaz de Usuario

**Archivos**:
- `index.html`: Estructura HTML5
- `css/styles.css`: Estilos responsivos
- `js/app.js`: Lógica del cliente

**Características**:
- Vanilla JavaScript (sin frameworks)
- Fetch API para comunicación REST
- Tarjetas de agentes con colores/emojis
- Chat interface con historial
- Responsive design (móvil/desktop)

### 2. API/ - Servidor de Aplicación

#### API/server.py

**Responsabilidades**:
- Servidor FastAPI
- Endpoints REST:
  - `GET /`: Redirige a `/static/index.html`
  - `GET /api/agents`: Lista agentes disponibles
  - `POST /api/chat`: Chat general (requiere agent_id)
  - `POST /api/chat/{agent_id}`: Endpoints específicos por agente
  - `GET /api/sessions`: Lista sesiones activas
  - `POST /api/sessions`: Crea nueva sesión
  - `DELETE /api/sessions/{session_id}`: Elimina sesión

**Endpoints Específicos por Agente**:
```python
@app.post("/api/chat/gente_montana", response_model=AgentResponse)
async def chat_gente_montana(request: SimpleMessageRequest):
    respuesta = await orchestrator.procesar_mensaje(
        mensaje=request.message,
        agente_id="gente_montana"
    )
    # ...

# Similar para:
# /api/chat/pasto_bogotano
# /api/chat/diario_intuitivo
# /api/chat/guatila_m
# /api/chat/agente_bosque
# /api/chat/agente_sonido
# /api/chat/horaculo
```

#### API/config.py

**Responsabilidades**:
- Cargar variables de entorno desde `.env`
- Validar configuración requerida
- Proporcionar constantes para toda la aplicación

**Variables Clave**:
```python
API_HOST = "localhost"
API_PORT = 8000
ALLOWED_ORIGINS = ["http://localhost:8000"]
MAX_MESSAGE_LENGTH = 2000
MAX_RESPONSE_LENGTH = 10000
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

#### API/orchestrator/orchestrator.py

**Clase Principal**: `AgentOrchestrator`

**Atributos**:
```python
self.agentes: Dict[str, Dict]           # Metadata + instancias de agentes
self.runners: Dict[str, InMemoryRunner] # Runners ADK por agente
self.sessions: Dict[str, Any]           # Sesiones ADK por agente
self.agente_activo: Optional[str]       # ID del agente seleccionado
self.historial_conversacion: List       # Historial global
```

**Métodos Clave**:
```python
def obtener_lista_agentes() -> List[Dict]:
    """Retorna metadata de agentes para frontend"""

async def seleccionar_agente(agente_id: str) -> Dict:
    """Selecciona agente activo"""

async def procesar_mensaje(mensaje: str, agente_id: str) -> Dict:
    """Procesa mensaje con agente específico"""
    # 1. Validar agente existe
    # 2. Obtener/crear runner
    # 3. Obtener/crear sesión ADK
    # 4. Ejecutar runner.run()
    # 5. Extraer respuesta de eventos
    # 6. Retornar dict con resultado
```

### 3. DATAR/ - Capa de Agentes

#### DATAR/__init__.py

```python
from .agents.root_agent import root_agent, AGENTS_METADATA

__all__ = ['root_agent', 'AGENTS_METADATA']
```

**Propósito**: Exponer agente raíz y metadata como API pública del módulo.

#### DATAR/agents/root_agent.py

**Agente Coordinador**:
```python
root_agent = Agent(
    model=...,  # LiteLlm o gemini-2.5-flash
    name='root_agent',
    description='Agente raíz DATAR',
    instruction='Reflexiona y responde sobre EEP Bogotá',
    sub_agents=[
        Gente_Montaña,
        PastoBogotano,
        DiarioIntuitivo,
        SequentialPipelineAgent,
        agente_bosque,
        agente_sonido,
        horaculo
    ],
)
```

**Metadata**:
```python
AGENTS_METADATA = {
    'gente_montana': {
        'nombre': 'Gente Montaña',
        'descripcion': 'Saluda desde la montaña',
        'color': '#8B4513',
        'emoji': '🏔️'
    },
    # ... 6 agentes más
}
```

#### DATAR/agents/sub_agents/

Cada sub-agente implementa patrones específicos:

| Agente | Patrón ADK | Características |
|--------|------------|-----------------|
| Gente_Montaña | `Agent` | Agente simple con instrucción personalizada |
| PastoBogotano | `Agent` | Genera audio con pydub |
| DiarioIntuitivo | `Agent` | Visualizaciones con NumPy/Pillow |
| GuatilaM | `SequentialAgent` + `ParallelAgent` | Pipeline: paralelo → merger |
| agente_bosque | `Agent` + `MCPToolset` | Herramientas MCP para consultas ecológicas |
| agente_sonido | `Agent` | Representaciones biocéntricas (Turtle/ASCII/Audio) |
| horaculo | `Agent` | Oráculo ambiental con alta temperatura |

---

## Patrones de Diseño Implementados

### 1. Layered Architecture (Capas)
- Presentación (WEB) → Aplicación (API) → Dominio (DATAR)

### 2. Dependency Injection
```python
# API/server.py
orchestrator = get_orchestrator()  # Factory function

# API/orchestrator/orchestrator.py
def get_orchestrator() -> AgentOrchestrator:
    if not hasattr(get_orchestrator, 'instance'):
        get_orchestrator.instance = AgentOrchestrator()
    return get_orchestrator.instance
```

### 3. Singleton Pattern
- `orchestrator` instancia única compartida

### 4. Strategy Pattern
- Diferentes agentes implementan misma interfaz ADK
- Orchestrator selecciona estrategia (agente) en runtime

### 5. Observer Pattern (implícito)
- `runner.run()` retorna async generator
- Consumidor observa eventos del agente

### 6. Facade Pattern
- `AgentOrchestrator` simplifica interacción con múltiples agentes
- API unificada para servidor

### 7. Factory Pattern
- `InMemoryRunner(agent=...)` crea runners
- `session_service.create_session()` crea sesiones

---

## Gestión de Sesiones

### Dos Niveles de Sesiones

#### Nivel 1: Sesiones HTTP (API/server.py)
```python
sessions_store: Dict[str, Dict[str, Any]] = {}

def create_session():
    session_id = str(uuid.uuid4())
    sessions_store[session_id] = {
        "created_at": datetime.now(),
        "last_activity": datetime.now()
    }
    return session_id
```

**Propósito**: Identificar usuarios web, tracking temporal.

#### Nivel 2: Sesiones ADK (API/orchestrator/orchestrator.py)
```python
self.sessions: Dict[str, Any] = {}  # Por agente

async def procesar_mensaje(self, mensaje: str, agente_id: str):
    if agente_id not in self.sessions:
        self.sessions[agente_id] = runner.session_service.create_session()

    session = self.sessions[agente_id]
    async for event in runner.run(user_prompt=mensaje, session_id=session):
        # ...
```

**Propósito**: Mantener historial de conversación ADK, memoria del agente.

### Persistencia

**Estado Actual**: Sesiones en memoria (perdidas al reiniciar).

**Para Producción**:
- Redis para sesiones HTTP
- PostgreSQL para historial ADK
- Implementar `SessionService` personalizado

---

## Configuración de Modelos

### Modo Flexible (Adaptativo)

#### Configuración Completa (OpenRouter + Google)
```env
OPENROUTER_API_KEY=sk-or-v1-xxx
GOOGLE_API_KEY=AIzaSy...
```

**Resultado**:
- `root_agent`: OpenRouter MiniMax (gratis, 128K context)
- Sub-agentes: Gemini 2.5 Flash

#### Configuración Simplificada (Solo Google)
```env
OPENROUTER_API_KEY=
GOOGLE_API_KEY=AIzaSy...
```

**Resultado**:
- Todos los agentes: Gemini 2.5 Flash

### Detección Automática

**Archivo**: `DATAR/agents/root_agent.py:72-119`

```python
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

if OPENROUTER_KEY:
    print("✅ Usando OpenRouter MiniMax para root_agent")
    root_agent = Agent(
        model=LiteLlm(
            model="openrouter/minimax/minimax-m2:free",
            api_key=OPENROUTER_KEY,
            api_base="https://openrouter.ai/api/v1"
        ),
        # ...
    )
elif GOOGLE_KEY:
    print("⚠️ Solo GOOGLE_API_KEY disponible, usando Gemini 2.5 Flash")
    root_agent = Agent(
        model='gemini-2.5-flash',
        # ...
    )
else:
    print("❌ No hay claves API configuradas")
    root_agent = None
```
