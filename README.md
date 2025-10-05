# proyecto-cc-michael-maurer
Proyecto Cloud Computing de Michael Maurer

Este repositorio recoge el avance de un proyecto de despliegue de una aplicación web para diseñar y colaborar sobre Business Model Canvas (BMC). La solución actual parte de una tesis de grado que diseñó y probó un prototipo con IA para ayudar a crear Business Model Canvas. El prototipo tiene explicaciones y ejemplos contextuales, el Value Proposition Canvas y funciones de apoyo durante el proceso para mejorar ideas y comprensión. También incluye exportación del BMC y notas para guardar avances. 

### Estado actual

Base teórica y prototipo inicial enfocado en la ayuda con IA para crear y evaluar el BMC, con VPC, ejemplos y guías breves. 
El código es de verano de 2023, cuando salió GPT-4. En estos años cambió el acceso a la API de OpenAI, así que ajusté las peticiones en App.py para que funcione.

Ahora no hay almacenamiento de datos en servidor. Solo se guarda de forma local en la caché del navegador o por exportación a un archivo JSON. Ese JSON se puede volver a importar.


### Plan para el semestre

- Despliegue en la nube con base de datos.
- Gestión de usuarios con registro e inicio de sesión.
- Creación de equipos con acceso compartido a un mismo BMC.
