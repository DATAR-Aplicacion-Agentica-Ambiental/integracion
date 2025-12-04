# Dockerfile personalizado para DATAR
# Este Dockerfile crea una imagen completa con ffmpeg y todas las dependencias necesarias
# La imagen se sube a Artifact Registry y se referencia en adk.yaml

FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Verificar que ffmpeg esté instalado
RUN ffmpeg -version || echo "Error: ffmpeg no se instaló correctamente"

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto que Cloud Run usará (ADK puede sobrescribir esto)
EXPOSE 8080

# El comando de inicio será manejado por ADK
# ADK puede sobrescribir esto, pero las dependencias del sistema ya estarán instaladas
CMD ["python", "-m", "google.adk.cli.fast_api"]

