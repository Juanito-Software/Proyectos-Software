import { describe, it, expect } from 'vitest';
import type { Request } from 'express';
import { validarUuid } from './validate.middleware.js';

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
