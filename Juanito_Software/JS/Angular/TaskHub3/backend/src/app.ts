import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import cookieParser from 'cookie-parser';
import pinoHttp from 'pino-http';
import { env } from './config/env';
import { logger } from './config/logger';
import { errorHandler, notFoundHandler } from './middlewares/errorHandler';
import { apiRouter } from './routes';

export function createApp(): Application {
  const app = express();

  app.use(helmet());
  app.use(
    cors({
      origin: env.corsOrigin,
      credentials: true,
    }),
  );
  app.use(compression());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  // La unica cookie de esta API es el refresh token. La proteccion frente a
  // CSRF esta en sus atributos (sameSite 'strict' y path acotado), definidos en
  // controllers/auth.controller.ts, no en un middleware aparte.
  //
  // No se usa middleware de token CSRF a proposito: el resto de la API se
  // autentica con Bearer en la cabecera Authorization, que el navegador no
  // adjunta automaticamente y por tanto no es vulnerable a CSRF. Solo dos rutas
  // (/api/auth/refresh y /api/auth/logout) dependen de la cookie, y el peor
  // desenlace posible en ellas es un cierre de sesion forzado.
  app.use(cookieParser());
  app.use(pinoHttp({ logger }));

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.use('/api', apiRouter);

  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}
