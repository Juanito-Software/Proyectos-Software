/**
 * Punto de entrada del servidor (`npm run dev` / `npm start`).
 *
 * Orden de arranque:
 * 1. Crea o actualiza el esquema de PostgreSQL y siembra el administrador.
 * 2. Construye la app de Express (`createApp`) y escucha en `PORT`.
 * 3. Arranca la limpieza periódica de sesiones caducadas.
 *
 * También instala el apagado ordenado: ante Ctrl+C, una señal del sistema o
 * un error sin capturar, deja de aceptar conexiones, cierra el pool de la
 * base y sale.
 *
 * La lógica HTTP vive en `app.ts`, separada de aquí para que los tests puedan
 * crear la app sin abrir puertos ni conectar a la base.
 */
import { createApp } from './app.js';
import { env } from './config/env.js';
import { initSchema, closePool } from './config/db.js';
import { seedAdmin } from './config/seed-admin.js';
import { iniciarLimpiezaDeSesiones, detenerLimpiezaDeSesiones } from './config/session-cleanup.js';

/**
 * El esquema se crea antes de aceptar peticiones. Es idempotente, así que en
 * un despliegue nuevo levanta las tablas y en uno existente no hace nada. Si
 * la base de datos no responde, es preferible no arrancar a servir errores.
 */
try {
  await initSchema();
  console.log('Base de datos lista');
  await seedAdmin();
} catch (err) {
  console.error('No se pudo preparar la base de datos:', err);
  process.exit(1);
}

const app = createApp();

const server = app.listen(env.port, () => {
  console.log(`TaskHub API en http://localhost:${env.port}`);
});

// La tabla de sesiones acumula una fila por renovación y nadie las borraba.
iniciarLimpiezaDeSesiones();

/**
 * Una promesa rechazada sin capturar tumbaba el proceso sin cerrar el pool de
 * conexiones, que en los planes gratuitos son un recurso escaso. Se registra y
 * se apaga por el mismo camino ordenado que una señal del sistema.
 */
process.on('unhandledRejection', (motivo) => {
  console.error('[fatal] Promesa rechazada sin capturar:', motivo);
  void shutdown();
});

process.on('uncaughtException', (err) => {
  console.error('[fatal] Excepción sin capturar:', err);
  void shutdown();
});

/** Evita ejecutar el apagado dos veces si llegan varias señales seguidas. */
let shuttingDown = false;

/**
 * Apagado ordenado: para la limpieza de sesiones, deja de aceptar conexiones
 * nuevas, espera a que terminen las abiertas, cierra el pool y sale con 0.
 * Si en 5 segundos no ha terminado (conexiones colgadas), sale con 1 de todos
 * modos para no bloquear un redespliegue.
 */
async function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;

  console.log('\nCerrando servidor…');
  detenerLimpiezaDeSesiones();
  server.close(async () => {
    // Cerrar el pool deja que las consultas en curso terminen y libera las
    // conexiones en el servidor de base de datos, que en los planes gratuitos
    // son un recurso escaso.
    await closePool();
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 5000);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
