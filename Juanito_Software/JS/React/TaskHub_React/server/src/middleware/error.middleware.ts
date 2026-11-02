import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/api-error.js';
import { ApiResponse } from '../utils/api-response.js';
import { isProduction } from '../config/env.js';

/**
 * Manejador de errores final de Express.
 *
 * Único punto de la app que escribe el cuerpo de una respuesta de error.
 * Los controladores solo hacen next(err) y llegan aquí.
 *
 * - Un `ApiError` es un error esperado (validación, 404, 409...): se responde
 *   con su código y su mensaje, que están pensados para el usuario.
 * - Cualquier otra cosa es un fallo inesperado: se registra completo en la
 *   consola y se responde 500. En producción el mensaje es genérico para no
 *   filtrar detalles internos (SQL, rutas, nombres de clases); en desarrollo
 *   se muestra el real para depurar.
 *
 * Express lo reconoce como manejador de errores por tener cuatro parámetros,
 * por eso `_next` está aunque no se use.
 *
 * @param err  lo que se pasó a `next(err)` o se lanzó en un handler
 * @param _req petición (no se usa)
 * @param res  respuesta en la que se escribe el error
 * @param _next obligatorio en la firma; no se llama
 */
export function errorHandler(err: unknown, _req: Request, res: Response, _next: NextFunction): void {
  if (err instanceof ApiError) {
    res.status(err.statusCode).json(ApiResponse.error(err.message, err.details));
    return;
  }

  console.error('[unhandled]', err);
  const message = err instanceof Error ? err.message : 'Error interno del servidor';
  res.status(500).json(ApiResponse.error(isProduction ? 'Error interno del servidor' : message));
}
