import { describe, it, expect } from 'vitest';
import {
  resolverAuthLimit,
  AUTH_LIMIT_POR_DEFECTO,
  claveDeCuenta,
  resolverCuentaLimit,
  CUENTA_LIMIT_POR_DEFECTO,
} from './rateLimit.middleware.js';

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

describe('límite por cuenta', () => {
  /**
   * El contador que cierra el hueco del limitador por IP: un ataque repartido
   * entre muchas direcciones nunca agotaba la cuota de ninguna.
   *
   * Lo que se prueba aquí es la **derivación de la clave**, que es donde está
   * toda la sustancia. Si la clave se calcula mal, el limitador sigue
   * existiendo y deja de servir para nada — y no hay forma de notarlo mirando
   * si el middleware está montado.
   */

  const req = (body: unknown) => ({ body }) as { body?: unknown };

  it('la clave es el nombre de usuario', () => {
    expect(claveDeCuenta(req({ username: 'juan', password: 'x' }))).toBe('juan');
  });

  it('normaliza mayúsculas', () => {
    // Sin esto bastaría con alternar mayúsculas para multiplicar los intentos:
    // `Juan`, `jUan` y `JUAN` serían tres cubos distintos contra la misma
    // cuenta, que en la base de datos es una sola por el índice sobre LOWER().
    const claves = ['juan', 'Juan', 'JUAN', 'jUaN'].map((u) => claveDeCuenta(req({ username: u })));

    expect(new Set(claves).size).toBe(1);
  });

  it('recorta los espacios', () => {
    expect(claveDeCuenta(req({ username: '  juan  ' }))).toBe('juan');
  });

  it('no depende de la contraseña', () => {
    // Si la clave incluyera la contraseña, cada intento caería en un cubo
    // nuevo y el límite no se alcanzaría nunca. Es el error que convierte
    // este mecanismo en decoración.
    const a = claveDeCuenta(req({ username: 'juan', password: 'uno' }));
    const b = claveDeCuenta(req({ username: 'juan', password: 'dos' }));

    expect(a).toBe(b);
  });

  it('un cuerpo sin usuario cae en un cubo común', () => {
    expect(claveDeCuenta(req({}))).toBe('__sin-usuario__');
    expect(claveDeCuenta(req(undefined))).toBe('__sin-usuario__');
    expect(claveDeCuenta(req({ username: '   ' }))).toBe('__sin-usuario__');
  });

  it('un usuario que no es texto no rompe la derivación', () => {
    // Express entrega un array si el campo se repite, y el cuerpo lo controla
    // quien llama. Esto no puede lanzar dentro de un middleware.
    expect(() => claveDeCuenta(req({ username: ['a', 'b'] }))).not.toThrow();
    expect(() => claveDeCuenta(req({ username: 42 }))).not.toThrow();
  });

  it('cuentas distintas no comparten cubo', () => {
    // Lo contrario del test anterior: que no se agrupe de más. Si todas las
    // cuentas cayeran en el mismo cubo, veinte intentos contra cualquiera
    // bloquearían el inicio de sesión de todo el mundo.
    expect(claveDeCuenta(req({ username: 'juan' })))
      .not.toBe(claveDeCuenta(req({ username: 'ana' })));
  });

  it('el nombre inventado también cuenta', () => {
    // No se consulta la base de datos: si solo se contaran los usuarios
    // reales, la diferencia de comportamiento entre un nombre registrado y uno
    // inventado permitiría enumerarlos.
    expect(claveDeCuenta(req({ username: 'no-existe-jamas' }))).toBe('no-existe-jamas');
  });
});

describe('resolverCuentaLimit', () => {
  it('sin variable usa el valor por defecto', () => {
    expect(resolverCuentaLimit({})).toBe(CUENTA_LIMIT_POR_DEFECTO);
  });

  it('fuera de producción la variable manda', () => {
    expect(resolverCuentaLimit({ ACCOUNT_RATE_LIMIT: '500' })).toBe(500);
  });

  it('en producción la variable se IGNORA', () => {
    // Un límite que se afloja desde el panel de despliegue no es un límite.
    expect(
      resolverCuentaLimit({ ACCOUNT_RATE_LIMIT: '100000', NODE_ENV: 'production' }),
    ).toBe(CUENTA_LIMIT_POR_DEFECTO);
  });

  it.each([['no-numero'], ['0'], ['-5'], ['3.5']])(
    'un valor inválido (%s) cae al por defecto',
    (valor) => {
      expect(resolverCuentaLimit({ ACCOUNT_RATE_LIMIT: valor })).toBe(CUENTA_LIMIT_POR_DEFECTO);
    },
  );

  it('el límite por cuenta es más holgado que el de IP', () => {
    // A propósito: el de cuenta puede bloquear a un usuario legítimo si alguien
    // lo ataca aposta, así que tiene que quedar lejos de lo que alcanza quien
    // solo se equivoca al teclear.
    expect(CUENTA_LIMIT_POR_DEFECTO).toBeGreaterThan(AUTH_LIMIT_POR_DEFECTO);
  });
});
