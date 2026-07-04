import { Router } from 'express';
import { authRouter } from './auth.routes';
import { userRouter } from './user.routes';
import { projectRouter } from './project.routes';
import { taskRouter } from './task.routes';

export const apiRouter = Router();

apiRouter.use('/auth', authRouter);
apiRouter.use('/users', userRouter);
apiRouter.use('/projects', projectRouter);
apiRouter.use('/tasks', taskRouter);
