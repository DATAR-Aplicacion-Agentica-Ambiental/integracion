# Usar Python 3.13 como base
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY DATAR/requirements.txt /app/requirements.txt

# Instalar dependencias del sistema necesarias para algunas librerías de Python
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código completo del proyecto
COPY . /app/

# Crear directorio para outputs si no existe
RUN mkdir -p /app/WEB/outputs

# Exponer el puerto que usa el servidor
EXPOSE 8000

# Variables de entorno por defecto (se pueden sobreescribir)
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV API_ENV=production

# Comando para iniciar el servidor
CMD ["python", "API/server.py"]
