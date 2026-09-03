import { describe, it, expect } from 'vitest';
import type { Request, Response } from 'express';
import {
  readRefreshCookie,
  setRefreshCookie,
  clearRefreshCookie,
  REFRESH_COOKIE,
} from './auth.cookie.js';
import { env } from '../../config/env.js';

/**
 * La lectura de la cookie está escrita a mano en lugar de añadir
 * `cookie-parser`, así que conviene fijar con tests los casos que esa librería
 * habría resuelto: varias cookies juntas, espacios, nombres parecidos y valores
 * mal formados.
 */

const req = (cookie?: string) => ({ headers: cookie ? { cookie } : {} }) as unknown as Request;

describe('readRefreshCookie', () => {
  it('lee la cookie cuando va sola', () => {
    expect(readRefreshCookie(req(`${REFRESH_COOKIE}=abc123`))).toBe('abc123');
  });

  it('la encuentra entre otras cookies', () => {
    expect(
      readRefreshCookie(req(`tema=oscuro; ${REFRESH_COOKIE}=abc123; idioma=es`)),
    ).toBe('abc123');
  });

  it('tolera el espacio que el navegador pone tras cada punto y coma', () => {
    expect(readRefreshCookie(req(`a=1;   ${REFRESH_COOKIE}=abc123`))).toBe('abc123');
  });

  it('devuelve undefined si no hay cabecera de cookies', () => {
    expect(readRefreshCookie(req())).toBeUndefined();
  });

  it('devuelve undefined si la cookie no está', () => {
    expect(readRefreshCookie(req('tema=oscuro; idioma=es'))).toBeUndefined();
  });

  it('no confunde una cookie cuyo nombre empieza igual', () => {
    // Sin comparar el nombre completo, `taskhub_refresh_otro` casaría por
    // prefijo y se devolvería el valor equivocado.
    expect(readRefreshCookie(req(`${REFRESH_COOKIE}_otro=noesesta`))).toBeUndefined();
  });

  it('no confunde una cookie cuyo nombre termina igual', () => {
    expect(readRefreshCookie(req(`x_${REFRESH_COOKIE}=noesesta`))).toBeUndefined();
  });

  it('conserva un valor que contenga el signo igual', () => {
    // El corte es por el PRIMER `=`, no por todos: si no, un valor con relleno
    // base64 se truncaría.
    expect(readRefreshCookie(req(`${REFRESH_COOKIE}=a=b=c`))).toBe('a=b=c');
  });

  it('decodifica el valor', () => {
    expect(readRefreshCookie(req(`${REFRESH_COOKIE}=a%20b`))).toBe('a b');
  });

  it('no se rompe con un valor mal codificado', () => {
    // Un `%` suelto hace estallar a decodeURIComponent. Se trata como si no
    // hubiera cookie en lugar de tumbar la petición.
    expect(() => readRefreshCookie(req(`${REFRESH_COOKIE}=%E0%A4%A`))).not.toThrow();
    expect(readRefreshCookie(req(`${REFRESH_COOKIE}=%E0%A4%A`))).toBeUndefined();
  });

  it('ignora fragmentos sin signo igual', () => {
    expect(readRefreshCookie(req(`basura; ${REFRESH_COOKIE}=abc123`))).toBe('abc123');
  });

  it('devuelve cadena vacía si la cookie está vacía', () => {
    // El servicio la trata luego como ausencia de sesión; lo importante es que
    // no lance.
    expect(readRefreshCookie(req(`${REFRESH_COOKIE}=`))).toBe('');
  });
});

describe('escritura de la cookie', () => {
  /**
   * Los atributos con los que sale la cookie **son la protección**: `HttpOnly`
   * la esconde del JavaScript de la página y `SameSite=Strict` es lo que cierra
   * el CSRF que se abriría al empezar a usar cookies. Que estén no es un
   * detalle de configuración, es el motivo por el que este diseño es seguro.
   */

  /** Response simulado que se queda con lo que le pasan a cookie()/clearCookie(). */
  function respuestaFalsa() {
    const puesta: { nombre?: string; valor?: string; opciones?: Record<string, unknown> } = {};
    const borrada: { nombre?: string; opciones?: Record<string, unknown> } = {};
    const res = {
      cookie(nombre: string, valor: string, opciones: Record<string, unknown>) {
        Object.assign(puesta, { nombre, valor, opciones });
        return this;
      },
      clearCookie(nombre: string, opciones: Record<string, unknown>) {
        Object.assign(borrada, { nombre, opciones });
        return this;
      },
    } as unknown as Response;
    return { res, puesta, borrada };
  }

  it('usa el nombre esperado y el valor que se le pasa', () => {
    const { res, puesta } = respuestaFalsa();
    setRefreshCookie(res, 'AbCdEf123456');

    expect(puesta.nombre).toBe(REFRESH_COOKIE);
    expect(puesta.valor).toBe('AbCdEf123456');
  });

  it('es HttpOnly: el JavaScript de la página no puede leerla', () => {
    const { res, puesta } = respuestaFalsa();
    setRefreshCookie(res, 'x');

    expect(puesta.opciones!.httpOnly).toBe(true);
  });

  it('lleva SameSite=Strict, que es lo que cierra el CSRF', () => {
    const { res, puesta } = respuestaFalsa();
    setRefreshCookie(res, 'x');

    expect(puesta.opciones!.sameSite).toBe('strict');
  });

  it('se limita a /api/auth y no viaja al resto de la API', () => {
    const { res, puesta } = respuestaFalsa();
    setRefreshCookie(res, 'x');

    expect(puesta.opciones!.path).toBe('/api/auth');
  });

  it('su caducidad coincide con la del token de refresco', () => {
    // Si la cookie durara menos, la sesión moriría antes de tiempo; si durara
    // más, el navegador seguiría mandando un token ya inservible.
    const { res, puesta } = respuestaFalsa();
    setRefreshCookie(res, 'x');

    expect(puesta.opciones!.maxAge).toBe(env.refreshTokenTtlMs);
  });

  it('el borrado repite los MISMOS atributos', () => {
    // Si no coincidieran, el navegador no identificaría la cookie y se quedaría
    // con la vieja: el logout no borraría nada del lado del cliente.
    const { res, puesta, borrada } = respuestaFalsa();
    setRefreshCookie(res, 'x');
    clearRefreshCookie(res);

    expect(borrada.nombre).toBe(puesta.nombre);
    for (const clave of ['httpOnly', 'secure', 'sameSite', 'path']) {
      expect(borrada.opciones![clave]).toBe(puesta.opciones![clave]);
    }
  });

  it('lo que se escribe se puede volver a leer', () => {
    // Cierra el círculo: escritura y lectura son dos funciones distintas y
    // nada garantizaba que hablaran el mismo idioma.
    const { res, puesta } = respuestaFalsa();
    const token = 'AbCdEf-123_456';
    setRefreshCookie(res, token);

    const leido = readRefreshCookie({
      headers: { cookie: `${puesta.nombre}=${puesta.valor}` },
    } as unknown as Request);

    expect(leido).toBe(token);
  });
});
