import { NextFunction, Request, Response } from 'express';
import { AnyZodObject } from 'zod';

// Middleware genérico de validación con Zod. Valida body/query/params a la vez
// y reemplaza req.body con los datos ya parseados (con defaults y coerciones aplicadas).
export function validate(schema: AnyZodObject) {
  return (req: Request, _res: Response, next: NextFunction) => {
    const parsed = schema.parse({
      body: req.body,
      query: req.query,
      params: req.params,
    });
    req.body = parsed.body ?? req.body;
    next();
  };
}
