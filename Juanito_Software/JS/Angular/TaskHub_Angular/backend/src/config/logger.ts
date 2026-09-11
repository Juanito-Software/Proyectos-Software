import pino, { DestinationStream, Logger, LoggerOptions } from 'pino';
import { env, isProduction } from './env';

/**
 * Cabeceras que NUNCA deben llegar a un log.
 *
 * pino-http escribe las cabeceras completas de cada peticion y de cada
 * respuesta en la linea «request completed», que sale con nivel `info`: el
 * mismo nivel que usa produccion. Sin esta lista, cada token de acceso
 * (`authorization`) y cada refresh token (en `cookie` al llegar y en
 * `set-cookie` al emitirse, valido 7 dias) quedaban en texto plano en los
 * logs. Quien pudiera leerlos podia suplantar cualquier sesion. Comprobado
 * lanzando la aplicacion con NODE_ENV=production antes del arreglo.
 *
 * La redaccion se hace en el logger y no en las opciones de pino-http a
 * proposito: `redact` es una opcion del constructor de pino, y pino-http la
 * ignora cuando recibe un logger ya creado, que es lo que hace app.ts.
 */
export const REDACTED_PATHS = [
  'req.headers.authorization',
  'req.headers.cookie',
  'res.headers["set-cookie"]',
];

export function buildLoggerOptions(level?: string): LoggerOptions {
  return {
    // En los tests el log se apaga: cada peticion escribia unas 40 lineas y los
    // fallos quedaban enterrados entre cientos de ellas. Los tests que necesitan
    // ver el log pasan su propio nivel.
    level: level ?? (env.nodeEnv === 'test' ? 'silent' : isProduction ? 'info' : 'debug'),
    redact: { paths: REDACTED_PATHS, censor: '[REDACTED]' },
  };
}

/**
 * Con `destination` se escribe ahi, sin transporte; asi los tests pueden leer
 * exactamente lo que se registraria. Sin ella, se usa pino-pretty en desarrollo
 * y JSON por la salida estandar en produccion y en tests.
 */
export function createLogger(opts: { level?: string; destination?: DestinationStream } = {}): Logger {
  const options = buildLoggerOptions(opts.level);
  if (opts.destination) return pino(options, opts.destination);

  const usePretty = !isProduction && env.nodeEnv !== 'test';
  return pino({
    ...options,
    transport: usePretty
      ? {
          target: 'pino-pretty',
          options: { colorize: true, translateTime: 'HH:MM:ss', ignore: 'pid,hostname' },
        }
      : undefined,
  });
}

export const logger = createLogger();
