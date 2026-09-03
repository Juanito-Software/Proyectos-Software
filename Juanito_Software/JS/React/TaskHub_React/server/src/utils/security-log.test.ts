import { describe, it, expect, vi, afterEach } from 'vitest';
import { registrarEventoSeguridad } from './security-log.js';

/**
 * El registro de eventos de seguridad.
 *
 * Lo que de verdad hay que fijar con tests aquí no es que registre, sino que
 * **no registre credenciales**. Un registro que filtra tokens es peor que no
 * tener registro: además de la fuga, da una falsa sensación de control. Y ya
 * pasó una vez en este proyecto — la suite de API volcaba la cabecera
 * `Set-Cookie` entera, con el token de refresco dentro, en la salida del CI.
 */

function capturar() {
  const lineas: string[] = [];
  vi.spyOn(console, 'warn').mockImplementation((linea: unknown) => {
    lineas.push(String(linea));
  });
  return lineas;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe('formato', () => {
  it('escribe una línea de JSON válido', () => {
    const lineas = capturar();
    registrarEventoSeguridad('login.correcto', { usuario: 'juan' });

    expect(lineas).toHaveLength(1);
    expect(() => JSON.parse(lineas[0])).not.toThrow();
  });

  it('lleva tipo, evento y momento', () => {
    const lineas = capturar();
    registrarEventoSeguridad('login.fallido', { usuario: 'juan' });

    const registro = JSON.parse(lineas[0]);
    expect(registro.tipo).toBe('seguridad');
    expect(registro.evento).toBe('login.fallido');
    expect(registro.momento).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  it('conserva los datos que se le pasan', () => {
    const lineas = capturar();
    registrarEventoSeguridad('logout', { userId: 'u-1', tokensRevocados: 3 });

    const registro = JSON.parse(lineas[0]);
    expect(registro.userId).toBe('u-1');
    expect(registro.tokensRevocados).toBe(3);
  });

  it('omite los campos indefinidos en lugar de escribirlos como null', () => {
    const lineas = capturar();
    registrarEventoSeguridad('logout', { userId: 'u-1', ip: undefined });

    expect(Object.keys(JSON.parse(lineas[0]))).not.toContain('ip');
  });

  it('funciona sin datos adicionales', () => {
    const lineas = capturar();
    expect(() => registrarEventoSeguridad('logout')).not.toThrow();
    expect(JSON.parse(lineas[0]).evento).toBe('logout');
  });

  it('va por console.warn, no por console.log', () => {
    // Para que quede en el flujo de errores y no se pierda entre las miles de
    // líneas del registro de peticiones.
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});

    registrarEventoSeguridad('login.correcto');

    expect(warn).toHaveBeenCalledTimes(1);
    expect(log).not.toHaveBeenCalled();
  });
});

describe('censura de credenciales', () => {
  it.each([
    ['password', { password: 'Cafe con leche y 2 tostadas!' }],
    ['accessToken', { accessToken: 'eyJhbGciOi...' }],
    ['refreshToken', { refreshToken: 'AbCdEf123456' }],
    ['token', { token: 'AbCdEf123456' }],
    ['tokenHash', { tokenHash: 'a'.repeat(64) }],
    ['cookie', { cookie: 'taskhub_refresh=AbCdEf' }],
    ['authorization', { authorization: 'Bearer eyJ...' }],
    ['jwtSecret', { jwtSecret: 'clave-larguisima' }],
  ])('censura el campo %s', (_caso, datos) => {
    const lineas = capturar();
    registrarEventoSeguridad('login.correcto', datos);

    const valor = Object.values(datos)[0];
    expect(lineas[0]).not.toContain(valor);
    expect(lineas[0]).toContain('<censurado>');
  });

  it('censura sin distinguir mayúsculas', () => {
    const lineas = capturar();
    registrarEventoSeguridad('login.correcto', { PassWord: 'secreta-larga-de-verdad' });

    expect(lineas[0]).not.toContain('secreta-larga-de-verdad');
  });

  it('censura aunque la clave sea compuesta', () => {
    const lineas = capturar();
    registrarEventoSeguridad('login.correcto', { user_password_hash: 'abc123' });

    expect(lineas[0]).not.toContain('abc123');
  });

  it('el nombre de usuario SÍ se registra: sin él no se sabe a quién atacan', () => {
    const lineas = capturar();
    registrarEventoSeguridad('login.fallido', { usuario: 'juan', motivo: 'credenciales-invalidas' });

    expect(JSON.parse(lineas[0]).usuario).toBe('juan');
    expect(JSON.parse(lineas[0]).motivo).toBe('credenciales-invalidas');
  });

  it('la censura no tapa los campos legítimos del mismo evento', () => {
    const lineas = capturar();
    registrarEventoSeguridad('refresh.reutilizacion', {
      userId: 'u-1',
      familia: 'f-1',
      tokensRevocados: 2,
      refreshToken: 'no-debe-salir',
    });

    const registro = JSON.parse(lineas[0]);
    expect(registro.userId).toBe('u-1');
    expect(registro.familia).toBe('f-1');
    expect(registro.tokensRevocados).toBe(2);
    expect(registro.refreshToken).toBe('<censurado>');
  });
});

describe('la censura no confunde credenciales con contadores', () => {
  it('un número con "token" en el nombre NO se censura', () => {
    // La primera versión del filtro tapaba `tokensRevocados: 3` por contener
    // "token". Una credencial siempre es una cadena; un recuento nunca.
    const lineas = capturar();
    registrarEventoSeguridad('logout', { tokensRevocados: 3 });

    expect(JSON.parse(lineas[0]).tokensRevocados).toBe(3);
  });

  it('pero una cadena con el mismo nombre sí', () => {
    const lineas = capturar();
    registrarEventoSeguridad('logout', { tokensRevocados: 'AbCdEf123456' });

    expect(JSON.parse(lineas[0]).tokensRevocados).toBe('<censurado>');
  });

  it('un booleano relacionado con contraseñas tampoco se censura', () => {
    const lineas = capturar();
    registrarEventoSeguridad('login.fallido', { passwordCorrecta: false });

    expect(JSON.parse(lineas[0]).passwordCorrecta).toBe(false);
  });
});
