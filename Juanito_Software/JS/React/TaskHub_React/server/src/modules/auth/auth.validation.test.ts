import { describe, it, expect } from 'vitest';
import type { Request } from 'express';
import { registerValidator, loginValidator } from './auth.validation.js';

const req = (body: unknown) => ({ body }) as unknown as Request;

describe('registerValidator', () => {
  it('acepta credenciales válidas', () => {
    expect(registerValidator(req({ username: 'juan', password: 'secreto123' }))).toBeNull();
  });

  it('exige al menos 8 caracteres de contraseña', () => {
    // Se subió de 6 a 8 durante la auditoría, siguiendo la recomendación del
    // NIST para contraseñas elegidas por la persona.
    expect(registerValidator(req({ username: 'juan', password: '1234567' }))).not.toBeNull();
    expect(registerValidator(req({ username: 'juan', password: '12345678' }))).toBeNull();
  });

  it('rechaza contraseñas de más de 72 caracteres', () => {
    // bcrypt ignora lo que pase de 72 bytes: aceptarlas daría una falsa
    // sensación de seguridad y encarecería cada intento de acceso.
    const larga = 'a'.repeat(73);
    expect(registerValidator(req({ username: 'juan', password: larga }))).not.toBeNull();
  });

  it('exige al menos 3 caracteres de usuario', () => {
    expect(registerValidator(req({ username: 'ab', password: 'secreto123' }))).not.toBeNull();
  });

  it('rechaza nombres de usuario de más de 32 caracteres', () => {
    const largo = 'u'.repeat(33);
    expect(registerValidator(req({ username: largo, password: 'secreto123' }))).not.toBeNull();
  });

  it.each([
    ['sin usuario', { password: 'secreto123' }],
    ['sin contraseña', { username: 'juan' }],
    ['usuario en blanco', { username: '   ', password: 'secreto123' }],
    ['usuario numérico', { username: 12345, password: 'secreto123' }],
    ['contraseña numérica', { username: 'juan', password: 12345678 }],
    ['cuerpo vacío', {}],
  ])('rechaza: %s', (_caso, body) => {
    expect(registerValidator(req(body))).not.toBeNull();
  });

  it('no repite el mismo mensaje dos veces', () => {
    // Si faltan usuario y contraseña, ambos empujan el mismo texto: el
    // validador los deduplica para no mostrar el error repetido.
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

  it('no aplica la longitud mínima al entrar', () => {
    // Al iniciar sesión no se valida la longitud: hacerlo revelaría qué
    // política de contraseñas tenía la cuenta, y además una cuenta antigua
    // podría tener una contraseña más corta que la política actual.
    expect(loginValidator(req({ username: 'juan', password: 'abc' }))).toBeNull();
  });

  it.each([
    ['sin usuario', { password: 'x' }],
    ['sin contraseña', { username: 'juan' }],
    ['ambos vacíos', { username: '', password: '' }],
  ])('rechaza: %s', (_caso, body) => {
    expect(loginValidator(req(body))).not.toBeNull();
  });
});
