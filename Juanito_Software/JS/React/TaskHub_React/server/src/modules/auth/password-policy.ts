/**
 * Política de contraseñas de TaskHub.
 *
 * Sigue NIST SP 800-63B Revisión 4 (julio de 2025). Todo lo que viene de la
 * norma está marcado como tal; lo que es decisión propia del proyecto está
 * marcado como decisión de TaskHub, para no atribuir a NIST criterios que no
 * son suyos.
 *
 * ── Longitud mínima: 15 ─────────────────────────────────────────────── NIST
 * La Revisión 4 exige 15 caracteres cuando la contraseña es el único factor de
 * autenticación, y permite bajar a 8 solo si hay un segundo factor. TaskHub no
 * tiene MFA, así que le corresponden los 15.
 *
 * ── Sin reglas de composición ───────────────────────────────────────── NIST
 * La Revisión 4 **prohíbe** exigir mezclas de mayúsculas, números o símbolos
 * (en revisiones anteriores solo lo desaconsejaba). El motivo es conocido: esas
 * reglas producen contraseñas predecibles como "Password1!" o "Verano2026!",
 * que un atacante prueba de las primeras. Una frase larga sin un solo símbolo
 * es mucho más resistente.
 *
 * ── Se permite cualquier carácter, espacios incluidos ───────────────── NIST
 * La norma pide aceptar todos los caracteres imprimibles y el espacio, para no
 * estorbar a quien usa frases de paso o un gestor de contraseñas.
 *
 * ── Lista de bloqueo ────────────────────────────────────────────────── NIST
 * La norma exige comparar la contraseña contra una lista de las comprometidas
 * o predecibles. Cómo se construye esa lista es decisión de cada sistema.
 *
 * ── Máximo de 72 ─────────────────────────── límite técnico, no requisito NIST
 * bcrypt solo tiene en cuenta los primeros 72 bytes. Aceptar contraseñas más
 * largas sería engañoso: la parte sobrante no protegería nada. NIST pide
 * admitir al menos 64, así que 72 cumple con margen. Se **rechaza** lo que pase
 * de ahí en lugar de recortarlo en silencio, que es lo que exige la norma.
 */

export const MIN_PASSWORD_LENGTH = 15;
export const MAX_PASSWORD_LENGTH = 72;

/**
 * Contraseñas y patrones que no se aceptan aunque cumplan la longitud.
 *
 * **Decisión de TaskHub:** lista corta y embebida en el código, en lugar de un
 * servicio externo tipo Have I Been Pwned. NIST pide comprobar contra
 * contraseñas comprometidas, pero para un proyecto de este tamaño una consulta
 * externa en cada registro añade una dependencia de red, latencia y un punto de
 * fallo desproporcionados. Esta lista cubre lo que de verdad aparece primero en
 * un ataque por diccionario contra este tipo de aplicación.
 *
 * Queda anotado como mejora futura conectar una fuente real de credenciales
 * filtradas si el proyecto llegara a tener usuarios de verdad.
 */
const BLOQUEADAS = [
  // Las más habituales que además llegan a 15 caracteres
  'password123456',
  'passwordpassword',
  '123456789012345',
  '111111111111111',
  'qwertyuiopasdfg',
  'administrador123',
  'contrasenasegura',
  'contraseñasegura',
  'iloveyouforever',
  'letmeinletmein',
  // Relacionadas con el propio producto: son lo primero que se prueba
  'taskhubtaskhub',
  'taskhub123456789',
  'taskhubpassword',
];

/** Un solo carácter repetido: "aaaaaaaaaaaaaaa" cumple longitud pero no aporta nada. */
function esUnCaracterRepetido(valor: string): boolean {
  return valor.length > 0 && new Set(valor.toLowerCase()).size === 1;
}

/** Secuencias de teclado o numéricas: "123456789012345", "abcdefghijklmno". */
function esSecuencia(valor: string): boolean {
  const v = valor.toLowerCase();
  const secuencias = 'abcdefghijklmnopqrstuvwxyz0123456789qwertyuiopasdfghjklzxcvbnm';
  for (let i = 0; i + v.length <= secuencias.length; i++) {
    if (secuencias.slice(i, i + v.length) === v) return true;
  }
  return false;
}

export interface ResultadoPolitica {
  valida: boolean;
  error?: string;
}

/**
 * Comprueba una contraseña contra la política.
 *
 * Es la única fuente de verdad: la usan el registro y la semilla del
 * administrador. El formulario del cliente replica la longitud para dar aviso
 * antes de enviar, pero quien decide es esta función.
 */
export function validarPassword(password: unknown, username?: string): ResultadoPolitica {
  if (typeof password !== 'string' || !password) {
    return { valida: false, error: 'La contraseña es obligatoria' };
  }

  if (password.length < MIN_PASSWORD_LENGTH) {
    return {
      valida: false,
      error:
        `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres. ` +
        'Una frase fácil de recordar funciona mejor que una palabra corta con símbolos.',
    };
  }

  if (password.length > MAX_PASSWORD_LENGTH) {
    return {
      valida: false,
      error: `La contraseña no puede superar los ${MAX_PASSWORD_LENGTH} caracteres`,
    };
  }

  const normalizada = password.toLowerCase().replace(/\s+/g, '');

  if (BLOQUEADAS.includes(normalizada)) {
    return { valida: false, error: 'Esa contraseña es demasiado común. Elige otra.' };
  }

  if (esUnCaracterRepetido(normalizada)) {
    return { valida: false, error: 'La contraseña no puede ser un mismo carácter repetido' };
  }

  if (esSecuencia(normalizada)) {
    return { valida: false, error: 'La contraseña no puede ser una secuencia de teclado' };
  }

  // Que la contraseña contenga el nombre de usuario es de los primeros
  // intentos de cualquier ataque dirigido.
  //
  // El umbral es de 4 caracteres y no de 3 por los falsos positivos: con un
  // usuario "ana", buscar esa secuencia rechazaría frases legítimas que
  // contengan "semana", "mañana" o "ventana". A partir de cuatro letras la
  // coincidencia deja de ser casual.
  const MIN_USERNAME_PARA_COMPARAR = 4;

  if (
    username &&
    username.length >= MIN_USERNAME_PARA_COMPARAR &&
    normalizada.includes(username.toLowerCase())
  ) {
    return { valida: false, error: 'La contraseña no puede contener tu nombre de usuario' };
  }

  return { valida: true };
}
