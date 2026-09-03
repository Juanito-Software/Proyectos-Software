/**
 * Registro de eventos de seguridad.
 *
 * Antes de esto, el único evento que dejaba rastro era la detección de
 * reutilización de un token de refresco. Todo lo demás —quién entra, quién
 * falla al entrar, quién cierra sesión, a quién se le revoca— ocurría en
 * silencio. Con eso, un ataque de fuerza bruta contra una cuenta concreta es
 * invisible: lo único que quedaría en el registro son unos cuantos 401 y 429
 * mezclados con el tráfico normal, sin nada que los relacione.
 *
 * ── Qué se registra y qué NO ────────────────────────────────────────────────
 *
 * La regla es sencilla y no admite excepciones: **se registra lo que pasó,
 * nunca con qué**. Ni contraseñas, ni tokens de acceso, ni de refresco, ni
 * hashes. Un registro que filtra credenciales es peor que no tener registro,
 * porque además da una falsa sensación de control — y ya pasó una vez en este
 * proyecto: la suite de API volcaba la cabecera `Set-Cookie` entera, con el
 * token de refresco dentro, en la salida del CI.
 *
 * El nombre de usuario sí se registra, y es deliberado: sin él no se puede
 * saber qué cuenta está siendo atacada, que es justo para lo que sirve esto.
 *
 * ── Formato ────────────────────────────────────────────────────────────────
 *
 * Una línea JSON por evento. Render y la mayoría de recolectores saben leer
 * JSON por línea, así que se puede filtrar por `evento` o por `usuario` sin
 * escribir una expresión regular. Va por `console.warn` para que quede en el
 * flujo de errores y no se pierda entre el registro de peticiones.
 */

export type EventoSeguridad =
  | 'login.correcto'
  | 'login.fallido'
  | 'registro.correcto'
  | 'logout'
  | 'logout.global'
  | 'refresh.correcto'
  | 'refresh.rechazado'
  | 'refresh.reutilizacion'
  | 'autorizacion.denegada'
  | 'cuenta.borrada';

interface DatosEvento {
  /** Nombre de usuario, si se conoce. En un login fallido es lo que se intentó. */
  usuario?: string;
  /** Identificador del usuario, cuando existe. */
  userId?: string;
  /** Motivo, en términos de negocio: 'credenciales-invalidas', 'token-gastado'… */
  motivo?: string;
  /** Dirección de origen, para poder distinguir un ataque distribuido. */
  ip?: string;
  /** Cualquier dato adicional NO sensible: recuentos, identificadores de familia. */
  [clave: string]: unknown;
}

/**
 * Claves que nunca deben salir en un registro, por mucho que alguien las pase
 * por descuido al añadir un evento nuevo.
 *
 * Es una red de seguridad, no la defensa principal: la defensa es no pasarlas.
 * Pero un despiste aquí cuesta una credencial en un fichero de texto, así que
 * la red compensa.
 */
const PROHIBIDAS = /password|token|secret|cookie|hash|authorization/i;

/**
 * Solo se censuran los valores de **texto**.
 *
 * La primera versión tapaba cualquier clave que casara con el patrón, y con eso
 * `tokensRevocados: 3` salía como `<censurado>` — un contador, no una
 * credencial. Lo detectó su propio test.
 *
 * La regla que separa una cosa de otra es simple y aguanta: una credencial
 * siempre es una cadena. Un recuento, una marca de tiempo o un booleano no
 * pueden serlo, así que se dejan pasar aunque la clave se llame
 * `tokensRevocados` o `gastadoHaceSegundos`.
 */
function esSospechoso(clave: string, valor: unknown): boolean {
  return typeof valor === 'string' && PROHIBIDAS.test(clave);
}

export function registrarEventoSeguridad(evento: EventoSeguridad, datos: DatosEvento = {}): void {
  const limpio: Record<string, unknown> = {};

  for (const [clave, valor] of Object.entries(datos)) {
    if (esSospechoso(clave, valor)) {
      limpio[clave] = '<censurado>';
      continue;
    }
    if (valor !== undefined) limpio[clave] = valor;
  }

  console.warn(
    JSON.stringify({
      tipo: 'seguridad',
      evento,
      momento: new Date().toISOString(),
      ...limpio,
    }),
  );
}
