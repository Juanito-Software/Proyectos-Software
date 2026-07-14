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

  findMany(params: {
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
