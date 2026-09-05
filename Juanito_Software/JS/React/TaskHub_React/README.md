# TaskHub – Gestor de tareas multiusuario

[![CI](https://github.com/Juanito-Software/Proyectos-Software/actions/workflows/taskhub-react-ci.yml/badge.svg)](https://github.com/Juanito-Software/Proyectos-Software/actions/workflows/taskhub-react-ci.yml)

Aplicación full-stack con **React** (frontend), **Express + TypeScript** (backend) y **PostgreSQL**. Cada usuario tiene su propia cuenta y ve únicamente sus tareas: los datos están aislados por usuario a nivel de consulta, no solo en la interfaz.

## Demo en vivo

**[taskhub-react.onrender.com](https://taskhub-react.onrender.com)**

Regístrate con cualquier usuario y contraseña — no hace falta correo ni
verificación, y cada cuenta solo ve sus propias tareas.

- La **aplicación** está en la raíz.
- El **[playground de la API](https://taskhub-react.onrender.com/playground)**
  permite lanzar peticiones reales contra los endpoints y ver las respuestas
  JSON, sin clonar el repositorio. Tiene su propio registro, y comparte sesión
  con la aplicación.

> Está en planes gratuitos (Render + Neon): el servicio se duerme tras 15 minutos sin tráfico, así que **la primera carga puede tardar cerca de un minuto**. Las siguientes van rápidas.

## Estructura del proyecto

```
TaskHub/
├── client/                       # Frontend React (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthForm.jsx      # login y registro, con confirmación
│   │   │   ├── AuthForm.test.jsx      ← 32 tests
│   │   │   ├── TaskForm.jsx      # alta y edición, con estado y prioridad
│   │   │   ├── TaskForm.test.jsx      ← 9 tests
│   │   │   ├── TaskItem.jsx      # tarjeta de tarea con sus distintivos
│   │   │   ├── TaskItem.test.jsx      ← 18 tests
│   │   │   ├── TaskList.jsx      # lista, filtros y búsqueda
│   │   │   └── TaskList.test.jsx      ← 25 tests
│   │   ├── context/
│   │   │   ├── AuthContext.jsx   # sesión, renovación automática y logout
│   │   │   └── AuthContext.test.jsx   ← 20 tests
│   │   ├── services/
│   │   │   ├── api.js            # tareas; abre el envoltorio de respuesta
│   │   │   ├── api.test.js            ← 16 tests
│   │   │   ├── api.refresh.test.js    ← 9 tests
│   │   │   ├── authApi.js        # login y registro
│   │   │   └── authApi.test.js        ← 16 tests
│   │   ├── test/setup.js         # limpia DOM y localStorage entre tests
│   │   ├── constants.js          # etiquetas de estado y prioridad, en un solo sitio
│   │   ├── passwordPolicy.js     # réplica de la política; el servidor manda
│   │   ├── passwordPolicy.test.js     ← 22 tests
│   │   ├── App.jsx               # formulario de acceso o lista, según sesión
│   │   ├── App.test.jsx               ← 15 tests
│   │   └── main.jsx
│   ├── vite.config.js            # build, proxy en desarrollo y umbrales de cobertura
│   └── package.json
├── server/                       # Backend Node.js + TypeScript (Express)
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/             # router · controller · service · JWT
│   │   │   │   ├── password-policy.ts            # política de contraseñas, fuente de verdad
│   │   │   │   ├── password-policy.test.ts       ← 73 tests
│   │   │   │   ├── auth.validation.test.ts       ← 30 tests
│   │   │   │   ├── sessions.repository.ts        # familias de refresco en SQL
│   │   │   │   ├── refresh-token.ts              # generación y hash del refresco
│   │   │   │   ├── token.service.test.ts         ← 19 tests
│   │   │   │   ├── auth.cookie.ts                # cookie HttpOnly del refresco
│   │   │   │   └── auth.cookie.test.ts           ← 12 tests
│   │   │   ├── users/            # repository (SQL) · types (rol user/admin)
│   │   │   ├── tasks/            # router · controller · service · repository
│   │   │   │   ├── tasks.repository.test.ts       ← 13 tests
│   │   │   │   └── tasks.validation.test.ts       ← 25 tests
│   │   │   └── admin/            # router · controller · service (solo rol admin)
│   │   ├── middleware/           # auth · admin · rate limit · validación · errores · logging
│   │   │   ├── rateLimit.middleware.test.ts       ← 8 tests
│   │   │   └── validate.middleware.test.ts        ← 15 tests
│   │   ├── config/               # env · db · schema · seed-admin · limpieza de sesiones
│   │   ├── utils/                # ApiError · ApiResponse · registro de seguridad
│   │   │   └── security-log.test.ts               ← 21 tests
│   │   ├── types/                # express.d.ts (userId en Request)
│   │   ├── public/               # playground de la API (se sirve en /playground)
│   │   │   ├── index.html        # marcado, sin nada de JavaScript dentro
│   │   │   └── app.js            # su lógica, aparte para que la CSP no ceda
│   │   ├── app.ts                # fábrica de la app Express
│   │   ├── server.ts             # arranque, semilla del admin y apagado ordenado
│   │   └── verify.ts             # suite end-to-end de la API      ← 154 tests
│   ├── scripts/build-assets.mjs  # copia playground y cliente compilado a dist/
│   ├── vitest.config.ts          # tests unitarios: solo lógica pura, sin BD
│   ├── .env.example              # plantilla de variables de entorno
│   └── package.json
├── e2e/taskhub.spec.js           # end-to-end de navegador          ← 36 tests
├── docs/AUDITORIA.md             # auditoría: seguridad, bugs, tests y cobertura
├── eslint.config.js              # lint del servidor (TS) y del cliente (React)
├── playwright.config.js          # arranca el servidor y espera a /api/health
├── .github/workflows/            # pipeline de CI (copia; GitHub lee el de la raíz)
└── README.md
```

Los tests viven **junto al código que prueban** (`TaskForm.jsx` y
`TaskForm.test.jsx` en la misma carpeta), salvo los de navegador, que van en
`e2e/` porque prueban la aplicación entera y no un fichero concreto.

En producción se despliega **un único proceso**: el mismo Express sirve el
cliente React compilado en `/`, el playground en `/playground` y la API en
`/api`.

## Cómo ejecutarlo

### 1. Instalar dependencias

Desde la raíz del proyecto:

```bash
npm run install:all
```

O por separado:

```bash
cd server && npm install
cd ../client && npm install
```

### 1.b Configurar la base de datos

El backend usa **PostgreSQL**. Crea una base de datos vacía y copia la plantilla
de variables de entorno:

```bash
createdb taskhub          # o CREATE DATABASE taskhub; desde psql
cd server
cp .env.example .env      # y edita DATABASE_URL con tu usuario y contraseña
```

Las tablas se crean solas la primera vez que arranca el servidor: el script del
esquema es idempotente, así que no hay que ejecutar migraciones a mano.

### 2. Arrancar servidor y cliente (recomendado)

En una sola terminal:

```bash
npm run dev
```

Arranca el backend (http://localhost:3001) y el frontend (http://localhost:5173). **Ctrl+C detiene ambos procesos** y cierra el servidor correctamente.

### Alternativa: arrancar por separado

```bash
# Terminal 1
npm run server

# Terminal 2
npm run client
```

Si arrancas por separado, pulsa **Ctrl+C** en cada terminal para detenerlos.

## Funcionalidades

- **Login/Registro**: token de acceso JWT de 15 minutos más un token de refresco rotativo en cookie HttpOnly. La sesión se renueva sola y el cierre revoca en el servidor.
- **Lista de tareas**: título, descripción, estado (pendiente / en progreso / completada) y prioridad (baja / media / alta), con distintivos de color. Solo ves tus tareas.
- **Agregar y editar**: el mismo formulario, con selectores de estado y prioridad.
- **Eliminar tarea**: con confirmación.
- **Marcar como completada**: checkbox, como atajo de un clic para el caso más habitual. El cambio se pinta al instante y se revierte si la petición falla, así que no hay espera visible.
- **Filtros y búsqueda**: por estado, por prioridad y por texto en título o descripción. **Los resuelve la API**, no el navegador: viajan como parámetros de consulta y solo llegan las tareas que se piden. La búsqueda espera 300 ms desde la última tecla para no lanzar una petición por carácter.
- **Notificaciones**: mensaje breve al crear o actualizar una tarea.
- **Modo claro y oscuro**: sigue la preferencia del sistema mientras nadie diga lo contrario, y recuerda la elección si se usa el conmutador.
- **Cambio de contraseña**: pide la actual, aplica la misma política que el registro y cierra las sesiones del resto de dispositivos.

## Interfaz y accesibilidad

### Tokens de color en lugar de valores sueltos

Todo el color sale de variables CSS declaradas una vez en `index.css`. Antes
había unos cuarenta valores hexadecimales repartidos por la hoja de estilos y
repetidos a mano, lo que funciona hasta que hay que cambiar uno —o añadir un
modo oscuro— y toca perseguirlos con la garantía de que alguno se queda atrás.

El modo oscuro es lo que obliga a que esto sea una variable y no un color
literal: cada valor tiene que existir en dos versiones, y la única forma de que
no se desincronicen es que el componente **no sepa cuál está usando**. No hay ni
una regla duplicada entre los dos temas.

El acento es un gris casi negro, no un azul de marca. Es deliberado: en un
gestor de tareas el color tiene que quedar libre para decir algo —qué está
pendiente, qué es urgente—, y si la interfaz ya viene coloreada de serie, esas
señales dejan de destacar. El azul se reserva para el anillo de foco.

### El tema respeta la preferencia del sistema

El conmutador distingue tres estados, no dos: claro, oscuro y **«el usuario no
ha elegido»**. Sin esa distinción, quien tiene el sistema en oscuro se comería
un fogonazo blanco al abrir la página. Mientras no haya elección explícita manda
`prefers-color-scheme`; en cuanto se pulsa el botón, gana la elección y se
recuerda.

El acceso a `localStorage` va envuelto en `try/catch`: lanza en navegación
privada y con el almacenamiento de terceros bloqueado. Que no se pueda recordar
el tema es un inconveniente; que la aplicación no arranque por eso, no.

### Accesibilidad

Era un punto ciego: ninguna de las auditorías anteriores la había mirado.

- **Foco de teclado visible.** Este era un defecto real, no una cuestión de
  gusto. Los botones llevan fondo propio, y sobre un fondo personalizado el
  anillo por defecto del navegador se pierde: quien navega con teclado no sabía
  dónde estaba. Se usa `:focus-visible` y no `:focus`, para que el anillo salga
  al tabular pero no al hacer clic — que es cuando estorba y lleva a la gente a
  quitarlo con `outline: none`, que es como empieza este problema.
- **El estado nunca depende solo del color.** Los requisitos de la contraseña
  llevan símbolo (✓ / ·) y un texto oculto para lectores de pantalla, además del
  color.
- **Los botones sin texto tienen nombre accesible**, y ese nombre describe la
  acción y no el estado: «Activar modo oscuro» se entiende sin ver el icono,
  mientras que «Modo oscuro» sería ambiguo.
- **`prefers-reduced-motion` respetado.** Las transiciones son decorativas;
  ninguna comunica nada que no se vea igual sin ellas.
- **Diseño adaptable.** La cabecera se apila en pantallas estrechas y los
  selectores pasan a una columna, en lugar de encogerse hasta lo ilegible.

Lo que **no** está hecho: no se ha pasado un validador automático como axe, ni
se ha probado con un lector de pantalla real. Lo de arriba es lo que se ha
cuidado al escribir el código, no un certificado de conformidad.

## API REST (ejemplos)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registro (`username`, `password`) |
| POST | `/api/auth/login` | Login (`username`, `password`) |
| POST | `/api/auth/refresh` | Cambia la cookie de refresco por credenciales nuevas |
| POST | `/api/auth/logout` | Cierra la sesión **en el servidor** |
| POST | `/api/auth/logout-all` | Cierra todas las sesiones del usuario |
| GET | `/api/tasks` | Listar tareas del usuario. Filtros: `?status=`, `?priority=`, `?search=` |
| GET | `/api/tasks/stats` | Resumen del usuario por estado |
| GET | `/api/tasks/:id` | Obtener una tarea |
| POST | `/api/tasks` | Crear tarea |
| PATCH | `/api/tasks/:id` | Actualizar parcial |
| PUT | `/api/tasks/:id` | Actualizar tarea completa |
| DELETE | `/api/tasks/:id` | Eliminar tarea |
| GET | `/api/system/stats` | Uptime, peticiones servidas y versión de Node |
| GET | `/api/health` | Comprobación de vida |
| GET | `/api/admin/users` | Listado de usuarios con su número de tareas · **admin** |
| DELETE | `/api/admin/users/:id` | Borra un usuario y, en cascada, sus tareas · **admin** |
| GET | `/api/admin/stats` | Resumen global de la instancia · **admin** |

Las rutas de tareas requieren cabecera `Authorization: Bearer <accessToken>`. Los títulos deben ser únicos **por usuario** (409 si se repite; dos usuarios distintos sí pueden tener el mismo título).

### Formato de respuesta

Todas las respuestas van envueltas:

```jsonc
// Correcta
{ "success": true, "data": { /* … */ }, "message": "…", "timestamp": "2026-08-23T…" }

// Error
{ "success": false, "error": "Tarea no encontrada", "timestamp": "2026-08-23T…" }
```

### Modelo de tarea

`status` (`pending` · `in-progress` · `completed`) y `priority` (`low` · `medium` · `high`) son la fuente de verdad. El campo `completed` se sigue devolviendo, calculado como `status === 'completed'`, y se acepta como entrada traduciéndolo a `status` — así el checkbox del cliente React sigue funcionando sin cambios. Las tareas guardadas antes de este cambio se normalizan al leerlas, sin script de migración.

## Playground de la API

Una interfaz para lanzar peticiones reales contra todos los endpoints y ver las
respuestas JSON, con filtros, contador de peticiones y uptime.

- En local: **http://localhost:3001/playground**, con el backend arrancado.
- Desplegado: **[taskhub-react.onrender.com/playground](https://taskhub-react.onrender.com/playground)**

### Cómo se entra

Todas las rutas de `/api/tasks` exigen un token, así que el playground pide
sesión antes de dejarte llamar a nada. **No hace falta tener cuenta previa**: la
pantalla que aparece al entrar tiene un enlace para registrarte ahí mismo, y
sirve cualquier usuario y contraseña.

El token se guarda en `localStorage` con la misma clave que usa el cliente
React, así que las dos partes comparten sesión: si ya has entrado en la
aplicación, el playground abre autenticado, y al revés. Si el token caduca
mientras lo usas, vuelve a aparecer la pantalla de acceso sin perder la página.

Desde el playground se sale con el botón de la esquina superior derecha, y hay
un enlace **← Ir a la aplicación** para volver al cliente React.

### Por qué su JavaScript vive en un fichero aparte

El playground era un solo `index.html` con toda su lógica dentro de un
`<script>` y sus manejadores en atributos `onclick`. Eso obligaba a que la CSP
llevara `'unsafe-inline'` en `script-src`, y con esa concesión puesta la
política deja de defender de lo único que se le pide: un atacante que
consiguiera inyectar una etiqueta de script la vería ejecutarse igual.

La lógica está ahora en `public/app.js`, los `onclick` son `addEventListener`, y
los botones que se generan al pintar cada tarea van por delegación en
`document`. A cambio, `script-src` es `'self'` y `script-src-attr` es `'none'`.
Se pierde la propiedad de «una herramienta de un solo fichero»; a cambio su CSP
sirve para algo.

El `<script>` apunta a `/playground/app.js` con **ruta absoluta a propósito**.
La página se sirve en `/playground`, sin barra final, así que un `src` relativo
lo resuelve el navegador contra la raíz y acaba pidiendo `/app.js`, donde no hay
nada. El playground se queda pintado pero inerte, sin ningún error a la vista.

### Probar los endpoints de administración

Los tres endpoints de `/api/admin` no tienen interfaz propia: se prueban desde
aquí, entrando con la cuenta de administrador definida en `ADMIN_USERNAME`.
Con un usuario normal responden 403, que es justo lo que conviene comprobar.

## Despliegue

El servicio web va en **Render** y la base de datos en **Neon**. Los dos tienen
plan gratuito permanente; el de Render duerme el servicio tras 15 minutos sin
tráfico, así que la primera carga puede tardar cerca de un minuto.

### Configuración del servicio en Render

Como esto vive dentro de un monorepo, hay que apuntar al subdirectorio:

| Campo | Valor |
|-------|-------|
| Repository | `Juanito-Software/Proyectos-Software` |
| Root Directory | `Juanito_Software/JS/React/TaskHub_React` |
| Runtime | Node |
| Build Command | `npm run install:all && npm run build` |
| Start Command | `npm start --prefix server` |
| Instance Type | Free |

`install:all` usa `--include=dev` a propósito: con `NODE_ENV=production`, npm
omite las devDependencies, y ahí están Vite, TypeScript y tsx. Sin ese flag el
build falla con `vite: not found`.

### Variables de entorno en Render

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | La cadena de Neon, con `?sslmode=require` |
| `JWT_SECRET` | Una clave larga y aleatoria, **distinta de la de desarrollo** |
| `NODE_ENV` | `production` |
| `ADMIN_USERNAME` | Opcional. Nombre del administrador |
| `ADMIN_PASSWORD` | Opcional. Mínimo 12 caracteres |

`PORT` no se configura: Render la inyecta y `config/env.ts` la lee.

El build compila el cliente React, luego el servidor, y copia el resultado a
`server/dist/client`. En producción un único proceso Express sirve las tres
cosas: la aplicación en `/`, el playground en `/playground` y la API en `/api`.

## Tests

**962 en total**, repartidos en cuatro capas que prueban cosas distintas:

| Comando | Qué ejecuta | Cuántos | Necesita |
|---------|-------------|---------|----------|
| `npm test` | Unitarios de servidor y cliente | 548 + 224 | Nada |
| `npm run verify` | End-to-end de la API | 154 | PostgreSQL |
| `npm run test:e2e` | Navegador real (Playwright) | 36 | PostgreSQL y `npm run build` |
| `npm run ci` | Lint, tipos, unitarios y build | — | Nada |

Los **unitarios** cubren lógica pura —validadores, política de contraseñas,
escapado de comodines de `LIKE`, servicios, controladores, middleware, la capa
de servicios del cliente y los componentes— y corren en milisegundos sin nada
instalado. En el servidor llegan al **99,5% de esa lógica**, con el umbral
puesto justo por debajo en `vitest.config.ts` para que una rama nueva sin cubrir
ponga el CI en rojo.

Ese porcentaje mide solo lo que corre sin base de datos: los repositorios, los
routers y el cableado de Express están excluidos a propósito porque quien los
ejercita es `npm run verify` contra PostgreSQL real. Un 99,5% aquí no significa
que el servidor entero esté probado al 99,5%.

La **suite de la API** levanta la aplicación en un puerto temporal contra un
esquema de base de datos propio, que se crea al empezar y se destruye al
terminar aunque falle a mitad. Incluye una batería de manipulación de tokens
(firma inválida, caducado, `alg: none`, sin identificador, usuario inexistente)
y cargas de inyección SQL que deben tratarse como texto.

Los **de navegador** son la única capa que comprueba que cliente, API y base de
datos encajan de verdad. La primera vez hay que descargar Chromium:

```bash
npx playwright install chromium
```

#### Salvaguarda: no se pueden ejecutar contra producción

Estos tests **escriben datos reales**: crean usuarios, crean y borran tareas, y
uno de ellos llega a eliminar una cuenta. Como el `.env` de desarrollo apunta a
la base de datos desplegada, ejecutarlos sin pensar dejaba usuarios `e2e-*` en
la aplicación en producción. Pasó, y por eso existe esta protección.

`playwright.config.js` **aborta antes de arrancar nada** si `DATABASE_URL`
apunta a una base de datos gestionada — Neon, Render, Supabase o RDS— y explica
cómo apuntar a una local. La protección está en la herramienta, no en acordarse.

Preparar la base de datos de pruebas, **una sola vez**:

```sql
CREATE DATABASE taskhub_e2e;
```

Y después, en cada terminal donde vayas a lanzarlos:

```bash
set DATABASE_URL=postgresql://usuario:clave@localhost:5432/taskhub_e2e
npm run test:e2e
```

La variable solo vive en esa ventana y tiene prioridad sobre el `.env`, así que
la configuración de desarrollo se queda intacta. En CI no hace falta: allí
`DATABASE_URL` ya apunta al contenedor de PostgreSQL del propio job, que se
destruye al terminar.

Si en algún momento quieres saltarte la protección a propósito —por ejemplo
contra un entorno de pruebas remoto— define `E2E_ALLOW_REMOTE_DB=1`.

Y si quedaran restos de una ejecución antigua:

```sql
DELETE FROM users WHERE username LIKE 'e2e-%';
```

Las tareas asociadas se van solas por el borrado en cascada.

### Qué cubren las 154 comprobaciones de la API

Registro, login, acceso sin token, CRUD completo, validación de campos y de
filtros, título duplicado, traducción `completed` ↔ `status`, los tres filtros,
ambos endpoints de estadísticas, que el playground se sirva, aislamiento entre
usuarios, borrado, que el índice único rechace duplicados aunque cambien
mayúsculas y espacios, y que borrar un usuario arrastre sus tareas.

Más la sesión completa: forma y atributos de la cookie de refresco, rotación,
detección de reutilización con revocación de la familia, tolerancia a
renovaciones simultáneas, logout con revocación en servidor, cierre de todas las
sesiones, y la batería de intentos que deben fallar — un token de acceso usado
como refresco, un refresco usado como token de acceso, y un token de la política
anterior.

**Seguridad:** token firmado con otro secreto, caducado, sin firmar con
`alg: none`, sin identificador de usuario, de un usuario que ya no existe y con
formato inválido — todos deben devolver 401. Y cargas de inyección SQL en el
filtro de búsqueda, que deben tratarse como texto sin romper la consulta.

**Rol de administrador:** que registrarse nunca lo conceda —ni enviando
`role: "admin"` en el cuerpo—, que un usuario normal reciba 403, que sin token
se reciba 401 y no 403, que el administrador de la semilla exista y entre, que
el listado no filtre ningún hash de contraseña, y que un administrador no pueda
borrarse a sí mismo.

## Integración continua y despliegue

### CI — GitHub Actions

Cada push y cada pull request ejecuta ocho jobs en GitHub Actions: lint, tipos,
unitarios del servidor, tests del cliente con cobertura, suite de la API contra
un PostgreSQL real, end-to-end de navegador, build de producción y auditoría de
dependencias. Todos cuelgan de un job final, `ci-ok`, del que cuelga a su vez la
regla de protección de rama —y del que depende el despliegue— sin tener que
enumerar los demás cada vez que se añade uno.

El pipeline falla si falla cualquier test, si el build no produce servidor,
playground y cliente, si el lint o los tipos protestan, si la cobertura baja de
los umbrales, o si aparece una vulnerabilidad **alta o crítica**. Las moderadas
y bajas no lo bloquean: con `--audit-level=moderate` estaría en rojo permanente
por dependencias de desarrollo, y un CI siempre en rojo deja de mirarse.

El workflow está en `.github/workflows/taskhub-react-ci.yml`, con una copia en
la raíz del monorepo, que es donde GitHub los busca.

El token que GitHub inyecta en cada job va con `permissions: contents: read`.
Por defecto ese token puede **escribir** en el repositorio, y cualquier acción de
terceros que se ejecute en el pipeline lo hereda: si una resultara comprometida,
tendría permiso para crear commits o publicar releases. Aquí solo hace falta leer
el código, así que se declara eso y nada más.

### Análisis estático de seguridad

El repositorio tiene **CodeQL** activado, y sus avisos se corrigen en lugar de
descartarse. Tres ejemplos de este proyecto, porque ilustran por qué conviene
mirarlos uno a uno en vez de silenciarlos en bloque:

- **Registro en claro de información sensible.** La suite de la API imprimía la
  cabecera `Set-Cookie` completa como detalle de tres comprobaciones, y ahí va el
  token de refresco. Esa salida queda guardada en el registro del CI: dejaba allí
  una credencial utilizable durante siete días. Ahora se censura el valor y se
  conservan los atributos, que es lo que el test comprueba.
- **Aleatoriedad insegura.** Los tests de navegador generaban nombres de usuario
  con `Math.random()`. La alerta era un falso positivo en cuanto a seguridad —ahí
  no se genera ninguna credencial—, pero al mirarlo apareció un fallo real:
  `Date.now()` con tres cifras colisiona cuando varios tests arrancan en el mismo
  milisegundo, y dos usuarios iguales hacen fallar el registro. Se cambió a
  `crypto.randomUUID()`, que resuelve las dos cosas.
- **Ruta sin limitador.** La del playground acaba en una lectura de disco y no
  tenía límite de peticiones. Ahora pasa por el mismo `apiLimiter` que el resto.

### CD — encadenado al CI

**El único camino a producción pasa por el pipeline.** El job `deploy` depende
de `ci-ok`, así que un commit con los tests en rojo no llega a desplegarse.

Antes no era así: Render tenía Auto-Deploy y publicaba por su cuenta en cuanto
llegaba un commit a `main`, sin esperar al pipeline. Los dos procesos corrían en
paralelo sin mirarse, y una versión rota podía estar sirviendo tráfico veinte
minutos antes de que el CI terminara en rojo. Pasó. Ochocientos tests que no
pueden impedir un despliegue son una red de seguridad decorativa, y esa era la
situación real hasta este cambio.

El job se lanza solo si se cumplen tres condiciones: que `ci-ok` haya terminado
en verde, que la rama sea `main` y que el evento sea un `push` —ni pull
requests, ni disparo manual desde la pestaña Actions—. Usa además su propio
grupo de concurrencia **sin cancelación**: el resto del workflow sí cancela
ejecuciones superadas, pero cortar un despliegue a la mitad deja el servicio en
un estado que nadie ha decidido.

#### Por qué el pipeline se ejecuta en todo el monorepo

Tuvo filtros de ruta, para no gastar minutos cuando el commit tocaba otro
proyecto. Se quitaron, y la razón merece contarse porque el primer intento fue
peor que el problema.

`ci-ok` es comprobación obligatoria en `main`. Una comprobación obligatoria que
**no se ejecuta** no se interpreta como «no aplica» sino como «pendiente», y
pendiente para siempre: con filtros de ruta, cualquier commit a otro proyecto
del monorepo quedaba bloqueado sin remedio.

El apaño habitual es un segundo workflow que reporte el mismo nombre de
comprobación cuando el filtro no casa. Se probó y **se retiró**: en un commit
que toca TaskHub *y además* otro proyecto se disparan los dos, aparecen dos
comprobaciones llamadas igual y cuál manda es ambiguo. Un pipeline en rojo podía
quedar tapado por el verde trivial del otro — es decir, el remedio abría un
agujero justo en la puerta que se quería cerrar.

Ejecutarlo siempre elimina esa clase de problema entera: hay **una** «CI en
verde» y significa exactamente lo que dice. El coste son un par de minutos de
runner en commits ajenos, y en un repositorio público esos minutos son gratuitos
e ilimitados.

El filtro no desaparece, se muda: el job de despliegue compara el commit con el
anterior y solo despliega si el cambio toca de verdad este proyecto. Así se
evita republicar lo mismo una y otra vez, que sí gasta tiempo de construcción en
Render. Si no puede comparar —primer push de una rama, force-push—, despliega:
desplegar de más es molesto, desplegar de menos deja producción desactualizada
sin que nadie se entere.

#### Qué comprueba el job antes de darse por bueno

Tres pasos, y el verde exige los tres:

1. **Lanza el despliegue por la API de Render**, no por el deploy hook. El hook
   contesta 200 sin decir qué despliegue ha creado, así que para esperarlo
   habría que mirar el más reciente y confiar en que sea el nuestro; si alguien
   redespliega a mano en ese momento, se esperaría al equivocado. La API
   devuelve el despliegue con su identificador y esa ambigüedad desaparece.
2. **Espera al estado final**, consultando ese despliegue concreto. Solo `live`
   cuenta como éxito. `build_failed`, `update_failed`, `pre_deploy_failed`,
   `canceled` y `deactivated` ponen el job en rojo, y un estado desconocido
   también: si Render añade uno nuevo, es preferible enterarse por un fallo que
   darlo por bueno. Hay quince minutos de margen y tolerancia a fallos
   puntuales de red, para no cambiar un verde que miente por un rojo que miente.
3. **Comprueba que la aplicación responde**, pidiendo `/api/health` a la URL
   pública. Que Render diga `live` y que la aplicación conteste no son lo mismo:
   el proceso puede arrancar y morir al primer tráfico. La URL se pregunta a la
   API en lugar de escribirla en el workflow, para que no haya una dirección a
   mano que se quede vieja sin que nadie lo note.

#### Configuración necesaria (una vez)

Tres pasos fuera del repositorio. Sin los tres, el encadenado no está completo:

1. **Desactivar Auto-Deploy en Render**, en los ajustes del servicio. Es el paso
   que más fácil se olvida y el que invalida todo lo demás: si sigue encendido,
   el job *añade* un segundo despliegue en vez de sustituir al primero, y Render
   sigue publicando commits sin pasar por el CI.
2. **Crear una clave de API en Render** —*Account Settings → API Keys*— y
   guardarla como secreto `RENDER_API_KEY`, junto con el identificador del
   servicio (`srv-…`, visible en la URL del panel) como `RENDER_SERVICE_ID`.
   Los dos en `Settings → Secrets and variables → Actions` del repositorio. La
   clave **es una credencial**, así que no va al código ni a este README.
3. **Proteger la rama `main`** exigiendo `ci-ok` como comprobación obligatoria.
   Sin esto, `ci-ok` existe pero no bloquea nada: la puerta está puesta y la
   pared no. Está configurado mediante un *ruleset* del repositorio, que es el
   mecanismo actual de GitHub; conviene saberlo porque el endpoint de
   protección de rama clásica responde «Branch not protected» aunque las reglas
   existan.

El secreto `RENDER_DEPLOY_HOOK` ya no se usa y puede retirarse de los ajustes
del repositorio y de Render.

## Sesiones: token de acceso y token de refresco

Hay **dos credenciales con papeles distintos**, y la diferencia entre ellas es
lo que permite revocar una sesión de verdad.

| | Token de acceso | Token de refresco |
|---|---|---|
| Qué es | JWT firmado (HS256) | 32 bytes aleatorios, **no es un JWT** |
| Dura | 15 minutos | 7 días |
| Viaja en | `Authorization: Bearer` | Cookie `HttpOnly` |
| Sirve para | Cualquier ruta protegida | Solo `POST /api/auth/refresh` |
| Se guarda en el servidor | No | Sí, su SHA-256, en `refresh_sessions` |
| Se puede revocar | No hasta que caduque | Sí, al instante |

**Por qué el de refresco no es un JWT.** Si los dos lo fueran, separarlos
dependería de comprobar un claim `typ` en todos los sitios, y olvidarlo en uno
solo bastaría para que un refresco valiera como token de acceso. Siendo bytes
opacos, esa confusión es imposible: el middleware intentaría verificar una firma
que no existe. El claim `typ: 'access'` está igualmente, como segunda barrera.

**Por qué el de acceso dura tan poco.** Un JWT firmado sigue siendo válido hasta
que caduca, aunque se cierre la sesión: no hay forma de retirarlo sin consultar
una lista negra en cada petición, y eso costaría una consulta por llamada. La
respuesta no es la lista negra, es que la ventana sea pequeña. Quince minutos es
el máximo que puede sobrevivir un token robado.

### Rotación y detección de reutilización

Cada renovación **gasta** el token de refresco y entrega otro. La fila vieja se
marca revocada y la nueva nace con el mismo `family_id`, así que una sesión es
la cadena de filas que comparten familia.

Esa cadena es lo que permite distinguir dos cosas que se parecen:

```
Refresco A  →  renovar  →  A revocado, nace B          ← normal
Refresco A  →  renovar otra vez                        ← alguien tiene una copia
                ↓
        se revoca la FAMILIA entera, no solo A
```

Revocar solo el token presentado no serviría de nada: quien pudo copiar A tiene
también B. Por eso cae la cadena completa y la sesión se cierra en todos los
dispositivos que la compartían.

**Con una excepción deliberada.** Dos pestañas del mismo usuario pueden renovar a
la vez con la misma cookie, y eso no es un ataque. Dentro de una ventana de
tolerancia (`REFRESH_GRACE_SECONDS`, 10 por defecto) la segunda se rechaza sin
matar la familia, y el cliente reintenta con la cookie ya rotada. Es un
compromiso explícito: estrecha la detección durante esos segundos a cambio de no
echar a la calle a quien solo tenía dos pestañas abiertas.

La rotación es **atómica**: `UPDATE ... WHERE token_hash = $1 AND revoked_at IS
NULL`. PostgreSQL serializa las escrituras sobre una misma fila, así que de dos
rotaciones simultáneas solo una la encuentra sin revocar. No hace falta
transacción explícita ni bloqueo — una sola sentencia ya lo es.

### Por qué el refresco va en cookie y no en localStorage

Es la credencial que de verdad importa: sirve para emitir tokens de acceso
durante días. `HttpOnly` la deja fuera del alcance de `document.cookie`, así que
un XSS puede llevarse el token de acceso —quince minutos— pero no la llave que
renueva la sesión.

Meter una cookie en una aplicación que no las usaba obliga a mirar **CSRF**, que
es el riesgo clásico de autenticar por cookie. Aquí queda cerrado por tres vías:

1. **`SameSite=Strict`**: el navegador no manda la cookie en peticiones que
   nazcan de otro sitio. Es la defensa principal y hace innecesario un token
   anti-CSRF.
2. **La cookie no autoriza nada.** Ninguna ruta de datos la mira; las protegidas
   exigen la cabecera `Authorization`, que una petición cross-site no puede
   fijar.
3. **`Path=/api/auth`**: ni siquiera se envía al resto de la API.

CORS se queda como estaba, con `credentials: false`. No hace falta relajarlo: en
producción la aplicación, el playground y la API salen del mismo origen, y en
desarrollo Vite hace de proxy, así que el navegador nunca ve una petición
cross-origin.

### Cerrar sesión

`POST /api/auth/logout` revoca la familia **en el servidor**. Antes el logout
solo vaciaba el estado del navegador, y el token seguía siendo válido durante
días para quien tuviera una copia. Cerrar una sesión no toca las demás del mismo
usuario; para eso está `POST /api/auth/logout-all`, que las cierra todas y saca
el identificador del token, nunca del cuerpo de la petición.

### Cambiar la contraseña

`POST /api/auth/change-password` exige sesión y **la contraseña actual**.

Pedirla teniendo ya un token parece redundante y no lo es: sin ese requisito, un
token de acceso robado permitiría cambiar la contraseña y quedarse con la cuenta
para siempre. Con él, el robo dura lo que dure el token — quince minutos.

La contraseña nueva pasa exactamente la misma política que en el registro,
incluida la comparación contra el nombre de usuario. Ese nombre se saca de la
base de datos a partir del token, **nunca del cuerpo de la petición**: validar
contra un dato que controla el cliente no valida nada. Repetir la contraseña que
ya se tenía se rechaza, porque expulsaría todos los dispositivos sin cambiar
nada.

**Al terminar se revocan todas las sesiones y se abre una nueva.** Es la parte
que más se piensa. Cambiar la contraseña es lo que hace quien sospecha que le
han entrado; si las demás sesiones siguieran vivas, el intruso conservaría su
acceso hasta que caducara su refresco, siete días después. Pero revocar «todas»
incluiría la del propio usuario, que se vería expulsado justo después de hacer
lo correcto — así que a continuación se le entrega una credencial nueva. Él sigue
dentro, el resto de dispositivos fuera. Es lo que hacen GitHub o Google, y es la
diferencia entre una medida que se usa y una que se evita por incómoda.

Las sesiones cerradas así quedan marcadas con el motivo `password-changed`, y no
con `logout-all`: una avalancha de las primeras significa que varias cuentas se
sienten comprometidas a la vez, que es una señal muy distinta.

Lo que **no** hay todavía es «he olvidado mi contraseña». Eso exige correo, y el
correo exige dominio verificado y proveedor de envío: sin eso los mensajes caen
en spam y la función existe sin funcionar.

### Qué pasó con los tokens de 7 días ya emitidos

**Se invalidaron todos.** Los de la política anterior no llevan el claim
`typ: 'access'`, así que el middleware los rechaza desde el primer despliegue y
todo el mundo tuvo que volver a entrar.

Fue una decisión, no un descuido. Mantenerlos vivos por comodidad habría dejado
abierta durante una semana justo la puerta que este cambio venía a cerrar:
tokens de larga duración imposibles de revocar. Un cierre de sesión molesto es
más barato que eso.

### Variables de entorno

| Variable | Por defecto | Para qué |
|---|---|---|
| `ACCESS_TOKEN_TTL` | `15m` | Duración del token de acceso |
| `REFRESH_TOKEN_TTL` | `7d` | Duración de la sesión sin volver a escribir la contraseña |
| `REFRESH_GRACE_SECONDS` | `10` | Tolerancia para renovaciones simultáneas |
| `JWT_SECRET` | — | Firma del token de acceso. Obligatoria en producción |

## Política de contraseñas

La implementación está en `server/src/modules/auth/password-policy.ts`, que es
la única fuente de verdad: la usan tanto el registro como la semilla del
administrador. El formulario replica las reglas en `client/src/passwordPolicy.js`
para avisar antes de enviar, pero quien decide es el servidor.

La política combina recomendaciones de **NIST SP 800-63B Revisión 4** (julio de
2025) con requisitos propios más estrictos. Conviene no mezclarlos:

| Regla | Valor | Origen |
|---|---|---|
| Longitud mínima | **15 caracteres** | NIST: exige 15 cuando la contraseña es el único factor; los 8 solo valen con MFA, y TaskHub no la tiene |
| Contraseñas largas permitidas | Hasta 72 bytes | NIST pide admitir al menos 64 |
| Sin truncamiento silencioso | Se rechaza, no se recorta | NIST |
| Caracteres permitidos | Todos, espacios incluidos | NIST |
| Almacenamiento | bcrypt con sal | NIST |
| Lista de bloqueo | Contraseñas comunes, caracteres repetidos, secuencias de teclado y el propio nombre de usuario | NIST exige la comprobación; **el contenido concreto de la lista es decisión de TaskHub** |
| **Al menos una mayúscula** | Obligatoria | **Decisión de TaskHub** |
| **Al menos un número** | Obligatorio | **Decisión de TaskHub** |
| **Al menos un símbolo** | Obligatorio | **Decisión de TaskHub** |
| Longitud máxima | 72 **bytes** | **Límite técnico**, no requisito de NIST: bcrypt solo lee los primeros 72 bytes |

**Las tres reglas de composición son más estrictas que NIST, no una lectura de
NIST.** La Revisión 4 no se limita a desaconsejarlas: dice que los verificadores
**no deben** imponerlas. TaskHub las aplica igualmente como requisito de
producto, y este README no pretende justificarlo apelando a la norma.

Lo que sí hay que hacer es asumir el efecto secundario conocido. Obligar a
mezclar tipos de carácter empuja a la gente hacia formas predecibles:
`Password123!`, `Verano2026!`, `P@ssw0rd`. Son las primeras que prueba un ataque
por diccionario, y cumplen los cuatro requisitos sin esfuerzo. Por eso la lista
de bloqueo **cubre expresamente los patrones que la propia regla fomenta**: una
palabra común rodeada de dígitos y símbolos se rechaza aunque cumpla la
composición, y la comprobación deshace antes las sustituciones de estilo *leet*,
de forma que `P@ssword2026!!!` cae igual que `Password2026!!!`. Sin esa
contrapartida, exigir composición dejaría la aplicación menos segura que sin
exigirla.

**Por qué 72 bytes y no 72 caracteres.** bcrypt cuenta bytes. Una contraseña de
72 caracteres con acentos o eñes pasa de los 72 bytes en UTF-8, y bcrypt
descartaría el sobrante sin avisar — justo el truncamiento silencioso que la
norma prohíbe. Medir con `.length` dejaba ese caso pasar.

**Otras decisiones propias de TaskHub, no requisitos de NIST:**

- La lista de bloqueo está **embebida en el código** en lugar de consultar un
  servicio de credenciales filtradas. Para un proyecto de este tamaño, una
  llamada externa en cada registro añadiría latencia y un punto de fallo
  desproporcionados. Conectar una fuente real queda como mejora futura si el
  proyecto llegara a tener usuarios reales.
- El umbral de 4 caracteres para comparar la contraseña con el nombre de
  usuario: por debajo hay demasiados falsos positivos (un usuario "ana"
  rechazaría frases con "semana" o "mañana").
- El espacio **no cuenta como símbolo**. Si contara, cualquier frase con
  espacios cumpliría el requisito sin llevar un solo símbolo y la regla no
  comprobaría nada.

**Usuarios existentes.** La política se aplica **solo al registro**. Quien creó
su cuenta cuando el mínimo era de 8 caracteres, o cuando no se exigía
composición, sigue pudiendo entrar con su contraseña de siempre: el validador
del inicio de sesión no comprueba longitud, composición ni lista de bloqueo.
Hacerlo dejaría fuera a esas cuentas y, además, daría respuestas distintas según
el caso, lo que revela información antes siquiera de comprobar las credenciales.
Hay tests en las capas unitaria y de API que fijan este comportamiento.

No hay ningún mecanismo de cambio de contraseña forzoso, así que tampoco se ha
añadido uno: endurecer la política no invalida nada. Quien quiera ponerse al día
puede hacerlo desde el botón «Contraseña» de la cabecera, y ahí sí se aplica la
política nueva.

### Límite de intentos: tres capas

Hay **tres mecanismos** sobre el inicio de sesión, y cada uno tapa lo que el
anterior deja abierto.

**1. Por dirección de origen.** `authLimiter`: diez intentos fallidos cada
quince minutos. Frena a quien ataca desde un sitio, que es el caso corriente.

Lo que no frena es a quien reparte. Con mil direcciones, diez intentos desde
cada una son diez mil contra la misma cuenta sin que ninguna agote su cuota.

**2. Retrasos progresivos por cuenta.** `accountSlowDown` cuenta por **nombre de
usuario**, no por origen, así que las mil direcciones caen todas en el mismo
cubo. Y en lugar de denegar, retrasa:

| Intentos fallidos | Retraso |
|---|---|
| 1-3 | ninguno |
| 4 | 1 s |
| 5 | 2 s |
| 6 | 4 s |
| 7 | 8 s |
| 8 o más | 30 s (tope) |

**Toda la defensa está en la asimetría de esa curva.** Quien conoce su
contraseña acierta al primer o segundo intento y no nota nada. Quien se
equivoca de verdad falla tres o cuatro veces y espera un segundo. Quien prueba a
ciegas necesita miles de intentos, y a treinta segundos cada uno pasa de miles
por minuto a **menos de ciento veinte por hora**.

**3. Tope duro, como red de seguridad.** `accountLimiter` corta a los doscientos
intentos por cuenta. Está deliberadamente lejos, y ese número tiene una historia.

#### Por qué se retrasa en vez de bloquear

La primera versión de esto era solo un bloqueo duro a los veinte intentos.
Resolvía el ataque repartido e introducía otro: **si bloquear es posible,
cualquiera que sepa un nombre de usuario puede provocarlo aposta** y dejar a su
dueño sin poder entrar.

Afinar el umbral no lo arregla. El problema no es el número, es el mecanismo: un
bloqueo es un binario —permitido o denegado—, y cualquier binario que un
atacante pueda forzar se convierte en un arma. Con veinte deja fuera a
cualquiera; con doscientos, si esos doscientos son alcanzables, también.

Lo que sí lo arregla es cambiar el castigo. **Un retraso no tiene estado
«bloqueado» que forzar.** Nadie queda fuera: el dueño de la cuenta atacada
escribe su contraseña, espera lo que toque y entra.

El tope duro sigue ahí para el caso patológico, pero con los retrasos por medio
llegar a doscientos exige **más de una hora de martilleo continuado** para
conseguir un bloqueo de quince minutos. Deja de ser un arma y pasa a ser lo que
debe ser: un límite que en la práctica no se toca.

#### Detalles que importan

La clave se normaliza en minúsculas igual que el índice único de la tabla: sin
eso, alternar mayúsculas abriría un cubo nuevo por cada variante.

El cubo se crea con el nombre que llegue, **exista o no** en la base de datos.
Si solo se contaran los usuarios reales, la diferencia de comportamiento entre un
nombre registrado y uno inventado sería una forma de enumerarlos.

Solo cuentan los fallos: quien entra a la primera no acumula nada aunque lo haga
cien veces al día.

**Qué comprueban los tests.** La curva de retrasos se fija con tests unitarios
sobre la función pura que la calcula —medir esperas reales daría un test lento y
frágil sin comprobar nada más—, incluyendo que sea monótona, que respete el
techo y que la fuerza bruta quede por debajo de doscientos intentos por hora. Y
en la suite de API hay una comprobación del punto delicado: desde **la misma
dirección** que acaba de quedar bloqueada para una cuenta, otra cuenta sigue
respondiendo con normalidad. Si el contador siguiera siendo por IP, ahí saldría
un 429.

**Confirmación de contraseña.** El registro pide escribir la contraseña dos
veces, pero eso es **asunto del formulario**: se compara en el cliente y no
viaja a la API, que sigue recibiendo solo `username` y `password`. No se
almacena, no se hashea y no existe en la base de datos.

## Administración

Existe un rol `admin` que puede listar usuarios, borrarlos —arrastrando sus
tareas por la clave foránea en cascada— y consultar un resumen global.

**El rol solo se concede por semilla.** Al arrancar, si están definidas
`ADMIN_USERNAME` y `ADMIN_PASSWORD`, ese usuario se crea o se promueve a
administrador. No hay ningún camino desde la API pública hasta el rol: el
registro fuerza `user`, el repositorio no acepta el rol como parámetro y no
existe ningún endpoint para promocionar a nadie. Quien controla las variables
de entorno del despliegue decide quién administra.

Tres decisiones que conviene explicar:

**El rol se lee de la base de datos en cada petición, no del JWT.** Si viajara
dentro del token, retirarle el rol a alguien no surtiría efecto hasta que su
token caducara, hasta siete días después. Cuesta una consulta, pero el permiso
comprobado es siempre el vigente.

**403 y no 404.** En las tareas ajenas se devuelve 404 para no revelar que
existen; aquí no aplica, porque quien pregunta ya está autenticado y la
existencia de una zona de administración no es un secreto.

**Un administrador no puede borrarse a sí mismo ni dejar la instancia sin
administradores.** Las dos comprobaciones existen para que un clic no deje la
aplicación sin nadie que pueda gestionarla.

## Decisiones de diseño

**SQL escrito a mano, sin ORM.** El acceso a datos usa el driver `pg` con
consultas parametrizadas (`$1`, `$2`…). Los valores nunca se concatenan en la
cadena SQL, que es lo que hace imposible la inyección.

**Restricciones en la base de datos, no solo en el código.** El título único por
usuario es un índice sobre `(user_id, LOWER(TRIM(title)))`. El servicio lo
comprueba antes para devolver un 409 con mensaje claro, pero la garantía real la
da el índice: dos peticiones simultáneas ya no pueden colarse entre la
comprobación y la escritura, como sí ocurría con el almacenamiento en ficheros.

**Composición obligatoria, con su contrapartida.** Se exigen mayúscula, número y
símbolo además de los 15 caracteres. Es una decisión de producto más estricta
que NIST, que desaconseja esas reglas por el patrón predecible que provocan; el
patrón se ataja bloqueando expresamente las contraseñas que ese patrón produce.
El detalle está en la sección de política de contraseñas.

**Filtrado en SQL, no en memoria.** Los filtros por estado, prioridad y texto se
resuelven en la consulta, así que solo viajan las filas que se piden. El resumen
por estado se calcula con una única agregación.

## Próximos pasos (opcional)

- **Despliegue**: servicio web en Render y base de datos en Neon.
- ~~**Revocación de sesiones**~~: access tokens de 15 minutos y refresh rotativo con tabla de sesiones.
- ~~**Base de datos real**~~: migrado de ficheros JSON a PostgreSQL.
- ~~**Autenticación**~~: implementado con JWT (login/registro).
- ~~**Asignar tareas a usuarios**~~: cada tarea tiene `userId` y solo se muestran las del usuario.

## Tecnologías

- **Frontend**: React 18, Vite.
- **Backend**: Node.js, Express, **TypeScript** (arquitectura router → controller → service → repository), JWT, bcrypt, express-rate-limit.
- **Base de datos**: PostgreSQL con el driver `pg` y consultas parametrizadas.
