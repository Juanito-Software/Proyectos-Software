import { Router } from 'express';
import { tasksController } from './tasks.controller.js';
import { validate, validarUuid } from '../../middleware/validate.middleware.js';
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

// A partir de aquí todas las rutas llevan un :id. Se valida su forma antes de
// que llegue a la consulta: la columna es UUID y un valor mal formado hacía
// reventar a PostgreSQL con un 500 en lugar de responder 400.
const idValido = validate(validarUuid('id'));

// GET /api/tasks/:id - Obtener una tarea por ID
router.get('/:id', idValido, tasksController.getById);

// POST /api/tasks - Crear tarea
router.post('/', validate(createTaskValidator), tasksController.create);

// PUT /api/tasks/:id - Actualizar tarea completa
router.put('/:id', idValido, validate(updateTaskValidator), tasksController.update);

// PATCH /api/tasks/:id - Actualización parcial (ej. solo marcar completada)
router.patch('/:id', idValido, validate(updateTaskValidator), tasksController.update);

// DELETE /api/tasks/:id - Eliminar tarea
router.delete('/:id', idValido, tasksController.remove);

export const tasksRouter = router;
