import { Router } from 'express';
import { authController } from './auth.controller.js';
import { validate } from '../../middleware/validate.middleware.js';
import { registerValidator, loginValidator } from './auth.validation.js';
import { authLimiter } from '../../middleware/rateLimit.middleware.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';

const router = Router();

// Límite de intentos en todas las rutas de este router: son las que permiten
// adivinar credenciales por fuerza bruta.
//
// La renovación también entra, y no estorba: el limitador solo cuenta las
// peticiones que fallan, así que un usuario que renueve cada cuarto de hora no
// gasta cuota nunca. Quien sí la gasta es el que prueba tokens de refresco a
// ciegas, que es justo a quien hay que frenar.
router.use(authLimiter);

router.post('/register', validate(registerValidator), authController.register);
router.post('/login', validate(loginValidator), authController.login);

// Sin authMiddleware a propósito: la renovación se pide cuando el token de
// acceso ya ha caducado. Quien autentica aquí es la cookie de refresco.
router.post('/refresh', authController.refresh);

// El logout tampoco lo exige: si alguien se deja la pestaña abierta más de
// quince minutos, su token de acceso habrá caducado, y sería absurdo impedirle
// cerrar sesión justo entonces. La cookie basta para saber qué sesión cerrar.
router.post('/logout', authController.logout);

// Este sí, porque cierra TODAS las sesiones del usuario. El identificador sale
// del token de acceso, nunca del cuerpo de la petición: si viniera del cuerpo,
// cualquiera podría cerrar las sesiones de otro.
router.post('/logout-all', authMiddleware, authController.logoutAll);

export const authRouter = router;
