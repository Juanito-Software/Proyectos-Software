import { Prisma } from '@prisma/client';
import { prisma } from '../config/prisma';

// La capa de repositorio es la única que habla directamente con Prisma.
// Servicios y controladores nunca importan `prisma` directamente.
export const userRepository = {
  findByEmail(email: string) {
    return prisma.user.findUnique({ where: { email } });
  },

  findById(id: string) {
    return prisma.user.findUnique({ where: { id } });
  },

  create(data: Prisma.UserCreateInput) {
    return prisma.user.create({ data });
  },

  update(id: string, data: Prisma.UserUpdateInput) {
    return prisma.user.update({ where: { id }, data });
  },

  delete(id: string) {
    return prisma.user.delete({ where: { id } });
  },

  findMany(params: { skip?: number; take?: number } = {}) {
    return prisma.user.findMany({
      skip: params.skip,
      take: params.take,
      orderBy: { createdAt: 'desc' },
    });
  },

  count() {
    return prisma.user.count();
  },
};
