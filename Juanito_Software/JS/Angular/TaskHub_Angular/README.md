# TaskHub

Proyecto: TaskHub
Tecnologías: Node.js, TypeScript, Express, Prisma, PostgreSQL, Angular, Material

## 1. Descripción General

TaskHub es una aplicación web para la gestión de proyectos y tareas. Permite crear proyectos, asignar miembros, gestionar tareas con estados y prioridades, y mantener comentarios asociados a cada tarea.

El sistema está dividido en dos partes:

- **Backend**: API REST desarrollada con Node.js + TypeScript + Express + Prisma.
- **Frontend**: interfaz web desarrollada con Angular.

## 2. Objetivo

Proporcionar una herramienta sencilla y escalable para organizar trabajo colaborativo mediante proyectos, miembros y tareas.

## 3. Arquitectura

El proyecto está organizado en dos módulos principales:

### Backend

- `src/app.ts`: configuración principal de la aplicación.
- `src/server.ts`: punto de entrada del servidor.
- `src/controllers/`: controladores de autenticación, usuarios, proyectos y tareas.
- `src/services/`: lógica de negocio.
- `src/repositories/`: acceso a datos.
- `src/routes/`: definición de rutas de la API.
- `src/middlewares/`: autenticación, validación y manejo de errores.
- `src/validators/`: validaciones de entradas.
- `src/config/`: configuración de entorno, logger y Prisma.
- `prisma/schema.prisma`: esquema de base de datos.

### Frontend

- `src/app/`: estructura principal de la aplicación Angular.
- `src/app/core/`: servicios, guards e interfaces compartidas.
- `src/app/features/`: módulos funcionales como autenticación y dashboard.
- `src/app/shared/`: componentes compartidos.

## 4. Funcionalidades Principales

- Registro e inicio de sesión de usuarios.
- Gestión de proyectos.
- Gestión de miembros por proyecto.
- Creación, edición, asignación y seguimiento de tareas mediante tablero Kanban con arrastrar y soltar.
- Vista de detalle de tarea: edición de estado, prioridad, responsable y fecha límite, con hilo de comentarios.
- Estados de tarea: `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`.
- Prioridades: `LOW`, `MEDIUM`, `HIGH`, `URGENT`.
- Comentarios en tareas.
- Autenticación basada en JWT y refresh tokens.
- Permisos por rol dentro de cada proyecto (ver abajo).

### Quién puede hacer qué con las tareas

| Rol en el proyecto | Ver tareas | Crear, editar, borrar y comentar |
|---|---|---|
| `OWNER` | Sí | Sí |
| `EDITOR` | Sí | Sí |
| `VIEWER` | Sí | No — `403` |
| Ajeno al proyecto | No — `403` | No — `403` |

El propietario del proyecto cuenta como `OWNER` aunque le falte la fila de
miembro. Un proyecto o una tarea que no existen responden `404`.

Hasta septiembre de 2026 las rutas de `/api/tasks` solo exigían estar
autenticado: cualquier cuenta —y el registro es libre— podía listar, leer,
editar y borrar las tareas de cualquier proyecto. Los proyectos sí comprobaban
la pertenencia; las tareas no. Lo destaparon los primeros tests que atacaban la
API por HTTP.

## 5. Modelos de Datos

El esquema de base de datos incluye los modelos:

- `User`
- `RefreshToken`
- `Project`
- `ProjectMember`
- `Task`
- `Comment`

Relaciones principales:

- Un usuario puede ser propietario de varios proyectos.
- Un proyecto tiene múltiples miembros y tareas.
- Una tarea pertenece a un proyecto, puede tener un responsable y un creador.
- Una tarea puede tener múltiples comentarios.

## 6. Tecnologías Utilizadas

### Backend

- Node.js
- TypeScript
- Express
- Prisma ORM
- PostgreSQL
- JWT
- bcrypt
- Zod
- Vitest

### Frontend

- Angular 19
- Angular Material
- RxJS
- TypeScript
- Angular SSR

## 7. Requisitos Previos

- Node.js instalado.
- npm o pnpm.
- PostgreSQL configurado.
- Variable de entorno `DATABASE_URL`.
- Variable de entorno `JWT_SECRET`, si aplica.

## 8. Instalación

### Backend

1. Entrar en la carpeta `backend`.
2. Ejecutar `npm install`.
3. Configurar el archivo `.env` con las variables necesarias.
4. Ejecutar `npx prisma generate`.
5. Ejecutar `npx prisma migrate dev`.
6. Ejecutar `npm run dev`.
7. El servidor queda disponible en `http://localhost:3000`.

### Frontend

1. Entrar en la carpeta `frontend`.
2. Ejecutar `npm install`.
3. Ejecutar `npm start`.
4. La aplicación queda disponible en `http://localhost:4200`.

## 9. Comandos Útiles

### Backend

- `npm run dev`: iniciar el servidor en modo desarrollo.
- `npm run build`: compilar TypeScript.
- `npm run start`: iniciar la versión compilada.
- `npm run prisma:generate`: generar cliente Prisma.
- `npm run prisma:migrate`: aplicar migraciones.
- `npm run prisma:seed`: cargar datos iniciales.
- `npm run test`: ejecutar pruebas.

### Frontend

- `npm start`: iniciar la aplicación Angular.
- `npm run build`: construir la aplicación.
- `npm run test`: ejecutar pruebas.

## 10. Tests

**145 tests con Vitest en el backend.** No necesitan base de datos ni
`prisma generate`: sustituyen `config/prisma` y `@prisma/client` por dobles, y
`src/tests/setup.ts` inyecta las variables de entorno mínimas para que
`config/env.ts` no lance al importarse.

```bash
cd backend
npm ci
npm test
```

Hay dos clases de test, y prueban cosas distintas:

- **De servicio** (`*.service.test.ts`): llaman a la lógica directamente.
- **HTTP** (`*.http.test.ts`): levantan la aplicación real con `createApp()`
  en un puerto libre y le hacen peticiones con el `fetch` de Node. Solo se
  sustituyen los repositorios, así que rutas, middlewares, validación,
  controladores y manejador de errores son los de producción. Sin supertest:
  `fetch` viene con Node 22 y no añade dependencias.

| Fichero | Tests | Qué cubre |
|---|---|---|
| `src/tests/tasks.http.test.ts` | 33 | Permisos de tareas por rol: estado HTTP **y** si la escritura llegó al repositorio |
| `src/tests/token.service.test.ts` | 22 | Emisión y rotación de *refresh tokens*, conversión de caducidades |
| `src/tests/project.service.test.ts` | 19 | Lógica y control de acceso de proyectos, incluida la comprobación de rol |
| `src/tests/auth.http.test.ts` | 18 | Tokens rechazados (caducado, otra firma, `alg: none`, manipulado), `authorize(ADMIN)`, atributos de la cookie del *refresh token* |
| `src/tests/task.service.test.ts` | 15 | Lógica de tareas |
| `src/tests/auth.service.test.ts` | 10 | Registro, login y hashing |
| `src/tests/apiError.test.ts` | 10 | Errores de API y sus códigos |
| `src/tests/users.http.test.ts` | 8 | El hash nunca sale; cambio de contraseña; un `role` colado en el perfil no llega a la base de datos |
| `src/tests/errors.http.test.ts` | 5 | Validación por campo, JSON mal formado, errores internos sin detalle |
| `src/tests/rateLimit.http.test.ts` | 3 | Límite de intentos de login |
| `src/tests/task.repository.test.ts` | 2 | Que el filtro de pertenencia llega al `where` de Prisma |

Cada comportamiento de los tests HTTP se ha comprobado rompiéndolo a propósito
en el código: los 28 cambios probados ponen algún test en rojo.

Cobertura de líneas de `src/` (sin `server.ts`): **85 %**, antes 30 %. Lo que queda fuera son
sobre todo los repositorios, que solo se pueden probar contra una base de datos
de verdad.

### En CI

El job **`Node · tests`** de `.github/workflows/ci.yml` los ejecuta en cada push
con `npm ci && npm test`. Antes de eso estaban escritos, en verde y sin
ejecutarse en ningún sitio salvo a mano: el script `test` llevaba tiempo
declarado en `package.json` y nada lo llamaba.

El job exige además un mínimo de tests ejecutados. Comprobar solo que la suite
pasa no detecta que la suite haya **encogido** — si alguien borra un fichero o
lo renombra a algo que Vitest ya no reconoce, los que quedan siguen pasando y el
tick sale verde igual.

Si el job falla, `Monorepo en verde` —la comprobación obligatoria de `main`— cae
con él y la *pull request* no se puede fusionar.

### Frontend

**84 tests con Vitest**, lanzados por el constructor `@angular/build:unit-test`
de Angular sobre jsdom. Tampoco necesitan backend: las peticiones se interceptan
con `HttpTestingController`.

```bash
cd frontend
npm ci
npx ng test --no-watch
```

| Carpeta | Tests | Qué cubre |
|---|---|---|
| `src/app/core/` | 28 | Sesión y SSR, renovación de token con dos 401 simultáneos, guardia de rutas, contrato HTTP de los servicios |
| `src/app/features/auth/` | 11 | A dónde va el usuario tras login y registro; el aviso de credenciales no revela si el email existe |
| `src/app/features/dashboard/` | 15 | Crear y borrar proyectos: qué petición sale, cuál no sale al cancelar, y que «Eliminar» no navega al proyecto |
| `src/app/features/projects/` | 28 | Tablero: mover tarjetas guarda solo el estado y se revierte si el servidor falla; edición de tareas, fechas y comentarios |
| `src/app/app.component.spec.ts` | 2 | El del andamiaje del CLI |

Los componentes se prueban por su **efecto** —la petición que sale, o la que no
sale— y no por su estado interno. Cada comportamiento de `features/dashboard` y
`features/projects` se ha comprobado rompiéndolo a propósito en el código del
componente: los 21 cambios probados ponen algún test en rojo.

Un detalle que no se ve leyendo los tests: el de ida y vuelta de la fecha límite
fuerza la zona horaria a `America/Los_Angeles`. Los runners de CI están en UTC,
donde convertir en hora local en vez de en UTC da el mismo resultado y el error
pasaría sin ruido.

---

## 11. Consideraciones de Desarrollo

- Se recomienda mantener el backend y frontend en carpetas separadas.
- Las variables sensibles deben almacenarse en archivos `.env` y no subirse al control de versiones.
- Prisma debe mantenerse sincronizado con el esquema de base de datos.
- Se recomienda revisar periódicamente la documentación de Angular y Prisma para mantener compatibilidad.

## 12. Estado del Proyecto

Este proyecto se encuentra en desarrollo y su estructura base ya está definida para soportar autenticación, gestión de proyectos y tareas. El tablero Kanban y la vista de detalle/edición de tareas con comentarios ya están operativos; quedan pendientes la gestión avanzada de miembros (invitaciones), notificaciones e historial de actividad.

## 13. Nota Final

TaskHub es una base sólida para un sistema de gestión de tareas colaborativo con arquitectura modular, separación entre backend y frontend, y uso de tecnologías modernas.
