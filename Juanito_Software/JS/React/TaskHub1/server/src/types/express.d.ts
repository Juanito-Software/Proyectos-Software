import 'express';

// authMiddleware guarda aquí los datos del JWT verificado para que el resto
// de la petición (controllers, services) los use sin volver a decodificar el token.
declare global {
  namespace Express {
    interface Request {
      userId?: string;
      username?: string;
    }
  }
}

export {};
