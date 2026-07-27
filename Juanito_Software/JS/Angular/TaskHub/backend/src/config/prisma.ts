import { PrismaClient } from '@prisma/client';
import { isProduction } from './env';

// Patrón singleton: evita crear múltiples conexiones en desarrollo (hot-reload).
declare global {
   
  var __prisma__: PrismaClient | undefined;
}

export const prisma =
  global.__prisma__ ??
  new PrismaClient({
    log: isProduction ? ['error', 'warn'] : ['query', 'error', 'warn'],
  });

if (!isProduction) {
  global.__prisma__ = prisma;
}
