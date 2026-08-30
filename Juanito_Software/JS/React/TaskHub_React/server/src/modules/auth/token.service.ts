import jwt from 'jsonwebtoken';
import { env } from '../../config/env.js';

export interface TokenPayload {
  userId: string;
  username: string;
}

/**
 * Se fija el algoritmo explícitamente, al firmar y al verificar.
 *
 * Sin `algorithms` en la verificación, la librería acepta el algoritmo que
 * declare el propio token. Ese es el vector del ataque clásico "alg: none",
 * en el que un atacante quita la firma y cambia el algoritmo a "none" para
 * que se acepte cualquier contenido. Las versiones actuales de jsonwebtoken
 * ya lo rechazan por su cuenta, pero declararlo no depende de que la librería
 * mantenga ese comportamiento y protege también frente a la confusión entre
 * algoritmos simétricos y asimétricos.
 */
const ALGORITHM: jwt.Algorithm = 'HS256';

export const tokenService = {
  generateToken(payload: TokenPayload): string {
    return jwt.sign(payload, env.jwtSecret, {
      algorithm: ALGORITHM,
      expiresIn: env.jwtExpiresIn as jwt.SignOptions['expiresIn'],
    });
  },

  verifyToken(token: string): TokenPayload {
    const payload = jwt.verify(token, env.jwtSecret, {
      algorithms: [ALGORITHM],
    }) as TokenPayload;

    // Un token con firma válida pero sin los campos esperados no sirve: mejor
    // rechazarlo aquí que dejar que llegue a una consulta con userId undefined.
    if (typeof payload?.userId !== 'string' || !payload.userId) {
      throw new jwt.JsonWebTokenError('El token no contiene un identificador de usuario válido');
    }

    return payload;
  },
};
