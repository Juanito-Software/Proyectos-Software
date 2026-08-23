import rateLimit from 'express-rate-limit';

/**
 * Límite estricto para las rutas de autenticación.
 *
 * Sin él, un atacante puede probar contraseñas al ritmo que le permita la red:
 * miles por minuto contra el mismo usuario. Con 10 intentos cada 15 minutos por
 * IP, un ataque de fuerza bruta pasa de horas a siglos, y un usuario legítimo
 * que se equivoque un par de veces no lo nota.
 *
 * skipSuccessfulRequests: los inicios de sesión correctos no gastan cuota, así
 * que solo penaliza a quien falla repetidamente.
 */
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 10,
  skipSuccessfulRequests: true,
  standardHeaders: 'draft-7',
  legacyHeaders: false,
  message: {
    error: 'Demasiados intentos de acceso. Inténtalo de nuevo en unos minutos.',
  },
});

/**
 * Límite general para el resto de la API.
 *
 * Más holgado: aquí no protegemos contra adivinar credenciales, sino contra el
 * abuso accidental (un bucle mal escrito en el cliente) o la saturación
 * deliberada del servidor.
 */
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 300,
  standardHeaders: 'draft-7',
  legacyHeaders: false,
  message: {
    error: 'Demasiadas peticiones. Inténtalo de nuevo más tarde.',
  },
});
