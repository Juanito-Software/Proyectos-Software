import { Request } from 'express';
import { ValidatorFn } from '../../middleware/validate.middleware.js';
import { validarPassword } from './password-policy.js';

const MIN_USERNAME_LENGTH = 3;
const MAX_USERNAME_LENGTH = 32;

export const registerValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { username, password } = req.body ?? {};

  if (typeof username !== 'string' || !username.trim()) {
    errors.push('Usuario y contraseña son obligatorios');
  } else if (username.trim().length < MIN_USERNAME_LENGTH) {
    errors.push(`El usuario debe tener al menos ${MIN_USERNAME_LENGTH} caracteres`);
  } else if (username.trim().length > MAX_USERNAME_LENGTH) {
    errors.push(`El usuario no puede superar los ${MAX_USERNAME_LENGTH} caracteres`);
  }

  if (typeof password !== 'string' || !password) {
    errors.push('Usuario y contraseña son obligatorios');
  } else {
    // La política vive en password-policy.ts, que es la única fuente de verdad
    // y la comparte con la semilla del administrador. Aquí solo se traslada su
    // veredicto al formato de errores de la API.
    const resultado = validarPassword(
      password,
      typeof username === 'string' ? username.trim() : undefined,
    );
    if (!resultado.valida && resultado.error) {
      errors.push(resultado.error);
    }
  }

  return errors.length > 0 ? [...new Set(errors)] : null;
};

/**
 * El inicio de sesión NO valida la política.
 *
 * Es deliberado y tiene dos motivos. Uno: aplicarla aquí dejaría fuera a los
 * usuarios que se registraron cuando el mínimo era menor, y cambiar la política
 * no debe invalidar cuentas existentes. Dos: rechazar por longitud antes de
 * comprobar las credenciales revelaría qué política tenía la cuenta, y da una
 * respuesta distinta según el caso —justo lo que evita el mensaje único de
 * "usuario o contraseña incorrectos".
 */
export const loginValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { username, password } = req.body ?? {};

  if (typeof username !== 'string' || !username.trim() || typeof password !== 'string' || !password) {
    errors.push('Usuario y contraseña son obligatorios');
  }

  return errors.length > 0 ? errors : null;
};
