import { Request } from 'express';
import { ValidatorFn } from '../../middleware/validate.middleware.js';

/**
 * Ocho caracteres es el mínimo que recomienda el NIST para contraseñas
 * elegidas por la persona. Se prefiere exigir longitud antes que composición
 * (mayúsculas, símbolos…): las reglas de composición empujan a patrones
 * predecibles del tipo "Password1!" sin ganar entropía real.
 */
const MIN_PASSWORD_LENGTH = 8;
const MAX_PASSWORD_LENGTH = 72;
const MAX_USERNAME_LENGTH = 32;

export const registerValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { username, password } = req.body ?? {};

  if (typeof username !== 'string' || !username.trim()) {
    errors.push('Usuario y contraseña son obligatorios');
  } else if (username.trim().length < 3) {
    errors.push('El usuario debe tener al menos 3 caracteres');
  } else if (username.trim().length > MAX_USERNAME_LENGTH) {
    errors.push(`El usuario no puede superar los ${MAX_USERNAME_LENGTH} caracteres`);
  }

  if (typeof password !== 'string' || !password) {
    errors.push('Usuario y contraseña son obligatorios');
  } else if (password.length < MIN_PASSWORD_LENGTH) {
    errors.push(`La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres`);
  } else if (password.length > MAX_PASSWORD_LENGTH) {
    // bcrypt solo tiene en cuenta los primeros 72 bytes: aceptar contraseñas
    // más largas daría una falsa sensación de seguridad. Además, un texto
    // enorme obligaría a calcular un hash costoso por cada intento.
    errors.push(`La contraseña no puede superar los ${MAX_PASSWORD_LENGTH} caracteres`);
  }

  return errors.length > 0 ? [...new Set(errors)] : null;
};

export const loginValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { username, password } = req.body ?? {};

  if (typeof username !== 'string' || !username.trim() || typeof password !== 'string' || !password) {
    errors.push('Usuario y contraseña son obligatorios');
  }

  return errors.length > 0 ? errors : null;
};
