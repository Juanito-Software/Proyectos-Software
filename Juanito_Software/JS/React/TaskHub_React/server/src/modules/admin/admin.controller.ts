import { Request, Response, NextFunction } from 'express';
import { adminService } from './admin.service.js';
import { ApiResponse } from '../../utils/api-response.js';

export const adminController = {
  async listUsers(_req: Request, res: Response, next: NextFunction) {
    try {
      const users = await adminService.listUsers();
      res.json(ApiResponse.success(users, 'Usuarios obtenidos correctamente'));
    } catch (err) {
      next(err);
    }
  },

  async removeUser(req: Request, res: Response, next: NextFunction) {
    try {
      // El id de quien pide se toma del token, nunca del cuerpo de la
      // petición: si viniera de fuera, cualquiera podría saltarse la
      // comprobación de "no puedes borrarte a ti mismo" mandando otro id.
      const deleted = await adminService.removeUser(req.params.id, req.userId!);
      res.json(ApiResponse.success(deleted, 'Usuario eliminado junto con sus tareas'));
    } catch (err) {
      next(err);
    }
  },

  async stats(_req: Request, res: Response, next: NextFunction) {
    try {
      const stats = await adminService.globalStats();
      res.json(ApiResponse.success(stats, 'Resumen global'));
    } catch (err) {
      next(err);
    }
  },
};
