# Hito 4: Composición de servicios

En este hito he transformado mi aplicación en una arquitectura de microservicios real usando contenedores Docker. Ahora la aplicación es fácil de desplegar y reproducible.

## 1. Estructura del Clúster

He diseñado un clúster compuesto por 5 contenedores que funcionan juntos. He decidido separar las responsabilidades para que el sistema sea modular:

1.  Frontend (Gateway):Es la aplicación Flask principal que sirve el HTML. Actúa como puerta de entrada.
2.  User Service:Microservicio dedicado a la gestión de usuarios y autenticación (JWT).
3.  Group Service:Microservicio para gestionar los grupos y los BMC compartidos.
4.  BMC Service:Microservicio que contiene la lógica de Inteligencia Artificial (OpenAI).
5.  Base de Datos (PostgreSQL):Un contenedor exclusivo para guardar los datos, como pide el requisito.

Todos los contenedores se comunican a través de una red interna llamada `aibmc-network`.

## 2. Configuración de Contenedores e Imágenes Base

Para los contenedores he tomado las siguientes decisiones de diseño:

* **Python Services:** Uso la imagen base `python:3.10-slim`.
    * *Justificación:* Es una imagen oficial de Python pero mucho más ligera (menos megabytes) que la versión completa. Es más segura y rápida para desplegar.
* **Base de Datos:** Uso la imagen `postgres:15-alpine`.
    * *Justificación:* Alpine Linux es una distribución muy pequeña y segura, ideal para contenedores de bases de datos en producción.
* **Servidor Web:** Uso `gunicorn` en lugar del servidor de desarrollo de Flask para tener un rendimiento real de producción.

## 3. Los archivos Dockerfile

He creado un `Dockerfile` para cada servicio para aislar sus dependencias:

* **[bmc_service/Dockerfile](../bmc_service/Dockerfile):** Instala solo las librerías de IA y ejecuta el servicio en el puerto 5001.
* **[user_service/Dockerfile](../user_service/Dockerfile):** Instala librerías de base de datos y seguridad. Corre en el puerto 5002.
* **[group_service/Dockerfile](../group_service/Dockerfile):** Instala lo necesario para grupos y corre en el puerto 5003.
* **[Dockerfile (Frontend)](../Dockerfile):** Es el contenedor principal que expone el puerto 8888 para el usuario.

Todos los Dockerfiles usan variables de entorno para configurar cosas importantes como claves secretas (API Keys).

## 4. GitHub Packages (CI/CD)

He configurado una **GitHub Action** para automatizar la publicación de contenedores.

* **Archivo:** [.github/workflows/publish.yml](../.github/workflows/publish.yml)
* **Funcionamiento:** Cada vez que hago un "push" a la rama `main`:
    1.  GitHub ejecuta los tests de integración.
    2.  Si los tests pasan, construye las 4 imágenes Docker.
    3.  Sube las imágenes automáticamente a **GitHub Container Registry (GHCR)**.

Puedes ver los paquetes publicados en la página principal del repositorio, en la barra lateral derecha.

## 5. Orquestación con Docker Compose

El archivo **[compose.yaml](../compose.yaml)** es el corazón del despliegue. Define cómo se relacionan los servicios:

* **Services:** Define los 5 contenedores.
* **Networks:** Crea la red `aibmc-network` para que los servicios se vean entre ellos usando sus nombres (ej: `http://user-service:5002`).
* **Volumes:** He definido un volumen `postgres_data` para que los datos de la base de datos no se pierdan si apago el contenedor.
* **Environment:** Paso las credenciales (DB User, API Keys) desde el archivo `.env` local a los contenedores de forma segura.

## 6. Test del Clúster

He creado un script de prueba para verificar que el despliegue funciona correctamente.

* **Script:** [tests/test_cluster.sh](../tests/test_cluster.sh)
* **Qué hace:**
    1.  Levanta todo el entorno con `docker compose up -d`.
    2.  Espera 15 segundos para que la base de datos inicie.
    3.  Usa `curl` para comprobar que el Frontend (puerto 8888) responde con código 200.
    4.  Usa `curl` para comprobar que la API interna (puerto 5001) responde correctamente.
    5.  Apaga el clúster.

Este test se ejecuta automáticamente en GitHub Actions antes de publicar las imágenes, asegurando la calidad.
