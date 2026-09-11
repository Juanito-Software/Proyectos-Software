import { Prisma, TaskStatus } from '@prisma/client';
import { prisma } from '../config/prisma';

export const taskRepository = {
  create(data: Prisma.TaskCreateInput) {
    return prisma.task.create({ data, include: { assignee: true, creator: true } });
  },

  findById(id: string) {
    return prisma.task.findUnique({
      where: { id },
      include: { assignee: true, creator: true, comments: { include: { author: true } }, project: true },
    });
  },

  /**
   * `visibleTo` es obligatorio a proposito: no hay forma de listar tareas sin
   * decir para quien. Los demas filtros pueden venir `undefined`, y Prisma
   * ignora las claves `undefined` del `where`; sin esta condicion, una peticion
   * sin filtros devolvia las tareas de todos los proyectos de la base de datos.
   */
  findMany(params: {
    visibleTo: string;
    projectId?: string;
    status?: TaskStatus;
    assigneeId?: string;
    skip?: number;
    take?: number;
  }) {
    return prisma.task.findMany({
      where: {
        projectId: params.projectId,
        status: params.status,
        assigneeId: params.assigneeId,
        project: {
          OR: [{ ownerId: params.visibleTo }, { members: { some: { userId: params.visibleTo } } }],
        },
      },
      include: { assignee: true, creator: true },
      skip: params.skip,
      take: params.take,
      orderBy: { createdAt: 'desc' },
    });
  },

  update(id: string, data: Prisma.TaskUpdateInput) {
    return prisma.task.update({ where: { id }, data, include: { assignee: true, creator: true } });
  },

  delete(id: string) {
    return prisma.task.delete({ where: { id } });
  },

  addComment(taskId: string, authorId: string, text: string) {
    return prisma.comment.create({
      data: { taskId, authorId, text },
      include: { author: true },
    });
  },

  countByStatusForUser(userId: string) {
    return prisma.task.groupBy({
      by: ['status'],
      where: { OR: [{ assigneeId: userId }, { creatorId: userId }] },
      _count: true,
    });
  },
};
