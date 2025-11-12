# Cambios en Arquitectura DATAR - Orquestación Automática

**Fecha**: 2025-11-12
**Objetivo**: Implementar arquitectura correcta de ADK con orquestación automática por root_agent

---

## 🎯 Problema Original

La implementación anterior no seguía el patrón correcto de Google ADK:

❌ **Antes:**
- Endpoints específicos por agente (`/api/chat/gente_montana`, etc.)
- Selección manual de agente desde el frontend
- "Saltar" el root_agent para comunicación directa
- Sin soporte para multimedia (imágenes, sonidos, mapas)

---

## ✅ Solución Implementada

**Arquitectura correcta de ADK:**
- Un único endpoint `/api/chat` para todas las comunicaciones
- El `root_agent` orquesta automáticamente todos los sub-agentes
- Selección inteligente de agente basada en contenido del mensaje
- Soporte completo para archivos multimedia generados

---

## 📝 Cambios Realizados

### 1. Backend (API/server.py)

#### 1.1 Modelos Pydantic Actualizados

**Nuevo modelo `MediaFile`:**
```python
class MediaFile(BaseModel):
    type: str  # "image", "audio", "map", "text"
    url: str   # URL relativa ej: /static/outputs/file.png
    filename: str
    description: Optional[str]
```

**Modelo `ChatResponse` extendido:**
```python
class ChatResponse(BaseModel):
    response: str
    agent_name: str
    session_id: str
    timestamp: str
    files: Optional[List[MediaFile]] = []  # ← NUEVO
```

#### 1.2 Detección Automática de Archivos Multimedia

**Nueva función `detect_and_process_files()`:**
- Busca rutas de archivos en la respuesta del agente
- Detecta patrones como: `Imagen guardada en: /path/to/file.png`
- Copia archivos a `WEB/outputs/` con timestamp único
- Retorna metadata estructurada para el frontend
- Soporta: `.png`, `.jpg`, `.wav`, `.mp3`, `.html`, `.pdf`

**Ubicación de archivos generados:**
```
DATAR/datar/sub_agents/
├── Gente_Intuitiva/imagenes_generadas/  → Imágenes emocionales
├── Gente_Sonora/output/                  → Audio y gráficos
└── [otros agentes]/output/               → Varios formatos
```

#### 1.3 Función `send_message_to_agent` Actualizada

**Antes:**
```python
async def send_message_to_agent(...) -> str:
    # Solo retornaba texto
    return respuesta_texto
```

**Ahora:**
```python
async def send_message_to_agent(...) -> Tuple[str, List[Dict]]:
    # Detecta y procesa archivos automáticamente
    respuesta_limpia, archivos = detect_and_process_files(respuesta_texto)
    return respuesta_limpia, archivos
```

#### 1.4 Endpoints Específicos ELIMINADOS

**Eliminados:**
- `POST /api/chat/gente_montana`
- `POST /api/chat/gente_pasto`
- `POST /api/chat/gente_intuitiva`
- `POST /api/chat/gente_interpretativa`
- `POST /api/chat/gente_bosque`
- `POST /api/chat/gente_sonora`
- `POST /api/chat/gente_horaculo`

**Razón:** Contradice el diseño de orquestación automática de ADK. El root_agent debe decidir qué sub-agente usar.

**Reemplazo:** Un único endpoint `/api/chat` para todo.

---

### 2. Frontend (WEB/js/app.js)

#### 2.1 Arquitectura de Comunicación Simplificada

**Antes:**
```javascript
// Requería selección manual de agente
body: JSON.stringify({
    message: message,
    session_id: sessionId,
    agent_id: selectedAgent.id  // ← Manual
})
```

**Ahora:**
```javascript
// Sin agent_id - orquestación automática
body: JSON.stringify({
    message: message,
    session_id: sessionId
    // El root_agent decide automáticamente
})
```

#### 2.2 Función `addMessageToChat` con Multimedia

**Soporta 4 tipos de contenido:**

1. **Imágenes** (`.png`, `.jpg`, `.svg`):
   ```html
   <img src="/static/outputs/file.png"
        style="max-width: 100%; border-radius: 8px;">
   ```

2. **Audio** (`.wav`, `.mp3`):
   ```html
   <audio controls>
       <source src="/static/outputs/audio.wav">
   </audio>
   ```

3. **Mapas** (`.html`):
   ```html
   <a href="/static/outputs/map.html" target="_blank">
       Abrir mapa
   </a>
   ```

4. **Archivos** (otros):
   ```html
   <a href="/static/outputs/file.pdf" download>
       📄 Descargar archivo
   </a>
   ```

#### 2.3 Experiencia de Usuario Mejorada

**Inicialización Automática:**
- Sesión creada automáticamente al cargar la página
- Mensaje de bienvenida con lista de agentes disponibles
- No requiere selección manual para empezar a chatear

**Selección de Agente (Opcional):**
- Hacer clic en tarjeta de agente → Muestra información
- No bloquea el uso - es solo educativo
- El sistema selecciona automáticamente al agente apropiado

---

### 3. Configuración (.env)

**API Key de OpenRouter Actualizada:**
```env
OPENROUTER_API_KEY=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
```

**Detección automática de modelos (root_agent.py:26-74):**
- Si `OPENROUTER_API_KEY` está presente → root_agent usa MiniMax (gratis)
- Si solo `GOOGLE_API_KEY` → root_agent usa Gemini 2.5 Flash
- Sub-agentes siempre usan Gemini 2.5 Flash

---

### 4. Estructura de Archivos

**Nuevo directorio creado:**
```
WEB/
└── outputs/          ← Archivos multimedia servidos públicamente
    └── .gitkeep      ← Mantiene directorio en Git
```

**Actualización de .gitignore:**
```gitignore
# WEB Outputs (archivos multimedia generados por agentes)
WEB/outputs/*
!WEB/outputs/.gitkeep
```

---

## 🔄 Flujo de Comunicación Actualizado

### Flujo Anterior (Incorrecto)
```
Usuario → Frontend → /api/chat/gente_montana → Gente Montaña directamente
                                             ↓
                                        Solo texto
```

### Flujo Actual (Correcto)
```
Usuario → Frontend → /api/chat → root_agent
                                     ↓
                    [Decisión automática basada en contenido]
                                     ↓
              ┌──────────────────────┼──────────────────────┐
              ↓                      ↓                      ↓
        Gente Montaña          Pasto Bogotano         Agente Sonido
              ↓                      ↓                      ↓
         Genera respuesta      Genera respuesta      Genera audio + texto
              ↓                      ↓                      ↓
         [detect_and_process_files() detecta archivos]
              ↓                      ↓                      ↓
         Copia a WEB/outputs/  Copia a WEB/outputs/  Copia a WEB/outputs/
              ↓                      ↓                      ↓
              └──────────────────────┴──────────────────────┘
                                     ↓
                    ChatResponse { response, files: [...] }
                                     ↓
                              Frontend renderiza
                         (Texto + Imágenes + Audio)
```

---

## 🧪 Casos de Uso

### Ejemplo 1: Consulta sobre Cerros Orientales

**Usuario pregunta:**
```
"Cuéntame sobre los Cerros Orientales"
```

**Flujo interno:**
1. root_agent analiza → Determina que es consulta geográfica/montaña
2. Delega a `Gente_Montaña` automáticamente
3. Gente_Montaña responde con texto
4. Frontend muestra: "**Gente_Montaña:** Los Cerros Orientales..."

### Ejemplo 2: Visualización Emocional

**Usuario pregunta:**
```
"Visualiza mi emoción: alegría en el parque"
```

**Flujo interno:**
1. root_agent analiza → Detecta solicitud de visualización
2. Delega a `DiarioIntuitivo` (Gente_Intuitiva)
3. DiarioIntuitivo genera imagen → Guarda en `imagenes_generadas/trazo_YYYYMMDD_HHMMSS.png`
4. Respuesta texto: "✨ He creado tu visualización... Imagen guardada en: /app/DATAR/.../trazo_20251112_130823.png"
5. `detect_and_process_files()` detecta la ruta
6. Copia imagen a `WEB/outputs/20251112_130823_trazo_20251112_130823.png`
7. Frontend renderiza imagen inline en el chat

### Ejemplo 3: Representación Sonora

**Usuario pregunta:**
```
"Crea un sonido de un río tranquilo"
```

**Flujo interno:**
1. root_agent → Detecta solicitud de audio
2. Delega a `agente_sonido` (Gente_Sonora)
3. Genera archivo `.wav` + gráfico `.png`
4. Sistema detecta ambos archivos
5. Copia a `WEB/outputs/`
6. Frontend renderiza:
   - Texto descriptivo
   - Reproductor de audio inline
   - Imagen del gráfico

---

## ⚠️ Consideraciones Importantes

### 1. Rendimiento

**Detección de archivos:**
- Usa expresiones regulares eficientes
- Solo procesa archivos que realmente existen
- Copia con `shutil.copy2` (rápida, preserva metadata)

**Almacenamiento:**
- Los archivos en `WEB/outputs/` se acumulan
- Considerar limpieza periódica (tarea programada)
- Alternativa: Implementar TTL (time-to-live) por archivo

### 2. Seguridad

**Validación de rutas:**
- Solo procesa archivos dentro de `DATAR/`
- Previene path traversal con validación de extensiones
- No ejecuta código - solo copia archivos estáticos

**Exposición pública:**
- Archivos en `WEB/outputs/` son públicamente accesibles
- No incluir información sensible en nombres de archivo
- Considerar autenticación para producción

### 3. Escalabilidad

**Para producción en Cloud Run:**
- Los archivos en `WEB/outputs/` son efímeros (contenedor stateless)
- Considerar Cloud Storage para persistencia
- Implementar CDN para servir multimedia (Cloud CDN)

**Alternativas:**
1. **Cloud Storage + Signed URLs:**
   ```python
   from google.cloud import storage
   # Generar URL temporal firmada
   url = blob.generate_signed_url(expiration=3600)
   ```

2. **Redis para cache de URLs:**
   ```python
   redis.setex(f"file:{filename}", 3600, url)
   ```

---

## 📚 Referencias Técnicas

### Patrones de Google ADK Implementados

1. **Root Agent Pattern:**
   - Agente principal coordina sub-agentes
   - Toma decisiones de routing basadas en contexto
   - Mantiene coherencia de conversación

2. **Sequential Pipeline:**
   - Usado en `GuatilaM` (Gente_Interpretativa)
   - Pipeline paralelo + secuencial para análisis complejo

3. **MCP Integration:**
   - `agente_bosque` usa Model Context Protocol
   - Herramientas externas para búsqueda web, PDFs

### Endpoints Documentados

**Swagger UI disponible en:** `http://localhost:8000/docs`

**Endpoints activos:**
- `GET /` - Info del sistema
- `GET /health` - Estado del servicio
- `GET /api/agents` - Lista de agentes (metadata)
- `POST /api/chat` - **Único endpoint de comunicación**
- `GET /api/sessions` - Sesiones activas
- `GET /api/sessions/{id}` - Historial de sesión
- `DELETE /api/sessions/{id}` - Eliminar sesión

---

## 🚀 Próximos Pasos Sugeridos

### Corto Plazo (Opcional)
1. **Pruebas de integración:** Verificar cada agente genera archivos correctamente
2. **Manejo de errores:** Mejorar mensajes cuando archivos no se encuentran
3. **Loading states:** Indicador visual mientras se generan archivos grandes

### Mediano Plazo (Producción)
1. **Cloud Storage:** Migrar archivos a Google Cloud Storage
2. **Limpieza automática:** Cron job para eliminar archivos antiguos
3. **Compresión:** Optimizar imágenes antes de servir
4. **Thumbnails:** Generar previsualizaciones para imágenes grandes

### Largo Plazo (Mejoras)
1. **Streaming:** Respuestas en tiempo real (Server-Sent Events)
2. **Galería:** Vista de todos los archivos generados en sesión
3. **Descarga batch:** ZIP de todos los archivos de una conversación
4. **Análisis:** Métricas sobre tipos de archivos más generados

---

## ✅ Checklist de Verificación

- [x] OpenRouter API Key configurada en `.env`
- [x] Endpoints específicos eliminados
- [x] Modelos Pydantic actualizados con `MediaFile`
- [x] Función `detect_and_process_files()` implementada
- [x] Frontend renderiza imágenes, audio, mapas
- [x] Directorio `WEB/outputs/` creado con `.gitkeep`
- [x] `.gitignore` actualizado para excluir outputs
- [x] Documentación de arquitectura completa

---

## 📞 Soporte

Si encuentras problemas con la nueva arquitectura:

1. **Verificar logs del servidor:** Buscar mensajes `📁 Archivo copiado:` o `⚠️ Error procesando archivo`
2. **Revisar consola del navegador:** Verificar que `data.files` existe en respuesta
3. **Validar que archivos existen:** Comprobar que agentes generan archivos en sus directorios

**Logs útiles:**
```bash
# Ver inicialización
python run.py | grep "✅"

# Monitorear archivos copiados
tail -f logs/server.log | grep "📁"
```

---

## 🎓 Conclusión

La nueva arquitectura sigue correctamente el patrón de Google ADK:

✅ **Orquestación centralizada** por root_agent
✅ **Decisiones inteligentes** basadas en contenido
✅ **Multimedia nativo** en respuestas
✅ **Experiencia unificada** para el usuario
✅ **Escalable y mantenible** para producción

El sistema ahora permite que cada agente genere contenido rico (imágenes, sonidos, mapas) y el frontend lo muestre automáticamente sin configuración manual.

---

**Documento creado:** 2025-11-12
**Última actualización:** 2025-11-12
**Autor:** Claude Code (Anthropic)
