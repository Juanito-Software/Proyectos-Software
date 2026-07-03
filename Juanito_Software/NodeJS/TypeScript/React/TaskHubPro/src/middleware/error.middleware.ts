import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/api-error';
import { ApiResponse } from '../utils/api-response';

export function errorHandler(
  err: any,
  _req: Request,
  res: Response,
  _next: NextFunction
): void {
  const isProduction = process.env.NODE_ENV === 'production';

  if (err instanceof ApiError) {
    res.status(err.statusCode).json(
      ApiResponse.error(err.message, err.details)
    );
    return;
  }

  // Handle other unexpected errors
  const message = err.message || 'An unexpected error occurred';
  const details = isProduction ? undefined : { stack: err.stack, originalError: err };

  res.status(500).json(
    ApiResponse.error(message, details)
  );
}
