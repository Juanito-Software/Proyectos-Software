import { Request, Response, NextFunction } from 'express';
import { adminService } from './admin.service.js';
import { ApiResponse } from '../../utils/api-response.js';

/**
 * Controlador del panel de administración (`/api/admin/*`).
 *
 * Solo traduce entre HTTP y `adminService`: lee parámetros, llama al servicio
 * y envuelve el resultado con `ApiResponse`. Los errores se pasan a `next()` y
 * los responde `errorHandler`. Que el usuario sea administrador ya lo
 * comprobaron `authMiddleware` y `adminMiddleware` en el router.
 */
export const adminController = {
  /** `GET /api/admin/users` — todos los usuarios con su número de tareas. */
  async listUsers(_req: Request, res: Response, next: NextFunction) {
    try {
      const users = await adminService.listUsers();
      res.json(ApiResponse.success(users, 'Usuarios obtenidos correctamente'));
    } catch (err) {
      next(err);
    }
  },

  /**
   * `DELETE /api/admin/users/:id` — borra un usuario y, en cascada, sus
   * tareas y sesiones. Responde 400 si el administrador intenta borrarse a sí
   * mismo o borrar al último administrador, y 404 si el usuario no existe.
   */
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

  /** `GET /api/admin/stats` — recuentos globales de usuarios y tareas. */
  async stats(_req: Request, res: Response, next: NextFunction) {
    try {
      const stats = await adminService.globalStats();
      res.json(ApiResponse.success(stats, 'Resumen global'));
    } catch (err) {
      next(err);
    }
  },
};
