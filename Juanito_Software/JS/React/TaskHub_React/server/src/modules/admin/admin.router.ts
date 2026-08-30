import { Router } from 'express';
import { adminController } from './admin.controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';
import { requireAdmin } from '../../middleware/admin.middleware.js';
import { apiLimiter } from '../../middleware/rateLimit.middleware.js';

const router = Router();

// Los dos middlewares se aplican al router entero, no ruta por ruta: así una
// ruta nueva nace protegida y no depende de que alguien se acuerde de añadir
// el guardia. Primero identificar (401 si no hay token), después autorizar
// (403 si no es administrador).
router.use(apiLimiter);
router.use(authMiddleware);
router.use(requireAdmin);

// GET /api/admin/users - Listado de usuarios con su número de tareas
router.get('/users', adminController.listUsers);

// DELETE /api/admin/users/:id - Borra el usuario y, en cascada, sus tareas
router.delete('/users/:id', adminController.removeUser);

// GET /api/admin/stats - Resumen de toda la instancia
router.get('/stats', adminController.stats);

export const adminRouter = router;
