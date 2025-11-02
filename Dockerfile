# Imagen base con Python 3.10 estable
FROM python:3.10-slim

# No escribir .pyc y loguear todo sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero requirements para aprovechar cache de build
COPY requirements.txt /app/requirements.txt

# Instalamos dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiamos el resto del código (app.py, assets/, data/, etc.)
COPY . /app

# Render expone la variable de entorno PORT; gunicorn la va a usar
ENV PORT=10000

# Comando para ejecutar la app en producción
CMD gunicorn --bind 0.0.0.0:$PORT app:server
