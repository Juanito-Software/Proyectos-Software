import { Router } from 'express';
import { authController } from '../controllers/auth.controller';
import { validate } from '../middlewares/validate';
import { authLimiter } from '../middlewares/rateLimit';
import { registerSchema, loginSchema } from '../validators/auth.validators';

export const authRouter = Router();

// Límite de intentos: estas rutas son las que permiten adivinar credenciales.
authRouter.use(authLimiter);

authRouter.post('/register', validate(registerSchema), authController.register);
authRouter.post('/login', validate(loginSchema), authController.login);
authRouter.post('/refresh', authController.refresh);
authRouter.post('/logout', authController.logout);
