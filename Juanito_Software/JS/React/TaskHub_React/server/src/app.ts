import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { authRouter } from './modules/auth/auth.router.js';
import { tasksRouter } from './modules/tasks/tasks.router.js';
import { adminRouter } from './modules/admin/admin.router.js';
import { requestLogger } from './middleware/logging.middleware.js';
import { errorHandler } from './middleware/error.middleware.js';
import { ApiError } from './utils/api-error.js';
import { ApiResponse } from './utils/api-response.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Fábrica en vez de una instancia exportada directamente: así verify.ts puede
// crear la app DESPUÉS de fijar DB_SCHEMA al esquema temporal de pruebas, sin
// tocar nunca los datos reales del usuario.
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

  // El playground vive en /playground. En desarrollo se sirve desde
  // src/public; tras `npm run build`, desde dist/public (el script lo copia).
  //
  // redirect:false evita que express.static conteste con un 301 a
  // "/playground/" con barra final, que es lo que hace por defecto al servir
  // un directorio. La URL va a acabar en un CV: mejor sin saltos.
  const playgroundDir = path.join(__dirname, 'public');
  app.use('/playground', express.static(playgroundDir, { redirect: false }));
  app.get('/playground', (_req: Request, res: Response) => {
    res.sendFile(path.join(playgroundDir, 'index.html'));
  });

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
  app.use('/api/admin', adminRouter);

  // ── Cliente React ──────────────────────────────────────────────────────
  // El build del cliente se copia a dist/client durante `npm run build`. En
  // desarrollo esa carpeta no existe y no pasa nada: el cliente se sirve con
  // Vite en el 5173, que ya redirige /api al 3001.
  const clientDir = path.join(__dirname, 'client');
  if (fs.existsSync(clientDir)) {
    app.use(express.static(clientDir));
  }

  // A partir de aquí, cualquier ruta que no sea de la API es responsabilidad
  // del enrutador del cliente. El 404 en JSON se reserva para /api/*, para que
  // una llamada mal escrita a la API no devuelva el HTML de la aplicación.
  app.use((req: Request, res: Response, next: NextFunction) => {
    if (req.path.startsWith('/api/')) {
      return next(ApiError.notFound(`No existe ${req.method} ${req.originalUrl}`));
    }

    const indexFile = path.join(clientDir, 'index.html');
    if (req.method === 'GET' && fs.existsSync(indexFile)) {
      return res.sendFile(indexFile);
    }

    next(ApiError.notFound(`No existe ${req.method} ${req.originalUrl}`));
  });

  app.use(errorHandler);

  return app;
}
