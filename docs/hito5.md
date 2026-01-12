# Hito 5: Despliegue de la aplicación en IaaS/PaaS

## 1. Selección del proveedor PaaS (Platform as a Service)

Para el despliegue productivo de la aplicación AI Business Model Canvas, se ha seleccionado la plataforma Render.

### Justificación de la elección:
* **Infraestructura como Código (IaC):** Render permite la configuración completa de la infraestructura mediante un archivo YAML (`render.yaml`). Esto cumple con el requisito de reproducibilidad y evita configuraciones manuales en la interfaz web.
* **Localización en Europa:** Render dispone de una región en **Frankfurt (Alemania)**. Esto es fundamental para cumplir con la normativa de protección de datos (GDPR) exigida en las especificaciones del proyecto.
* **Integración con GitHub:** El despliegue se realiza de forma automática ("Zero Downtime Deployment") cada vez que se hace un `push` a la rama principal (`main`), siempre que los tests de CI (`ci.yml`) hayan pasado correctamente.
* **Base de datos gestionada:** Provee una instancia de PostgreSQL gestionada, lo cual es más robusto que el archivo SQLite utilizado en el entorno de desarrollo.

---

## 2. Configuración de la Infraestructura (IaC)

La infraestructura se ha definido en el archivo `render.yaml` situado en la raíz del repositorio.

### Descripción del archivo `render.yaml`
El archivo define dos servicios principales que se despliegan conjuntamente:

1.  **Servicio Web (`web`):**
    * **Entorno:** Python 3.10.
    * **Comando de arranque:** `gunicorn app:app`. Se utiliza Gunicorn como servidor WSGI de producción en lugar del servidor de desarrollo de Flask.
    * **Variables de entorno:** Se inyectan automáticamente las credenciales de la base de datos (`DATABASE_URL`) y otras claves secretas definidas en el dashboard de Render.
    
2.  **Base de Datos (`postgres`):**
    * Motor: PostgreSQL.
    * Persistencia: Almacenamiento persistente en disco para asegurar que los datos de usuarios y BMCs no se pierdan entre reinicios.

**Enlace al código:** [`render.yaml`](./render.yaml)

---

## 3. Monitorización y Observabilidad

Para garantizar la operación continua y detectar incidencias proactivamente, se han implementado herramientas de observabilidad en dos niveles: interno (aplicación) y externo (disponibilidad).

### 3.1. Monitorización de Errores y Rendimiento (Sentry)
Se ha integrado Sentry en la aplicación Flask (`app.py`).

* **Funcionalidad:** Captura excepciones no controladas (Errores 500) y monitoriza el rendimiento de las transacciones HTTP.
* **Beneficio:** Permite ver la traza completa del error (Stack Trace) y las variables locales en el momento del fallo, facilitando una corrección rápida.

*(Insertar aquí: Captura de pantalla del Dashboard de Sentry mostrando una incidencia o la lista de transacciones)*

### 3.2. Monitorización de Disponibilidad (UptimeRobot)
Se utiliza UptimeRobot como monitor sintético externo.

* **Configuración:** Realiza una petición HTTP `GET` cada 5 minutos al endpoint principal de la aplicación.
* **Alerta:** En caso de que la respuesta no sea `200 OK` (por ejemplo, caída del servidor o error 503), se envía una notificación inmediata por correo electrónico.

*(Insertar aquí: Captura de pantalla de UptimeRobot mostrando el estado "Up" y el historial de respuesta)*

---

## 4. Pruebas de Carga (Stress Testing)

Se han realizado pruebas de estrés para verificar la estabilidad del despliegue bajo carga concurrente. Para ello se ha utilizado la herramienta Locust.

### Escenario de prueba (`tests/locustfile.py`)
El script de prueba simula un comportamiento realista de usuario:
1.  **Autenticación:** El usuario virtual intenta hacer login. Si la cuenta no existe (primera ejecución), se registra automáticamente y luego inicia sesión.
2.  **Navegación:** Una vez autenticado, el usuario accede repetidamente a su Dashboard de BMCs y a su perfil de usuario.

### Ejecución y Resultados
* **Configuración:** 50 usuarios concurrentes con una tasa de crecimiento (spawn rate) de 5 usuarios/segundo.
* **Resultado:** La aplicación desplegada en Render respondió correctamente a todas las peticiones sin errores de servidor (5xx) y manteniendo tiempos de respuesta estables.

*(Insertar aquí: Captura de pantalla de los gráficos de Locust mostrando "Requests per Second" y "Response Times")*

---

## 5. Despliegue

La aplicación se encuentra desplegada y accesible públicamente en la siguiente URL:

🚀 **[https://aibmc-frontend.onrender.com](https://aibmc-frontend.onrender.com/)**