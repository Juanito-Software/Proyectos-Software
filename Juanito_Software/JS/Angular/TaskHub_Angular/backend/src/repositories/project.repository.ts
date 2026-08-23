import { Prisma } from '@prisma/client';
import { prisma } from '../config/prisma';

export const projectRepository = {
  create(data: Prisma.ProjectCreateInput) {
    return prisma.project.create({ data, include: { members: true } });
  },

  findById(id: string) {
    return prisma.project.findUnique({
      where: { id },
      include: { members: { include: { user: true } }, owner: true },
    });
  },

  findManyForUser(userId: string, params: { skip?: number; take?: number; search?: string }) {
    return prisma.project.findMany({
      where: {
        AND: [
          { OR: [{ ownerId: userId }, { members: { some: { userId } } }] },
          params.search ? { name: { contains: params.search, mode: 'insensitive' } } : {},
        ],
      },
      skip: params.skip,
      take: params.take,
      orderBy: { createdAt: 'desc' },
    });
  },

  update(id: string, data: Prisma.ProjectUpdateInput) {
    return prisma.project.update({ where: { id }, data });
  },

  delete(id: string) {
    return prisma.project.delete({ where: { id } });
  },

  addMember(projectId: string, userId: string, role: 'OWNER' | 'EDITOR' | 'VIEWER' = 'VIEWER') {
    return prisma.projectMember.create({ data: { projectId, userId, role } });
  },

  findMembership(projectId: string, userId: string) {
    return prisma.projectMember.findUnique({
      where: { projectId_userId: { projectId, userId } },
    });
  },
};
