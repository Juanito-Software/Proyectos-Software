import rateLimit from 'express-rate-limit';
import slowDown from 'express-slow-down';

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

/**
 * Tope duro por cuenta. **Es una red de seguridad, no la defensa principal.**
 *
 * El trabajo real lo hacen los retrasos progresivos de más abajo. Este número
 * está deliberadamente lejos —doscientos, no veinte— porque un bloqueo es un
 * binario, y cualquier binario que un atacante pueda forzar se convierte en un
 * arma: con el umbral bajo, cualquiera que supiera un nombre de usuario podía
 * dejar a su dueño sin poder entrar. A doscientos intentos con retrasos de
 * treinta segundos por medio, provocarlo cuesta más de una hora de trabajo
 * continuado para conseguir un bloqueo de quince minutos.
 */
export const CUENTA_LIMIT_POR_DEFECTO = 200;

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

/** Fallos que se perdonan antes de empezar a retrasar. */
export const RETRASO_DESDE = 3;

/**
 * Igual que las otras dos válvulas, y por el mismo motivo doble.
 *
 * La suite de API necesita apagar los retrasos: comprueba el tope duro con una
 * veintena de intentos fallidos, y con la curva puesta esa comprobación
 * tardaría siete minutos en vez de dos segundos.
 *
 * **En producción se ignora.** Un retraso que se puede desactivar desde el
 * panel de despliegue no retrasa nada: bastaría con colar un número enorme para
 * dejar la fuerza bruta a velocidad completa.
 */
export function resolverRetrasoDesde(
  env: Record<string, string | undefined> = process.env,
): number {
  const bruto = env.ACCOUNT_SLOWDOWN_AFTER;
  if (!bruto) return RETRASO_DESDE;
  if (env.NODE_ENV === 'production') return RETRASO_DESDE;

  const valor = Number(bruto);
  return Number.isInteger(valor) && valor > 0 ? valor : RETRASO_DESDE;
}

/** Techo del retraso, en milisegundos. */
export const RETRASO_MAXIMO_MS = 30_000;

/**
 * Cuánto se retrasa la respuesta según los intentos fallidos acumulados.
 *
 * Duplicando: 1 s, 2 s, 4 s, 8 s, 16 s y tope en 30 s.
 *
 * **Toda la defensa está en la asimetría de esa curva.** Quien conoce su
 * contraseña acierta al primer o segundo intento y no llega a notar nada; quien
 * se equivoca de verdad falla tres o cuatro veces y espera un segundo. Quien
 * prueba a ciegas necesita miles de intentos, y a treinta segundos cada uno
 * pasa de miles por minuto a ciento veinte por hora. La fuerza bruta deja de
 * ser viable sin que nadie quede bloqueado.
 *
 * Se extrae como función pura para poder probar la curva entera sin esperar
 * medio minuto por caso. Es la parte que de verdad hay que fijar con tests: si
 * la progresión se rompe —por ejemplo devolviendo siempre cero—, el middleware
 * sigue montado y ya no defiende de nada.
 */
export function calcularRetraso(intentos: number, desde: number = RETRASO_DESDE): number {
  const exceso = intentos - desde;
  if (exceso <= 0) return 0;
  return Math.min(2 ** (exceso - 1) * 1000, RETRASO_MAXIMO_MS);
}

/**
 * Retrasos progresivos por cuenta.
 *
 * **Por qué retrasar en vez de denegar.** El limitador duro de arriba resuelve
 * el ataque repartido entre muchas direcciones, pero introduce uno nuevo: si
 * bloquear es posible, alguien puede provocarlo aposta contra una cuenta ajena.
 * Afinar el umbral no lo arregla, porque siempre existe un número de intentos
 * que deja fuera a alguien. Lo que lo arregla es cambiar el castigo: un retraso
 * no tiene estado «bloqueado» que forzar.
 *
 * Comparte `claveDeCuenta` con el limitador duro, así que ambos cuentan lo
 * mismo: intentos contra un nombre de usuario, vengan de donde vengan.
 *
 * `skipSuccessfulRequests` hace que solo cuenten los fallos. Un usuario que
 * entra a la primera no acumula nada aunque lo haga cien veces al día.
 */
/**
 * El retraso que aplica el middleware, con el umbral ya resuelto del entorno.
 *
 * Con nombre y exportada en vez de una lambda dentro de la configuración, para
 * que se pueda probar. Una lambda anónima ahí dentro solo la ejecuta la
 * librería en tiempo de petición, así que ningún test unitario la alcanza — y
 * es la línea que decide cuánto se retrasa cada intento.
 */
export function retrasoDelMiddleware(usados: number): number {
  return calcularRetraso(usados, resolverRetrasoDesde());
}

export const accountSlowDown = slowDown({
  windowMs: 15 * 60 * 1000,
  delayAfter: resolverRetrasoDesde(),
  delayMs: retrasoDelMiddleware,
  maxDelayMs: RETRASO_MAXIMO_MS,
  keyGenerator: claveDeCuenta,
  skipSuccessfulRequests: true,
  validate: { delayMs: false },
});
