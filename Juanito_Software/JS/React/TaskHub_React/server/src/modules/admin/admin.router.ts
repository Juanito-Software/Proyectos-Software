import { Router } from 'express';
import { adminController } from './admin.controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';
import { requireAdmin } from '../../middleware/admin.middleware.js';
import { apiLimiter } from '../../middleware/rateLimit.middleware.js';
import { validate, validarUuid } from '../../middleware/validate.middleware.js';

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
// El :id se valida antes de consultar: la columna es UUID y un valor mal
// formado acababa en 500 en vez de 400.
router.delete('/users/:id', validate(validarUuid('id')), adminController.removeUser);

// GET /api/admin/stats - Resumen de toda la instancia
router.get('/stats', adminController.stats);

export const adminRouter = router;
