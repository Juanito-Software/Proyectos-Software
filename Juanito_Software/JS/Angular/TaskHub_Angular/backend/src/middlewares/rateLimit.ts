import rateLimit from 'express-rate-limit';

/**
 * Límite estricto para las rutas de autenticación.
 *
 * Sin él, un atacante puede probar contraseñas al ritmo que le permita la red.
 * Con 10 intentos cada 15 minutos por IP, la fuerza bruta deja de ser viable y
 * un usuario legítimo que se equivoque un par de veces no lo nota.
 *
 * skipSuccessfulRequests hace que los accesos correctos no gasten cuota: solo
 * penaliza a quien falla repetidamente.
 */
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  limit: 10,
  skipSuccessfulRequests: true,
  standardHeaders: 'draft-7',
  legacyHeaders: false,
  message: {
    error: 'Demasiados intentos de acceso. Inténtalo de nuevo en unos minutos.',
  },
});

/**
 * Límite general para el resto de la API: protege frente al abuso accidental
 * (un bucle mal escrito en el cliente) y frente a la saturación deliberada.
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
