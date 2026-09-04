import { Router } from 'express';
import { authController } from './auth.controller.js';
import { validate } from '../../middleware/validate.middleware.js';
import {
  registerValidator,
  loginValidator,
  changePasswordValidator,
} from './auth.validation.js';
import {
  authLimiter,
  accountLimiter,
  accountSlowDown,
} from '../../middleware/rateLimit.middleware.js';
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
// Tres capas sobre el inicio de sesión, que es la única ruta donde se adivina
// una contraseña a partir de un nombre de usuario del cuerpo:
//
// 1. `authLimiter` (arriba, para todo el router) corta por dirección de origen.
//    Frena a quien ataca desde un sitio, que es el caso corriente.
// 2. `accountSlowDown` retrasa por cuenta, con la curva creciendo desde el
//    cuarto fallo. Es la defensa principal contra el ataque repartido entre
//    muchas direcciones, y **no bloquea a nadie**: por eso va antes que el
//    limitador duro, para hacer el trabajo cuando aún no hace falta cortar.
// 3. `accountLimiter` es el tope duro, doscientos, como red de seguridad para
//    el caso patológico.
//
// El orden importa: el retraso primero encarece cada intento, así que llegar al
// tope duro exige más de una hora de martilleo continuado.
router.post(
  '/login',
  accountSlowDown,
  accountLimiter,
  validate(loginValidator),
  authController.login,
);

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

// Exige sesión: el usuario sale del token de acceso, nunca del cuerpo. Si
// viniera del cuerpo, cualquiera podría cambiar la contraseña de otro con solo
// escribir su identificador.
//
// Y hereda el `authLimiter` de arriba, que aquí importa más de lo que parece:
// esta ruta comprueba la contraseña actual, así que sin límite sería un oráculo
// para adivinarla a ciegas con un token robado.
router.post(
  '/change-password',
  authMiddleware,
  validate(changePasswordValidator),
  authController.changePassword,
);

export const authRouter = router;
