/**
 * Política de contraseñas de TaskHub.
 *
 * Este archivo distingue de forma deliberada dos cosas que suelen mezclarse:
 * lo que recomienda NIST SP 800-63B Revisión 4 (julio de 2025) y lo que TaskHub
 * decide por su cuenta. Atribuir a la norma un criterio que no es suyo sería
 * incorrecto, así que cada regla va marcada con su origen.
 *
 * ══ Alineado con NIST ═══════════════════════════════════════════════════════
 *
 * ── La longitud es lo que manda ─────────────────────────────────────── NIST
 * La Revisión 4 exige 15 caracteres cuando la contraseña es el único factor de
 * autenticación, y permite bajar a 8 solo si hay un segundo factor. TaskHub no
 * tiene MFA, así que le corresponden los 15.
 *
 * ── Se permiten contraseñas largas ──────────────────────────────────── NIST
 * La norma pide admitir al menos 64 caracteres. Aquí el tope son 72 bytes, por
 * el motivo técnico que se explica abajo.
 *
 * ── Se acepta cualquier carácter, espacios incluidos ─────────────────── NIST
 * Todos los caracteres imprimibles y el espacio, para no estorbar a quien usa
 * frases de paso o un gestor de contraseñas.
 *
 * ── No se trunca nunca en silencio ──────────────────────────────────── NIST
 * Lo que no cabe se rechaza con un mensaje, no se recorta por detrás.
 *
 * ── Lista de bloqueo ────────────────────────────────────────────────── NIST
 * La norma exige comparar contra contraseñas comprometidas o predecibles. Cómo
 * se construya esa lista es decisión de cada sistema.
 *
 * ── Almacenamiento con hash ─────────────────────────────────────────── NIST
 * bcrypt con sal, en users.password_hash. Nunca se guarda el texto plano.
 *
 * ══ Decisiones propias de TaskHub ═══════════════════════════════════════════
 *
 * ── Composición obligatoria ─────────────────────── decisión de TaskHub
 * Se exige al menos una mayúscula, un dígito y un símbolo.
 *
 * Esto es MÁS RESTRICTIVO que NIST, y conviene ser explícito: la Revisión 4 no
 * se limita a desaconsejar las reglas de composición, sino que dice que los
 * verificadores NO DEBEN imponerlas. TaskHub las aplica igualmente como
 * requisito de producto, asumiendo el efecto secundario conocido: obligar a
 * mezclar tipos de carácter empuja a la gente hacia formas predecibles como
 * "Password123!" o "Verano2026!".
 *
 * Ese efecto secundario no se ignora, se compensa: la lista de bloqueo de más
 * abajo cubre precisamente los patrones que esta regla fomenta (ver
 * `esPatronPredecible`). Sin esa contrapartida, la composición obligatoria
 * empeoraría la seguridad en lugar de mejorarla.
 *
 * ── Máximo de 72 bytes ──────────── límite técnico, no requisito de NIST
 * bcrypt solo tiene en cuenta los primeros 72 bytes de la entrada; lo que pase
 * de ahí no interviene en el hash. Aceptar contraseñas más largas daría una
 * falsa sensación de seguridad, así que se rechazan.
 *
 * Se miden BYTES y no caracteres a propósito. `"ñ"` ocupa un carácter pero dos
 * bytes en UTF-8, así que una contraseña de 72 caracteres acentuados pasaría de
 * los 72 bytes y bcrypt la truncaría sin avisar — exactamente lo que la norma
 * prohíbe. Contar `.length` habría dejado ese caso pasar.
 *
 * ── Lista de bloqueo embebida ─────────────────────── decisión de TaskHub
 * En vez de consultar un servicio de credenciales filtradas tipo Have I Been
 * Pwned. Para un proyecto de este tamaño, una llamada de red en cada registro
 * añade latencia, una dependencia externa y un punto de fallo desproporcionados.
 *
 * ── Umbral de 4 caracteres para el nombre de usuario ─ decisión de TaskHub
 * Explicado junto a la comprobación correspondiente.
 */

export const MIN_PASSWORD_LENGTH = 15;

/**
 * Tope en BYTES, no en caracteres. Ver la nota sobre bcrypt en la cabecera.
 */
export const MAX_PASSWORD_BYTES = 72;

/**
 * Alias en caracteres para el atributo `maxLength` del formulario, donde no se
 * pueden contar bytes. Es un límite superior seguro: 72 caracteres nunca son
 * menos de 72 bytes, así que el formulario jamás deja escribir algo que el
 * servidor fuera a aceptar y el navegador hubiera cortado.
 */
export const MAX_PASSWORD_LENGTH = MAX_PASSWORD_BYTES;

/**
 * Contraseñas que no se aceptan aunque cumplan longitud y composición.
 *
 * Se comparan en minúsculas y sin espacios.
 */
const BLOQUEADAS = [
  // Habituales que además llegan a 15 caracteres
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

/**
 * Palabras base que, adornadas con dígitos y símbolos, producen justo las
 * contraseñas que la regla de composición empuja a elegir.
 *
 * **Decisión de TaskHub, y es la contrapartida de exigir composición.** Sin
 * esta comprobación, `Password123456!` cumpliría los 15 caracteres, la
 * mayúscula, el dígito y el símbolo, y sería una de las primeras que probaría
 * cualquier ataque por diccionario. La regla de composición sin esta lista
 * dejaría la aplicación peor de lo que estaba.
 */
const BASES_PREDECIBLES = [
  'password',
  'passwort',
  'contrasena',
  'contraseña',
  'taskhub',
  'admin',
  'administrador',
  'usuario',
  'qwerty',
  'welcome',
  'bienvenido',
  'verano',
  'invierno',
  'primavera',
  'otono',
  'otoño',
  'enero',
  'febrero',
  'marzo',
  'abril',
  'mayo',
  'junio',
  'julio',
  'agosto',
  'septiembre',
  'octubre',
  'noviembre',
  'diciembre',
  'madrid',
  'barcelona',
  'santander',
  'iloveyou',
  'letmein',
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

/**
 * Sustituciones de estilo «leet»: la otra forma habitual de cumplir la regla de
 * composición sin cambiar de contraseña. `P@ssw0rd` es la misma palabra que
 * `password` para cualquier diccionario de ataque, que las prueba de serie.
 */
const SUSTITUCIONES_LEET: Record<string, string> = {
  '@': 'a',
  '4': 'a',
  '0': 'o',
  '1': 'i',
  '!': 'i',
  '3': 'e',
  '5': 's',
  $: 's',
  '7': 't',
  '+': 't',
  '8': 'b',
};

function deshacerLeet(valor: string): string {
  return valor.replace(/[@40!13$57+8]/g, (c) => SUSTITUCIONES_LEET[c] ?? c);
}

/**
 * Formas en que una contraseña puede reducirse a una palabra común.
 *
 * Hay que probar varias porque el relleno y la sustitución se estorban entre
 * sí. En `P@ssword2026!!!` la `@` es una sustitución que hay que deshacer,
 * mientras que el `2026!!!` es relleno que hay que tirar; aplicar solo una de
 * las dos operaciones no llega a `password` por ninguno de los dos caminos.
 *
 * Así que se generan cuatro candidatos —con y sin relleno, con y sin leet— y
 * basta con que uno coincida.
 */
function formasNormalizadas(valor: string): string[] {
  const soloLetras = (v: string) => v.toLowerCase().replace(/[^\p{L}]/gu, '');

  // Relleno = lo que no son letras al principio y al final: "2026Password!!"
  const sinRelleno = valor.replace(/^[^\p{L}]+/u, '').replace(/[^\p{L}]+$/u, '');

  const candidatos = new Set<string>();
  for (const base of [valor, sinRelleno]) {
    candidatos.add(soloLetras(base));
    candidatos.add(soloLetras(deshacerLeet(base)));
  }

  return [...candidatos].filter(Boolean);
}

/**
 * Detecta el patrón «palabra común + adornos para cumplir la composición».
 *
 * Caen `Password123456!`, `P@ssword2026!!!`, `Taskhub-2026!!` o
 * `Verano_2026_2026`. Una frase de paso normal no se ve afectada, porque al
 * quitarle los adornos siguen quedando varias palabras pegadas y la
 * comparación exige que quede exactamente una de la lista, o esa misma
 * repetida ("adminadminadmin").
 */
function esPatronPredecible(valor: string): boolean {
  const formas = formasNormalizadas(valor);

  return formas.some((forma) =>
    BASES_PREDECIBLES.some((base) => {
      if (forma === base) return true;
      // La misma palabra repetida hasta llegar a la longitud.
      if (forma.length % base.length !== 0) return false;
      return forma === base.repeat(forma.length / base.length);
    }),
  );
}

/**
 * Las tres comprobaciones de composición.
 *
 * Se definen con clases Unicode y no con `[A-Z]` / `[!@#...]` para no producir
 * falsos negativos:
 *
 * - Mayúscula: `\p{Lu}` acepta también `Á`, `Ñ` o `Ü`, que son mayúsculas
 *   perfectamente válidas y que un `[A-Z]` habría rechazado.
 * - Símbolo: cualquier carácter que no sea letra, ni dígito, ni espacio. Cubre
 *   `! @ # $ % ^ & * ( ) _ - + = [ ] { } ; : ' " , . / ?` y además `¿ ¡ € · «`,
 *   sin tener que mantener una lista a mano.
 *
 * El espacio se excluye del conjunto de símbolos a propósito: si contara, una
 * frase como "caballo correcto grapa pila" cumpliría el requisito solo por
 * llevar espacios, y la regla no estaría comprobando nada.
 */
const TIENE_MAYUSCULA = /\p{Lu}/u;
const TIENE_DIGITO = /[0-9]/;
const TIENE_SIMBOLO = /[^\p{L}\p{N}\s]/u;

export interface ResultadoPolitica {
  valida: boolean;
  error?: string;
}

/**
 * Comprueba una contraseña contra la política.
 *
 * Es la única fuente de verdad: la usan el registro y la semilla del
 * administrador. El formulario del cliente replica las reglas para avisar antes
 * de enviar, pero quien decide es esta función — un atacante puede saltarse el
 * formulario y llamar directamente a POST /api/auth/register.
 *
 * El orden de las comprobaciones está elegido para que el mensaje sea el más
 * útil de los que apliquen: la lista de bloqueo va ANTES que la composición,
 * porque a quien escribe "passwordpassword" le sirve más saber que es una
 * contraseña común que saber que le falta una mayúscula.
 */
export function validarPassword(password: unknown, username?: string): ResultadoPolitica {
  if (typeof password !== 'string' || !password) {
    return { valida: false, error: 'La contraseña es obligatoria' };
  }

  if (password.length < MIN_PASSWORD_LENGTH) {
    return {
      valida: false,
      error: `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres`,
    };
  }

  // En bytes, no en caracteres: bcrypt cuenta bytes y truncaría el resto.
  if (Buffer.byteLength(password, 'utf8') > MAX_PASSWORD_BYTES) {
    return {
      valida: false,
      error:
        `La contraseña no puede superar los ${MAX_PASSWORD_BYTES} bytes. ` +
        'Los acentos y las eñes ocupan dos, así que el límite en caracteres puede ser algo menor.',
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

  if (esPatronPredecible(normalizada)) {
    return {
      valida: false,
      error:
        'Esa contraseña sigue un patrón demasiado previsible: una palabra común con números ' +
        'y símbolos alrededor. Es de lo primero que prueba un ataque por diccionario.',
    };
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

  // ── Composición: requisito propio de TaskHub, más estricto que NIST ──────

  if (!TIENE_MAYUSCULA.test(password)) {
    return { valida: false, error: 'La contraseña debe incluir al menos una letra mayúscula' };
  }

  if (!TIENE_DIGITO.test(password)) {
    return { valida: false, error: 'La contraseña debe incluir al menos un número' };
  }

  if (!TIENE_SIMBOLO.test(password)) {
    return {
      valida: false,
      error:
        'La contraseña debe incluir al menos un símbolo, por ejemplo ! ? # $ % & * - _ + = . ,' +
        ' (el espacio no cuenta como símbolo)',
    };
  }

  return { valida: true };
}

/**
 * Los requisitos en texto, para que el formulario y los mensajes de error no se
 * inventen su propia redacción ni se desincronicen de lo que aplica el
 * servidor.
 */
export const REQUISITOS_PASSWORD = [
  `Al menos ${MIN_PASSWORD_LENGTH} caracteres`,
  'Al menos una letra mayúscula',
  'Al menos un número',
  'Al menos un símbolo',
] as const;
