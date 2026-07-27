import { Router } from 'express';
import { projectController } from '../controllers/project.controller';
import { authenticate } from '../middlewares/authenticate';
import { validate } from '../middlewares/validate';
import { apiLimiter } from '../middlewares/rateLimit';
import { addMemberSchema, createProjectSchema, updateProjectSchema } from '../validators/project.validators';

export const projectRouter = Router();

projectRouter.use(apiLimiter);
projectRouter.use(authenticate);

projectRouter.post('/', validate(createProjectSchema), projectController.create);
projectRouter.get('/', projectController.list);
projectRouter.get('/:id', projectController.getById);
projectRouter.put('/:id', validate(updateProjectSchema), projectController.update);
projectRouter.delete('/:id', projectController.remove);
projectRouter.post('/:id/members', validate(addMemberSchema), projectController.addMember);
