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

export const CUENTA_LIMIT_POR_DEFECTO = 20;

/**
 * Igual que `resolverAuthLimit`, y por el mismo motivo: la suite de
 * verificación necesita aflojarlo y producción tiene que ignorarlo.
 */
export function resolverCuentaLimit(
  env: Record<string, string | undefined> = process.env,
): number {
  const bruto = env.ACCOUNT_RATE_LIMIT;
  if (!bruto) return CUENTA_LIMIT_POR_DEFECTO;
  if (env.NODE_ENV === 'production') return CUENTA_LIMIT_POR_DEFECTO;

  const valor = Number(bruto);
  return Number.isInteger(valor) && valor > 0 ? valor : CUENTA_LIMIT_POR_DEFECTO;
}

/**
 * Deriva la clave del limitador por cuenta a partir del cuerpo de la petición.
 *
 * **Se normaliza igual que en el inicio de sesión** —recortado y en
 * minúsculas—, porque la unicidad del nombre de usuario está garantizada por un
 * índice sobre `LOWER(username)`. Sin normalizar, `Juan` y `juan` caerían en
 * cubos distintos y bastaría con alternar mayúsculas para multiplicar los
 * intentos permitidos.
 *
 * Un cuerpo sin usuario cae en un cubo común. No es un problema: quien manda
 * peticiones malformadas solo se estorba a sí mismo y a otras peticiones
 * igualmente malformadas.
 */
export function claveDeCuenta(req: { body?: unknown }): string {
  const cuerpo = (req.body ?? {}) as Record<string, unknown>;
  const usuario = cuerpo.username;
  if (typeof usuario !== 'string' || !usuario.trim()) return '__sin-usuario__';
  return usuario.trim().toLowerCase();
}

/**
 * Límite por CUENTA, además del que ya existe por IP.
 *
 * **El agujero que cierra.** `authLimiter` cuenta intentos por dirección de
 * origen, así que frena a quien ataca desde un sitio. No frena a quien reparte:
 * con mil direcciones, diez intentos desde cada una son diez mil contra la
 * misma cuenta sin que salte nada. Este contador va por nombre de usuario, y le
 * da igual de dónde venga cada intento.
 *
 * **No filtra qué cuentas existen.** El cubo se crea con el nombre que llegue,
 * exista o no en la base de datos. Si solo se contaran los usuarios reales, la
 * diferencia de comportamiento entre un nombre registrado y uno inventado sería
 * un modo de enumerarlos.
 *
 * **El precio, dicho claro: esto permite bloquear una cuenta ajena a
 * propósito.** Cualquiera que sepa un nombre de usuario puede fallar veinte
 * veces y dejarlo sin poder iniciar sesión durante un cuarto de hora. Es el
 * compromiso clásico de este mecanismo, y aquí se acepta por tres razones:
 *
 * 1. El límite es **el doble** que el de IP, así que un usuario que se
 *    equivoque de verdad no lo alcanza jamás.
 * 2. El bloqueo es temporal y acotado: quince minutos, no permanente.
 * 3. Y sobre todo, **no expulsa a nadie**. Solo impide iniciar sesión de nuevo;
 *    quien ya está dentro sigue dentro, porque su renovación va por la cookie
 *    de refresco y no vuelve a pasar por la contraseña. El daño es «no puedo
 *    entrar desde un dispositivo nuevo durante un rato», no «me han echado».
 *
 * La alternativa sin ese precio son los retardos progresivos, que no bloquean a
 * nadie pero exigen estado propio y no vienen en esta librería. Queda anotado.
 */
export const accountLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: resolverCuentaLimit(),
  keyGenerator: claveDeCuenta,
  skipSuccessfulRequests: true,
  standardHeaders: 'draft-7',
  legacyHeaders: false,
  message: {
    error: 'Demasiados intentos para esta cuenta. Inténtalo de nuevo en unos minutos.',
  },
});
