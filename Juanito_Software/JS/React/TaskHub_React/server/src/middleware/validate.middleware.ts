import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/api-error.js';

// Un validador es una función pura: recibe la request y devuelve la lista de
// errores encontrados, o null si todo está bien. Así los módulos (auth, tasks)
// declaran sus propias reglas sin acoplarse a Express ni a una librería de
// esquemas externa.
export type ValidatorFn = (req: Request) => string[] | null;

export function validate(validator: ValidatorFn) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    const errors = validator(req);
    if (errors && errors.length > 0) {
      // Con un único error se conserva el mensaje específico de siempre
      // (p. ej. "El título es obligatorio"); con varios se agrupan bajo un
      // mensaje genérico y el detalle va en `details`, que el cliente actual
      // ignora pero no rompe nada si lo lee.
      const message = errors.length === 1 ? errors[0] : 'Error de validación';
      next(ApiError.badRequest(message, errors.length > 1 ? errors : undefined));
      return;
    }
    next();
  };
}
