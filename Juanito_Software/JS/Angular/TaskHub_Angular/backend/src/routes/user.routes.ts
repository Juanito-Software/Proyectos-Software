import { Router } from 'express';
import { Role } from '@prisma/client';
import { userController } from '../controllers/user.controller';
import { authenticate, authorize } from '../middlewares/authenticate';
import { validate } from '../middlewares/validate';
import { apiLimiter } from '../middlewares/rateLimit';
import { updateProfileSchema, changePasswordSchema, listUsersSchema } from '../validators/user.validators';

export const userRouter = Router();

userRouter.use(apiLimiter);
userRouter.use(authenticate);

userRouter.get('/', validate(listUsersSchema), userController.list);
userRouter.get('/:id', userController.getById);
userRouter.patch('/me/profile', validate(updateProfileSchema), userController.updateProfile);
userRouter.patch('/me/password', validate(changePasswordSchema), userController.changePassword);
userRouter.delete('/:id', authorize(Role.ADMIN), userController.remove);
