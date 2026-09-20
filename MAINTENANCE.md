# TODO del repositorio (consolidado)

Seguimiento de las tareas pendientes extraídas del historial. La **fuente de
verdad es [`MAINTENANCE.md`](MAINTENANCE.md)**: cada tarea apunta a la entrada de
la que salió, y el estado del código prevalece sobre este listado. Al cerrar una
tarea, múdala aquí a la sección resuelta con la referencia de la sesión que la
cerró (fecha + PR si la hay).

Convención de estados:

- `[ ]` pendiente
- `[x]` resuelta (tachada, en su sección de proyecto)

---

## TaskHub_Angular — frontend

- [x] **Tablero cortado a 20 tareas sin aviso.** `TaskService.listByProject`
  ahora manda `limit: 100` (máximo del validador). _Fuente: entrada 2026-09-11
  (noche), #90. Resuelto 2026-09-18._
- [x] **Dashboard cortado a 10 proyectos sin aviso.** `loadProjects` pide
  `listProjects(1, 100)`. _Fuente: 2026-09-11 (noche), #90. Resuelto 2026-09-18._
- [x] **Error de carga mudo («No tienes proyectos aún»).** Ahora hay estado
  `loadError` distinto de lista vacía. _Fuente: 2026-09-11 (noche), #90.
  Resuelto 2026-09-18._
- [x] **Botones habilitados con 1 carácter + «No se pudo crear» genérico.**
  `trim().length >= 2` en los diálogos y el aviso muestra el `{ message }` del
  backend. _Fuente: 2026-09-11 (noche), #90. Resuelto 2026-09-18._
- [x] **README del proyecto desactualizado: «99 tests».**
  `JS/Angular/TaskHub_Angular/README.md` sigue diciendo que son 99; el CI exige
  103 del frontend (cifras vigentes en el README raíz). Actualizado el 2026-09-19
  con la verificación real de la suite: 103 frontend (dashboard 17, projects 44)
  y 175 backend (162 con dobles + 13 contra PostgreSQL). _Fuente: auditoría
  `/VerificarDocs` 2026-09-19 → resuelto 2026-09-19 (rama `UpgradeDocs`)._

## RadioStack

- [x] **`@EntityScan` / `@EnableJpaRepositories` al módulo de persistencia.** Hoy
  viven en la clase de arranque de la API; moverlas a una configuración de
  `radiostack-persistence` resolvería de raíz las rodajas y quitaría a la API el
  conocimiento de los paquetes internos de otro módulo. Es cambio de producción,
  merece PR propio. _Bloque C. Fuente: 2026-09-12, «Lo que queda anotado y sin
  hacer». Resuelto 2026-09-18 (PR #105, `fix: move JPA configuration to
  persistence`); la ficha quedó abierta por error en el ToDo y se cierra
  2026-09-20._
- [x] **GET públicos bajo `/api/v1`.** Regla pensada para la parrilla/programas,
  alcanza a todos los GET (incluido `/api/v1/auth/me`). Decisión de producto:
  queda **documentado con un test**, no se cambia por iniciativa propia.
  `SecurityConfigTest.la_parrilla_se_puede_leer_sin_token` fija la regla para un
  GET de catálogo. _Fuente: 2026-09-12. Resuelto 2026-09-19 (rama
  `Fix_GET_Publicos`, mín. CI 166)._
- [x] **Suplantación por REST en el chat.** `ChatController` ya toma el alias del
  token (`usuario.email()`), no del cuerpo. _Fuente: 2026-09-11 (noche) →
  resuelto 2026-09-12._
- [x] **`maven-test` buscaba `surefire-reports` en la raíz.** El CI ya usa
  `find` de `*/target/` (multimódulo). _Fuente: 2026-09-11 (noche) → resuelto
  2026-09-12._
- [x] **Comentario «Java · compilar» decía sin tests.** Actualizado; menciona
  `LocutorTest`. _Fuente: 2026-09-11 (noche) → resuelto 2026-09-12._
- [x] **`radiostack-api` sin dependencias de test.** Ya declara
  `spring-boot-starter-test`. _Fuente: 2026-09-11 (noche) → resuelto 2026-09-12._
- [x] **500 en todo endpoint con id de ruta (`-parameters`).** Resuelto en el
  `pom` padre; 11 endpoints, 0 con 500. _Fuente: 2026-09-12._
- [x] **Test STOMP de punta a punta con `@SpringBootTest`.**
  `ChatStompEndToEndTest` recorre el chat completo contra un servidor real:
  CONNECT con token, suscripción al tópico de una emisión, SEND autenticado que
  se guarda y se difunde con el alias del token, lectura anónima permitida y
  envío sin token rechazado sin guardar nada. Comparte el gate
  `RADIOSTACK_DB_TESTS` con `EsquemaYMigracionesTest`; api pasa de 126 a 129 y
  el mínimo de CI de 162 a 165. _Fuente: 2026-09-12 → resuelto 2026-09-19 (rama
  `Fix_Stomp_EndToEnd`)._

## CV

- [x] **CV desactualizado: «71 tests», «Angular 19» y las cifras de TaskHub_Angular.**
  El `package.json` declara `@angular/core ^21.2.19` y las cifras vigentes están
  en `README.md` (tabla de tests del CI). Actualizado vía el comando global
  `ActualizarCV`: las dos variantes de `CV_Tecnico` declaran 278 tests —175
  backend + 103 frontend— y Angular 21. _Fuente: 2026-09-11 (noche), 2026-09-18
  y 2026-09-19 → resuelto 2026-09-19._

## Seguridad y dependencias

- [x] **44 vulnerabilidades sin verificar por API.** GitHub informó de «44
  vulnerabilities on the default branch (16 high, 22 moderate, 6 low)» al hacer
  push; la cabecera de MAINTENANCE.md dice 2 alertas Dependabot abiertas. Hace
  falta consultar la API. Verificadas por la API de GitHub el 2026-09-19: **44
  abiertas (16 high, 22 medium, 6 low)** —npm 33, pip 8, maven 2, composer 1—.
  Detalle en la entrada fechada. _Fuente: 2026-09-11 (noche) → resuelto
  2026-09-19 (rama `UpgradeDocs`)._
- [x] **Dependabot (pip): bloque «En curso».** Es la única fila no saneada del
  estado de mantenimiento del README raíz. Las 8 alertas pip son todas `torch`
  de FPS-AI-Toolkit, excluidas a propósito por `dependabot.yml` (el stack de
  PyTorch se gestiona a mano con el índice CUDA). _Fuente: README.md (tabla de
  mantenimiento) → resuelto 2026-09-19 (rama `UpgradeDocs`)._
- [ ] **Vulnerabilidades corregibles (npm/Maven con parche).** Bloque G (alta):
  corregir las alertas que tienen parche disponible y dejar documentadas las que
  no lo tienen (`extract-zip` y `torch ≤ 2.6.0`). Punto de partida en el análisis
  del 2026-09-19 (44 abiertas: 16 high, 22 medium, 6 low). _Bloque G. Fuente:
  2026-09-19 (rama `UpgradeDocs`)._

## TaskHub_React (del historial, siguen abiertos)

- [x] **Encadenar el despliegue al CI.** Render ya espera al pipeline: un commit
  en rojo no llega a producción. Lo resolvió el usuario personalmente. _Fuente:
  2026-08-29/30, «Pendiente» → resuelto 2026-09-19._
- [x] **Limitación de intentos por cuenta además de por IP** (hoy solo por
  dirección). _Fuente: 2026-08-29/30 → resuelto 2026-09-19._ Implementado como
  capas 2 y 3 del login (`accountSlowDown` + `accountLimiter`, tope duro de 200
  por cuenta) en `server/src/middleware/rateLimit.middleware.ts` y cableado en
  `server/src/modules/auth/auth.router.ts`, con tests en
  `rateLimit.middleware.test.ts`.
- [x] **Acciones del CI fijadas a etiqueta mayor, no a SHA.** Todas las acciones
  de `taskhub-react-ci.yml` y de `ci.yml` (raíz) quedaron ancladas a SHA completos
  con nota de política en la cabecera: `checkout`, `setup-node`, `upload-artifact`,
  `setup-python`, `setup-java` y `shivammathur/setup-php` (este último apuntaba a
  un tag anotado; se resolvió al commit real del tag). Verificado: cero referencias
  `@v*` restantes en `.github/workflows/`. _Fuente: 2026-08-29/30 → resuelto
  2026-09-19._
- [x] **Protección de rama** que exija `ci-ok` antes de fusionar (sin revisión
  humana). Lo resolvió el usuario personalmente. _Fuente: 2026-08-29/30 →
  resuelto 2026-09-19._
- [x] **`PUT` y `PATCH` comparten controlador** (actualización parcial en ambos;
  desviación de la semántica HTTP, con tests desde la auditoría). Separados:
  `PUT` es reemplazo completo (exige título como `POST`; campos omitidos vuelven
  a sus valores por defecto) con `replaceTaskValidator` y método `replace`; `PATCH`
  sigue siendo parcial con `update`. Tests nuevos en `tasks.validation.test.ts`,
  `tasks.service.test.ts` y `tasks.controller.test.ts`, y comprobaciones en
  `verify.ts`. _Fuente: 2026-08-29/30 → resuelto 2026-09-19._
- [x] **E2E comparten la base de desarrollo** y dejan usuarios `e2e-*`; limpiarlos
  o darles BD propia. La salvaguarda de `playwright.config.js` ya impedía apuntar
  a producción; ahora hay además un `npm run wipe:e2e` que borra de una vez los
  usuarios `e2e-*` (tareas y sesiones en cascada). _Bloque D. Fuente: 2026-08-29/30.
  Resuelto 2026-09-20 (rama `BloqueD`)._

## OmniForge y GPTDevTeam (Bloque F)

- [x] **OmniForge.** Documentación reescrita (arquitectura real: planner
  multi-agente, `--solo`, 29 tools en 5 módulos, memoria, evaluador, skills,
  visión) y suite pytest de **115 tests** (planner, evaluador, memoria, skills,
  LLM, filesystem, terminal, visión, configuración, estados, main y contrato de
  tools). Sin LLM, pantalla, navegador ni red. De paso se corrigió un bug en
  `main.py`: `run()` comparaba el estado final contra `{"timeout",
  "plan_empty"}` cuando `synthesize()` emite `"error"`/`"done"`, así que las
  tareas fallidas **sí** entraban en la memoria; ahora solo guarda `status ==
  "done"`. `requirements-dev.txt` (pytest) creado. _Bloque F. Fuente: 2026-09-11
  (noche) y 2026-09-18. Resuelto 2026-09-20 (rama `BloqueF`)._
- [x] **GPTDevTeam.** Suite pytest de **82 tests** sobre `GPTDevTeam_v2.0.py`
  (parser, limpiar_docstring_inicial, AST, sandbox, validadores, memoria),
  sin necesidad de Ollama: se carga el fichero como módulo y se prueban helpers
  puros. De paso se corrigió `limpiar_docstring_inicial`, que no detectaba el
  cierre de un docstring multilínea y devolvía `"""` colgando en el código.
  `requirements-dev.txt` (pytest) creado. En el CI (Linux) se ejecutan 81: uno
  de los tests es de entorno Windows y se descuenta por saltado. _Bloque F.
  Fuente: 2026-09-11 (noche) y 2026-09-18. Resuelto 2026-09-20 (rama
  `BloqueF`)._

## Notas — requieren decisión, no hay tarea definida

- [ ] **`Claude outputs/` en el historial.** Un borrador de entrada y un PDF
  quedaron versionados y salen del `.gitignore`; aunque desindexados, siguen
  descargables por hash mientras no se reescriba la historia de git. _Bloque E
  (decisión, no tarea de código). Fuente: 2026-09-12 (tarde)._

## Stack tecnológico y hoja de ruta de aprendizaje

> _Fuente: `ROADMAP.md` (integrado 2026-09-19; fichero original eliminado)._
> Tecnologías en uso en los
> proyectos del repositorio y las que están en el plan de aprendizaje (marcadas
> como *por aprender*). Listas copiadas tal cual de su documento de origen.

### Backend

- **Java** — Spring Boot, Spring Batch
- **Python** — FastAPI, Flask · Django *(por aprender)*
- **JavaScript / TypeScript** — Node.js, Express.js · NestJS *(por aprender)*
- **C#** — ASP.NET Core *(por aprender)*
- **Rust** — Axum, Actix Web *(por aprender)*
- **PHP** — Laravel · Symfony *(por aprender)*

### Frontend Desktop

- JavaFX, Swing (Java)
- Tkinter, Qt Designer, PyQt/PySide (Python)
- Flutter, Electron *(por aprender)*, Tauri *(por aprender)*, .NET MAUI *(por aprender)*, WPF *(por aprender)*

### Web

- **Frontend UI** — React, Angular · Vue.js *(por aprender)*
- **Meta-frameworks** — Next.js *(por aprender)*
- **Fullstack / SSR** — Blade (Laravel) · Inertia.js *(por aprender)*

### Bases de datos

- **SQL** — PostgreSQL, MySQL
- **NoSQL** — MongoDB

### APIs

- REST, WebSockets · GraphQL, gRPC *(por aprender)*

### DevOps / Herramientas

- Git, Linux, Nginx
- Docker
- Kubernetes *(por aprender)*
- AWS *(por aprender)*
- CI/CD con GitHub Actions *(por aprender)*

### Inteligencia Artificial

- **Frameworks** — PyTorch · TensorFlow *(por aprender)*
- **LLMs** — Ollama · vLLM, llama.cpp *(por aprender)*
- **Orquestación** — LangChain, LangGraph

### Documentación y gestión de proyectos

- Obsidian, Jira, Notion

---

# Historial de mantenimiento del repositorio

Registro de operaciones estructurales sobre el repositorio (no sobre el código
de los proyectos).

---

## Estado de las alertas de seguridad

> **Actualización 2026-08-30.** TaskHub_React es el primer proyecto desplegado
> públicamente y el primero con pipeline de CI propio. Cambia el criterio de
> descarte descrito más abajo: al estar en producción, sus alertas entran en el
> supuesto 1 y ninguna puede descartarse por ser un proyecto experimental.
> Detalle en la sección del 29 y 30 de agosto.

> **Actualización 2026-09-11.** Dos puntos de este estado hay que leerlos con
> reservas. La familia «registro de secretos en claro» tenía un caso vivo en
> TaskHub_Angular —`pino-http` escribía tokens y cookies en el log—, corregido en
> la #92. Y al hacer push, GitHub informó de 44 vulnerabilidades de Dependabot en
> `main`, frente a las 2 que se anotan abajo; estaba sin verificar por API.

> **Actualización 2026-09-19.** Verificadas por la API de GitHub: son **44
> alertas Dependabot abiertas** en `main` (16 high, 22 medium, 6 low), todas
> dependencias transitivas del build. Por ecosistema: **npm 33, pip 8, maven 2,
> composer 1**. Las 8 de pip son todas `torch` de FPS-AI-Toolkit, excluidas a
> propósito (ver `dependabot.yml`). La anotación de «2 abiertas» de abajo era lo
> que quedaba tras el saneamiento de septiembre; el resto son las alertas
> bloqueadas aguas arriba, deliberadamente abiertas. Detalle en la entrada
> fechada `2026-09-19 — Bloque A`.

- **Dependabot:** 44 abiertas (16 high, 22 medium, 6 low), todas dependencias
  transitivas del build —npm 33, pip 8, maven 2, composer 1—. Las de npm/Maven
  sin arreglo disponible (las únicas "correcciones" son retrocesos de versión)
  se dejan abiertas a propósito para que GitHub las cierre cuando la cadena
  actualice; las 8 de pip (`torch`) se excluyen porque el stack se gestiona a
  mano. Detalle: actualización **2026-09-19** de esta cabecera y entrada
  fechada.
- **Secret scanning:** 4 alertas revisadas. Una era real (clave de API de
  Google, revocada y restringida a YouTube Data API v3), dos falsos positivos y una de
  código de terceros ya retirado.
- **Code scanning (CodeQL):** 69 alertas agrupadas en nueve familias de
  problemas, más una décima descubierta después. **246 cerradas, 10 abiertas**
  en el momento de escribir esto, y las 10 corregidas en el último commit a la
  espera de que CodeQL reanalice.

  Las familias abordadas: modo debug de Flask, exposición de información (Java y
  Python), falta de límite de peticiones, path traversal, XSS, criptografía
  débil, CSRF, enlace de sockets, validación de URL y registro de secretos en
  claro.

  **Matiz importante:** las familias se cerraron por grupos de ficheros, no
  siempre por repositorio. Al revisar las 10 restantes aparecieron dos casos de
  «familia dada por cerrada» que seguían vivos en ficheros que no se habían
  mirado: límite de peticiones en `unified-chat-widget` y `JSGameChat`, y
  exposición por excepción en `TestMail.py` y `rumble_server.py`. La lección es
  que **cerrar una familia significa cerrar la lista de alertas de esa familia,
  no garantizar que el patrón no exista en otro sitio**; lo segundo requiere
  buscar el patrón, no fiarse del listado.
- **Credenciales en código:** dos incidentes revisados y corregidos, con todas
  las credenciales afectadas **rotadas o revocadas**. Ninguna era detectable por
  el escáner automático; aparecieron leyendo el código. Los detalles de dónde
  estuvo cada una se omiten a propósito: este historial es público y señalarlos
  equivaldría a señalar los commits anteriores al arreglo.

---

## 2026-09-20 — OmniForge y GPTDevTeam: de 0 tests a 115 + 82

Primer día con las dos suites de Python que faltaban del inventario. El plan era
«añadir tests al portafolio»; una vez más, lo interesante no fue el número sino
lo que apareció al escribirlos.

### OmniForge: 115 tests y un bug de memoria destapado

Tras reescribir su `README.md` a la arquitectura real (planner multi-agente,
`--solo`, 29 tools en 5 módulos, memoria, evaluador, skills, visión), se montó
la suite sobre `pytest` (nuevo `requirements-dev.txt`). Los 115 tests cubren la
lógica pura —planner (`_parse_plan`, prompts), evaluador (fallos, eficiencia,
`analyze_and_generate_hint` con un LLM falso), memoria (límites, dedup,
migración `[HINT]`), skills, fábrica de LLM (solo construcción, sin red),
filesystem, terminal (`_subprocess_fallback`), helpers de visión, config,
estados, y `_build_*_initial_state`/`run()` con fakes— sin tocar LLM, pantalla,
navegador ni red.

El bug: `run()` en `main.py` decidía qué guardar en memoria comparando el
estado final con `{"timeout", "plan_empty"}`, pero `synthesize()` emite
`"error"`/`"done"` — **las tareas fallidas entraban igualmente al historial** y
contaminaban el contexto. Ahora `run()` solo guarda con `status == "done"`
(alineado con el comentario que ya decía «`status="error"` → se omite
`memory.add()`»).

Detalles de la puesta a punto (los tests, rojos primero, destaparon además):
los tools de langchain son `StructuredTool` y hay que invocarlos con
`.invoke({...})`, no como funciones; `Evaluator(eval_dir=":nunca:")` no es
ruta válida en Windows; `CONFIG.agent.verbose` imprime `─` y revienta con
cp1252 en CI (fixture que lo desactiva); y un `__len__` en un fake hizo falsy
la memoria (el objeto era falsy con longitud 0).

### GPTDevTeam: 82 tests y `limpiar_docstring_inicial` arreglado

`GPTDevTeam_v2.0.py` se carga como módulo con `importlib` (el nombre del
fichero tiene un punto) y se prueban helpers puros: parser (`extraer_codigo_puro`,
`extract_json`, `limpiar_docstring_inicial`), heurísticas AST (bucles infinitos,
atributos fantasma, `extraer_api_estatica`, validador de tests vs API), sandbox
de subprocess real, estado/evaluación y memoria JSON. **82 tests, sin Ollama.**

De paso: `limpiar_docstring_inicial` no detectaba el cierre de un docstring
multilínea (`"""\nTexto\n"""`) y devolvía las comillas colgando de la respuesta
del LLM; arreglado. También se confirmó que el orden de `attributes` en
`extraer_api_estatica` no es determinista (viene de un `set`) — el test
compara ordenado.

### Lo que quedó

Las dos suites corren en cada push dentro del job `python-test` de `ci.yml`,
que ahora admite una matriz parametrizada: cada proyecto declara los
`requirements` a instalar y la `ruta_tests` de pytest. OmniForge instala solo
`requirements-dev.txt` (la suite no importa los pesos pesados de
`requirements.txt`: browser-use, playwright, open-interpreter, pyautogui) y
GPTDevTeam necesita `pytest tests` para no recoger `MetaGPT/` vendorizado. El
mínimo declarado para GPTDevTeam es **81**, no 82: su 82.º test
(`test_mantiene_temp_y_perfil_en_windows`) solo corre en Windows y el CI es
Linux, así que se descuenta por saltado. La tabla del inventario pasó a 115 y
81 (CI), y la cifra total del README raíz, a 1.739 (756 en `ci.yml`).

---

## 2026-09-19 — Git: `git subir` blindado, ramas legadas podadas y ToDo con bloques C–G

Sesión de higiene del árbol y de los aliases de git, con el ToDo consolidado
como hilo conductor. El usuario ejecutó los comandos mutadores; el agente solo
los entregó adaptados.

### `git subir` blindado

Al alias se le anteponen dos guardas que lo detienen antes de tocar nada: un
merge en curso (`MERGE_HEAD`) y cambios sin commitear
(`git status --porcelain`). La última línea del alias
(`gh pr merge --"$metodo" --delete-branch --auto`) queda intacta, de modo que el
auto-merge se conserva incluso en el caso «PR cerrado adelante» — es el flujo
que ya probaron los PR #121, #122 y #123. El blindaje y la integración de `main`
en ramas ya fusionadas quedan documentados en `AGENTS.md` (paso 4 del flujo de
git; PR #124).

### Ramas legadas podadas

`Maintenance_upgrade`, `fix_taskhub-angular` y `docs_agentes_v2` se borraron
también en el remoto (`git push origin --delete`), y `UpgradeDoc` en local. Las
cuatro se verificaron libres de contenido que `main` no tuviera: 0 diffs, o
contenido ya integrado por squash (p. ej. el test STOMP vía la #108). Quedan
solo `origin/main` y dos ramas de Dependabot (#55, #57). Aclarado el porqué de
la poda selectiva: `git nueva` solo borra ramas locales cuyo remoto desapareció
(`: gone]`); las legadas no calificaban porque su remota seguía viva, y el
`--delete-branch` del auto-merge ya borra las remotas en el flujo normal.

### ToDo consolidado: bloques C–G

Se etiquetaron los pendientes existentes como Bloques C (`@EntityScan` /
`@EnableJpaRepositories` a persistencia), D (E2E compartiendo BD, usuarios
`e2e-*`), E (`Claude outputs/`, decisión) y F (OmniForge, GPTDevTeam), y se
añadió en «Seguridad y dependencias» el **Bloque G** nuevo: vulnerabilidades
corregibles de npm/Maven con parche (cifras del análisis del 2026-09-19). PR
#123.

### Bloques A y B verificados cerrados

Entradas `[x]` en el ToDo y PRs #118 (Bloque A) y #119/#120 (Bloque B)
integrados en `main`; sin cambios nuevos que añadir.

### `how_to_use_git.md` alineado con el alias final

El bloque `[alias] subir` del documento queda idéntico al instalado (blindaje +
integración con abort limpio), y la guía y los diagramas «camino completo»
están al día. Commiteado en `686fa0c`; la rama `Documentacion-General` queda
lista para `git subir` (PR no creado todavía en el momento del cierre).

---

## 2026-09-19 — TaskHub_React: Bloque B — SHA en el CI, límite por cuenta y `PUT`/`PATCH` (rama `BloqueB`)

Tercer bloque del endurecimiento de TaskHub_React, tres frentes (los nombres
son los de la sesión de auditoría del 2026-08-29/30):

**1. Acciones del CI a SHA completos.** Es la medida pendiente que quedaba en la
ficha de CI/CD de la auditoría. Se sustituyeron todas las referencias por tag
(`@v4`/`@v5`/`@v2`) por su commit SHA completo, verificando cada SHA contra la
API de GitHub (los tags anotados se resuelven al commit real del tag, no a la
etiqueta). Cobertura: `taskhub-react-ci.yml` (`checkout`, `setup-node`,
`upload-artifact`) y `ci.yml` de la raíz (`checkout`, `setup-python`,
`setup-node`, `setup-java`, `shivammathur/setup-php`). Cada workflow lleva un
comentario en la cabecera con la política de pin y cómo actualizar una acción.
Verificado: cero ocurrencias de `uses: …@v*` en `.github/workflows/`. Con esto
se cierra la única tarea pendiente de la ficha CI/CD de la auditoría.

**2. Límite de intentos por cuenta: cerrar la tarea, no el código.** Las capas 2
y 3 del login (`accountSlowDown` + `accountLimiter`, tope duro de 200 por
cuenta) ya estaban implementadas desde el 2026-09-03 (commit `b6d0989`) con sus
tests; el nombre de la ficha de MAINTENANCE («limitación por cuenta además de
por IP») no se había marcado `[x]`. Se verifica mediante el acceso al
`rateLimit.middleware.test.ts` (los tests de duplicación de fichero de la
sesión del 2026-09-12 los avalan) y se cierra como resuelto.

**3. `PUT` como reemplazo completo y `PATCH` como parcial.** Hasta ahora ambos
verbos ejecutaban `update` (parcial), una desviación de la semántica HTTP que la
auditoría denunció. `PUT` pasa a reemplazo completo: exige `title` igual que
`POST` (comparte validador `createTaskValidator` vía el alias
`replaceTaskValidator`) y los campos omitidos vuelven a sus valores por defecto
(`description ''`, `status 'pending'`, `priority 'medium'`); detecta títulos
duplicados excluyendo la propia tarea y devuelve 409, 404 si no existe y 500 si
la escritura no devuelve fila. `PATCH` conserva la semántica parcial (`update`).
Test-first: unitarios en `tasks.validation.test.ts` (4 nuevos),
`tasks.service.test.ts` (10 nuevos) y `tasks.controller.test.ts` (2 casos en
`it.each` ya existentes), y 5 comprobaciones nuevas en `verify.ts` dedicadas a
`PUT` con una tarea propia. El playground (`public/app.js`) ya enviaba los
cuatro campos en `PUT`, así que es compatible con la semántica nueva.

**Cifras tras el bloque:** 983 comprobaciones (564 unitarios de servidor —de 548—
, 224 de cliente, 159 de API contra PostgreSQL —de 154— y 36 de navegador).
Cobertura de servidor 99,61 / 98,87 / 98,87 / 99,58, sobre los umbrales
99/98/98/99. README raíz, README del proyecto y AUDITORIA alineados. Funciones
de `tasks.service.ts` al 90 % en la métrica de cobertura: se deja así porque el
98 % se mide sobre el proyecto; no se expande la tarea.

## 2026-09-19 — Bloque A de mantenimiento (rama `UpgradeDocs`)

Primera ejecución del comando `/NewTask` (renombrado ese mismo día desde
`/NewProject`, PR #116). Se abordan las tres tareas rápidas sin riesgo de la
priorización:

1. **README de TaskHub_Angular actualizado.** La suite se ejecutó en local y
   dio **103 tests frontend** (antes «99» en el README del proyecto; el mínimo
   del CI ya era 103). Se actualizaron también las cifras por carpeta
   (dashboard 15 → 17, projects 42 → 44) y el backend (162 → **175**, para
   reflejar los 13 tests contra PostgreSQL real que estaban fuera del bucle de
   `npm test`, contados solo en CI).
2. **44 vulnerabilidades verificadas por API de GitHub.** El 2026-09-11 el push
   avisaba de «44 vulnerabilities on the default branch» sin verificar. Son
   **44 abiertas (16 high, 22 medium, 6 low)**, todas transitivas del build,
   por ecosistema **npm 33, pip 8, maven 2, composer 1**. Los paquetes con
   varias: `qs` (8), `torch` (8), `fast-uri` (4), `@angular/*` (5),
   `hono`/`vitest`/`@vitest/mocker`/`brace-expansion`/`extract-zip`/
   `js-yaml` (2 c/u). Sin parche disponible aguas arriba: `extract-zip` (2) y
   `torch <= 2.6.0` (3).
3. **Dependabot (pip) saneado.** Las 8 alertas pip son todas `torch` de
   `FPS-AI-Toolkit` (`requirements.txt`, fijado `2.6.0+cu124`), y
   `dependabot.yml` las excluye a propósito desde el 2026-09-03: el stack de
   PyTorch se gestiona a mano con el índice CUDA (`pip install --index-url
   https://download.pytorch.org/whl/cu124`), donde Dependabot solo propondría
   versiones de PyPI que romperían la compilación CUDA o dejarían el proyecto en
   CPU. La fila del README raíz pasa de «En curso» a «Saneado».

Cambios: README del proyecto (cifras de tests) y fila Dependabot (pip) del
README raíz.

---

## 2026-09-19 — Comandos de opencode y MCP de GitHub (rama `CommandsOpenCode`)

Para agilizar el mantenimiento del repo se añaden seis comandos de opencode
de proyecto en `.opencode/command/`:

- `/CierreSesion` — cierra la sesión: resume cambios, añade la entrada fechada
  en `MAINTENANCE.md`, marca `[x]` las tareas del ToDo consolidado y consolida
  en `AGENTS.md` el comportamiento/conocimiento del agente (es el responsable
  directo de la memoria persistente del agente).
- `/VerificarDocs` — auditoría de coherencia de la documentación (enlaces,
  Markdown, contradicciones, duplicidades, fuentes de verdad). Audita **siempre**
  los documentos raíz, incluidos `MAINTENANCE.md` y `AGENTS.md`, aunque se
  solape con el trabajo de `/CierreSesion`; **solo audita e informa** y no
  modifica documentos salvo petición explícita. Variante autorizada
  `/VerificarDocs_Validado` que aplica las correcciones.
- `/EstadoRepo` — fotografía del estado del repo (rama, git status, commits,
  ramas, PRs, ToDo, última entrada); solo lectura.
- `/NewTask <rama>` — protocolo de una nueva tarea: entrega `git nueva <rama>`
  (la rama la crea el usuario), recopila requisitos y espera confirmación de
  que la rama está creada antes de programar; al terminar el desarrollo valida
  lo que aplique y entrega `git subir` (no recibe rama, sino el método de
  integración). El agente **nunca** crea la rama ni hace push.
- `/Write` — comando real de opencode: registra durante la conversación el
  comportamiento/conocimiento del agente relevante para que `/CierreSesion` lo
  consolide en `AGENTS.md` y `MAINTENANCE.md` (la memoria persistente de la
  sesión es competencia de `/CierreSesion`). Variantes por argumento: `/Write`
  (a criterio), `/Write message` (solo el mismo mensaje), `/Write chat` (toda
  la conversación). Confirmación: ✅ INFO updated.
- `/Technical` — comando real de opencode (la vía `/Activate.Command(...)` se
  documentó de forma incorrecta y se eliminó): análisis profundo y riguroso,
  investigación intensiva, búsqueda web si hay herramientas, razonamiento
  prolongado, detalle muy alto.

El MCP de GitHub (hosted, solo-lectura) queda configurado en
`.opencode/opencode.json` con `GITHUB_TOKEN` del entorno; no da rama ni push al
agente. **Actualización 2026-09-19:** `GITHUB_TOKEN` definido en `$PROFILE` (vía
`gh auth token`), opencode reiniciado —MCP y comandos cargados— y el PR #113
fusiona esta rama en `main`.

---

## 2026-09-19 — RadioStack: los GET bajo `/api/v1`, documentados con un test

Cierra el pendiente anotado el 12 de septiembre. La regla
`GET /api/v1/** -> permitAll` existe en `SecurityConfig` (pensada para la parrilla
y los programas, información para los oyentes) y ya estaba documentado su caso
incómodo, `/api/v1/auth/me`, pero no había ninguna prueba positiva de un GET de
catálogo: el chat la tenía, la parrilla no.

`SecurityConfigTest.la_parrilla_se_puede_leer_sin_token` atraviesa la cadena de
filtros de verdad con MockMvc —sin identidad, como un oyente anónimo— contra
`ParrillaController`, el destinatario citado por la propia regla. Ahora el primer
GET de catálogo que deje de ser público es el test que lo delata, no un
incidente.

**Sin tocar producción**: solo el test y el recuento. Total 165 → **166**
(api 129 → 130) y `minimo: 166` en `ci.yml`. Es además una tercera rodaja
`@WebMvcTest` (con `ChatController`, `AuthController` y ahora `ParrillaController`
traídos por `@Import`), de modo que sigue sin arrancar la aplicación ni pedir
PostgreSQL.

---

## 2026-09-19 — RadioStack: el chat por STOMP, de punta a punta con `@SpringBootTest`

Cierra el pendiente anotado el 12 de septiembre. El chat por WebSocket STOMP
tenía tests del interceptor (`StompAuthChannelInterceptorTest`) y del
controlador con dobles, pero nadie había atravesado el camino entero contra un
servidor real: CONNECT con token, suscripción al tópico de una emisión, SEND
que se guarda en la base y se difunde con el alias del token, y los rechazos.

`ChatStompEndToEndTest` levanta la aplicación con `WebEnvironment.RANDOM_PORT`
y entra por un `WebSocketStompClient` real (Spring 6.1 tenía ya en el classpath
`spring-websocket`, `spring-messaging` y `tomcat-embed-websocket`; no hizo falta
tocar el `pom`). Tres pruebas:

1. **Enviar con token** guarda el mensaje en `chat_message` y lo difunde al
   tópico con el alias del token (`lucia@radiostack.com`), no con el que dice el
   cuerpo.
2. **Leer sin token** está permitido: un oyente anónimo suscrito recibe la
   difusión de un autor autenticado.
3. **Enviar sin token** se rechaza en el interceptor y **no queda nada** en el
   historial.

### Sin tocar producción

El test pasó contra el código de producción tal como estaba: no se cambió una
sola línea de `src/main`. Que el SEND sin token no deje rastro no es algo que
haya que arreglar, es el comportamiento existente, y ahora está demostrado de
punta a punta. El interceptor corta la trama en el `clientInboundChannel`
**antes** de que el controlador llegue a ejecutarse, de modo que
`chatService.enviarMensaje` ni se invoca. La comprobación explícita de
`Authentication` dentro de `ChatWebSocketController.enviar`, que está ahí "por
si esa política cambiase" (así lo dice su comentario), quedó cubierta por el
test 1, que afirma que el alias sale del token.

### Cuatro lecciones del recorrido, que pagaron la sesión

- **El broker simple no manda RECEIPT para SUBSCRIBE.** Se intentó sincronizar
  la suscripción por receipt y el test colgaba: en
  `SimpleBrokerMessageHandler` el SUBSCRIBE solo registra el destino, no
  responde. Se sustituyó por un asentamiento de 300 ms con el comentario que
  explica por qué.
- **El canal entrante es multi-hilo**, y el orden suscripción/emisión no está
  garantizado ni en la misma conexión: el `clientInboundChannel` de Spring usa
  un `ThreadPoolTaskExecutor` con core igual a 2×núcleos. El asentamiento de
  arriba cubre esa carrera, no la mala voluntad del broker.
- **`MappingJackson2MessageConverter` desconoce `java.time`.** Con el convertidor
  por defecto, el MESSAGE con `timestamp` (`LocalDateTime`) llegaba y la
  conversión a `ChatMessageDTO` fallaba en silencio con
  `MessageConversionException`. Se registró `JavaTimeModule` en un `ObjectMapper`
  propio. De paso, `ConcurrentTaskScheduler()` estaba deprecado en Spring 6.1:
  el cliente usa un `ThreadPoolTaskScheduler` compartido.
- **Los tests con servidor real no pueden fiarse de `@Transactional`** para
  limpiar: los hilos del broker no viven en la transacción del test, así que
  `@AfterEach` borra las filas con el marcador único que genera cada test.

### Cifras

- api: 126 → **129** tests. RadioStack: **162 → 165**, mínimo de CI
  actualizado en `.github/workflows/ci.yml`.
- Ya son **10** los tests que arrancan el contexto completo contra PostgreSQL
  (7 de `EsquemaYMigracionesTest` + 3 de `ChatStompEndToEndTest`), todos detrás
  de la misma marca `RADIOSTACK_DB_TESTS` para entrar y salir juntos del
  recuento del CI. El javadoc de `EsquemaYMigracionesTest` se actualizó en
  consecuencia (ya no es «el único» de RadioStack que toca una base de datos).
- Sin la marca, el recuento baja de 165 a 155, y el paso de comprobación del
  workflow lo detecta.

---

## 2026-09-18 — TaskHub_Angular: los cuatro comportamientos pendientes de la #90

La sesión anterior terminó con el frontend de Angular en 261 tests y cuatro
comportamientos anotados como «encontrado y no arreglado»: los límites
silenciosos de 20 tareas y 10 proyectos, el error de carga mudo del dashboard y
la longitud mínima de 2 caracteres que los botones de creación ignoraban. Esta
sesión los cierra, todos comprobados con tests escritos de antemano.

### La decisión sobre los límites

Las dos pantallas afectadas son panorámicas: un tablero kanban y un panel de
proyectos, ninguna con paginación ni contador. Pedir menos de lo que hay
esconde el resto sin avisar. La decisión fue explícita y la mínima posible:

- `TaskService.listByProject` manda ahora `limit: 100`, el máximo que acepta el
  validador del backend (`listTasksSchema`, `.max(100)`). El tablero deja de
  recortarse a 20 por defecto.
- El dashboard pide `listProjects(1, 100)`. El *default* del servicio sigue
  siendo 10 (los tests lo fijan desde la #93); solo cambia la llamada del panel.
  El endpoint de proyectos no valida el `query`, así que 100 llega igual; se usa
  el mismo tope para no inventar una cifra nueva por pantalla.
- No se toca el contrato de la API: el backend sigue devolviendo `Task[]` /
  `Project[]` planos. Cambiarlo a `{ data, total, … }` habría resuelto el aviso
  de truncamiento, pero ampliaba el alcance a backend, prueba y los 261 tests
  por el camino; con 100 de tope, el corte cae en un caso que un kanban
  personal no alcanza.

### Qué se cambió, y cómo se comprobó

Cada comportamiento nuevo se escribió como test antes del código. Ese primer
paso dejó el build en rojo por una razón distinta de la esperada —el spec usa
`loadError`, que el componente aún no tiene—, lo que confirmó de paso que el
comportamiento no existía: el compilador no deja mentir sobre si un campo está.

| Comportamiento de #90 | Cambio | Test |
|---|---|---|
| Tablero cortado a 20 tareas | `listByProject` manda `limit: 100` | `task.service.spec` fija `limit=100` |
| Dashboard cortado a 10 proyectos | `listProjects(1, 100)` en `loadProjects` | `dashboard.component.spec` fija `page=1&limit=100` |
| Error de carga mudo | campo `loadError`; «No se pudieron cargar los proyectos» distinto de «No tienes proyectos aún» | nuevo: flush 500 → dice el error y no el vacío |
| Botones habilitados con 1 carácter | `[disabled]="name.trim().length < 2"` y lo mismo para el título | nuevo: «Crear» no cierra con 1 carácter y sí con 2 |
| «No se pudo crear» genérico | el aviso muestra el `{ message }` del validador (con respaldo al texto genérico) | `dashboard.spec` espera «nombre corto»; nuevo en `project-detail.spec` espera el motivo del 400 |

De paso, `error: () => (this.projects = [])` se sustituye por marcar el error
sin vaciar la lista: una recarga fallida ya no borra lo que había en pantalla.

### Lo que costó

- 99 → **103 tests** en el frontend (4 nuevos, todos en rojo antes del código).
- `node_modules` ya estaba instalado; los tests corrieron en local con
  `ng test`, sin el rodeo del clon en la nube.
- El mínimo de CI del frontend sube de 99 a **103**, como pide el propio
  workflow (`::notice::` cuando el mínimo se queda atrás).

### Pendiente

- **CV:** las dos variantes dicen **71 tests** para TaskHub_Angular; el mínimo
  de CI ahora es **162 + 103 = 265**. Además dicen **Angular 19**, y el
  `package.json` declara `@angular/core` `^21.2.19`.
- **Vulnerabilidades:** las 44 notificadas por GitHub al hacer push siguen sin
  verificar por la API (el estado de la cabecera dice 2 de Dependabot).
- **RadioStack:** el pendiente de la entrada del 12 de septiembre. El entorno de
  la nube no ejecuta Java (Maven Central y `binaries.prisma.sh` bloqueados), así
  que el runner será el CI sobre una PR borrador.
- **OmniForge y GPTDevTeam**, sin empezar.

---

## 2026-09-12 (tarde) — Un fichero que nunca existió, y dos agujeros que se taparon entre ellos

Esta sesión empezó cerrando los huecos de cobertura que había dejado la anterior
y terminó descubriendo que la PR que los cerraba **nunca llegó a aplicarse**. El
episodio es el más instructivo del historial reciente, porque no falló ningún
paso: ni el `mv`, ni el `git add`, ni el CI. Todo salió en verde y nada de lo que
decía que se había comprobado se comprobó.

### El fichero que nunca existió

La PR #99 tenía que modificar `.github/workflows/ci.yml`. Lo que hizo fue crear
un fichero nuevo en la raíz del repositorio llamado `.githubworkflowsci.yml`, de
33.772 bytes, idéntico byte a byte al contenido que debía ir al workflow.

La causa está en el comando que se ejecutó:

```
mv ci-nuevo.yml .github\workflows\ci.yml
```

Con barras invertidas, en Git Bash. La barra invertida es allí un carácter de
escape: `\.` es `.` y `\w` es `w`. Bash no vio una ruta con directorios, vio **un
único nombre de fichero** con los separadores comidos, y `mv` hizo exactamente lo
que se le pidió. El error no fue de quien lo tecleó, fue de quien redactó el
comando: una ruta de Windows en una orden destinada a un intérprete POSIX.

### Los dos agujeros que se taparon mutuamente

La consecuencia no fue cosmética, y merece leerse despacio porque es un patrón
que se repetirá.

`EsquemaYMigracionesTest` está anotado con
`@EnabledIfEnvironmentVariable(named = "RADIOSTACK_DB_TESTS")`. Esa variable la
define el bloque `env:` del workflow, que se quedó en el fichero fantasma. Sus 7
tests, por tanto, **se saltaron en el CI** igual que se saltan en un portátil sin
base de datos.

Y el contador de tests del job de Java —el suelo que existe precisamente para
detectar cobertura que desaparece— **los contó igual**, porque Surefire escribe
un elemento `<testcase>` para un test saltado exactamente igual que para uno
ejecutado, con un `<skipped/>` dentro. El recuento dio 155 + 7 = 162 frente a un
mínimo declarado de 155: por encima del suelo, aviso en lugar de fallo.

Los dos defectos se anulaban el uno al otro. El descuento de saltados habría
delatado que faltaba la variable; la variable habría hecho irrelevante el
descuento. Al perderse los dos a la vez, el CI informó de un éxito que no
existía: **una PR verde en la que Flyway no aplicó una sola migración.**

La lección, escrita sin adornos: *un suelo de tests que cuenta lo que no se
ejecuta no es un suelo, es una decoración*. Y un umbral que solo puede
sobrepasarse nunca avisa de nada.

### Los tres contadores que tenían el mismo agujero

Arreglado el de Java, quedaba comprobar si los otros compartían el defecto. En
lugar de suponerlo, se midió: se escribió un fichero de prueba con un
`describe.skipIf` y se miró el XML que produce vitest.

```xml
<testcase name="grupo entero saltado &gt; uno" time="0">
    <skipped/>
</testcase>
```

Idéntico a Surefire. Pasado ese XML por el contador que había —3 casos, 2
saltados— devolvía **3**; por el contador nuevo, **1**.

Los tres contadores (Node, PHP y Python) pasan a descontar los saltados, con la
misma regla que ya usaba el de Java: contar elementos `<testcase>` y restar los
que llevan un `<skipped>` dentro. El de Python cambia además de método: sumaba el
atributo `tests=` de cada `<testsuite>`, que incluye los saltados y además
depende de cómo anide el XML cada herramienta.

Esto no era higiene. El diseño de los tests nuevos de TaskHub_Angular **depende**
de ello: si `TASKHUB_DB_TESTS` dejara de llegar al job, sus 13 tests se
saltarían, el contador viejo los sumaría y el CI volvería a dar por buena una
comprobación que no se hizo. Con el descuento, el total baja de 175 a 162 y el
job falla.

### Lo que un doble no puede comprobar, por definición

El hueco era el mismo en los dos proyectos: **ningún test tocaba nunca una base
de datos real ni ejecutaba una migración.**

En TaskHub_Angular, los 162 tests del backend doblan `config/prisma`, así que
ninguno lanzaba una sola consulta. Comprobaban que el código llama a Prisma con
los argumentos correctos; nunca que esos argumentos produzcan el resultado
correcto. Son dos preguntas distintas y la segunda solo la contesta una base de
datos. La migración `20260704180530_init` no se ejecutaba en ninguna parte del
CI: una migración rota habría pasado entera.

`db.repositories.test.ts` añade 13 tests que cubren lo que un doble no puede
cubrir **por definición**, porque un doble no tiene restricciones:

- que las seis tablas existan, comprobadas **por nombre**: una migración futura
  que se dejara una sin crear se aplicaría sin error y el fallo saldría en la
  primera petición que la usara;
- que los valores por defecto los ponga la base y no el código;
- que el email único y el par (proyecto, usuario) único estén **en el esquema** y
  no solo en la comprobación previa del servicio —esa comprobación no cubre dos
  altas simultáneas; la única defensa real es el índice—;
- que las cascadas las ejecute PostgreSQL. Importa por seguridad y no solo por
  limpieza: un *refresh token* que sobreviviera a su usuario sería una credencial
  huérfana con siete días de vida por delante;
- y que el filtro `visibleTo` de `taskRepository.findMany` se traduzca a un SQL
  correcto. Ese filtro es el que cerró el IDOR de `/api/tasks`, y hasta ahora
  solo estaba comprobado sobre la *forma* de un objeto `where`, que es justo lo
  que ya se sabía. Ejecutado contra PostgreSQL, el log lo confirma: el filtro de
  proyecto se combina con `AND`, no sustituye al de visibilidad.

En el lado del CI, el job de Node levanta `postgres:17-alpine`, aplica las
migraciones con `prisma migrate deploy` y comprueba la deriva con
`prisma migrate diff --exit-code`. Esto último es el equivalente exacto del
`ddl-auto: validate` de Hibernate que usa RadioStack: compara lo que describe
`schema.prisma` con lo que las migraciones han dejado en la base. Existe porque
los dos pueden separarse sin que nadie se entere —se añade un campo al modelo, se
olvida `prisma migrate dev`, y el cliente generado pide una columna que no
existe—, y con dobles eso no se ve nunca.

### Un seguro que no estaba previsto

Los tests vacían las seis tablas antes de cada test. Leyendo el `.env.example`
apareció que la base de desarrollo del proyecto se llama `taskmanager`: bastaba
con exportar `TASKHUB_DB_TESTS=true` teniendo el `.env` cargado para vaciarla sin
aviso y sin vuelta atrás.

El fichero lleva por eso un `beforeAll` que se niega a arrancar si la base no se
llama `taskhub_ci` o `taskhub_test`, y aborta antes de tocar una fila. Es un
accidente de un solo comando y de efecto irreversible; seis líneas para
descartarlo salen baratas.

### `Claude outputs/`, o cómo se cuelan las cosas

Al preparar el `.gitignore` de esa carpeta apareció que **ya tenía dos ficheros
versionados**: un borrador de entrada de este mismo fichero (PR #94) y un PDF
(PR #97). Ninguno de los dos estaba destinado a versionarse.

El mecanismo es mundano: la aplicación de escritorio guarda ahí lo que se
descarga del chat, y la carpeta cae dentro de la carpeta conectada a la sesión,
que en este caso es la raíz del repositorio. A partir de ahí, `git add -A` hace
el resto.

Dos consecuencias prácticas. La primera es que `.gitignore` **no hace nada sobre
ficheros ya versionados**: hay que desindexarlos explícitamente con
`git rm --cached`. La segunda, más incómoda: `git rm --cached` tampoco los quita
del historial, y en un repositorio público eso significa que siguen siendo
descargables por su hash mientras el historial no se reescriba.

### Lo que cambia en el método de verificación

Tres reglas, las tres nacidas de un error concreto de esta sesión.

1. **Nunca una ruta con barra invertida en un comando destinado a bash.** Solo
   barras normales, que funcionan en `cmd`, en PowerShell y en bash por igual.

2. **El punto de control verifica el estado final, no la operación.** Pedir un
   `git diff --stat` después de mover un fichero no demuestra que el fichero
   correcto haya cambiado. Lo que se hace ahora es comprobar una cadena que solo
   existe en el contenido nuevo, en la ruta donde debe estar, y para ficheros
   completos una huella `sha256` que no admite interpretación.

3. **Antes de cada commit se lee el `git status --short` entero**, y se nombra
   cualquier línea que cuelgue de la raíz del repositorio en vez de mirar solo si
   están los ficheros esperados.

Y una cuarta que no es de método sino de honestidad: de esta sesión, lo único que
no pudo ejecutarse en ningún entorno intermedio fue `prisma migrate diff`, porque
el host de los motores de Prisma está bloqueado por la política de salida. Se
entregó marcado como no verificado y se ejecutó en local antes de commitear
—`No difference detected`, código 0—. Lo que no se ha ejecutado se dice, no se
supone.

---

## 2026-09-12 — RadioStack: de 2 tests a 121, y un 500 en todos los endpoints con id

RadioStack empezó la sesión con dos tests y la terminó con 121. Por el camino
aparecieron tres defectos que ninguno de los tests que ya existían podía haber
encontrado, y dos lecciones sobre el propio CI que costaron más tiempo que el
código.

La última es la que más dice: **todos los endpoints de la API con un
identificador en la URL devolvían 500**, y llevaban así desde que se montó el
proyecto. Lo encontró el primer test que atraviesa el `DispatcherServlet` de
verdad, en su primera ejecución válida.

### El punto de partida

El día anterior RadioStack pasó del job «Java · compilar» —que ejecuta
`mvn -DskipTests compile` y por tanto no ejecutaba nada— al job de tests, con su
`LocutorTest` de 2 tests. Esa era toda la cobertura de un proyecto multimódulo
con autenticación JWT, WebSocket con STOMP, chat en directo y cinco
controladores REST.

El encargo fue: autenticación y WebSocket del chat primero, y una cobertura
decente después.

### Tanda 1: 96 tests, y un token que autenticaba a medias

Diez clases nuevas en `radiostack-api`: `JwtService`, `JwtAuthenticationFilter`,
`StompAuthChannelInterceptor`, `AuthController`, `ChatWebSocketController`, los
cuatro servicios y el mapeador de DTO.

El primer defecto salió del test `un_token_bien_firmado_sin_email_ni_rol_se_descarta`.
`UsuarioAutenticado` se construía así:

```java
try {
    return new UsuarioAutenticado(Long.parseLong(claims.getSubject()), email, rol);
} catch (NullPointerException ex) {
    return null;
}
```

Ese `catch` no se ejecutaba nunca. `claims.get("email", String.class)` devuelve
`null` en vez de lanzar, y un `record` acepta nulos sin protestar. Un token
firmado pero sin claims autenticaba con email y rol a `null`, y con la autoridad
literal **`ROLE_null`**: una identidad a medias que ninguna regla por rol
reconocería, y que en el chat habría firmado los mensajes como «null».

No era explotable desde fuera, porque solo el servidor puede firmar. Era algo
peor de otra manera: una defensa escrita que no defendía, y que cualquiera que
leyera el código habría dado por buena.

Se sustituyó por una factoría que valida de verdad —`sub` numérico, email y rol
no vacíos— y que usan **las dos puertas**, el filtro HTTP y el interceptor de
STOMP, para que acepten exactamente los mismos tokens.

### El contador de Surefire: tres ejecuciones en rojo por 13 tests

El job de Java declara un mínimo de tests y falla si el número baja. Con los 96
nuevos el total era 98, y el CI insistía en que se habían ejecutado **85**.

`mvn test` terminaba en `BUILD SUCCESS`. El log demostraba que los tests
anidados se ejecutaban. Los informes locales estaban bien formados. Y repitiendo
la tubería exacta del CI sobre esos informes reales, el recuento salía correcto.
Tres intentos de reproducirlo fallaron.

Lo que lo cerró fue cambiar el paso para que **imprimiera el desglose por
fichero**, en vez de una sola cifra que no se puede depurar:

```
  13  ./radiostack-api/target/surefire-reports/TEST-…CatalogoServiciosTest.xml
```

Un solo informe, con 13 elementos `<testcase>` dentro. No existían los ficheros
`…CatalogoServiciosTest$Programas.xml` que sí estaban en local. Surefire escribe
**un informe por clase de primer nivel**, y en la cabecera `<testsuite tests="N">`
pone solo los tests *propios* de esa clase. Con `@Nested`, la clase externa no
tiene ninguno: el atributo dice `0` mientras los 13 `<testcase>` de las clases
anidadas están dentro del mismo fichero.

**La lección: el atributo `tests=` de Surefire no cuenta lo que parece.** Hay que
contar elementos `<testcase>`, que es uno por test ejecutado, sea cual sea la
forma del árbol. Es el mismo criterio que ya usaban los jobs de Node y PHP; el de
Java era el único que sumaba el atributo.

La segunda mitad de la lección es de método: cuando algo no se reproduce, el
siguiente paso no es otra hipótesis, es **hacer que el sistema diga lo que ve**.
El desglose por fichero resolvió en una ejecución lo que tres conjeturas no
habían resuelto.

### Un commit a medias, y un `git diff --stat` que nadie miró

Entre medias se perdió media hora por una tontería evitable. El arreglo del
contador se entregó como parche para `git apply`, porque `.github/workflows/` no
se puede escribir desde la herramienta. El commit resultante llevaba el mensaje
largo y correcto… y **una sola línea cambiada**: la del mínimo. El trozo del
contador nunca entró.

La receta incluía un `git diff --stat` precisamente para cazar eso, y no sirvió
de nada porque nadie miró el número. Desde entonces los cambios sobre el
workflow se entregan como **fichero completo** —`mv fichero .github/workflows/ci.yml`—
en vez de como parche, y con un alto explícito antes de commitear.

### Tanda 2: la segunda puerta del chat

`ChatWebSocketController` ya tomaba el alias del token verificado en el CONNECT
de STOMP; esa suplantación se había cerrado en su día. Pero el chat tiene dos
puertas, y la otra seguía así:

```java
String alias = body.getOrDefault("alias", "Anónimo");
```

`POST /api/v1/emisiones/{id}/chat` leía el alias del cuerpo de la petición.
Cualquier usuario con cuenta válida podía enviar
`{"alias": "locutor@…", "contenido": "…"}` y el mensaje quedaba firmado con el
email de otro. Se guardaba en el mismo `ChatService`, sobre la misma emisión, y
se difundía por el mismo `/topic`: los oyentes no podían distinguirlo de uno
legítimo. Y era la puerta más cómoda de las dos, porque un POST no necesita
cliente de WebSocket.

**Cuando un recurso tiene dos entradas, la política de identidad se arregla en
las dos a la vez o no se arregla.** Tapar una y dejar la otra abierta no reduce
el riesgo: lo esconde.

### El primer test que levanta Spring, y lo que encontró a la primera

Hasta aquí, todos los tests de RadioStack construían con `new` la clase que
probaban. Las reglas de `SecurityConfig` no se pueden probar así: no son un
método al que llamar, son el comportamiento de la cadena de filtros. Así que
`SecurityConfigTest` usa `@WebMvcTest` y atraviesa el `DispatcherServlet` real.

Costó dos intentos, y los dos fallos fueron informativos.

**Primero: `@EnableJpaRepositories` no es autoconfiguración.**
`RadiostackApiApplication` lleva `@EntityScan` y `@EnableJpaRepositories` como
anotaciones directas. `@WebMvcTest` apaga la autoconfiguración, pero no puede
apagar esas: se ejecutan igual, Spring Data registra los 6 repositorios y todos
piden un `entityManagerFactory` que en una rodaja web no existe. El contexto ni
arrancaba. Se resolvió dándole al test su propia clase raíz
`@SpringBootConfiguration` sin escaneo de componentes, con las clases de
producción traídas una a una por `@Import`.

**Y después, el hallazgo de la noche.** Con el contexto ya en pie, cuatro tests
—justo los que llegaban a ejecutar un método de `ChatController`— fallaron con:

```
Name for argument of type [java.lang.Long] not specified,
and parameter name information not available via reflection.
Ensure that the compiler uses the '-parameters' flag.
```

`@PathVariable Long emisionId` no dice su nombre entre paréntesis. Spring lo
resuelve por reflexión, y ese nombre solo está en el `.class` si javac compiló
con `-parameters`. Sin la bandera, en el bytecode el parámetro se llama `arg0` y
Spring no puede casarlo con `{emisionId}` de la ruta: excepción al despachar,
que el cliente ve como un **500**.

No es solo el chat. Son **11 métodos en 5 controladores**: el chat, los
comentarios, los programas, el activar y desactivar de locutores y el obtener
una emisión. Es decir, **todo endpoint de RadioStack con un identificador en la
URL**. Solo funcionaban los que no llevan variable de ruta.

Estaba así desde el principio, y el motivo es de manual: el proyecto **no hereda
de `spring-boot-starter-parent`**, solo importa su BOM de versiones, y define el
`maven-compiler-plugin` a mano con `source` y `target` y nada más. `-parameters`
es una de las cosas que ese padre configura por defecto. Al montar el `pom` a
mano se quedó fuera, y como ningún test levantaba la capa web, nada lo delató
durante meses.

El arreglo es una línea en el `pom` padre:

```xml
<parameters>true</parameters>
```

La alternativa —escribir `@PathVariable("emisionId")` en los 11 sitios—
funcionaría igual, y deja la trampa puesta para el método número 12.

**La lección, y es la más cara de la sesión:** 98 tests que llaman a los métodos
directamente no prueban que la aplicación funcione. Prueban que las clases
funcionan. Todo lo que hay *entre* la petición HTTP y el método —resolver
argumentos, aplicar filtros, decidir el código de estado— se quedaba sin probar,
y ahí es exactamente donde estaba el fallo. Un solo test que atraviesa la cadena
real vale, para esto, más que cien que la rodean.

### Lo que queda anotado y sin hacer

- **Los GET públicos bajo `/api/v1`.** La regla está pensada para la parrilla y los
  programas, que son información pública. Pero alcanza a *todos* los GET de la
  API, incluido `/api/v1/auth/me`. Hoy no se escapa nada porque `AuthController`
  comprueba el principal y se defiende solo. El riesgo es el GET que alguien
  añada mañana bajo `/api/v1` dando por hecho que está protegido. Queda
  **documentado con un test** que falla si se decide restringir la regla, en vez
  de cambiada por iniciativa propia: qué es público en esta API es una decisión
  de producto.
- **`@EntityScan` y `@EnableJpaRepositories`** deberían vivir en una
  configuración del módulo de persistencia, no en la clase de arranque de la API.
  Resolvería de raíz el problema de las rodajas y de paso quitaría a la API el
  conocimiento de los paquetes internos de otro módulo. Es cambio de producción
  y merece su propio PR.
- **Un test STOMP de punta a punta** con `@SpringBootTest` sigue pendiente.
  Necesita una historia de base de datos, porque las migraciones de Flyway son
  específicas de PostgreSQL.

### Cifras

| | Antes | Después |
| --- | --- | --- |
| Tests de RadioStack | 2 | **121** |
| Clases de test | 1 | 13 |
| Defectos de producción corregidos | — | 3 |
| Endpoints que devolvían 500 | 11 | 0 |

Los tres defectos —`ROLE_null`, la suplantación por REST y el `-parameters`—
tienen algo en común: **ninguno lo había señalado CodeQL, Dependabot ni el
escaneo de secretos**. Los tres aparecieron escribiendo tests que comprueban el
efecto y no el estado, y el más grave de los tres solo era visible atravesando la
aplicación de verdad.

---

## 2026-09-11 (noche) — TaskHub_Angular: de cubrir pantallas a tres fallos de seguridad

La tarde terminó con el frontend de Angular en 41 tests. La noche empezó con la
idea de cubrir las dos carpetas que faltaban y acabó en cuatro PR (#90 a #93),
tres de ellas con código de producción: al probar por el efecto, y no por el
estado, los tests fueron destapando fallos que ninguna revisión había visto.

| PR | Qué | Tests en CI |
|---|---|---|
| #90 | Frontend: `features/dashboard` y `features/projects` | frontend 41 → 84 |
| #91 | Backend: autorización de tareas por rol y tests de la capa HTTP | backend 71 → 145 |
| #92 | Backend: tokens y cookies fuera del log de peticiones | backend 145 → 148 |
| #93 | Pantalla para añadir miembros a un proyecto | backend 148 → 162, frontend 84 → 99 |

TaskHub_Angular pasa de 112 a **261 tests** en CI.

### Antes de empezar: un conflicto que ya no existía

La sesión arrancó con una indicación de estado: rama con un conflicto pendiente
en `ci.yml`, a resolver con `git rebase origin/main` y `push --force-with-lease`.
Leer el `.git` lo desmintió. El reflog terminaba en `rebase (finish)`, no había
`rebase-merge/` ni `MERGE_HEAD`, la #88 ya estaba en `main` y el `ci.yml` local
era idéntico byte a byte al del remoto. El *force-push* habría recreado una rama
muerta o lo habría rechazado el *lease*.

Y `git nueva` tal cual también habría fallado: el `main` local era anterior a la
#86, que toca `MAINTENANCE.md`, y ese fichero estaba modificado sin commitear.
Se resolvió con `git stash` → `git nueva` → `git stash pop`. Es el cuarto caso
de «anotado como hecho sin estarlo» de esta lista, esta vez sobre el estado de
git: una descripción de hace una hora tampoco se verifica sola.

### #90 — Frontend: tres cosas que no se ven leyendo los tests

43 tests nuevos. Además de la regla de montaje de la tarde (servicio real más
espía), tres detalles:

- **Navegar de verdad en vez de falsificar la ruta.** `ProjectDetailComponent`
  se monta con `RouterTestingHarness` sobre `/projects/p1`, sin ningún doble de
  `ActivatedRoute`. Un doble con solo `snapshot.paramMap` es justo el tipo de
  doble incompleto que rompe a un tercero, y así el id sale de la URL por el
  mismo camino que en producción.
- **El test de reordenar vio un PUT que la aplicación no hace.** El ayudante que
  simula soltar una tarjeta creaba dos objetos contenedor distintos para la misma
  columna, y el componente decide «misma columna» comparando contenedores por
  identidad (`previousContainer === container`). El fallo era del test, no del
  componente; se habría quedado como una falsa alarma sin leer el mensaje.
- **Los runners de CI están en UTC, y en UTC los fallos de zona horaria no
  existen.** Provocado: cambiar la conversión de la fecha límite a medianoche
  *local* salía verde con `TZ=UTC` y rojo con `TZ=Europe/Madrid`. El test habría
  pasado en CI y fallado en un portátil en Madrid. Ahora fuerza
  `America/Los_Angeles` durante la conversión, y las dos regresiones —escribir
  y leer en hora local— salen rojas también en UTC.

Cada comportamiento se comprobó rompiéndolo a propósito: los 21 cambios ponen
algún test en rojo.

**Encontrado y no arreglado** (no es cobertura, es comportamiento):

- El tablero muestra **como mucho 20 tareas** por proyecto: `listByProject` no
  manda `limit` y el backend aplica 20 por defecto. Sin aviso.
- El dashboard muestra **como mucho 10 proyectos**, por el mismo motivo.
- Si la lista de proyectos falla al cargar, el dashboard dice «No tienes
  proyectos aún» en vez de avisar del error.
- El backend exige nombres y títulos de al menos 2 caracteres; los botones se
  habilitan con 1, y el usuario recibe un «No se pudo crear» genérico.

### #91 — Backend: la cifra de cobertura que callaba el resto

«Cubrir el backend también» empezó por medir, y la medición tenía trampa.
`vitest.config.ts` limitaba la cobertura a `services/` y `utils/`, y con ese
filtro daba un **81 %**. Midiendo todo `src/` salía un **30 %**: middlewares,
controladores, rutas y validadores estaban al 0 %. Es la misma lección que los
249 tests de MetaGPT: una cifra sin procedencia no vale nada. El filtro se amplió
a todo `src/`.

Al leer esa capa apareció el fallo más serio de la noche: **las tareas no
comprobaban la pertenencia al proyecto**. Los proyectos sí (`assertOwner`,
`getById`); las rutas de `/api/tasks` solo exigían estar autenticado. Comprobado
con peticiones HTTP antes de escribir nada, con un token de un usuario ajeno:

```
GET    /api/tasks        200  → tareas de todos los proyectos
GET    /api/tasks/t-a    200
PUT    /api/tasks/t-a    200  → título cambiado
DELETE /api/tasks/t-a    204
```

Con el registro abierto, cualquiera podía crearse una cuenta y leer, editar y
borrar todas las tareas. El peor caso era el listado sin filtros: Prisma ignora
las claves `undefined` del `where`, así que la consulta quedaba vacía.

La política se decidió explícitamente antes de arreglar:

| Rol en el proyecto | Leer | Crear, editar, borrar, comentar |
|---|---|---|
| `OWNER` / `EDITOR` | sí | sí |
| `VIEWER` | sí | 403 |
| ajeno | 403 | 403 |

Los tests se escribieron **antes** del arreglo: 13 de los 33 salieron en rojo
contra el código de entonces, exactamente los del agujero. Cada uno comprueba
dos cosas, el código de estado **y** si la escritura llegó al repositorio: un
403 devuelto después de borrar pasaría un test que solo mirase el estado.

Los tests HTTP levantan la aplicación real con `createApp()` y le hacen
peticiones con el `fetch` de Node; solo se sustituyen los repositorios. Sin
supertest, así que sin dependencias nuevas. Destaparon dos fallos más en
`errorHandler`:

- **Un JSON mal formado respondía 500** —y se registraba como fallo del
  servidor—, porque el error de `express.json()` caía en la rama genérica.
- **Los errores de validación llegaban todos bajo la clave `body`**:
  `flatten()` agrupa por el primer segmento de la ruta, y `validate` envuelve el
  esquema en `{ body, query, params }`. El nombre del campo se perdía.

De 71 a 145 tests, 28 cambios provocados y todos en rojo, cobertura de todo
`src/` del 30 al 85 %.

### #92 — Tokens en el log, destapados por el ruido de los tests

Al ejecutar la suite de #91 en Windows, la salida traía cientos de líneas de
`request completed`, y en ellas se leía `"authorization": "Bearer eyJ…"`,
`"cookie": "refreshToken=…"` y `"set-cookie": "refreshToken=…"`. `pino-http`
escribe las cabeceras completas de cada petición y respuesta **con nivel
`info`, el de producción**.

Primero se convirtió la inferencia en hecho: la aplicación arrancada con
`NODE_ENV=production` escribió, con `"level":30`, el token y la cookie en claro.
Cada token de acceso y cada *refresh token* —válido 7 días— habría quedado en
los logs de un despliegue.

El arreglo tiene un matiz que cuesta una vuelta: **`redact` va en el constructor
de pino, no en las opciones de `pino-http`**, que lo ignora cuando recibe un
logger ya creado, que es lo que hace `app.ts`. Los tests leen la línea JSON real
que se escribiría, con el logger construido por la misma función que usa
producción: contra el logger anterior, 2 de 3 en rojo (el tercero vigila lo
contrario, que no se tape de más). De paso, el log se apaga en los tests: de
cientos de líneas a 9.

Se miró el otro TaskHub: el servidor de TaskHub_React, que sí está desplegado,
no usa `pino`, `morgan` ni `winston`. No le afecta.

**Relación con el estado de arriba:** la familia «registro de secretos en claro»
figura como abordada. Este caso no era una llamada a `log` con una variable, sino
la configuración por defecto de una librería, y apareció leyendo la salida de los
tests, no un listado de alertas. Es el «matiz importante» de esa sección otra vez:
cerrar una familia no garantiza que el patrón no exista en otro sitio.

### #93 — Una pantalla que la API anunciaba y no existía

El README decía «Gestión de miembros por proyecto», y existía el endpoint, pero
no había forma de usarlo desde la aplicación. Tres decisiones explícitas:

- **Por email, no con un desplegable de usuarios.** Responder «no existe ningún
  usuario con ese email» revela qué emails están registrados; se aceptó a
  sabiendas, porque solo lo ve el propietario de un proyecto y el desplegable
  enseñaría a todos los usuarios a cualquiera.
- **Solo `EDITOR` y `VIEWER`.** El validador aceptaba `OWNER`, pero `ownerId`
  es uno solo: un segundo «OWNER» tendría los permisos de un EDITOR con otro
  nombre.
- **Solo ver y añadir.** Quitar miembros y cambiar el rol necesitan endpoints
  que no existen.

La pantalla habría destapado dos fallos el primer día: añadir a alguien que ya
era miembro, o un usuario inexistente, respondía **500**. Eran errores de Prisma
(clave única y clave foránea) que `errorHandler` no reconoce. Ahora son 409 y
404, incluido el caso de dos altas simultáneas que chocan en la base de datos.

Contrato cambiado: `POST /members` recibe `email`, ya no `userId`.

De 21 cambios provocados, **20 en rojo**. El que sobrevive es quitar el
`disabled` del botón «Añadir», que no deja pasar nada porque `add()` comprueba el
email por su cuenta. Se deja anotado en vez de maquillar la cifra. Hubo un
segundo superviviente, quitar la comprobación de `ownerId`, y se cerró con un
test nuevo: el propietario sin fila de miembro.

### Cómo se trabajó, y lo que costó

El shell del equipo sigue sin montar las carpetas (la actualización de Windows
del 8 de septiembre). Esta vez los tests se ejecutaron en un clon del repositorio
en la nube, que tiene salida a npm y PyPI, y los ficheros se escribían después en
la carpeta local. Cuatro cosas que conviene saber para la próxima:

- **Maven Central y `binaries.prisma.sh` están bloqueados** por la política de
  red de ese entorno (403). Java no se puede ejecutar ahí, y los tipos de Prisma
  no se generan, así que el `tsc` del backend se pasó siempre en local antes del
  commit. Antes de descubrirlo se afirmó que había «Java/Maven» a partir de
  `java -version` y `mvn -v`, sin lanzar un `mvn test`: el mismo error de
  anotar sin comprobar, cazado al primer intento real.
- **`.github/workflows/` está protegido contra escritura remota.** Los mínimos
  se subieron a mano con `sed` y número de línea, y el número importa:
  `minimo: 41` aparecía dos veces (línea 306, frontend de Angular; línea 391,
  gym-app), y un `sed` sin línea habría bloqueado la PR de PHP.
- **Los ficheros a más de 7 carpetas de profundidad no se pueden leer desde ese
  entorno**, aunque sí escribir. Para no pisar cambios locales se comparó el
  tamaño con el de `main`, contando los CRLF de los ficheros antiguos.
- **Cada tanda tuvo rama nueva antes de escribir nada**, y se verificó en el
  reflog que la rama salía del último `main` antes de copiar los ficheros.

### Pendiente

- **CV:** las dos variantes dicen **71 tests** para TaskHub_Angular, y el mínimo
  de CI ya es **162 + 99 = 261**. Además dicen **Angular 19**, y el
  `package.json` del frontend declara `@angular/core` `^21.2.19`: hay que
  confirmarlo antes de cambiarlo.
- **Vulnerabilidades:** al hacer push, GitHub informó de «44 vulnerabilities on
  the default branch (16 high, 22 moderate, 6 low)». El estado de arriba dice
  2 alertas de Dependabot abiertas. Sin verificar todavía: hace falta consultar la
  API.
- **Frontend de TaskHub_Angular:** los cuatro comportamientos anotados en #90
  (límites de 20 tareas y 10 proyectos, error de carga mudo, longitud mínima).
- **RadioStack**, con lo ya encontrado leyendo el código:
  - `ChatController` (REST) toma el alias del cuerpo, cuando `ChatWebSocketController`
    lo toma del token precisamente para evitar suplantaciones. Decidido: se
    arregla en la tanda de tests con MockMvc.
  - El paso que cuenta tests de `maven-test` busca `target/surefire-reports` en
    la raíz, y RadioStack es multimódulo: hay que cambiar ese `ls` por un `find`.
  - El comentario de «Java · compilar» dice que sus proyectos no tienen ni una
    clase de test, y RadioStack tiene `LocutorTest`.
  - `radiostack-api` no declara dependencias de test.
  - Como el entorno no ejecuta Java, el runner será el CI sobre una PR borrador.
- **OmniForge y GPTDevTeam**, sin empezar.

---

## 2026-09-11 — El frontend de Angular, de 2 tests a 41

El backend de TaskHub_Angular llevaba 71 tests en CI desde el día anterior. El
frontend tenía **2**, y uno era el `app.component.spec.ts` que genera el CLI al
crear el proyecto. La cifra conjunta tapaba un hueco entero.

### Qué se cubrió

Cinco ficheros en `src/app/core/` y dos en `src/app/features/auth/`. Los que de
verdad importan:

- **Regresión del fallo de SSR** (`auth.service.spec.ts`). Durante el
  renderizado en servidor no existe `localStorage`, y cada acceso está protegido
  con `isPlatformBrowser`. Los tests no comprueban que «no explote» —en jsdom
  `localStorage` existe y no explotaría— sino el **comportamiento** que impone
  la protección: con `PLATFORM_ID` a `'server'` no se lee ni se escribe, aunque
  haya datos delante. Si alguien quita esos guardas por parecer redundantes, se
  ponen en rojo.

- **Dos 401 simultáneos disparan una sola renovación**
  (`auth.interceptor.spec.ts`). Sin el candado `isRefreshing`, cada 401 lanzaría
  su propio *refresh*; con rotación de tokens el segundo llega con uno que el
  primero acaba de invalidar, el servidor lo toma por reutilización y revoca la
  sesión. El usuario se ve expulsado por tener dos pestañas abiertas.

- **Un 401 del propio login no intenta renovar.** El bucle clásico:
  credenciales malas → 401 → renovar → el *refresh* también falla → 401.

- **El aviso de credenciales inválidas no menciona el email**
  (`login.component.spec.ts`). Distinguir «ese usuario no existe» de «la
  contraseña es incorrecta» convierte el login en un comprobador de cuentas
  registradas.

Los componentes se prueban llamando a sus métodos, sin renderizar. Lo que tienen
es una decisión —a dónde va el usuario según lo que responda el servidor— y eso
no necesita DOM: si mañana cambia la plantilla, estos tests deben seguir pasando.

### El comando del CI, averiguado a base de probarlo

El frontend no se lanza como el backend. El constructor
`@angular/build:unit-test` envuelve a Vitest y **no le reenvía sus opciones**:

| Se intentó | Resultado |
|---|---|
| `--reporter` / `--outputFile` | «Unknown arguments». Son de Vitest |
| `--reporters` | Aceptada — plural, del esquema del constructor |
| `--outputFile` | Rechazada; el CLI convierte camelCase a guiones |
| `--output-file` | Aceptada |

Y el **orden importa**: `--output-file` se aplica «solo al primer reporter», así
que `junit` va delante y `default` detrás. Al revés, el XML se llenaría con la
salida de consola y el contador leería basura. Con `junit` a secas la consola no
imprime ni un resumen, y un fallo obligaría a abrir el XML para saber qué se
rompió.

El esquema del constructor está en
`node_modules/@angular/build/src/builders/unit-test/schema.json`, y leerlo
ahorró la mitad de los intentos.

### Cuatro vueltas en rojo por el montaje, no por los tests

Los dos ficheros de componentes fallaron cuatro veces seguidas, cada una por una
causa distinta y ninguna en lo que el test afirma:

1. **Sin `provideRouter`** → «No provider found for `ActivatedRoute`». La
   plantilla lleva un `routerLink` y la directiva `RouterLink` inyecta
   `ActivatedRoute`. No se ve leyendo el componente; solo la plantilla lo delata.
2. **Con `provideRouter` y un doble de `Router`** → «Cannot read properties of
   undefined (reading `root`)». La fábrica de `ActivatedRoute` lee
   `routerState.root` **del `Router` inyectado**, y un doble con solo `navigate`
   lo deja en `undefined`.
3. **Con un doble de `MatSnackBar`** → el espía a cero. El componente importa
   `MatSnackBarModule`, que aporta su propio proveedor, y ese gana.
4. **Espiando `TestBed.inject(MatSnackBar)`** → también a cero. Eso resuelve
   desde el inyector raíz y el componente resuelve desde el suyo: son objetos
   distintos.

Lo que funcionó: espiar el **campo del propio componente**, que es la instancia
que recibe la llamada por definición. Es meter mano en un privado desde un test,
y aquí fue la opción honesta — la alternativa era seguir suponiendo de qué
inyector sale cada cosa.

**La regla, para no repetir las cuatro vueltas en cada componente nuevo:** con
componentes *standalone* que importan módulos de Angular Material, sustituir un
servicio por un objeto propio no funciona, y algunos servicios de Angular se
leen entre ellos, así que un doble incompleto rompe a un tercero. Servicio real
más espía.

### Un patrón de git que ya no es casualidad

Cinco incidencias en tres días del mismo tipo: una rama cuya PR ya se fusionó en
modo *squash*, con commits nuevos encima. El *squash* reescribe el commit como
uno nuevo en `main`, git deja de poder emparejarlos, y aparece un conflicto en el
fichero que ambos tocan.

Lo que lo hace invisible es que `git subir` termina con
`gh pr merge --squash --delete-branch --auto`: la fusión ocurre **sola** minutos
después, mientras uno sigue trabajando en esa misma rama. El momento en que la
rama muere no se ve.

Se resuelve siempre igual —`git rebase origin/main`, que descarta el duplicado
con un «skipped previously applied commit», y `push --force-with-lease`— y se
evita sacando rama nueva después de cada `git subir`. El alias `git nueva` ya
limpia las ramas locales cuyo remoto desapareció.

### Nota de contexto

Toda esta tanda se hizo **sin terminal**: una actualización de Windows del 8 de
septiembre impidió que el entorno de trabajo montara los ficheros, así que los
tests los escribía uno y los ejecutaba el otro, pegando la salida. Funciona, y
tiene un coste medible: las cuatro vueltas del montaje habrían sido una sola con
capacidad de ejecutar.

---

## 2026-09-10 (noche) — El guardián que no guardaba la puerta

Cerrada la tanda anterior, quedaban tres jobs de tests nuevos con sus mínimos
declarados y la sensación de haber terminado. Dos cosas de esa misma noche
demostraron que no.

### Un tercer «pasa en mi máquina», y la conclusión que sacar de los tres

El job de PHP se puso en rojo con **siete tests fallando** y un mensaje que no
decía nada: «Expected response status code [200] but received 500». Setenta
líneas de traza más abajo estaba la causa real:
`ViteManifestNotFoundException`. Los *layouts* Blade llaman a `@vite(...)`, que
al renderizar busca `public/build/manifest.json`; sin él, cualquier ruta con
vista devuelve 500. Los siete que fallaban eran exactamente los que renderizan
una pantalla; los otros 34 no tocan vistas y pasaban.

En local no se nota porque `public/build/` existe de haber lanzado
`npm run build` alguna vez, y está en `.gitignore`. Se resolvió añadiendo
`npm ci && npm run build` al job — compilar assets dentro de un pipeline de PHP
parece fuera de sitio y no lo es: son una dependencia de ejecución tanto como el
`vendor/`.

**Van tres en una noche, y el patrón es el mismo:**

| Caso | Qué faltaba en un entorno limpio |
|---|---|
| TaskHub FastAPI | `pytest` y `httpx`, no declarados en ninguna parte |
| TaskHub FastAPI | El directorio en `sys.path`, que solo añadía `python -m pytest` |
| gym-app | Los assets compilados de Vite |

Los tres eran **invisibles por definición** en la máquina de quien escribió los
tests. Ninguna revisión de código los habría encontrado; los tres aparecieron al
primer intento de ejecutarlos en otro sitio. Es el argumento entero a favor de
un *runner* limpio, y conviene tenerlo escrito porque el reflejo natural ante un
fallo así es pensar que el CI está mal configurado.

### Lo que se descubrió al mirar por qué se había fusionado igual

La PR con esos siete tests en rojo **se fusionó sola**. No fue un descuido: la
única comprobación obligatoria de `main` era `CI en verde`, que sale del
workflow de TaskHub_React. Los jobs de `ci.yml` —incluidos los cuatro de tests—
no eran obligatorios, así que el *auto-merge* ni los esperaba.

Dicho de otro modo: **los mínimos de tests que se acababan de poner detectaban
la pérdida de cobertura y no impedían fusionarla.** Un guardián que avisa y no
bloquea.

Se añadió `Monorepo en verde`, mismo patrón que el `ci-ok` que ya existía en el
otro workflow: un job que depende de los nueve y falla si alguno falló. Dos
detalles que no son de adorno:

- **`if: always()` es imprescindible.** Sin él, el job se *salta* cuando falla
  alguno de los anteriores, y un job saltado no cuenta como fallo para la
  protección de rama: la puerta quedaría en gris y la PR se fusionaría igual,
  que es justo lo que se venía a arreglar.
- **Un único nombre estable, no los nueve jobs.** El nombre de un check de
  matriz incluye sus parámetros —`PHP · tests (…/gym-app, 41)`—, así que cambia
  al subir un mínimo. Exigir ese nombre haría que al pasar de 41 a 45 la
  comprobación obligatoria dejara de existir y se quedara pendiente para
  siempre. Es el mismo fallo ya documentado en el otro workflow a cuenta de los
  filtros de ruta, reaparecido por otra puerta.

El ruleset exige ahora `CI en verde` y `Monorepo en verde`, verificado por API y
no por captura de pantalla.

### Un tercer «anotado como hecho sin estarlo»

Al abrir el ruleset se vio que **«Require a pull request before merging» estaba
desmarcado**, cuando la entrada del 5 de septiembre de este mismo fichero dice
que se activó. El riesgo real era bajo —los *status checks* se aplican también a
los push directos— pero el historial afirmaba algo que no era cierto.

Es el tercer caso de la misma especie en esta lista. Los dos anteriores
aparecieron en el repaso del 5 de septiembre. La conclusión no es que el
historial esté mal escrito, sino que **una lista de estado no se verifica sola**:
hay que ir a mirar, y mirar cuesta un comando.

**Activado y verificado por API el 11 de septiembre.** El episodio tuvo dos
recaídas en el mismo error que el párrafo describe, y las dos las cazó el mismo
comando: se estuvo a punto de anotar aquí como «activado» a partir de una
confirmación verbal, sin consultar; y la primera consulta devolvió vacío porque
el cambio se había marcado en la interfaz sin pulsar «Save changes».

### La puerta sabe fallar: comprobado

Quedó pendiente una noche, y era lo más importante que quedaba. Mientras todo
está en verde, la condición `contains(needs.*.result, 'failure')` **no se evalúa
nunca**: el job pasa porque no hay nada que lo tumbe, no porque se sepa que
reacciona. Un guardián sin provocar es una afirmación, no una garantía — la
misma duda que llevó a escribir tests que comprueban filas y peticiones en vez
de estados `COMPLETED`.

Se provocó: rama de usar y tirar con un `.json` mal formado a propósito, PR
abierta y cerrada sin fusionar. Resultado:

```
✗ CI / Config - JSON y YAML     Failing after 7s
✗ CI / Monorepo en verde        Failing after 4s
```

**Rojo, no gris**, que era el punto entero. Un job que se salta no cuenta como
fallo para la protección de rama: si el `if: always()` faltara, ahí habría
aparecido un check en gris y la PR se habría podido fusionar igual. El fallo que
la puerta viene a evitar, escondido dentro de la propia puerta.

Cuatro segundos. La puerta no repite trabajo, solo lee resultados, así que
tenerla no cuesta nada.

---

## 2026-09-10 (tarde) — Tests que existían y no se ejecutaban en ninguna parte

Cerrada la tanda de BatchProcessor, el plan era «añadir tests a los demás
proyectos del portfolio». Lo primero fue medir, y la medición cambió el plan:
**en tres de los cuatro proyectos abordados no faltaban tests, faltaba que
alguien los ejecutara.**

### El inventario, y por qué no bastaba contar ficheros

| Proyecto | Tests propios | ¿Se ejecutaban? | ¿En CI? |
|---|---|---|---|
| TaskHub React | 962 | `npm run verify` | Sí, workflow propio |
| TaskHub Angular (backend) | 71 | `vitest run` declarado | **No** |
| TaskHub Angular (frontend) | 2 | `ng test` | **No** |
| TaskHub FastAPI | 55 | pytest + conftest | **No** |
| gym-app | 25 | — sin script en `composer.json` | **No** |
| RadioStack | 2 | — | Solo compila |
| OmniForge | 115 | pytest (CI, solo requirements-dev.txt) | Sí |
| GPTDevTeam | 82 (81 en CI: uno es de Windows) | pytest (CI, ruta `tests`) | Sí |

Dos correcciones que hizo falta hacerse a uno mismo mientras se levantaba esa
tabla:

**Contar ficheros no es contar tests, y contar `it(` tampoco.** El primer
recuento dio 6 ficheros en Angular y 2 en FastAPI, y sonaba a cobertura
simbólica. Al ejecutarlos salieron **71 y 55**. La diferencia son los `it.each`
y los métodos dentro de clases, que expanden a varios casos. La cifra buena sale
de ejecutar, no de leer el código fuente.

**Los 249 ficheros de test de GPTDevTeam eran todos de MetaGPT vendorizado.** El
código propio son dos ficheros y 2.629 líneas, con cero tests. Es el ejemplo más
claro de por qué un número sin procedencia no vale nada.

### Lo que faltaba en cada caso

**TaskHub FastAPI: 55 tests que solo podían pasar en una máquina.** Ni `pytest`
ni `httpx` estaban declarados como dependencia en ninguna parte. Comprobado en
un entorno limpio, en dos pasos: con solo `requirements.txt`, «No module named
pytest»; añadiendo pytest pero no httpx, `ImportError` al cargar `conftest.py`,
porque `TestClient` de Starlette usa httpx por debajo. No es un test en rojo, es
que la suite no arranca. Se resolvió con un `requirements-dev.txt` aparte, para
no arrastrar herramientas de test a producción.

Y un segundo fallo, este introducido al montarlo: el job se escribió con `pytest`
a secas y se había verificado en local con `python -m pytest`. **No es lo
mismo** — el `-m` mete el directorio actual en `sys.path` y el ejecutable no—,
así que el CI falló con «No module named 'app'». Se comprobó con un control en
el mismo venv:

| Comando | Sin `pytest.ini` | Con `pytest.ini` |
|---|---|---|
| `pytest -q` | ModuleNotFoundError | 55 pasan |
| `python -m pytest -q` | 55 pasan | 55 pasan |

Se arregló con `pythonpath = .` en un `pytest.ini` en vez de cambiando el
comando del CI, para que funcione con cualquiera de las dos invocaciones y con
la del IDE. La causa de fondo: pytest añade al `sys.path` el primer directorio
**ancestro** del fichero de test que no sea un paquete, y como `tests/` no tiene
`__init__.py`, ese directorio es `tests/` y no `backend/`.

**TaskHub Angular: 71 tests con el script ya declarado y nadie llamándolo.** Sin
sorpresas: `npm ci && npm test` sobre una copia limpia y los 71 en verde en 1,4
segundos. No necesitan base de datos ni `prisma generate` porque sustituyen
`config/prisma` y `@prisma/client` por dobles.

**gym-app: 25 tests que eran de Laravel Breeze.** Aquí la sorpresa fue de otro
tipo. Los 25 existían, pero al abrirlos resultaron ser exactamente los que
genera Breeze al instalarse —registro, login, verificación de correo, perfil—
más dos `ExampleTest` del andamiaje. Cero tests de la aplicación.

Y lo que estaba sin cubrir era justo lo que el CV destaca del proyecto: la
autorización por rol. Se añadieron 16 tests en dos ficheros que prueban cosas
deliberadamente distintas, porque son fallos independientes:

- `RoleMiddlewareTest` — que el middleware **decide** bien. Define sus propias
  rutas de usar y tirar en vez de atacar las reales, para que un fallo signifique
  «la autorización está rota» y no «al controlador le faltaban datos». Fija que
  un visitante sin autenticar se redirige a `/login` y **no** recibe un 403 —un
  403 le confirmaría que el recurso existe— y, sobre todo, que **un `admin` entra
  en rutas que no lo mencionan**: esa regla vive en un `if` dentro del middleware
  y no se ve en `routes/web.php`.
- `RutasPorRolTest` — que el middleware está **aplicado** donde debe. Un
  middleware impecable que nadie ha puesto en la ruta deja la sección abierta
  igual. Inspecciona la tabla de rutas, sin base de datos ni controladores, e
  incluye un barrido de todas las rutas bajo `/admin`, `/coach` y `/clients`
  exigiendo `auth` y algún `role:`.

De 25 tests y 61 aserciones a 41 y 196.

**TaskHub React: nada que hacer.** Se verificó por dos vías independientes —548
tests de servidor y 224 de cliente en verde en local; y su workflow, que no tiene
filtros de ruta y por tanto se había ejecutado entero, con Postgres y Playwright,
en cada una de las PR de esa madrugada—.

### Tres jobs nuevos, y tres formas distintas de contar lo mismo

`Node · tests`, `PHP · tests` —el primero de PHP del repositorio— y
`Python · tests`. Los tres con la misma forma que el de Java: un **mínimo de
tests declarado** en la matriz, no un «mayor que cero».

Lo interesante apareció al copiar el contador de un job a otro. Cada herramienta
escribe el informe JUnit de una forma y **cada una necesita una regla distinta**:

| Herramienta | Forma del XML | Cómo se cuenta |
|---|---|---|
| Surefire (Java) | un fichero por clase, plano | sumar `tests=` |
| vitest | `tests="71"` en `<testsuites>` **y además** en cada `<testsuite>` | sumar solo `<testsuite>` |
| PHPUnit | `<testsuite>` **anidados**: suite → clase | contar `<testcase>` |

En vitest se comprobó en el informe real: un `grep` habría dado **142** en vez de
71, y el mínimo no habría saltado nunca. PHPUnit tiene el problema simétrico
—anida en vez de duplicar— y por eso ahí se cuentan elementos `<testcase>`, que
es inmune a la forma del árbol.

Es la misma tarea tres veces con tres respuestas distintas, y el número
equivocado sigue pareciendo un número. Merece estar escrito porque el error se
comete copiando el job anterior, que es exactamente lo que se hizo.

### Documentación

Los tres READMEs de proyecto no mencionaban los tests en absoluto. Al escribir
las secciones aparecieron dos datos falsos que no tenían que ver con tests:

- El README de FastAPI anunciaba **python-jose** en su tabla de stack. Se
  sustituyó por PyJWT en julio, y precisamente porque python-jose estuvo cuatro
  años sin publicar versión arrastrando una confusión de algoritmos. El README
  seguía recomendando la librería retirada por insegura.
- El README de gym-app trae un fragmento de Tinker para crear los usuarios de
  prueba con roles `'entrenador'` y `'usuario'`. La columna es
  `enum('client','coach','admin')`: MySQL en modo estricto rechaza la inserción y
  en modo permisivo guarda cadena vacía, dejando un usuario que no encaja en
  ningún grupo de rutas.

En el CV se corrigió además «middleware propio aplicado a **seis** grupos de
rutas», que son **tres**. Los seis salían de contar los `Route::resource` dentro
del grupo de admin.

### Estado

De 4 proyectos con tests ejecutándose en CI a 5, y **187 tests** que antes no
corría nadie ahora corren en cada push (71 + 55 + 41, más los 20 de
BatchProcessor de la tanda anterior).

Pendiente de la lista: frontend de Angular (2 tests, uno del andamiaje del CLI),
RadioStack (2). OmniForge y GPTDevTeam se cubrieron después en la rama
`BloqueF` (2026-09-20): 115 y 82 tests, respectivamente; al principio se
pensaba que no los podían tener porque dependían de un LLM, y resultó que la
parte testable (núcleo, AST, sandbox, memoria) no necesita red.

---

## 2026-09-10 — BatchProcessor: las nueve rutas, y tres que estaban rotas

La entrada anterior dejó el proyecto con 7 tests y una ruta cubierta de nueve.
Esta cierra las nueve. Lo que importa no es el número, sino lo que apareció al
escribirlas: **tres rutas llevaban rotas meses y ninguna lo decía**.

### Las tres averías

**Lectura desde base de datos (dos rutas), por un renombrado.**
`DatabaseItemReader` llevaba `@Component` y además se declaraba como `@Bean` con
ese mismo nombre. En una colisión así **gana el escaneado**, que es una fábrica y
no implementa `ItemReader`, de modo que el controlador reventaba con
`ClassCastException` al componer el paso.

Lo interesante es por qué no siempre fue así. La clase se llamaba antes
`DatabaseReader`, así que el bean escaneado era `databaseReader` y convivía sin
problema con el explícito. **El renombrado creó la colisión**, y
`spring.main.allow-bean-definition-overriding=true` impidió que Spring
protestara al arrancar. Un cambio de nombre aparentemente inocuo rompió dos
rutas sin un solo mensaje de error.

Se corrigió una afirmación por el camino: se dijo aquí que estas rutas «nunca
habían funcionado». Es falso —funcionaban en las prácticas—, y el propio fichero
de instrucciones del autor lo demostraba.

**Escritura en API (tres rutas), por un bucle de más.** `ApiItemWriter` iteraba
sobre cada elemento del bloque y en cada vuelta enviaba la lista completa: diez
registros generaban diez peticiones de diez registros, cien envíos en total. El
job terminaba en `COMPLETED` porque las cien respondían 200. El test se escribió
primero, se vio fallar con «No further requests expected... 1 request(s)
executed», y solo entonces se arregló.

### Cambios de funcionalidad

- `databaseItemWriter` pasa a ser un `JpaItemWriter`. El anterior era un
  `ManualItemWriter<T extends GenericEntity>`, y esa firma era el motivo de que
  `Persona` pudiera leerse y escribirse a CSV o a la API pero no guardarse en
  base de datos. La clase se conserva sin uso, documentada como tal.
- `ApiItemReader` construye el tipo con la clase que resuelve `Class.forName` en
  vez de con `ParameterizedTypeReference<List<T>>`, cuyo `T` borra el
  compilador. Jackson deserializa ya en la entidad y no en `LinkedHashMap`, así
  que `genericProcessor` vale para todas las rutas y `PersonaItemProcessor`
  —que existía solo para compensar ese borrado de tipos— se retira.
- Ruta nueva de base de datos a base de datos: `SecondDatabaseConfig` aporta un
  segundo `DataSource`, `EntityManagerFactory` y `TransactionManager`, y
  `/batch/run` acepta un cuarto parámetro opcional, `transactionManager`.
  `JpaItemWriter` persiste con el `EntityManager` del gestor que gobierna el
  paso, así que escritor y gestor tienen que apuntar a la misma base.

### Higiene, con un intento fallido que merece quedar escrito

Fuera `springfox-swagger2` y `springfox-swagger-ui`: no se importaban en ninguna
clase —la documentación la sirve springdoc— y además están compilados contra
`javax.servlet`, que Spring Boot 3 ya no usa. Funcionaban porque nadie las
tocaba.

**`allow-bean-definition-overriding` se intentó quitar y no se pudo.** La
hipótesis era que estaba ahí solo por la colisión de `databaseItemReader`, ya
resuelta. Se escribió como hecho —incluso en la sección «Resuelto» del README—
sin comprobarlo. Al quitarla, la aplicación dejó de arrancar por una colisión
distinta: `BatchAutoConfiguration` registra `jobRepository` y `jobLauncher` **sin
condición de «solo si no existen»**, y `BatchConfig` declara los dos a propósito.
La propiedad tiene, además de la razón que tapaba, una razón legítima.

La salida buena queda anotada y sin hacer: dejar de declarar esos dos beans y
quedarse con los de la autoconfiguración. Eso quitaría de paso el
`setDatabaseType("MYSQL")` fijo del `JobRepository`, que es justo lo que impide
fiarse del test de base de datos a base de datos contra un MySQL real.

### CI

El guardián exigía «más de cero tests». Eso solo detecta el caso extremo; el
realista es que alguien borre o renombre mal una clase y el total baje de 20 a
14, siga siendo mayor que cero y el tick verde no diga nada. Ahora se declara un
**mínimo esperado** en la matriz del workflow: si baja, el CI falla y hay que
bajar el suelo a mano, de modo que quitar cobertura sea una decisión escrita en
el diff. Los tests no se enumeran —`mvn test` los recoge solos—, porque una
segunda lista que mantener se desfasa en silencio.

### Cómo se trabajó, porque el método es la mitad del resultado

Cada test asserta el **efecto** —filas en la tabla, líneas en el fichero,
peticiones enviadas—, no el estado del job. Es lo único que habría cazado un
`COMPLETED` con cien envíos duplicados.

La lectura del código se equivocó al menos cinco veces y la ejecución corrigió
todas. Dos ejemplos: se predijo que el CSV de salida tendría cabecera `data,id`
por un bloque que invierte las columnas, y sale `id,data` —el bloque no hace
nada, y así está documentado en vez de aceptado en silencio—; y se borraron
`PersonaItemProcessor` y `Persona` por muertos, lo que rompió dos rutas
documentadas y hubo que restaurar.

También hubo dos intentos seguidos de arreglar la misma consulta SQL del test de
API a base de datos filtrando por una columna en camelCase. H2 pasa a mayúsculas
los identificadores sin comillas, así que `WHERE nombreCompleto` busca
`NOMBRECOMPLETO`; el segundo intento eligió `personaId`, que tiene el mismo
problema. La versión final no nombra ninguna columna. De ahí salió el consejo del
README de nombrar los campos en minúsculas.

### Estado y lo que queda abierto

**20 tests**, las nueve rutas de punta a punta, sin MySQL ni red. README del
proyecto escrito desde cero con las nueve peticiones literales y los pasos para
mover cualquier entidad en cualquier dirección.

- **La ruta base de datos → base de datos solo está probada contra H2.** El
  `JobRepository` fija `setDatabaseType("MYSQL")` y las dos bases del test son
  H2 en memoria. Falta probarla a mano contra dos esquemas MySQL reales.
- **Dos rutas sin recorrido propio hasta el final.** API → CSV y API → base de
  datos estuvieron un tiempo marcadas como cubiertas porque había test del
  lector por un lado y de los escritores por otro. Deducir no es probar; ahora
  tienen el suyo.
- **Credenciales versionadas**, igual que en la entrada anterior.
- **Código muerto**: `BatchScheduler` es un `@Component` con el cuerpo entero
  comentado y `BatchJobProperties` lee un `batch.job.cron` que ya no existe.

**Cerrado de la entrada anterior:** la configuración por defecto ya es coherente
consigo misma —`entityClass` apunta a `GenericEntity`, que es lo que encaja con
`input.csv`—, así que el perfil de test dejó de fijarla y los tests ejecutan la
configuración real del repositorio.

---

## 2026-09-09 — BatchProcessor: el CI deja de saltarse los tests

El job de Java del `ci.yml` general compilaba con `mvn -q -B -DskipTests
compile`. La bandera estaba puesta a propósito y documentada, pero el efecto
era que la comprobación «Java · compilar» salía en verde sin ejecutar un solo
test en ningún proyecto.

**Lo que había realmente.** Al mirarlo, BatchProcessor tenía una única clase de
test: la que genera Spring Initializr, con un `contextLoads()` de cuerpo vacío.
Los otros cuatro proyectos Maven no tenían ninguna. Así que no existía la
«victoria rápida» de quitar la bandera: no había suite que encender.

Peor: ese `contextLoads` **tampoco habría pasado**. `@SpringBootTest` levanta el
contexto completo y `application.properties` apunta a un MySQL en
`localhost:3306` con `ddl-auto=create`. Sin base de datos delante el contexto no
arranca, así que el test solo pasaba en la máquina de quien tuviera el servidor
levantado.

**Lo que se hizo.** H2 en memoria con alcance `test` y un perfil
`application-test.properties` activado con `@ActiveProfiles("test")`. Se eligió
perfil y no un `application.properties` de test porque este último *sustituye*
al principal en vez de fusionarse: `DatabaseConfig` construye el `DataSource` a
mano leyendo `spring.datasource.hikari.*`, y esos campos son primitivos sin
valor por defecto, así que al perder el fichero principal HikariCP arrancaría
con `maximumPoolSize=0` y fallaría.

Sobre esa base, cinco tests de lo que hace genérico al lector y que no necesitan
base de datos: la resolución de la entidad por reflexión —parámetro ausente,
clase inexistente— y la validación de cabeceras del CSV contra los campos
declarados de la entidad —coincidencia, cabecera desconocida, fichero sin
cabeceras—.

Y uno más que vale por todos los demás: **el recorrido completo**. Lanza el job
igual que lo lanza el endpoint `/batch/run` —lector de CSV, procesador
genérico, escritor a base de datos— y comprueba que las diez filas del
`input.csv` de ejemplo acaban guardadas. Sale `COMPLETED`. Es la primera prueba
de que la aplicación hace lo que dice hacer, y no solo de que arranca.

Total: **7 tests**, verificados en local.

Merece anotarse cómo salió: antes de escribirlo se dieron por defectuosas dos
cosas leyendo el código. Una era falsa —`DatabaseItemWriter` resuelve el
repositorio por nombre construido, `getSimpleName() + "Repository"`, y parecía
que ese bean no existía; existe, y el job escribe—. La otra sigue abierta. En
ambos casos la lectura del código llevó a una conclusión equivocada y la
ejecución la corrigió en segundos.

**El CI.** Job nuevo `Java · tests` para BatchProcessor, y el de compilación se
queda con los cuatro proyectos sin tests, con su nombre intacto para que no
sugiera cobertura que no existe. El job de tests **exige que el número de tests
ejecutados sea mayor que cero**: un `mvn test` sobre un proyecto sin tests
termina en verde sin probar nada, y ese tick verde sería exactamente el tipo de
señal vacía que este repositorio lleva dos semanas quitándose de encima. La
cuenta se saca de los informes de surefire y se comprobó contra informes reales
antes de escribirla.

**Anotado de paso, sin arreglar:** `application.properties` versiona
`spring.datasource.password=1234` con usuario `root`. Son credenciales de
desarrollo local y el riesgo real es nulo, pero es lo primero que se ve al abrir
el repositorio.

**Abierto: la configuración por defecto no es coherente consigo misma.**
`application.properties` trae `entityClass=...model.Persona` y
`csv.file.path=input.csv`. Pero `input.csv` tiene cabeceras `id,data`, que son
los campos de `GenericEntity`; `Persona` declara `personaId`, `nombreCompleto` y
`empleo`. Con los valores de fábrica, el lector de CSV rechaza el propio fichero
de ejemplo del repositorio.

El test de recorrido completo **no cubre esto**: fija `entityClass=GenericEntity`
en el perfil de test para que el par entidad/fichero encaje. O sea, se esquivó
el problema en vez de resolverlo, y conviene que quede dicho para que nadie lea
ese test como prueba de que la configuración por defecto funciona.

Las salidas son dos: cambiar el valor por defecto a `GenericEntity`, y entonces
quien clone el repositorio puede lanzar el ejemplo sin tocar nada; o dejarlo y
documentar en el README que hay que ajustar `entityClass` según el fichero. La
primera parece mejor, pero exige comprobar antes para qué se usa `Persona` en el
resto de la aplicación.

> **Actualización (2026-09-10).** Resuelto por la primera vía: el valor por
> defecto es `GenericEntity` y el perfil de test dejó de fijarlo, así que los
> tests ejecutan la configuración real del repositorio. También queda superado lo
> que dice el párrafo del CI de más arriba: el umbral de «mayor que cero» se
> sustituyó por un mínimo declarado. Ver la entrada del 10 de septiembre.

---

## 2026-09-05 (tarde) — TaskHub_React: el despliegue deja de darse por bueno solo

El job de despliegue terminaba cuando Render **aceptaba** la petición del deploy
hook, no cuando la versión nueva estaba sirviendo. Una compilación que fallara
dentro de Render dejaba el CI en verde y la web con la versión anterior. Estaba
anotado como pendiente en la auditoría y documentado dentro del propio workflow,
así que no era un descuido; era una limitación conocida y sin cerrar.

**Lo que se hizo.** El disparo pasa del deploy hook a la API de Render. El
motivo no es estético: el hook contesta 200 sin decir qué despliegue ha creado,
de modo que para esperarlo habría que consultar el más reciente y confiar en que
sea el nuestro; si alguien redespliega a mano en ese momento, se esperaría al
equivocado. La API devuelve el despliegue con su identificador y esa ambigüedad
desaparece. A cambio, `RENDER_DEPLOY_HOOK` se sustituye por `RENDER_API_KEY` y
`RENDER_SERVICE_ID`.

Sobre eso se añaden dos pasos. El primero espera al estado final consultando ese
despliegue concreto: solo `live` cuenta como éxito, los cinco estados de fallo
ponen el job en rojo, y un estado desconocido también —si Render añade uno
nuevo, es preferible enterarse por un fallo que darlo por bueno—. Hay quince
minutos de margen y se toleran hasta cinco consultas seguidas sin respuesta,
para no sustituir un verde que miente por un rojo que miente. El segundo pide
`/api/health` a la URL pública, que se pregunta a la API en vez de escribirla en
el workflow: que Render diga `live` y que la aplicación conteste no son lo
mismo, y una dirección a mano se queda vieja sin que nadie lo note.

**Verificado en producción, no supuesto.** Primera ejecución tras la fusión:
despliegue `dep-dae7sv1t0dsc7395so80` lanzado con HTTP 201, cinco consultas
intermedias —tres `build_in_progress`, dos `update_in_progress`—, `live`, y
`/api/health` respondiendo 200 al primer intento. Los 59 segundos totales
parecían pocos para una compilación en el plan gratuito; se revisó el registro
en lugar de darlo por bueno, y las consultas intermedias confirman que Render
compiló de verdad.

**La lista de Pendiente, repasada punto por punto contra el código.** Resultó
tener bastante deriva, que es lo que le quita valor a una lista así:

- El **cambio de contraseña con revocación global** seguía como pendiente y
  llevaba varias revisiones implementado, descrito en A04 y cubierto por una
  docena de comprobaciones de `verify`.
- **Exigir `ci-ok` en la rama principal** figuraba como pendiente y estaba
  hecho, mediante un *ruleset* del repositorio. El endpoint de protección de
  rama clásica responde «Branch not protected» aunque las reglas existan, lo
  que induce a pensar que falta. Conviene consultar
  `repos/{owner}/{repo}/rules/branches/main`.
- Apareció uno nuevo: `strict_required_status_checks_policy` estaba en `false`,
  así que una PR podía fusionarse sin estar al día con `main` y su verde se
  había calculado contra otro estado. Se activó, junto con exigir *pull
  request* para tocar `main`.

  > **Corrección (2026-09-11).** Lo primero era cierto; lo segundo no. Al abrir
  > el *ruleset* cinco días después, «Require a pull request before merging»
  > estaba **desmarcado**. Ya está activado y verificado:
  >
  > ```
  > $ gh api repos/{owner}/{repo}/rules/branches/main --jq '.[].type'
  > ...
  > pull_request
  > ```
  >
  > Es el tercer punto de esta misma lista que figuraba como hecho sin estarlo,
  > y los otros dos aparecieron en este mismo repaso. La conclusión no es que el
  > historial esté mal escrito, sino que **repasar una lista contra lo que uno
  > recuerda no sirve**: hay que ir a mirar el estado real, y mirar cuesta un
  > comando. El de arriba.
  >
  > De hecho hizo falta dos veces: la primera consulta devolvió vacío porque el
  > cambio se había marcado en la interfaz sin pulsar «Save changes», que está
  > al final de una página larga. Marcar no es guardar.
- Los demás se comprobaron en el código antes de dejarlos escritos: `PUT` y
  `PATCH` comparten controlador, no hay `LIMIT` ni `OFFSET` en el repositorio de
  tareas, `error.middleware.ts` vuelca el objeto de error entero, y el registro
  de acceso solo escribe método, URL, código y duración —con la cadena de
  consulta dentro de la URL, que es el detalle a decidir—.

**Estado.** De la lista de Alto no queda nada abierto. Lo que sobrevive es
higiene barata (los dos puntos de registro), funcionalidad que este proyecto no
necesita (correo, paginación) y madurez de producción que sería decorativa sin
usuarios reales (métricas, alertas, resiliencia). Nada de ello pertenece ya a la
familia de «señales verdes que no significan lo que parecen», que es lo que se
ha estado cerrando estos dos días.

---

## 2026-09-05 — TaskHub_React: la CSP deja de tener `'unsafe-inline'`

La cabecera `Content-Security-Policy` del proyecto llevaba `'unsafe-inline'` en
`script-src`. Con esa directiva la política deja de defender de la inyección de
scripts, que es prácticamente lo único que se le pide: un atacante que
consiguiera inyectar una etiqueta de script en la página la vería ejecutarse
igual. Estaba puesta, se veía en las cabeceras, y no servía para nada.

La concesión existía por el playground, que era un `index.html` con toda su
lógica dentro de un `<script>` y sus manejadores en atributos `onclick`. La
entrada del 29 de agosto lo describe como «`helmet` con CSP a medida,
compatible con los estilos y scripts en línea del playground»: compatible era
exactamente el problema.

**Lo que se hizo.** La lógica sale a `server/src/public/app.js`. Los 21
manejadores estáticos pasan a `addEventListener` —16 por delegación desde un
`data-accion` y 5 enganchados por `id`—, y los 2 que se generan al pintar cada
tarea se resuelven con un único oyente en `document` que sube por el árbol con
`closest()`. Con eso `script-src` queda en `'self'` y `script-src-attr` en
`'none'`. Se pierde la propiedad de «herramienta de un solo fichero» que tenía
el playground; a cambio su CSP pasa a valer para algo.

**El fallo que casi se cuela, que es lo que merece estar escrito aquí.** Se
añadieron comprobaciones de la política nueva: `script-src 'self'`,
`script-src-attr 'none'`, cero atributos `on*` en el marcado, el HTML cargando
su lógica de un fichero. Las cinco en verde. Y las cinco pasaban sobre una
página que el navegador no ejecutaba: el `<script>` tenía `src="app.js"`
relativo, la página se sirve en `/playground` **sin barra final** —por el
`redirect: false` que se puso a propósito para no encadenar un 301 en una URL
que va en un currículum—, y el navegador resolvía contra la raíz y pedía
`/app.js`. Ahí no hay nada: se llevaba el `index.html` del cliente React y, con
`nosniff`, se negaba a ejecutarlo. El playground se pintaba entero y no
respondía a un solo clic. Sin error en la página y sin nada en rojo.

Lo detectaron los 5 tests de Playwright, únicos que abren un navegador. Las
comprobaciones de cabeceras y marcado no podían: miran lo que el servidor dice,
no lo que el navegador hace. La primera comprobación que se escribió para cubrir
el hueco tenía el mismo defecto —pedía `/playground/app.js` a mano, una URL que
el navegador nunca solicita— y también daba verde con la página muerta.

La versión que quedó **resuelve** la URL sacándola del marcado y aplicándole
`new URL(src, pageUrl)`, igual que haría el navegador, de modo que solo puede
pasar si el fichero está donde se va a pedir. Con ella van dos más: que toda
acción del marcado tenga manejador en la tabla de delegación y que ninguno
sobre —un `data-accion` sin entrada deja un botón muerto en silencio, sin error
ni aviso—, y que los cinco oyentes por `id` encuentren su elemento, porque si
uno falta el `TypeError` corta el resto del arranque.

### Abierto: `taskhub: file:..` vuelve sola con cualquier `npm install`

La auditoría de agosto retiró el paquete raíz como dependencia de sus propios
subpaquetes. **No se quedó retirada.** Un `npm install --prefix server` de esta
noche la reintrodujo en `server/package.json`, y un `npm install --prefix
client` hizo lo mismo con el del cliente. Es reproducible: basta instalar dentro
de cualquiera de los dos subpaquetes.

Lo comprobado:

- HEAD **no** declara la dependencia en ninguno de los dos `package.json`.
- Los dos `package-lock.json` de HEAD sí conservan un nodo `".."` con
  `"name": "taskhub"` y `"extraneous": true`.
- Existía un enlace `server/node_modules/taskhub` apuntando al directorio padre.

Lo **no** explicado, y por eso esto queda abierto: se probó a podar el nodo
`".."` de los dos locks y aun así `npm install --prefix client` volvió a añadir
la dependencia al cliente, que además no tenía el enlace en su `node_modules`.
Con el servidor el enlace explica el comportamiento; con el cliente no hay
mecanismo identificado. Se revirtió todo a HEAD antes de commitear para no
dejar a medias un cambio de dependencias cuya causa no se entiende.

Para retomarlo: reproducir en limpio —clonar aparte, `npm install` en cada
subpaquete y observar qué aparece—, revisar si hay algún `.npmrc` con
`install-links` o similar, y no dar por buena ninguna poda del lock hasta que un
`npm install` posterior la respete.

**Estado.** 962 comprobaciones en las cuatro capas, todas en verde: 548
unitarios de servidor, 224 de cliente, 154 de API contra PostgreSQL y 36 de
navegador. La cifra del README del repositorio estaba en 831 y la de la
auditoría en 937, ninguna de las dos actualizada desde hace dos revisiones;
las tres quedan alineadas.

---

## 2026-08-29 / 2026-08-30 — TaskHub_React: producción, auditoría y CI

Primer proyecto del monorepo desplegado y accesible públicamente:
**taskhub-react.onrender.com**. Servicio web en Render y PostgreSQL gestionado
en Neon, los dos en la región de Frankfurt (`eu-central-1`) para que las
consultas no crucen el Atlántico. Ambos en plan gratuito permanente.

El detalle que decidió el reparto: **el PostgreSQL gratuito de Render caduca a
los 30 días**. Para una demo enlazada desde un currículum eso significa que
quien la abra mes y medio después se encuentra un error. Neon no caduca, así
que la base de datos vive allí y Render solo ejecuta el proceso. Supabase se
descartó por el mismo motivo: pausa los proyectos tras 7 días sin actividad.

### De ficheros JSON a PostgreSQL

`d5780ab` — El almacenamiento eran dos ficheros JSON. En Render el disco es
efímero, así que cada despliegue habría borrado los datos: desplegar obligaba a
migrar.

Se escribió SQL a mano sobre el driver `pg`, sin ORM, con todos los valores
como parámetros. El único elemento estructural dinámico —qué columnas actualiza
un `UPDATE`— se resuelve con lista blanca, que es el patrón correcto cuando la
parametrización no es aplicable.

**Un fallo que el almacenamiento en ficheros escondía:** comprobar si un título
está repetido y escribirlo son dos operaciones. Con JSON, dos peticiones
simultáneas pasaban ambas la comprobación y creaban las dos tareas. Ahora lo
impide un índice único sobre `(user_id, LOWER(TRIM(title)))`, y el servicio
traduce el error `23505` de Postgres al mismo 409 de siempre en lugar de
devolver un 500.

**Lo que no salió como estaba previsto:** se dijo que el patrón repository
aislaría el cambio y que controllers y services no se enterarían. Fue cierto a
medias: el acceso a datos quedó encapsulado, pero el repositorio pasó de
síncrono a asíncrono y eso obligó a propagar `async`/`await` hacia arriba. El
patrón aísla *cómo* se accede a los datos, no que pasen a ser asíncronos.

El aislamiento de la suite dejó de ser una carpeta temporal y pasó a ser un
esquema de Postgres creado y destruido en cada ejecución, incluso si falla a
mitad.

### Un proceso para tres cosas

`06a084b`, `ca9068d` — El mismo Express sirve el cliente React compilado en
`/`, el playground en `/playground` y la API en `/api`. Las rutas desconocidas
devuelven el `index.html` para que decida el enrutador de React, salvo las de
`/api/`, que siguen devolviendo 404 en JSON: si no, un error de escritura en
una llamada devolvería HTML y el cliente fallaría al parsearlo.

El primer despliegue falló con `vite: not found`. Causa: Render define
`NODE_ENV=production` y npm omite entonces las devDependencies, donde están
Vite, TypeScript y tsx. Se resolvió forzando `--include=dev` en la instalación.

### Rate limiting inutilizado detrás del proxy

`f9abef2` — Con Render por delante, Express veía la IP del proxy en todas las
peticiones, así que `express-rate-limit` contaba a todos los visitantes como un
único cliente: un solo usuario activo podía agotar el límite para el resto.
Aparecía en los registros como `ERR_ERL_UNEXPECTED_X_FORWARDED_FOR`.

Se confía en **exactamente un salto**, no en `true`. Confiar en todos permitiría
a cualquiera falsificar `X-Forwarded-For` y saltarse el límite con una IP
inventada distinta en cada petición.

### Rol de administrador por semilla

`6befc84` — Rol `admin` que puede listar usuarios, borrarlos —arrastrando sus
tareas por la clave foránea— y consultar un resumen global.

**Solo se concede por semilla**, desde `ADMIN_USERNAME` y `ADMIN_PASSWORD` al
arrancar. No hay ningún camino desde la API pública: el registro fuerza `user`,
el repositorio no acepta el rol como parámetro y no existe endpoint de
promoción. Un test manda `role: "admin"` en el registro y comprueba que sale un
usuario normal.

Tres decisiones registradas por si se revisan más adelante:

- **El rol se lee de la base de datos en cada petición, no del JWT.** Si viajara
  en el token, retirarle el rol a alguien no surtiría efecto hasta que caducara,
  hasta siete días después.
- **403 y no 404**, al contrario que en las tareas ajenas. Allí el 404 evita
  confirmar que un recurso existe; aquí quien pregunta ya está autenticado y la
  existencia de una zona de administración no es un secreto. Queda así resuelta
  la incoherencia aparente entre proyectos: no es criterio cambiante, es que
  cada situación pide una respuesta distinta.
- **Un administrador no puede borrarse a sí mismo ni dejar la instancia sin
  administradores.**

### Auditoría de seguridad completa

Informe en `Juanito_Software/JS/React/TaskHub_React/docs/AUDITORIA_SEGURIDAD.md`.

Lo que estaba bien: cero inyecciones SQL en 16 consultas, aislamiento entre
usuarios correcto, ningún `innerHTML` ni `dangerouslySetInnerHTML` en el
cliente React, cero vulnerabilidades en las dependencias del servidor.

Hallazgos corregidos:

| Severidad | Problema | Corrección |
|---|---|---|
| **HIGH** | `JWT_SECRET` con valor por defecto publicado en el repositorio: si faltaba la variable, la aplicación arrancaba con una clave conocida y cualquiera podía firmar tokens | En producción se niega a arrancar sin secreto propio, y rechaza el de desarrollo y los de menos de 32 caracteres |
| **HIGH** | Sin CI: los tests solo corrían si alguien se acordaba | Pipeline de 8 jobs (ver más abajo) |
| MEDIUM | CORS abierto a cualquier origen | Lista de orígenes en `ALLOWED_ORIGINS`; en producción, ninguno externo por defecto |
| MEDIUM | Sin ninguna cabecera de seguridad | `helmet` con CSP a medida, compatible con los estilos y scripts en línea del playground |
| MEDIUM | `jwt.verify` sin restringir el algoritmo | `algorithms: ['HS256']` explícito, al firmar y al verificar |
| MEDIUM | `nanoid < 3.3.18` (transitiva de Vite) | `npm audit fix`; cliente y servidor a cero |
| LOW | Contraseñas de 6 caracteres mínimos | 8 como mínimo y 72 como máximo, que es lo que bcrypt tiene en cuenta |
| LOW | Estado, prioridad e id sin escapar en el playground | Escapados; ya no depende de que el esquema no cambie |
| LOW | `taskhub: file:..`, el paquete raíz como dependencia de sus propios subpaquetes | Retirada |

**Un bug real que solo apareció al escribir el test de regresión:** el filtro de
búsqueda parametrizaba correctamente —no había inyección posible— pero no
escapaba los comodines de `LIKE`. Buscar `%` devolvía todas las tareas y buscar
`50%` no encontraba ese texto. Se añadió `escapeLikePattern` con `ESCAPE`
explícito. **El comentario que había en el código afirmando lo contrario era
falso**, lo que ilustra por qué un comentario no sustituye a un test.

### Tests: de 37 a 229

| Capa | Antes | Ahora | Herramienta |
|---|---|---|---|
| End-to-end de API | 37 | **62** | Script propio contra Postgres real |
| Unitarios del servidor | 0 | **86** | Vitest |
| Componentes y servicios del cliente | 0 | **61** | Vitest + Testing Library |
| End-to-end de navegador | 0 | **20** | Playwright + Chromium |
| Cobertura | No medida | Umbrales que fallan el build | v8 |

Lo añadido cubre lo que la auditoría señaló como huecos: manipulación de tokens
(firma inválida, caducado, `alg: none`, sin `sub`, usuario inexistente,
formato inválido), regresión de inyección SQL con cargas reales, validadores,
escapado de comodines y campo calculado `completed`.

Con esto, TaskHub_React deja de ser el único de los tres TaskHub sin batería de
ataques a JWT — la tenía el de FastAPI y faltaba aquí.

**Los E2E de navegador destaparon un desajuste entre cliente y servidor que
ninguna otra capa podía ver:** el campo de contraseña del formulario tenía
`minLength={6}` mientras el servidor, tras subir el mínimo a 8 en esta misma
auditoría, rechazaba las de 7 caracteres. El formulario dejaba enviar y el
error llegaba después, sin que el usuario pudiera preverlo. Es exactamente el
tipo de fallo que solo aparece cuando algo prueba las dos mitades a la vez.

**Lecciones de la puesta a punto de Playwright**, por si sirven para los
próximos proyectos:

- Playwright **falla ante un selector ambiguo** en lugar de elegir el primero.
  Es lo correcto, pero obliga a acotar: "Alta", "Pendiente" o "En progreso"
  aparecen a la vez como distintivo de una tarjeta y como `<option>` de los
  desplegables de filtro. La solución es buscar dentro de un contenedor —el
  formulario, el `<li>` de la tarea— y localizar los distintivos por clase CSS
  en lugar de por texto.
- **Un checkbox controlado por React no cambia de estado hasta que responde la
  API**, así que `check()` falla siempre: comprueba el cambio justo después del
  clic. Con `click()` más una espera al distintivo se verifica además el viaje
  completo, que es una aserción más fuerte.
- **Dos pestañas del mismo contexto comparten `localStorage`**: para simular
  dos usuarios distintos hace falta un contexto de navegador independiente, no
  una pestaña nueva.
- Se sustituyeron las esperas por tiempo fijo (`waitForTimeout`) por esperas a
  que un elemento aparezca. Los tiempos fijos son la causa más común de tests
  que fallan de forma intermitente en CI, donde la máquina va más lenta.

Los umbrales de cobertura se fijaron **por debajo** de la medición real (35% de
sentencias, 40% de ramas). No son un objetivo, son un suelo: impiden que baje
sin que nadie se entere. Un umbral inalcanzable acaba desactivándose.

### Pipeline de CI

`.github/workflows/taskhub-react-ci.yml`, ocho jobs con filtro de rutas para
que solo se dispare cuando cambia este proyecto:

`static` (ESLint y TypeScript) · `server-unit` · `client-tests` con cobertura ·
`api-tests` contra un servicio de PostgreSQL 17 real · `e2e` con Chromium ·
`build` con `NODE_ENV=production`, que comprueba que el artefacto contiene
servidor, playground y cliente · `security` con `npm audit` · `ci-ok`, un job
único del que colgar la protección de rama sin tener que enumerar los demás.

**Política de auditoría:** solo bloquean las vulnerabilidades altas y críticas.
Con `--audit-level=moderate` el pipeline estaría en rojo permanente por
dependencias transitivas de herramientas de desarrollo, y un CI siempre en rojo
deja de mirarse. Las moderadas y bajas quedan para Dependabot.

Se añadió ESLint, que no existía en ningún paquete: TypeScript en el servidor,
reglas de hooks en el cliente. El criterio es señalar errores reales, no
cuestiones de formato.

### Política de contraseñas según NIST SP 800-63B Rev 4

Último cambio funcional de la tanda. Se revisó la política de contraseñas y se
añadió confirmación en el registro.

**Lo que exige la norma** (Revisión 4, julio de 2025):

- **15 caracteres mínimo** cuando la contraseña es el único factor de
  autenticación. El mínimo de 8 solo vale con MFA, que TaskHub no tiene, así
  que se subió de 8 a 15.
- **Prohibido exigir composición.** La Rev 4 pasó de desaconsejar a prohibir
  los requisitos de mayúsculas, números y símbolos. El motivo es que producen
  contraseñas predecibles: obligado a poner una mayúscula, casi todo el mundo
  la pone la primera; obligado a un número, casi todo el mundo pone un `1` o el
  año al final. `Password1!` está en las primeras posiciones de cualquier
  diccionario de ataque; `café con leche y dos tostadas` no está en ninguno.
- **Aceptar todos los caracteres**, espacios incluidos.
- **Comprobar contra contraseñas comprometidas o predecibles.**

**Decisiones propias de TaskHub, que no son requisitos de NIST:**

- El **máximo de 72** es el límite técnico de bcrypt, que solo lee los primeros
  72 bytes. Se rechaza lo que pase de ahí en lugar de recortarlo en silencio,
  que sí es lo que exige la norma.
- La **lista de bloqueo va embebida en el código** en lugar de consultar un
  servicio de credenciales filtradas. Una llamada de red por registro añadiría
  latencia y un punto de fallo desproporcionados para este proyecto. Conectar
  una fuente real queda como mejora futura.
- El **umbral de 4 caracteres** para comparar la contraseña con el nombre de
  usuario. Con 3 aparecían falsos positivos: un usuario "ana" no habría podido
  usar frases con "semana" o "mañana".

**Confirmación de contraseña.** El registro pide escribirla dos veces, pero es
asunto exclusivo del formulario: se compara en el cliente, no viaja a la API y
no se persiste. El contrato de `POST /api/auth/register` sigue siendo
`username` y `password`. Hay un test que manda `passwordConfirmation` con un
valor distinto y comprueba que el servidor lo ignora.

**Compatibilidad.** La política se aplica **solo al registro**. El validador
del inicio de sesión no comprueba longitud ni lista de bloqueo, así que las
cuentas creadas con el mínimo anterior de 8 caracteres siguen entrando. Un test
lo fija insertando un usuario con contraseña de 7 caracteres y verificando que
puede iniciar sesión. Aplicar la política al login habría invalidado cuentas
existentes y, además, daría respuestas distintas según el caso, revelando
información sobre la cuenta antes de comprobar las credenciales.

**Tres cosas que aparecieron al implementarlo:**

1. El **administrador tenía su propia regla de 12 caracteres**, independiente
   de la general. En cuanto la política subiera a 15, la cuenta con más
   permisos habría quedado con un mínimo más laxo que un usuario normal. Ahora
   `seed-admin` usa la misma función de validación.
2. La comprobación de longitud del manejador del formulario resultó
   **inalcanzable desde la interfaz**: el `minLength` del campo bloquea el
   envío antes. Se mantiene como segunda barrera —por si el atributo se pierde
   o el navegador autocompleta— y el test se ajustó para comprobar lo que de
   verdad ocurre.
3. `getByPlaceholder` de Playwright busca **por subcadena**, así que
   `'Contraseña'` casaba también con `'Repite la contraseña'` y catorce tests
   fallaron a la vez por ambigüedad. Ahora usan `{ exact: true }`.

**Tests: de 162 a 229.** Los nuevos incluyen varios cuya única función es
impedir que alguien reintroduzca reglas de composición más adelante: afirman
que `caballo correcto grapa pila` es una contraseña válida y que el campo del
formulario **no** lleva atributo `pattern`.

> **Nota posterior (3 de septiembre de 2026).** Esa decisión se revirtió: la
> política pasó a exigir mayúscula, número y símbolo. Los tests citados en el
> párrafo anterior cumplieron su función —fallaron y obligaron a tomar la
> decisión de forma consciente— y se sustituyeron por sus inversos. Ver la
> entrada siguiente.

### Composición obligatoria: una decisión más estricta que NIST

Fecha: 3 de septiembre de 2026.

Se revirtió la ausencia de reglas de composición. La política pasa a exigir, en
el registro y además de los 15 caracteres, **al menos una mayúscula, un número y
un símbolo**.

**Esto no es una lectura distinta de NIST: es apartarse de NIST.** La Revisión 4
dice que los verificadores **no deben** imponer reglas de composición. La
documentación del proyecto no debe presentarlas como requisito de la norma, y se
reescribió el README y la sección anterior para dejarlo separado:

| Alineado con NIST | Decisión propia de TaskHub |
|---|---|
| Mínimo de 15 caracteres | Mayúscula obligatoria |
| Admitir contraseñas largas | Número obligatorio |
| No truncar en silencio | Símbolo obligatorio |
| Aceptar cualquier carácter, espacios incluidos | Contenido de la lista de bloqueo |
| Comprobar contra una lista de bloqueo | Máximo de 72 bytes (límite de bcrypt) |
| Almacenamiento con hash | Umbral de 4 caracteres del nombre de usuario |

**El efecto secundario se asume y se compensa.** Obligar a mezclar tipos de
carácter empuja a `Password123!`, `Verano2026!` o `P@ssw0rd`, que cumplen los
cuatro requisitos y están en la primera página de cualquier diccionario de
ataque. Aplicar la regla sin más habría dejado la aplicación **peor** que antes.
Por eso se añadió `esPatronPredecible`: rechaza una palabra común rodeada de
dígitos y símbolos aunque cumpla la composición.

**Un fallo encontrado escribiendo esa comprobación.** La primera versión quitaba
todo lo que no fuera letra y comparaba el resto contra la lista de palabras
comunes. Con `P@ssword2026!!!` quedaba `pssword`, que no está en la lista, y se
colaba. Lo detectó un test propio. La corrección deshace las sustituciones de
estilo *leet* antes de comparar y prueba cuatro normalizaciones distintas,
porque el relleno (`2026!!!`) y la sustitución (`@` por `a`) se estorban entre
sí: aplicar solo una de las dos operaciones no llega a `password` por ninguno de
los dos caminos.

**El máximo pasó de caracteres a bytes.** bcrypt cuenta bytes. Una contraseña de
72 caracteres con acentos o eñes son más de 72 bytes en UTF-8, y bcrypt
descartaba el sobrante sin avisar — justo el truncamiento silencioso que la
norma prohíbe. La comprobación anterior, con `.length`, dejaba ese caso pasar.
Es un fallo que estaba desde el principio y que solo salió al revisar el límite.

**La suite de API se estrangulaba a sí misma.** Al añadir las comprobaciones de
las tres reglas, `verify.ts` pasó a hacer una decena de registros que deben ser
rechazados, y cada rechazo cuenta como intento fallido de autenticación. El
limitador cortaba a partir del décimo y todo lo posterior fallaba con 429 en vez
de por lo que se estaba probando. Se resolvió con `AUTH_RATE_LIMIT`, que **se
ignora cuando `NODE_ENV` es `production`**: un límite de fuerza bruta que se
puede aflojar desde el entorno no protege de nada, bastaría con colar la
variable en el panel de despliegue. Tres tests nuevos fijan ese comportamiento.

**Interfaz.** El formulario muestra los cuatro requisitos y los marca según se
escribe, en vez de soltarlos todos al enviar. Con cuatro reglas, descubrirlas de
una en una a base de rechazos es precisamente lo que acaba en `Password123!`. El
estado no se transmite solo con el color: cada línea lleva `✓` o `·` y un texto
para lectores de pantalla.

**Compatibilidad.** Sin cambios respecto a lo anterior: la política se aplica
solo al registro. Se añadió un test que inserta directamente el hash de
`caballo correcto grapa pila` y comprueba que esa cuenta sigue pudiendo entrar.

**Tests: de 229 a 344.** La auditoría individual de los 229 anteriores está en
`docs/AUDITORIA_TESTS_229.md`: 150 quedaron intactos, 63 necesitaron actualizar
fixture o aserción y 10 eran incompatibles con la política nueva y se
sustituyeron por sus inversos. Ninguno se borró ni se desactivó.

### `.gitattributes` estaba truncado y nunca normalizó nada

Fecha: 3 de septiembre de 2026. Afecta a **todo el monorepo**, no solo a TaskHub.

Al revisar el estado del repositorio aparecían como modificados una docena de
archivos de TaskHub_React que nadie había tocado —`App.jsx`, `main.jsx`,
`db.ts`, `schema.ts`, `index.html`…—. El diff era CRLF contra LF: contenido
idéntico, final de línea distinto.

La causa era que **`.gitattributes` estaba cortado a media frase**. Tenía cuatro
líneas, todas de comentario, y terminaba en `#  ` sin salto de línea final. Las
reglas nunca llegaron a escribirse, y así estaba también en el commit: no era un
archivo mal editado en local, era un archivo mal commiteado en su día. Sin
ninguna regla activa, git no normalizaba, y cada editor que guardara con CRLF
dejaba el archivo marcado como modificado para siempre.

El alcance real era mucho mayor de lo que parecía: **`git status` listaba unos
920 archivos modificados en todo el monorepo** —el vault de Obsidian, los
proyectos de Java, los de PHP— y prácticamente todos eran ruido de finales de
línea. Con el archivo reparado, la cifra baja a 44, que son cambios de contenido
de verdad.

La regla que se ha puesto es `* text=auto eol=lf`, con dos matices:

- Se fija `eol=lf` explícitamente en lugar de dejarlo a `core.autocrlf`, que es
  configuración de cada máquina. Así el resultado es el mismo en Windows, en
  Linux y en el runner del CI, sin depender de cómo tenga cada uno su git.
- **Excepción para `*.bat` y `*.cmd`, que van con CRLF.** El intérprete de
  Windows puede fallar al leer un archivo por lotes con LF, sobre todo en las
  etiquetas de `goto`. Hay 79 `.bat` en el repositorio, así que la excepción no
  es teórica. Los `.sh` llevan la marca contraria, LF obligatorio.

Para los archivos de código no hizo falta `git add --renormalize`: el índice ya
guardaba LF y era el árbol de trabajo el que tenía CRLF, así que en cuanto hubo
reglas git dejó de ver diferencia.

**Para los scripts sí hizo falta, y ahí apareció un fallo de verdad.** Los 79
`.bat`, el `mvnw.cmd` y los `.sh` estaban guardados **en el repositorio** con
CRLF, no solo en disco: nunca hubo normalización que lo impidiera. Al declararlos
como texto, git pasó a querer almacenarlos con LF y los marcó todos como
modificados, lo que obligó a renormalizarlos:

```
git add --renormalize "*.bat" "*.cmd" "*.sh"
```

En los `.bat` el efecto es puramente interno —siguen saliendo con CRLF al disco
por la excepción `eol=crlf`, así que en Windows no cambia nada—, pero en los
`.sh` era un error real: `install-linux.sh` e `install-macos.sh` tenían
`#!/bin/bash\r` en la primera línea. En Linux eso falla con `bad interpreter:
/bin/bash^M`, porque el `\r` forma parte de la ruta del intérprete. Los scripts
llevaban rotos desde que se subieron y solo salió a la luz al mirar los finales
de línea.

El renormalizado se acotó con esas tres extensiones en lugar de usar `.`, que
habría arrastrado al índice el trabajo en curso de otros proyectos.

**De paso, dos temporales que llevaban meses versionados.** `server/csp-temp.ts`
y `server/sch-temp.ts` eran scripts de diagnóstico de un solo uso —uno imprimía
la CSP para localizar el `script-src-attr 'none'` que rompió el playground, el
otro contaba esquemas `verify_` huérfanos—. Se borraron.

### Sesiones revocables: access token corto y refresh rotativo

Fecha: 3 de septiembre de 2026.

Era el hueco de seguridad más real que quedaba, y estaba anotado como pendiente
desde la auditoría: **tokens de siete días sin forma de revocarlos**. Un token
robado servía una semana, y el logout solo vaciaba el navegador — quien tuviera
una copia seguía dentro.

**Lo que hay ahora.** Dos credenciales en vez de una. Un JWT de acceso de quince
minutos, que es lo que viaja en `Authorization`, y un token de refresco de siete
días guardado en la tabla `refresh_sessions`. Solo el segundo se puede revocar,
y por eso el primero dura tan poco: un JWT firmado vale hasta que caduca, y la
alternativa —una lista negra consultada en cada petición— cuesta una consulta
por llamada para resolver un problema que se resuelve acortando la ventana.

**El refresco no es un JWT, y eso es lo que hace segura la separación.** Son 32
bytes aleatorios. Si los dos fueran JWT, distinguirlos dependería de comprobar
un claim `typ` en cada sitio, y olvidarlo una sola vez bastaría para que un
refresco valiera como token de acceso. Siendo opaco, el middleware intentaría
verificar una firma inexistente y falla solo. El claim está igualmente, como
segunda barrera.

**Rotación con detección de reutilización.** Cada renovación gasta el token y
entrega otro con el mismo `family_id`. Si reaparece uno ya gastado, no basta con
rechazarlo: quien pudo copiarlo tiene también el siguiente de la cadena, así que
se revoca la familia entera.

Con una excepción que hubo que añadir: dos pestañas del mismo usuario pueden
renovar a la vez con la misma cookie, y eso no es un ataque. Dentro de una
ventana de diez segundos la perdedora se rechaza sin matar la familia. Es un
compromiso explícito —estrecha la detección durante esos segundos— pero la
alternativa era cerrar la sesión a quien tuviera dos pestañas abiertas.

**El refresco va en cookie HttpOnly**, no en localStorage. Es la credencial que
importa: sirve para emitir tokens de acceso durante días. Meter una cookie
obligaba a mirar CSRF, que la documentación anterior citaba como ausente
precisamente porque no había cookies. Queda cerrado con `SameSite=Strict`, que
impide que el navegador la mande en peticiones nacidas de otro sitio, más el
hecho de que la cookie no autoriza ninguna ruta de datos y va limitada a
`Path=/api/auth`. CORS se queda con `credentials: false`: todo es mismo origen
en producción, y en desarrollo Vite hace de proxy.

**Dos cosas que aparecieron al implementarlo:**

1. **Dos renovaciones seguidas devolvían el mismo token de acceso.** El único
   campo variable de un JWT es `iat`, con resolución de segundos, así que dos
   emisiones dentro del mismo segundo salían byte a byte idénticas —con la misma
   caducidad—. Se añadió `jti` con un UUID.
2. **Un test de concurrencia que pasaba por el motivo equivocado.** Lanzaba dos
   renovaciones en paralelo y comprobaba que solo una respondiera 200. Pasaba,
   pero porque el driver del entorno de desarrollo solo admite una conexión y
   tumbaba la segunda, no porque el guardián de la rotación funcionara. Se
   sustituyó por una comprobación determinista: dos llamadas seguidas a
   `marcarRotado`, de las que la segunda tiene que devolver `null`.

**Migración de los tokens antiguos: se invalidaron todos.** No llevan el claim
`typ`, así que dejaron de valer en el primer despliegue y todo el mundo tuvo que
volver a entrar. Fue deliberado: mantenerlos por comodidad habría dejado abierta
una semana justo la puerta que el cambio venía a cerrar.

**Tests: de 344 a 453.** La revisión individual de los 344 anteriores está en
`docs/AUDITORIA_TESTS_344.md`. Cobertura del cliente: del 54,93 % al 72,34 %,
con `AuthContext.jsx` pasando de 0 % a 100 %.

### Experiencia de uso y cobertura del cliente

Fecha: 3 de septiembre de 2026.

Los dos fallos de experiencia de uso que estaban anotados como pendientes, más
la parte del cliente que seguía sin cubrir.

**El checkbox de completada esperaba a la respuesta del servidor** antes de
cambiar de aspecto. Con la base de datos en la misma región son 40-80 ms y
apenas se nota, pero desde una conexión lenta la casilla se quedaba quieta lo
suficiente para que pareciera que el clic no había funcionado, y la gente vuelve
a pulsar. Ahora se pinta el cambio de inmediato y se revierte con un aviso si la
petición falla, que es la contrapartida obligatoria: enseñar un cambio que no
llegó a guardarse sería peor que tardar en enseñarlo.

Un detalle que había que resolver: `completed` es un campo calculado a partir de
`status`, así que el estado optimista tiene que traducir los dos. Cambiar solo
`completed` dejaba la tarjeta incoherente durante el instante en que se pinta,
con la casilla marcada y el distintivo diciendo «Pendiente». La regla —marcar
lleva a `completed`, desmarcar vuelve a `pending`— queda duplicada entre cliente
y servidor, y el test de navegador que marca una tarea y comprueba el distintivo
es lo que detectaría que las dos se separen.

También hubo que distinguir las actualizaciones silenciosas: el ciclo optimista
llama a `onUpdate` dos o tres veces por clic, y el aviso «Tarea actualizada»
salía repetido. El checkbox no avisa —él mismo es la confirmación visual—; la
edición sí, porque el formulario se cierra y sin el mensaje no queda claro que
se haya guardado.

**Al salir, el formulario conservaba el modo** en el que estuviera. Quien acababa
de registrarse y pulsaba Salir se encontraba otra vez «Crear cuenta», con su
campo de confirmación y sus cuatro requisitos de contraseña, cuando lo que casi
siempre quiere es volver a entrar. Ahora vuelve a modo «iniciar sesión» al
perder la sesión, sea por Salir o porque caducara. El reinicio va atado al cambio
de `isAuthenticated` y no a cada render, para no estorbar a quien pulsa
«Regístrate» estando ya fuera.

Los dos tests de navegador que **rodeaban** este comportamiento en lugar de
arreglarlo se han enderezado: uno comprobaba el campo de usuario en vez del
botón porque «podía decir Entrar o Registrarse», y el otro tenía que pulsar
«Inicia sesión» antes de buscar el botón «Entrar».

**Cobertura del cliente: del 72% al 96,95%.** `TaskList.jsx` eran 163 líneas sin
un solo test siendo el componente central de la aplicación, y `App.jsx` otras 51
con el enrutado. Los dos están ahora al 100%, y de paso los tests de `TaskList`
son los que fijan que **los filtros los resuelve la API**: si alguien los
reimplementara en el navegador, la lista seguiría pareciendo correcta con pocas
tareas y dejaría de escalar sin que nada avisara.

**Un `vi.mock` que podía romper otro archivo.** `TaskItem.test.jsx` sustituía el
módulo de servicios entero, y esa sustitución vive en el registro de módulos,
que se comparte entre archivos cuando la suite corre sin aislamiento. Según el
orden de ejecución, dejaba a `api.refresh.test.js` sin el módulo de verdad.
Se cambió por espías, que se instalan y se retiran dentro de su propio archivo.

**Tests: de 453 a 501.** Umbrales de cobertura subidos a 95/94/93/96, siempre
justo por debajo de lo real para que actúen como trinquete.

### Alertas de seguridad: qué era del proyecto y qué no

Fecha: 3 de septiembre de 2026.

Tras los commits de la sesión aparecieron unas treinta alertas en el panel de
seguridad. La mitad no venían de este trabajo, así que lo primero fue separar.

**Dependabot no reacciona a los commits, reacciona a los avisos publicados.** Las
alertas de `qs`, `fast-uri` y `browserslist` salieron todas «hace 15 horas»
porque ese día se publicaron los avisos, no porque hubiera cambiado ningún
`package-lock.json` — de hecho los de Angular, JSGameChat y gym-app llevan meses
sin tocarse. Las de JasperReports y PyTorch son de hace dos y tres meses.

De todo el listado, **cuatro cosas sí eran de este proyecto**, todas de CodeQL:

**1. El token de refresco acababa en el registro del CI.** `verify.ts` imprimía
la cabecera `Set-Cookie` entera como detalle de tres comprobaciones, y ahí va el
token en claro. Esa salida queda guardada en el registro de GitHub Actions, que
ve cualquiera con acceso al repositorio: dejaba allí un token utilizable durante
siete días. Es el hallazgo real de la tanda, y lo introduje yo el día anterior al
escribir los tests de la cookie. Ahora se censura el valor y se conservan los
atributos, que es lo que el test comprueba.

**2. `Math.random()` en los tests de navegador.** Se usaba para generar nombres
de usuario únicos. CodeQL lo marca como «insecure randomness» sin poder saber
que ahí no se genera ninguna credencial, pero además tenía un problema propio:
`Date.now()` con un número de tres cifras colisiona cuando varios tests arrancan
en el mismo milisegundo, y dos usuarios iguales hacen fallar el registro. Se
cambió a `crypto.randomUUID()`, que arregla las dos cosas. Silenciar la alerta
habría dejado el fallo de colisión ahí.

**3. La ruta del playground sin limitador.** Cada petición acaba en una lectura
de disco y no tenía límite. La ruta es fija —no entra nada del usuario en el
path, así que no hay recorrido de directorios—, pero sin límite se puede pedir en
bucle. Ahora pasa por `apiLimiter`, igual que el resto.

**4. Los workflows sin `permissions`.** Siete alertas, una por job. El token que
GitHub inyecta puede escribir en el repositorio por defecto, y cualquier acción
de terceros que corra en el pipeline lo hereda. Se declaró `contents: read` a
nivel de workflow en los dos, `ci.yml` y `taskhub-react-ci.yml`.

El resto sigue abierto y pertenece a otros proyectos del monorepo: PyTorch en
`FPS-AI-Toolkit`, JasperReports en el informe de `LeaderBoard_Unity`, y varias
transitivas de npm en Angular, JSGameChat, unified-chat-widget y gym-app. El
`qs` de TaskHub_React es transitiva de Express y depende de que Express publique
una versión con el arreglo.

### Auditoría integral y los arreglos que salieron de ella

Fecha: 3 de septiembre de 2026. El informe completo está en
`docs/AUDITORIA_INTEGRAL.md`, con la puntuación por áreas y el roadmap.

**Resultado: 7,4/10, sin ninguna vulnerabilidad explotable.** No hay forma de
leer ni modificar datos de otro usuario, escalar privilegios ni mantener acceso
tras una revocación más allá de los quince minutos documentados. Lo que salió
no estaba en la autenticación —que es hoy la parte más sólida— sino alrededor.

**El hallazgo más importante no era un bug.** No existía **ni un solo test** que
comprobara que un usuario no puede modificar ni borrar la tarea de otro. Solo se
probaba la lectura. El código era correcto —`user_id` va en el `WHERE` de las
tres operaciones—, pero si alguien lo quitara en un refactor, los 501 tests
seguirían en verde mientras cualquiera podría editar las tareas de los demás. Es
el patrón OWASP A01, y ahora hay siete comprobaciones que además verifican **en
la base de datos** que la fila no cambió, no solo el código de estado.

**Cuatro bugs reproducibles, todos arreglados:**

1. **Cualquier identificador mal formado devolvía 500.** `GET`, `PUT`, `PATCH` y
   `DELETE` sobre `/api/tasks/:id` pasaban el parámetro a una consulta donde la
   columna es `UUID`; PostgreSQL lanzaba el error 22P02 y la petición acababa en
   500. Un 500 significa «el servidor ha fallado con una petición válida», y
   aquí pasaba justo lo contrario. Ahora hay un `validarUuid` que responde 400.
2. **Un usuario borrado conservaba acceso quince minutos**, y al crear una tarea
   reventaba con un 500 por violación de clave foránea. Se traduce el código
   23503 a un 401, igual que ya se hacía con el 23505 → 409. La ventana de
   lectura se mantiene y queda documentada en `authMiddleware`: cerrarla costaría
   una consulta en cada petición autenticada, y para adelantar quince minutos una
   expulsión no compensa.
3. **`limpiarCaducadas()` no la llamaba nadie.** Estaba escrita y documentada
   desde el primer día: código muerto, con la tabla de sesiones creciendo sin
   techo. Ahora hay un temporizador diario en `session-cleanup.ts`, con `unref`
   para que no impida que el proceso salga.
4. **Sin límite de longitud en `description` ni en `search`.** Se aceptaban
   50 000 y 5 000 caracteres. Los límites nuevos —5 000 y 200— llevan escrito
   el porqué: el de búsqueda importa más porque acaba en un `ILIKE '%…%'` que no
   puede usar índice y recorre la tabla entera.

**Registro de eventos de seguridad.** Era el peor apartado de OWASP: el único
evento que dejaba rastro era la detección de reutilización de un token. Ahora se
registran inicio de sesión correcto y fallido, alta, cierre, cierre global,
renovación, rechazo de renovación, reutilización, denegación de autorización y
borrado de cuenta.

En los fallos de inicio de sesión el **motivo se distingue en el registro pero
no en la respuesta**: al atacante se le sigue dando siempre el mismo mensaje, y
quien mira los logs puede separar «atacan una cuenta que existe» de «prueban
nombres al azar», que son dos ataques distintos.

`security-log.ts` censura por su cuenta cualquier campo que huela a credencial.
Y aquí apareció un fallo propio: la primera versión tapaba **cualquier** clave
que casara con el patrón, así que `tokensRevocados: 3` salía como `<censurado>`.
Lo detectó su propio test. La regla que separa una cosa de otra es que una
credencial siempre es una cadena y un recuento nunca, así que ahora solo se
censuran los valores de texto.

**Un test mío que pasaba por el motivo equivocado.** La comprobación de
`DELETE /api/admin/users/<no-uuid>` usaba un usuario normal y afirmaba que la
respuesta «no era 500». Pasaba, pero porque `requireAdmin` devolvía 403 antes de
que la petición llegara al validador: no comprobaba nada de lo que decía. Se
movió al bloque donde hay token de administrador y ahora exige un 400.

**Cobertura del servidor, por fin medida.** El cliente estaba al 96,95 % con
umbrales; el servidor al 35,76 % **sin medirse en ninguna parte**. El número
sigue siendo bajo y conviene leerlo bien: esa suite solo cubre lógica pura, y
todo lo que necesita base de datos lo ejercita `npm run verify` con 130
comprobaciones. Pero ahora hay umbral y un job en el CI, así que una rama nueva
sin cubrir ya no entra en silencio.

**Las tres vulnerabilidades moderadas de `qs`, cerradas.** Aquí hay que
rectificar lo que se dijo antes: no era cierto que hubiera que esperar a
Express. `npm audit fix` no arregla nada —deja `qs` en 6.15.3, dentro del rango
vulnerable— pero `qs@6.16.0` está publicada, y un `overrides` en el
`package.json` del servidor la fuerza sin tocar Express. Resultado: **0
vulnerabilidades**.

**bcrypt de 10 a 12 rondas.** Medido en la máquina de desarrollo: 48 ms, 94 ms y
189 ms por hash con 10, 11 y 12. No era urgente —con quince caracteres,
composición obligatoria y lista de bloqueo ya no quedan contraseñas que un
diccionario vaya a encontrar—, pero cuesta poco y solo se paga al entrar. Los
hashes antiguos siguen validando: el coste va dentro del propio hash.

**Tests: de 501 a 558.**

### CD: despliegue automático, no encadenado al CI

Render publica en cada commit a `main` mediante Auto-Deploy. **El CI y el
despliegue van en paralelo**: Render no espera al pipeline, así que un commit
con los tests en rojo llega igualmente a producción. Ocurrió con `9bca722`, que
falló el CI y se desplegó, dejando la aplicación rota por el fallo de CORS.

Se mantiene así a propósito mientras el proyecto está en desarrollo: poder
desplegar un commit con tests fallando permite depurar contra el entorno real.
Encadenarlos —desactivar el auto-deploy y llamar a un Deploy Hook desde un job
que dependa de `ci-ok`— queda para cuando la aplicación se estabilice.

### Pendiente

- **Encadenar el despliegue al CI**, según lo anterior.
- **Limitación de intentos por cuenta además de por IP.** Hoy el contador es por
  dirección, así que un ataque distribuido contra un solo usuario no se frena.
- **Acciones del CI fijadas a etiqueta mayor, no a SHA.** Son oficiales de
  GitHub y el riesgo es bajo, pero una etiqueta se puede mover.
- **Protección de rama sin configurar.** Al ser un repositorio de una sola
  persona, lo razonable es exigir que `ci-ok` pase antes de fusionar, sin exigir
  revisión humana: no hay nadie que pueda aprobarla.
- **`PUT` y `PATCH` comparten controlador** y hacen los dos actualización
  parcial. Un `PUT` estricto debería reemplazar el recurso completo. No rompe
  nada, pero es una desviación de la semántica HTTP. Desde la auditoría al menos
  tiene tests: antes no había ninguno en ninguna capa.
- ~~**Tokens de 7 días sin revocación.**~~ Resuelto: access token de 15 minutos
  y refresh rotativo con tabla de sesiones.
- ~~**Cobertura del cliente al 72%.**~~ Resuelto: 96,95%, con `TaskList.jsx` y
  `App.jsx` al 100%.
- ~~**El checkbox de completada espera a la respuesta del servidor.**~~
  Resuelto: actualización optimista con reversión y aviso si falla.
- **Los E2E comparten la base de datos de desarrollo** y dejan usuarios
  `e2e-*` detrás de cada ejecución. En CI da igual porque el contenedor se
  destruye, pero en local conviene limpiarlos de vez en cuando o darles su
  propia base de datos.

---

## 2026-07-26 / 2026-07-27 — Saneamiento de dependencias y seguridad

Revisión completa de las alertas de seguridad del repositorio, con el criterio
de **corregir en lugar de silenciar**: solo se descarta lo que no tiene arreglo
posible, y siempre con el motivo registrado.

### Credenciales expuestas

Se encontraron credenciales de servicios de terceros escritas en un fichero
versionado. El escáner de secretos de GitHub solo había detectado una de ellas,
por ser la única con un formato reconocible; el resto pasaba inadvertido.

**Todas las credenciales afectadas se rotaron o revocaron**, y los valores del
repositorio se sustituyeron por marcadores de posición. El origen de la fuga no
fue el `.env` —que nunca estuvo versionado— sino copiar su contenido a un
fichero que sí lo estaba.

> Los detalles concretos —qué ficheros, qué proyectos, qué servicios— se han
> retirado de este documento a propósito. Este historial es público, y describir
> dónde estuvo cada fuga es un mapa hacia los commits anteriores al arreglo. Las
> credenciales están rotadas, así que ese mapa no lleva a nada utilizable, pero
> no hay ninguna razón para publicarlo. La conclusión técnica se conserva; las
> coordenadas, no.

Se revisaron además las otras alertas del escáner de secretos, de las que dos
resultaron ser falsos positivos (marcadores de posición y un nombre de clase
que coincide con un patrón de clave) y una pertenece a código de terceros
retirado del repositorio.

### Código de terceros vendorizado

`unified-chat-widget` incluía una copia completa del código fuente de
`@retconned/kick-js` en `libs/`. Ahora se instala desde npm como cualquier otra
dependencia. Además de eliminar 347 paquetes y la duplicación de alertas (el
mismo aviso aparecía hasta cuatro veces por tener la librería sus propios
manifiestos), corrige un fallo latente: el código importaba `libs/kick-js/dist`,
que estaba en `.gitignore`, por lo que un clon limpio no podía arrancar.

### Actualizaciones de dependencias

- **gym-app (PHP):** Laravel 10 → 12.64. Las ramas 10 y 11 están fuera de
  soporte y Composer se negaba a instalar cualquier versión de ambas por
  avisos de seguridad sin parche. Se actualizaron en bloque Sanctum 4,
  Breeze 2, PHPUnit 11, Collision 8 y los componentes de Symfony 7.
  `composer audit` pasó de 29 avisos en 13 paquetes a ninguno.
- **gym-app (npm):** Vite y `laravel-vite-plugin` a sus versiones mayores
  actuales. Nota: Laravel declara `axios` y `alpinejs` como dependencias de
  desarrollo, pero ambas se empaquetan para el navegador, así que se tratan
  como de producción a efectos de seguridad.
- **Angular/TaskHub/backend:** `bcrypt` v5 → v6, lo que elimina la cadena
  `node-pre-gyp` / `node-gyp` / `tar` (48 paquetes menos) que arrastraba las
  vulnerabilidades críticas. Compatibilidad de hashes verificada con el flujo
  de login real. También `vitest` 4 y `eslint` 10.
- **Angular/TaskHub/frontend:** Angular 19 → 21 mediante `ng update`, en dos
  saltos mayores verificados por separado, con `@angular/material` y
  `@angular/cdk` alineados. Migrado al paquete `@angular/build`.
- **React/TaskHub/client y FastApi/TaskHub/frontend:** Vite 8 y
  `@vitejs/plugin-react`, con la compilación verificada en ambos.
- **unified-chat-widget:** retirado el soporte de BitChute, DLive, Odysee y
  Trovo. La carpeta `messages/` deja de versionarse por ser estado de
  ejecución.
- Cerradas las pull requests de Dependabot que apuntaban a rutas eliminadas en
  la reestructuración de julio.

### Fallos latentes que salieron a la luz

La actualización de Laravel obligó a ejecutar la batería de tests de gym-app,
probablemente por primera vez, y destapó tres problemas anteriores a esta
sesión:

- `phpunit.xml` tenía comentadas las líneas que redirigen los tests a SQLite en
  memoria. Como los tests usan `RefreshDatabase` (que ejecuta `migrate:fresh`),
  **destruían la base de datos de desarrollo** al ejecutarse. Corregido y
  documentado en el propio archivo.
- `UserFactory` no generaba `phone_number`, campo que la migración declara
  `NOT NULL`, por lo que todos los tests basados en factorías fallaban.
- Los tests de registro y perfil, heredados del scaffolding de Breeze, no
  enviaban los campos que la aplicación añadió después (`phone_number`, `role`)
  ni cumplían su política de contraseñas.
- `Angular/TaskHub/backend` declaraba un script `lint` sin tener ninguna
  configuración de ESLint: nunca había llegado a ejecutarse. Añadido
  `eslint.config.mjs` en formato flat config.

### Recuperación de la base de datos de gym-app

Los respaldos existentes (`docs/sql/*.sql`) eran volcados de MySQL y dejaron de
ser restaurables cuando el proyecto migró a PostgreSQL. Se añadió
`docs/sql/gym_app_postgres.sql`, un script de **solo datos** — el esquema es
responsabilidad de las migraciones — con las secuencias sincronizadas mediante
`setval`, paso imprescindible al migrar de MySQL a PostgreSQL.

### Análisis estático (CodeQL)

Las 69 alertas de CodeQL se agruparon en nueve familias de problemas: lo que
parecían decenas de fallos distintos era el mismo puñado de patrones repetidos
en varios archivos. Se han abordado dos de esas familias.

**Modo debug de Flask (4 alertas, resuelta).** Desactivado en las cuatro
aplicaciones que lo tenían activo. El depurador de Werkzeug permite ejecutar
código Python arbitrario desde el navegador; en dos de ellas se combinaba con
`host='0.0.0.0'`, lo que lo exponía a toda la red local. En `BackCount` se
mantiene el `0.0.0.0` de forma deliberada: OBS necesita alcanzar el servidor
desde otro equipo de la red, y esa es precisamente la razón por la que el
depurador debía apagarse.

**Exposición de información en mensajes de error (parte Java, resuelta).**
El patrón `catch (Exception e) { ... .body("..." + e.getMessage()) }` devuelve
al cliente el detalle interno del fallo, que puede incluir rutas del sistema,
consultas SQL o nombres de clases. Corregido en trece controladores: el detalle
pasa a registrarse con `log.error` y la respuesta HTTP lleva un mensaje
genérico. Donde había `e.printStackTrace()` se sustituyó por el mismo registro.

Dos casos se dejaron intactos a propósito, por estar dentro de bloques de
código comentado y no en rutas activas. Y en `HanoiController2`, que no exponía
nada pero se tragaba la excepción sin dejar rastro, se añadió el registro: un
error silencioso es un problema distinto, pero también es un problema.

La mayoría de esos trece archivos son variantes del mismo ejercicio de Spring
Batch guardadas como carpetas paralelas, por lo que cada aviso aparecía
multiplicado por el número de copias. Se valoró excluir esas carpetas del
análisis y se descartó: son código propio y corregirlo cuesta poco más que
justificar por qué no se corrige.

**Exposición de información (parte Python, resuelta).** Mismo patrón en Flask:
`return jsonify({'error': str(e)}), 500` devuelve la excepción al cliente.
Corregidos 21 casos en la API de puntuaciones de LeaderBoard, en
`flask_api_personas.py` y en el servidor TTS del widget de chat. El detalle
pasa a `app.logger.exception` y la respuesta lleva un mensaje genérico.

**Falta de límite de peticiones (resuelta).** Las rutas de autenticación de los
dos TaskHub con backend Express admitían intentos ilimitados: sin límite, probar
contraseñas por fuerza bruta solo depende del ancho de banda del atacante.

Añadido `express-rate-limit` con dos políticas: una estricta para autenticación
(10 intentos cada 15 minutos por IP) y otra general para el resto de la API
(300). La estricta usa `skipSuccessfulRequests`, de forma que los accesos
correctos no consumen cuota y solo se penaliza a quien falla repetidamente —
que es justo el patrón de un ataque, no el de un usuario despistado.

Verificado en los dos sentidos contra el servidor en marcha: diez intentos
fallidos devuelven 401 y a partir del undécimo 429; doce accesos correctos
seguidos no producen ningún bloqueo. Ambas mitades importan — un límite que
frenara también a los usuarios legítimos sería una defensa convertida en avería.

Limitación conocida: el contador es por IP y vive en memoria, así que se
reinicia con el servidor y no cubre a un atacante distribuido. Suficiente para
el uso de estos proyectos; en un despliegue real habría que respaldarlo en
Redis y bloquear también por cuenta, no solo por origen.

Conviene subrayar dónde vive esta protección: en el **backend** de ambos
proyectos, que en los dos casos es Express. El framework de la interfaz
(Angular o React) no interviene ni puede hacerlo, porque un atacante no usa la
interfaz — lanza peticiones directas contra la API. Toda validación de
seguridad tiene que estar en el servidor; la del cliente es comodidad para el
usuario, no defensa.

**Path traversal (resuelta).** Tres servicios construían rutas de fichero a
partir de datos que controla quien hace la petición: dos servicios de lectura y
escritura de CSV en los ejercicios de Spring Batch —cuya ruta llega por un
parámetro HTTP— y el servidor de juegos, que aceptaba por socket una orden
`DESCARGAR <nombre>` y servía el fichero sin comprobar nada. Este último era el
más grave: bastaba pedir `DESCARGAR ../../..` seguido de cualquier ruta para
que el servidor enviase cualquier fichero de la máquina.

En los tres casos se aplica el mismo patrón, y el orden de los pasos es lo que
lo hace correcto: resolver la ruta contra un directorio base, **normalizarla**
para colapsar los `..`, y solo entonces comprobar que sigue estando dentro de
la base. Comprobar antes de normalizar es el error habitual al implementar esta
defensa, y deja la puerta igual de abierta. En el servicio de escritura se
sanea además el nombre derivado de una columna del CSV, sustituyendo cualquier
carácter que no sea alfanumérico, punto, guion o guion bajo.

Cambio de comportamiento a tener en cuenta: esos servicios aceptaban antes
rutas absolutas cualesquiera y ahora solo rutas dentro del directorio base, que
por defecto es el de trabajo y se puede cambiar con `-Dbatch.files.dir=...`.

### Wrappers de Maven incompletos

Al intentar compilar para verificar los cambios anteriores apareció otro
defecto de fondo: **doce proyectos tenían el script `mvnw` versionado pero sin
los ficheros del wrapper**, así que ninguno era construible desde un clon
limpio — incluido `Java/BatchProcessor`, que figura en el catálogo como
proyecto mantenido. Restaurados los doce.

Es el mismo patrón que el script de lint sin configuración de ESLint y que los
tests que nunca llegaban a ejecutarse: **herramientas declaradas pero jamás
ejercitadas**. Tres hallazgos con la misma causa y la misma solución, que es
integración continua: un pipeline que compile y ejecute lo que el repositorio
dice tener habría detectado los tres el primer día.

**XSS y sanitización incompleta (resuelta).** Cuatro avisos con tres causas
distintas, y cada uno pedía una solución diferente:

En el controlador de pseudocifrado, la respuesta contiene texto del usuario y
podía servirse con un tipo de contenido que el navegador interpretara como
HTML. Aquí **escapar no era una opción** — alteraría el resultado del cifrado —,
así que la defensa es declarar `produces = TEXT_PLAIN`: el navegador muestra la
respuesta literalmente en lugar de interpretarla.

En la consola de depuración de TaskHubPro se construía el contenido con
`innerHTML` a partir de la URL (que incluye los filtros que teclea el usuario)
y de la respuesta del servidor. Sustituido por construcción del DOM con
`textContent`. La diferencia es de fondo: `innerHTML` interpreta lo que recibe,
`textContent` lo inserta tal cual.

Y en el saneado de texto para el sintetizador de voz del widget había el error
más instructivo de los tres. La línea original quitaba etiquetas con una única
pasada de `replace(/<[^>]*>/g, '')`. Parece correcta, pero con una entrada como
`<<span>script>` el filtro elimina el `<span>` central y **produce** `<script>`,
una etiqueta recién creada que ya nadie vuelve a revisar. Ahora se repite hasta
que el texto deja de cambiar y se eliminan los signos sueltos. La lección
general: un filtro de una sola pasada puede construir aquello que pretende
eliminar.

### Más herramientas declaradas pero nunca ejercitadas

Intentar compilar para verificar los cambios anteriores destapó dos defectos
más, ninguno relacionado con esta sesión:

- El `pom.xml` de `ApiService` **se declaraba como dependencia de sí mismo**, lo
  que impedía a Maven ni siquiera leer el proyecto. Tenía además un
  `spring-boot-starter` duplicado y Lombok fijado a `RELEASE`, un valor obsoleto
  que hacía que la compilación pudiera cambiar de un día para otro sin tocar
  nada. Ese proyecto no había compilado nunca.
- Siete `application.properties` estaban guardados en ISO-8859 en lugar de
  UTF-8, por haberse escrito con un editor de Windows en español. Maven y Spring
  Boot leen los recursos como UTF-8, así que la compilación fallaba en cuanto
  aparecía una vocal acentuada en un comentario. Convertidos los siete.

Con estos, van seis hallazgos de la misma naturaleza: script de lint sin
configuración de ESLint, tests que destruían la base de datos y nunca se
ejecutaban, doce wrappers de Maven incompletos, un `pom.xml` ilegible y unos
recursos mal codificados. Todos son **cosas declaradas que nadie llegó a
ejecutar**, y todos los habría detectado un pipeline de integración continua en
su primer día. Es, con diferencia, la conclusión más útil de esta revisión.

(Más adelante aparecieron cinco más, hasta once: el `IvParameterSpec` y la
generación de claves RSA de HashTools, el SSR de TaskHub Angular, el
`permitAll()` con token de demostración de RadioStack, y unos `@types/node`
fijados a la versión 18 en un proyecto que se ejecuta sobre Node 22. Todos
documentados en sus respectivas secciones.)

### Criptografía débil en HashTools

Cuatro alertas en `Java/HashTools`, un ejercicio del ciclo formativo que cifra
ficheros con AES y con RSA. Las alertas señalaban los modos de operación: AES en
CBC y RSA con relleno PKCS#1 v1.5. Ambos son corregibles con un cambio de una
línea, pero al revisar el código apareció algo más importante que las propias
alertas.

**El vector de inicialización nunca fue aleatorio.** El código creaba el
`IvParameterSpec` a partir de un array vacío y *después* llamaba a
`SecureRandom.nextBytes()` sobre ese array. `IvParameterSpec` copia el array que
recibe en el constructor, así que rellenarlo más tarde no tiene ningún efecto:
el IV han sido siempre dieciséis bytes a cero. La intención era correcta y el
código lo aparenta, pero la aleatoriedad nunca llegó a aplicarse.

Lo relevante es que **el programa funcionaba gracias a ese fallo**. El IV no se
guardaba en ninguna parte, así que si de verdad hubiera sido aleatorio, el
descifrado no habría tenido forma de reconstruirlo y habría fallado siempre. Un
error tapaba al otro. Es el mismo patrón que los seis hallazgos de la sección
anterior: código escrito, nunca comprobado de verdad.

La corrección:

- **AES pasa a GCM** (`AES/GCM/NoPadding`) con un nonce de 12 bytes generado en
  cada cifrado y escrito al principio del fichero de salida, que es de donde lo
  lee el descifrado. GCM además es cifrado autenticado: si el fichero se
  manipula, el descifrado lanza una excepción en lugar de devolver datos
  corruptos en silencio, cosa que CBC no detecta.
- **RSA pasa a OAEP** con SHA-256 en el hash y en MGF1, declarados de forma
  explícita porque el valor por defecto de Java combina SHA-256 con MGF1-SHA1 y
  esa incoherencia provoca fallos de interoperabilidad difíciles de localizar.

Al cambiar a OAEP hubo que tocar el tamaño de bloque, y eso destapó un tercer
defecto. OAEP consume 66 bytes de relleno frente a los 11 de PKCS#1, así que el
bloque de 117 bytes fijado a mano dejaba de valer; ahora se calcula a partir del
módulo de la clave. Pero además el descifrado RSA leía el fichero **entero** y
lo pasaba a un único `doFinal`, cosa que solo funciona si el original cabía en
un bloque: cualquier fichero mayor que el bloque fallaba al descifrarse. Ahora
se descifra bloque a bloque.

**Aviso de compatibilidad:** cambia el formato del fichero cifrado. Los ficheros
generados con la versión anterior del programa ya no pueden descifrarse con
ésta. Dado que se trata de un ejercicio y no hay datos que conservar, se asume.

#### Generación de claves RSA

Mismo patrón que el IV, en el mismo proyecto. `generarClaves(String pass, int
tamaño)` no usaba ninguno de sus dos parámetros: nunca llamaba a
`kpg.initialize(...)`, así que Java generaba una clave de 2048 bits con su
generador por defecto e ignoraba tanto el tamaño como el `SecureRandom`
sembrado con la contraseña.

Lo interesante es que **los dos parámetros muertos eran trampas** para quien
intentara "arreglarlos" sin mirar:

- El único sitio que llamaba al método pasaba `256`, un valor copiado de la
  generación de claves AES, donde 256 bits es lo normal. Para RSA es un error de
  categoría: `initialize(256)` habría lanzado `InvalidParameterException`.
- Conectar el `SecureRandom` habría sido peor. `setSeed` sobre SHA1PRNG
  sustituye la semilla y vuelve **determinista** la generación: cualquiera que
  conociese la contraseña podría reproducir la misma clave privada. Y
  `PasswordValidator` acepta contraseñas de 8 a 20 caracteres, al alcance de un
  ataque por fuerza bruta.

Corregido llamando a `initialize(2048)` con el generador aleatorio del sistema,
rechazando cualquier tamaño inferior a 2048, y eliminando el `SecureRandom`
sembrado en lugar de conectarlo. Se retiró el parámetro `pass`, que ya no
interviene.

**El comportamiento observable no cambia**: antes se generaban claves de 2048
bits con el generador por defecto, y es lo que se sigue haciendo. Las claves ya
guardadas siguen siendo válidas. Lo que cambia es que el código ahora dice lo
que hace.

### Protección CSRF desactivada

Dos alertas, en dos proyectos, que pese a la etiqueta común **no son el mismo
problema**. La distinción que decide ambos casos es si existe *autoridad
ambiental*: credenciales que el navegador adjunta por su cuenta a una petición
provocada desde otro sitio web. Sin eso, no hay CSRF posible, porque la petición
forjada llega sin identidad.

**RadioStack — falso positivo.** La API es `STATELESS` y no crea sesión ni emite
ninguna cookie; no hay `HttpSession`, `Cookie`, `formLogin` ni `httpBasic` en
todo el proyecto. Desactivar CSRF ahí es la configuración correcta. CodeQL ve
`csrf.disable()` y avisa sin poder determinar si hay autoridad ambiental.
Documentado en el propio `SecurityConfig`, con la condición que obligaría a
revertirlo: si algún día se añade autenticación por sesión o por cookie.

**TaskHub Angular — real, aunque de impacto bajo.** El access token viaja en la
cabecera `Authorization`, que el navegador no añade solo y por tanto es inmune.
Pero el refresh token va en cookie, y `POST /api/auth/refresh` y
`POST /api/auth/logout` se autentican **únicamente** con ella. Eso sí es
autoridad ambiental.

El impacto conviene medirlo con precisión en lugar de asumir el peor caso: el
CORS está restringido a un solo origen, así que un atacante no puede leer la
respuesta y no roba ningún token. Lo máximo que consigue es forzar un cierre de
sesión o una rotación del refresh token. Molestia, no robo de credenciales.

Corregido subiendo la cookie de `sameSite: 'lax'` a `'strict'`. Es un cambio que
no puede romper nada: la SPA y la API son *same-site*, que es la razón de que ya
funcionase con `lax`; `strict` solo restringe el caso cruzado, que aquí no
existe. Se descartó montar un token CSRF con librería (patrón double-submit):
para dos rutas cuyo peor desenlace es un logout forzado, es más infraestructura
de la que el problema justifica.

También se descartó **quitar la cookie** y devolver el refresh token en el
cuerpo de la respuesta. Eliminaría la clase de vulnerabilidad entera, pero esa
cookie es `httpOnly` precisamente para que un XSS no pueda leer el refresh
token: sería cambiar un CSRF de impacto bajo por un XSS con robo de sesión.

**La alerta de TaskHub se descarta a mano.** La consulta
`js/missing-token-validation` es sintáctica — busca `cookie-parser` sin
middleware CSRF y no evalúa los atributos de la cookie, así que no hay forma de
que la corrección aplicada la cierre sola. Es la única excepción al criterio de
*corregir en lugar de silenciar* seguido en el resto de la revisión, y la
diferencia respecto a un descarte de conveniencia es que aquí sí hay un arreglo
real de por medio: lo que se descarta es una comprobación que no sabe mirar
dónde está puesta la defensa.

La corrección se verificó ejecutándola, no por deducción: con la cookie ya en
`Strict`, `POST /api/auth/refresh` devuelve 200 con usuario y token nuevos, y
`POST /api/auth/logout` devuelve 204. Las dos rutas que dependen de la cookie
siguen funcionando.

**Hallazgo aparte:** `SecurityConfig` de RadioStack declaraba
`anyRequest().permitAll()`, es decir, la API entera accesible sin autenticación.
Se anotó aquí como *"puede ser deliberado si es de solo lectura"*; al revisarlo
resultó que no lo era. Resuelto en la sección «Autenticación real en RadioStack».

### Bug de sesión con SSR en TaskHub Angular

Descubierto al verificar lo anterior, y no relacionado con ello: **al pulsar F5
estando dentro, la aplicación expulsaba al usuario al login**.

Lo primero fue descartar que lo hubiera provocado el cambio de la cookie. Tres
medidas lo dejaron claro:

- `localStorage` conservaba la sesión intacta después del F5. Si la causa
  hubiera sido la cookie, el único camino hasta la pantalla de login pasa por
  `clearSession()`, que la habría borrado.
- No se registró **ninguna** petición a `/api/auth/refresh`. La expulsión ocurría
  sin consultar al backend.
- Pedir `/` directamente devolvía un **redirect HTTP** (respuesta 3xx), es decir,
  la decisión venía del servidor, antes de ejecutarse una línea de JavaScript en
  el navegador.

La cadena causal: `ng serve` renderiza en servidor; allí se construye
`AuthService`, cuyo `readUser()` devuelve `null` porque en el servidor no existe
`localStorage`; `isAuthenticated()` da `false`; el `authGuard` que protege la
ruta raíz responde `createUrlTree(['/login'])`; y Angular SSR traduce eso a un
redirect. **En el servidor la aplicación estaba siempre deslogueada.** Solo se
manifestaba al refrescar, que es la única ocasión en que interviene el servidor.

Había además un agravante: `app.routes.server.ts` declaraba
`{ path: '**', renderMode: RenderMode.Prerender }`. Prerenderizar es generar
HTML en tiempo de compilación, así que una ruta protegida por un guard quedaba
congelada en un fichero estático con el resultado de evaluar la sesión de un
usuario inexistente.

**Corregido** marcando las rutas protegidas como `RenderMode.Client`, de modo
que el guard se evalúa solo en el navegador, que es donde vive la sesión. Login
y registro siguen prerenderizándose: son públicas y no dependen de quién sea el
usuario. La regla que ordena ahora ese fichero está escrita en él, junto con la
condición que permitiría revertirlo (deducir la sesión de la cookie `httpOnly`,
que el servidor sí puede leer).

Es el octavo caso del patrón dominante de esta revisión: el SSR estaba
configurado, compilaba y arrancaba, pero el estado de sesión se había diseñado
como si solo existiera el navegador. **Nadie había pulsado F5 estando dentro.**

### Sockets enlazados a todas las interfaces

Once alertas de la misma regla (`py/bind-socket-all-network-interfaces`), en
cuatro programas de Python. Tratarlas en bloque habría sido el error: la regla
detecta `bind("")` o `bind("0.0.0.0")`, pero la pregunta que decide cada caso no
es *¿escucha en todas las interfaces?* sino **¿tiene sentido que este programa
reciba conexiones de la red?**. Salieron tres respuestas distintas.

**Intencionadas — chat de voz, 8 alertas (#63 a #70).** Aplicación de voz entre
equipos de una red doméstica, con descubrimiento por broadcast
(`BROADCAST_IP = "192.168.1.255"`). Recibir conexiones de otros equipos es su
función; enlazar a `127.0.0.1` la dejaría sin hacer nada. Documentadas en la
cabecera de ambos ficheros y descartadas.

El riesgo real de estos programas no es el enlace sino que **no autentican**:
cualquiera en la misma red puede unirse o inyectar audio. Se asume por ser una
red doméstica, y así queda escrito en el código, con la advertencia de no
usarlos en redes ajenas.

**Intencionada — `EnviarArchivos.py`, 1 alerta (#224).** Mismo caso, con un
matiz a favor: sí comprueba un `dest_hash` (SHA-256 derivado del nombre que se
comparte con el emisor) y rechaza lo que no lo traiga. Documentada y descartada.

**Descuido real — `servidor_ftp.py`, 2 alertas (#72, #73).** Aquí el problema
era más grave que la alerta, y solo se ve leyendo el código:

```python
elif cmd == "PASS":
    if last_user is not None:
        logged_in = True          # cualquier usuario, cualquier contraseña
```

**No había autenticación.** Con `USER` y `PASS` arbitrarios se obtenía lectura y
escritura sobre el directorio del script. Enlazado a `0.0.0.0`, eso significaba
un servidor de ficheros abierto a toda la red local.

Y era además incoherente con su propio diseño: el modo pasivo anuncia al cliente
la dirección `127.0.0.1` como destino del canal de datos, con el comentario
*"cliente suele conectar a la misma máquina"*. Es decir, **el código ya asumía
uso local**, pero abría el puerto de control a la red entera.

Corregido:

- `HOST = "127.0.0.1"`, coherente con lo que el modo pasivo ya daba por hecho.
  El socket pasivo se enlaza también a `HOST` en lugar de a `0.0.0.0`: el canal
  de datos no debe estar más expuesto que aquel por el que uno se autentica.
- Credenciales reales, leídas de `FTP_USUARIO` y `FTP_CLAVE`. Si faltan, **el
  servidor no arranca**: arrancar sin credenciales equivaldría a aceptar a
  cualquiera, que es justo lo que hacía antes. Mismo criterio de fallo ruidoso
  que se aplicó en `LeaderBoard_Unity`.
- Comparación con `hmac.compare_digest` en lugar de `==`. Un `==` corta en el
  primer carácter distinto, y ese tiempo desigual permite adivinar la clave
  carácter a carácter midiendo la respuesta.
- Mismo mensaje de error para usuario inexistente y clave incorrecta, para no
  revelar qué usuarios existen.

**Un tercer defecto encontrado de camino**, en el mismo fichero: las cuatro
comprobaciones de que una ruta no se sale de la raíz usaban
`str(ruta).startswith(str(root))`. Comparar rutas como cadenas es un error
clásico: si la raíz es `/datos/FTP`, la ruta `/datos/FTP_privado` empieza por esa
cadena y pasaba el filtro pese a estar fuera. Sustituidas por
`Path.is_relative_to`, que compara por componentes.

### Path traversal en EnviarArchivos.py

No lo detectó CodeQL; apareció al revisar el código de la familia anterior.

```python
save_path = os.path.join("received_files", filename)   # filename lo elige el emisor
```

El nombre del fichero viene en la cabecera que envía el remitente, sin sanear.
Con `../../algo.txt` se escribía fuera del directorio de destino. Requiere
conocer el `dest_hash`, así que no era explotable por cualquiera, pero es la
misma clase de fallo que ya se corrigió en los proyectos Java.

Corregido con `os.path.basename` para quedarse solo con el último componente, y
una verificación posterior con `os.path.commonpath` que confirma que la ruta
final resuelta cuelga realmente del directorio de destino. Se sanea primero y se
comprueba después, en ese orden: el saneo por sí solo es fácil de dar por bueno
sin serlo, y la comprobación es lo que lo respalda.

### Autenticación real en RadioStack

Salió del descarte de la alerta de CSRF. Al documentar por qué desactivar CSRF
era correcto allí quedó anotado un cabo suelto: `anyRequest().permitAll()`. Se
dejó dicho que *"puede ser deliberado si es de solo lectura"*. **No lo era.**

La API tiene `POST`, `PUT`, `PATCH` y `DELETE` sobre programas, locutores,
emisiones, comentarios y chat. Cualquiera podía crear o borrar programas de
radio sin identificarse. Y debajo había algo peor:

```java
res.setToken("Bearer-demo-" + u.getId());
...
Long id = Long.parseLong(auth.replace("Bearer-demo-", ""));
```

El token era el texto `Bearer-demo-` seguido del identificador del usuario. Sin
firma, sin secreto y sin caducidad: enviando la cabecera
`Authorization: Bearer-demo-1` se suplantaba al usuario 1. No había nada que
falsificar, bastaba con teclearlo.

**Lo relevante no es que faltase autenticación, sino que el código aparentaba
tenerla.** Había un `AuthController`, un `/login`, un `PasswordEncoder` con
BCrypt comparando hashes correctamente y un `/me` que devolvía 401. Todo el
andamiaje estaba bien construido, y solo el token era un marcador de posición.
Un sistema sin autenticación se reconoce a simple vista; uno que la simula
induce a error a quien lo lea después.

Sustituido por JWT firmado:

- `JwtService` firma con HMAC-SHA256. La clave se lee de
  `RADIOSTACK_JWT_SECRET` y **no tiene valor por defecto**: uno escrito en el
  repositorio sería una clave pública con la que cualquiera podría emitir
  tokens válidos. Se rechaza al arrancar cualquier clave de menos de 256 bits.
- El token lleva identificador, email y rol. Nada secreto: un JWT viaja en
  Base64, no cifrado, y su contenido es legible por cualquiera. Lo que no se
  puede es alterarlo sin invalidar la firma.
- `JwtAuthenticationFilter` deja la identidad en el contexto de seguridad pero
  **nunca rechaza una petición**. Si no hay token, continúa con el contexto
  vacío. Decidir quién pasa es competencia de `SecurityConfig`, y así las reglas
  de acceso viven en un único sitio en lugar de repartidas en dos.
- `SecurityConfig` sustituye el `permitAll()` global: login abierto, `GET`
  abierto (la parrilla de una radio es información para los oyentes) y todo lo
  que modifica datos exige token. Se añadió un `authenticationEntryPoint` para
  responder **401** en lugar de 403: la diferencia importa, porque no es que
  falte permiso, es que no se ha dicho quién eres.
- `/me` vuelve a consultar la base de datos para comprobar que la cuenta sigue
  activa. **Un JWT no se puede revocar**: al desactivar un usuario, su token
  sigue siendo criptográficamente válido hasta que caduque. La caducidad (una
  hora por defecto) es el único límite real, y por eso es configurable.

**Cambio de compatibilidad:** el cliente JavaFX enviaba `Authorization: <token>`
sin el prefijo `Bearer`, porque el prefijo venía incrustado en la cadena
`Bearer-demo-<id>`. Funcionaba por coincidencia. Corregido en `ApiClient`, que
ahora añade el esquema donde corresponde —forma parte del protocolo HTTP, no del
token—. **El módulo admin hay que recompilarlo.**

Es el noveno caso del patrón dominante: `permitAll()` y el token de demostración
eran marcadores de posición que nadie retiró.

#### Autenticación del WebSocket del chat

Quedó abierta en un primer momento y se cerró después. El filtro JWT de HTTP no
sirve para el chat: una conexión WebSocket se abre con un único handshake y
luego las tramas viajan por un canal ya establecido, fuera del ciclo
petición-respuesta donde actúan los filtros de servlet. Y el handshake tampoco
puede llevar cabecera `Authorization`, porque la API de WebSocket de los
navegadores no permite añadirlas.

La solución es autenticar **una trama más tarde**, en el `CONNECT` de STOMP, que
es la primera que el cliente envía y sí admite cabeceras propias. Lo hace
`StompAuthChannelInterceptor`, y el usuario resultante queda asociado a la
sesión, de modo que las tramas posteriores lo heredan.

El criterio de acceso es **el mismo que en HTTP**, a propósito, para no tener dos
políticas distintas según el transporte:

- `SUBSCRIBE` a `/topic` (leer el chat) es público, como los `GET`.
- `SEND` a `/app` exige token válido, como los `POST`.

Un `CONNECT` sin token se admite como anónimo. Uno con token inválido se
rechaza en lugar de degradarse a anónimo: un token caducado o manipulado indica
que algo va mal, y conviene que el cliente lo sepa.

**Un segundo fallo encontrado al hacerlo:** el alias del mensaje venía en el
cuerpo (`payload.getOrDefault("alias", "Anónimo")`), así que cualquiera podía
firmar con el nombre de otro. Ahora se toma del email del token, que es la única
identidad que el servidor puede verificar. El cliente ha dejado de enviarlo.

En el cliente de escritorio, `StompClient` envía el token en el `CONNECT` y pasa
a interpretar las tramas `ERROR`, que antes descartaba en silencio: sin eso, un
envío rechazado por falta de permisos simplemente no aparecía y el usuario no
recibía explicación alguna.

**Pendiente en la interfaz:** el campo "Tu alias" de `chat.fxml` ya no tiene
efecto. Se deja señalado en lugar de retirarlo, pero es un control muerto.

### Validación incompleta de URL en YoutubeToMp4

Una sola alerta, en la línea que detectaba si el usuario había escrito una URL
en lugar de `csv` o `manual`:

```python
if modo.startswith("http://") or ... or "youtube.com" in modo or "youtu.be" in modo:
```

Buscar `"youtube.com"` dentro de la URL entera parece equivalente a comprobar el
dominio y no lo es. La URL completa contiene partes que controla quien la
escribe —ruta, parámetros, fragmento—, así que
`https://youtube.com.sitio-falso.net/x` y `https://malo.net/?ref=youtube.com`
pasan el filtro sin ser de YouTube.

Ahora bien, **esa línea concreta no era un control de seguridad**: si acierta,
pasa al modo manual, que vuelve a pedir la URL. El fallo real estaba en otro
sitio y CodeQL no lo señalaba: **ni el modo interactivo ni el CSV comprobaban el
destino**. El interactivo solo exigía que empezara por `http://` o `https://`, y
el CSV no comprobaba nada.

Corregido con `es_url_de_youtube()`, que analiza la URL con `urlparse` y compara
el **host**, no la cadena completa. Dos detalles que hacen que funcione:

- Se exige que el esquema sea `http` o `https`, lo que descarta `file://` y
  `javascript:`.
- La coincidencia por subdominio compara con el punto delante
  (`host.endswith(".youtube.com")`). Sin ese punto, `mi-youtube.com` pasaría.

La validación se colocó dentro de `descargar_video_mp4()`, que es el punto por
el que pasan los dos modos, en lugar de repetirla en cada punto de entrada:
repartirla es como se acaba olvidando en uno de ellos.

Verificado con 14 casos, incluidos los cuatro que el filtro anterior aceptaba
indebidamente. Los 14 pasan.

Con esto quedan cerradas las nueve familias **de la lista inicial**. Ver más
abajo: al revisar el listado después aparecieron diez alertas más, dos de ellas
de familias que se creían cerradas.

### Migración de Karma a Vitest en TaskHub Angular

No viene de una alerta de CodeQL sino de Dependabot: la cadena vulnerable de
`brace-expansion` entraba por Karma, el ejecutor de tests. Angular 21 usa Vitest
por defecto y ofrece guía de migración, así que en vez de perseguir la
dependencia se retiró la rama entera.

- El builder pasa de `@angular/build:karma` a `@angular/build:unit-test`. Vitest
  no lanza un navegador: ejecuta en Node y simula el DOM con jsdom.
- El builder nuevo no admite opciones de compilación en el target de test
  (`polyfills`, `assets`, `styles`), que ya estaban en el de `build`. La única
  que no estaba, `zone.js/testing`, no hace falta: el único test no usa
  `fakeAsync` ni `waitForAsync`. Si algún día se usan, hay que añadir
  `zone.js/plugins/vitest-patch`.
- Como el proyecto tiene SSR, se añadió una configuración de build `testing` que
  desactiva `ssr` y `outputMode: server`. Sin ella, el builder habría usado
  `development`, que arrastra el servidor a los tests.
- `tsconfig.spec.json` pasa de tipos `jasmine` a `vitest/globals`.

El fichero de test no se tocó: usa `describe`, `it`, `expect`, `toBeTruthy` y
`not.toBeNull`, todo compatible. Existe un schematic oficial
(`refactor-jasmine-vitest`) para convertir espías y matchers de Jasmine, pero
aquí no había nada que convertir.

**Resultado:** los 2 tests pasan en Vitest y las vulnerabilidades de npm en ese
proyecto **bajan de 12 a 3**, desapareciendo las seis de severidad alta. El
árbol de dependencias pasa de 668 a 519 paquetes.

Desinstalar Karma no bastó por sí solo. Tras hacerlo, `npm audit` seguía
señalando la cadena `brace-expansion → minimatch → glob → karma →
@angular/build`. La causa se vio en el `package.json` de `@angular/build`:

```json
"peerDependencies":     { "karma": "^6.4.0", "vitest": "^4.0.8" },
"peerDependenciesMeta": { "karma": { "optional": true }, "vitest": { "optional": true } }
```

Angular declara **ambos runners como peers opcionales**, para que cada proyecto
instale solo el que use. npm no instala los peers opcionales, así que ese Karma
no lo necesitaba nadie: era un resto que sobrevivía en el `package-lock.json` de
cuando sí era dependencia directa. `npm uninstall` retira la declaración pero no
purga el árbol. Se resolvió regenerando `node_modules` y el `package-lock.json`
desde cero.

La lección, que vale para cualquier proyecto de npm: **desinstalar un paquete no
garantiza que salga del árbol**. Mientras siga en el bloqueo, sus dependencias
transitivas siguen instaladas y siguen contando en la auditoría.

**Queda abierta a propósito** la cadena
`@angular/cli → @modelcontextprotocol/sdk → @hono/node-server` (3 moderadas). El
único arreglo que ofrece npm es retroceder `@angular/cli` a la 21.0.4. Mismo
criterio que las otras alertas bloqueadas aguas arriba: no se descarta, se deja
abierta para que se cierre sola cuando Angular actualice.

**No se ejecutó `npm audit fix --force` en ningún momento.** Proponía instalar
`@angular/build@19.1.9` y `@angular/cli@21.0.4`, es decir, deshacer la
actualización a Angular 21 que costó dos rondas de `ng update`. Retroceder de
versión no es corregir una vulnerabilidad.

**Un hallazgo de camino.** La instalación falló primero con `ERESOLVE`: Vitest 4
exige `@types/node` 20, 22 o 24 en adelante, y el proyecto declaraba `^18.18.0`
mientras el Node realmente instalado es el **22.16.0**. Llevaba tiempo
compilándose con los tipos de una versión de Node que no se usa, y que además ya
está fuera de soporte. Se alineó a `^22`, la que coincide con el runtime: unos
tipos más modernos que el intérprete permitirían usar APIs inexistentes en la
máquina, y el fallo aparecería en ejecución en lugar de al compilar.

Se resolvió subiendo la dependencia, **no** con `--force` ni
`--legacy-peer-deps`: el conflicto era real, no un aviso espurio.

**Nota:** la propia documentación de Angular marca como *experimental* la
migración de un proyecto existente a Vitest.

### python-jose sustituido por PyJWT en TaskHub (FastAPI)

Primera de las alertas de Dependabot abordadas una a una. `python-jose 3.3.0`
acumulaba una alerta **crítica** —confusión de algoritmos con claves OpenSSH
ECDSA, que permite forjar tokens— y una moderada de denegación de servicio.

**La crítica no era explotable aquí, y conviene dejarlo escrito.** Ese ataque
necesita que el servidor verifique con una clave ECDSA y que el atacante firme
con HS256 usando esa clave pública como secreto HMAC. Este proyecto usa un
secreto simétrico y, sobre todo, fija la lista de algoritmos en el descifrado:

```python
jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

Ese `algorithms=` es precisamente la defensa contra la familia de ataques de
confusión de algoritmos: impide que el servidor use el `alg` que venga en la
cabecera del token. Estaba bien hecho desde el principio.

Aun así se corrigió, porque bastaría con cambiar `ALGORITHM` en el `.env` para
que dejara de ser teórico.

**Se eligió migrar a PyJWT en lugar de subir a `python-jose 3.5.0`**, que habría
sido una línea. El motivo no es la vulnerabilidad concreta sino el historial:
python-jose pasó **cuatro años sin publicar versión** —3.3.0 en 2021, 3.4.0 en
2025— y en ese hueco arrastró la confusión de algoritmos sin corregir. Subir de
versión arregla el fallo de hoy pero no el riesgo de cadena de suministro. La
documentación oficial de FastAPI dejó de recomendarlo por lo mismo.

Y unifica: `LeaderBoard_Unity` ya usaba PyJWT, así que ahora hay **una sola
librería de JWT** en el repositorio en lugar de dos que hacen lo mismo.

El cambio son tres líneas: el import, el tipo de excepción capturada y la
dependencia. Las llamadas a `encode` y `decode` tienen firma idéntica en ambas
librerías. Se retiró el extra `[cryptography]`, innecesario con HS256, lo que
elimina también `ecdsa`, `rsa` y `pyasn1` del árbol.

**Verificado con cinco pruebas contra el servidor en marcha**, no solo con el
caso feliz:

| Prueba | Resultado |
|---|---|
| Token válido | 200 |
| Sin cabecera `Authorization` | 401 |
| Cadena que no es un token | 401 |
| Firma alterada en un byte | 401 |
| **`sub` cambiado de `prueba1` a `admin`, firma original intacta** | **401** |

La última es la que de verdad importa: comprueba la propiedad que hace útil un
JWT, que el contenido no se puede modificar sin invalidar la firma. Debería
estar en el CI.

**Un error metodológico digno de recordar.** El primer intento de alterar la
firma cambió su último carácter, de `...Erno` a `...Ernp`, y el servidor
respondió 200. Parecía que la autenticación estaba rota. No lo estaba: una firma
HMAC-SHA256 son 32 bytes, que en base64url ocupan 43 caracteres, y el último
grupo de 3 caracteres codifica solo 2 bytes. **Los 2 bits sobrantes se
descartan**, y `o` y `p` se diferencian justo en uno de ellos. Ambas cadenas
decodifican a los mismos 32 bytes: el token era auténtico y el servidor hizo lo
correcto.

Es el tercer caso en dos días en que la herramienta o la prueba dicen algo que
no es —tras las clases duplicadas de CodeQL y las alertas fantasma de
Dependabot—. Sin comprobar los bytes, se habría "arreglado" código que
funcionaba.

**Anotado y no corregido:** `datetime.utcnow()` está obsoleto desde Python 3.12.
Funciona correctamente con PyJWT, que interpreta el datetime ingenuo como UTC,
así que no es un fallo. Se deja para cuando toque.

#### python-multipart y python-dotenv en el mismo proyecto

`python-multipart` 0.0.12 → 0.0.32 y `python-dotenv` 1.0.1 → 1.2.2.

`python-multipart` acumulaba cuatro alertas altas, y conviene separar cuál
importaba. La de **escritura arbitraria de ficheros indica en su propio título
«via Non-Default Configuration»**: requiere una configuración que FastAPI no
usa, así que no aplicaba. Las otras tres son denegación de servicio al parsear
formularios —cabeceras de parte sin límite, frontera malformada, parseo
cuadrático de la cadena de consulta— y esas **sí** eran alcanzables.

El motivo es dónde interviene el paquete: FastAPI lo usa para leer formularios,
y aquí eso ocurre en `OAuth2PasswordRequestForm`, en `routers/auth.py`. Es
decir, en el **login**, que es una ruta pública y sin autenticar. Cualquiera
podía enviarle un formulario deformado sin tener cuenta.

El salto de versión es grande, así que antes de aplicarlo se comprobó en un
entorno aparte que `OAuth2PasswordRequestForm` sigue funcionando con FastAPI
0.115.0 y `python-multipart` 0.0.32, en `application/x-www-form-urlencoded` y en
`multipart/form-data`, y que sigue devolviendo 422 cuando falta un campo.

Verificado después contra el servidor real: `POST /auth/token` con credenciales
incorrectas devuelve 401 y con las correctas devuelve el token. El 401 también
cuenta como prueba: significa que el formulario se parseó bien y la comparación
se hizo; si el parseo hubiera fallado, el error habría sido otro.

### Jackson al día en radiostack-admin

`jackson-databind` 2.15.2 → 2.22.0, con dos altas: saltos del validador de tipos
polimórficos que permiten instanciar clases arbitrarias.

**Lo interesante fue cómo hacerlo, no la versión.** El pom padre importa el BOM
de Spring Boot, que fija las versiones de Jackson para **todos** los módulos.
Subir aquí solo `jackson-databind` habría dejado su `jackson-core` transitivo en
la versión que marca Spring Boot, y esa mezcla de versiones distintas entre
artefactos del mismo grupo es exactamente la que producía las alertas separadas
de `jackson-core` en los proyectos que se retiraron.

Peor aún: **ese desajuste no rompe la compilación**. Las clases se encuentran y
el build pasa; falla en tiempo de ejecución, al deserializar.

Se resolvió importando el **BOM de Jackson en el propio módulo**, que mantiene
`databind`, `core` y `annotations` en bloque y solo afecta a este módulo.

No se subió Jackson en todo el proyecto a propósito: `radiostack-api` es una
aplicación Spring Boot y debe usar el Jackson que Spring espera. `radiostack-admin`
es un cliente JavaFX independiente que solo usa `ObjectMapper` para leer el JSON
de la API, así que ahí el salto está aislado. **Es el mismo criterio aplicado a
PyTorch: actualizar hasta donde el cambio está contenido, y no más allá.**

Verificado con `dependency:tree`, que es lo que compilar no demuestra:

```
jackson-databind:jar:2.22.0
+- jackson-annotations:jar:2.22
\- jackson-core:jar:2.22.0
```

(El `2.22` de `annotations` no es un desajuste: Jackson publica ese artefacto con
versión de dos componentes en las entregas `.0`.)

#### El bug que la prueba destapó: el cliente nunca pudo iniciar sesión

Al arrancar la API y el cliente JavaFX juntos para probar el parseo, el login
falló:

```
Unrecognized field "activo" (class com.radiostack.admin.client...LoginResponse$UserInfo)
```

**No lo causó la actualización.** El historial lo confirma: el `UsuarioDTO` del
servidor devuelve el campo `activo` desde el commit original del proyecto
(`7076f35`), y la clase `UserInfo` del cliente nunca lo declaró. El
`ObjectMapper` del cliente estaba sin configurar, y su comportamiento por
defecto es fallar ante campos desconocidos. Es decir: **el cliente de RadioStack
no ha podido iniciar sesión desde el primer día.** Nadie lo notó porque nadie
había arrancado los dos módulos a la vez.

Que apareciera *ahora* es, irónicamente, la prueba de que Jackson 2.22 funciona:
el error solo puede producirse después de recibir y empezar a leer el JSON.

Corregido en el sitio correcto —el `ObjectMapper` del cliente, no la clase
`UserInfo`— con `FAIL_ON_UNKNOWN_PROPERTIES = false`. Añadir el campo a mano
habría dejado el mismo fallo latente para el próximo campo que el servidor
añadiese. Un cliente HTTP debe tolerar que el servidor incorpore campos: es la
forma normal de evolucionar una API sin romper a quien la consume.

Verificado de extremo a extremo: la API arranca (Tomcat en 8080, Flyway valida,
PostgreSQL conecta), el cliente hace login con `admin@radiostack.local` y entra
al panel de administración.

Es el duodécimo caso del patrón de esta revisión —algo que compila pero que
nunca se ejercitó— y el mejor argumento para el CI pendiente: **arrancar los dos
módulos juntos una sola vez** habría detectado que el cliente no podía loguearse.

### Conector de MySQL: cambio de artefacto, no de versión

`Java/BatchProcessor` declaraba `mysql:mysql-connector-java:8.0.33`, con una alta
(*MySQL Connectors takeover*). Este no se arregla subiendo la versión: **ese
artefacto está descatalogado**. Oracle movió el conector a
`com.mysql:mysql-connector-j` en 2022 y dejó de publicar el anterior, que se
quedó congelado en la 8.0.33 con la vulnerabilidad sin parchear. Subir el número
no habría servido de nada, porque no hay versiones nuevas de las coordenadas
viejas.

Cambiadas las coordenadas a `com.mysql:mysql-connector-j` y retirada la
`<version>`: el proyecto hereda de `spring-boot-starter-parent`, que gestiona
ese artefacto y lo mantiene al día.

**El cambio es transparente** porque el nombre de la clase del driver no cambia
en la práctica: `application.properties` ya usaba `com.mysql.cj.jdbc.Driver`, que
es la clase del artefacto nuevo. No hubo que tocar ninguna configuración.

### Apache POI en XlsxToCsvConverter

`poi-ooxml` 5.3.0 → 5.5.1 (una moderada de validación de entrada al parsear
OOXML). `poi` y `poi-ooxml` se subieron en bloque mediante una propiedad
`poi.version` compartida: `poi-ooxml` depende de `poi`, y versiones distintas del
mismo grupo dan errores de enlace en ejecución. Salto dentro de la serie 5.x y el
código solo usa `XSSFWorkbook` y `ss.usermodel`, así que no hubo cambios de
código.

**Un hallazgo de camino, el decimotercero del patrón:** al compilar falló con
`invalid target release: 23`. El pom declaraba `maven.compiler.target=23`, una
versión de Java que el JDK instalado (21) no puede generar. Es decir, **este
proyecto no compilaba en la máquina donde vive**, y nadie lo había notado porque
nadie lo había compilado. Bajado a 21, que es el JDK real y le sobra a POI, que
solo requiere Java 8.

### JasperReportExecutor: reescritura del pom y compilación al vuelo

Cinco alertas concentradas en un proyecto del portfolio (el TFG): iText 2.1.7 de
2009 (XXE), dos de `jasperreports`, POI y el driver de PostgreSQL. Como el
proyecto **se ejecuta de verdad** —genera informes contra PostgreSQL y exporta a
PDF—, no bastaba con que compilara: tenía que seguir produciendo los informes.

**El pom estaba roto, no solo desactualizado.** Declaraba a mano iText, POI,
groovy y commons, y **dos versiones distintas de `jasperreports`** (6.18.1 y
5.6.0) más `poi`/`poi-ooxml` repetidos tres veces. Maven se queda con la primera
versión de cada uno e ignora el resto, así que medio pom no hacía nada.

El código solo usa `net.sf.jasperreports` y JDBC; iText y POI los emplea
JasperReports por debajo. Así que se reescribió el pom a **dos dependencias**:
`jasperreports 6.21.5` (última de la serie 6.x, que conserva la API de
exportadores del código) y `postgresql 42.7.7`. Lo demás viene transitivo y
parcheado. El dato que hizo esto viable: **JasperReports 6.21.5 ya no usa iText,
usa OpenPDF** (`com.github.librepdf:openpdf`, el fork libre que corrige los fallos
de aquella iText 2.1.7), y trae POI 5.4.1 y Jackson 2.17 dentro. Verificado con
`dependency:tree`: `com.lowagie:itext` **desaparece del árbol**.

**Dos problemas destapados al ejecutarlo, ninguno de la actualización en sí:**

Las plantillas declaraban `language="groovy"`, y al arrancar fallaban con
`CompilationFailedException`: el pom viejo traía `groovy-all:2.5.14` para eso, y
JasperReports 6.21.5 declara Groovy como opcional (no se arrastra). Las
expresiones de los informes son Java válido —`$F{campo}`, `new java.util.Date()`,
`$V{REPORT_COUNT}%2 == 0`—, sin nada de Groovy, así que se pasaron las dos
plantillas a `language="java"`. JasperReports compila Java con su propio `ecj`
incluido, sin dependencia extra.

Y el programa cargaba ficheros **`.jasper` precompilados**, que llevan grabada
dentro la versión con la que se compilaron (y su Groovy). Eran el origen del
acoplamiento: al cambiar la librería, dejaban de cargarse. Se reescribió para
**compilar los `.jrxml` al vuelo con `JasperCompileManager`** en cada arranque,
de modo que la plantilla siempre se compila con la versión que corre. Se
retiraron los `.jasper` obsoletos.

De paso se corrigió un fallo latente en la carga: usaba
`getResource().getPath()`, que devuelve rutas inválidas en Windows (prefijo
`/C:/`, `%20` en los espacios). Cambiado a `getResourceAsStream`, que habría dado
problemas en cuanto la ruta del proyecto tuviera un espacio.

**Verificado ejecutándolo:** conecta a PostgreSQL, compila las dos plantillas y
genera `informePuntuaciones.pdf` e `informeJugadores.pdf`. De 200 líneas de pom a
60, de cinco vulnerabilidades a cero, y el proyecto queda **menos acoplado que
antes** —ya no depende de ficheros precompilados con una versión concreta—.

### PyTorch en AI_DuoTalk

`torch` 2.7.1 → 2.13.0. La 2.7.1 arrastraba varias alertas moderadas y bajas de
corrupción de memoria. Conviene aclarar que **aquí no estaba la crítica**: el
`torch.load` con RCE (`weights_only`) es de FPS-AI-Toolkit con torch 2.1.0, no de
este proyecto.

Antes de tocar la versión se comprobó qué la ataba: **nada la fijaba**. El código
no importa `torch` directamente —lo usan Whisper (transcripción) y Silero (voz)
por debajo—, `openai-whisper` pide `torch` sin rango de versión, y `gpt4all` ni
siquiera depende de torch. Así que subir a la última estable (2.13.0) era seguro
por el lado de las dependencias.

**Es la única actualización de esta ronda que no se pudo verificar en el
sandbox:** torch pesa cientos de MB y necesita la máquina real. Se probó
ejecutando AI_DuoTalk de extremo a extremo —Whisper transcribe y Silero
sintetiza voz—, que es lo que ejercita torch de verdad; que `pip install`
termine no habría demostrado nada, porque el modelo de Silero se carga vía
`torch.hub` en tiempo de ejecución.

**Queda `torch` de FPS-AI-Toolkit sin tocar** (entrada aparte): allí es
`torch==2.1.0+cu121`, una compilación CUDA que no viene de PyPI, y actualizarla
exige conocer la GPU y mover torch, torchvision y torchaudio en bloque. Sigue
excluida en `dependabot.yml`.

### FPS-AI-Toolkit: PyTorch CUDA y Pillow

El proyecto con más alertas de toda la revisión: **24** (Pillow 13, torch 11),
más de la mitad de las 46 que quedaban. Es una herramienta de visión por
ordenador del portfolio, y usa GPU, así que la actualización dependía del
hardware real de la máquina.

**Pillow** 12.2.0 → 12.3.0. Las 13 alertas eran de vulnerabilidades publicadas
después de la 12.2.0 —escrituras fuera de límites, bombas de descompresión,
inyección de comandos en `WindowsViewer`—, todas corregidas en la 12.3.0.

**El stack de PyTorch** pasó de `torch/torchvision/torchaudio 2.1.0/0.16.0/2.1.0
+cu121` a `torch/torchvision 2.6.0/0.21.0 +cu124`. Tres decisiones:

- **De cu121 a cu124.** Aunque el toolkit CUDA instalado (`nvcc`) es 12.1, el
  driver de NVIDIA es retrocompatible: torch trae sus propias librerías CUDA y
  solo necesita un driver suficientemente moderno. Verificado en la máquina:
  `torch.cuda.is_available()` da `True` sobre la RTX 4060 Ti (sm_89). La 2.6.0 es
  además la versión que arregla por defecto el `torch.load` con RCE
  (`weights_only`), que era la alerta crítica de este proyecto.

- **Se retiró `torchaudio`.** Estaba en el `requirements.txt` (2.1.0+cu121) pero
  el código no usa audio: es un proyecto de visión, y `torchaudio` no llegó a
  instalarse siquiera. Lo requiere `ultralytics` (YOLO) a través de torch y
  torchvision, nunca torchaudio. Fuera ~100 MB de dependencia muerta.

- **Los tres —ahora dos— artefactos se fijan emparejados** (torch 2.6.0 ↔
  torchvision 0.21.0). Mezclar versiones del stack de torch da errores en
  ejecución, no al instalar. Documentado en el propio `requirements.txt`, con la
  orden de instalación desde el índice de PyTorch (no PyPI) porque las builds
  `+cuXXX` no están en PyPI.

`torch` sigue **excluido en `dependabot.yml`** a propósito, y esto explica por
qué: Dependabot no entiende el sufijo `+cu124` ni el índice alternativo de
PyTorch, así que propondría la build de CPU de PyPI y rompería la GPU.
Actualizarlo requiere hacerlo a mano, como aquí.

**Verificado ejecutándolo:** las versiones quedan emparejadas con CUDA activa, y
el toolkit arranca con YOLO detectando en GPU.

### FPS-AI-Toolkit: el stack de PyTorch con CUDA

La mayor concentración de la revisión: 24 alertas (13 de Pillow, 11 de torch),
más de la mitad de todo lo que quedaba. Un toolkit de visión con YOLO que se
ejecuta en la GPU, así que compilar no bastaba: tenía que seguir detectando.

**PyTorch.** Estaba en `torch==2.1.0+cu121` con `torchvision` y `torchaudio`
emparejados, con una crítica (`torch.load` con RCE) y varias altas de corrupción
de memoria. Nada del proyecto fija la versión —la usa `ultralytics` por debajo, y
solo pide `torch>=1.8.0`—, así que se pudo subir.

El dato que lo decidió: la máquina ya tenía **torch 2.6.0+cu124** instalado y
funcionando. El driver de NVIDIA es retrocompatible, así que la build cu124 corre
sobre una RTX 4060 Ti aunque el toolkit `nvcc` sea 12.1: torch trae sus propias
librerías CUDA y solo necesita un driver moderno. Se alineó el `requirements.txt`
a esa versión real (2.6.0+cu124 / torchvision 0.21.0+cu124), que además es donde
se corrige por defecto el `torch.load` con RCE. Verificado:
`torch.cuda.is_available()` es `True` y ve la GPU.

**Pillow** 12.2.0 → 12.3.0. Aquí sí había parche: las 13 alertas eran de
vulnerabilidades publicadas después de la 12.2.0, y la 12.3.0 las cierra.

**Tres defectos destapados al ejecutarlo, todos del patrón dominante:**

- `torchaudio` estaba en el `requirements.txt` pero **el único uso era un import
  muerto** (`from torchaudio.models.wav2vec2 import wav2vec2_base`), sobrante de
  una prueba antigua: se importaba y no se usaba en ninguna parte. Es un proyecto
  de visión, no de audio. Se borró el import y se retiró torchaudio del
  `requirements`, ~100 MB de dependencia inútil menos.
- `dxcam` (captura de pantalla rápida) **se importaba pero faltaba en el
  `requirements.txt`**, así que una instalación limpia no arrancaba. Añadido.
- Ambos fallos solo aparecieron **ejecutando** el programa, uno tras otro: el
  import de torchaudio tumbaba el arranque en la línea 34, y una vez quitado,
  faltaba dxcam en la 39.

Son los hallazgos trece y catorce del tipo «declarado pero nunca ejercitado», y
el argumento más claro para el CI pendiente: **un CI que solo importara el módulo
principal** habría cazado los dos sin necesidad de GPU ni de nada más.

**Queda `torch` de AI_DuoTalk ya resuelto aparte; este era el último proyecto
con el stack CUDA.** Verificado ejecutando `MultifuncionFPS.py`: arranca y YOLO
detecta.

### flask-cors 5.0.0 a 6.0.5 en LeaderBoard_Unity

La última entrada de la lista real, y la única de salto de versión mayor, por eso
se dejó para el final. Tres alertas moderadas: coincidencia de rutas
inconsistente y sensibilidad a mayúsculas al casar orígenes.

El salto 5 → 6 endurece precisamente cómo flask-cors casa los patrones de
origen, que es lo que corrige las tres alertas. Podría haber roto una
configuración que dependiera de la laxitud anterior, pero aquí no aplica: el uso
es una sola llamada `CORS(app, methods=[...], origins=Config.CORS_ALLOWED_ORIGINS)`
con la **lista de orígenes vacía**. Sin orígenes que casar, el cambio de
comportamiento no tiene nada que romper. La API de la librería (`CORS(...)`) es
idéntica entre la 5 y la 6.

Verificado: instala limpio y la API arranca. Con esto quedan cerradas las 19
entradas de la lista real de vulnerabilidades, salvo las tres dejadas abiertas a
propósito (sección siguiente).

### Limpieza de validación en gym-app

Tres arreglos en `RegisteredUserController::store`, ninguno de seguridad: código
de validación redundante que se había ido acumulando.

- **`phone_number` se validaba dos veces**: la regla `size:9` y, justo después,
  una comprobación manual con `strlen`. Eliminada la manual; la regla ya lo hace.
- **`sport` era obligatorio para coach mediante un `if` con `filled()`** tras el
  `validate()`. Movido a la propia regla como `required_if:role,coach`, que es lo
  que Laravel ofrece para esto.
- **`Password::uncompromised()` corría también en los tests.** Esa regla consulta
  la API de HaveIBeenPwned por HTTP, así que metía una llamada de red externa en
  la suite: la hacía lenta y dependiente de que el servicio respondiera. Ahora se
  añade solo fuera del entorno `testing`; en producción sigue rechazando
  contraseñas filtradas.

Verificado con `php artisan test`: **25 tests, 61 assertions, todo verde**,
incluido `new users can register`, que ejercita justo esta validación. Los tests
usan SQLite en memoria (por el `phpunit.xml` corregido en su día), así que no
tocan la base de datos de desarrollo.

Los dumps MySQL obsoletos (`gym_app.sql`, `gym_app_v1.0.sql`) que figuraban como
pendientes ya no existen en `docs/sql/`; solo queda el script de PostgreSQL.

**Nota no corregida:** `size:9` valida la longitud, no que sean dígitos —
`"abcdefghi"` pasaría—. El código anterior tenía el mismo comportamiento, así que
no se cambió. Para exigir dígitos sería `digits:9`.

### Acabado: chat.fxml y el README de YoutubeToMp3

**Campo alias muerto retirado.** Tras autenticar el WebSocket de RadioStack, el
servidor firma cada mensaje con el usuario del token, así que el campo "Tu alias"
de `chat.fxml` ya no servía para nada — se dejó en su día señalado como pendiente.
Eliminados el `<TextField fx:id="aliasField">` del fxml y el
`@FXML private TextField aliasField` del controlador. El layout no se resiente:
el campo de mensaje ya tenía `HBox.hgrow="ALWAYS"` y ocupa el hueco. Ojo: el
`alias` que aparece en los mensajes **recibidos** es distinto —es el de quien
envía, que llega del servidor— y se conserva.

**README de YoutubeToMp3 corregido.** Documentaba un `batch_downloader.py` que no
existe, tanto en el árbol de ficheros como en un comando de ejecución. La
descarga masiva por CSV **sí existe**, pero está integrada en `YoutubeToMp3.py`
(función `descargar_desde_csv`), no en un script aparte. Corregidas las dos
referencias para apuntar al script real. Es documentación que mandaba a ejecutar
un fichero inexistente.

**Sobre los READMEs en general:** la tarea preveía escribir READMEs mínimos por
proyecto, pero al revisarlo la mayoría ya los tenía, y bastante completos —los
cuatro TaskHub, casi todos los de Python—. No hacía falta la ronda masiva; solo
la corrección puntual del fantasma de YoutubeToMp3.

### Angular: dependencia muerta retirada, salto a 22 aplazado

La tarea pendiente hablaba de "actualizar Node y las deprecaciones de Angular".
Al revisarlo, ninguna de las dos deprecaciones que se creían pendientes aplicaba:

- **`@angular/platform-browser-dynamic`** figuraba en el `package.json` pero **no
  se importa en ningún sitio**: la aplicación arranca con `bootstrapApplication`
  desde `@angular/platform-browser`, la forma moderna. Era dependencia muerta.
  Retirada.
- **`@angular/animations`** sí se usa, pero mediante `provideAnimations()`, que es
  la API actual y correcta (la usa Angular Material por debajo). La deprecación
  real —las animaciones basadas en `trigger()`/`transition()`, sustituidas por
  `animate.enter`/`animate.leave`— no aparece en el código. Nada que cambiar.

**El salto a Angular 22 se deja aplazado a propósito.** El proyecto está en
Angular 21, que se fijó en su día porque Angular 22 exige Node ≥ 22.22.3 y la
máquina tiene 22.16.0. Pero 21 no es una versión atascada: el `@angular/cli` 21
declara `node: ^20.19.0 || ^22.12.0 || >=24.0.0`, y el 22.16.0 instalado cumple.
Es decir, **Angular 21 funciona con el Node actual**; el requisito de 22.22.3 solo
entra en juego si se salta a 22.

Saltar a 22 obligaría a: subir Node primero, luego `ng update` (un major cada
vez), y volver a probar SSR, Vitest y el flujo de sesión, todo lo cual está
verificado sobre 21. Es una migración mayor sin nada que hoy la empuje —21 es
reciente y está soportado—, así que queda como decisión futura y no como deuda.

**Cuando se aborde:** actualizar Node a ≥ 22.22.3, `ng update @angular/core@22
@angular/cli@22` (con material y cdk en el mismo comando, que deben moverse en
bloque), y re-probar arranque, F5 con sesión y `npm test`.

### Bug de ritmo en unified-chat-widget: mensajes en tanda

Reportado por Juan: antes los mensajes del overlay aparecían de uno en uno, en
orden de llegada; en algún refactor pasaron a mostrarse **todos de golpe**.

La causa es una asimetría entre conectores que quedó al descubierto al retirar la
pool antigua:

- **Twitch y Kick** entregan por evento (`on("ChatMessage")`): un mensaje, una
  llamada, en tiempo real. Gotean solos.
- **YouTube y Rumble** entregan por **sondeo**: cada ciclo (YouTube cada 60 s)
  hacen `messages.forEach(onMessage)` y sueltan de golpe todo lo acumulado.

El diseño original amortiguaba esto con la pool de `utils/globalMessages.js`: los
mensajes se guardaban y el cliente los iba leyendo en orden. Esa pool quedó
comentada al migrar al WebSocket, y `handleMessage` pasó a llamar
`saveAndBroadcastMessage` directamente, sin nada que espaciara las tandas. Con
solo Twitch/Kick no se notaba; al volver a usar Rumble, cada sondeo inundaba el
overlay.

**Corregido** reponiendo el amortiguador del lado del servidor: una cola FIFO
(`broadcastQueue`) en la que `handleMessage` encola, y un temporizador que la
drena **de uno en uno, en orden de recepción**, cada `BROADCAST_INTERVAL_MS`
(1 s, en una sola constante para poder ajustarlo). Es el mismo efecto que daba la
pool, ahora sobre el WebSocket. Los mensajes de sistema (avisos de conexión) se
dejan inmediatos a propósito, por ser esporádicos.

Verificado por Juan con Rumble conectado: los mensajes vuelven a aparecer uno a
uno en orden.

**Limitación conocida:** con un ritmo de entrada sostenido superior a uno por
segundo, la cola acumula retraso respecto al directo. Es el mismo comportamiento
que la pool original (también era una cola); si llega a molestar, se puede
acelerar el drenado cuando la cola supere un umbral.

### Segunda tanda de alertas (avisos nuevos tras la primera limpieza)

Semanas después aparecieron alertas nuevas —unas de avisos publicados esos días,
otras que la reescritura del pom de Jasper no llegó a cubrir—. Clasificadas:

**pgjdbc 42.7.7 → 42.7.12 (corregido).** Dos altas: downgrade silencioso de
channel-binding (CVE-2026-54291) y el PBKDF2 sin límite anterior. La 42.7.7 que
se había puesto seguía afectada (rango `>= 42.7.4, < 42.7.12`). Subida a 42.7.12,
que es donde pgJDBC refuerza la comprobación en su propio código.

**Angular 21.2.18 → 21.2.19 (corregido).** Cuatro altas del propio framework, de
publicación reciente: dos XSS por atributos de manejador de evento en el pipeline
i18n (`@angular/core`, `@angular/compiler`), envenenamiento de caché en
`HttpTransferCache` (`@angular/common`) y XSS de SSR (`@angular/platform-server`).
**El parche es la 21.2.19, dentro de la rama 21** —no obliga a saltar a Angular 22
ni a subir Node—. El `package.json` ya pedía `^21.2.18`, así que el fallo estaba
solo en la versión clavada en el `package-lock.json`; se subió el suelo de todos
los `@angular/*` a `^21.2.19` y se regeneró el lock. Confirma, de paso, que valió
la pena quedarse en 21: la rama sigue recibiendo parches de seguridad.

**JasperReports (abierta a propósito, documentada).** Dos altas de deserialización
con RCE (CVE-2026-6009 y relacionada). **El parche es jasperreports 7.0.7**, y la
6.21.5 que se puso sigue afectada (`< 7.0.7`). No se sube a 7.x porque es un cambio
mayor —nueva estructura de módulos y API— que obligaría a rehacer el pom y
reprobar la generación de informes, que ya dio guerra con Groovy.

La decisión de dejarla abierta se apoya en que **el vector no existe en este
proyecto**: la RCE por deserialización necesita datos serializados no confiables
—típicamente un `.jasper` de origen externo—, y el ejecutor solo compila
plantillas `.jrxml` propias desde `resources`, no carga `.jasper` ajenos ni
deserializa entrada de usuario, y se ejecuta en local contra la base de datos del
propio autor. Es un TFG de escritorio, no un servicio que reciba informes de
terceros.

**Se deja abierta, no se descarta en GitHub.** Y con una advertencia honesta: un
aviso High de RCE abierto lo ve cualquiera que mire la pestaña de seguridad,
aunque en este uso no sea explotable. Si el proyecto llegara a exponerse como
servicio, la migración a 7.0.7 pasa a ser obligatoria.

### Pipeline de CI (GitHub Actions)

La conclusión que más se repitió en toda la revisión: **catorce fallos del tipo
"declarado pero nunca ejercitado"** —imports rotos, `requirements.txt`
incompletos, poms que no compilaban, un `.env` con valores de ejemplo, un cliente
que nunca podía loguearse—, todos encontrados a mano al ejecutar cada proyecto, y
todos los habría cazado un CI el primer día. `.github/workflows/ci.yml` es ese
CI.

**Alcance: ligero y universal, no "construir todo".** El monorepo tiene ~50
unidades construibles de cuatro ecosistemas, muchas experimentales; un CI que las
compilara y testeara todas estaría en rojo permanente (la mitad no construyen
limpias, y las que sí necesitan base de datos y secretos). En vez de eso, el
pipeline hace comprobaciones baratas que atrapan justo la clase de fallo que se
coló:

- **`python-syntax`** — `py_compile` de los 128 `.py` propios (excluye venvs y
  código vendorizado). Verificado a cero antes de crear el workflow.
- **`js-syntax`** — `node --check` de los 32 `.js` propios. Habría cazado el
  import muerto de `torchaudio`... el equivalente JS: el import roto de
  unified-chat-widget.
- **`config-lint`** — JSON y YAML bien formados. **Excluye a propósito los
  `tsconfig*.json` de Angular**, que son JSONC (con comentarios) y darían falso
  positivo con un validador de JSON estricto.
- **`regression-guard`** — falla si reaparecen dos patrones ya corregidos:
  `str(e)` en respuestas HTTP (fuga de información) y `console.log` de
  `process.env` (fuga de secretos). Hoy ambos a cero.
- **`maven-compile`** — `mvn -DskipTests compile` (sin BD ni secretos) de los
  cinco proyectos Java mantenidos, con JDK 21. Habría cazado el `target 23`
  imposible de XlsxToCsvConverter o el pom ilegible de ApiService.

Todos los jobs se verificaron en verde **antes** de crear el workflow: 128 `.py`
y 32 `.js` sin errores de sintaxis, JSON válidos (salvo los tsconfig excluidos),
y los dos patrones peligrosos a cero. El CI nace verde y a partir de ahí protege
contra regresiones.

Lo que **no** cubre, a propósito: tests con base de datos y arranque de
servicios. Eso son jobs por proyecto, con contenedores y secretos, y se añadirán
aparte si algún proyecto vitrina lo justifica.

### Flask 3.0.3 → 3.1.3 en LeaderBoard_Unity

Un aviso Low: la sesión no añade la cabecera `Vary: Cookie` en ciertos accesos,
lo que puede provocar que una caché sirva una respuesta con sesión a otro
usuario. Corregido en Flask 3.1.0; subido a 3.1.3.

Comprobada la compatibilidad con la Werkzeug 3.1.8 ya instalada (van acopladas)
en un entorno aparte antes de aplicarlo: arranca, la sesión funciona y **la
respuesta ya incluye `Vary: Cookie`**, que es justo lo que faltaba.

### PyTorch: 8 avisos abiertos a propósito (parche fuera de alcance CUDA)

Ocho avisos en `torch` (FPS-AI-Toolkit), Moderate y Low: corrupción de memoria en
funciones concretas (`unpack_sequence`, `lstm_cell`, `jit.script`,
`pad_packed_sequence`...) y un DoS local. El parche es **torch 2.9.1**.

Se dejan abiertas por dos razones que se refuerzan:

1. **El parche no existe para la CUDA de esta máquina.** El proyecto usa builds
   `+cu124` (RTX 4060 Ti), y la rama cu124 de PyTorch se quedó en la 2.6.0 —no
   hay 2.7/2.8/2.9 en cu124, cu126 ni cu128 para Windows—. Subir a 2.9.1
   obligaría a cambiar de rama CUDA y reprobar todo el stack GPU + ultralytics.
2. **Son todas de vector Local.** Requieren que el atacante ya tenga acceso a la
   máquina y consiga pasar tensores manipulados a esas funciones internas. En una
   herramienta de escritorio que ejecuta su propio autor con sus propios datos,
   el riesgo práctico es nulo: quien pudiera explotarlo ya estaría dentro.

Coste de "arreglar" (cambio de CUDA + reprueba completa de GPU) desproporcionado
frente a un riesgo local inexistente. Además, PyTorch publica avisos de esta
clase de forma continua, así que subir de versión solo cambiaría unos números por
otros. **No se descartan en GitHub; se dejan abiertas y documentadas.**

### undici forzada a 7.29.0 en TaskHub Angular (overrides)

Cinco avisos en `undici` (uno High, cuatro Moderate): filtración cross-user por
directivas de caché, inyección CRLF, inyección de atributos de cookie,
desincronización de respuestas. Todas **transitivas y de scope Development**:
undici entra por `@angular/build` (servidor de desarrollo), por `jsdom` (tests) y
por `node-gyp` (vía el CLI). **No llega al bundle de producción.**

El parche es undici 7.29.0, pero `@angular/build` **clava la 7.28.0 exacta**
(`"undici": "7.28.0"`, sin rango), así que Dependabot no podía actualizarla:
bloqueada aguas arriba como `@hono`.

A diferencia de `@hono`, aquí sí cabía forzarla con un **`overrides`** en el
`package.json` (`"undici": "7.29.0"`). Es seguro porque es un salto de parche
—un único arreglo en `lib/util/cache.js`— sobre herramientas que no se despliegan.
Verificado: `npm ls undici` muestra las tres rutas en 7.29.0 (`overridden` /
`deduped`), el build compila y `npm audit` baja de 5 a 3 (las 3 restantes son las
moderadas de `@hono`/tooling, bloqueadas aguas arriba).

Anotado en el propio `package.json`: si un futuro `@angular/build` ya trae
undici ≥ 7.29, este override sobra y debe retirarse.

### Guzzle 7.15.1 → 7.15.2 en gym-app

Dos avisos recientes en `guzzlehttp/guzzle`, dependencia **directa** del proyecto
(`composer.json: ^7.8`): host no canónico que burla comprobaciones basadas en
host (CVE-2026-69246, High) y dominio de cookie que conserva alcance de
subdominio (Moderate). Es el primer arreglo del ecosistema **Composer/PHP** en
toda la revisión.

El parche es la 7.15.2, dentro de `^7.8`, así que **no hizo falta tocar el
`composer.json`**: solo actualizar el `composer.lock` con
`composer update guzzlehttp/guzzle --with-all-dependencies`.

**Alcance real bajo:** el propio aviso dice que solo afecta a aplicaciones que
construyen la URI de la petición a partir de entrada no confiable. gym-app usa
Guzzle por debajo del cliente HTTP de Laravel, no fabrica URLs con datos de
usuario. Aun así el arreglo es un salto de parche de coste y riesgo nulos, así
que se aplica sin más.

**Obstáculo de entorno, no del proyecto:** `composer update` fallaba con
`curl error 60 (unable to get local issuer certificate)`. No era un bundle de CA
ausente —apuntar `curl.cainfo`/`openssl.cafile` al `cacert.pem` de Laragon no lo
resolvió—, sino el **antivirus interceptando HTTPS**: presenta un certificado
firmado por su propia raíz, que está en el almacén de Windows (por eso el
navegador confía) pero no en el `cacert.pem` que usa el OpenSSL de PHP. Es el
mismo problema que ya apareció con Avast semanas atrás. Se resolvió desactivando
el escaneo HTTPS del antivirus durante la actualización. Queda anotado que el
`php.ini` de Laragon no tiene `curl.cainfo` configurado.

### Alertas dejadas abiertas a propósito (bloqueadas aguas arriba)

Tres alertas no se corrigen porque el fallo está en una dependencia transitiva
de un paquete de terceros, varios niveles por debajo de lo que el repositorio
controla. En ninguna de las tres hay un fichero propio donde documentarlo —el
código vulnerable vive en `node_modules`, que no se versiona—, así que la
decisión queda registrada solo aquí. **No se descartan en GitHub: se dejan
abiertas para que se cierren solas cuando el mantenedor de aguas arriba
actualice.** Es el criterio de *corregir en lugar de silenciar* llevado a su
consecuencia lógica: si no hay corrección posible, tampoco se silencia.

- **`brace-expansion` en `unified-chat-widget`** (alta, DoS). Entra por una
  cadena de siete niveles: `@retconned/kick-js` → `puppeteer-extra-plugin-stealth`
  → … → `rimraf@3` → `glob@7` → `minimatch@3` → `brace-expansion@1.1.16`.
  `npm audit fix` responde literalmente *"No fix available"*: `kick-js` fija
  versiones antiguas de puppeteer, y estas fijan el resto de la cadena. Es una
  dependencia **de desarrollo** —puppeteer automatiza el navegador para leer el
  chat de Kick, no llega a producción— y el DoS solo se dispara con patrones de
  llaves construidos por un atacante, cosa que aquí no ocurre. Forzarla con
  `overrides` inyectaría una versión no probada siete niveles por encima; se
  descartó.

- **`@hono/node-server` en `TaskHub` Angular** (moderada). Cadena
  `@angular/cli` → `@modelcontextprotocol/sdk` → `@hono/node-server`. El único
  arreglo que ofrece npm es retroceder `@angular/cli` a la 21.0.4, deshaciendo la
  actualización a Angular 21.

- **Dos dependencias del build de Angular** ya documentadas en la cabecera de
  este archivo: sus únicas "correcciones" son retrocesos de versión.

El patrón común: **la única corrección disponible es peor que el problema**
—retroceder una versión mayor, o inyectar un paquete no probado en una cadena
ajena—. Todas se resolverán solas cuando el proyecto de aguas arriba publique.

### El listado de Dependabot se sincronizó

Las alertas fantasma descritas más abajo desaparecieron por sí solas: **de 202 a
46**, y las 46 corresponden a ficheros que existen. Ya no aparece
`Java/Spring/SpringBatch/`, `Java/Spring/SpringBoot/`, `Python/TaskHub/` ni los
paquetes no declarados de `GPTDevTeam`.

El reparto de lo que queda es más útil que el total:

| Proyecto | Alertas |
|---|---|
| `FPS-AI-Toolkit` (Pillow 13 + torch 11) | **24** |
| `JasperReportExecutor` (itext, jasperreports ×2, pgjdbc, poi) | 5 |
| `radiostack-admin` (jackson, ya corregidas) | 5 |
| `AI_DuoTalk` (torch) | 4 |
| `LeaderBoard_Unity` (flask-cors ×3, flask) | 4 |
| Sueltas (mysql-connector, poi, brace-expansion, @hono) | 4 |

**Tres proyectos concentran 33 de las 46.** Y en los tres la actualización no es
viable por motivos distintos: Pillow ya está en la última versión publicada,
torch está excluido por el asunto de la compilación CUDA, e iText 2.1.7 lleva
abandonado desde 2009 y migrar significa reescribir con iText 7 u OpenPDF.

Es decir: **el techo de lo alcanzable actualizando dependencias está en unas 13
alertas.** Bajar de ahí exige decidir si esos proyectos siguen siendo necesarios,
que es una decisión de alcance del repositorio, no de mantenimiento.

### BackCount y FFMPEG_UI

Dos proyectos pequeños, resueltos de una vez.

**`StreamTools/BackCount`** — `Flask` 3.0.0 → 3.1.3 y `Werkzeug` 3.0.1 → 3.1.8.

La alerta que figuraba como alta era *"Werkzeug debugger vulnerable to remote
execution"*, y **no era explotable**: el depurador de Werkzeug solo permite
ejecutar código si el modo debug está encendido, y `app.py` tiene `debug=False`.
Con el comentario que se dejó al arreglarlo en su momento:

```python
# host='0.0.0.0' es intencionado: OBS necesita alcanzar el servidor desde
# la red local. Por eso mismo debug debe estar desactivado: el depurador
```

Es un caso que merece señalarse: **una corrección de una sesión anterior
neutralizó una alerta que apareció después**, y el comentario evitó tener que
reconstruir el razonamiento al volver. La actualización se aplicó igualmente,
porque la 3.0.1 sí arrastra los fallos de `safe_join` en Windows.

Comprobado antes de aplicarlo que Flask 3.1.3 funciona con Werkzeug 3.1.8 en los
tres patrones que usa el proyecto —plantillas, respuestas JSON y sesión—, por
estar los dos paquetes acoplados.

**`FFMPEG_UI`** — `python-dotenv` 1.1.1 → 1.2.2. Salto menor en un proyecto de
escritorio con PyQt; no requiere verificación funcional.

### Dependencias de LeaderBoard_Unity al día

Cuatro entradas de la lista real viven en el mismo `requirements.txt`, así que se
trataron juntas.

| Paquete | Antes | Ahora | Motivo |
|---|---|---|---|
| `PyJWT` | 2.10.1 | 2.13.0 | 4 avisos, **3 no aplicables** |
| `Werkzeug` | 3.0.4 | 3.1.8 | `safe_join` inseguro en Windows, agotamiento de recursos |
| `requests` | 2.31.0 | 2.34.2 | fuga de `.netrc`, `verify=False` persistente |
| `python-dotenv` | 1.0.1 | 1.2.2 | `set_key` sigue enlaces simbólicos |

**De los cuatro avisos de PyJWT, tres no afectaban a este proyecto**: los de
clave pública JWK aceptada como secreto HMAC, SSRF en `PyJWKClient` y peticiones
JWKS ilimitadas requieren `PyJWK` o `PyJWKClient`, que no se usan en ninguna
parte. Los dos que sí aplicaban son denegación de servicio.

El proyecto ya estaba bien escrito en lo que importa: **las cinco llamadas a
`jwt.decode` fijan `algorithms=['HS256']`**, sin excepción, y el `SECRET_KEY`
mide 64 bytes. Las alertas graves no aplicaban por cómo está hecho el código, no
por casualidad.

Sin cambios de código: `encode`, `decode`, `ExpiredSignatureError` e
`InvalidTokenError` son idénticos entre 2.10 y 2.13. Se comprobó también que
Flask 3.0.3 funciona con Werkzeug 3.1.8 antes de subirlo, por estar acoplados.

**Verificado extremo a extremo**: registro 201, login 200 con los dos tokens,
perfil con token válido 200, y —la que importa— **perfil con el `id` del token
cambiado de 8 a 1 conservando la firma original: 403**. Esa API identifica al
usuario por el `id` que viaja dentro del token, así que si la firma no se
comprobara bien, bastaría cambiar un número para leer el perfil de otro.

#### Dos cabos sueltos que salieron al probarlo

**El `.env` era idéntico al `.env.example`.** Al mover las credenciales de
código a variables de entorno en una sesión anterior, el `.env` se quedó con los
valores de muestra: el rol `usuario`, que no existe en PostgreSQL. La API llevaba
desde entonces sin poder conectar a su base de datos, y nadie lo había notado
porque nadie la había arrancado. Es la undécima aparición del patrón de esta
revisión, y esta vez el descuido fue propio.

**La contraseña real contenía `@` y `?`.** En una URL de conexión el `@` separa
las credenciales del host, así que `psycopg2` partía la cadena por el sitio
equivocado. Corregido codificando (`%40`, `%3F`) y **documentado en el
`.env.example`** con la tabla de equivalencias, porque le va a ocurrir a
cualquiera que clone el proyecto.

#### Anotados y no corregidos

En `authenticate_token` (`app.py`, línea 41):

```python
if auth_header:
    token = auth_header.split(" ")[1]
if not token:
```

Si la petición llega sin cabecera `Authorization`, `token` nunca se asigna y el
`if not token` lanza `UnboundLocalError` → **500 en lugar de 403**. Si llega con
la cabecera pero sin espacio, el `split(" ")[1]` lanza `IndexError` → otro 500.
Rechaza igual, así que no es un fallo de seguridad, pero un 500 en el camino de
autenticación revela que algo revienta por dentro.

Y `app.run(host='0.0.0.0')` en la línea 1335 escucha en todas las interfaces.
Puede ser deliberado, porque el cliente es un juego de Unity que quizá corra en
otra máquina.

### El punto ciego de CodeQL en Java

Descubierto al abrir por fin el aviso amarillo *"CodeQL is reporting warnings"*
que llevaba semanas en la cabecera de la pestaña de seguridad y que nunca se
había mirado. Decía:

> **166 duplicate classes filtered out.** 166 files defined a class that clashes
> with the fully-qualified name of another scanned class. This means that only
> one of each clashing pair will be scanned.

La causa: nueve copias del ejercicio de Spring Batch conviviendo como variantes,
todas con el mismo paquete y los mismos nombres de clase. Para CodeQL,
`com.example.BatchProcessor.BatchProcessorApplication` era una sola clase
repetida nueve veces, así que analizaba una y descartaba ocho.

**Consecuencia:** el «0 alertas abiertas» de la sección anterior era cierto
sobre lo analizado, no sobre todo el código Java del repositorio.

Y el punto ciego escondía defectos reales. Un `grep` de dos minutos por las
copias no analizadas encontró **el mismo path traversal** que CodeQL sí había
reportado en `FalsosBatch` —un `@RequestParam` de HTTP entrando directo en una
ruta del sistema de ficheros— en **cuatro controladores más** que nunca
aparecieron en ninguna lista de alertas.

No era una sospecha teórica: ya se sabía que las copias divergían, porque al
corregir `FileReaderService` se dio por hecho que eran idénticas, se sobrescribió
una y falló la compilación. Copias distintas, fallos distintos.

Lo mismo ocurría con `api/ApiExtractData` y `api/api2/ApiExtractData`: dos
versiones que difieren en casi todos los ficheros pero comparten los 25 nombres
de clase, de modo que una de las dos jamás se analizó.

**Resuelto retirando del repositorio** `Java/Spring/SpringBatch` y
`Java/Spring/SpringBoot`, en lugar de renombrar paquetes o excluir rutas. Se
elimina la causa en vez de rodearla. El aviso bajó de 166 a 28 al sacar Spring
Batch, y las 28 restantes eran exactamente las dos parejas de `SpringBoot`.

Con esos proyectos se van también varias correcciones documentadas más arriba
—el `produces = TEXT_PLAIN` de `PseudoCifradoController`, los
`resolverDentroDeBase` de `FileReaderService` y `FileWritterService`— y buena
parte de las alertas de Maven, que vivían en esos `pom.xml`
(`mysql-connector-java`, `log4j-core`, `jackson-databind`, `jackson-core`). El
registro de aquellas intervenciones se mantiene aquí porque describe decisiones
válidas, aunque el código ya no esté en el repositorio.

**La lección, que es la misma que la de la sección siguiente:** el aviso de
estado de una herramienta importa tanto como su lista de resultados. Un análisis
que informa de 0 problemas y de 166 ficheros no analizados no está diciendo que
el código esté limpio.

### Las diez alertas que quedaban

Revisado el listado de code scanning tras dar por cerradas las nueve familias,
quedaban 10 alertas abiertas (frente a 246 cerradas). Ocho de ellas no eran
nuevas: pertenecían a familias ya tratadas, en ficheros que no se habían mirado.

**Registro de secretos en claro (4).** Familia que no estaba en la lista inicial,
y donde estaba el único hallazgo serio de los diez:

```js
// test-twitch.js:6
console.log("TOKEN:", process.env.TWITCH_OAUTH_TOKEN);
```

Imprimía el token de OAuth de Twitch completo por consola. Ese token da control
sobre la cuenta, y una vez escrito en la salida queda en el historial del
terminal y en el log de cualquier sistema que ejecute el script. `debug-env.js`
lo truncaba a 12 caracteres, que es menos, pero sigue siendo material secreto.

Corregido en los dos ficheros informando de si cada variable **está definida y
cuánto mide**, nunca de su valor. Los scripts existen para comprobar que el
`.env` carga, y para eso el valor no aporta nada.

**Falta de límite de peticiones (2).** `unified-chat-widget/index.js` y
`JSGameChat/server/index.js`. Añadido `express-rate-limit` con límites holgados
(600 y 300 por minuto): estos servidores los consume la fuente de navegador de
OBS, que sondea con frecuencia. El objetivo no es frenar un ataque sino que una
pestaña recargando en bucle no sature un proceso de un solo hilo que además
atiende websockets.

**Exposición de información por excepción (4).** `TestMail.py` y
`rumble_server.py`, con el mismo `str(e)` en la respuesta HTTP que se corrigió en
`app.py`. En el caso de Rumble el detalle importa: el mensaje de error de su API
puede incluir la URL completa con la clave de acceso.

`TestMail.py` merece mención aparte: **es un fichero que ya se había editado** en
la familia 1 para desactivar el modo debug de Flask, y su `str(e)` se pasó por
alto en la familia 2. La alerta apareció como nueva porque esa misma edición
provocó el reanálisis del fichero. No se escapó del listado: se dejó a medias.

### Segunda fuga de credenciales, encontrada leyendo el código

Al revisar los mensajes de error de una de las API aparecieron más credenciales
escritas directamente en el código y versionadas. **Ninguna la había detectado
el escáner de secretos de GitHub**: no tienen un formato reconocible, así que no
hay patrón que buscar.

Es el mismo tipo de fuga que la anterior y refuerza la misma conclusión —
**las herramientas automáticas encuentran los secretos con formato conocido; el
resto solo aparece leyendo el código**. Dos incidentes independientes con la
misma causa dejan poco margen a la interpretación.

**Todas se han rotado o revocado.** Como en el caso anterior, los detalles —qué
proyecto, qué servicios, en cuántos ficheros estaba repetida cada una— se han
retirado de este documento: es público, y describirlos sería señalar los commits
donde siguen estando los valores viejos.

Sí merece la pena registrar la lección que dejó la más grave de ellas: era una
clave de firma de JWT, y con una clave de firma se pueden **fabricar tokens
válidos para cualquier usuario, incluido el rol de administrador, sin conocer
ninguna contraseña**. No todas las credenciales filtradas cuestan lo mismo, y
esa es de las que lo cuestan todo.

**Cambios aplicados:** todas las credenciales pasan a leerse de variables de
entorno, con un `.env.example` documentado y `python-dotenv` añadido a las
dependencias. La configuración **aborta el arranque con un mensaje explícito**
si falta alguna variable, en lugar de recurrir a un valor por defecto: una
clave de respaldo silenciosa acabaría en producción sin que nadie lo notara, y
eso es peor que la fuga original.

**Resultado:** alertas de Dependabot de **590 a 2**. Las dos restantes son
dependencias transitivas del sistema de compilación de Angular, cuyas únicas
"correcciones" disponibles son retrocesos de versión; se dejan abiertas a la
espera de que el framework las actualice.

### Tercera tanda: league/commonmark (gym-app) y js-yaml (unified-chat-widget)

Dos grupos nuevos que ilustran los dos extremos del criterio *corregir en lugar
de silenciar*: uno tiene arreglo limpio y se aplica; el otro no tiene arreglo
aplicable y se deja abierto y documentado.

- **`league/commonmark` 2.8.3 → 2.9.1 en gym-app** (seis alertas de golpe).
  Es transitiva: la arrastra `laravel/framework`, que la declara como
  `^2.8.1` (no está en el `composer.json` propio). Las seis son avisos
  acumulados contra la serie 2.x:
    - DoS por complejidad cuadrática al parsear Markdown malicioso
      (GHSA-c2pc-g5qf-rfrf y CVE-2026-71488).
    - Bypass del allowlist de la extensión Embed —`youtube.com.evil` cuela
      cuando se permite `youtube.com`, con riesgo de SSRF/XSS
      (CVE-2026-33347, parcheado en 2.8.2).
    - XSS en `AttributesExtension` vía `javascript:` con bytes de control que
      el navegador descarta antes de leer el esquema (CVE-2026-71478 y
      CVE-2025-46734, parcheado en 2.9.0).

  Todas las versiones de parche (2.6.0, 2.8.2, 2.9.0) son ≤ 2.9.1, la última
  de la serie 2.x, y 2.9.1 cae dentro del `^2.8.1` que exige Laravel
  (`>=2.8.1 <3.0.0`). Por eso basta con
  `composer update league/commonmark --with-dependencies`: cierra las seis sin
  tocar el `composer.json` ni romper la restricción de Laravel. No se sube a
  la 3.x porque quedaría fuera del rango que Laravel admite.

- **`js-yaml` 4.3.0 en unified-chat-widget** (una alerta, se deja abierta).
  Transitiva por la misma cadena que `brace-expansion`:
  `@retconned/kick-js` → `puppeteer` → `cosmiconfig@9` → `js-yaml`. La alerta
  es CVE-2026-59870 (consumo cuadrático de CPU al resolver `!!omap`). **El fix
  solo existe en la línea 5.x —desde 5.2.1— y no se retroportó a las ramas 3.x
  ni 4.x**; el propio aviso lo dice. `cosmiconfig@9` fija `js-yaml@^4`, así que
  forzar la 5.x con `overrides` rompería cosmiconfig (la API cambió entre 4.x y
  5.x). Además el vector no aplica: aquí js-yaml lo usa cosmiconfig para leer el
  fichero de configuración propio en arranque, no para parsear YAML de fuentes
  no confiables. Sin corrección posible en la rama 4.x y bloqueada aguas
  arriba, se deja **abierta y sin descartar en GitHub**, igual que
  `brace-expansion`.

---

## 2026-07-05 — Limpieza de historia (git filter-repo)

Se reescribió la historia completa del repositorio para eliminar contenido
que no debía estar bajo control de versiones: artefactos de build, entornos
virtuales, dependencias de terceros vendorizadas, binarios pesados y archivos
de configuración local. Como parte de la operación se rotaron preventivamente
credenciales de desarrollo.

**Resultado:** el repositorio pasó de 2,06 GiB a 48,84 MiB (−97,7%).

**Consecuencias operativas:**

- Todos los hashes de commit anteriores al 2026-07-05 cambiaron.
- Los clones y forks previos a esa fecha son incompatibles con la historia
  actual: es necesario clonar de nuevo. No hacer pull ni push desde un clon
  antiguo, y nunca forzarlos (--force / --allow-unrelated-histories):
  restauraría la historia purgada.
- La operación se realizó sobre un clon espejo con `git filter-repo`,
  validando el resultado antes de sustituir el repositorio y publicar.

---

## Política de dependencias y alertas de seguridad

Este repositorio es un monorepo de proyectos personales y experimentales: la
mayoría no se despliega en ningún servidor y varios están archivados. Las
alertas de Dependabot se tratan, por tanto, con el siguiente criterio:

1. **Se corrigen** las vulnerabilidades que afectan a dependencias de
   *producción* de proyectos mantenidos (las que acabarían ejecutándose en un
   despliegue real).
2. **Se descartan**, indicando el motivo en la propia alerta, las que afectan
   únicamente a *dependencias de desarrollo* — linters, empaquetadores,
   servidores de desarrollo, frameworks de test — porque no forman parte de
   ningún artefacto distribuible.
3. **Se descartan** igualmente las de proyectos archivados o experimentales
   que no se ejecutan.

El descarte es una decisión explícita y registrada, no un descuido. Si alguno
de estos proyectos pasara a desplegarse, sus alertas deberían revisarse de
nuevo bajo el criterio 1.

**No se descartan** las alertas que sí tienen intención de arreglarse pero
cuya corrección depende de terceros — por ejemplo, dependencias transitivas
del sistema de compilación de Angular, que solo se resuelven cuando el
framework actualiza las suyas. Esas se dejan abiertas a propósito: son el
recordatorio de una tarea pendiente, y GitHub las cerrará automáticamente
cuando la actualización llegue. Descartarlas las ocultaría sin resolverlas.

---

## 2026-07-03 / 2026-07-05 — Reestructuración del monorepo

- Política de fin de línea unificada en `.gitattributes` (`* text=auto`,
  CRLF para scripts de Windows, LF para shell) y renormalización completa.
- Anidamientos de carpetas redundantes aplanados.
- Reorganización por ecosistema: `NodeJS/{JavaScript,TypeScript}` → `JS/`,
  `Laravel/` → `PHP/`, TaskHub de Python bajo `Python/FastApi/`.
- Artefactos de runtime fuera del control de versiones; `.gitignore`
  ampliado con reglas acotadas por ruta.
- README raíz convertido en catálogo de proyectos; hoja de ruta en
  `ROADMAP.md`; notas sueltas reubicadas en `docs/` por proyecto.
