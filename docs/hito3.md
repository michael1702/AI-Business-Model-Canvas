

# Hito 3: Diseño de microservicios

## Resumen

En este hito dividí la aplicación en microservicios y expuse la lógica por una **API REST bajo `/api/v1`**. Separé API, dominio y adaptadores, añadí **logs**, y preparé **tests y CI**. También incorporé un microservicio de **usuarios** (registro, login, perfil y CRUD de BMCs por usuario). 

-  **Framework**: Flask se mantiene por continuidad, simplicidad y ecosistema; Blueprints permiten modularidad por servicio y versionado de API (`/api/v1`), lo que facilita pruebas y crecimiento.
-  **Diseño por capas**: API desacoplada de dominio/adaptadores; `user_service` y `bmc_service` con rutas claras y tests.
-  **Logs**: registro JSON por petición.
-  **Tests**: pytest para flujo de usuarios y CRUD de BMC, ejecutados en GitHub Actions. 

* **Continuidad y velocidad**: el proyecto original ya usaba Flask; mantenerlo evita reescrituras y reduce riesgo. Además, Flask es ligero, “baterías opcionales” y encaja muy bien con un diseño por capas sencillo (API + dominio + adaptadores).
* **Ecosistema**: Jinja2 para vistas, fácil integración con logging, testing con `pytest` y despliegues simples (Gunicorn/Docker).
* **Blueprints**: permiten **modularizar** por microservicio (p. ej., `bmc_service` y `user_service`), versionar rutas con prefijos (`/api/v1/...`), **aislar dependencias** y **testear** cada módulo por separado. Esto facilita crecer (añadir futuros servicios como grupos) sin “monolito”.

## Estructura del repositorio (resumen)

Raíz del repo con carpetas y ficheros clave:

* **`bmc_service/`**: lógica de negocio del BMC y comunicación con la IA (rutas como `/api/v1/bmc/example` y `/api/v1/bmc/prefill`).
* **`frontend`** Incluye `templates/` y `static/` para la UI actual.
* **`user_service/`**: API de usuarios (registro, login JWT, `/users/me`, y **CRUD de BMCs del usuario**).
* **`frontend/`**: páginas y scripts del cliente para navegación (auth, listado de BMCs, página del BMC).
* **`tests/`**: incluye los **tests de `user_service`** añadidos en este hito (registro, login, `/me` y CRUD de BMCs).
* **`app.py`** (raíz): punto de entrada que **registra los Blueprints** de cada microservicio y activa el logging por petición
* Infraestructura: **`Makefile`** (tareas comunes), **`.github/workflows/`** (CI con GitHub Actions), **`dockerfile`**, **`env.example`**, y **`LICENSE`** (Apache-2.0).

## Rutas principales

**BMC**

* `POST /api/v1/bmc/example` → Canvas de ejemplo por idea.
* `POST /api/v1/bmc/prefill` → Rellenar un building block con el LLM.

**Usuarios**

* `POST /api/v1/users/register` → Registro.
* `POST /api/v1/users/login` → Login (JWT).
* `GET  /api/v1/users/me` → Perfil actual (requiere token).
* `GET  /api/v1/users/me/bmcs` → Listar BMCs del usuario.
* `POST /api/v1/users/me/bmcs` → Crear/actualizar BMC del usuario.
* `GET  /api/v1/users/me/bmcs/<id>` → Obtener un BMC.
* `DELETE /api/v1/users/me/bmcs/<id>` → Borrar un BMC. 

## Gestión de usuarios: cómo está hecha

* **Autenticación con JWT**: `POST /users/login` emite un **access token** firmado (secreto `JWT_SECRET` por variable de entorno) y con expiración configurable; el cliente lo envía como `Authorization: Bearer <token>`.
* **Autorización**: las rutas bajo `/users/me/*` validan el token y extraen el `user_id`.
* **Contraseñas**: se guardan **hasheadas** (no en claro) antes de validar.
* **Almacenamiento actual**: por simplicidad del hito, los BMCs de usuario se guardan en memoria del servicio (y en el cliente hay persistencia local para la UI). El plan es pasar a BD en el siguiente hito.
* **Flujo en frontend**: al hacer login, el token se guarda (storage), la **sidebar** se habilita y el usuario puede **crear/listar/abrir** sus BMCs desde *“My BMCs”*. Al guardar en la página del BMC, se puede **guardar como nuevo** o **actualizar el actual**, y queda disponible en el listado. (La UI vive en `frontend/` y los endpoints residen en `user_service/`.) 

## Logs

Middleware de Flask registra cada petición y respuesta en JSON (eventos `request_in`/`request_out` con ruta y estado) para depurar y preparar **logs centralizados** en despliegue.

## Tests añadidos (Hito 3)

En `tests/user_service/` se añadieron **dos ficheros de pytest** que cubren:

* **Registro y login**; `/users/me` con token válido/ inválido.
* **CRUD de BMCs**: crear → listar → obtener → actualizar → borrar.
  Se ejecutan en local y en **GitHub Actions** en cada *push* y *PR*. 

## Cómo ejecutar (local)

* **App**: `python app.py` y abrir `http://localhost:8888`.
* **Tests**: `pytest -q` (o `make test`). 

## Estado de persistencia

De momento **sin BD**: lado servidor mínimo (memoria) y **almacenamiento local del navegador** para la UI. Próximo hito: persistencia real (DB) y modelos relacionales (usuarios, BMCs, grupos). 

## Problemas conocidos

* La **sesión** no siempre se conserva al navegar; en algunos casos vuelve a pedir autenticación.
* Al abrir un BMC guardado, a veces la **Product Idea** no se actualiza si hay estado previo del navegador.
* Sidebar homogénea en todas las páginas: aún se está afinando el orden de carga de scripts. (Se resolverá junto con la persistencia real).

## Próximos pasos

* **Base de Datos** para usuarios y BMCs; migración del almacenamiento en memoria.
* **Grupos/teams** y permisos de acceso compartido.
* Más endpoints (VPC, evaluación, tips) y **tests de integración**.
* Docker + despliegue en cloud con **logs centralizados**.



