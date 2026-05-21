# express-ts-crud

API REST CRUD construida con **Express** y **TypeScript**, con un dashboard web interactivo (Glassmorphism) para gestionar tareas.

---

## Características

- CRUD completo de tareas (`GET`, `POST`, `PUT`, `DELETE`)
- Validación de datos con middleware (tipos, longitudes, duplicados)
- Dashboard visual accesible desde el navegador en `http://localhost:3000`
- Suite de pruebas automatizadas (`verify.ts`)
- Compilación multiplataforma: copia automática de assets estáticos al hacer build

---

## Requisitos

- [Node.js](https://nodejs.org/) v18 o superior
- npm

---

## Instalación

```bash
git clone <url-del-repositorio>
cd express-ts-crud
npm install
```

---

## Ejecución

### Modo desarrollo

**CMD:**
```cmd
npm run dev
```

**PowerShell** (si hay error de permisos con la directiva de ejecución):
```powershell
npm.cmd run dev
```

El servidor arrancará en `http://localhost:3000`.

---

### Modo producción

**CMD:**
```cmd
npm run build && npm start
```

**PowerShell:**
```powershell
npm.cmd run build; npm.cmd start
```

> El script de build transpila TypeScript y copia automáticamente `src/public` a `dist/public`, por lo que el dashboard queda disponible en producción sin pasos adicionales.

---

## Dashboard

Con el servidor corriendo, abre el navegador en:

```
http://localhost:3000
```

Desde el dashboard puedes:

- Crear, editar y eliminar tareas
- Filtrar por prioridad (`Low`, `Medium`, `High`) y estado (`Pending`, `In Progress`, `Completed`)
- Ver las respuestas JSON reales de la API en la consola simulada
- Probar el comportamiento del middleware de validación en tiempo real (títulos duplicados, datos inválidos, longitudes fuera de límite)

---

## Pruebas automatizadas

**CMD:**
```cmd
npm run verify
```

**PowerShell:**
```powershell
npm.cmd run verify
```

La suite cubre:

| Caso | Resultado esperado |
|---|---|
| `GET /api/tasks` — semillas iniciales | 3 tareas devueltas |
| `POST /api/tasks` — tarea válida | Registro correcto con ID único |
| `POST /api/tasks` — título duplicado | `400` por regla de negocio |
| `POST /api/tasks` — datos inválidos | `400` por validación de tipos y longitudes |
| `GET` por ID, `PUT` y `DELETE` | CRUD completo; estado restaurado a las 3 tareas iniciales |

---

## Estructura del proyecto

```
express-ts-crud/
├── src/
│   ├── public/
│   │   └── index.html        # Dashboard Glassmorphism
│   └── ...                   # Fuentes TypeScript
├── dist/                     # Salida compilada (generada con npm run build)
├── verify.ts                 # Suite de pruebas automatizadas
├── package.json
└── tsconfig.json
```

---

## Scripts disponibles

| Script | Descripción |
|---|---|
| `npm run dev` | Servidor de desarrollo con recarga automática |
| `npm run build` | Compila TypeScript y copia assets estáticos a `dist/` |
| `npm start` | Arranca el servidor desde la carpeta `dist/` (producción) |
| `npm run verify` | Ejecuta la suite de pruebas automatizadas |
