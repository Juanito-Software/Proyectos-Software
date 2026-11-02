/**
 * Registro de acceso: una línea por petición en la consola del servidor.
 *
 * Formato: `[fecha ISO] MÉTODO /ruta?query ESTADO - DURACIÓNms`.
 * No escribe cabeceras ni cuerpos, así que tokens, cookies y contraseñas no
 * llegan nunca al log por esta vía.
 */
import { Request, Response, NextFunction } from 'express';

/**
 * Middleware de Express que mide cuánto tarda cada petición.
 *
 * Arranca el cronómetro al entrar y escribe la línea en el evento `finish` de
 * la respuesta, cuando ya se conoce el código de estado. Si el cliente corta
 * la conexión antes de terminar, `finish` no se emite y la petición no queda
 * registrada.
 *
 * @param req  petición entrante
 * @param res  respuesta; se escucha su evento `finish`
 * @param next continúa la cadena inmediatamente (no espera a la respuesta)
 */
export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    const { method, originalUrl } = req;
    const { statusCode } = res;
    console.log(`[${new Date().toISOString()}] ${method} ${originalUrl} ${statusCode} - ${duration}ms`);
  });

  next();
}
