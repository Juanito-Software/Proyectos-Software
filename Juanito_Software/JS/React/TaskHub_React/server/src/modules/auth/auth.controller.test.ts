import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
import { authController } from './auth.controller.js';
import { authService } from './auth.service.js';
import { REFRESH_COOKIE } from './auth.cookie.js';
import { ApiError } from '../../utils/api-error.js';

/**
 * El controlador de autenticación.
 *
 * Parece un envoltorio fino sobre el servicio, pero guarda **la invariante que
 * sostiene todo el diseño de la cookie**: el token de refresco sale por
 * `Set-Cookie` y **nunca** en el cuerpo de la respuesta. Si apareciera en el
 * JSON, el JavaScript de la página podría leerlo y el `HttpOnly` no habría
 * servido de nada — que es exactamente el ataque del que protege.
 *
 * Hasta ahora esa invariante solo la vigilaba la suite de API, y allí en un
 * único punto. Aquí se comprueba en las tres rutas que emiten credenciales.
 */

const CREDENCIALES = {
  user: { id: 'user-1', username: 'juan', role: 'user' as const },
  accessToken: 'jwt-de-acceso',
  refreshToken: 'REFRESCO-QUE-NO-DEBE-SALIR-EN-EL-CUERPO',
};

/** Response simulado que registra estado, cuerpo y cookies. */
function respuestaFalsa() {
  const capturado = {
    status: 200,
    cuerpo: null as unknown,
    cookiePuesta: null as { nombre: string; valor: string } | null,
    cookieBorrada: null as string | null,
  };
  const res = {
    status(codigo: number) {
      capturado.status = codigo;
      return this;
    },
    json(cuerpo: unknown) {
      capturado.cuerpo = cuerpo;
      return this;
    },
    cookie(nombre: string, valor: string) {
      capturado.cookiePuesta = { nombre, valor };
      return this;
    },
    clearCookie(nombre: string) {
      capturado.cookieBorrada = nombre;
      return this;
    },
  } as unknown as Response;
  return { res, capturado };
}

const peticion = (extra: Partial<Request> = {}) =>
  ({ headers: {}, body: {}, ...extra }) as unknown as Request;

/** Ejecuta un método del controlador y devuelve lo escrito y lo pasado a next(). */
async function ejecutar(
  metodo: (r: Request, s: Response, n: NextFunction) => Promise<void>,
  req: Request = peticion(),
) {
  const { res, capturado } = respuestaFalsa();
  let error: unknown;
  await metodo(req, res, ((err?: unknown) => {
    error = err;
  }) as NextFunction);
  return { capturado, error };
}

let espias: Record<string, ReturnType<typeof vi.spyOn>>;

beforeEach(() => {
  espias = {
    register: vi.spyOn(authService, 'register').mockResolvedValue(CREDENCIALES),
    login: vi.spyOn(authService, 'login').mockResolvedValue(CREDENCIALES),
    refresh: vi.spyOn(authService, 'refresh').mockResolvedValue(CREDENCIALES),
    logout: vi.spyOn(authService, 'logout').mockResolvedValue(undefined),
    logoutAll: vi.spyOn(authService, 'logoutAll').mockResolvedValue(3),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('el refresco NUNCA sale en el cuerpo', () => {
  it.each([
    ['register', () => ejecutar(authController.register)],
    ['login', () => ejecutar(authController.login)],
    ['refresh', () => ejecutar(authController.refresh)],
  ])('%s: el cuerpo no contiene el token de refresco', async (_ruta, accion) => {
    const { capturado } = await accion();

    expect(JSON.stringify(capturado.cuerpo)).not.toContain(CREDENCIALES.refreshToken);
    expect(JSON.stringify(capturado.cuerpo)).not.toContain('refreshToken');
  });

  it.each([
    ['register', () => ejecutar(authController.register)],
    ['login', () => ejecutar(authController.login)],
    ['refresh', () => ejecutar(authController.refresh)],
  ])('%s: sí lo manda por cookie', async (_ruta, accion) => {
    const { capturado } = await accion();

    expect(capturado.cookiePuesta).toEqual({
      nombre: REFRESH_COOKIE,
      valor: CREDENCIALES.refreshToken,
    });
  });

  it('el token de ACCESO sí va en el cuerpo: el cliente lo necesita', async () => {
    // Tiene que ponerlo en la cabecera Authorization de cada petición, así que
    // el JavaScript de la página sí debe poder leerlo.
    const { capturado } = await ejecutar(authController.login);

    expect(JSON.stringify(capturado.cuerpo)).toContain('jwt-de-acceso');
  });

  it('el usuario también, para pintar la cabecera', async () => {
    const { capturado } = await ejecutar(authController.login);

    expect(capturado.cuerpo).toMatchObject({ data: { user: { username: 'juan' } } });
  });
});

describe('códigos de estado', () => {
  it('el registro responde 201: ha creado algo', async () => {
    const { capturado } = await ejecutar(authController.register);
    expect(capturado.status).toBe(201);
  });

  it('el login responde 200: no crea nada nuevo', async () => {
    const { capturado } = await ejecutar(authController.login);
    expect(capturado.status).toBe(200);
  });

  it('la renovación responde 200', async () => {
    const { capturado } = await ejecutar(authController.refresh);
    expect(capturado.status).toBe(200);
  });
});

describe('renovación', () => {
  it('saca el token de la cookie, no del cuerpo', async () => {
    // Si lo leyera del cuerpo, el cliente tendría que poder escribirlo, y para
    // eso el JavaScript necesitaría leerlo primero.
    await ejecutar(
      authController.refresh,
      peticion({ headers: { cookie: `${REFRESH_COOKIE}=el-de-la-cookie` } }),
    );

    expect(espias.refresh).toHaveBeenCalledWith('el-de-la-cookie');
  });

  it('si falla, borra la cookie para que el cliente deje de reintentar', async () => {
    espias.refresh.mockRejectedValue(ApiError.unauthorized('Sesión inválida o expirada'));

    const { capturado, error } = await ejecutar(authController.refresh);

    expect(capturado.cookieBorrada).toBe(REFRESH_COOKIE);
    expect((error as ApiError).statusCode).toBe(401);
  });

  it('sin cookie, se lo pasa igualmente al servicio para que decida', async () => {
    await ejecutar(authController.refresh, peticion());
    expect(espias.refresh).toHaveBeenCalledWith(undefined);
  });
});

describe('cierre de sesión', () => {
  it('responde 200 aunque no hubiera sesión', async () => {
    // Distinguir "había sesión" de "no la había" solo serviría para que
    // alguien sondeara tokens ajenos.
    const { capturado, error } = await ejecutar(authController.logout, peticion());

    expect(capturado.status).toBe(200);
    expect(error).toBeUndefined();
  });

  it('borra la cookie del navegador', async () => {
    const { capturado } = await ejecutar(authController.logout);
    expect(capturado.cookieBorrada).toBe(REFRESH_COOKIE);
  });

  it('el cierre global saca el usuario del TOKEN, nunca del cuerpo', async () => {
    // Si viniera del cuerpo, cualquiera podría cerrar las sesiones de otro.
    await ejecutar(
      authController.logoutAll,
      peticion({ userId: 'user-9', body: { userId: 'victima' } }),
    );

    expect(espias.logoutAll).toHaveBeenCalledWith('user-9');
  });

  it('el cierre global informa de cuántas sesiones cayeron', async () => {
    const { capturado } = await ejecutar(authController.logoutAll, peticion({ userId: 'u' }));

    expect(capturado.cuerpo).toMatchObject({ data: { revocadas: 3 } });
  });
});

describe('propagación de errores', () => {
  it.each([
    ['register', 'register', () => ejecutar(authController.register)],
    ['login', 'login', () => ejecutar(authController.login)],
    ['logout', 'logout', () => ejecutar(authController.logout)],
  ])('%s pasa el fallo a next() en lugar de tragárselo', async (_r, metodo, accion) => {
    espias[metodo].mockRejectedValue(ApiError.conflict('El usuario ya existe'));

    const { error } = await accion();

    expect((error as ApiError).statusCode).toBe(409);
  });

  it('un error no escribe cuerpo: de eso se encarga el manejador de errores', async () => {
    espias.login.mockRejectedValue(ApiError.unauthorized());

    const { capturado } = await ejecutar(authController.login);

    expect(capturado.cuerpo).toBeNull();
  });
});
