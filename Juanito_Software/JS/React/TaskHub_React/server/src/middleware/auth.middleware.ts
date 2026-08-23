import { Request, Response, NextFunction } from 'express';
import { tokenService } from '../modules/auth/token.service.js';
import { ApiError } from '../utils/api-error.js';

export function authMiddleware(req: Request, _res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;

  if (!token) {
    next(ApiError.unauthorized('Token de autenticación requerido'));
    return;
  }

  try {
    const payload = tokenService.verifyToken(token);
    req.userId = payload.userId;
    req.username = payload.username;
    next();
  } catch {
    next(ApiError.unauthorized('Token inválido o expirado'));
  }
}
