import { describe, it, expect, vi, afterEach } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
import { authMiddleware } from './auth.middleware.js';
import { requireAdmin } from './admin.middleware.js';
import { tokenService } from '../modules/auth/token.service.js';
import { usersRepository } from '../modules/users/users.repository.js';
import { ApiError } from '../utils/api-error.js';

/**
 * Los dos guardias de la API: identificar y autorizar.
 *
 * La distinción entre ambos es lo que separa un **401** («no sé quién eres») de
 * un **403** («sé quién eres y no puedes»), y el cliente actúa distinto en cada
 * caso: con el primero borra la sesión y vuelve al formulario, con el segundo
 * no. Confundirlos echaría a un usuario normal de la aplicación cada vez que
 * tocara sin querer una ruta de administración.
 */

const USUARIO = {
  id: 'user-1',
  username: 'juan',
  role: 'user' as const,
  passwordHash: '$2b$12$hash',
  createdAt: '2026-01-01T00:00:00.000Z',
};
const ADMIN = { ...USUARIO, id: 'admin-1', username: 'jefe', role: 'admin' as const };

/** Petición simulada con la cabecera que se quiera. */
const peticion = (authorization?: string, extra: Partial<Request> = {}) =>
  ({ headers: authorization ? { authorization } : {}, ...extra }) as unknown as Request;

const res = {} as Response;

/** Ejecuta un middleware y devuelve lo que le pasó a next(). */
async function ejecutar(
  middleware: (r: Request, s: Response, n: NextFunction) => void | Promise<void>,
  req: Request,
): Promise<{ error: unknown; req: Request }> {
  let error: unknown;
  await middleware(req, res, ((err?: unknown) => {
    error = err;
  }) as NextFunction);
  return { error, req };
}

const tokenValido = () =>
  tokenService.generateAccessToken({ userId: USUARIO.id, username: USUARIO.username });

afterEach(() => {
  vi.restoreAllMocks();
});

describe('authMiddleware: lectura de la cabecera', () => {
  it('acepta un token válido y deja el usuario en la petición', async () => {
    const { error, req } = await ejecutar(authMiddleware, peticion(`Bearer ${tokenValido()}`));

    expect(error).toBeUndefined();
    expect(req.userId).toBe(USUARIO.id);
    expect(req.username).toBe('juan');
  });

  it.each([
    ['sin cabecera', undefined],
    ['cabecera vacía', ''],
    ['solo la palabra Bearer', 'Bearer'],
    ['Bearer con espacio y nada más', 'Bearer '],
    ['sin el prefijo Bearer', 'un-token-suelto'],
    ['con otro esquema', 'Basic dXNlcjpwYXNz'],
    ['con el prefijo en minúsculas', 'bearer algo'],
  ])('rechaza con 401: %s', async (_caso, cabecera) => {
    const { error } = await ejecutar(authMiddleware, peticion(cabecera));

    expect((error as ApiError).statusCode).toBe(401);
  });

  it('el prefijo distingue mayúsculas a propósito', async () => {
    // La especificación de HTTP dice que el esquema no las distingue, pero
    // aceptar solo la forma canónica evita ambigüedades y ningún cliente
    // legítimo manda otra cosa. Queda anotado por si algún día molesta.
    const { error } = await ejecutar(authMiddleware, peticion(`bearer ${tokenValido()}`));
    expect(error).toBeDefined();
  });

  it.each([
    ['malformado', 'esto-no-es-un-jwt'],
    ['con solo dos partes', 'aaa.bbb'],
    ['vacío tras el prefijo', ' '],
  ])('rechaza un token %s', async (_caso, token) => {
    const { error } = await ejecutar(authMiddleware, peticion(`Bearer ${token}`));

    expect((error as ApiError).statusCode).toBe(401);
  });

  it('el mensaje de rechazo no dice POR QUÉ falló el token', async () => {
    // Distinguir "caducado" de "firma inválida" en la respuesta le diría a un
    // atacante si acertó con la firma. El detalle va al registro, no al cliente.
    const { error } = await ejecutar(authMiddleware, peticion('Bearer aaa.bbb.ccc'));

    expect((error as ApiError).message).not.toMatch(/firma|caducado|expired|signature/i);
  });

  it('no consulta la base de datos: es la decisión que lo hace barato', async () => {
    // Documentado en el propio middleware. La contrapartida es la ventana de
    // quince minutos de un usuario borrado, y está asumida.
    const findById = vi.spyOn(usersRepository, 'findById');

    await ejecutar(authMiddleware, peticion(`Bearer ${tokenValido()}`));

    expect(findById).not.toHaveBeenCalled();
  });
});

describe('requireAdmin: autorización', () => {
  it('deja pasar a un administrador', async () => {
    vi.spyOn(usersRepository, 'findById').mockResolvedValue(ADMIN);

    const { error } = await ejecutar(requireAdmin, peticion(undefined, { userId: ADMIN.id }));

    expect(error).toBeUndefined();
  });

  it('a un usuario normal le da 403, no 401', async () => {
    // 403 y no 401 porque quien pregunta ya está autenticado: echarle la sesión
    // por tocar una ruta de administración sería desproporcionado.
    vi.spyOn(usersRepository, 'findById').mockResolvedValue(USUARIO);
    vi.spyOn(console, 'warn').mockImplementation(() => {});

    const { error } = await ejecutar(requireAdmin, peticion(undefined, { userId: USUARIO.id }));

    expect((error as ApiError).statusCode).toBe(403);
  });

  it('si la cuenta ya no existe da 401: la sesión sí está muerta', async () => {
    vi.spyOn(usersRepository, 'findById').mockResolvedValue(null);

    const { error } = await ejecutar(requireAdmin, peticion(undefined, { userId: 'fantasma' }));

    expect((error as ApiError).statusCode).toBe(401);
    expect((error as ApiError).message).toMatch(/ya no existe/i);
  });

  it('lee el rol de la BASE DE DATOS, no del token', async () => {
    // Si viniera del JWT, quitarle el rol a alguien no tendría efecto hasta que
    // su token caducara. Cuesta una consulta y compra revocación inmediata.
    const findById = vi.spyOn(usersRepository, 'findById').mockResolvedValue(ADMIN);

    await ejecutar(requireAdmin, peticion(undefined, { userId: ADMIN.id }));

    expect(findById).toHaveBeenCalledWith(ADMIN.id);
  });

  it('registra la denegación con la ruta', async () => {
    // Una vez puede ser un enlace guardado; repetido es otra cosa, y sin
    // registro no hay forma de distinguirlas.
    vi.spyOn(usersRepository, 'findById').mockResolvedValue(USUARIO);
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    await ejecutar(
      requireAdmin,
      peticion(undefined, { userId: USUARIO.id, originalUrl: '/api/admin/users' }),
    );

    const registro = JSON.parse(String(warn.mock.calls[0][0]));
    expect(registro.evento).toBe('autorizacion.denegada');
    expect(registro.ruta).toBe('/api/admin/users');
    expect(registro.usuario).toBe('juan');
  });

  it('un fallo de la base de datos se propaga, no se traga', async () => {
    // Tragárselo dejaría pasar la petición: un error de conexión no puede
    // convertirse en un permiso concedido.
    vi.spyOn(usersRepository, 'findById').mockRejectedValue(new Error('conexión perdida'));

    const { error } = await ejecutar(requireAdmin, peticion(undefined, { userId: 'x' }));

    expect((error as Error).message).toBe('conexión perdida');
  });
});

describe('los dos guardias juntos', () => {
  it('sin token, requireAdmin nunca llega a ejecutarse', async () => {
    // El orden del router importa: primero identificar, después autorizar. Por
    // eso una ruta de administración sin token responde 401 y no 403.
    const { error } = await ejecutar(authMiddleware, peticion(undefined));

    expect((error as ApiError).statusCode).toBe(401);
  });

  it('401 y 403 no se confunden en el recorrido completo', async () => {
    vi.spyOn(usersRepository, 'findById').mockResolvedValue(USUARIO);
    vi.spyOn(console, 'warn').mockImplementation(() => {});

    const sinToken = await ejecutar(authMiddleware, peticion(undefined));
    const conTokenNormal = await ejecutar(
      requireAdmin,
      peticion(undefined, { userId: USUARIO.id }),
    );

    expect((sinToken.error as ApiError).statusCode).toBe(401);
    expect((conTokenNormal.error as ApiError).statusCode).toBe(403);
  });
});
