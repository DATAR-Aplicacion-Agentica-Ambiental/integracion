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

### Opción 1: Con Proxy (recomendado para desarrollo)

```bash
cd WEB/dev
python3 proxy.py
# Abre http://localhost:8080
```

El proxy redirige `/api/*` a Cloud Run con headers CORS.

### Opción 2: Servidor Simple (solo modo mock)

```bash
cd WEB
python3 -m http.server 8080
# Edita js/api.js: useMock: true
```

## Configuración (js/api.js)

```javascript
const CONFIG = {
    useMock: false,    // true = datos de prueba, false = API real
    devMode: true,     // true = muestra panel de token, false = oculto
    useProxy: true     // true = usa /api (local), false = conexión directa
};
```

### Para Producción
```javascript
useMock: false,
devMode: false,
useProxy: false
```

## Despliegue a Producción

### Prerrequisito: CORS en el Backend

Antes de desplegar, el backend debe habilitar CORS. Agregar en el servidor FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O dominios específicos
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Opción A: Firebase Hosting (Recomendado)

1. Instalar Firebase CLI:
```bash
npm install -g firebase-tools
firebase login
```

2. Inicializar proyecto:
```bash
firebase init hosting
# Seleccionar directorio: WEB
# SPA: No
```

3. Configurar `firebase.json` para proxy (opcional):
```json
{
  "hosting": {
    "public": "WEB",
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "datar-integraciones",
          "region": "southamerica-east1"
        }
      }
    ]
  }
}
```

4. Desplegar:
```bash
firebase deploy --only hosting
```

### Opción B: Cloud Storage + CDN

1. Crear bucket:
```bash
gsutil mb -l southamerica-east1 gs://datar-frontend
```

2. Configurar como sitio web:
```bash
gsutil web set -m index.html gs://datar-frontend
```

3. Subir archivos:
```bash
gsutil -m cp -r WEB/* gs://datar-frontend/
```

4. Hacer público:
```bash
gsutil iam ch allUsers:objectViewer gs://datar-frontend
```

### Opción C: Cloud Run (Contenedor)

1. Crear `Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY WEB/ /usr/share/nginx/html/
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

2. Construir y desplegar:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/datar-frontend
gcloud run deploy datar-frontend --image gcr.io/PROJECT_ID/datar-frontend --platform managed
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
| Lightbox | ✅ | Ampliación de imágenes |
| File Preview | ✅ | Vista previa antes de enviar |

## Limitaciones Conocidas (Backend)

1. **Modelo no multimodal**: El modelo `minimax/minimax-m2` no procesa imágenes
2. **Imágenes no retornadas**: Algunos agentes no devuelven URLs de imágenes generadas
3. **CORS**: Debe habilitarse en el backend para producción

Ver `INFORME_PRUEBAS_API.md` para detalles completos.

## Compatibilidad de Navegadores

- Chrome 80+ ✅
- Firefox 75+ ✅
- Safari 13+ ✅
- Edge 80+ ✅

Speech-to-Text requiere Chrome, Edge o Safari.
