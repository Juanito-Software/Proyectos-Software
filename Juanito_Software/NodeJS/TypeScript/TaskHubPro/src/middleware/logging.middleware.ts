import { Request, Response, NextFunction } from 'express';

export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const timestamp = new Date().toISOString();
    const { method, originalUrl } = req;
    const { statusCode } = res;
    
    console.log(`[${timestamp}] ${method} ${originalUrl} ${statusCode} - ${duration}ms`);
  });
  
  next();
}
