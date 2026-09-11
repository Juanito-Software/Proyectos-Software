import { NextFunction, Request, Response } from 'express';
import { ZodError } from 'zod';
import { ApiError } from '../utils/ApiError';
import { logger } from '../config/logger';

/**
 * Errores de validacion agrupados por campo: `{ name: [...], email: [...] }`.
 *
 * No se usa `err.flatten().fieldErrors` porque `validate` envuelve el esquema
 * en `{ body, query, params }`, y flatten agrupa por el PRIMER segmento de la
 * ruta: todo acababa bajo una unica clave `body` y el nombre del campo se
 * perdia. Aqui se quita ese primer segmento.
 */
function fieldErrors(err: ZodError): Record<string, string[]> {
  const result: Record<string, string[]> = {};
  for (const issue of err.issues) {
    const path = issue.path.length > 1 && ['body', 'query', 'params'].includes(String(issue.path[0]))
      ? issue.path.slice(1)
      : issue.path;
    const key = path.join('.') || '_';
    (result[key] ??= []).push(issue.message);
  }
  return result;
}

/**
 * `express.json()` lanza un error con `type: 'entity.parse.failed'` y estado
 * 400 cuando el cuerpo no es JSON valido. Sin tratarlo aqui caia en la rama
 * generica y la API respondia 500 —y lo registraba como fallo del servidor—
 * por un error del cliente.
 */
function isBodyParseError(err: unknown): boolean {
  return typeof err === 'object' && err !== null && (err as { type?: unknown }).type === 'entity.parse.failed';
}

export function errorHandler(err: unknown, _req: Request, res: Response, _next: NextFunction) {
  if (err instanceof ZodError) {
    return res.status(400).json({
      message: 'Error de validación',
      errors: fieldErrors(err),
    });
  }

  if (isBodyParseError(err)) {
    return res.status(400).json({ message: 'El cuerpo de la petición no es JSON válido' });
  }

  if (err instanceof ApiError) {
    if (err.statusCode >= 500) logger.error({ err }, err.message);
    return res.status(err.statusCode).json({
      message: err.message,
      ...(err.details ? { details: err.details } : {}),
    });
  }

  logger.error({ err }, 'Error no controlado');
  return res.status(500).json({ message: 'Error interno del servidor' });
}

export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({ message: `Ruta no encontrada: ${req.method} ${req.originalUrl}` });
}
