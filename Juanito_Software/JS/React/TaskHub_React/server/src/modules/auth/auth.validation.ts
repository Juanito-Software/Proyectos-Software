import { Request } from 'express';
import { ValidatorFn } from '../../middleware/validate.middleware.js';

export const registerValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { username, password } = req.body ?? {};

  if (typeof username !== 'string' || !username.trim()) {
    errors.push('Usuario y contraseña son obligatorios');
  } else if (username.trim().length < 3) {
    errors.push('El usuario debe tener al menos 3 caracteres');
  }

  if (typeof password !== 'string' || !password) {
    errors.push('Usuario y contraseña son obligatorios');
  } else if (password.length < 6) {
    errors.push('La contraseña debe tener al menos 6 caracteres');
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
