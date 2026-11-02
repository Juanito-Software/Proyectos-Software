import { Request, Response, NextFunction } from 'express';
import { tokenService } from '../modules/auth/token.service.js';
import { ApiError } from '../utils/api-error.js';

/**
 * Identifica al usuario a partir del token de acceso.
 *
 * **No comprueba que el usuario siga existiendo**, y es una decisión con su
 * coste: si un administrador borra una cuenta, su token de acceso sigue
 * abriendo las rutas de lectura hasta que caduque —quince minutos como máximo,
 * que es justo para lo que se acortó—. Durante esa ventana la aplicación le
 * responde con una lista vacía, porque sus tareas se fueron en cascada, así que
 * no ve datos de nadie.
 *
 * Comprobarlo costaría una consulta a la base de datos en **cada petición**
 * autenticada, casi el doble de las que hace ahora la mayoría de rutas. Para
 * una aplicación con un plan gratuito de base de datos, pagar eso por adelantar
 * quince minutos una expulsión no compensa.
 *
 * Donde sí se comprueba es en `requireAdmin`, porque allí la consulta hace
 * falta de todas formas para leer el rol, y en la creación de tareas, que
 * traduce la violación de clave foránea a un 401 en lugar de reventar con un
 * 500. Esas son las dos vías por las que una cuenta borrada podía provocar algo
 * más que una pantalla vacía.
 *
 * Espera la cabecera `Authorization: Bearer <token>`. Si el token es válido,
 * rellena `req.userId` y `req.username` y deja pasar; si falta, está caducado o
 * su firma no cuadra, responde 401.
 *
 * @param req  petición entrante
 * @param _res no se usa
 * @param next continúa, o recibe un `ApiError` 401
 */
export function authMiddleware(req: Request, _res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;

  if (!token) {
    next(ApiError.unauthorized('Token de autenticación requerido'));
    return;
  }

  try {
    const payload = tokenService.verifyAccessToken(token);
    req.userId = payload.userId;
    req.username = payload.username;
    next();
  } catch {
    next(ApiError.unauthorized('Token inválido o expirado'));
  }
}
