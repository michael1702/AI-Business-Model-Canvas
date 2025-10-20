# proyecto-cc-michael-maurer
Proyecto Cloud Computing de Michael Maurer

Este repositorio recoge el avance de un proyecto de despliegue de una aplicación web para diseñar y colaborar sobre Business Model Canvas (BMC). La solución actual parte de una tesis de grado que diseñó y probó un prototipo con IA para ayudar a crear Business Model Canvas. El prototipo tiene explicaciones y ejemplos contextuales, el Value Proposition Canvas y funciones de apoyo durante el proceso para mejorar ideas y comprensión. También incluye exportación del BMC y notas para guardar avances. 

### Estado actual

Base teórica y prototipo inicial enfocado en la ayuda con IA para crear y evaluar el BMC, con VPC, ejemplos y guías breves. 
El código es de verano de 2023, cuando salió GPT-4. En estos años cambió el acceso a la API de OpenAI, así que ajusté las peticiones en App.py para que funcione.

Ahora no hay almacenamiento de datos en servidor. Solo se guarda de forma local en la caché del navegador o por exportación a un archivo JSON. Ese JSON se puede volver a importar.


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

### Prerequisitos para la ejecución del codigo
Para ejecutar el codigo necesitas tener python instalado. 
En una Virtual Environment tienes que instalar todos los librerías iniciado en el fichero "requirements.txt" --> "pip install -r requirements.txt".
Necesitas añadir un fichero .env, donde añades tu llave de API para OpenAI (mira el fichero env.example)

### Enlaces
- [Licencia](LICENSE)
- [Hito 1](docs/hito1.md)
- [Hito 2](docs/hito2.md)
