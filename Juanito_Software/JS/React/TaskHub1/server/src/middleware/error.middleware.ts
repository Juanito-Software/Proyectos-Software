import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/api-error.js';
import { ApiResponse } from '../utils/api-response.js';
import { isProduction } from '../config/env.js';

// Único punto de la app que escribe el cuerpo de una respuesta de error.
// Los controladores solo hacen next(err) y llegan aquí.
export function errorHandler(err: unknown, _req: Request, res: Response, _next: NextFunction): void {
  if (err instanceof ApiError) {
    res.status(err.statusCode).json(ApiResponse.error(err.message, err.details));
    return;
  }

  console.error('[unhandled]', err);
  const message = err instanceof Error ? err.message : 'Error interno del servidor';
  res.status(500).json(ApiResponse.error(isProduction ? 'Error interno del servidor' : message));
}
