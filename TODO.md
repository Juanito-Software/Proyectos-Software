# TODO del repositorio

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

## RadioStack

- [ ] **`@EntityScan` / `@EnableJpaRepositories` al módulo de persistencia.** Hoy
  viven en la clase de arranque de la API; moverlas a una configuración de
  `radiostack-persistence` resolvería de raíz las rodajas y quitaría a la API el
  conocimiento de los paquetes internos de otro módulo. Es cambio de producción,
  merece PR propio. _Fuente: 2026-09-12, «Lo que queda anotado y sin hacer»._
- [ ] **GET públicos bajo `/api/v1`.** Regla pensada para la parrilla/programas,
  alcanza a todos los GET (incluido `/api/v1/auth/me`). Decisión de producto:
  queda **documentado con un test**, no se cambia por iniciativa propia. _Fuente:
  2026-09-12._
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

## Repositorio — flujo de trabajo

- [x] **Perdurabilidad del flujo de trabajo: `AGENTS.md`.** Se crea la guía del
  agente en la raíz (flujo git con los aliases `git nueva`/`git subir`, fuentes
  de verdad, mínimos de CI y comandos de test por ecosistema), y queda la regla
  de cerrar toda sesión con un commit final de documentación en `README.md`,
  `MAINTENANCE.md`, `TODO.md` y `AGENTS.md`. Supera al borrador de la rama
  `docs_agents`, que tenía cifras atrasadas y no estaba en `main`. _Fuente:
  2026-09-19 (tarde)._

## CV

- [ ] **Cifras desactualizadas: «71 tests» y «Angular 19».** El mínimo de CI de
  TaskHub_Angular es ahora **162 backend + 103 frontend = 265** y el
  `package.json` declara `@angular/core ^21.2.19`. Confirmarlo antes de
  cambiarlo. _Fuente: 2026-09-11 (noche) y 2026-09-18._

## Seguridad y dependencias

- [ ] **44 vulnerabilidades sin verificar por API.** GitHub informó de «44
  vulnerabilities on the default branch (16 high, 22 moderate, 6 low)» al hacer
  push; la cabecera de MAINTENANCE.md dice 2 alertas Dependabot abiertas. Hace
  falta consultar la API. _Fuente: 2026-09-11 (noche)._
- [ ] **Dependabot (pip): bloque «En curso».** Es la única fila no saneada del
  estado de mantenimiento del README raíz. _Fuente: README.md (tabla de
  mantenimiento)._

## TaskHub_React (del historial, siguen abiertos)

- [ ] **Encadenar el despliegue al CI.** Hoy Render no espera al pipeline; se
  mantiene a propósito en desarrollo. _Fuente: 2026-08-29/30, «Pendiente»._
- [ ] **Limitación de intentos por cuenta además de por IP** (hoy solo por
  dirección). _Fuente: 2026-08-29/30._
- [ ] **Acciones del CI fijadas a etiqueta mayor, no a SHA.**
  _Fuente: 2026-08-29/30._
- [ ] **Protección de rama** que exija `ci-ok` antes de fusionar (sin revisión
  humana). _Fuente: 2026-08-29/30._
- [ ] **`PUT` y `PATCH` comparten controlador** (actualización parcial en ambos;
  desviación de la semántica HTTP, con tests desde la auditoría). _Fuente:
  2026-08-29/30._
- [ ] **E2E comparten la base de desarrollo** y dejan usuarios `e2e-*`; limpiarlos
  o darles BD propia. _Fuente: 2026-08-29/30._

## Sin empezar

- [ ] **OmniForge.** _Fuente: 2026-09-11 (noche) y 2026-09-18._
- [ ] **GPTDevTeam.** _Fuente: 2026-09-11 (noche) y 2026-09-18._

## Notas — requieren decisión, no hay tarea definida

- [ ] **`Claude outputs/` en el historial.** Un borrador de entrada y un PDF
  quedaron versionados y salen del `.gitignore`; aunque desindexados, siguen
  descargables por hash mientras no se reescriba la historia de git. _Fuente:
  2026-09-12 (tarde)._