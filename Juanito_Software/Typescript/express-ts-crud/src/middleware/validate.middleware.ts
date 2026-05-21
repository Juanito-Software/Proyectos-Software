import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/api-error';

export type ValidatorFn = (req: Request) => string[] | null;

export function validate(validator: ValidatorFn) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    const errors = validator(req);
    if (errors && errors.length > 0) {
      next(ApiError.badRequest('Validation failed', errors));
      return;
    }
    next();
  };
}
