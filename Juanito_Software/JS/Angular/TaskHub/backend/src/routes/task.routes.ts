import { Router } from 'express';
import { taskController } from '../controllers/task.controller';
import { authenticate } from '../middlewares/authenticate';
import { validate } from '../middlewares/validate';
import { createCommentSchema, createTaskSchema, listTasksSchema, updateTaskSchema } from '../validators/task.validators';

export const taskRouter = Router();

taskRouter.use(authenticate);

taskRouter.post('/', validate(createTaskSchema), taskController.create);
taskRouter.get('/', validate(listTasksSchema), taskController.list);
taskRouter.get('/dashboard/summary', taskController.dashboard);
taskRouter.get('/:id', taskController.getById);
taskRouter.put('/:id', validate(updateTaskSchema), taskController.update);
taskRouter.delete('/:id', taskController.remove);
taskRouter.post('/:id/comments', validate(createCommentSchema), taskController.addComment);
