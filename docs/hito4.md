# Hito 4: Composición de servicios

En este hito he transformado mi aplicación en una arquitectura de microservicios usando contenedores Docker. Ahora la aplicación es fácil de desplegar y reproducible en cualquier máquina.

## 1. Estructura del Clúster

He diseñado un sistema compuesto por 5 contenedores que funcionan juntos. He separado las responsabilidades para que el código esté ordenado:

1.  Frontend (Gateway): Es la aplicación Flask principal. Sirve las páginas HTML y actúa como puerta de entrada.
2.  User Service: Microservicio para la gestión de usuarios y autenticación (tokens JWT).
3.  Group Service: Microservicio para gestionar los grupos y los BMC compartidos.
4.  BMC Service: Microservicio que contiene la lógica de Inteligencia Artificial (conecta con OpenAI).
5.  Base de Datos (PostgreSQL): Un contenedor exclusivo para guardar datos.

Todos los contenedores se comunican a través de una red interna privada llamada `aibmc-network`.

## 2. Configuración de Contenedores

Para los contenedores he tomado las siguientes decisiones:

* **Python Services:** Uso la imagen base `python:3.10-slim`.
    * *Justificación:* Es una imagen oficial de Python. Uso la versión "slim" porque ocupa mucho menos espacio en disco y es más segura porque tiene menos programas innecesarios instalados.
* **Base de Datos:** Uso la imagen `postgres:15-alpine`.
    * *Justificación:* Alpine Linux es una distribución muy pequeña y rápida. Es el estándar para contenedores de bases de datos ligeros.
* **Servidor Web:** Uso `gunicorn` en lugar del servidor de desarrollo de Flask. Esto es necesario para tener un rendimiento real y estable en producción.

## 3. Los archivos Dockerfile

He creado un archivo `Dockerfile` independiente para cada servicio. Esto permite instalar solo las librerías necesarias para cada uno:

* **[bmc_service/Dockerfile](../bmc_service/Dockerfile):** Instala librerías de IA. Puerto 5001.
* **[user_service/Dockerfile](../user_service/Dockerfile):** Instala librerías de seguridad. Puerto 5002.
* **[group_service/Dockerfile](../group_service/Dockerfile):** Instala librerías para grupos. Puerto 5003.
* **[Dockerfile (Frontend)](../Dockerfile):** Contenedor principal. Puerto 8888.

## 4. GitHub Packages (CI/CD)

He configurado una **GitHub Action** para automatizar todo el proceso.

* **Archivo:** [.github/workflows/publish.yml](../.github/workflows/publish.yml)
* **Funcionamiento:** Cuando hago un "push" a la rama `main`:
    1.  Se ejecutan los tests de integración del clúster.
    2.  Si los tests pasan, GitHub construye las 4 imágenes Docker.
    3.  Sube las imágenes automáticamente a **GitHub Container Registry (GHCR)**.

## 5. Orquestación con Docker Compose

El archivo **[compose.yaml](../compose.yaml)** une todas las piezas. Define:

* **Services:** Los 5 contenedores necesarios.
* **Environment:** Paso las credenciales (API Keys, Secretos) desde el archivo `.env` de forma segura.
* **Healthchecks:** Verifico que la base de datos esté lista antes de iniciar los servicios que dependen de ella.

## 6. Estado Actual y Limitaciones

Aunque la infraestructura está completa, hay dos puntos importantes sobre el estado actual del código:

1.  **Base de Datos:** El contenedor de PostgreSQL (`db`) está desplegado y configurado correctamente en el clúster (cumpliendo el requisito de infraestructura). Sin embargo, **el código Python todavía no escribe en la base de datos**. Actualmente, los datos se guardan en la memoria RAM de los servicios. La conexión real mediante código se hará en el siguiente hito.
2.  **Group Service (WIP):** El servicio de grupos funciona para crear grupos, pero la función de **"Añadir Miembros"** está en progreso (*Work in Progress*). Actualmente devuelve un error `user_not_found` porque el servicio de grupos aún no puede consultar la base de datos de usuarios correctamente.

## 7. Test del Clúster

He creado un script para verificar que el despliegue funciona.

* **Script:** [tests/test_cluster.ps1](../tests/test_cluster.ps1) (PowerShell para Windows) y `.sh` para Linux.
* **Qué hace:** Levanta el entorno con `docker compose`, espera a que inicie y lanza peticiones HTTP para confirmar que el Frontend y la API responden con código 200 (OK).
