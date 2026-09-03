import { describe, it, expect } from 'vitest';
import {
  validarPassword,
  MIN_PASSWORD_LENGTH,
  MAX_PASSWORD_BYTES,
  REQUISITOS_PASSWORD,
} from './password-policy.js';

/**
 * La política combina dos cosas de origen distinto, y los tests están agrupados
 * igual para que se vea cuál es cuál:
 *
 * - De NIST SP 800-63B Rev 4: longitud mínima de 15, admitir contraseñas
 *   largas, aceptar cualquier carácter incluido el espacio, no truncar y
 *   comparar contra una lista de bloqueo.
 * - Decisión propia de TaskHub: exigir mayúscula, dígito y símbolo. Esto es
 *   más restrictivo que la norma, que dice explícitamente que no deberían
 *   imponerse reglas de composición.
 *
 * Los tests del bloque de composición son los que fijan esa decisión propia.
 */

// Contraseña de referencia: cumple todo sin ser un galimatías.
const VALIDA = 'Cafe con leche y 2 tostadas!';

describe('longitud', () => {
  it(`rechaza por debajo de ${MIN_PASSWORD_LENGTH} caracteres`, () => {
    // 14 caracteres que sí cumplen mayúscula, dígito y símbolo: así el único
    // motivo posible de rechazo es la longitud.
    const catorce = 'Corto-Horse12!';
    expect(catorce).toHaveLength(MIN_PASSWORD_LENGTH - 1);

    const r = validarPassword(catorce);
    expect(r.valida).toBe(false);
    expect(r.error).toContain(String(MIN_PASSWORD_LENGTH));
  });

  it(`acepta justo en el límite de ${MIN_PASSWORD_LENGTH}`, () => {
    const quince = 'Correct-Horse2!';
    expect(quince).toHaveLength(MIN_PASSWORD_LENGTH);
    expect(validarPassword(quince).valida).toBe(true);
  });

  it('acepta contraseñas bastante más largas', () => {
    expect(VALIDA.length).toBeGreaterThan(MIN_PASSWORD_LENGTH);
    expect(validarPassword(VALIDA).valida).toBe(true);
  });

  it('acepta una contraseña larga de verdad, cerca del máximo', () => {
    const larga = 'Una frase larga de paso que recuerdo sin ningun esfuerzo 2026!';
    expect(larga.length).toBeGreaterThan(50);
    expect(Buffer.byteLength(larga, 'utf8')).toBeLessThanOrEqual(MAX_PASSWORD_BYTES);
    expect(validarPassword(larga).valida).toBe(true);
  });

  it(`rechaza por encima de ${MAX_PASSWORD_BYTES} bytes, sin recortar en silencio`, () => {
    // bcrypt ignora lo que pase de 72 bytes: aceptarla daría una falsa
    // sensación de seguridad. NIST exige rechazar, no truncar.
    const r = validarPassword('A1!' + 'x'.repeat(MAX_PASSWORD_BYTES));
    expect(r.valida).toBe(false);
    expect(r.error).toContain(String(MAX_PASSWORD_BYTES));
  });

  it('cuenta BYTES y no caracteres: los acentos ocupan dos', () => {
    // Este es el caso que se colaba cuando el límite se medía con .length.
    // 40 eñes son 40 caracteres pero 80 bytes en UTF-8, así que bcrypt habría
    // truncado la contraseña sin que nadie se enterara.
    const conEñes = 'Ñ1!' + 'ñ'.repeat(40);
    expect(conEñes.length).toBeLessThanOrEqual(MAX_PASSWORD_BYTES);
    expect(Buffer.byteLength(conEñes, 'utf8')).toBeGreaterThan(MAX_PASSWORD_BYTES);

    const r = validarPassword(conEñes);
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/bytes/i);
  });

  it('acepta justo en el límite de bytes', () => {
    const enElLimite = 'A1!' + 'x'.repeat(MAX_PASSWORD_BYTES - 3);
    expect(Buffer.byteLength(enElLimite, 'utf8')).toBe(MAX_PASSWORD_BYTES);
    expect(validarPassword(enElLimite).valida).toBe(true);
  });
});

describe('composición obligatoria (decisión de TaskHub, más estricta que NIST)', () => {
  // NIST Rev 4 dice que los verificadores NO DEBEN imponer reglas de
  // composición. TaskHub las impone igualmente como requisito de producto.
  // Estos tests fijan esa decisión: si alguien las quitara, fallarían.

  it('rechaza una contraseña sin mayúscula', () => {
    const r = validarPassword('correct-horse-2026!');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/mayúscula/i);
  });

  it('rechaza una contraseña sin número', () => {
    const r = validarPassword('Correct-Horse-Battery!');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/número/i);
  });

  it('rechaza una contraseña sin símbolo', () => {
    const r = validarPassword('Correct Horse Battery 2026');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/símbolo/i);
  });

  it('el espacio NO cuenta como símbolo', () => {
    // Si contara, cualquier frase con espacios cumpliría el requisito sin
    // llevar un solo símbolo, y la regla no comprobaría nada.
    const r = validarPassword('Frase Con Espacios 2026');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/símbolo/i);
  });

  it('rechaza cuando faltan varios requisitos a la vez', () => {
    // Ni mayúscula, ni número, ni símbolo. Basta con que devuelva un error.
    const r = validarPassword('caballo correcto grapa');
    expect(r.valida).toBe(false);
    expect(r.error).toBeTruthy();
  });

  it('rechaza cuando faltan longitud y composición a la vez', () => {
    expect(validarPassword('corta').valida).toBe(false);
  });

  it.each([
    ['exclamación', 'Melon con Jamon 7!'],
    ['interrogación', 'Melon con Jamon 7?'],
    ['almohadilla', 'Melon con Jamon 7#'],
    ['dólar', 'Melon con Jamon 7$'],
    ['porcentaje', 'Melon con Jamon 7%'],
    ['ampersand', 'Melon con Jamon 7&'],
    ['asterisco', 'Melon con Jamon 7*'],
    ['guion', 'Melon con Jamon 7-'],
    ['guion bajo', 'Melon con Jamon 7_'],
    ['más', 'Melon con Jamon 7+'],
    ['igual', 'Melon con Jamon 7='],
    ['paréntesis', 'Melon con Jamon (7)'],
    ['corchetes', 'Melon con Jamon [7]'],
    ['llaves', 'Melon con Jamon {7}'],
    ['punto y coma', 'Melon con Jamon 7;'],
    ['dos puntos', 'Melon con Jamon 7:'],
    ['comilla simple', "Melon con Jamon 7'"],
    ['comilla doble', 'Melon con Jamon 7"'],
    ['coma', 'Melon con Jamon 7,'],
    ['punto', 'Melon con Jamon 7.'],
    ['barra', 'Melon con Jamon 7/'],
    ['arroba', 'Melon con Jamon 7@'],
    ['circunflejo', 'Melon con Jamon 7^'],
    ['apertura de interrogación', 'Melon con Jamon 7¿'],
    ['euro', 'Melon con Jamon 7€'],
  ])('acepta %s como símbolo', (_caso, password) => {
    // El requisito es "un símbolo", no "un signo de exclamación". Restringir la
    // lista sería un falso negativo para quien usa un gestor de contraseñas.
    expect(validarPassword(password).valida).toBe(true);
  });

  it('acepta una mayúscula acentuada como mayúscula', () => {
    // \p{Lu} y no [A-Z]: "Á" es una mayúscula perfectamente válida y
    // rechazarla sería un falso negativo para cualquier hispanohablante.
    expect(validarPassword('Álvaro come pan 7!').valida).toBe(true);
  });

  it('acepta la Ñ mayúscula como mayúscula', () => {
    expect(validarPassword('Ñoño come pan a las 7!').valida).toBe(true);
  });
});

describe('contraseñas válidas', () => {
  it.each([
    ['de exactamente 15 caracteres', 'Correct-Horse2!'],
    ['por encima del mínimo', 'Correct-Horse-2026!'],
    ['larga', 'Cafe con leche y dos tostadas 7!'],
    ['con varias mayúsculas', 'CAFE con Leche y 2 Tostadas!'],
    ['con varios números', 'Cafe 12 con leche 34!'],
    ['con varios símbolos', 'Cafe!con#leche$y%2'],
    ['con espacios', 'Melon con Jamon y 7 panes!'],
    ['compleja al estilo tradicional', 'P4ss!w0rd#Distinta2026'],
    ['con todo mezclado', 'Zx9#Qw2!Lm4$Pk7&Rt1'],
  ])('acepta una contraseña %s', (_caso, password) => {
    const r = validarPassword(password);
    expect(r.error ?? '').toBe('');
    expect(r.valida).toBe(true);
  });
});

describe('lista de bloqueo', () => {
  it('rechaza una contraseña común antes que por composición', () => {
    // El orden importa: a quien escribe "passwordpassword" le sirve más saber
    // que es una contraseña común que saber que le falta una mayúscula.
    const r = validarPassword('passwordpassword');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/común/i);
  });

  it('la comparación ignora mayúsculas y espacios', () => {
    expect(validarPassword('Password Password').valida).toBe(false);
  });

  it('rechaza un único carácter repetido', () => {
    expect(validarPassword('aaaaaaaaaaaaaaaaaa').valida).toBe(false);
  });

  it('rechaza secuencias de teclado', () => {
    expect(validarPassword('abcdefghijklmnop').valida).toBe(false);
    expect(validarPassword('qwertyuiopasdfgh').valida).toBe(false);
  });

  it('rechaza que la contraseña contenga el nombre de usuario', () => {
    const r = validarPassword('Juanito y su clave 7!', 'juanito');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/nombre de usuario/i);
  });

  it('no compara con nombres de usuario de menos de 4 caracteres', () => {
    // Con un usuario "ana", buscar esa secuencia rechazaría frases legítimas
    // que contengan "semana", "mañana" o "ventana". El umbral evita ese falso
    // positivo, que apareció al escribir este mismo test.
    expect(validarPassword('La semana que viene 7!', 'ana').valida).toBe(true);
  });

  it('sí compara a partir de 4 caracteres', () => {
    expect(validarPassword('Mi usuario es juan 7!', 'juan').valida).toBe(false);
  });
});

describe('patrones que la propia regla de composición fomenta', () => {
  /**
   * Estos son la contrapartida de exigir mayúscula, dígito y símbolo.
   *
   * Todas las de aquí abajo cumplen los cuatro requisitos y aun así son
   * pésimas: son literalmente lo que produce alguien obligado a "añadir una
   * mayúscula, un número y un símbolo" a una palabra común. Sin esta
   * comprobación, la regla de composición empeoraría la seguridad en vez de
   * mejorarla, y estos tests son los que lo impiden.
   */

  it.each([
    ['Password123456!'],
    ['Password2026!!!'],
    ['P@ssword2026!!!'],
    ['Taskhub-2026!!!!'],
    ['Verano_2026_2026'],
    ['Admin-Admin-123!'],
    ['Bienvenido2026!'],
    ['Santander-2026!'],
  ])('rechaza %s aunque cumpla longitud y composición', (password) => {
    // Se comprueba primero que efectivamente cumple los cuatro requisitos:
    // si no, el test estaría pasando por el motivo equivocado.
    expect(password.length).toBeGreaterThanOrEqual(MIN_PASSWORD_LENGTH);
    expect(password).toMatch(/\p{Lu}/u);
    expect(password).toMatch(/[0-9]/);
    expect(password).toMatch(/[^\p{L}\p{N}\s]/u);

    expect(validarPassword(password).valida).toBe(false);
  });

  it('no confunde una frase normal con un patrón predecible', () => {
    // La comprobación mira si al quitar dígitos y símbolos queda exactamente
    // una palabra común. Una frase deja varias palabras pegadas, que no están
    // en la lista.
    expect(validarPassword('Melon con Jamon 7!').valida).toBe(true);
  });
});

describe('entradas inválidas', () => {
  it.each([
    ['indefinida', undefined],
    ['nula', null],
    ['numérica', 123456789012345],
    ['vacía', ''],
    ['booleana', true],
    ['un objeto', { password: 'Correct-Horse2!' }],
  ])('rechaza una contraseña %s sin lanzar excepción', (_caso, valor) => {
    expect(() => validarPassword(valor)).not.toThrow();
    expect(validarPassword(valor).valida).toBe(false);
  });

  it('la contraseña vacía da el mensaje de obligatoria, no el de longitud', () => {
    expect(validarPassword('').error).toMatch(/obligatoria/i);
  });
});

describe('requisitos publicados', () => {
  it('la lista de requisitos coincide con lo que aplica la función', () => {
    // Existe para que el formulario y los mensajes no se inventen su propia
    // redacción. Si se añade una regla y no se añade aquí, el usuario vería
    // una lista incompleta.
    expect(REQUISITOS_PASSWORD).toHaveLength(4);
    expect(REQUISITOS_PASSWORD[0]).toContain(String(MIN_PASSWORD_LENGTH));
    expect(REQUISITOS_PASSWORD.join(' ')).toMatch(/mayúscula/i);
    expect(REQUISITOS_PASSWORD.join(' ')).toMatch(/número/i);
    expect(REQUISITOS_PASSWORD.join(' ')).toMatch(/símbolo/i);
  });
});
