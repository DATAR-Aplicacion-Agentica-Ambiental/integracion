# Dockerfile personalizado para DATAR
# Este Dockerfile crea una imagen completa con todas las dependencias necesarias
# La imagen se sube a Artifact Registry y se referencia en adk.yaml
# Nota: Ya no requiere ffmpeg - el procesamiento de audio usa WAV con scipy/numpy

FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

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

