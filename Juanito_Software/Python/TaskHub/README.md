# TaskHub

API REST de gestión de tareas construida con **FastAPI** (backend) y **React** (frontend). Autenticación JWT, CRUD completo de tareas, etiquetas con relación muchos-a-muchos y filtros por query params.

---

## Índice

1. [Objetivo](#objetivo)
2. [Stack](#stack)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Instalación y arranque](#instalación-y-arranque)
5. [Variables de entorno](#variables-de-entorno)
6. [Endpoints](#endpoints)
7. [Arquitectura backend](#arquitectura-backend)
8. [Arquitectura frontend](#arquitectura-frontend)
9. [Conceptos clave](#conceptos-clave)
10. [Diferencias respecto a Flask](#diferencias-respecto-a-flask)

---

## Objetivo

Proyecto de aprendizaje para cubrir en la práctica las piezas fundamentales de FastAPI:

- Registro e inicio de sesión con JWT real
- CRUD completo de tareas asociadas a cada usuario
- Etiquetas con relación muchos-a-muchos
- Filtros por estado y etiqueta vía query params
- Documentación interactiva automática en `/docs`

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + SQLAlchemy + Pydantic v2 |
| Autenticación | python-jose (JWT) + bcrypt |
| Base de datos | SQLite (dev) |
| Frontend | React 18 + Vite |
| Estilos | CSS custom properties (sin frameworks) |

---

## Estructura del proyecto

```
TaskHub/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # instancia FastAPI, CORS, monta routers
│   │   ├── config.py        # Pydantic Settings, lee .env
│   │   ├── database.py      # engine, SessionLocal, get_db
│   │   ├── models.py        # User, Task, Tag + tabla intermedia
│   │   ├── schemas.py       # schemas Pydantic (input/output separados)
│   │   ├── auth.py          # hash, verify, JWT, get_current_user
│   │   └── routers/
│   │       ├── auth.py      # POST /auth/register  POST /auth/token
│   │       └── tasks.py     # CRUD /tasks/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx         # punto de entrada
│       ├── App.jsx          # enruta según token
│       ├── AuthContext.jsx  # Context + Provider de autenticación
│       ├── api.js           # todas las llamadas fetch a la API
│       ├── AuthPage.jsx     # login/registro con tabs
│       ├── TasksPage.jsx    # dashboard, filtros, listado
│       ├── TaskCard.jsx     # tarjeta individual
│       ├── TaskForm.jsx     # modal crear/editar
│       └── index.css
└── README.md
```

---

## Instalación y arranque

### Backend

```bash
cd TaskHub/backend
python -m venv venv

# Windows
venv\Scripts\activate
# Unix
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000`
Documentación interactiva en `http://localhost:8000/docs` y `/redoc`

### Frontend

```bash
# En otra terminal
cd TaskHub/frontend
npm install
npm run dev
```

App disponible en `http://localhost:5173`

---

## Variables de entorno

Crea `backend/.env` con:

```env
DATABASE_URL=sqlite:///./taskhub.db
SECRET_KEY=cambia-esto-por-un-secreto-real-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Endpoints

### Autenticación

| Método | Ruta | Body | Descripción |
|---|---|---|---|
| `POST` | `/auth/register` | `{ email, username, password }` | Registro |
| `POST` | `/auth/token` | form-urlencoded `{ username, password }` | Login, devuelve JWT |

### Tareas *(requieren `Authorization: Bearer <token>`)*

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/tasks/` | Lista todas las tareas del usuario |
| `GET` | `/tasks/?completed=true` | Solo completadas |
| `GET` | `/tasks/?tag=trabajo` | Filtrar por etiqueta |
| `POST` | `/tasks/` | Crear tarea |
| `GET` | `/tasks/{id}` | Obtener una tarea |
| `PATCH` | `/tasks/{id}` | Actualizar parcialmente |
| `DELETE` | `/tasks/{id}` | Eliminar |

---

## Arquitectura backend

### Flujo de una petición

```
Cliente HTTP
    │
    ▼
FastAPI valida el body con el schema Pydantic de entrada
    │
    ▼
Se resuelven las dependencias: get_db() → sesión  /  get_current_user() → usuario
    │
    ▼
Lógica del router: consultas SQLAlchemy
    │
    ▼
Respuesta serializada con el schema Pydantic de salida (response_model)
```

### Ficheros clave

| Fichero | Responsabilidad |
|---|---|
| `main.py` | Instancia `FastAPI`, registra routers, aplica CORS, crea tablas |
| `config.py` | `BaseSettings` lee `.env` y valida tipos automáticamente |
| `database.py` | `engine`, `SessionLocal`, `get_db` (generador con `yield`) |
| `models.py` | Modelos SQLAlchemy: `User`, `Task`, `Tag`, tabla `task_tags` |
| `schemas.py` | Schemas Pydantic separados por dirección: `*Create`, `*Update`, `*Public` |
| `auth.py` | `hash_password`, `verify_password`, `create_access_token`, `get_current_user` |

---

## Arquitectura frontend

### Flujo de autenticación

1. `App.jsx` lee el token de `AuthContext`
2. Sin token → `AuthPage` (login/registro)
3. Login llama `POST /auth/token` con `form-urlencoded` (formato que espera `OAuth2PasswordRequestForm`)
4. JWT se guarda en `localStorage` y se inyecta en `Authorization: Bearer` en cada petición
5. Logout limpia `localStorage` → vuelve a `AuthPage`

### Gestión de estado

`TasksPage` mantiene la lista de tareas en `useState` y recarga con `useCallback + useEffect` cuando cambian los filtros. Sin librería de estado global (Redux, Zustand) porque el árbol de componentes es pequeño.

### CORS

`CORSMiddleware` configurado con `allow_origins=["http://localhost:5173"]`. En producción actualizar al dominio real.

---

## Conceptos clave

| Concepto | Dónde se aplica |
|---|---|
| `Depends()` | `get_db` y `get_current_user` inyectados en cada endpoint |
| Schemas Pydantic separados | `TaskCreate` (entrada) vs `TaskPublic` (salida) |
| `from_attributes = True` | Permite construir schemas desde objetos SQLAlchemy |
| `model_dump(exclude_unset=True)` | PATCH real: solo actualiza los campos enviados |
| `yield` en `get_db` | FastAPI ejecuta el `finally` (cierre de sesión) tras el endpoint |

---

## Diferencias respecto a Flask

| Aspecto | Flask | FastAPI |
|---|---|---|
| Validación | Manual o Marshmallow | Automática con Pydantic |
| Documentación | No existe por defecto | `/docs` y `/redoc` gratis |
| Async | Soporte limitado | Nativo desde el diseño |
| Dependencias | `g`, contexto de aplicación | `Depends()` explícito |
| Rutas | Blueprints | `APIRouter` (mismo concepto) |
| Servidor | Werkzeug / Gunicorn | Uvicorn (ASGI) |

SQLAlchemy se usa igual en ambos frameworks. La única diferencia real es cómo se obtiene la sesión (`Depends(get_db)` en vez de `g.db`), no cómo se usa una vez obtenida.
