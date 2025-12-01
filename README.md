# proyecto-cc-michael-maurer
Proyecto Cloud Computing de Michael Maurer

Este repositorio recoge el avance de un proyecto de despliegue de una aplicación web para diseñar y colaborar sobre Business Model Canvas (BMC). La solución actual parte de una tesis de grado que diseñó y probó un prototipo con IA para ayudar a crear Business Model Canvas. El prototipo tiene explicaciones y ejemplos contextuales, el Value Proposition Canvas y funciones de apoyo durante el proceso para mejorar ideas y comprensión. También incluye exportación del BMC y notas para guardar avances. 

### Estado actual (Hito 4)

La aplicación ha sido completamente **contenerizada**. Ahora utiliza una arquitectura de microservicios orquestada con Docker Compose.

* **Frontend:** Flask App.
* **Microservicios:** User Service, Group Service, BMC Service.
* **Datos:** Base de datos PostgreSQL en contenedor.
* **Despliegue:** Imágenes Docker publicadas automáticamente en GitHub Packages.

### Cómo ejecutar el proyecto (Docker)

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

### Plan para el semestre

- Despliegue en la nube con base de datos.
Los BMC deben estar almacenados en la nube y ser accesibles desde distintos usuarios y dispositivos vía web. Ahora mismo los BMC están solo en la caché del navegador o en un fichero JSON compartible.
- Gestión de usuarios con registro e inicio de sesión.
Añadir registro, login y logout. Cada usuario podrá crear, ver, editar y borrar sus BMC en la nube, unirse a grupos y salir de ellos, y ver o editar BMC del grupo según permisos.
- Creación de equipos con acceso compartido a un mismo BMC.
Crear/borrar grupos, gestionar miembros, y almacenar BMC de grupo accesibles para todos los miembros con permisos definidos.

### Funciones a añadir (resumen)

- Usuarios y seguridad: registro, login, recuperación de contraseña, roles básicos (usuario, admin), API rate limit.
- BMC en la nube: Almacenamiento de BMC en la nube, accesible de varios dispositivos.
- Grupos y colaboración: crear grupos, invitar y expulsar miembros, permisos de lectura y edición.
- Plantillas: cambiar entre plantillas (BMC, Lean Canvas, plantilla personalizada).
- Infraestructura: CI con GitHub Actions, tests con pytest, mocks de API, y futura integración con base de datos gestionada.
- Admin: panel simple para ver/gestionar usuarios, grupos.

### Enlaces
- [Licencia](LICENSE)
- [Hito 1](docs/hito1.md)
- [Hito 2](docs/hito2.md)
- [Hito 3](docs/hito3.md)
- [Hito 4](docs/hito4.md)
