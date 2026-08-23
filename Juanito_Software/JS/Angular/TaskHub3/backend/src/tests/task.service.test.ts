import { describe, it, expect, vi, beforeEach } from 'vitest';

// El cliente Prisma se instancia al importar config/prisma; lo aislamos para que
// los tests unitarios no abran conexión ni exijan `prisma generate`.
vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class { $connect() {} $disconnect() {} },
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));

vi.mock('../repositories/task.repository', () => ({
  taskRepository: {
    create: vi.fn(),
    findMany: vi.fn(),
    findById: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    addComment: vi.fn(),
    countByStatusForUser: vi.fn(),
  },
}));

import { taskService } from '../services/task.service';
import { taskRepository } from '../repositories/task.repository';

const repo = vi.mocked(taskRepository);

const rawUser = {
  id: 'user-1',
  name: 'Juan',
  email: 'juan@test.com',
  role: 'MEMBER' as const,
  avatarUrl: null,
  createdAt: new Date('2026-01-01'),
  password: 'NO-DEBE-SALIR',
};

const rawTask = {
  id: 'task-1',
  title: 'Escribir tests',
  description: null,
  status: 'TODO' as const,
  priority: 'HIGH' as const,
  deadline: null,
  projectId: 'proj-1',
  createdAt: new Date('2026-01-01'),
  updatedAt: new Date('2026-01-01'),
  assignee: rawUser,
  creator: rawUser,
  comments: [],
};

beforeEach(() => vi.clearAllMocks());

describe('taskService.create', () => {
  it('conecta proyecto y creador, y omite assignee si no se envía', async () => {
    repo.create.mockResolvedValue(rawTask as never);

    await taskService.create('user-1', {
      title: 'Escribir tests',
      projectId: 'proj-1',
    } as never);

    const arg = repo.create.mock.calls[0][0] as Record<string, unknown>;
    expect(arg.project).toEqual({ connect: { id: 'proj-1' } });
    expect(arg.creator).toEqual({ connect: { id: 'user-1' } });
    expect(arg.assignee).toBeUndefined();
  });

  it('convierte el deadline de string ISO a Date', async () => {
    repo.create.mockResolvedValue(rawTask as never);

    await taskService.create('user-1', {
      title: 'x',
      projectId: 'proj-1',
      deadline: '2026-06-15T10:00:00.000Z',
    } as never);

    const arg = repo.create.mock.calls[0][0] as { deadline: Date };
    expect(arg.deadline).toBeInstanceOf(Date);
    expect(arg.deadline.toISOString()).toBe('2026-06-15T10:00:00.000Z');
  });

  it('no filtra la contraseña del assignee ni del creator en el DTO', async () => {
    repo.create.mockResolvedValue(rawTask as never);
    const dto = await taskService.create('user-1', { title: 'x', projectId: 'p' } as never);

    expect(dto.assignee).not.toHaveProperty('password');
    expect(dto.creator).not.toHaveProperty('password');
  });
});

describe('taskService.list', () => {
  it('traduce página y límite a skip/take (paginación 1-indexada)', async () => {
    repo.findMany.mockResolvedValue([] as never);

    await taskService.list({ projectId: 'proj-1' }, 3, 20);

    expect(repo.findMany).toHaveBeenCalledWith(
      expect.objectContaining({ projectId: 'proj-1', skip: 40, take: 20 }),
    );
  });

  it('la primera página empieza en skip 0', async () => {
    repo.findMany.mockResolvedValue([] as never);
    await taskService.list({}, 1, 10);
    expect(repo.findMany).toHaveBeenCalledWith(expect.objectContaining({ skip: 0 }));
  });
});

describe('taskService.getById', () => {
  it('lanza 404 si la tarea no existe', async () => {
    repo.findById.mockResolvedValue(null as never);
    await expect(taskService.getById('nope')).rejects.toMatchObject({
      statusCode: 404,
      message: 'Tarea no encontrada',
    });
  });

  it('devuelve el DTO cuando existe', async () => {
    repo.findById.mockResolvedValue(rawTask as never);
    const dto = await taskService.getById('task-1');
    expect(dto.id).toBe('task-1');
    expect(dto.title).toBe('Escribir tests');
  });
});

describe('taskService.update', () => {
  it('lanza 404 sin llamar a update si la tarea no existe', async () => {
    repo.findById.mockResolvedValue(null as never);
    await expect(taskService.update('nope', {} as never)).rejects.toMatchObject({ statusCode: 404 });
    expect(repo.update).not.toHaveBeenCalled();
  });

  it('distingue null (desasignar) de undefined (no tocar) en assigneeId', async () => {
    repo.findById.mockResolvedValue(rawTask as never);
    repo.update.mockResolvedValue(rawTask as never);

    await taskService.update('task-1', { assigneeId: null } as never);
    expect((repo.update.mock.calls[0][1] as Record<string, unknown>).assignee).toEqual({
      disconnect: true,
    });

    vi.clearAllMocks();
    repo.findById.mockResolvedValue(rawTask as never);
    repo.update.mockResolvedValue(rawTask as never);

    await taskService.update('task-1', { title: 'nuevo' } as never);
    expect((repo.update.mock.calls[0][1] as Record<string, unknown>).assignee).toBeUndefined();
  });

  it('permite limpiar el deadline enviando null', async () => {
    repo.findById.mockResolvedValue(rawTask as never);
    repo.update.mockResolvedValue(rawTask as never);

    await taskService.update('task-1', { deadline: null } as never);
    expect((repo.update.mock.calls[0][1] as Record<string, unknown>).deadline).toBeNull();
  });
});

describe('taskService.remove', () => {
  it('no borra si la tarea no existe', async () => {
    repo.findById.mockResolvedValue(null as never);
    await expect(taskService.remove('nope')).rejects.toMatchObject({ statusCode: 404 });
    expect(repo.delete).not.toHaveBeenCalled();
  });

  it('borra cuando existe', async () => {
    repo.findById.mockResolvedValue(rawTask as never);
    await taskService.remove('task-1');
    expect(repo.delete).toHaveBeenCalledWith('task-1');
  });
});

describe('taskService.addComment', () => {
  it('valida que la tarea existe antes de comentar', async () => {
    repo.findById.mockResolvedValue(null as never);
    await expect(taskService.addComment('nope', 'user-1', { text: 'hola' })).rejects.toMatchObject({
      statusCode: 404,
    });
    expect(repo.addComment).not.toHaveBeenCalled();
  });
});

describe('taskService.dashboardSummary', () => {
  it('rellena con 0 los estados sin tareas', async () => {
    repo.countByStatusForUser.mockResolvedValue([
      { status: 'TODO', _count: 3 },
      { status: 'DONE', _count: 7 },
    ] as never);

    expect(await taskService.dashboardSummary('user-1')).toEqual({
      TODO: 3,
      IN_PROGRESS: 0,
      IN_REVIEW: 0,
      DONE: 7,
    });
  });

  it('devuelve todos los estados a 0 si el usuario no tiene tareas', async () => {
    repo.countByStatusForUser.mockResolvedValue([] as never);

    expect(await taskService.dashboardSummary('user-1')).toEqual({
      TODO: 0,
      IN_PROGRESS: 0,
      IN_REVIEW: 0,
      DONE: 0,
    });
  });
});
