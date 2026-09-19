# AGENTS.md

Monorepo personal (© Juanito Software): ~50 proyectos heterogéneos en
`Juanito_Software/<lenguaje>/…`; la mayoría son experimentos sin CI. Todo se
escribe y se comenta en **español**.

## Flujo de git con el usuario (obligatorio antes de tocar nada)

Cada cambio sigue estos cuatro pasos y **el usuario ejecuta los comandos**; el
agente los entrega ya adaptados (rama, rutas exactas, mensaje) y no usa git por
su cuenta (`commit`, `push`, `merge`, `gh`).

1. `git nueva <NombreRama>` — alias que actualiza `main`, poda las ramas ya
   integradas (`: gone]`) y crea la rama. Nombres históricos: `Fix_RadioStack`,
   `fix_taskhub-angular`.
2. `git add "<ruta1>"` … — las rutas exactas de lo tocado.
3. `git commit -m "<commit_message>"` — Conventional Commits en una línea (sin `-m`, git interpreta el texto como una ruta y falla)
   (`fix:`, `feat:`, `refactor:`, `test:`, `docs:`), p. ej. `fix: move JPA
   configuration to persistence`.
4. `git subir` — alias: push, abre/reutiliza el PR y programa el auto-merge en
   squash; con el push arranca el CI y, al integrar en `main`, el despliegue.
   Antes de tocar nada, **blinda** el árbol: si hay un merge en curso
   (`MERGE_HEAD`) o cambios sin commitear, avisa y se detiene. Si no hay PR
   abierto de la rama y esta ya se fusionó antes (PR `merged` previo), el alias
   integra `main` en la rama antes de pushear para que el PR nuevo solo lleve el
   cambio nuevo; sin cambios nuevos avisa y se detiene.

La **documentación canónica del flujo Git** (diagramas completos de `nueva` y
`subir`, métodos de integración y situaciones del día a día) es
`Doc/Programacion/git/how_to_use_git.md`.

## Fuentes de verdad

- `MAINTENANCE.md` — **única fuente consolidada del repo**. Empieza con el ToDo
  (el Roadmap quedó integrado en `## Stack tecnológico…`) y sigue con el
  historial operativo y las decisiones. Las tareas llevan trazabilidad
  (`_Fuente: …_`); al cerrar una, múdala a su sección como `[x]` con la
  referencia de la sesión, y al cerrar un cambio estructural añade una entrada
  fechada.
- **El estado real del código prevalece sobre los docs.** Las cifras de tests y
  cobertura se documentan **solo** en `README.md`; los `minimo` de `ci.yml` son
  los que las hacen cumplir.
- Método de verificación: "comportamiento provocado" — test antes del código,
  rojo primero, implementación después. Los tests se escriben en español
  snake_case (p. ej. `un_programa_va_y_vuelve_por_el_adaptador_real`).
- Cambios mínimos, sin refactorizar fuera de la tarea.

## CI

Dos workflows corren en cada push/PR a `main` y bloquean el merge: `ci.yml`
(job estable **`Monorepo en verde`**) y `taskhub-react-ci.yml` (job estable
**`CI en verde`**). Solo se ejecutan los de la **raíz** `.github/workflows`.

- No referenciar los nombres de jobs de matriz en reglas de protección: incluyen
  el mínimo declarado y cambian al subirlo.
- Cada job de tests declara un **mínimo** y cuenta `<testcase>` menos
  `<skipped>`. **Al añadir tests hay que subir el `minimo` correspondiente** en
  el workflow (si el total baja del mínimo, el job falla; si lo supera, avisa
  con `::notice::`). Las cifras actuales de tests y sus mínimos no se duplican
  aquí: viven en `README.md`.

## Java / Maven (RadioStack)

Multimódulo: core → persistence → api (+ stream, admin). Spring Boot 3, target
Java 17. Desde la raíz del proyecto: `mvn -B test`.

- La app **no arranca sin `RADIOSTACK_JWT_SECRET`** (Base64, sin valor por
  defecto). Los tests `@SpringBootTest` (`EsquemaYMigracionesTest` y
  `ChatStompEndToEndTest`) necesitan además PostgreSQL y
  `RADIOSTACK_DB_TESTS=true`; sin la variable **se saltan** (la cifra de la
  suite con y sin BD está en `README.md`). Local: servicio
  `postgresql-x64-17`, BD/usuario `radiostack`/`radiostack` (iguales a
  `application.yml` a propósito; es el mismo par que CI levanta en
  `postgres:17-alpine`). No hay docker local: la verificación con BD se hace en
  el PostgreSQL local o en el CI.
- Test suelto a través del reactor — en PowerShell **los `-D…` van entre
  comillas**:
  `mvn -pl radiostack-api -am test "-Dtest=Nombre" "-Dsurefire.failIfNoSpecifiedTests=false"`
- Los informes Surefire caen en `*/target/surefire-reports` de cada módulo (el
  CI los busca con `find` y cuenta `<testcase>`).
- Arquitectura: arranque `com.radiostack.RadiostackApiApplication`; el escaneo
  de entidades y repositorios JPA vive en `radiostack-persistence`
  (`com.radiostack.persistence.config.JpaConfig`). La rodaja `@WebMvcTest`
  (`SecurityConfigTest`) **no** usa la app real: tiene raíz propia
  (`ContextoWebDePrueba`). WebSocket: el handshake va abierto a propósito; la
  autenticación real está en la trama STOMP CONNECT (interceptor de canal).
- `radiostack-stream` es placeholder; `radiostack-admin` es JavaFX que consume
  la API. No tocar salvo tarea explícita.

## Node / TypeScript

- **TaskHub_Angular** (`JS/Angular/TaskHub_Angular/{backend,frontend}`).
  - Backend (Express + Prisma): `npm ci && npm test`. Los tests que tocan
    PostgreSQL real exigen `TASKHUB_DB_TESTS=true` + `DATABASE_URL` (cifras en
    `README.md`); el CI corre antes
    `prisma migrate deploy` y verifica que el esquema no se ha desviado de las
    migraciones (`prisma migrate diff --exit-code`). Los tests unitarios no
    necesitan `prisma generate` (doblan `@prisma/client`).
  - Frontend (Angular ≥21): el constructor de Angular envuelve Vitest y **no
    reenvía sus banderas**. Con `npx ng test --no-watch`, para el informe CI:
    `--reporters=junit --reporters=default --output-file=vitest-report.xml`
    (junit **primero**: `--output-file` aplica solo al primer reporter).
  - En CI se usa `npm ci` (lock), no `npm install`.
- **TaskHub_React** (`JS/React/TaskHub_React`, workflow propio): `npm run
  install:all` → `npm run lint` / `npm run typecheck` / `npm run verify` (e2e de
  API contra Postgres) / `npm run build` con `NODE_ENV=production` /
  `npm run test:e2e` (Playwright). El despliegue a Render viene después de
  `CI en verde`, solo en push a `main`, y se filtra por caminos: un commit que
  no toca el proyecto no republica.

## Python / PHP

- **TaskHub FastAPI** (`Python/FastApi/TaskHub/backend`): `pip install -r
  requirements.txt -r requirements-dev.txt` y `pytest -q
  --junitxml=pytest-report.xml` (SQLite en memoria por test, en `conftest.py`).
- **gym-app** (PHP/Laravel): `composer install`, crear `.env` desde el ejemplo +
  `php artisan key:generate`, **`npm run build` antes de los tests** (los Blade
  llaman a `@vite` y sin `public/build/manifest.json` las vistas dan 500), y
  `vendor/bin/phpunit --log-junit=phpunit-report.xml`.

## Entorno de ejecución

Windows, PowerShell (`pwsh`); JDK 21 + Maven 3.9.9, Node 22 y PostgreSQL 17 como
servicio local. En un entorno headless/nube, Maven Central y
`binaries.prisma.sh` pueden estar bloqueados: los cambios Java/Prisma se
verifican en la máquina local o en el CI, no ahí.

## Comandos de opencode

El repo define comandos de opencode de proyecto en `.opencode/command/` (cada
archivo es un comando real, invocado por su nombre):

- `/CierreSesion` — cierra la sesión: resume cambios, añade la entrada fechada en
  `MAINTENANCE.md` y marca `[x]` las tareas del ToDo consolidado.
- `/VerificarDocs` — auditoría de coherencia de la doc (enlaces, Markdown,
  contradicciones, duplicidades, fuentes de verdad). **Solo audita e informa**;
  no modifica documentos salvo que el usuario lo pida explícitamente.
- `/VerificarDocs_Validado` — variante autorizada de `/VerificarDocs`: audita y
  aplica directamente las correcciones de los hallazgos; invocar el comando es
  la autorización de escritura.
- `/EstadoRepo` — fotografía del repo (rama, git status, commits, ramas, PRs,
  ToDo, última entrada de MAINTENANCE); solo lectura.
- `/NewTask <rama>` — prepara una nueva tarea: entrega `git nueva <rama>` (el
  usuario crea la rama), recopila requisitos y espera confirmación de que la
  rama está creada antes de programar; al terminar el desarrollo valida lo que
  aplique y entrega `git subir` (el alias no recibe rama, sino el método:
  `squash`/`rebase`/`merge`). **El agente nunca crea la rama.**
- `/Write` — registra información relevante de la conversación para que
  `/CierreSesion` la consolide en la memoria persistente del agente (vía
  `$ARGUMENTS`: `message`, `chat` o ninguna).
- `/Technical` — activa el modo de análisis profundo y riguroso.

### Responsabilidades de escritura (política de escritores)

- `/Write` — registra durante la conversación información relevante de
  comportamiento/conocimiento del agente para que se consolide en **`AGENTS.md`**
  al cierre. Analiza antes de escribir, comprueba si la información ya existe,
  evita duplicados y no registra información especulativa o no confirmada. No
  usa `MAINTENANCE.md` como memoria genérica ni modifica documentos solo porque
  "podrían mejorar".
- `/CierreSesion` — responsable directo de la **memoria persistente del
  agente**: entradas fechadas y estado `[x]` de las tareas en `MAINTENANCE.md`,
  y comportamiento/conocimiento consolidado en `AGENTS.md`. No difiere esa
  escritura a `/Write`.
- `/VerificarDocs` — es **auditor**, no escritor: inspecciona, informa y solo
  aplica los hallazgos si el usuario lo solicita. Su variante autorizada
  `/VerificarDocs_Validado` sí aplica las correcciones: invocarla es el permiso.

El MCP de GitHub (hosted, solo-lectura) se configura en `.opencode/opencode.json`
y requiere `GITHUB_TOKEN` en el entorno; no da rama ni push al agente.

## Comandos `/Write` y `/Technical`

`/Write` y `/Technical` **son comandos reales** de opencode: viven como archivos
`.opencode/command/Write.md` y `.opencode/command/Technical.md` y se invocan en
el chat por su nombre (`/Write`, `/Technical`). No existe en opencode una
sintaxis `/Activate.Command(...)`: esa vía se documentó de forma incorrecta y se
elimina. Como cualquier comando, pueden recibir argumentos tras el nombre
(`/Write message`, `/Write chat`).

- `/Write` — marca información relevante de la conversación para registrarla en
  `AGENTS.md` (comportamiento/conocimiento del agente). La memoria persistente
  de la sesión es competencia de `/CierreSesion`. Variantes por argumento:
  `/Write` (a tu criterio), `/Write message` (solo el mismo mensaje) y
  `/Write chat` (toda la conversación). Confirma con: ✅ INFO updated.
- `/Technical` — activa un modo de análisis profundo y riguroso: investigación
  intensiva de los datos, búsqueda web si hay herramientas activas, razonamiento
  prolongado, `nivel_de_detalle = muy alto` y `estilo = técnico | académico`.
  Ámbitos ideales: IA, redes neuronales, arquitectura de software, programación
  avanzada, seguridad, protocolos y diseño de sistemas.