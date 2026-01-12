# proyecto-cc-michael-maurer
Proyecto Cloud Computing de Michael Maurer

Este repositorio recoge el avance de un proyecto de despliegue de una aplicación web para diseñar y colaborar sobre Business Model Canvas (BMC). La solución actual parte de una tesis de grado que diseñó y probó un prototipo con IA para ayudar a crear Business Model Canvas. El prototipo tiene explicaciones y ejemplos contextuales, el Value Proposition Canvas y funciones de apoyo durante el proceso para mejorar ideas y comprensión. También incluye exportación del BMC y notas para guardar avances.

### Estado actual (Hito 5)

La aplicación ha sido completamente **desplegada en la nube**. Ahora utiliza una arquitectura de microservicios productiva alojada en **Render**.

* **Infraestructura:** Despliegue automatizado mediante Infrastructure as Code (IaC) con `render.yaml`.
* **Persistencia:** Base de datos PostgreSQL gestionada para usuarios, grupos y BMCs (ya no se usa memoria RAM).
* **CI/CD:**
    * Tests automáticos en cada Push (GitHub Actions).
    * Despliegue continuo (CD) a Render tras pasar los tests.
* **Observabilidad:**
    * Monitorización de errores con **Sentry**.
    * Monitorización de disponibilidad con **UptimeRobot**.
    * Pruebas de carga realizadas con **Locust**.

> **URL del despliegue:** [https://aibmc-frontend.onrender.com](https://aibmc-frontend.onrender.com/)

### Cómo ejecutar el proyecto (Local con Docker)

1.  **Requisitos:** Tener Docker y Docker Compose instalados.
2.  **Configuración:** Crea un archivo `.env` en la raíz (basado en `env.example`) con tu API Key de OpenAI.
3.  **Ejecución:**
    ```bash
    docker compose up --build
    ```
4.  Abrir `http://localhost:8888` en el navegador.

### Ejecución de Tests

Para probar que el clúster levanta correctamente:
```bash
# En Linux/Mac/Git Bash
./tests/test_cluster.sh

# En Windows PowerShell
.\tests\test_cluster.ps1
```
### Plan para el semestre
[x] Despliegue en la nube con base de datos (Hito 5).
[x] Gestión de usuarios con registro e inicio de sesión (Hito 4/5).
[x] Creación de equipos con acceso compartido a un mismo BMC (Hito 4/5).

### Funciones a añadir (resumen)

- Usuarios y seguridad: Registro, login (JWT), almacenamiento seguro de contraseñas.
- BMC en la nube: Creación, edición y borrado de BMCs persistentes en base de datos.
- Microservicios: Arquitectura separada para Frontend, User-Service, Group-Service y BMC-Service.
- Infraestructura: CI/CD con GitHub Actions, tests de integración, despliegue en PaaS (Render).
- Monitorización: Alertas de caída y trazas de errores en tiempo real.

### Enlaces
- [Licencia](LICENSE)
- [Hito 1](docs/hito1.md)
- [Hito 2](docs/hito2.md)
- [Hito 3](docs/hito3.md)
- [Hito 4](docs/hito4.md)
- [Hito 5](docs/hito5.md)
