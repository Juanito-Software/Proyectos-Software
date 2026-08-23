# TaskHub – Gestor de tareas colaborativo minimalista

Aplicación full-stack para aprender **React** (frontend), **Express** (backend) y **API REST**. Varios usuarios pueden crear, editar y marcar tareas como completadas.

## Estructura del proyecto

```
TaskHub/
├── client/          # Frontend React (Vite)
│   ├── src/
│   │   ├── components/   # TaskList, TaskItem, TaskForm
│   │   ├── services/     # api.js (fetch a la API)
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── server/          # Backend Node.js + TypeScript (Express)
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/      # router · controller · service · validation · JWT
│   │   │   ├── users/     # repository (usuarios en data/users.json)
│   │   │   └── tasks/     # router · controller · service · repository · validation
│   │   ├── middleware/    # auth, rate limit, validación, errores, logging
│   │   ├── config/        # env.ts (variables de entorno) · paths.ts (rutas de datos)
│   │   ├── utils/         # ApiError
│   │   ├── app.ts         # fábrica de la app Express
│   │   ├── server.ts      # arranque + apagado ordenado
│   │   └── verify.ts      # smoke test end-to-end (npm run verify)
│   ├── data/         # tasks.json, users.json (almacenamiento)
│   └── package.json
└── README.md
```

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

Con el backend arrancado, abre **http://localhost:3001**: una interfaz para probar todos los endpoints en vivo, con consola de respuestas JSON, filtros, contador de peticiones y uptime. Requiere iniciar sesión (comparte el token con el cliente React vía `localStorage`).

## Verificación automática

```bash
cd server
npm run verify
```

Levanta la API en un puerto temporal, apunta el almacenamiento a una carpeta temporal (no toca `data/users.json` ni `data/tasks.json`) y ejecuta **24 comprobaciones end-to-end**: registro, login, acceso sin token, CRUD completo, validación de campos y de filtros, título duplicado, traducción `completed` ↔ `status`, los tres filtros, ambos endpoints de estadísticas, que el playground se sirva, aislamiento entre usuarios y borrado.

## Próximos pasos (opcional)

- **MongoDB**: ver guía paso a paso en [`docs/MONGO_GUIA.md`](docs/MONGO_GUIA.md).
- ~~**Autenticación**~~: implementado con JWT (login/registro).
- ~~**Asignar tareas a usuarios**~~: cada tarea tiene `userId` y solo se muestran las del usuario.

## Tecnologías

- **Frontend**: React 18, Vite.
- **Backend**: Node.js, Express, **TypeScript** (arquitectura router → controller → service → repository, como en TaskHub2), JWT, bcrypt, express-rate-limit.
- **Almacenamiento**: JSON en `server/data/` (listo para cambiar a MongoDB).
