import { describe, it, expect, vi, beforeEach } from 'vitest';

// El cliente Prisma se instancia al importar config/prisma; lo aislamos para que
// los tests unitarios no abran conexión ni exijan `prisma generate`.
vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class { $connect() {} $disconnect() {} },
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
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
  },
}));

import { projectService } from '../services/project.service';
import { projectRepository } from '../repositories/project.repository';

const repo = vi.mocked(projectRepository);

const owner = {
  id: 'owner-1',
  name: 'Juan',
  email: 'juan@test.com',
  role: 'MEMBER' as const,
  avatarUrl: null,
  createdAt: new Date('2026-01-01'),
  password: 'NO-DEBE-SALIR',
};

const member = { ...owner, id: 'member-1', email: 'ana@test.com', name: 'Ana' };

const project = {
  id: 'proj-1',
  name: 'TaskHub',
  description: null,
  ownerId: 'owner-1',
  createdAt: new Date('2026-01-01'),
  updatedAt: new Date('2026-01-01'),
  owner,
  members: [{ userId: 'member-1', role: 'MEMBER', user: member }],
};

beforeEach(() => vi.clearAllMocks());

describe('projectService.create', () => {
  it('añade al creador como miembro OWNER en la misma operación', async () => {
    repo.create.mockResolvedValue(project as never);

    await projectService.create('owner-1', { name: 'TaskHub' } as never);

    const arg = repo.create.mock.calls[0][0] as Record<string, unknown>;
    expect(arg.owner).toEqual({ connect: { id: 'owner-1' } });
    expect(arg.members).toEqual({ create: { userId: 'owner-1', role: 'OWNER' } });
  });
});

describe('projectService.getById — control de acceso', () => {
  it('lanza 404 si el proyecto no existe', async () => {
    repo.findById.mockResolvedValue(null as never);
    await expect(projectService.getById('nope', 'owner-1')).rejects.toMatchObject({
      statusCode: 404,
    });
  });

  it('lanza 403 a un usuario que no es owner ni miembro', async () => {
    repo.findById.mockResolvedValue(project as never);
    await expect(projectService.getById('proj-1', 'intruso')).rejects.toMatchObject({
      statusCode: 403,
      message: 'No tienes acceso a este proyecto',
    });
  });

  it('permite el acceso al propietario', async () => {
    repo.findById.mockResolvedValue(project as never);
    const dto = await projectService.getById('proj-1', 'owner-1');
    expect(dto.id).toBe('proj-1');
  });

  it('permite el acceso a un miembro que no es propietario', async () => {
    repo.findById.mockResolvedValue(project as never);
    const dto = await projectService.getById('proj-1', 'member-1');
    expect(dto.id).toBe('proj-1');
  });

  it('no expone la contraseña de owner ni de los miembros', async () => {
    repo.findById.mockResolvedValue(project as never);
    const dto = await projectService.getById('proj-1', 'owner-1');

    expect(dto.owner).not.toHaveProperty('password');
    expect(dto.members[0].user).not.toHaveProperty('password');
  });
});

describe('projectService.assertOwner', () => {
  it('lanza 404 si el proyecto no existe', async () => {
    repo.findById.mockResolvedValue(null as never);
    await expect(projectService.assertOwner('nope', 'owner-1')).rejects.toMatchObject({
      statusCode: 404,
    });
  });

  it('lanza 403 a un miembro que no es propietario', async () => {
    repo.findById.mockResolvedValue(project as never);
    await expect(projectService.assertOwner('proj-1', 'member-1')).rejects.toMatchObject({
      statusCode: 403,
      message: 'Solo el propietario puede realizar esta acción',
    });
  });

  it('devuelve el proyecto si es el propietario', async () => {
    repo.findById.mockResolvedValue(project as never);
    expect(await projectService.assertOwner('proj-1', 'owner-1')).toEqual(project);
  });
});

describe('operaciones restringidas al propietario', () => {
  it('update: un miembro no propietario no puede modificar', async () => {
    repo.findById.mockResolvedValue(project as never);
    await expect(
      projectService.update('proj-1', 'member-1', { name: 'hack' } as never),
    ).rejects.toMatchObject({ statusCode: 403 });
    expect(repo.update).not.toHaveBeenCalled();
  });

  it('remove: un miembro no propietario no puede borrar', async () => {
    repo.findById.mockResolvedValue(project as never);
    await expect(projectService.remove('proj-1', 'member-1')).rejects.toMatchObject({
      statusCode: 403,
    });
    expect(repo.delete).not.toHaveBeenCalled();
  });

  it('addMember: un miembro no propietario no puede añadir gente', async () => {
    repo.findById.mockResolvedValue(project as never);
    await expect(
      projectService.addMember('proj-1', 'member-1', { userId: 'x', role: 'MEMBER' } as never),
    ).rejects.toMatchObject({ statusCode: 403 });
    expect(repo.addMember).not.toHaveBeenCalled();
  });

  it('el propietario sí puede actualizar', async () => {
    repo.findById.mockResolvedValue(project as never);
    repo.update.mockResolvedValue(project as never);

    await projectService.update('proj-1', 'owner-1', { name: 'Nuevo' } as never);
    expect(repo.update).toHaveBeenCalledWith('proj-1', { name: 'Nuevo' });
  });
});

describe('projectService.listForUser', () => {
  it('traduce página/límite a skip/take y propaga la búsqueda', async () => {
    repo.findManyForUser.mockResolvedValue([] as never);

    await projectService.listForUser('owner-1', 2, 15, 'task');

    expect(repo.findManyForUser).toHaveBeenCalledWith('owner-1', {
      skip: 15,
      take: 15,
      search: 'task',
    });
  });
});
