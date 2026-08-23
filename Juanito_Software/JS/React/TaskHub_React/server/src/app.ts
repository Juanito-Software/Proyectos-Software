import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { authRouter } from './modules/auth/auth.router.js';
import { tasksRouter } from './modules/tasks/tasks.router.js';
import { requestLogger } from './middleware/logging.middleware.js';
import { errorHandler } from './middleware/error.middleware.js';
import { ApiError } from './utils/api-error.js';
import { ApiResponse } from './utils/api-response.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Fábrica en vez de una instancia exportada directamente: así verify.ts puede
// crear la app DESPUÉS de fijar DATA_DIR a una carpeta temporal, sin tocar
// nunca los datos reales del usuario.
export function createApp() {
  const app = express();

  const startTime = new Date();
  let requestCount = 0;

  app.use(cors());
  app.use(express.json());
  app.use(requestLogger);

  app.use((_req: Request, _res: Response, next: NextFunction) => {
    requestCount++;
    next();
  });

  // Playground de la API en la raíz. En desarrollo se sirve desde src/public;
  // tras `npm run build`, desde dist/public (el script copia la carpeta).
  app.use(express.static(path.join(__dirname, 'public')));

  app.get('/api/health', (_req: Request, res: Response) => {
    res.json(ApiResponse.success({ ok: true }, 'TaskHub API'));
  });

  // Estadísticas del proceso. Público a propósito: no expone datos de ningún
  // usuario, solo salud del servidor (el resumen por usuario está en
  // GET /api/tasks/stats, que sí requiere token).
  app.get('/api/system/stats', (_req: Request, res: Response) => {
    const uptime = Math.floor((Date.now() - startTime.getTime()) / 1000);
    res.json(
      ApiResponse.success(
        {
          uptimeSeconds: uptime,
          uptimeFormatted: `${Math.floor(uptime / 60)}m ${uptime % 60}s`,
          totalRequests: requestCount,
          startedAt: startTime.toISOString(),
          nodeVersion: process.version,
          platform: process.platform,
        },
        'Estadísticas del sistema',
      ),
    );
  });

  app.use('/api/auth', authRouter);
  app.use('/api/tasks', tasksRouter);

  app.use((req: Request, _res: Response, next: NextFunction) => {
    next(ApiError.notFound(`No existe ${req.method} ${req.originalUrl}`));
  });

  app.use(errorHandler);

  return app;
}
