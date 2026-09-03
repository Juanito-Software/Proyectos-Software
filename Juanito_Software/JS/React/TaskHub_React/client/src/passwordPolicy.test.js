import { describe, it, expect } from 'vitest';
import {
  validarPasswordCliente,
  estadoRequisitos,
  PASSWORD_PATTERN,
  REQUISITOS_PASSWORD,
  MIN_PASSWORD_LENGTH,
  MAX_PASSWORD_BYTES,
} from './passwordPolicy';

/**
 * La copia de la política que vive en el cliente.
 *
 * Es solo experiencia de uso —el servidor vuelve a validar siempre—, pero si se
 * desincroniza el usuario recibe un aviso en el formulario y otro distinto de
 * la API para el mismo problema, que es peor que no avisar. De ahí que se
 * pruebe con el mismo detalle que la del servidor.
 */

const VALIDA = 'Cafe con leche y 2 tostadas!';

describe('validarPasswordCliente', () => {
  it('acepta una contraseña que cumple los cuatro requisitos', () => {
    expect(validarPasswordCliente(VALIDA)).toBeNull();
  });

  it('acepta exactamente en el mínimo', () => {
    const quince = 'Correct-Horse2!';
    expect(quince).toHaveLength(MIN_PASSWORD_LENGTH);
    expect(validarPasswordCliente(quince)).toBeNull();
  });

  it.each([
    ['vacía', '', /obligatoria/i],
    ['corta', 'Corto-Horse12!', /15/],
    ['sin mayúscula', 'cafe con leche y 2 tostadas!', /mayúscula/i],
    ['sin número', 'Cafe con leche y tostadas!', /número/i],
    ['sin símbolo', 'Cafe con leche y 2 tostadas', /símbolo/i],
  ])('rechaza una contraseña %s con el mensaje correspondiente', (_caso, password, mensaje) => {
    expect(validarPasswordCliente(password)).toMatch(mensaje);
  });

  it('avisa del primer problema en el mismo orden que el servidor', () => {
    // Le falta todo. Si el cliente empezara por la composición y el servidor
    // por la longitud, el usuario vería dos mensajes distintos para el mismo
    // fallo según se saltara o no el formulario.
    expect(validarPasswordCliente('corta')).toMatch(/15/);
  });

  it('cuenta bytes y no caracteres en el máximo', () => {
    // Los acentos ocupan dos bytes; bcrypt cuenta bytes y truncaría el resto.
    const conEñes = 'Ñ1!' + 'ñ'.repeat(40);
    expect(conEñes.length).toBeLessThanOrEqual(MAX_PASSWORD_BYTES);
    expect(validarPasswordCliente(conEñes)).toMatch(/bytes/i);
  });

  it('el espacio no cuenta como símbolo', () => {
    expect(validarPasswordCliente('Frase Con Espacios 2026')).toMatch(/símbolo/i);
  });

  it('acepta una mayúscula acentuada', () => {
    expect(validarPasswordCliente('Álvaro come pan 7!')).toBeNull();
  });

  it('no reimplementa la lista de bloqueo: eso es cosa del servidor', () => {
    // Mantener aquí una copia de la lista sería una fuente de
    // desincronización, y no aporta nada: la API la rechaza igual.
    expect(validarPasswordCliente('Password123456!')).toBeNull();
  });
});

describe('estadoRequisitos', () => {
  it('con la cadena vacía no cumple ninguno', () => {
    expect(estadoRequisitos('')).toEqual({
      longitud: false,
      mayuscula: false,
      digito: false,
      simbolo: false,
    });
  });

  it('sin argumento tampoco se rompe', () => {
    expect(estadoRequisitos().longitud).toBe(false);
  });

  it('con una contraseña válida los cumple todos', () => {
    expect(estadoRequisitos(VALIDA)).toEqual({
      longitud: true,
      mayuscula: true,
      digito: true,
      simbolo: true,
    });
  });

  it('detecta cada requisito por separado', () => {
    expect(estadoRequisitos('aaaaaaaaaaaaaaaa').longitud).toBe(true);
    expect(estadoRequisitos('aaaaaaaaaaaaaaaa').mayuscula).toBe(false);
    expect(estadoRequisitos('A').mayuscula).toBe(true);
    expect(estadoRequisitos('7').digito).toBe(true);
    expect(estadoRequisitos('!').simbolo).toBe(true);
    expect(estadoRequisitos(' ').simbolo).toBe(false);
  });
});

describe('PASSWORD_PATTERN', () => {
  // El navegador ancla el patrón por su cuenta; aquí hay que hacerlo a mano
  // para reproducir exactamente cómo lo evalúa.
  const anclado = new RegExp(`^(?:${PASSWORD_PATTERN})$`, 'u');

  it('acepta una contraseña válida', () => {
    expect(anclado.test(VALIDA)).toBe(true);
  });

  it.each([
    ['sin mayúscula', 'cafe con leche y 2 tostadas!'],
    ['sin número', 'Cafe con leche y tostadas!'],
    ['sin símbolo', 'Cafe con leche y 2 tostadas'],
  ])('rechaza una contraseña %s', (_caso, password) => {
    expect(anclado.test(password)).toBe(false);
  });

  it('coincide con validarPasswordCliente en todo lo que es composición', () => {
    // El pattern no comprueba la longitud, que la cubre minLength. Para el
    // resto, los dos caminos tienen que dar el mismo veredicto.
    const casos = [
      VALIDA,
      'Correct-Horse2!',
      'cafe con leche y 2 tostadas!',
      'Cafe con leche y tostadas!',
      'Cafe con leche y 2 tostadas',
      'Álvaro come pan 7!',
    ];

    for (const caso of casos) {
      const errorDeComposicion = /mayúscula|número|símbolo/.test(
        validarPasswordCliente(caso) ?? '',
      );
      expect(anclado.test(caso)).toBe(!errorDeComposicion);
    }
  });
});

describe('REQUISITOS_PASSWORD', () => {
  it('publica los cuatro requisitos que aplica la función', () => {
    expect(REQUISITOS_PASSWORD).toHaveLength(4);
    expect(REQUISITOS_PASSWORD[0]).toContain(String(MIN_PASSWORD_LENGTH));
    expect(REQUISITOS_PASSWORD.join(' ')).toMatch(/mayúscula/i);
    expect(REQUISITOS_PASSWORD.join(' ')).toMatch(/número/i);
    expect(REQUISITOS_PASSWORD.join(' ')).toMatch(/símbolo/i);
  });
});
