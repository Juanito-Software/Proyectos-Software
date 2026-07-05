import { createApp } from './app';
import { env } from './config/env';
import { logger } from './config/logger';
import { prisma } from './config/prisma';

const app = createApp();

const server = app.listen(env.port, () => {
  logger.info(`Servidor escuchando en http://localhost:${env.port} (${env.nodeEnv})`);
});

async function shutdown(signal: string) {
  logger.info(`Señal ${signal} recibida, cerrando servidor...`);
  server.close(async () => {
    await prisma.$disconnect();
    logger.info('Servidor y conexión a base de datos cerrados correctamente');
    process.exit(0);
  });
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
