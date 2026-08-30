import { describe, it, expect } from 'vitest';
import type { Request } from 'express';
import { registerValidator, loginValidator } from './auth.validation.js';
import { MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH } from './password-policy.js';

const req = (body: unknown) => ({ body }) as unknown as Request;

// Una contraseña que cumple la política sin recurrir a composición: es la
// forma que se quiere fomentar, así que es la que usan los casos válidos.
const FRASE_VALIDA = 'melon con jamon y pan';

describe('registerValidator: contraseña', () => {
  it('acepta una frase larga sin mayúsculas, números ni símbolos', () => {
    expect(registerValidator(req({ username: 'juan', password: FRASE_VALIDA }))).toBeNull();
  });

  it('acepta también una contraseña compleja tradicional', () => {
    // No se prohíbe la composición, solo se deja de exigir.
    expect(registerValidator(req({ username: 'juan', password: 'P4ss!w0rd#Larga2026' }))).toBeNull();
  });

  it(`exige al menos ${MIN_PASSWORD_LENGTH} caracteres`, () => {
    const corta = 'melon y sandia'; // 14
    expect(registerValidator(req({ username: 'juan', password: corta }))).not.toBeNull();
    expect(registerValidator(req({ username: 'juan', password: corta + 's' }))).toBeNull();
  });

  it(`rechaza por encima de ${MAX_PASSWORD_LENGTH}, el límite técnico de bcrypt`, () => {
    const larga = 'a'.repeat(MAX_PASSWORD_LENGTH + 1);
    expect(registerValidator(req({ username: 'juan', password: larga }))).not.toBeNull();
  });

  it('rechaza una contraseña de la lista de bloqueo', () => {
    expect(registerValidator(req({ username: 'juan', password: 'passwordpassword' }))).not.toBeNull();
  });

  it('rechaza que la contraseña contenga el nombre de usuario', () => {
    const errores = registerValidator(req({ username: 'juanito', password: 'juanito y su clave' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toMatch(/nombre de usuario/i);
  });

  it('permite espacios en la contraseña', () => {
    expect(registerValidator(req({ username: 'juan', password: 'esto tiene espacios ok' }))).toBeNull();
  });
});

describe('registerValidator: usuario', () => {
  it('exige al menos 3 caracteres de usuario', () => {
    expect(registerValidator(req({ username: 'ab', password: FRASE_VALIDA }))).not.toBeNull();
  });

  it('rechaza nombres de usuario de más de 32 caracteres', () => {
    expect(registerValidator(req({ username: 'u'.repeat(33), password: FRASE_VALIDA }))).not.toBeNull();
  });

  it.each([
    ['sin usuario', { password: FRASE_VALIDA }],
    ['sin contraseña', { username: 'juan' }],
    ['usuario en blanco', { username: '   ', password: FRASE_VALIDA }],
    ['usuario numérico', { username: 12345, password: FRASE_VALIDA }],
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
    // Deliberado: quien se registró cuando el mínimo era de 8 caracteres debe
    // poder seguir entrando. Subir la política no invalida cuentas existentes.
    expect(loginValidator(req({ username: 'juan', password: 'corta' }))).toBeNull();
  });

  it('tampoco rechaza una contraseña de la lista de bloqueo al entrar', () => {
    // Si la rechazara aquí, revelaría información sobre la cuenta antes
    // siquiera de comprobar las credenciales.
    expect(loginValidator(req({ username: 'juan', password: 'passwordpassword' }))).toBeNull();
  });

  it('no acepta el campo de confirmación: no forma parte del contrato', () => {
    // La confirmación es asunto del formulario. Que llegue no debe romper
    // nada, pero tampoco se valida ni se usa.
    expect(loginValidator(req({ username: 'juan', password: 'x', passwordConfirmation: 'y' }))).toBeNull();
  });

  it.each([
    ['sin usuario', { password: 'x' }],
    ['sin contraseña', { username: 'juan' }],
    ['ambos vacíos', { username: '', password: '' }],
  ])('rechaza: %s', (_caso, body) => {
    expect(loginValidator(req(body))).not.toBeNull();
  });
});
