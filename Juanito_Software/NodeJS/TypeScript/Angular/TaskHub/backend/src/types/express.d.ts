import { Role } from '@prisma/client';

// Extiende el Request de Express para incluir el usuario autenticado
// una vez que pasa por el middleware de autenticación JWT.
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email: string;
        role: Role;
      };
    }
  }
}

export {};
