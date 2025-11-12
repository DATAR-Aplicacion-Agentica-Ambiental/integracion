# Comandos Rápidos - DATAR

Referencia rápida de comandos más usados para trabajar con DATAR.

---

## 🏃 Desarrollo Local

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor (modo normal)
python run.py

# Iniciar servidor (auto-reload)
python run.py --dev

# Instalar nueva dependencia
pip install nombre-libreria
echo "nombre-libreria>=version" >> requirements.txt
```

---

## 🚀 Deploy a Producción

```bash
# Deploy rápido (recomendado)
./deploy-quick.sh

# Deploy manual
gcloud run deploy datar --source . --region us-central1

# Deploy con variables de entorno
gcloud run deploy datar \
  --source . \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="TU_KEY"
```

---

## 📊 Monitoreo y Logs

```bash
# Ver logs en tiempo real
gcloud run services logs tail datar --region us-central1

# Ver últimos 50 logs
gcloud run services logs read datar --region us-central1 --limit 50

# Filtrar errores
gcloud run services logs read datar --region us-central1 | grep ERROR

# Estado del servicio
gcloud run services describe datar --region us-central1
```

---

## 🌐 URLs de Producción

```
Frontend:  https://datar-456258944189.us-central1.run.app/static/index.html
API Docs:  https://datar-456258944189.us-central1.run.app/docs
Health:    https://datar-456258944189.us-central1.run.app/health
Agentes:   https://datar-456258944189.us-central1.run.app/api/agents
```

---

## 🔧 Configuración del Servicio

```bash
# Aumentar memoria
gcloud run services update datar --region us-central1 --memory 2Gi

# Aumentar timeout
gcloud run services update datar --region us-central1 --timeout 600

# Actualizar variable de entorno (sin re-deploy)
gcloud run services update datar \
  --region us-central1 \
  --set-env-vars VARIABLE="valor"

# Ver variables configuradas
gcloud run services describe datar \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

---

## 🐛 Depuración

```bash
# Ver revisiones (versiones)
gcloud run revisions list --service datar --region us-central1

# Rollback a versión anterior
gcloud run services update-traffic datar \
  --region us-central1 \
  --to-revisions datar-00002-abc=100

# Probar endpoint desde terminal
curl https://datar-456258944189.us-central1.run.app/health

# Ver builds recientes
gcloud builds list --limit 5

# Ver logs de un build específico
gcloud builds log [BUILD_ID]
```

---

## 📦 Git (Opcional pero Recomendado)

```bash
# Ver estado
git status

# Crear rama para nueva funcionalidad
git checkout -b feature/nombre-funcionalidad

# Hacer commit
git add .
git commit -m "Descripción del cambio"

# Volver a main
git checkout main

# Merge de cambios
git merge feature/nombre-funcionalidad

# Push a GitHub
git push origin main
```

---

## 🆘 Solución Rápida de Problemas

### Aplicación no responde (503)
```bash
# Ver logs para identificar error
gcloud run services logs read datar --region us-central1 --limit 30

# Verificar que la revisión esté lista
gcloud run revisions list --service datar --region us-central1
```

### Cambios no se reflejan
```bash
# Deploy forzando rebuild
gcloud run deploy datar --source . --region us-central1 --no-cache

# Limpiar cache del navegador: Ctrl+Shift+R
```

### Error 403 Forbidden
```bash
# Verificar permisos
gcloud run services get-iam-policy datar --region us-central1

# Permitir acceso público
gcloud run services add-iam-policy-binding datar \
  --region us-central1 \
  --member=allUsers \
  --role=roles/run.invoker
```

### Dependencia faltante
```bash
# Agregar a requirements.txt
echo "nombre-libreria>=version" >> requirements.txt

# Deploy (instalará la nueva dependencia)
gcloud run deploy datar --source . --region us-central1
```

---

## ⚡ Workflow Completo en 4 Pasos

```bash
# 1. Hacer cambios
nano archivo.py

# 2. Probar localmente
python run.py --dev

# 3. Deploy a producción
./deploy-quick.sh

# 4. Verificar
# Abrir: https://datar-456258944189.us-central1.run.app/static/index.html
```

---

## 📚 Documentación Completa

- **FLUJO_TRABAJO.md** - Guía detallada del flujo de trabajo
- **DEPLOY.md** - Guía completa de deploy desde cero
- **CLAUDE.md** - Documentación del proyecto
- **HABILITAR_ACCESO_PUBLICO.md** - Configurar acceso público

---

**Proyecto**: datar-476419
**Región**: us-central1
**Servicio**: datar
