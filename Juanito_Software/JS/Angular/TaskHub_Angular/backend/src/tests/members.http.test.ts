import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from 'vitest';

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../repositories/project.repository', () => ({
  projectRepository: {
    create: vi.fn(),
    findManyForUser: vi.fn(),
    findById: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    addMember: vi.fn(),
    findMembership: vi.fn(),
  },
}));
vi.mock('../repositories/user.repository', () => ({
  userRepository: { findByEmail: vi.fn(), findById: vi.fn() },
}));

import { projectRepository } from '../repositories/project.repository';
import { userRepository } from '../repositories/user.repository';
import { arrancar, peticion, tokenDe, usuarioCrudo } from './http';

/**
 * Añadir miembros a un proyecto: POST /api/projects/:id/members { email, role }.
 *
 * Decisiones del 11 de septiembre de 2026, que estos tests fijan:
 *
 * - Se añade por EMAIL, no por id. La pantalla no lista a todos los usuarios
 *   registrados; el propietario escribe el email de quien quiere añadir.
 * - Solo se asignan EDITOR o VIEWER. OWNER queda reservado a quien creo el
 *   proyecto: `ownerId` es uno solo, y un segundo «OWNER» tendria los mismos
 *   permisos que un EDITOR con otro nombre.
 * - Solo el propietario añade gente (ya lo imponia `assertOwner`).
 *
 * Y dos fallos que habia antes y que la pantalla habria destapado el primer dia:
 * añadir a alguien que ya era miembro, o un usuario inexistente, llegaba al
 * cliente como 500 «Error interno del servidor». Eran errores de Prisma (clave
 * unica y clave foranea) que `errorHandler` no reconoce.
 */

const P1 = '11111111-1111-4111-8111-111111111111';

const PROYECTO = {
  id: P1,
  name: 'Informe',
  description: null,
  ownerId: 'ana',
  owner: usuarioCrudo('ana'),
  createdAt: new Date('2026-01-01'),
  updatedAt: new Date('2026-01-01'),
  members: [
    { id: 'm1', projectId: P1, userId: 'ana', role: 'OWNER', user: usuarioCrudo('ana') },
    { id: 'm2', projectId: P1, userId: 'eva', role: 'EDITOR', user: usuarioCrudo('eva') },
  ],
};

const proyectos = vi.mocked(projectRepository);
const usuarios = vi.mocked(userRepository);
const ruta = `/api/projects/${P1}/members`;

let api: Awaited<ReturnType<typeof arrancar>>;
beforeAll(async () => (api = await arrancar()));
afterAll(() => api.cerrar());

beforeEach(() => {
  vi.clearAllMocks();
  proyectos.findById.mockImplementation((async (id: string) => (id === P1 ? PROYECTO : null)) as never);
  usuarios.findByEmail.mockImplementation((async (email: string) =>
    ['ana@test.com', 'eva@test.com', 'bob@test.com'].includes(email) ? usuarioCrudo(email.split('@')[0]) : null) as never);
  proyectos.addMember.mockImplementation((async (projectId: string, userId: string, role: string) => ({
    id: 'm9',
    projectId,
    userId,
    role,
    joinedAt: new Date('2026-09-11'),
    user: usuarioCrudo(userId),
  })) as never);
});

describe('el propietario añade por email', () => {
  it('201: busca al usuario por su email y lo añade con el rol pedido', async () => {
    const res = await peticion(api.url, 'POST', ruta, {
      token: tokenDe('ana'),
      cuerpo: { email: '  bob@test.com ', role: 'EDITOR' },
    });

    expect(res.status).toBe(201);
    expect(usuarios.findByEmail).toHaveBeenCalledWith('bob@test.com');
    expect(proyectos.addMember).toHaveBeenCalledWith(P1, 'bob', 'EDITOR');
  });

  it('sin rol, entra como VIEWER: el minimo privilegio', async () => {
    await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo: { email: 'bob@test.com' } });

    expect(proyectos.addMember).toHaveBeenCalledWith(P1, 'bob', 'VIEWER');
  });

  it('la respuesta trae al usuario para pintarlo, pero sin su contraseña', async () => {
    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo: { email: 'bob@test.com' } });

    const texto = await res.text();
    expect(JSON.parse(texto).user).toMatchObject({ id: 'bob', email: 'bob@test.com' });
    expect(texto).not.toContain('password');
    expect(texto).not.toContain('NO-DEBE-SALIR');
  });
});

describe('quien NO puede añadir', () => {
  it.each([
    ['un EDITOR del proyecto', 'eva'],
    ['alguien ajeno al proyecto', 'bob'],
  ])('%s recibe 403 y no se añade a nadie', async (_quien, usuario) => {
    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe(usuario), cuerpo: { email: 'bob@test.com' } });

    expect(res.status).toBe(403);
    expect(proyectos.addMember).not.toHaveBeenCalled();
  });
});

describe('lo que el propietario puede equivocar', () => {
  it('un email que no esta registrado: 404 con un mensaje que se puede enseñar', async () => {
    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo: { email: 'nadie@test.com' } });

    expect(res.status).toBe(404);
    expect((await res.json()).message).toBe('No existe ningún usuario con ese email');
    expect(proyectos.addMember).not.toHaveBeenCalled();
  });

  it.each([
    ['alguien que ya es miembro', 'eva@test.com'],
    ['el propio propietario', 'ana@test.com'],
  ])('%s: 409, no un 500, y no se intenta insertar', async (_caso, email) => {
    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo: { email } });

    expect(res.status).toBe(409);
    expect((await res.json()).message).toBe('Ese usuario ya es miembro del proyecto');
    expect(proyectos.addMember).not.toHaveBeenCalled();
  });

  it('el propietario sin fila de miembro tampoco se puede añadir a si mismo', async () => {
    // Un proyecto anterior a la regla que crea esa fila, o tocado a mano. Sin
    // mirar `ownerId`, el alta saldria bien y el propietario apareceria en la
    // lista como «Lector» de su propio proyecto.
    proyectos.findById.mockResolvedValue({ ...PROYECTO, members: PROYECTO.members.filter((x) => x.userId !== 'ana') } as never);

    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo: { email: 'ana@test.com' } });

    expect(res.status).toBe(409);
    expect(proyectos.addMember).not.toHaveBeenCalled();
  });

  it('si dos peticiones compiten y la base de datos rechaza el duplicado: 409, no 500', async () => {
    // La comprobacion previa no cubre dos altas simultaneas del mismo usuario:
    // la segunda llega a insertar y Prisma responde P2002 (clave unica).
    proyectos.addMember.mockRejectedValue(Object.assign(new Error('Unique constraint failed'), { code: 'P2002' }));

    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo: { email: 'bob@test.com' } });

    expect(res.status).toBe(409);
  });

  it.each([
    ['rol OWNER', { email: 'bob@test.com', role: 'OWNER' }],
    ['rol inventado', { email: 'bob@test.com', role: 'ADMIN' }],
    ['email mal escrito', { email: 'bob-arroba-test' }],
    ['sin email', { role: 'EDITOR' }],
  ])('%s: 400 sin buscar ni insertar', async (_caso, cuerpo) => {
    const res = await peticion(api.url, 'POST', ruta, { token: tokenDe('ana'), cuerpo });

    expect(res.status).toBe(400);
    expect(usuarios.findByEmail).not.toHaveBeenCalled();
    expect(proyectos.addMember).not.toHaveBeenCalled();
  });
});
