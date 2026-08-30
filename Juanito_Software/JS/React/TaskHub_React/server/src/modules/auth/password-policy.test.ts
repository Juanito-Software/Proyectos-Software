import { describe, it, expect } from 'vitest';
import { validarPassword, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH } from './password-policy.js';

/**
 * La política sigue NIST SP 800-63B Rev 4: manda la longitud y **no** se
 * exigen mezclas de mayúsculas, números ni símbolos.
 *
 * Varios de estos tests existen precisamente para impedir que alguien
 * reintroduzca reglas de composición más adelante: si se añadieran, estos
 * fallarían.
 */

describe('longitud', () => {
  it(`rechaza por debajo de ${MIN_PASSWORD_LENGTH} caracteres`, () => {
    // 14 caracteres variados: el único motivo de rechazo debe ser la longitud.
    const catorce = 'melon y sandia';
    expect(catorce).toHaveLength(MIN_PASSWORD_LENGTH - 1);

    const r = validarPassword(catorce);
    expect(r.valida).toBe(false);
    expect(r.error).toContain(String(MIN_PASSWORD_LENGTH));
  });

  it(`acepta justo en el límite de ${MIN_PASSWORD_LENGTH}`, () => {
    expect(validarPassword('correo verde 12').valida).toBe(true);
  });

  it('acepta contraseñas mucho más largas', () => {
    const larga = 'una frase larga de paso que recuerdo sin esfuerzo';
    expect(larga.length).toBeGreaterThan(MIN_PASSWORD_LENGTH);
    expect(validarPassword(larga).valida).toBe(true);
  });

  it(`rechaza por encima de ${MAX_PASSWORD_LENGTH}, sin recortar en silencio`, () => {
    // bcrypt ignora lo que pase de 72 bytes: aceptarla daría una falsa
    // sensación de seguridad. NIST exige rechazar, no truncar.
    const r = validarPassword('x'.repeat(MAX_PASSWORD_LENGTH + 1));
    expect(r.valida).toBe(false);
    expect(r.error).toContain(String(MAX_PASSWORD_LENGTH));
  });

  it(`acepta justo en el límite de ${MAX_PASSWORD_LENGTH}`, () => {
    const enElLimite = 'la frase mas larga que cabe aqui sin pasarse del limite tecnico de bc';
    expect(enElLimite.length).toBeLessThanOrEqual(MAX_PASSWORD_LENGTH);
    expect(validarPassword(enElLimite).valida).toBe(true);
  });
});

describe('sin reglas de composición (NIST Rev 4)', () => {
  // El corazón de la política: estas contraseñas serían rechazadas por
  // cualquier sistema que exija "una mayúscula, un número y un símbolo", y
  // aquí deben pasar.

  it('acepta una frase solo en minúsculas, sin números ni símbolos', () => {
    expect(validarPassword('caballo correcto grapa pila').valida).toBe(true);
  });

  it('acepta una frase con acentos y eñes', () => {
    expect(validarPassword('el niño pequeño canta bien').valida).toBe(true);
  });

  it('acepta una contraseña compleja al estilo tradicional', () => {
    // No se prohíbe la composición: simplemente no se obliga.
    expect(validarPassword('P4ssw0rd!Segura#2026').valida).toBe(true);
  });

  it('acepta solo dígitos si la longitud es suficiente y no es secuencia', () => {
    expect(validarPassword('849205718360492').valida).toBe(true);
  });

  it('acepta espacios, que NIST exige permitir', () => {
    expect(validarPassword('con muchos espacios aqui').valida).toBe(true);
  });

  it('NO rechaza por faltar mayúsculas', () => {
    expect(validarPassword('todo en minusculas hoy').valida).toBe(true);
  });

  it('NO rechaza por faltar números', () => {
    expect(validarPassword('sin ningun numero dentro').valida).toBe(true);
  });

  it('NO rechaza por faltar símbolos', () => {
    expect(validarPassword('ningun simbolo por aqui').valida).toBe(true);
  });
});

describe('lista de bloqueo', () => {
  it('rechaza una contraseña común aunque tenga longitud suficiente', () => {
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
    const r = validarPassword('juanito y su contraseña', 'juanito');
    expect(r.valida).toBe(false);
    expect(r.error).toMatch(/nombre de usuario/i);
  });

  it('no compara con nombres de usuario de menos de 4 caracteres', () => {
    // Con un usuario "ana", buscar esa secuencia rechazaría frases legítimas
    // que contengan "semana", "mañana" o "ventana". El umbral evita ese falso
    // positivo, que apareció al escribir este mismo test.
    expect(validarPassword('la semana que viene ya', 'ana').valida).toBe(true);
  });

  it('sí compara a partir de 4 caracteres', () => {
    expect(validarPassword('mi usuario es juan aqui', 'juan').valida).toBe(false);
  });
});

describe('entradas inválidas', () => {
  it.each([
    ['indefinida', undefined],
    ['nula', null],
    ['numérica', 123456789012345],
    ['vacía', ''],
  ])('rechaza una contraseña %s sin lanzar excepción', (_caso, valor) => {
    expect(() => validarPassword(valor)).not.toThrow();
    expect(validarPassword(valor).valida).toBe(false);
  });
});
