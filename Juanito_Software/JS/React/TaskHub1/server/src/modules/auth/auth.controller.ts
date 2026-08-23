import { Request, Response, NextFunction } from 'express';
import { authService } from './auth.service.js';
import { ApiResponse } from '../../utils/api-response.js';

export const authController = {
  async register(req: Request, res: Response, next: NextFunction) {
    try {
      const result = await authService.register(req.body);
      res.status(201).json(ApiResponse.success(result, 'Cuenta creada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  async login(req: Request, res: Response, next: NextFunction) {
    try {
      const result = await authService.login(req.body);
      res.json(ApiResponse.success(result, 'Sesión iniciada correctamente'));
    } catch (err) {
      next(err);
    }
  },
};
