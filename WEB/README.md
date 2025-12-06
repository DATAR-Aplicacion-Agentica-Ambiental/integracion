# DATAR Frontend Web

Frontend web para el sistema DATAR - Chat con agentes ambientales.

## Estructura de Archivos

```
WEB/
├── index.html              # Página principal
├── css/
│   └── styles.css          # Estilos (mobile-first)
├── js/
│   ├── api.js              # Cliente API para Cloud Run
│   └── app.js              # Lógica de la aplicación
├── dev/
│   └── proxy.py            # Proxy CORS para desarrollo local
├── imagen_fondo.jpg        # Imagen de fondo
├── INFORME_PRUEBAS_API.md  # Informe de pruebas
└── README.md               # Este archivo
```

## Desarrollo Local

### Con Proxy (recomendado)

```bash
cd WEB
python3 dev/proxy.py
# Abre http://localhost:8080
```

El proxy redirige `/api/*` a Cloud Run con headers CORS.

### Generar Token para Pruebas

```bash
# Autenticarse con tu cuenta de Google
gcloud auth login

# Generar token de identidad (dura 1 hora)
TOKEN=$(gcloud auth print-identity-token)
echo $TOKEN
```

Luego en el frontend:
1. Clic en ⚙ (esquina superior derecha)
2. Pegar el token
3. Clic "Guardar Token"

## Configuración (js/api.js)

```javascript
const CONFIG = {
    useMock: false,    // true = datos de prueba, false = API real
    devMode: true,     // true = muestra panel de token, false = oculto
    useProxy: true     // true = usa proxy local, false = conexión directa
};
```

### Para Producción
```javascript
useMock: false,
devMode: false,
useProxy: false
```

## Despliegue en Cloud Run

### Prerrequisito: CORS en el Backend

El backend debe habilitar CORS. Agregar en el servidor FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O dominios específicos
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Despliegue

1. Crear `Dockerfile` en la raíz del proyecto:
```dockerfile
FROM nginx:alpine
COPY WEB/ /usr/share/nginx/html/
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

2. Construir y desplegar:
```bash
gcloud builds submit --tag gcr.io/datar-476419/datar-frontend
gcloud run deploy datar-frontend \
  --image gcr.io/datar-476419/datar-frontend \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated
```

## Funcionalidades

| Funcionalidad | Estado | Descripción |
|--------------|--------|-------------|
| Chat de texto | ✅ | Envío y recepción de mensajes |
| Markdown | ✅ | Renderizado de respuestas formateadas |
| Audio inline | ✅ | Reproducción de audio generado por agentes |
| Imágenes inline | ✅ | Visualización de imágenes (cuando backend las retorne) |
| Text-to-Speech | ✅ | Lectura de respuestas con play/pausa |
| Speech-to-Text | ✅ | Entrada por voz (Web Speech API) |
| Responsive | ✅ | Diseño mobile-first |

## Limitaciones Conocidas (Backend)

1. **Modelo no multimodal**: El modelo `minimax/minimax-m2` no procesa imágenes
2. **Imágenes no retornadas**: Algunos agentes no devuelven URLs de imágenes generadas
3. **CORS**: Debe habilitarse en el backend para producción

Ver `INFORME_PRUEBAS_API.md` para detalles completos.


