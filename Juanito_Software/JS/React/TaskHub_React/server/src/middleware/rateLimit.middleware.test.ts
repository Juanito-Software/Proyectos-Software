import { describe, it, expect } from 'vitest';
import { resolverAuthLimit, AUTH_LIMIT_POR_DEFECTO } from './rateLimit.middleware.js';

/**
 * El límite de intentos de autenticación se puede aflojar para que la suite de
 * verificación pueda probar una decena de contraseñas inválidas seguidas.
 *
 * Lo que de verdad hay que fijar con tests es lo contrario: que en producción
 * la variable no sirva de nada. Un límite de fuerza bruta que se desactiva
 * desde el entorno no es un límite.
 */

describe('resolverAuthLimit', () => {
  it('sin variable, usa el límite estricto', () => {
    expect(resolverAuthLimit({})).toBe(AUTH_LIMIT_POR_DEFECTO);
  });

  it('fuera de producción, respeta la variable', () => {
    expect(resolverAuthLimit({ AUTH_RATE_LIMIT: '1000' })).toBe(1000);
  });

  it('en producción IGNORA la variable', () => {
    // El caso importante: si alguien colara AUTH_RATE_LIMIT en el panel de
    // despliegue, la fuerza bruta tendría vía libre.
    expect(resolverAuthLimit({ AUTH_RATE_LIMIT: '1000000', NODE_ENV: 'production' })).toBe(
      AUTH_LIMIT_POR_DEFECTO,
    );
  });

  it.each([
    ['texto', 'muchos'],
    ['cero', '0'],
    ['negativo', '-5'],
    ['decimal', '10.5'],
    ['vacío', ''],
  ])('con un valor %s vuelve al límite estricto', (_caso, valor) => {
    expect(resolverAuthLimit({ AUTH_RATE_LIMIT: valor })).toBe(AUTH_LIMIT_POR_DEFECTO);
  });
});
