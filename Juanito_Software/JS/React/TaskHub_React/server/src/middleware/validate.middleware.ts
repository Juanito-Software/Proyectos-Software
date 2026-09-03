import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/api-error.js';

// Un validador es una función pura: recibe la request y devuelve la lista de
// errores encontrados, o null si todo está bien. Así los módulos (auth, tasks)
// declaran sus propias reglas sin acoplarse a Express ni a una librería de
// esquemas externa.
export type ValidatorFn = (req: Request) => string[] | null;

/**
 * Formato de un UUID versión 4, que es lo que genera `gen_random_uuid()`.
 *
 * Se acepta cualquier versión y variante para no romper si algún día se
 * insertan identificadores generados por otra vía: lo que importa aquí es la
 * FORMA, no la procedencia. Ocho-cuatro-cuatro-cuatro-doce en hexadecimal.
 */
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * Comprueba que un parámetro de ruta tiene forma de UUID.
 *
 * Sin esto, un identificador mal formado llegaba tal cual a una consulta donde
 * la columna es `UUID`, PostgreSQL lanzaba el error 22P02 y la petición acababa
 * en **500**. Un 500 significa «el servidor ha fallado procesando una petición
 * válida»; aquí lo que ocurre es lo contrario, que el cliente ha mandado algo
 * que no es un identificador. Además ensuciaba cualquier métrica de errores con
 * fallos que no son fallos del servidor.
 *
 * Se responde **400 y no 404** porque no hay nada que ocultar: un valor que ni
 * siquiera tiene forma de identificador no puede coincidir con ningún recurso,
 * así que distinguir «mal formado» de «no existe» no le dice a un atacante nada
 * que no supiera. Y 400 es coherente con el resto de validaciones de entrada.
 */
export function validarUuid(nombre: string): ValidatorFn {
  return (req) => {
    const valor = req.params[nombre];
    if (typeof valor !== 'string' || !UUID.test(valor)) {
      return [`El identificador '${nombre}' no es válido`];
    }
    return null;
  };
}

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
