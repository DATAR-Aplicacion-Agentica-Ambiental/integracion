# Flujo de Trabajo: Desarrollo Local → Producción

Esta guía explica cómo trabajar con DATAR localmente y actualizar el servidor de producción en Google Cloud Run.

---

## 📋 Resumen Rápido

```
1. Hacer cambios localmente
2. Probar localmente
3. Hacer commit (opcional pero recomendado)
4. Deploy a producción (1 comando)
5. Verificar que funcione
```

---

## 🛠️ PARTE 1: Trabajar Localmente

### 1. Activar el Entorno Virtual

Cada vez que abras una nueva terminal:

```bash
# En el directorio del proyecto
cd "/mnt/c/Users/chris/OneDrive/Documents/DATAR FIN INTEGRADO/integracion"

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac/WSL
# O en Windows CMD: venv\Scripts\activate
```

Verás `(venv)` al inicio de tu terminal cuando esté activado.

---

### 2. Hacer Tus Cambios

Edita los archivos que necesites:

```bash
# Ejemplos de cambios comunes:

# Modificar un agente
nano DATAR/agents/sub_agents/gente_montana/agent.py

# Cambiar el frontend
nano WEB/js/app.js
nano WEB/css/styles.css
nano WEB/static/index.html

# Ajustar configuración
nano API/config.py

# Agregar dependencias
nano requirements.txt
```

---

### 3. Probar Localmente

**Iniciar el servidor local:**

```bash
# Opción 1: Script rápido
python run.py

# Opción 2: Modo desarrollo con auto-reload
python run.py --dev

# Opción 3: Puerto personalizado
python run.py --port 9000
```

**Probar en el navegador:**
- Frontend: http://localhost:8000/static/index.html
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Detener el servidor:**
- Presiona `Ctrl + C` en la terminal

---

### 4. Verificar que Todo Funciona

**Checklist básico:**
- [ ] El servidor inicia sin errores
- [ ] Los agentes cargan correctamente
- [ ] Puedes enviar mensajes y recibir respuestas
- [ ] No hay errores en la consola del navegador (F12)

---

## 🚀 PARTE 2: Actualizar Producción

### Método 1: Deploy Rápido (Recomendado)

Usa el script automatizado:

```bash
# Desde el directorio del proyecto
./deploy.sh
```

El script te pedirá:
1. Confirmar tu GOOGLE_API_KEY
2. (Opcional) OPENROUTER_API_KEY
3. Confirmación para continuar

**Tiempo:** 3-8 minutos (dependiendo de los cambios)

---

### Método 2: Deploy Manual

Si prefieres control total:

```bash
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="TU_API_KEY_AQUI" \
  --set-env-vars API_ENV=production \
  --memory 1Gi \
  --timeout 300
```

**Reemplaza `TU_API_KEY_AQUI`** con tu API key real.

---

### Método 3: Deploy Solo con Código Actualizado

Si NO cambiaste las variables de entorno:

```bash
gcloud run deploy datar \
  --source . \
  --region us-central1
```

Este comando es **más rápido** porque reutiliza la configuración anterior.

---

## ⚡ PARTE 3: Casos Comunes

### Caso 1: Cambié el Frontend (HTML/CSS/JS)

```bash
# 1. Probar localmente
python run.py --dev

# 2. Verificar en http://localhost:8000/static/index.html

# 3. Deploy a producción
gcloud run deploy datar --source . --region us-central1

# 4. Verificar en producción
# Abre: https://datar-456258944189.us-central1.run.app/static/index.html
# Presiona Ctrl+Shift+R para forzar recarga sin cache
```

**Tiempo de deploy:** 2-3 minutos

---

### Caso 2: Cambié el Código de un Agente

```bash
# 1. Probar localmente
python run.py

# 2. Probar el agente específico en el frontend

# 3. Deploy a producción
gcloud run deploy datar --source . --region us-central1

# 4. Verificar en producción
# Prueba el agente modificado
```

**Tiempo de deploy:** 3-5 minutos

---

### Caso 3: Agregué una Nueva Dependencia

**Ejemplo:** Agregaste `pandas` a `requirements.txt`

```bash
# 1. Instalar localmente
pip install pandas

# 2. Agregar a requirements.txt
echo "pandas>=2.0.0" >> requirements.txt

# 3. Probar localmente
python run.py

# 4. Deploy a producción (tomará más tiempo)
gcloud run deploy datar --source . --region us-central1
```

**Tiempo de deploy:** 5-8 minutos (debe instalar la nueva dependencia)

---

### Caso 4: Cambié Variables de Entorno

**Ejemplo:** Cambiaste la API key de Google

```bash
# Deploy con nueva variable
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="NUEVA_API_KEY_AQUI"
```

**También puedes cambiar variables sin re-deploy:**

```bash
# Solo actualizar variables (muy rápido, ~10 segundos)
gcloud run services update datar \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="NUEVA_API_KEY"
```

---

### Caso 5: Agregué un Nuevo Agente

```bash
# 1. Crear el nuevo agente localmente
mkdir -p DATAR/agents/sub_agents/nuevo_agente
# ... crear agent.py, etc.

# 2. Registrarlo en root_agent.py y orchestrator.py

# 3. Agregar endpoint en API/server.py

# 4. Probar localmente
python run.py

# 5. Deploy a producción
gcloud run deploy datar --source . --region us-central1
```

**Tiempo de deploy:** 3-5 minutos

---

## 🔍 PARTE 4: Verificación Post-Deploy

### Ver el Estado del Deploy

```bash
# Ver información del servicio
gcloud run services describe datar --region us-central1

# Ver URL del servicio
gcloud run services describe datar --region us-central1 --format="value(status.url)"
```

---

### Ver Logs en Tiempo Real

```bash
# Ver logs mientras desarrollas
gcloud run services logs tail datar --region us-central1

# Ver últimos 50 logs
gcloud run services logs read datar --region us-central1 --limit 50

# Filtrar por errores
gcloud run services logs read datar --region us-central1 --limit 50 | grep ERROR
```

---

### Probar los Endpoints

```bash
# Health check
curl https://datar-456258944189.us-central1.run.app/health

# Lista de agentes
curl https://datar-456258944189.us-central1.run.app/api/agents

# Enviar mensaje de prueba
curl -X POST https://datar-456258944189.us-central1.run.app/api/chat/gente_montana \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola"}'
```

---

## 🎯 PARTE 5: Buenas Prácticas

### 1. Usa Git para Control de Versiones

```bash
# Antes de hacer cambios importantes
git checkout -b feature/mi-nuevo-cambio

# Hacer tus cambios...

# Commit de los cambios
git add .
git commit -m "Descripción clara del cambio"

# Hacer deploy
gcloud run deploy datar --source . --region us-central1

# Si funciona, merge a main
git checkout main
git merge feature/mi-nuevo-cambio
git push
```

---

### 2. Prueba SIEMPRE Localmente Primero

**Regla de oro:** Nunca hagas deploy sin probar localmente.

```bash
# ❌ MAL: Deploy directo sin probar
gcloud run deploy datar --source . --region us-central1

# ✅ BIEN: Probar primero
python run.py --dev
# ... probar todo ...
# ... verificar que funciona ...
gcloud run deploy datar --source . --region us-central1
```

---

### 3. Mantén un Log de Cambios

Crea un archivo `CHANGELOG.md`:

```markdown
## 2025-11-12
- Corregido API_BASE_URL para producción
- Agregado matplotlib a dependencias
- Deploy inicial exitoso

## 2025-11-13
- Mejorado agente Gente Montaña
- Actualizado frontend con nuevos colores
```

---

### 4. Revisa los Logs Después del Deploy

```bash
# Inmediatamente después del deploy
gcloud run services logs tail datar --region us-central1

# Busca:
# ✅ "✅ root_agent inicializado"
# ✅ "✅ Configuración validada correctamente"
# ❌ Errores o warnings inusual
```

---

## 📊 PARTE 6: Comandos Útiles de Referencia

### Gestión del Servicio

```bash
# Ver servicios desplegados
gcloud run services list --region us-central1

# Detalle del servicio
gcloud run services describe datar --region us-central1

# Ver revisiones (versiones)
gcloud run revisions list --service datar --region us-central1

# Rollback a versión anterior
gcloud run services update-traffic datar \
  --region us-central1 \
  --to-revisions datar-00002-abc=100
```

---

### Gestión de Recursos

```bash
# Aumentar memoria (si necesitas más)
gcloud run services update datar \
  --region us-central1 \
  --memory 2Gi

# Aumentar timeout
gcloud run services update datar \
  --region us-central1 \
  --timeout 600

# Cambiar número máximo de instancias
gcloud run services update datar \
  --region us-central1 \
  --max-instances 10
```

---

### Depuración

```bash
# Ver variables de entorno configuradas
gcloud run services describe datar \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"

# Ver todas las configuraciones
gcloud run services describe datar \
  --region us-central1 \
  --format yaml
```

---

## 🚨 PARTE 7: Solución de Problemas

### Problema: Deploy Falla

**Ver el error:**
```bash
# Los logs de build están en la URL que aparece en el error
# O ejecuta:
gcloud builds list --limit 5
gcloud builds log [BUILD_ID]
```

**Causas comunes:**
- Dependencia faltante en `requirements.txt`
- Error de sintaxis en Python
- Dockerfile mal configurado

---

### Problema: Aplicación no Responde Después del Deploy

```bash
# Ver logs en tiempo real
gcloud run services logs tail datar --region us-central1

# Busca:
# - ModuleNotFoundError (falta dependencia)
# - ImportError (error de importación)
# - Errores de API key
```

---

### Problema: Cambios no se Reflejan

**Solución:**

```bash
# Opción 1: Deploy forzando rebuild
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --no-cache

# Opción 2: Limpiar cache del navegador
# En el navegador: Ctrl+Shift+R (Windows/Linux) o Cmd+Shift+R (Mac)
```

---

### Problema: Error 403 Forbidden

```bash
# Verificar permisos
gcloud run services get-iam-policy datar --region us-central1

# Si no está "allUsers", agregar:
gcloud run services add-iam-policy-binding datar \
  --region us-central1 \
  --member=allUsers \
  --role=roles/run.invoker
```

---

## 📝 PARTE 8: Workflow Completo Resumido

```bash
# ========== DESARROLLO LOCAL ==========
cd "/mnt/c/Users/chris/OneDrive/Documents/DATAR FIN INTEGRADO/integracion"
source venv/bin/activate

# Hacer cambios en el código
nano API/server.py  # o el archivo que necesites

# Probar localmente
python run.py --dev

# Probar en navegador: http://localhost:8000/static/index.html

# ========== COMMIT (OPCIONAL) ==========
git add .
git commit -m "Descripción del cambio"

# ========== DEPLOY A PRODUCCIÓN ==========
gcloud run deploy datar --source . --region us-central1

# ========== VERIFICACIÓN ==========
# Abrir: https://datar-456258944189.us-central1.run.app/static/index.html
# Ver logs:
gcloud run services logs tail datar --region us-central1

# ========== LISTO ==========
```

---

## 🎓 Consejos Finales

1. **Desarrolla en ramas de Git** - Usa `git checkout -b feature/nombre`
2. **Commits frecuentes** - Cada cambio significativo
3. **Prueba localmente siempre** - Nunca deploy sin probar
4. **Revisa los logs** - Después de cada deploy
5. **Documenta cambios** - En CHANGELOG.md o commits
6. **Backup de .env** - Guarda tus API keys de forma segura
7. **Usa `--dev` localmente** - Auto-reload ahorra tiempo
8. **Deploy incremental** - Deploy frecuente con cambios pequeños

---

## 📞 Recursos Adicionales

- **Documentación del proyecto**: `CLAUDE.md`
- **Guía de deploy inicial**: `DEPLOY.md`
- **Guía de acceso público**: `HABILITAR_ACCESO_PUBLICO.md`
- **Cloud Run docs**: https://cloud.google.com/run/docs
- **Logs en consola**: https://console.cloud.google.com/logs?project=datar-476419

---

**Última actualización**: 2025-11-12
**Proyecto**: DATAR - datar-476419
**Región**: us-central1
**URL Producción**: https://datar-456258944189.us-central1.run.app
