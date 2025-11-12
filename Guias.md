 # Guías de DATAR

 ## 1. FLUJO_TRABAJO.md (PRINCIPAL)
 Léela una vez para entender el proceso completo.

 ### Contenido:
 - ✅ Cómo trabajar localmente
 - ✅ Cómo hacer cambios
 - ✅ Cómo actualizar producción
 - ✅ 5 casos comunes explicados paso a paso
 - ✅ Solución de problemas
 - ✅ Buenas prácticas

 ## 2. COMANDOS_RAPIDOS.md - Referencia Rápida (DÍA A DÍA)
 Una "cheat sheet" para el uso diario.

 ### Contenido:
 - ⚡ Comandos más usados
 - ⚡ URLs de producción
 - ⚡ Soluciones rápidas a problemas comunes
 - ⚡ Workflow en 4 pasos

 ## 3. `deploy-quick.sh` - Script Automatizado
 Para hacer deploy rápido sin escribir comandos largos.

 ### Cómo usarlo:
 ```bash
 ./deploy-quick.sh
 ```

 ### Qué hace:
 1. Verifica que tengas `gcloud` configurado.
 2. Hace deploy automáticamente.
 3. Te muestra la URL actualizada.
 4. Te da instrucciones de cómo ver logs.

 Es la forma más rápida de actualizar producción.

 ---

 # Workflow Típico Básico

 ## Opción A: Usando el Script

 1. **Hacer tus cambios**
    ```bash
    nano DATAR/agents/sub_agents/gente_montana/agent.py
    ```
 2. **Probar localmente**
    ```bash
    python run.py --dev
    ```
 3. **Deploy con un comando**
    ```bash
    ./deploy-quick.sh
    ```

 ## Opción B: Manual (Más Control)

 1. **Hacer tus cambios**
    ```bash
    nano WEB/js/app.js
    ```
 2. **Probar localmente**
    ```bash
    python run.py --dev
    ```
    Probar en: `http://localhost:8000/static/index.html`

 3. **Deploy manual**
    ```bash
    gcloud run deploy datar --source . --region us-central1
    ```
 4. **Verificar**
    Abrir: `https://datar-456258944189.us-central1.run.app/static/index.html`

 ---

 # Ejemplos

 ## Ejemplo 1: Cambiar el Frontend

 1. **Editar**
    ```bash
    nano WEB/css/styles.css
    ```
 2. **Ver cambios localmente**
    ```bash
    python run.py --dev
    ```
    Abre `http://localhost:8000/static/index.html`

 3. **Deploy**
    ```bash
    ./deploy-quick.sh
    ```
 4. **Ver en producción** (refresca con `Ctrl+Shift+R`)

 ## Ejemplo 2: Modificar un Agente

 1. **Editar el agente**
    ```bash
    nano DATAR/datar/sub_agents/Gente_Montaña/agent.py
    ```
 2. **Probar localmente**
    ```bash
    python run.py
    ```
    Abre el frontend y prueba el agente.

 3. **Deploy**
    ```bash
    ./deploy-quick.sh
    ```
 4. **Verificar en producción**

 ## Ejemplo 3: Ver Logs de Producción

 *   **Ver logs en tiempo real**
    ```bash
    gcloud run services logs tail datar --region us-central1
    ```
 *   **O ver últimos 50**
    ```bash
    gcloud run services logs read datar --region us-central1 --limit 50
    ```

 ---

 # Tips Importantes

 *   **Siempre prueba localmente primero**

    python run.py --dev  # ← Usa --dev para auto-reload

 *   **Usa el script rápido para deploy**

    ./deploy-quick.sh  # ← Más fácil que comandos largos

 *   **Revisa logs después del deploy**

    gcloud run services logs tail datar --region us-central1



 *   **Si algo falla, revisa los logs** El 90% de los problemas se resuelven viendo los logs.

 ---

 # Resumen Ultra-Rápido

 Para hacer cambios en producción:

 1. Edita el código localmente.
 2. Prueba con `python run.py --dev`.
 3. Deploy con `./deploy-quick.sh`.
 4. Verifica en `https://datar-456258944189.us-central1.run.app/static/index.html`.


 ---

 # Si Necesitas Ayuda

 1. Revisa `COMANDOS_RAPIDOS.md` - Probablemente esté ahí.
 2. Lee la sección de problemas en `FLUJO_TRABAJO.md`.
 3. Revisa los logs: `gcloud run services logs tail datar --region us-central1`.
