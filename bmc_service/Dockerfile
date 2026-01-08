# bmc_service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY bmc_service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY bmc_service/ bmc_service/

# Set Python path to find the module
ENV PYTHONPATH=/app

# Run the application using Gunicorn
# Calls the create_app factory in config.py
CMD gunicorn --bind 0.0.0.0:$PORT "bmc_service.config:create_app()"