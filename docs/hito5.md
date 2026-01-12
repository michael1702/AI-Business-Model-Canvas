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

La infraestructura se ha definido en el archivo `render.yaml` situado en la raíz del repositorio, orquestando una arquitectura de **microservicios**.

### Descripción del archivo `render.yaml`
El archivo define la orquestación de **4 servicios web y una base de datos** que se comunican a través de la red privada de Render:

1.  **Servicios Web:**
    * **Frontend:** Sirve la interfaz de usuario (Flask + Jinja2) y actúa como Gateway.
    * **User Service:** Gestiona autenticación y usuarios.
    * **Group Service:** Gestiona la lógica de grupos.
    * **BMC Service:** Gestiona la lógica de negocio del canvas e integración con IA.
    * **Configuración:** Todos utilizan Docker y se inician mediante Gunicorn (`gunicorn --bind 0.0.0.0:$PORT ...`). 
2.  **Base de Datos (`postgres`):**
    * Motor: PostgreSQL.
    * Persistencia: Almacenamiento persistente en disco para asegurar que los datos de usuarios y BMCs no se pierdan entre reinicios.

**Enlace al código:** [`render.yaml`](../render.yaml)

---

## 3. Monitorización y Observabilidad

Para garantizar la operación continua y detectar incidencias proactivamente, se han implementado herramientas de observabilidad en dos niveles: interno (aplicación) y externo (disponibilidad).

### 3.1. Monitorización de Errores y Rendimiento (Sentry)
Se ha integrado **Sentry** en la aplicación Flask (`app.py`) para capturar excepciones y métricas de rendimiento en tiempo real.

* **Validación de la integración:** Para verificar el correcto funcionamiento del sistema de alertas, se implementó una ruta de prueba temporal (`/testerror`) diseñada para provocar un fallo intencionado (una división por cero).
* **Resultado:** Como se observa en la captura de pantalla, Sentry detectó inmediatamente la excepción `ZeroDivisionError`, proporcionando la traza completa (Stack Trace) y el contexto de la petición, lo que demuestra la capacidad de la aplicación para reportar incidencias críticas automáticamente.

<img width="1281" height="901" alt="image" src="https://github.com/user-attachments/assets/792852cd-6706-488f-a898-f28ecbb8eca5" />

Adicionalmente, Sentry monitoriza la latencia de las peticiones HTTP (Performance Monitoring), permitiendo identificar cuellos de botella en los endpoints de la API.

*(Opcional: Insertar aquí una captura del tab "Performance" de Sentry)*
### 3.2. Monitorización de Disponibilidad (UptimeRobot)
Se utiliza UptimeRobot como monitor sintético externo.

* **Configuración:** Realiza una petición HTTP `GET` cada 5 minutos al endpoint principal de la aplicación.
* **Alerta:** En caso de que la respuesta no sea `200 OK` (por ejemplo, caída del servidor o error 503), se envía una notificación inmediata por correo electrónico.

<img width="1872" height="950" alt="image" src="https://github.com/user-attachments/assets/64509e73-7056-490a-9e34-ae1c732bd30e" />

---

## 4. Pruebas de Carga (Stress Testing)

Se han realizado pruebas de estrés para verificar la estabilidad del despliegue bajo carga concurrente. Para ello se ha utilizado la herramienta Locust.

### Escenario de prueba (`tests/locustfile.py`)
El script de prueba simula un comportamiento realista de usuario:
1.  **Autenticación:** El usuario virtual intenta hacer login. Si la cuenta no existe (primera ejecución), se registra automáticamente y luego inicia sesión.
2.  **Navegación:** Una vez autenticado, el usuario accede repetidamente a su Dashboard de BMCs y a su perfil de usuario.

### Ejecución y Resultados
* **Configuración:** 50 usuarios concurrentes con una tasa de crecimiento (spawn rate) de 5 usuarios/segundo.
* **Resultado:** La aplicación desplegada **en el entorno local** respondió correctamente a todas las peticiones sin errores de servidor (5xx) y manteniendo tiempos de respuesta estables.

**Nota sobre el entorno de pruebas:** Las pruebas de estrés se realizaron contra el despliegue local (Docker Compose) en lugar de la versión en la nube. Esto se debe a que la capa de seguridad de Render (Cloudflare) bloquea automáticamente el tráfico automatizado de alta frecuencia (Error 429), interpretándolo como un ataque DDoS.

<img width="916" height="66" alt="image" src="https://github.com/user-attachments/assets/670915f9-f37c-41b6-b781-92d031dc15c6" />
Al probar localmente, podemos medir el rendimiento real de los microservicios sin la limitación del WAF externo.

<img width="1649" height="557" alt="image" src="https://github.com/user-attachments/assets/cd4a2a98-553f-4d71-ae44-fbb9ff94946d" />

<img width="1514" height="904" alt="image" src="https://github.com/user-attachments/assets/ecb765c7-3614-4ab7-a4dc-8a65c3b50748" />


---

## 5. Despliegue

La aplicación se encuentra desplegada y accesible públicamente en la siguiente URL:

🚀 **[https://aibmc-frontend.onrender.com](https://aibmc-frontend.onrender.com/)**
