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
├── server/          # Backend Node.js (Express)
│   ├── routes/      # Rutas REST de tareas
│   ├── data/        # tasks.json (almacenamiento)
│   ├── store.js     # Lectura/escritura de tareas
│   ├── index.js
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
| GET | `/api/tasks` | Listar tareas del usuario (requiere token) |
| GET | `/api/tasks/:id` | Obtener una tarea |
| POST | `/api/tasks` | Crear tarea |
| PATCH | `/api/tasks/:id` | Actualizar parcial |
| PUT | `/api/tasks/:id` | Actualizar tarea completa |
| DELETE | `/api/tasks/:id` | Eliminar tarea |

Las rutas de tareas requieren cabecera `Authorization: Bearer <token>`.

## Próximos pasos (opcional)

- **MongoDB**: ver guía paso a paso en [`docs/MONGO_GUIA.md`](docs/MONGO_GUIA.md).
- ~~**Autenticación**~~: implementado con JWT (login/registro).
- ~~**Asignar tareas a usuarios**~~: cada tarea tiene `userId` y solo se muestran las del usuario.

## Tecnologías

- **Frontend**: React 18, Vite.
- **Backend**: Node.js, Express.
- **Almacenamiento**: JSON en `server/data/tasks.json` (listo para cambiar a MongoDB).
