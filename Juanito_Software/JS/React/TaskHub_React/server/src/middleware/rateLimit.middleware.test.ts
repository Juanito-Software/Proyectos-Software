import { describe, it, expect } from 'vitest';
import {
  resolverAuthLimit,
  AUTH_LIMIT_POR_DEFECTO,
  claveDeCuenta,
  resolverCuentaLimit,
  CUENTA_LIMIT_POR_DEFECTO,
  calcularRetraso,
  RETRASO_DESDE,
  RETRASO_MAXIMO_MS,
  resolverRetrasoDesde,
  retrasoDelMiddleware,
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

describe('retrasos progresivos', () => {
  /**
   * La curva es toda la defensa, así que se fija entera.
   *
   * Si `calcularRetraso` devolviera siempre cero, el middleware seguiría
   * montado, el pipeline seguiría en verde y la protección habría desaparecido
   * sin dejar rastro. Es exactamente el tipo de fallo que no se ve en una
   * revisión por encima.
   */

  it.each([
    [1, 0],
    [2, 0],
    [3, 0],
    [4, 1_000],
    [5, 2_000],
    [6, 4_000],
    [7, 8_000],
    [8, 16_000],
  ])('con %i intentos fallidos, retraso de %i ms', (intentos, esperado) => {
    expect(calcularRetraso(intentos)).toBe(esperado);
  });

  it('los primeros intentos son gratis', () => {
    // Quien conoce su contraseña acierta a la primera o segunda. Si el retraso
    // empezara en el primer fallo, castigaríamos a todo el mundo por una errata.
    for (let i = 0; i <= RETRASO_DESDE; i++) {
      expect(calcularRetraso(i)).toBe(0);
    }
  });

  it('nunca supera el techo', () => {
    // Sin tope, el retraso se dispararía a horas y el servidor acabaría con
    // conexiones abiertas eternamente. Además, un proxy inverso con tiempo de
    // espera propio cortaría antes.
    for (const intentos of [9, 10, 20, 100, 1_000]) {
      expect(calcularRetraso(intentos)).toBe(RETRASO_MAXIMO_MS);
    }
  });

  it('la curva es monótona: nunca baja', () => {
    let anterior = -1;
    for (let i = 0; i <= 30; i++) {
      const actual = calcularRetraso(i);
      expect(actual).toBeGreaterThanOrEqual(anterior);
      anterior = actual;
    }
  });

  it('un número de intentos negativo o cero no da retraso negativo', () => {
    // No debería ocurrir, pero un retraso negativo pasado a setTimeout haría
    // cosas raras en vez de fallar a la vista.
    expect(calcularRetraso(0)).toBe(0);
    expect(calcularRetraso(-5)).toBe(0);
  });

  it('el umbral es configurable y desplaza la curva entera', () => {
    expect(calcularRetraso(4, 10)).toBe(0);
    expect(calcularRetraso(11, 10)).toBe(1_000);
    expect(calcularRetraso(12, 10)).toBe(2_000);
  });

  it('la fuerza bruta deja de ser viable: menos de 200 intentos por hora', () => {
    // La cuenta que justifica el diseño. Con el retraso en su techo, un atacante
    // que martillee sin parar durante una hora no pasa de este número — frente a
    // los miles por minuto que conseguiría sin retraso.
    const porHora = 3_600_000 / RETRASO_MAXIMO_MS;

    expect(porHora).toBeLessThan(200);
  });

  it('el tope duro queda muy por encima de lo alcanzable en una ventana', () => {
    // Es lo que convierte el bloqueo en un caso patológico y no en un arma:
    // llegar a él dentro de la ventana de quince minutos es imposible con los
    // retrasos puestos.
    const alcanzablesEnLaVentana = (15 * 60 * 1000) / RETRASO_MAXIMO_MS;

    expect(alcanzablesEnLaVentana).toBeLessThan(CUENTA_LIMIT_POR_DEFECTO);
  });
});

describe('resolverRetrasoDesde', () => {
  it('sin variable usa el valor por defecto', () => {
    expect(resolverRetrasoDesde({})).toBe(RETRASO_DESDE);
  });

  it('fuera de producción la variable manda', () => {
    // Es lo que permite a la suite de API apagar los retrasos y comprobar el
    // tope duro en segundos en vez de en minutos.
    expect(resolverRetrasoDesde({ ACCOUNT_SLOWDOWN_AFTER: '10000' })).toBe(10000);
  });

  it('en producción la variable se IGNORA', () => {
    // El caso que importa: un retraso que se apaga desde el panel de despliegue
    // deja la fuerza bruta a velocidad completa.
    expect(
      resolverRetrasoDesde({ ACCOUNT_SLOWDOWN_AFTER: '999999', NODE_ENV: 'production' }),
    ).toBe(RETRASO_DESDE);
  });

  it.each([['no-numero'], ['0'], ['-3'], ['2.5']])(
    'un valor inválido (%s) cae al por defecto',
    (valor) => {
      expect(resolverRetrasoDesde({ ACCOUNT_SLOWDOWN_AFTER: valor })).toBe(RETRASO_DESDE);
    },
  );
});

describe('retrasoDelMiddleware', () => {
  /**
   * Es la función que la librería llama en cada petición. Estaba escrita como
   * lambda dentro de la configuración y ningún test la alcanzaba: el umbral de
   * cobertura de funciones lo detectó al bajar del 98%, que es exactamente para
   * lo que está puesto.
   */

  it('aplica la misma curva que calcularRetraso', () => {
    for (const intentos of [0, 1, 3, 4, 5, 8, 100]) {
      expect(retrasoDelMiddleware(intentos)).toBe(calcularRetraso(intentos));
    }
  });

  it('respeta el techo', () => {
    expect(retrasoDelMiddleware(1_000)).toBe(RETRASO_MAXIMO_MS);
  });

  it('no retrasa los primeros intentos', () => {
    expect(retrasoDelMiddleware(1)).toBe(0);
  });
});
