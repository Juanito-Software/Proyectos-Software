import { Router } from 'express';
import { TasksController } from './tasks.controller';
import { validate } from '../../middleware/validate.middleware';
import {
  createTaskValidator,
  updateTaskValidator,
  filterTasksValidator,
} from './tasks.validation';

const router = Router();
const controller = new TasksController();

// GET /api/tasks (Retrieves all tasks with optional filters)
router.get('/', validate(filterTasksValidator), controller.getAllTasks);

// GET /api/tasks/:id (Retrieves a single task by ID)
router.get('/:id', controller.getTaskById);

// POST /api/tasks (Creates a new task)
router.post('/', validate(createTaskValidator), controller.createTask);

// PUT /api/tasks/:id (Updates an existing task)
router.put('/:id', validate(updateTaskValidator), controller.updateTask);

// DELETE /api/tasks/:id (Deletes a task)
router.delete('/:id', controller.deleteTask);

export const tasksRouter = router;
