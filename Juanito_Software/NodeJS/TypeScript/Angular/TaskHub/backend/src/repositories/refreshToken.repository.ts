import { prisma } from '../config/prisma';

export const refreshTokenRepository = {
  create(userId: string, token: string, expiresAt: Date) {
    return prisma.refreshToken.create({ data: { userId, token, expiresAt } });
  },

  findByToken(token: string) {
    return prisma.refreshToken.findUnique({ where: { token }, include: { user: true } });
  },

  deleteByToken(token: string) {
    return prisma.refreshToken.deleteMany({ where: { token } });
  },

  deleteAllForUser(userId: string) {
    return prisma.refreshToken.deleteMany({ where: { userId } });
  },
};
