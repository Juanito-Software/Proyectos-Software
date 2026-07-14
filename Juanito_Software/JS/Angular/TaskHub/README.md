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

## 10. Consideraciones de Desarrollo

- Se recomienda mantener el backend y frontend en carpetas separadas.
- Las variables sensibles deben almacenarse en archivos `.env` y no subirse al control de versiones.
- Prisma debe mantenerse sincronizado con el esquema de base de datos.
- Se recomienda revisar periódicamente la documentación de Angular y Prisma para mantener compatibilidad.

## 11. Estado del Proyecto

Este proyecto se encuentra en desarrollo y su estructura base ya está definida para soportar autenticación, gestión de proyectos y tareas. El tablero Kanban y la vista de detalle/edición de tareas con comentarios ya están operativos; quedan pendientes la gestión avanzada de miembros (invitaciones), notificaciones e historial de actividad.

## 12. Nota Final

TaskHub es una base sólida para un sistema de gestión de tareas colaborativo con arquitectura modular, separación entre backend y frontend, y uso de tecnologías modernas.
