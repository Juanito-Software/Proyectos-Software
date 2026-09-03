import { describe, it, expect } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
import { validarUuid, validate, type ValidatorFn } from './validate.middleware.js';
import type { ApiError } from '../utils/api-error.js';

/**
 * Validación del formato de los identificadores de ruta.
 *
 * Sin esto, un `:id` mal formado llegaba a una consulta donde la columna es
 * `UUID`, PostgreSQL lanzaba el error 22P02 y la petición acababa en 500.
 * Cinco rutas estaban afectadas.
 */

const req = (params: Record<string, unknown>) => ({ params }) as unknown as Request;
const validador = validarUuid('id');

const VALIDO = 'a3f1c8d2-4b5e-4a7f-9c1d-2e3f4a5b6c7d';

describe('validarUuid', () => {
  it('acepta un UUID bien formado', () => {
    expect(validador(req({ id: VALIDO }))).toBeNull();
  });

  it('acepta mayúsculas: el hexadecimal no distingue', () => {
    expect(validador(req({ id: VALIDO.toUpperCase() }))).toBeNull();
  });

  it.each([
    ['texto suelto', 'no-soy-un-uuid'],
    ['cadena vacía', ''],
    ['solo números', '12345'],
    ['sin guiones', 'a3f1c8d24b5e4a7f9c1d2e3f4a5b6c7d'],
    ['un grupo de menos', 'a3f1c8d2-4b5e-4a7f-9c1d'],
    ['un carácter de más', VALIDO + 'a'],
    ['un carácter de menos', VALIDO.slice(0, -1)],
    ['con un carácter no hexadecimal', VALIDO.replace('a', 'z')],
    ['con espacios alrededor', ` ${VALIDO} `],
  ])('rechaza: %s', (_caso, valor) => {
    expect(validador(req({ id: valor }))).not.toBeNull();
  });

  it('rechaza cuando el parámetro no está', () => {
    expect(validador(req({}))).not.toBeNull();
  });

  it('rechaza un valor que no es texto', () => {
    // Express siempre entrega cadenas, pero el validador no debe confiar en
    // ello: una comprobación de tipo cuesta nada y evita un fallo raro.
    expect(validador(req({ id: 12345 }))).not.toBeNull();
  });

  it('el mensaje nombra el parámetro, para poder localizarlo', () => {
    const errores = validarUuid('taskId')(req({ taskId: 'malo' }));
    expect(errores!.join(' ')).toContain('taskId');
  });

  it('no se rompe con una carga de inyección en el identificador', () => {
    // Aunque nunca llegue a la consulta, el validador no debe lanzar.
    expect(() => validador(req({ id: "'; DROP TABLE tasks; --" }))).not.toThrow();
    expect(validador(req({ id: "'; DROP TABLE tasks; --" }))).not.toBeNull();
  });
});

describe('el envoltorio validate()', () => {
  /**
   * Convierte la lista de errores de un validador en un ApiError con el formato
   * de siempre. La regla que importa: **con un solo error se conserva su
   * mensaje**, con varios se agrupan. Si se agruparan siempre, mensajes útiles
   * como "El título es obligatorio" desaparecerían tras un genérico "Error de
   * validación" y el usuario no sabría qué corregir.
   */

  /** Ejecuta el middleware y devuelve lo que le llegó a next(). */
  function ejecutar(validador: ValidatorFn, peticion: Partial<Request> = {}): ApiError | undefined {
    let capturado: unknown;
    validate(validador)(peticion as Request, {} as Response, ((err?: unknown) => {
      capturado = err;
    }) as NextFunction);
    return capturado as ApiError | undefined;
  }

  it('deja pasar cuando el validador devuelve null', () => {
    expect(ejecutar(() => null)).toBeUndefined();
  });

  it('deja pasar cuando devuelve una lista vacía', () => {
    // No es lo mismo que null, pero significa lo mismo: nada que objetar.
    expect(ejecutar(() => [])).toBeUndefined();
  });

  it('con UN error conserva su mensaje', () => {
    const error = ejecutar(() => ['El título es obligatorio']);

    expect(error!.statusCode).toBe(400);
    expect(error!.message).toBe('El título es obligatorio');
    expect(error!.details).toBeUndefined();
  });

  it('con VARIOS agrupa y manda el detalle aparte', () => {
    const error = ejecutar(() => ['Falta el título', 'Estado inválido']);

    expect(error!.message).toBe('Error de validación');
    expect(error!.details).toEqual(['Falta el título', 'Estado inválido']);
  });

  it('siempre responde 400', () => {
    expect(ejecutar(() => ['uno'])!.statusCode).toBe(400);
    expect(ejecutar(() => ['uno', 'dos'])!.statusCode).toBe(400);
  });

  it('le pasa la petición entera al validador', () => {
    // Los validadores miran body, query y params según el caso.
    let recibida: Request | undefined;
    ejecutar((req) => {
      recibida = req;
      return null;
    }, { body: { title: 'x' }, query: { status: 'pending' }, params: { id: '1' } });

    expect(recibida!.body).toEqual({ title: 'x' });
    expect(recibida!.query).toEqual({ status: 'pending' });
    expect(recibida!.params).toEqual({ id: '1' });
  });

  it('se puede encadenar: validarUuid antes que el validador del cuerpo', () => {
    // Es como están montadas las rutas de tareas: primero la forma del
    // identificador, después el contenido.
    const conIdMalo = ejecutar(validarUuid('id'), { params: { id: 'no-es-uuid' } });
    const conIdBueno = ejecutar(validarUuid('id'), { params: { id: VALIDO } });

    expect(conIdMalo!.statusCode).toBe(400);
    expect(conIdBueno).toBeUndefined();
  });
});
