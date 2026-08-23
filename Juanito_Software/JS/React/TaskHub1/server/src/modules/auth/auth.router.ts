import { Router } from 'express';
import { authController } from './auth.controller.js';
import { validate } from '../../middleware/validate.middleware.js';
import { registerValidator, loginValidator } from './auth.validation.js';
import { authLimiter } from '../../middleware/rateLimit.middleware.js';

const router = Router();

// Límite de intentos en todas las rutas de este router: son las que permiten
// adivinar credenciales por fuerza bruta.
router.use(authLimiter);

router.post('/register', validate(registerValidator), authController.register);
router.post('/login', validate(loginValidator), authController.login);

export const authRouter = router;
