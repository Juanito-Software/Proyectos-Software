/**
 * Réplica en el cliente de la política de contraseñas.
 *
 * **La autoridad es `server/src/modules/auth/password-policy.ts`.** Lo de aquí
 * existe solo para avisar antes de enviar el formulario; el servidor vuelve a
 * validar siempre, porque cualquiera puede llamar a POST /api/auth/register
 * saltándose el navegador entero.
 *
 * Está duplicado y no compartido porque cliente y servidor son paquetes npm
 * distintos, sin un módulo común entre ellos. **Si cambia allí, hay que
 * cambiarlo aquí.** Un test end-to-end registra un usuario contra la API real,
 * así que una desincronización rompe el CI en lugar de pasar desapercibida.
 *
 * Se replican la longitud y la composición, que son las que el usuario puede
 * corregir mientras escribe. La lista de bloqueo y la comprobación del nombre
 * de usuario se dejan para el servidor: no aportan nada en el formulario y
 * mantenerlas sincronizadas sería una fuente de errores.
 */

export const MIN_PASSWORD_LENGTH = 15;
export const MAX_PASSWORD_BYTES = 72;
export const MAX_PASSWORD_LENGTH = MAX_PASSWORD_BYTES;

/**
 * Mismas clases Unicode que el servidor, por los mismos motivos: `\p{Lu}`
 * acepta `Á` y `Ñ` como mayúsculas, y un símbolo es cualquier cosa que no sea
 * letra, dígito ni espacio. El espacio queda fuera a propósito, para que una
 * frase con espacios no cumpla el requisito de símbolo sin tener ninguno.
 */
const TIENE_MAYUSCULA = /\p{Lu}/u;
const TIENE_DIGITO = /[0-9]/;
const TIENE_SIMBOLO = /[^\p{L}\p{N}\s]/u;

/**
 * `pattern` de HTML equivalente a las tres reglas de composición.
 *
 * Tres adelantos (lookahead) encadenados y luego `.*` para el resto. Va sin las
 * anclas `^` y `$` porque el navegador ya ancla el valor completo por su cuenta,
 * y con la bandera `u` implícita del atributo. El punto no casa con saltos de
 * línea, pero un `input type="password"` no admite ninguno.
 *
 * La longitud NO va aquí: la cubre `minLength`, que da un mensaje del navegador
 * mucho más claro que el genérico de un patrón incumplido.
 */
export const PASSWORD_PATTERN = '(?=.*\\p{Lu})(?=.*[0-9])(?=.*[^\\p{L}\\p{N}\\s]).*';

/** Los requisitos tal y como se le muestran al usuario. */
export const REQUISITOS_PASSWORD = [
  `Al menos ${MIN_PASSWORD_LENGTH} caracteres`,
  'Al menos una letra mayúscula',
  'Al menos un número',
  'Al menos un símbolo',
];

/**
 * Qué requisitos cumple ya una contraseña, para poder marcarlos en la interfaz
 * según se escribe.
 */
export function estadoRequisitos(password = '') {
  return {
    longitud: password.length >= MIN_PASSWORD_LENGTH,
    mayuscula: TIENE_MAYUSCULA.test(password),
    digito: TIENE_DIGITO.test(password),
    simbolo: TIENE_SIMBOLO.test(password),
  };
}

/**
 * Devuelve el primer error de la contraseña, o `null` si pasa.
 *
 * El orden coincide con el del servidor para que el usuario no reciba un aviso
 * en el formulario y otro distinto de la API para el mismo problema.
 */
export function validarPasswordCliente(password) {
  if (!password) return 'La contraseña es obligatoria';

  if (password.length < MIN_PASSWORD_LENGTH) {
    return `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres`;
  }

  // En bytes, igual que el servidor: bcrypt cuenta bytes y los acentos ocupan
  // dos. TextEncoder es la forma de contarlos en el navegador.
  if (new TextEncoder().encode(password).length > MAX_PASSWORD_BYTES) {
    return `La contraseña no puede superar los ${MAX_PASSWORD_BYTES} bytes`;
  }

  const estado = estadoRequisitos(password);
  if (!estado.mayuscula) return 'La contraseña debe incluir al menos una letra mayúscula';
  if (!estado.digito) return 'La contraseña debe incluir al menos un número';
  if (!estado.simbolo) return 'La contraseña debe incluir al menos un símbolo';

  return null;
}
