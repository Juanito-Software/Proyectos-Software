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
├── client/                   # Frontend React (Vite)
│   ├── src/
│   │   ├── components/       # TaskList · TaskItem · TaskForm · AuthForm
│   │   ├── context/          # AuthContext (sesión compartida con el playground)
│   │   ├── services/         # api.js · authApi.js (abren el envoltorio de respuesta)
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── server/                   # Backend Node.js + TypeScript (Express)
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/         # router · controller · service · validation · JWT
│   │   │   ├── users/        # repository (SQL) · types (rol user/admin)
│   │   │   ├── tasks/        # router · controller · service · repository · validation
│   │   │   └── admin/        # router · controller · service (solo rol admin)
│   │   ├── middleware/       # auth · admin · rate limit · validación · errores · logging
│   │   ├── config/           # env · db (pool) · schema (DDL) · seed-admin
│   │   ├── utils/            # ApiError · ApiResponse
│   │   ├── types/            # express.d.ts (userId en Request)
│   │   ├── public/           # playground de la API (se sirve en /playground)
│   │   ├── app.ts            # fábrica de la app Express
│   │   ├── server.ts         # arranque, semilla del admin y apagado ordenado
│   │   └── verify.ts         # suite end-to-end (npm run verify)
│   ├── scripts/
│   │   └── build-assets.mjs  # copia el playground y el cliente compilado a dist/
│   ├── .env.example          # plantilla de variables de entorno
│   └── package.json
└── README.md
```

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
- **Lista de tareas**: título, descripción y estado (pendiente/completada). Solo ves tus tareas.
- **Agregar tarea**: formulario arriba de la lista.
- **Editar tarea**: botón "Editar" en cada tarea; se muestra el mismo formulario con los datos actuales.
- **Eliminar tarea**: botón "Eliminar" con confirmación.
- **Marcar como completada**: checkbox en cada tarea.
- **Filtros**: Todas / Pendientes / Completadas.
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

## Verificación automática

```bash
cd server
npm run verify
```

Levanta la API en un puerto temporal y ejecuta **37 comprobaciones end-to-end** contra un **esquema de base de datos propio**, que se crea al empezar y se destruye al terminar — tus datos reales no se tocan, ni siquiera si la suite falla a mitad.

Cubre: registro, login, acceso sin token, CRUD completo, validación de campos y de filtros, título duplicado, traducción `completed` ↔ `status`, los tres filtros, ambos endpoints de estadísticas, que el playground se sirva, aislamiento entre usuarios, borrado, que el índice único rechace duplicados aunque cambien mayúsculas y espacios, y que borrar un usuario arrastre sus tareas.

Y, sobre el rol de administrador: que registrarse nunca conceda el rol —ni
enviando `role: "admin"` en el cuerpo—, que un usuario normal reciba 403, que
sin token se reciba 401 y no 403, que el administrador de la semilla exista y
entre, que el listado no filtre ningún hash de contraseña, y que un
administrador no pueda borrarse a sí mismo.

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
