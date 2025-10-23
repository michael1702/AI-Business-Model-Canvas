## Hito 2: Integración continua

En este hito apliqué TDD y configuré la integración continua del proyecto. Por eso tuve que decidir que herramientas voy a utilizar.
### Elección y justificación
- Gestor de Tareas: se usa Makefile para ejecutar los mismos comandos en local y en CI: make install, make test, make ci. El Makefile es sencillo, estándar y permite  el mismo comando en local y CI.
- Biblioteca de aserciones y test runner: se usa pytest. Es simple, detecta tests automáticamente y permite fixtures y parametrización.
- Pruebas de API externa: se usa vcrpy para grabr una llamada real a la API de OpenAI una vez y luego la reproduzco. Así los tests son rápidos, deterministas y muy cercanos a las respuestas reales del cliente de OpenAI.
  - Nota sobre “stub”: Un stub sustituye una función por una respuesta falsa para probar la lógica sin red. Es útil para unit tests puros, pero en este proyecto priorizo vcrpy para mantener los tests alineados con el formato real de OpenAI y evitar mantener mocks manuales.
- CI / Integración continua: GitHub Actions para ejecutar los tests en cada push y pull request. Tiene la ventaja que es gratuito para repos públicos, tiene integración directa con GitHub y hay matrices de Python.

### Tests implementados
- /prefill_building_block con vcrpy: graba y reproduce un caso donde se rellena un bloque del BMC a partir de una idea de producto.
- /example_canvas_by_product con vcrpy: graba y reproduce un caso donde se genera un Canvas completo de ejemplo para una idea de producto.

### Cómo se ejecuta
- Local: make test (el primer run graba la cassette; los siguientes se reproducen).
- CI: el workflow .github/workflows/ci.yml ejecuta pytest; usa la cassette, no necesita clave ni red.

### Cobertura de funciones
- Rellenar un building block con datos generados por la API (test con vcrpy).
- Rellenar el Canvas completo con datos generados por la API (test con vcrpy).
- Futuro: usuarios, grupos y persistencia en nube (se añadirán tests de integración con DB usando testcontainers).

