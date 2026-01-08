# user_service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copiar requirements especificos del user_service
COPY user_service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY user_service/ user_service/

# Configurar PYTHONPATH
ENV PYTHONPATH=/app

# Ejecutar en el puerto 5002
CMD gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:app