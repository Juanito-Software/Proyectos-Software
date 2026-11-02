import 'express';

/**
 * Amplía el tipo `Request` de Express con los datos del usuario autenticado.
 *
 * authMiddleware guarda aquí los datos del JWT verificado para que el resto
 * de la petición (controllers, services) los use sin volver a decodificar el
 * token. Son opcionales porque en las rutas públicas no existen; en las
 * protegidas, el middleware garantiza que están rellenos (por eso los
 * controladores usan `req.userId!`).
 */
declare global {
  namespace Express {
    interface Request {
      /** Id (UUID) del usuario dueño del token. */
      userId?: string;
      /** Nombre de usuario del token, útil para logs. */
      username?: string;
    }
  }
}

export {};
