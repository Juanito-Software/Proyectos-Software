import rateLimit from 'express-rate-limit';

export const AUTH_LIMIT_POR_DEFECTO = 10;

/**
 * Cuántos intentos fallidos de autenticación se permiten por ventana.
 *
 * La suite de verificación necesita subirlo: comprueba una decena de
 * contraseñas que deben ser rechazadas, y todas cuentan como intento fallido —
 * que es justamente lo que este limitador existe para frenar. Sin la variable,
 * la suite se estrangula a sí misma y los fallos posteriores son falsos.
 *
 * **En producción la variable se ignora.** Un límite de autenticación que se
 * puede aflojar desde el entorno es un límite que no protege: bastaría con
 * colar `AUTH_RATE_LIMIT=100000` en el panel de despliegue para dejar la fuerza
 * bruta vía libre. Fuera de producción no hay nada que proteger.
 */
export function resolverAuthLimit(
  env: Record<string, string | undefined> = process.env,
): number {
  const bruto = env.AUTH_RATE_LIMIT;
  if (!bruto) return AUTH_LIMIT_POR_DEFECTO;
  if (env.NODE_ENV === 'production') return AUTH_LIMIT_POR_DEFECTO;

  const valor = Number(bruto);
  return Number.isInteger(valor) && valor > 0 ? valor : AUTH_LIMIT_POR_DEFECTO;
}

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
  limit: resolverAuthLimit(),
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
