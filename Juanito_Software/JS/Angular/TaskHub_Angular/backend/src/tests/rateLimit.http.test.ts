import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../services/auth.service', () => ({
  authService: { register: vi.fn(), login: vi.fn(), refresh: vi.fn(), logout: vi.fn() },
}));

import { arrancar, peticion } from './http';

/**
 * El limite de intentos de login: 10 fallos cada 15 minutos por IP, y los
 * aciertos no gastan cuota (`skipSuccessfulRequests`).
 *
 * El contador vive en el propio modulo de rateLimit.ts, asi que dos tests que
 * compartieran aplicacion compartirian cuota y dependerian del orden. Cada test
 * importa una aplicacion nueva tras `vi.resetModules()`.
 */
async function aplicacionNueva() {
  vi.resetModules();
  const { createApp } = await import('../app');
  const { authService } = await import('../services/auth.service');
  const { ApiError } = await import('../utils/ApiError');
  const login = vi.mocked(authService.login);
  login.mockImplementation((async ({ password }: { password: string }) => {
    if (password !== 'buena') throw ApiError.unauthorized('Credenciales inválidas');
    return { user: { id: 'ana' }, accessToken: 'a', refreshToken: 'r' };
  }) as never);
  const api = await arrancar(createApp());
  const intentar = (password: string) =>
    peticion(api.url, 'POST', '/api/auth/login', { cuerpo: { email: 'ana@test.com', password } });
  return { api, login, intentar };
}

let cerrar: (() => Promise<void>) | undefined;
afterEach(async () => {
  await cerrar?.();
  cerrar = undefined;
});
beforeEach(() => vi.clearAllMocks());

describe('limite de intentos en /api/auth/login', () => {
  it('el undecimo fallo seguido recibe 429 y ni siquiera se comprueba la contraseña', async () => {
    const { api, login, intentar } = await aplicacionNueva();
    cerrar = api.cerrar;

    for (let i = 0; i < 10; i++) {
      expect((await intentar('mala')).status).toBe(401);
    }
    const bloqueado = await intentar('mala');

    expect(bloqueado.status).toBe(429);
    // El limitador corta ANTES de comprobar la contraseña. Si la comprobacion
    // se hiciera igualmente, el atacante seguiria probando contra la base de
    // datos —solo que sin ver el resultado— y cada intento seguiria costando un
    // bcrypt al servidor.
    expect(login).toHaveBeenCalledTimes(10);
  });

  it('bloqueado, tampoco entra quien pone la contraseña buena', async () => {
    const { api, intentar } = await aplicacionNueva();
    cerrar = api.cerrar;

    for (let i = 0; i < 10; i++) await intentar('mala');

    expect((await intentar('buena')).status).toBe(429);
  });

  it('los accesos correctos no gastan cuota', async () => {
    const { api, intentar } = await aplicacionNueva();
    cerrar = api.cerrar;

    // Un usuario que entra muchas veces al dia no debe acabar bloqueado.
    for (let i = 0; i < 15; i++) {
      expect((await intentar('buena')).status).toBe(200);
    }
    for (let i = 0; i < 9; i++) {
      expect((await intentar('mala')).status).toBe(401);
    }
    // Con 15 aciertos y 9 fallos, aun queda un intento.
    expect((await intentar('mala')).status).toBe(401);
  });
});
