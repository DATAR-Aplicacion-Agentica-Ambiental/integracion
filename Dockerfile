# Dockerfile para DATAR Integrado
# Deploy en Google Cloud Run

# Usar imagen oficial de Python
FROM python:3.11-slim

# Instalar FFmpeg (requerido para agente_sonido)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (mejor cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Exponer puerto 8080 (Cloud Run usa la variable PORT)
ENV PORT=8080
EXPOSE 8080

# Variables de entorno predeterminadas (se sobrescriben en Cloud Run)
ENV API_HOST=0.0.0.0
ENV API_ENV=production

# Comando para iniciar el servidor
# Cloud Run espera que la app escuche en 0.0.0.0:$PORT
# Ejecutar desde el directorio raíz con PYTHONPATH configurado
ENV PYTHONPATH=/app:/app/API:$PYTHONPATH
CMD ["sh", "-c", "cd /app && uvicorn API.server:app --host 0.0.0.0 --port ${PORT} --log-level info"]
