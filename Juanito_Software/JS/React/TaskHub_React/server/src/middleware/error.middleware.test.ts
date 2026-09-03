import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
// Solo para tipar el it.each de abajo; la clase que se usa en cada test es la
// que devuelve cargarManejador, no esta.
import type { ApiError as ApiErrorTipo } from '../utils/api-error.js';

/**
 * El único sitio de la aplicación que escribe el cuerpo de una respuesta de
 * error.
 *
 * Aquí se decide qué ve el mundo cuando algo falla, y **es lo que impide que un
 * mensaje de PostgreSQL salga por la API en producción**. Que no tuviera ni un
 * test era el hueco más incómodo de la auditoría: la protección existía pero
 * nadie la vigilaba, así que quitar el `isProduction` habría pasado inadvertido.
 *
 * `isProduction` se congela al importar el módulo de configuración, así que
 * cada bloque reimporta con el entorno ya puesto. De ahí `vi.resetModules()` y
 * los imports dinámicos.
 */

/** Response simulado que se queda con lo que le escriben. */
function respuestaFalsa() {
  const capturado = { status: 0, cuerpo: null as unknown };
  const res = {
    status(codigo: number) {
      capturado.status = codigo;
      return this;
    },
    json(cuerpo: unknown) {
      capturado.cuerpo = cuerpo;
      return this;
    },
  } as unknown as Response;
  return { res, capturado };
}

const req = {} as Request;
const next = (() => {}) as NextFunction;

/**
 * Carga el manejador con NODE_ENV puesto al valor que se quiera, **y con él la
 * clase ApiError del mismo registro de módulos**.
 *
 * Lo segundo no es un detalle: `vi.resetModules()` crea un registro nuevo, así
 * que un `ApiError` importado estáticamente arriba sería una clase DISTINTA de
 * la que ve el middleware recién cargado, y el `instanceof` de dentro fallaría.
 * El primer intento de este archivo cayó justo ahí: nueve tests en rojo
 * afirmando que un 404 devolvía 500. El código estaba bien; el test comparaba
 * dos clases homónimas.
 */
async function cargarManejador(entorno: string) {
  vi.resetModules();
  process.env.NODE_ENV = entorno;
  const [{ errorHandler }, { ApiError }] = await Promise.all([
    import('./error.middleware.js'),
    import('../utils/api-error.js'),
  ]);
  return { errorHandler, ApiError };
}

const entornoOriginal = process.env.NODE_ENV;

beforeEach(() => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
});

afterEach(() => {
  process.env.NODE_ENV = entornoOriginal;
  vi.restoreAllMocks();
  vi.resetModules();
});

describe('errores del dominio (ApiError)', () => {
  it('responde con el código que trae el error', async () => {
    const { errorHandler, ApiError } = await cargarManejador('development');
    const { res, capturado } = respuestaFalsa();

    errorHandler(ApiError.notFound('Tarea no encontrada'), req, res, next);

    expect(capturado.status).toBe(404);
  });

  it('conserva el mensaje: es información para el usuario, no un fallo interno', async () => {
    const { errorHandler, ApiError } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    errorHandler(ApiError.conflict('Ya tienes una tarea con este título'), req, res, next);

    // Incluso en producción, porque lo escribió la aplicación a propósito.
    expect(capturado.cuerpo).toMatchObject({
      success: false,
      error: 'Ya tienes una tarea con este título',
    });
  });

  it('incluye los detalles de validación cuando los hay', async () => {
    const { errorHandler, ApiError } = await cargarManejador('development');
    const { res, capturado } = respuestaFalsa();

    errorHandler(ApiError.badRequest('Error de validación', ['falta título']), req, res, next);

    expect(capturado.cuerpo).toMatchObject({ details: ['falta título'] });
  });

  it.each([
    ['400', (E: typeof ApiErrorTipo) => E.badRequest('x'), 400],
    ['401', (E: typeof ApiErrorTipo) => E.unauthorized(), 401],
    ['403', (E: typeof ApiErrorTipo) => E.forbidden(), 403],
    ['404', (E: typeof ApiErrorTipo) => E.notFound(), 404],
    ['409', (E: typeof ApiErrorTipo) => E.conflict('x'), 409],
  ])('traslada el %s tal cual', async (_caso, construir, esperado) => {
    const { errorHandler, ApiError } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    errorHandler(construir(ApiError), req, res, next);

    expect(capturado.status).toBe(esperado);
  });

  it('no registra los errores del dominio como fallos inesperados', async () => {
    // Un 404 es funcionamiento normal. Si acabara en console.error, el registro
    // de errores estaría lleno de ruido y los fallos de verdad no se verían.
    const { errorHandler, ApiError } = await cargarManejador('production');
    const { res } = respuestaFalsa();

    errorHandler(ApiError.notFound(), req, res, next);

    expect(console.error).not.toHaveBeenCalled();
  });
});

describe('errores inesperados en PRODUCCIÓN', () => {
  it('un error de PostgreSQL NO llega al cliente', async () => {
    // El caso concreto que motiva este bloque: antes de validar los
    // identificadores, un UUID mal formado producía este error exacto.
    const { errorHandler } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    const errorDeBd = Object.assign(
      new Error('invalid input syntax for type uuid: "no-soy-un-uuid"'),
      { code: '22P02' },
    );

    errorHandler(errorDeBd, req, res, next);

    expect(capturado.status).toBe(500);
    expect(JSON.stringify(capturado.cuerpo)).not.toContain('uuid');
    expect(JSON.stringify(capturado.cuerpo)).not.toContain('22P02');
    expect(capturado.cuerpo).toMatchObject({ error: 'Error interno del servidor' });
  });

  it('tampoco llega el detalle de una violación de clave foránea', async () => {
    const { errorHandler } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    errorHandler(
      new Error('insert or update on table "tasks" violates foreign key constraint'),
      req,
      res,
      next,
    );

    expect(JSON.stringify(capturado.cuerpo)).not.toMatch(/tasks|foreign key|constraint/i);
  });

  it('no filtra rutas del sistema de ficheros', async () => {
    const { errorHandler } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    errorHandler(new Error("ENOENT: no such file '/app/server/src/config/db.ts'"), req, res, next);

    expect(JSON.stringify(capturado.cuerpo)).not.toContain('/app/server');
  });

  it('nunca devuelve la traza de pila', async () => {
    const { errorHandler } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    errorHandler(new Error('lo que sea'), req, res, next);

    expect(JSON.stringify(capturado.cuerpo)).not.toContain('at ');
  });

  it('sí lo registra en el servidor: se oculta al cliente, no al operador', async () => {
    const { errorHandler } = await cargarManejador('production');
    const { res } = respuestaFalsa();

    errorHandler(new Error('algo se rompió'), req, res, next);

    expect(console.error).toHaveBeenCalled();
  });
});

describe('errores inesperados en DESARROLLO', () => {
  it('sí muestra el mensaje real, que es lo que hace falta al depurar', async () => {
    const { errorHandler } = await cargarManejador('development');
    const { res, capturado } = respuestaFalsa();

    errorHandler(new Error('invalid input syntax for type uuid'), req, res, next);

    expect(capturado.status).toBe(500);
    expect(capturado.cuerpo).toMatchObject({ error: 'invalid input syntax for type uuid' });
  });

  it('la diferencia entre entornos existe de verdad', async () => {
    // El test que fija la razón de ser del `isProduction`: mismo error, dos
    // respuestas distintas. Si alguien quitara la condición, este falla.
    const mismoError = new Error('detalle interno que no debe salir fuera');

    const enDesarrollo = respuestaFalsa();
    (await cargarManejador('development')).errorHandler(mismoError, req, enDesarrollo.res, next);

    const enProduccion = respuestaFalsa();
    (await cargarManejador('production')).errorHandler(mismoError, req, enProduccion.res, next);

    expect(JSON.stringify(enDesarrollo.capturado.cuerpo)).toContain('detalle interno');
    expect(JSON.stringify(enProduccion.capturado.cuerpo)).not.toContain('detalle interno');
  });
});

describe('valores que no son un Error', () => {
  it.each([
    ['una cadena', 'me han lanzado texto'],
    ['un número', 42],
    ['null', null],
    ['undefined', undefined],
    ['un objeto suelto', { algo: 'raro' }],
  ])('%s acaba en 500 sin romper el manejador', async (_caso, valor) => {
    // `throw 'texto'` es legal en JavaScript y una librería de terceros puede
    // hacerlo. El manejador no puede reventar al recibirlo.
    const { errorHandler } = await cargarManejador('production');
    const { res, capturado } = respuestaFalsa();

    expect(() => errorHandler(valor, req, res, next)).not.toThrow();
    expect(capturado.status).toBe(500);
    expect(capturado.cuerpo).toMatchObject({ success: false });
  });

  it('en desarrollo, lo que no es Error también sale como mensaje genérico', async () => {
    const { errorHandler } = await cargarManejador('development');
    const { res, capturado } = respuestaFalsa();

    errorHandler('me han lanzado texto', req, res, next);

    expect(capturado.cuerpo).toMatchObject({ error: 'Error interno del servidor' });
  });
});
