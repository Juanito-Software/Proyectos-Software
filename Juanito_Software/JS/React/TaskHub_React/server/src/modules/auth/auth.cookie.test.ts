import { describe, it, expect } from 'vitest';
import type { Request } from 'express';
import { readRefreshCookie, REFRESH_COOKIE } from './auth.cookie.js';

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
