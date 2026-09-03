import { describe, it, expect } from 'vitest';
import jwt from 'jsonwebtoken';
import { tokenService } from './token.service.js';
import { generarRefreshToken, hashRefreshToken } from './refresh-token.js';
import { env } from '../../config/env.js';

/**
 * Lo que se fija aquí es la separación entre los dos tipos de credencial.
 *
 * El token de acceso es un JWT firmado de vida corta; el de refresco son bytes
 * aleatorios que solo valen contra la tabla de sesiones. Confundirlos sería el
 * fallo más grave de este diseño, así que hay tests en las dos direcciones.
 */

const PAYLOAD = { userId: 'u-1', username: 'juan' };

describe('token de acceso', () => {
  it('se emite y se verifica', () => {
    const token = tokenService.generateAccessToken(PAYLOAD);
    const payload = tokenService.verifyAccessToken(token);

    expect(payload.userId).toBe('u-1');
    expect(payload.username).toBe('juan');
  });

  it('lleva el claim typ=access', () => {
    const token = tokenService.generateAccessToken(PAYLOAD);
    expect(jwt.decode(token)).toMatchObject({ typ: 'access' });
  });

  it('caduca en el plazo configurado, no en días', () => {
    const decodificado = jwt.decode(tokenService.generateAccessToken(PAYLOAD)) as {
      iat: number;
      exp: number;
    };
    const duracionMs = (decodificado.exp - decodificado.iat) * 1000;

    expect(duracionMs).toBe(env.accessTokenTtlMs);
    // La gracia del cambio: la ventana en que un token robado sirve pasa de
    // una semana a minutos.
    expect(duracionMs).toBeLessThanOrEqual(60 * 60 * 1000);
  });

  it('rechaza un token firmado con otro secreto', () => {
    const ajeno = jwt.sign({ ...PAYLOAD, typ: 'access' }, 'otro-secreto-completamente-distinto');
    expect(() => tokenService.verifyAccessToken(ajeno)).toThrow();
  });

  it('rechaza un token caducado', () => {
    const caducado = jwt.sign({ ...PAYLOAD, typ: 'access' }, env.jwtSecret, { expiresIn: '-1s' });
    expect(() => tokenService.verifyAccessToken(caducado)).toThrow();
  });

  it('rechaza un token sin userId', () => {
    const sinUsuario = jwt.sign({ typ: 'access' }, env.jwtSecret);
    expect(() => tokenService.verifyAccessToken(sinUsuario)).toThrow(/identificador/i);
  });

  it('rechaza un token con userId vacío', () => {
    const vacio = jwt.sign({ userId: '', username: 'x', typ: 'access' }, env.jwtSecret);
    expect(() => tokenService.verifyAccessToken(vacio)).toThrow(/identificador/i);
  });

  it('rechaza un token malformado', () => {
    expect(() => tokenService.verifyAccessToken('esto-no-es-un-jwt')).toThrow();
  });

  it('rechaza alg:none', () => {
    // Firma vacía y algoritmo "none": el ataque clásico. El algoritmo va
    // declarado explícitamente en la verificación para que no cuele.
    const cabecera = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
    const cuerpo = Buffer.from(JSON.stringify({ ...PAYLOAD, typ: 'access' })).toString('base64url');
    expect(() => tokenService.verifyAccessToken(`${cabecera}.${cuerpo}.`)).toThrow();
  });
});

describe('separación entre acceso y refresco', () => {
  it('un token SIN typ no vale como acceso', () => {
    // Es exactamente la forma de los tokens de la versión anterior, que duraban
    // siete días y no se podían revocar. Al no llevar el claim, dejan de valer
    // en cuanto se despliega este cambio, que es la decisión buscada.
    const antiguo = jwt.sign(PAYLOAD, env.jwtSecret, { expiresIn: '7d' });
    expect(() => tokenService.verifyAccessToken(antiguo)).toThrow(/token de acceso/i);
  });

  it('un token con typ=refresh no vale como acceso', () => {
    const falso = jwt.sign({ ...PAYLOAD, typ: 'refresh' }, env.jwtSecret);
    expect(() => tokenService.verifyAccessToken(falso)).toThrow(/token de acceso/i);
  });

  it('un token de refresco no es siquiera un JWT', () => {
    // La separación no depende de recordar comprobar un claim: son cosas de
    // naturaleza distinta. Un token de refresco no tiene firma que verificar.
    const refresco = generarRefreshToken();
    expect(refresco).not.toContain('.');
    expect(() => tokenService.verifyAccessToken(refresco)).toThrow();
  });
});

describe('token de refresco', () => {
  it('tiene entropía suficiente', () => {
    // 32 bytes en base64url son 43 caracteres. Adivinarlo no es una vía.
    expect(generarRefreshToken()).toHaveLength(43);
  });

  it('no se repite entre llamadas', () => {
    const muestras = new Set(Array.from({ length: 500 }, () => generarRefreshToken()));
    expect(muestras.size).toBe(500);
  });

  it('usa solo caracteres seguros para una cookie', () => {
    // base64url no lleva +, / ni =, que obligarían a codificar y complicarían
    // la lectura de la cookie.
    for (let i = 0; i < 50; i++) {
      expect(generarRefreshToken()).toMatch(/^[A-Za-z0-9_-]+$/);
    }
  });
});

describe('hash del token de refresco', () => {
  it('es determinista: es lo que permite buscar la sesión por él', () => {
    const token = generarRefreshToken();
    expect(hashRefreshToken(token)).toBe(hashRefreshToken(token));
  });

  it('produce un SHA-256 en hexadecimal', () => {
    expect(hashRefreshToken('lo-que-sea')).toMatch(/^[0-9a-f]{64}$/);
  });

  it('cambia por completo con un solo carácter distinto', () => {
    expect(hashRefreshToken('token-a')).not.toBe(hashRefreshToken('token-b'));
  });

  it('no permite recuperar el token', () => {
    // Obvio, pero es la propiedad por la que se guarda el hash y no el token:
    // un volcado de la tabla no da credenciales utilizables.
    const token = generarRefreshToken();
    expect(hashRefreshToken(token)).not.toContain(token);
  });
});
