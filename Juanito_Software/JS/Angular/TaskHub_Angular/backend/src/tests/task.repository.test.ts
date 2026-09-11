import { describe, it, expect, vi, beforeEach } from 'vitest';

const findMany = vi.fn();
vi.mock('../config/prisma', () => ({ prisma: { task: { findMany: (...a: unknown[]) => findMany(...a) } } }));
vi.mock('@prisma/client', () => ({ PrismaClient: class {} }));

import { taskRepository } from '../repositories/task.repository';

/**
 * El unico test de repositorio, y esta aqui por una razon concreta.
 *
 * tasks.http.test.ts comprueba que el servicio pasa `visibleTo` al
 * repositorio, pero con el repositorio sustituido no puede ver que ese dato
 * acabe en la consulta. Y es justo ahi donde estaba el fallo: Prisma ignora las
 * claves `undefined` del `where`, asi que una lista sin filtros devolvia las
 * tareas de todos los proyectos. Este test mira el `where` que recibe Prisma.
 */
describe('taskRepository.findMany', () => {
  beforeEach(() => findMany.mockReset().mockResolvedValue([]));

  it('sin filtros, la consulta sigue limitada a los proyectos del usuario', async () => {
    await taskRepository.findMany({ visibleTo: 'bob' });

    const { where } = findMany.mock.calls[0][0];
    expect(where.project).toEqual({
      OR: [{ ownerId: 'bob' }, { members: { some: { userId: 'bob' } } }],
    });
  });

  it('con projectId, el filtro de pertenencia se mantiene ademas del proyecto', async () => {
    // Defensa en profundidad: el servicio ya comprueba el acceso antes de
    // llamar, pero si algun dia alguien se lo salta, la consulta no devuelve
    // nada de un proyecto ajeno.
    await taskRepository.findMany({ visibleTo: 'bob', projectId: 'p1' });

    const { where } = findMany.mock.calls[0][0];
    expect(where.projectId).toBe('p1');
    expect(where.project.OR).toContainEqual({ ownerId: 'bob' });
  });
});
