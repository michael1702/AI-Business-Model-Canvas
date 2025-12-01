# group_service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies (Group service needs Flask and PyJWT)
# Using a manual install list since requirements.txt wasn't explicitly provided for group_service
RUN pip install Flask PyJWT gunicorn requests

# Copy Group Service Code
COPY group_service/ group_service/

# CRITICAL: Copy User Service code because group_service imports 'user_service.security'
COPY user_service/ user_service/

# Set Python path
ENV PYTHONPATH=/app

# Run on port 5003
CMD ["gunicorn", "--bind", "0.0.0.0:5003", "group_service.wsgi:app"]