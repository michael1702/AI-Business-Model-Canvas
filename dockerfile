# Dockerfile (Root/Frontend)
FROM python:3.10-slim

WORKDIR /app

# 1. Instalar dependencias de TODOS los microservicios
# (Necesario porque app.py importa el código directamente)
COPY user_service/requirements.txt user_reqs.txt
COPY bmc_service/requirements.txt bmc_reqs.txt

# Instalar dependencias combinadas + Gunicorn
RUN pip install --no-cache-dir -r user_reqs.txt && \
    pip install --no-cache-dir -r bmc_reqs.txt && \
    pip install gunicorn

# 2. Copiar todo el código del proyecto
COPY . .

# 3. Exponer el puerto
EXPOSE 8888

# 4. Ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "app:create_app()"]