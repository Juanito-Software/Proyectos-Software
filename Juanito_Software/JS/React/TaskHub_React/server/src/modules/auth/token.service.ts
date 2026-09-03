import crypto from 'node:crypto';
import jwt from 'jsonwebtoken';
import { env } from '../../config/env.js';

export interface TokenPayload {
  userId: string;
  username: string;
  /**
   * Marca el token como de acceso.
   *
   * Los tokens de refresco de TaskHub no son JWT —son 32 bytes aleatorios—, así
   * que no pueden colarse aquí por construcción: la verificación de firma los
   * rechazaría. Este claim es una segunda barrera y, sobre todo, deja el
   * propósito escrito en el propio token para cualquier cosa que se añada más
   * adelante.
   *
   * Además invalida de golpe los tokens de la política anterior, que no lo
   * llevan. Es deliberado: eran de siete días y no había forma de revocarlos,
   * que es justamente el problema que este cambio soluciona. Dejarlos vivos
   * habría mantenido el agujero abierto una semana más.
   */
  typ: 'access';
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
  /**
   * Emite un token de acceso de vida corta.
   *
   * Es autocontenido: el middleware lo valida con la firma, sin consultar la
   * base de datos. Eso lo hace rápido y es lo que permite que la revocación no
   * necesite una lista negra consultada en cada petición — a cambio, un token
   * ya emitido sigue valiendo hasta que caduca aunque se cierre la sesión, y
   * por eso la duración es de minutos y no de días.
   */
  generateAccessToken(payload: Omit<TokenPayload, 'typ'>): string {
    return jwt.sign({ ...payload, typ: 'access' }, env.jwtSecret, {
      algorithm: ALGORITHM,
      expiresIn: env.accessTokenTtl as jwt.SignOptions['expiresIn'],
      // Identificador único del token.
      //
      // Sin él, dos tokens emitidos para el mismo usuario dentro del mismo
      // segundo salen byte a byte idénticos: el único campo variable es `iat`,
      // que tiene resolución de segundos. Eso hacía que una renovación
      // inmediata devolviera literalmente el mismo token de acceso, con la
      // misma caducidad, dando la falsa impresión de haberse renovado.
      jwtid: crypto.randomUUID(),
    });
  },

  verifyAccessToken(token: string): TokenPayload {
    const payload = jwt.verify(token, env.jwtSecret, {
      algorithms: [ALGORITHM],
    }) as TokenPayload;

    // Un token con firma válida pero sin los campos esperados no sirve: mejor
    // rechazarlo aquí que dejar que llegue a una consulta con userId undefined.
    if (typeof payload?.userId !== 'string' || !payload.userId) {
      throw new jwt.JsonWebTokenError('El token no contiene un identificador de usuario válido');
    }

    if (payload.typ !== 'access') {
      throw new jwt.JsonWebTokenError('El token no es un token de acceso');
    }

    return payload;
  },
};
