import { describe, it, expect } from 'vitest';
import type { Request } from 'express';
import { registerValidator, loginValidator } from './auth.validation.js';
import { MIN_PASSWORD_LENGTH, MAX_PASSWORD_BYTES } from './password-policy.js';

const req = (body: unknown) => ({ body }) as unknown as Request;

/**
 * El validador del registro no reimplementa la política: delega en
 * `validarPassword`. Lo que se comprueba aquí es que la delegación existe y que
 * el veredicto llega al formato de errores de la API — el detalle de cada regla
 * está en password-policy.test.ts.
 */

// Cumple los cuatro requisitos: 15+, mayúscula, número y símbolo.
const PASSWORD_VALIDA = 'Melon con Jamon 7!';

describe('registerValidator: contraseña', () => {
  it('acepta una contraseña que cumple la política', () => {
    expect(registerValidator(req({ username: 'juan', password: PASSWORD_VALIDA }))).toBeNull();
  });

  it('acepta también una contraseña compleja al estilo tradicional', () => {
    expect(registerValidator(req({ username: 'juan', password: 'P4ss!w9rd#Distinta' }))).toBeNull();
  });

  it(`exige al menos ${MIN_PASSWORD_LENGTH} caracteres`, () => {
    const corta = 'Corto-Horse12!'; // 14, cumple composición
    expect(registerValidator(req({ username: 'juan', password: corta }))).not.toBeNull();
    expect(registerValidator(req({ username: 'juan', password: corta + 'x' }))).toBeNull();
  });

  it(`rechaza por encima de ${MAX_PASSWORD_BYTES} bytes, el límite técnico de bcrypt`, () => {
    const larga = 'A1!' + 'a'.repeat(MAX_PASSWORD_BYTES);
    expect(registerValidator(req({ username: 'juan', password: larga }))).not.toBeNull();
  });

  it('exige una mayúscula', () => {
    const errores = registerValidator(req({ username: 'juan', password: 'melon con jamon 7!' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toMatch(/mayúscula/i);
  });

  it('exige un número', () => {
    const errores = registerValidator(req({ username: 'juan', password: 'Melon con Jamon!!' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toMatch(/número/i);
  });

  it('exige un símbolo', () => {
    const errores = registerValidator(req({ username: 'juan', password: 'Melon con Jamon 77' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toMatch(/símbolo/i);
  });

  it('rechaza una contraseña de la lista de bloqueo', () => {
    expect(
      registerValidator(req({ username: 'juan', password: 'passwordpassword' })),
    ).not.toBeNull();
  });

  it('rechaza el patrón "palabra común con adornos" aunque cumpla composición', () => {
    // Es justo lo que produce obligar a mezclar tipos de carácter, así que el
    // registro tiene que pararlo.
    expect(registerValidator(req({ username: 'juan', password: 'Password123456!' }))).not.toBeNull();
  });

  it('rechaza que la contraseña contenga el nombre de usuario', () => {
    const errores = registerValidator(req({ username: 'juanito', password: 'Juanito y clave 7!' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toMatch(/nombre de usuario/i);
  });

  it('permite espacios en la contraseña', () => {
    expect(
      registerValidator(req({ username: 'juan', password: 'Esto tiene espacios 7!' })),
    ).toBeNull();
  });

  it('ignora passwordConfirmation: no forma parte del contrato de la API', () => {
    // La comparación de los dos campos es del formulario. Que llegue el campo
    // no debe cambiar el resultado ni provocar un error.
    expect(
      registerValidator(
        req({
          username: 'juan',
          password: PASSWORD_VALIDA,
          passwordConfirmation: 'algo completamente distinto',
        }),
      ),
    ).toBeNull();
  });
});

describe('registerValidator: usuario', () => {
  it('exige al menos 3 caracteres de usuario', () => {
    expect(registerValidator(req({ username: 'ab', password: PASSWORD_VALIDA }))).not.toBeNull();
  });

  it('rechaza nombres de usuario de más de 32 caracteres', () => {
    expect(
      registerValidator(req({ username: 'u'.repeat(33), password: PASSWORD_VALIDA })),
    ).not.toBeNull();
  });

  it.each([
    ['sin usuario', { password: PASSWORD_VALIDA }],
    ['sin contraseña', { username: 'juan' }],
    ['usuario en blanco', { username: '   ', password: PASSWORD_VALIDA }],
    ['usuario numérico', { username: 12345, password: PASSWORD_VALIDA }],
    ['contraseña numérica', { username: 'juan', password: 123456789012345 }],
    ['cuerpo vacío', {}],
  ])('rechaza: %s', (_caso, body) => {
    expect(registerValidator(req(body))).not.toBeNull();
  });

  it('no repite el mismo mensaje dos veces', () => {
    const errores = registerValidator(req({}));
    expect(errores).not.toBeNull();
    expect(new Set(errores!).size).toBe(errores!.length);
  });

  it('no se rompe con el cuerpo indefinido', () => {
    expect(() => registerValidator(req(undefined))).not.toThrow();
  });
});

describe('loginValidator', () => {
  it('acepta usuario y contraseña presentes', () => {
    expect(loginValidator(req({ username: 'juan', password: 'x' }))).toBeNull();
  });

  it('NO aplica la política de contraseñas al entrar', () => {
    // Deliberado: quien se registró cuando el mínimo era de 8 caracteres y no
    // había composición debe poder seguir entrando. Endurecer la política no
    // invalida cuentas existentes.
    expect(loginValidator(req({ username: 'juan', password: 'corta' }))).toBeNull();
  });

  it('NO exige composición al entrar', () => {
    // Una cuenta creada con una frase sin mayúsculas ni símbolos sigue siendo
    // válida: la política nueva se aplica al registro, no al inicio de sesión.
    expect(loginValidator(req({ username: 'juan', password: 'caballo correcto grapa' }))).toBeNull();
  });

  it('tampoco rechaza una contraseña de la lista de bloqueo al entrar', () => {
    // Si la rechazara aquí, revelaría información sobre la cuenta antes
    // siquiera de comprobar las credenciales.
    expect(loginValidator(req({ username: 'juan', password: 'passwordpassword' }))).toBeNull();
  });

  it('no acepta el campo de confirmación: no forma parte del contrato', () => {
    expect(
      loginValidator(req({ username: 'juan', password: 'x', passwordConfirmation: 'y' })),
    ).toBeNull();
  });

  it.each([
    ['sin usuario', { password: 'x' }],
    ['sin contraseña', { username: 'juan' }],
    ['ambos vacíos', { username: '', password: '' }],
  ])('rechaza: %s', (_caso, body) => {
    expect(loginValidator(req(body))).not.toBeNull();
  });
});
