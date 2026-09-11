import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from 'vitest';

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../repositories/project.repository', () => ({
  projectRepository: { create: vi.fn(), findManyForUser: vi.fn(), findById: vi.fn() },
}));
vi.mock('../repositories/user.repository', () => ({
  userRepository: { delete: vi.fn(), findById: vi.fn(), findByEmail: vi.fn() },
}));
// El servicio de autenticacion se sustituye entero: lo que se prueba aqui es lo
// que hace el CONTROLADOR con su resultado —la cookie—, y el servicio ya tiene
// sus propios tests en auth.service.test.ts.
vi.mock('../services/auth.service', () => ({
  authService: { register: vi.fn(), login: vi.fn(), refresh: vi.fn(), logout: vi.fn() },
}));

import { projectRepository } from '../repositories/project.repository';
import { userRepository } from '../repositories/user.repository';
import { authService } from '../services/auth.service';
import { ApiError } from '../utils/ApiError';
import { arrancar, peticion, tokenDe, usuarioCrudo } from './http';

const proyectos = vi.mocked(projectRepository);
const usuarios = vi.mocked(userRepository);
const auth = vi.mocked(authService);

let api: Awaited<ReturnType<typeof arrancar>>;
beforeAll(async () => (api = await arrancar()));
afterAll(() => api.cerrar());

beforeEach(() => {
  vi.clearAllMocks();
  proyectos.findManyForUser.mockResolvedValue([] as never);
  proyectos.create.mockResolvedValue({ id: 'p1', name: 'Informe', members: [] } as never);
  usuarios.delete.mockResolvedValue(usuarioCrudo('u2') as never);
});

/** Un JWT cualquiera con la cabecera `alg: none` y sin firma. */
function tokenSinFirma(sub: string) {
  const b64 = (o: object) => Buffer.from(JSON.stringify(o)).toString('base64url');
  return `${b64({ alg: 'none', typ: 'JWT' })}.${b64({ sub, email: `${sub}@test.com`, role: 'ADMIN' })}.`;
}

/** Token valido de `ana` con el payload cambiado a `bob` y la firma original. */
function tokenManipulado() {
  const [cabecera, , firma] = tokenDe('ana').split('.');
  const payload = Buffer.from(JSON.stringify({ sub: 'bob', email: 'bob@test.com', role: 'ADMIN' })).toString('base64url');
  return `${cabecera}.${payload}.${firma}`;
}

describe('authenticate: quien eres lo dice el token, y solo si es bueno', () => {
  it('con un token valido, la identidad sale del token', async () => {
    const res = await peticion(api.url, 'GET', '/api/projects', { token: tokenDe('ana') });

    expect(res.status).toBe(200);
    expect(proyectos.findManyForUser).toHaveBeenCalledWith('ana', expect.anything());
  });

  it.each([
    ['sin cabecera', {}],
    ['con esquema Basic', { Authorization: 'Basic YW5hOnNlY3JldG8=' }],
    ['con «Bearer» y nada detras', { Authorization: 'Bearer ' }],
    ['firmado con otro secreto', { Authorization: `Bearer ${tokenDe('ana', { secreto: 'otro-secreto' })}` }],
    ['caducado', { Authorization: `Bearer ${tokenDe('ana', { expiresIn: -10 })}` }],
    // `alg: none` es el ataque clasico contra JWT: un token sin firma que una
    // libreria mal configurada acepta. jsonwebtoken lo rechaza cuando se le da
    // un secreto; este test fija que siga siendo asi.
    ['sin firma (alg: none)', { Authorization: `Bearer ${tokenSinFirma('ana')}` }],
    ['con el payload cambiado y la firma original', { Authorization: `Bearer ${tokenManipulado()}` }],
  ])('%s: 401 y la peticion no llega al repositorio', async (_caso, cabeceras) => {
    const res = await peticion(api.url, 'GET', '/api/projects', { cabeceras: cabeceras as Record<string, string> });

    expect(res.status).toBe(401);
    expect(proyectos.findManyForUser).not.toHaveBeenCalled();
  });

  it('un propietario enviado en el cuerpo se ignora: manda el del token', async () => {
    const res = await peticion(api.url, 'POST', '/api/projects', {
      token: tokenDe('ana'),
      cuerpo: { name: 'Informe', ownerId: 'bob' },
    });

    expect(res.status).toBe(201);
    const datos = proyectos.create.mock.calls[0][0] as { owner: unknown };
    expect(datos.owner).toEqual({ connect: { id: 'ana' } });
  });
});

describe('authorize(ADMIN): borrar usuarios', () => {
  it('un MEMBER recibe 403 y no se borra nadie', async () => {
    const res = await peticion(api.url, 'DELETE', '/api/users/u2', { token: tokenDe('ana', { role: 'MEMBER' }) });

    expect(res.status).toBe(403);
    expect(usuarios.delete).not.toHaveBeenCalled();
  });

  it('un MANAGER tampoco', async () => {
    const res = await peticion(api.url, 'DELETE', '/api/users/u2', { token: tokenDe('ana', { role: 'MANAGER' }) });

    expect(res.status).toBe(403);
    expect(usuarios.delete).not.toHaveBeenCalled();
  });

  it('un ADMIN si, y se borra exactamente ese usuario', async () => {
    const res = await peticion(api.url, 'DELETE', '/api/users/u2', { token: tokenDe('root', { role: 'ADMIN' }) });

    expect(res.status).toBe(204);
    expect(usuarios.delete).toHaveBeenCalledWith('u2');
  });

  it('el rol ADMIN no se puede fabricar: un token manipulado no pasa de 401', async () => {
    // tokenManipulado() dice role: ADMIN. Si la firma no se comprobara, este
    // borrado saldria adelante.
    const res = await peticion(api.url, 'DELETE', '/api/users/u2', { cabeceras: { Authorization: `Bearer ${tokenManipulado()}` } });

    expect(res.status).toBe(401);
    expect(usuarios.delete).not.toHaveBeenCalled();
  });
});

/**
 * La proteccion frente a CSRF de las dos rutas que se autentican con cookie
 * (/refresh y /logout) esta en los atributos de la cookie, no en un middleware.
 * Lo dice un comentario en app.ts y otro en auth.controller.ts. Estos tests son
 * lo que impide que un cambio de opciones la desmonte sin que nadie lo note.
 */
describe('la cookie del refresh token', () => {
  const SESION = { user: { id: 'ana' }, accessToken: 'acceso-123', refreshToken: 'refresco-456' };

  function cookieDe(res: Response) {
    return res.headers.getSetCookie().find((c) => c.startsWith('refreshToken=')) ?? '';
  }

  it('al iniciar sesion viaja en cookie HttpOnly, SameSite=Strict y limitada a /api/auth', async () => {
    auth.login.mockResolvedValue(SESION as never);

    const res = await peticion(api.url, 'POST', '/api/auth/login', { cuerpo: { email: 'ana@test.com', password: 'x' } });

    expect(res.status).toBe(200);
    const cookie = cookieDe(res);
    expect(cookie).toContain('refreshToken=refresco-456');
    expect(cookie).toContain('HttpOnly');
    expect(cookie).toContain('SameSite=Strict');
    expect(cookie).toContain('Path=/api/auth');
  });

  it('y NO viaja en el cuerpo, donde el JavaScript de la pagina podria leerlo', async () => {
    auth.login.mockResolvedValue(SESION as never);

    const res = await peticion(api.url, 'POST', '/api/auth/login', { cuerpo: { email: 'ana@test.com', password: 'x' } });

    const texto = await res.text();
    expect(texto).toContain('acceso-123');
    expect(texto).not.toContain('refresco-456');
  });

  it('renovar sin cookie: 401 sin llegar a consultar', async () => {
    const res = await peticion(api.url, 'POST', '/api/auth/refresh');

    expect(res.status).toBe(401);
    expect(auth.refresh).not.toHaveBeenCalled();
  });

  it('renovar con una cookie que ya no vale: 401 y la cookie se borra', async () => {
    auth.refresh.mockRejectedValue(ApiError.unauthorized('Refresh token inválido o expirado'));

    const res = await peticion(api.url, 'POST', '/api/auth/refresh', { cabeceras: { Cookie: 'refreshToken=caducado' } });

    expect(res.status).toBe(401);
    // Sin el borrado, el navegador seguiria mandando la cookie muerta en cada
    // intento y la SPA reintentaria la renovacion en bucle.
    const cookie = cookieDe(res);
    expect(cookie).toMatch(/^refreshToken=;/);
    expect(cookie).toContain('Expires=Thu, 01 Jan 1970');
    expect(cookie).toContain('Path=/api/auth');
  });

  it('cerrar sesion revoca ESE token en el servidor y borra la cookie', async () => {
    const res = await peticion(api.url, 'POST', '/api/auth/logout', { cabeceras: { Cookie: 'refreshToken=refresco-456' } });

    expect(res.status).toBe(204);
    // Borrar solo la cookie dejaria el token vivo en la base de datos: quien lo
    // hubiera copiado podria seguir renovando sesiones.
    expect(auth.logout).toHaveBeenCalledWith('refresco-456');
    expect(cookieDe(res)).toContain('Expires=Thu, 01 Jan 1970');
  });
});
