import { describe, it, expect } from 'vitest';
import { ApiError } from './api-error.js';

/**
 * El error de dominio del que cuelga toda la API.
 *
 * Parece trivial y por eso no tenía tests, pero **es quien decide el código
 * HTTP de cada fallo del sistema**. Si `notFound` empezara a devolver 400, la
 * API seguiría funcionando y los tests de la suite de API seguirían pasando —
 * comprueban el código concreto, sí, pero uno a uno; aquí se fija la tabla
 * entera de un vistazo.
 *
 * El contrato importa hacia fuera: el cliente distingue «sesión caducada» (401)
 * de «no tienes permiso» (403) y de «no existe» (404) por el número.
 */

describe('códigos de estado', () => {
  it.each([
    ['badRequest', ApiError.badRequest('x'), 400],
    ['unauthorized', ApiError.unauthorized(), 401],
    ['forbidden', ApiError.forbidden(), 403],
    ['notFound', ApiError.notFound(), 404],
    ['conflict', ApiError.conflict('x'), 409],
    ['internal', ApiError.internal(), 500],
  ])('%s produce un %i', (_nombre, error, esperado) => {
    expect(error.statusCode).toBe(esperado);
  });

  it('401 y 403 no se confunden entre sí', () => {
    // La distinción es la que separa "vuelve a entrar" de "no puedes entrar
    // aquí", y el cliente actúa distinto en cada caso: con un 401 borra la
    // sesión, con un 403 no.
    expect(ApiError.unauthorized().statusCode).not.toBe(ApiError.forbidden().statusCode);
  });
});

describe('mensajes', () => {
  it('conserva el mensaje que se le pasa', () => {
    expect(ApiError.notFound('Tarea no encontrada').message).toBe('Tarea no encontrada');
  });

  it.each([
    ['unauthorized', ApiError.unauthorized(), /no autenticado/i],
    ['forbidden', ApiError.forbidden(), /no autorizado/i],
    ['notFound', ApiError.notFound(), /no encontrado/i],
    ['internal', ApiError.internal(), /error interno/i],
  ])('%s tiene un mensaje por defecto razonable', (_nombre, error, patron) => {
    expect(error.message).toMatch(patron);
  });

  it('los mensajes por defecto no filtran detalle interno', () => {
    // Son los que acaban en la respuesta cuando nadie pasa uno propio, así que
    // no pueden mencionar la base de datos, rutas ni nombres de fichero.
    for (const error of [ApiError.unauthorized(), ApiError.forbidden(), ApiError.internal()]) {
      expect(error.message).not.toMatch(/postgres|sql|\/src\/|\.ts|node_modules/i);
    }
  });
});

describe('detalles', () => {
  it('badRequest los acepta, para la lista de errores de validación', () => {
    const error = ApiError.badRequest('Error de validación', ['falta título', 'estado inválido']);
    expect(error.details).toEqual(['falta título', 'estado inválido']);
  });

  it('quedan indefinidos cuando no se pasan', () => {
    expect(ApiError.badRequest('x').details).toBeUndefined();
  });

  it('los códigos que no los admiten no los inventan', () => {
    // unauthorized, forbidden, notFound y conflict tienen un solo argumento a
    // propósito: en esos casos el detalle sería información de más.
    for (const error of [
      ApiError.unauthorized('x'),
      ApiError.forbidden('x'),
      ApiError.notFound('x'),
      ApiError.conflict('x'),
    ]) {
      expect(error.details).toBeUndefined();
    }
  });
});

describe('se comporta como un Error de verdad', () => {
  it('es instancia de Error y de ApiError', () => {
    const error = ApiError.notFound();
    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(ApiError);
  });

  it('el manejador de errores puede distinguirlo con instanceof', () => {
    // Es exactamente lo que hace error.middleware para decidir si responde con
    // el código del dominio o con un 500 genérico.
    expect(new Error('cualquiera') instanceof ApiError).toBe(false);
    expect(ApiError.conflict('x') instanceof ApiError).toBe(true);
  });

  it('se llama ApiError', () => {
    expect(ApiError.notFound().name).toBe('ApiError');
  });

  it('tiene traza de pila', () => {
    expect(ApiError.internal().stack).toBeTruthy();
  });

  it('la traza no empieza dentro del propio constructor', () => {
    // `captureStackTrace(this, this.constructor)` recorta el ruido para que la
    // primera línea apunte a quien lanzó el error, no a esta clase.
    expect(ApiError.notFound().stack).not.toMatch(/at new ApiError/);
  });

  it('se puede lanzar y capturar conservando el código', () => {
    try {
      throw ApiError.conflict('Ya tienes una tarea con este título');
    } catch (err) {
      expect((err as ApiError).statusCode).toBe(409);
      expect((err as ApiError).message).toContain('título');
    }
  });
});
