import { describe, it, expect, vi, afterEach } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
import { requestLogger } from './logging.middleware.js';

/**
 * El registro de peticiones.
 *
 * Tres líneas de código, pero con una decisión dentro: se escribe **cuando la
 * respuesta termina**, no cuando llega la petición. Al revés no se podría
 * registrar el código de estado ni la duración, que es justo lo que sirve para
 * algo cuando se está mirando qué falla.
 */

/** Response simulado que deja disparar el evento `finish` a voluntad. */
function respuestaFalsa(statusCode = 200) {
  const oyentes: Record<string, () => void> = {};
  const res = {
    statusCode,
    on(evento: string, cb: () => void) {
      oyentes[evento] = cb;
      return this;
    },
  } as unknown as Response;
  return { res, terminar: () => oyentes.finish?.() };
}

const peticion = (extra: Partial<Request> = {}) =>
  ({ method: 'GET', originalUrl: '/api/tasks', ...extra }) as unknown as Request;

afterEach(() => {
  vi.restoreAllMocks();
});

describe('requestLogger', () => {
  it('deja pasar la petición inmediatamente', () => {
    // No puede bloquear: lo que hace es registrar, no decidir.
    const next = vi.fn();
    requestLogger(peticion(), respuestaFalsa().res, next as unknown as NextFunction);

    expect(next).toHaveBeenCalledTimes(1);
  });

  it('NO escribe nada hasta que la respuesta termina', () => {
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const { res } = respuestaFalsa();

    requestLogger(peticion(), res, (() => {}) as NextFunction);

    expect(log).not.toHaveBeenCalled();
  });

  it('al terminar registra método, ruta y código', () => {
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const { res, terminar } = respuestaFalsa(201);

    requestLogger(
      peticion({ method: 'POST', originalUrl: '/api/tasks' }),
      res,
      (() => {}) as NextFunction,
    );
    terminar();

    const linea = String(log.mock.calls[0][0]);
    expect(linea).toContain('POST');
    expect(linea).toContain('/api/tasks');
    expect(linea).toContain('201');
  });

  it('incluye la duración en milisegundos', () => {
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const { res, terminar } = respuestaFalsa();

    requestLogger(peticion(), res, (() => {}) as NextFunction);
    terminar();

    expect(String(log.mock.calls[0][0])).toMatch(/\d+ms/);
  });

  it('lleva marca de tiempo en formato ISO', () => {
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const { res, terminar } = respuestaFalsa();

    requestLogger(peticion(), res, (() => {}) as NextFunction);
    terminar();

    expect(String(log.mock.calls[0][0])).toMatch(/\[\d{4}-\d{2}-\d{2}T[\d:.]+Z\]/);
  });

  it('registra también los códigos de error', () => {
    // Sin esto, en el registro solo se verían las peticiones que van bien.
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const { res, terminar } = respuestaFalsa(500);

    requestLogger(peticion(), res, (() => {}) as NextFunction);
    terminar();

    expect(String(log.mock.calls[0][0])).toContain('500');
  });

  it('la URL se registra tal cual, con su cadena de consulta', () => {
    // Queda anotado: el término de búsqueda del usuario acaba en el registro.
    // Aquí no hay datos sensibles, pero es el patrón que en otras aplicaciones
    // termina con tokens o identificadores personales en los logs.
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const { res, terminar } = respuestaFalsa();

    requestLogger(
      peticion({ originalUrl: '/api/tasks?search=pan' }),
      res,
      (() => {}) as NextFunction,
    );
    terminar();

    expect(String(log.mock.calls[0][0])).toContain('search=pan');
  });
});
