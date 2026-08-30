# TaskHub – Gestor de tareas multiusuario

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
│   │   │   ├── AuthForm.jsx      # login y registro
│   │   │   ├── TaskForm.jsx      # alta y edición, con estado y prioridad
│   │   │   ├── TaskForm.test.jsx      ← 9 tests
│   │   │   ├── TaskItem.jsx      # tarjeta de tarea con sus distintivos
│   │   │   ├── TaskItem.test.jsx      ← 10 tests
│   │   │   └── TaskList.jsx      # lista, filtros y búsqueda
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # sesión, compartida con el playground
│   │   ├── services/
│   │   │   ├── api.js            # tareas; abre el envoltorio de respuesta
│   │   │   ├── api.test.js            ← 16 tests
│   │   │   ├── authApi.js        # login y registro
│   │   │   └── authApi.test.js        ← 8 tests
│   │   ├── test/setup.js         # limpia DOM y localStorage entre tests
│   │   ├── constants.js          # etiquetas de estado y prioridad, en un solo sitio
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js            # build, proxy en desarrollo y umbrales de cobertura
│   └── package.json
├── server/                       # Backend Node.js + TypeScript (Express)
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/             # router · controller · service · JWT
│   │   │   │   └── auth.validation.test.ts        ← 18 tests
│   │   │   ├── users/            # repository (SQL) · types (rol user/admin)
│   │   │   ├── tasks/            # router · controller · service · repository
│   │   │   │   ├── tasks.repository.test.ts       ← 13 tests
│   │   │   │   └── tasks.validation.test.ts       ← 25 tests
│   │   │   └── admin/            # router · controller · service (solo rol admin)
│   │   ├── middleware/           # auth · admin · rate limit · validación · errores · logging
│   │   ├── config/               # env · db (pool) · schema (DDL) · seed-admin
│   │   ├── utils/                # ApiError · ApiResponse
│   │   ├── types/                # express.d.ts (userId en Request)
│   │   ├── public/               # playground de la API (se sirve en /playground)
│   │   ├── app.ts                # fábrica de la app Express
│   │   ├── server.ts             # arranque, semilla del admin y apagado ordenado
│   │   └── verify.ts             # suite end-to-end de la API      ← 47 tests
│   ├── scripts/build-assets.mjs  # copia playground y cliente compilado a dist/
│   ├── vitest.config.ts          # tests unitarios: solo lógica pura, sin BD
│   ├── .env.example              # plantilla de variables de entorno
│   └── package.json
├── e2e/taskhub.spec.js           # end-to-end de navegador          ← 16 tests
├── docs/AUDITORIA_SEGURIDAD.md   # informe de la auditoría de seguridad
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

- **Login/Registro**: autenticación con JWT; sesión persistida en localStorage.
- **Lista de tareas**: título, descripción, estado (pendiente / en progreso / completada) y prioridad (baja / media / alta), con distintivos de color. Solo ves tus tareas.
- **Agregar y editar**: el mismo formulario, con selectores de estado y prioridad.
- **Eliminar tarea**: con confirmación.
- **Marcar como completada**: checkbox, como atajo de un clic para el caso más habitual.
- **Filtros y búsqueda**: por estado, por prioridad y por texto en título o descripción. **Los resuelve la API**, no el navegador: viajan como parámetros de consulta y solo llegan las tareas que se piden. La búsqueda espera 300 ms desde la última tecla para no lanzar una petición por carácter.
- **Notificaciones**: mensaje breve al crear o actualizar una tarea.

## API REST (ejemplos)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registro (`username`, `password`) |
| POST | `/api/auth/login` | Login (`username`, `password`) |
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

Las rutas de tareas requieren cabecera `Authorization: Bearer <token>`. Los títulos deben ser únicos **por usuario** (409 si se repite; dos usuarios distintos sí pueden tener el mismo título).

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

**162 en total**, repartidos en cuatro capas que prueban cosas distintas:

| Comando | Qué ejecuta | Cuántos | Necesita |
|---------|-------------|---------|----------|
| `npm test` | Unitarios de servidor y cliente | 56 + 43 | Nada |
| `npm run verify` | End-to-end de la API | 47 | PostgreSQL |
| `npm run test:e2e` | Navegador real (Playwright) | 16 | PostgreSQL y `npm run build` |
| `npm run ci` | Lint, tipos, unitarios y build | — | Nada |

Los **unitarios** cubren lógica pura —validadores, escapado de comodines de
`LIKE`, campos calculados, la capa de servicios del cliente y los componentes de
tarea— y corren en milisegundos sin nada instalado.

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

### Qué cubren las 47 comprobaciones de la API

Registro, login, acceso sin token, CRUD completo, validación de campos y de
filtros, título duplicado, traducción `completed` ↔ `status`, los tres filtros,
ambos endpoints de estadísticas, que el playground se sirva, aislamiento entre
usuarios, borrado, que el índice único rechace duplicados aunque cambien
mayúsculas y espacios, y que borrar un usuario arrastre sus tareas.

**Seguridad:** token firmado con otro secreto, caducado, sin firmar con
`alg: none`, sin identificador de usuario, de un usuario que ya no existe y con
formato inválido — todos deben devolver 401. Y cargas de inyección SQL en el
filtro de búsqueda, que deben tratarse como texto sin romper la consulta.

**Rol de administrador:** que registrarse nunca lo conceda —ni enviando
`role: "admin"` en el cuerpo—, que un usuario normal reciba 403, que sin token
se reciba 401 y no 403, que el administrador de la semilla exista y entre, que
el listado no filtre ningún hash de contraseña, y que un administrador no pueda
borrarse a sí mismo.

## Integración continua

Cada push y cada pull request ejecuta ocho jobs en GitHub Actions: lint, tipos,
unitarios del servidor, tests del cliente con cobertura, suite de la API contra
un PostgreSQL real, end-to-end de navegador, build de producción y auditoría de
dependencias. Todos cuelgan de un job final, `ci-ok`, del que puede colgarse la
regla de protección de rama sin tener que enumerar los demás.

El pipeline falla si falla cualquier test, si el build no produce servidor,
playground y cliente, si el lint o los tipos protestan, si la cobertura baja de
los umbrales, o si aparece una vulnerabilidad **alta o crítica**. Las moderadas
y bajas no lo bloquean: con `--audit-level=moderate` estaría en rojo permanente
por dependencias de desarrollo, y un CI siempre en rojo deja de mirarse.

El workflow está en `.github/workflows/taskhub-react-ci.yml`, con una copia en
la raíz del monorepo, que es donde GitHub los busca.

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

**Filtrado en SQL, no en memoria.** Los filtros por estado, prioridad y texto se
resuelven en la consulta, así que solo viajan las filas que se piden. El resumen
por estado se calcula con una única agregación.

## Próximos pasos (opcional)

- **Despliegue**: servicio web en Render y base de datos en Neon.
- ~~**Base de datos real**~~: migrado de ficheros JSON a PostgreSQL.
- ~~**Autenticación**~~: implementado con JWT (login/registro).
- ~~**Asignar tareas a usuarios**~~: cada tarea tiene `userId` y solo se muestran las del usuario.

## Tecnologías

- **Frontend**: React 18, Vite.
- **Backend**: Node.js, Express, **TypeScript** (arquitectura router → controller → service → repository), JWT, bcrypt, express-rate-limit.
- **Base de datos**: PostgreSQL con el driver `pg` y consultas parametrizadas.
