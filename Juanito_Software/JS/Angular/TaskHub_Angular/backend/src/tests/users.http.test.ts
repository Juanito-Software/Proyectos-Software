import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from 'vitest';
import bcrypt from 'bcrypt';

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../repositories/user.repository', () => ({
  userRepository: { findById: vi.fn(), findMany: vi.fn(), count: vi.fn(), update: vi.fn(), delete: vi.fn() },
}));

import { userRepository } from '../repositories/user.repository';
import { arrancar, peticion, tokenDe, usuarioCrudo } from './http';

const usuarios = vi.mocked(userRepository);

// Coste 4 para que el test no tarde: bcrypt.compare acepta cualquier coste.
const HASH_ACTUAL = bcrypt.hashSync('Actual123', 4);

let api: Awaited<ReturnType<typeof arrancar>>;
beforeAll(async () => (api = await arrancar()));
afterAll(() => api.cerrar());

beforeEach(() => {
  vi.clearAllMocks();
  usuarios.findById.mockImplementation((async (id: string) => ({ ...usuarioCrudo(id), password: HASH_ACTUAL })) as never);
  usuarios.findMany.mockResolvedValue([usuarioCrudo('ana'), usuarioCrudo('bob')] as never);
  usuarios.count.mockResolvedValue(2 as never);
  usuarios.update.mockImplementation((async (id: string, datos: object) => ({ ...usuarioCrudo(id), ...datos })) as never);
});

/**
 * Las rutas de /api/users: el directorio de usuarios y lo que cada uno puede
 * cambiar de si mismo. Lo que se vigila es lo que sale (nunca la contraseña) y
 * lo que llega a la base de datos (nunca mas de lo que el esquema permite, y
 * siempre sobre el usuario del token).
 */
describe('lo que sale: el hash de la contraseña nunca', () => {
  it.each([
    ['el listado', '/api/users'],
    ['la ficha de un usuario', '/api/users/bob'],
  ])('%s no incluye el campo password', async (_que, ruta) => {
    const res = await peticion(api.url, 'GET', ruta, { token: tokenDe('ana') });

    expect(res.status).toBe(200);
    const texto = await res.text();
    expect(texto).not.toContain('password');
    expect(texto).not.toContain('NO-DEBE-SALIR');
  });
});

describe('PATCH /api/users/me/profile', () => {
  it('actualiza al usuario del token, y un rol colado en el cuerpo no llega a la base de datos', async () => {
    const res = await peticion(api.url, 'PATCH', '/api/users/me/profile', {
      token: tokenDe('ana'),
      cuerpo: { name: 'Ana María', role: 'ADMIN', email: 'otra@test.com', id: 'bob' },
    });

    expect(res.status).toBe(200);
    // Si `validate` dejara pasar el cuerpo original, un MEMBER se haria ADMIN
    // con una peticion. Zod descarta las claves que el esquema no declara, y
    // eso es lo unico que lo impide: el servicio pasa el objeto tal cual.
    expect(usuarios.update).toHaveBeenCalledWith('ana', { name: 'Ana María' });
  });
});

describe('PATCH /api/users/me/password', () => {
  it('con la contraseña actual equivocada: 400 y no se cambia nada', async () => {
    const res = await peticion(api.url, 'PATCH', '/api/users/me/password', {
      token: tokenDe('ana'),
      cuerpo: { currentPassword: 'Otra1234', newPassword: 'Nueva1234' },
    });

    expect(res.status).toBe(400);
    expect(usuarios.update).not.toHaveBeenCalled();
  });

  it('con la actual correcta: guarda la nueva HASHEADA, y solo para el usuario del token', async () => {
    const res = await peticion(api.url, 'PATCH', '/api/users/me/password', {
      token: tokenDe('ana'),
      cuerpo: { currentPassword: 'Actual123', newPassword: 'Nueva1234' },
    });

    expect(res.status).toBe(204);
    expect(usuarios.findById).toHaveBeenCalledWith('ana');
    const [id, datos] = usuarios.update.mock.calls[0] as [string, { password: string }];
    expect(id).toBe('ana');
    expect(datos.password).not.toBe('Nueva1234');
    expect(await bcrypt.compare('Nueva1234', datos.password)).toBe(true);
  });

  it.each([
    ['corta', 'Ab1'],
    ['sin mayuscula', 'nueva1234'],
    ['sin numero', 'NuevaNueva'],
  ])('una contraseña nueva %s se rechaza con 400 antes de comprobar nada', async (_caso, nueva) => {
    const res = await peticion(api.url, 'PATCH', '/api/users/me/password', {
      token: tokenDe('ana'),
      cuerpo: { currentPassword: 'Actual123', newPassword: nueva },
    });

    expect(res.status).toBe(400);
    expect(usuarios.findById).not.toHaveBeenCalled();
    expect(usuarios.update).not.toHaveBeenCalled();
  });
});
