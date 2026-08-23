import { Router } from 'express';
import { tasksController } from './tasks.controller.js';
import { validate } from '../../middleware/validate.middleware.js';
import { createTaskValidator, updateTaskValidator, filterTasksValidator } from './tasks.validation.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';
import { apiLimiter } from '../../middleware/rateLimit.middleware.js';

const router = Router();

router.use(apiLimiter);
router.use(authMiddleware);

// GET /api/tasks - Listar tareas del usuario (filtros: status, priority, search)
router.get('/', validate(filterTasksValidator), tasksController.list);

// GET /api/tasks/stats - Resumen por estado del usuario autenticado.
// Debe declararse ANTES de /:id, o Express interpretaría "stats" como un id.
router.get('/stats', tasksController.stats);

// GET /api/tasks/:id - Obtener una tarea por ID
router.get('/:id', tasksController.getById);

// POST /api/tasks - Crear tarea
router.post('/', validate(createTaskValidator), tasksController.create);

// PUT /api/tasks/:id - Actualizar tarea completa
router.put('/:id', validate(updateTaskValidator), tasksController.update);

// PATCH /api/tasks/:id - Actualización parcial (ej. solo marcar completada)
router.patch('/:id', validate(updateTaskValidator), tasksController.update);

// DELETE /api/tasks/:id - Eliminar tarea
router.delete('/:id', tasksController.remove);

export const tasksRouter = router;
