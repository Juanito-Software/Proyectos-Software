# AGENTS.md

Monorepo personal (© Juanito Software): ~50 proyectos heterogéneos en
`Juanito_Software/<lenguaje>/…`; la mayoría son experimentos sin CI. Todo se
escribe y se comenta en **español** (código, tests, commits y esta misma guía).

## Flujo de git con el usuario (obligatorio antes de tocar nada)

Cada cambio sigue estos pasos y **el usuario ejecuta los comandos**; el agente
los entrega ya adaptados (rama nueva, rutas exactas, mensaje) y no usa git por
su cuenta (`commit`, `push`, `merge`, `gh`).

1. `git nueva <NombreRama>` — alias que actualiza `main`, poda las ramas ya
   integradas (`: gone]`) y crea la rama. Nombres históricos: `Fix_RadioStack`,
   `Fix_Stomp_EndToEnd`, `fix_taskhub-angular`, `docs_agents`.
2. `git add "<ruta1>" …` — las rutas exactas de lo tocado (el agente las
   entrega; no usar `git add -A`).
3. `git commit -m "<mensaje>"` — Conventional Commits en una línea, en español
   (`fix:`, `feat:`, `refactor:`, `test:`, `docs:`, `ci:`, `chore:`). Ejemplos
   recientes: `test(radiostack): el chat por STOMP de punta a punta, y el minimo
   de CI a 165`, `fix(taskhub-angular): el tablero y el panel dejan de
   recortarse en silencio…`.
4. `git subir` — alias: push, crea/reutiliza el PR (título = mensaje del
   commit) y programa el auto-merge en **squash**; con el push arranca el CI y,
   al integrar en `main`, el despliegue.

Una rama/PR por cambio. No mezclar tareas en el mismo commit.

## Fuentes de verdad

- `MAINTENANCE.md` — historial operativo y decisiones, con lecciones caras de
  cada sesión. Añadir una entrada fechada al cerrar un cambio estructural.
- `TODO.md` — pendientes con trazabilidad (`_Fuente: …_`); al cerrar, marcar
  `[x]` con la referencia de la sesión.
- **El código y el CI prevalecen sobre los docs**: varios READMEs están
  atrasados en cifras; las cifras fiables son las de `.github/workflows/ci.yml`.
- Al añadir tests hay que subir el `minimo` correspondiente **y** actualizar el
  recuento del `README.md` raíz; al cerrar una tarea, también `TODO.md` y una
  entrada en `MAINTENANCE.md`.
- Método de verificación preferido: «comportamiento provocado» — test antes del
  código, rojo primero, implementación después. Tests en español snake_case
  (p. ej. `enviar_sin_token_se_rechaza_y_no_guarda_nada`).
- Cambios mínimos, sin refactorizar fuera de la tarea. No inventar ficheros
  «recordados»: si una ruta no responde, verificar con `Test-Path`/`git ls-files`.

## CI

Dos workflows corren en cada push/PR a `main` y bloquean el merge: `ci.yml`
(job estable **`Monorepo en verde`**) y `taskhub-react-ci.yml` (job estable
**`CI en verde`**). Solo se ejecutan los de la raíz `.github/workflows`.

- No referenciar los nombres de jobs de matriz en reglas de protección:
  incluyen el mínimo (`PHP · tests (…, 41)`) y cambian al subirlo.
- Cada job de tests declara un **mínimo**, cuenta `<testcase>` y descuenta
  `<skipped>`. Si el total baja del mínimo, el job falla; si lo supera, avisa
  con `::notice::` de que hay que subirlo.
- Mínimos actuales: RadioStack **165** · TaskHub_Angular backend 175 / frontend
  103 · gym-app 41 · TaskHub FastAPI 55 · BatchProcessor 20.

## Java / Maven (RadioStack)

Multimódulo: core → persistence → api (+ stream, admin). Spring Boot 3, target
Java 17. Desde la raíz del proyecto: `mvn -B test`.

- La app **no arranca sin `RADIOSTACK_JWT_SECRET`** (Base64, sin valor por
  defecto). Dos clases levantan el contexto completo contra PostgreSQL real y
  quedan detrás de la marca `RADIOSTACK_DB_TESTS`: `EsquemaYMigracionesTest`
  (7 tests: Flyway + validación de esquema) y `ChatStompEndToEndTest` (3 tests:
  chat STOMP de punta a punta). Sin la variable **se saltan**, así que local
  rinden **155** y en CI **165**. El PostgreSQL local (servicio
  `postgresql-x64-17`, BD/usuario `radiostack`/`radiostack`) es el mismo par que
  el CI levanta en `postgres:17-alpine`; las credenciales coinciden con
  `application.yml` a propósito. No hay docker local.
- Test suelto a través del reactor — en PowerShell **los `-D…` van entre
  comillas**:
  `mvn -pl radiostack-api -am test "-Dtest=Nombre" "-Dsurefire.failIfNoSpecifiedTests=false"`
- Los informes Surefire caen en `*/target/surefire-reports` de cada módulo (el
  CI los busca con `find` y cuenta `<testcase>`).
- Arquitectura: arranque `com.radiostack.RadiostackApiApplication`; el escaneo
  de entidades y repositorios JPA vive en `radiostack-persistence`
  (`com.radiostack.persistence.config.JpaConfig`). `SecurityConfigTest` es
  `@WebMvcTest` con raíz propia (`ContextoWebDePrueba`, al final del fichero), no
  la app real. WebSocket STOMP: handshake abierto a propósito (`/ws/stomp`);
  la autenticación real está en la trama CONNECT (interceptor de canal). Leer
  el chat es público; escribir exige token.
- Las trampas del test e2e de STOMP (sin RECEIPT para SUBSCRIBE, canal entrante
  multi-hilo, `JavaTimeModule` en el convertidor) están documentadas en la
  entrada de `MAINTENANCE.md` del 2026-09-19: consultarla antes de tocar ese
  test.
- `radiostack-stream` es placeholder; `radiostack-admin` es JavaFX que consume
  la API. No tocar salvo tarea explícita.

## Node / TypeScript

- **TaskHub_Angular** (`JS/Angular/TaskHub_Angular/{backend,frontend}`).
  - Backend (Express + Prisma): `npm ci && npm test`. 13 tests contra PostgreSQL
    real exigen `TASKHUB_DB_TESTS=true` + `DATABASE_URL`; el CI corre antes
    `prisma migrate deploy` y verifica que el esquema no se ha desviado
    (`prisma migrate diff --exit-code`). Los tests unitarios no necesitan
    `prisma generate` (doblan `@prisma/client`).
  - Frontend (Angular ≥21): el constructor de Angular envuelve Vitest y **no
    reenvía sus banderas**. Con `npx ng test --no-watch`; para el informe CI:
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