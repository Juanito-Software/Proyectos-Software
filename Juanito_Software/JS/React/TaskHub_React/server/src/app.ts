import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
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
import { env, isProduction } from './config/env.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Fábrica en vez de una instancia exportada directamente: así verify.ts puede
// crear la app DESPUÉS de fijar DB_SCHEMA al esquema temporal de pruebas, sin
// tocar nunca los datos reales del usuario.
export function createApp() {
  const app = express();

  const startTime = new Date();
  let requestCount = 0;

  // En producción la aplicación vive detrás del proxy de Render, que añade la
  // IP real del visitante en la cabecera X-Forwarded-For. Sin esto, Express
  // ve siempre la IP del proxy y el limitador de peticiones cuenta a todo el
  // mundo como un único cliente: bastaría un visitante activo para dejar la
  // aplicación bloqueada para el resto.
  //
  // Se confía exactamente en UN salto, no en `true`. Confiar en todos dejaría
  // que cualquiera se inventara la cabecera y se saltara el límite cambiando
  // de IP falsa en cada petición, que es justo lo contrario de lo que se
  // quiere. En local no hay proxy, así que no se activa.
  if (isProduction) {
    app.set('trust proxy', 1);
  }

  // ── Cabeceras de seguridad ─────────────────────────────────────────────
  //
  // helmet pone una docena de cabeceras que el navegador respeta: impide que
  // la página se cargue dentro de un iframe ajeno (clickjacking), evita que
  // el navegador adivine el tipo de contenido, y oculta que el servidor es
  // Express.
  //
  // La CSP se define a mano porque el playground es una página con estilos y
  // scripts en línea: la política por defecto de helmet los bloquearía y
  // dejaría el playground inservible. Se permite 'unsafe-inline' solo donde
  // hace falta y se prohíbe cargar recursos de terceros.
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'"],
          // El playground engancha sus acciones con atributos onclick en el
          // HTML. helmet pone por defecto script-src-attr 'none', que los
          // bloquea todos: la página carga pero ningún botón responde.
          //
          // Es una concesión consciente y acotada: el playground es una
          // herramienta de desarrollo de un solo fichero, y su contenido
          // dinámico ya se inserta con textContent y escapeHTML, nunca
          // interpretando HTML de terceros. La alternativa —reescribir los
          // ~40 manejadores como addEventListener— es lo correcto a medio
          // plazo y está anotado como pendiente.
          scriptSrcAttr: ["'unsafe-inline'"],
          styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
          fontSrc: ["'self'", 'https://fonts.gstatic.com', 'data:'],
          imgSrc: ["'self'", 'data:'],
          connectSrc: ["'self'"],
          objectSrc: ["'none'"],
          frameAncestors: ["'none'"],
          baseUri: ["'self'"],
          formAction: ["'self'"],
        },
      },
      // El navegador recordará durante un año que este dominio solo se sirve
      // por HTTPS. Render ya redirige, pero esto evita la primera petición en
      // claro de quien escriba la dirección a mano.
      hsts: isProduction ? { maxAge: 31536000, includeSubDomains: true } : false,
      // Necesario para que el playground pueda cargar tipografías de Google.
      crossOriginEmbedderPolicy: false,
    }),
  );

  // ── CORS ───────────────────────────────────────────────────────────────
  //
  // Antes se aceptaba cualquier origen. Ahora solo tres casos:
  //
  // 1. Sin cabecera Origin: curl, los tests, el propio servidor. CORS es una
  //    protección del navegador; bloquear esto no aporta seguridad y rompe
  //    herramientas legítimas.
  // 2. El MISMO origen que sirve la aplicación. Es imprescindible: el
  //    navegador manda `Origin` también en las peticiones POST del mismo
  //    sitio, así que sin este caso el propio cliente se quedaría fuera en
  //    cuanto alguien intentara iniciar sesión.
  // 3. Los orígenes declarados en ALLOWED_ORIGINS, para clientes externos.
  //
  // Se usa la forma con delegado porque hace falta `req` para saber desde qué
  // host se está sirviendo, y así funciona en cualquier dominio sin tener que
  // declararlo en la configuración.
  app.use(
    cors((req, callback) => {
      const origin = req.headers.origin;

      if (!origin) {
        callback(null, { origin: true, credentials: false });
        return;
      }

      const host = req.headers.host;
      const esMismoOrigen =
        !!host && (origin === `https://${host}` || origin === `http://${host}`);

      if (esMismoOrigen || env.allowedOrigins.includes(origin)) {
        callback(null, { origin: true, credentials: false });
        return;
      }

      // No se lanza un error: eso devolvería un 500 y ocultaría la causa.
      // Sin la cabecera de permiso, el navegador bloquea la respuesta por su
      // cuenta, que es exactamente el comportamiento que define CORS.
      callback(null, { origin: false, credentials: false });
    }),
  );

  // Límite explícito al tamaño del cuerpo: sin él, Express acepta hasta 100 kB
  // por defecto, pero conviene que el número sea una decisión y no un
  // accidente. Una tarea no necesita más de 100 kB.
  app.use(express.json({ limit: '100kb' }));
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
