import { createApp } from './app.js';
import { env } from './config/env.js';
import { initSchema, closePool } from './config/db.js';
import { seedAdmin } from './config/seed-admin.js';

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

let shuttingDown = false;

async function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;

  console.log('\nCerrando servidor…');
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
