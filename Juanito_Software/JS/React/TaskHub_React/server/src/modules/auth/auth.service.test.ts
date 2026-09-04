import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { authService } from './auth.service.js';
import { sessionsRepository } from './sessions.repository.js';
import { usersRepository } from '../users/users.repository.js';
import { env } from '../../config/env.js';

/**
 * La lógica de sesión, probada sin base de datos.
 *
 * Aquí está lo que la suite de API **no puede** cubrir bien: la frontera entre
 * «dos pestañas renovando a la vez» y «alguien reutilizando un token robado» es
 * una diferencia de tiempo, y contra PostgreSQL real la única forma de cruzarla
 * es esperar diez segundos o retrasar la fila a mano. Con el repositorio
 * simulado se controla el reloj y se puede probar a los dos lados del borde, en
 * milisegundos.
 *
 * Lo que NO se prueba aquí es el SQL —la atomicidad de la rotación, las
 * cascadas, los índices—: eso solo tiene sentido contra la base de datos y lo
 * hace `npm run verify` con 130 comprobaciones.
 */

const USUARIO = {
  id: 'user-1',
  username: 'juan',
  role: 'user' as const,
  passwordHash: '$2b$12$hashquenoimporta',
  createdAt: '2026-01-01T00:00:00.000Z',
};

/** Fila de `refresh_sessions` con los valores que interesen. */
function sesion(overrides: Partial<{
  id: string;
  family_id: string;
  user_id: string;
  revoked_at: Date | null;
  revoked_reason: string | null;
}> = {}) {
  return {
    id: 'sess-1',
    family_id: 'fam-1',
    user_id: USUARIO.id,
    created_at: new Date(),
    expires_at: new Date(Date.now() + 7 * 24 * 3600_000),
    revoked_at: null,
    revoked_reason: null,
    ...overrides,
  };
}

let espias: Record<string, ReturnType<typeof vi.spyOn>>;

beforeEach(() => {
  vi.spyOn(console, 'warn').mockImplementation(() => {});
  espias = {
    marcarRotado: vi.spyOn(sessionsRepository, 'marcarRotado').mockResolvedValue(null),
    buscarPorHash: vi.spyOn(sessionsRepository, 'buscarPorHash').mockResolvedValue(null),
    encadenar: vi.spyOn(sessionsRepository, 'encadenar').mockResolvedValue(sesion()),
    crearFamilia: vi.spyOn(sessionsRepository, 'crearFamilia').mockResolvedValue(sesion()),
    revocarFamilia: vi.spyOn(sessionsRepository, 'revocarFamilia').mockResolvedValue(2),
    revocarTodas: vi
      .spyOn(sessionsRepository, 'revocarTodasDelUsuario')
      .mockResolvedValue(3),
    findById: vi.spyOn(usersRepository, 'findById').mockResolvedValue(USUARIO),
    findByUsername: vi.spyOn(usersRepository, 'findByUsername').mockResolvedValue(null),
    verifyPassword: vi.spyOn(usersRepository, 'verifyPassword').mockResolvedValue(false),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

/** Todas las líneas escritas por el registro de seguridad, ya parseadas. */
const eventos = () =>
  (console.warn as unknown as ReturnType<typeof vi.fn>).mock.calls.map((c) =>
    JSON.parse(String(c[0])),
  );

describe('renovación correcta', () => {
  it('rota el token y devuelve credenciales nuevas', async () => {
    espias.marcarRotado.mockResolvedValue(sesion());

    const resultado = await authService.refresh('token-valido');

    expect(resultado.accessToken).toBeTruthy();
    expect(resultado.refreshToken).toBeTruthy();
    expect(resultado.refreshToken).not.toBe('token-valido');
  });

  it('revoca el viejo ANTES de crear el nuevo', async () => {
    // El orden no es negociable: al revés, un fallo entre las dos operaciones
    // dejaría dos tokens válidos a la vez sobre la misma sesión.
    const orden: string[] = [];
    espias.marcarRotado.mockImplementation(async () => {
      orden.push('revocar');
      return sesion();
    });
    espias.encadenar.mockImplementation(async () => {
      orden.push('crear');
      return sesion();
    });

    await authService.refresh('token-valido');

    expect(orden).toEqual(['revocar', 'crear']);
  });

  it('el token nuevo se encadena a la MISMA familia', async () => {
    // Si naciera con familia propia, la detección de reutilización dejaría de
    // funcionar: no habría cadena que revocar.
    espias.marcarRotado.mockResolvedValue(sesion({ id: 'sess-7', family_id: 'fam-9' }));

    await authService.refresh('token-valido');

    expect(espias.encadenar).toHaveBeenCalledWith('fam-9', USUARIO.id, expect.any(String), 'sess-7');
  });

  it('deja rastro del refresco en el registro', async () => {
    espias.marcarRotado.mockResolvedValue(sesion());

    await authService.refresh('token-valido');

    expect(eventos().map((e) => e.evento)).toContain('refresh.correcto');
  });
});

describe('la frontera entre carrera y reutilización', () => {
  /**
   * El borde que da sentido a `REFRESH_GRACE_SECONDS`. A un lado hay un usuario
   * con dos pestañas; al otro, alguien con una copia del token.
   */

  it('DENTRO de la ventana: rechaza la petición pero NO mata la familia', async () => {
    espias.buscarPorHash.mockResolvedValue(
      sesion({ revoked_at: new Date(Date.now() - 1_000), revoked_reason: 'rotated' }),
    );

    await expect(authService.refresh('token-gastado')).rejects.toMatchObject({ statusCode: 401 });

    // Lo importante: la sesión sigue viva y la otra pestaña puede seguir.
    expect(espias.revocarFamilia).not.toHaveBeenCalled();
  });

  it('FUERA de la ventana: revoca la familia entera', async () => {
    espias.buscarPorHash.mockResolvedValue(
      sesion({
        revoked_at: new Date(Date.now() - env.refreshGraceMs - 1_000),
        revoked_reason: 'rotated',
      }),
    );

    await expect(authService.refresh('token-robado')).rejects.toMatchObject({ statusCode: 401 });

    expect(espias.revocarFamilia).toHaveBeenCalledWith('fam-1', 'reuse-detected');
  });

  it('justo en el límite cuenta como carrera, no como ataque', async () => {
    // La comparación es `<=`: en la duda, se protege al usuario legítimo. Un
    // atacante que acierte el milisegundo exacto es una hipótesis, echar a
    // alguien de su sesión es un problema real.
    //
    // **El reloj se congela a propósito.** Escrito con `Date.now()` a secas,
    // este test era intermitente y tardó tres ejecuciones en delatarse: la
    // marca de revocación se calculaba al preparar el doble y la resta la hacía
    // el servicio unos milisegundos después, así que la diferencia salía
    // `graceMs + 1` y caía del lado equivocado. Pasaba solo cuando las dos
    // lecturas del reloj caían en el mismo milisegundo. Un test del borde
    // exacto no puede depender de que el reloj no avance entre medias.
    vi.useFakeTimers();
    try {
      espias.buscarPorHash.mockResolvedValue(
        sesion({ revoked_at: new Date(Date.now() - env.refreshGraceMs), revoked_reason: 'rotated' }),
      );

      await authService.refresh('token-en-el-limite').catch(() => {});

      expect(espias.revocarFamilia).not.toHaveBeenCalled();
    } finally {
      vi.useRealTimers();
    }
  });

  it('un milisegundo MÁS ALLÁ del límite ya es reutilización', async () => {
    // El otro lado del borde, para que quede claro que la ventana termina en
    // algún sitio y no es una tolerancia infinita.
    vi.useFakeTimers();
    try {
      espias.buscarPorHash.mockResolvedValue(
        sesion({
          revoked_at: new Date(Date.now() - env.refreshGraceMs - 1),
          revoked_reason: 'rotated',
        }),
      );

      await authService.refresh('token-robado').catch(() => {});

      expect(espias.revocarFamilia).toHaveBeenCalledWith('fam-1', 'reuse-detected');
    } finally {
      vi.useRealTimers();
    }
  });

  it('la carrera también deja rastro, con su motivo', async () => {
    // Si estas líneas se disparan en avalancha, el problema está en el cliente.
    espias.buscarPorHash.mockResolvedValue(
      sesion({ revoked_at: new Date(Date.now() - 500), revoked_reason: 'rotated' }),
    );

    await authService.refresh('token-gastado').catch(() => {});

    expect(eventos()).toContainEqual(
      expect.objectContaining({ evento: 'refresh.rechazado', motivo: 'rotacion-simultanea' }),
    );
  });

  it('la reutilización se registra con cuántos tokens cayeron', async () => {
    espias.buscarPorHash.mockResolvedValue(
      sesion({
        revoked_at: new Date(Date.now() - env.refreshGraceMs - 60_000),
        revoked_reason: 'rotated',
      }),
    );
    espias.revocarFamilia.mockResolvedValue(4);

    await authService.refresh('token-robado').catch(() => {});

    expect(eventos()).toContainEqual(
      expect.objectContaining({ evento: 'refresh.reutilizacion', tokensRevocados: 4 }),
    );
  });
});

describe('tokens que ya no valen por otros motivos', () => {
  it('un token revocado por logout NO se trata como reutilización', async () => {
    // La sesión ya está muerta: no hay familia que salvar ni ataque que atajar,
    // y marcarla como reutilización ensuciaría el registro de seguridad con
    // ruido que no lo es.
    espias.buscarPorHash.mockResolvedValue(
      sesion({ revoked_at: new Date(Date.now() - 3600_000), revoked_reason: 'logout' }),
    );

    await authService.refresh('token-de-sesion-cerrada').catch(() => {});

    expect(espias.revocarFamilia).not.toHaveBeenCalled();
    expect(eventos().map((e) => e.evento)).not.toContain('refresh.reutilizacion');
  });

  it('tampoco uno revocado por una reutilización anterior', async () => {
    espias.buscarPorHash.mockResolvedValue(
      sesion({ revoked_at: new Date(Date.now() - 3600_000), revoked_reason: 'reuse-detected' }),
    );

    await authService.refresh('token-de-familia-muerta').catch(() => {});

    expect(espias.revocarFamilia).not.toHaveBeenCalled();
  });

  it('un token que no existe se rechaza sin revocar nada', async () => {
    espias.buscarPorHash.mockResolvedValue(null);

    await expect(authService.refresh('inventado')).rejects.toMatchObject({ statusCode: 401 });
    expect(espias.revocarFamilia).not.toHaveBeenCalled();
  });

  it.each([
    ['undefined', undefined],
    ['cadena vacía', ''],
  ])('sin cookie (%s) responde 401 sin tocar la base de datos', async (_caso, valor) => {
    await expect(authService.refresh(valor)).rejects.toMatchObject({ statusCode: 401 });
    expect(espias.marcarRotado).not.toHaveBeenCalled();
  });
});

describe('la cuenta desaparece con la sesión abierta', () => {
  it('rechaza y mata la familia en lugar de emitir un token huérfano', async () => {
    espias.marcarRotado.mockResolvedValue(sesion());
    espias.findById.mockResolvedValue(null);

    await expect(authService.refresh('token-de-cuenta-borrada')).rejects.toMatchObject({
      statusCode: 401,
    });

    expect(espias.revocarFamilia).toHaveBeenCalledWith('fam-1', 'logout');
    expect(espias.encadenar).not.toHaveBeenCalled();
  });

  it('lo registra con su motivo', async () => {
    espias.marcarRotado.mockResolvedValue(sesion());
    espias.findById.mockResolvedValue(null);

    await authService.refresh('token-de-cuenta-borrada').catch(() => {});

    expect(eventos()).toContainEqual(
      expect.objectContaining({ evento: 'refresh.rechazado', motivo: 'cuenta-borrada' }),
    );
  });
});

describe('cierre de sesión', () => {
  it('revoca la FAMILIA, no solo el token presentado', async () => {
    // Si quedara viva la última fila de la cadena, el logout no habría cerrado
    // nada: quien tuviera esa copia podría seguir renovando.
    espias.buscarPorHash.mockResolvedValue(sesion({ family_id: 'fam-3' }));

    await authService.logout('token-cualquiera');

    expect(espias.revocarFamilia).toHaveBeenCalledWith('fam-3', 'logout');
  });

  it('sin cookie no hace nada y no falla', async () => {
    await expect(authService.logout(undefined)).resolves.toBeUndefined();
    expect(espias.revocarFamilia).not.toHaveBeenCalled();
  });

  it('con un token desconocido tampoco falla', async () => {
    // El cliente solo necesita saber que puede olvidarse de sus credenciales.
    espias.buscarPorHash.mockResolvedValue(null);

    await expect(authService.logout('inventado')).resolves.toBeUndefined();
    expect(espias.revocarFamilia).not.toHaveBeenCalled();
  });

  it('el cierre global revoca todas las del usuario y devuelve cuántas', async () => {
    espias.revocarTodas.mockResolvedValue(5);

    await expect(authService.logoutAll('user-9')).resolves.toBe(5);
    expect(espias.revocarTodas).toHaveBeenCalledWith('user-9', 'logout-all');
  });
});

describe('inicio de sesión', () => {
  it('con usuario inexistente y con contraseña incorrecta da el MISMO mensaje', async () => {
    // Si difirieran, la respuesta serviría para averiguar qué nombres de
    // usuario existen.
    espias.findByUsername.mockResolvedValue(null);
    const sinUsuario = await authService.login({ username: 'nadie', password: 'x' }).catch((e) => e);

    espias.findByUsername.mockResolvedValue(USUARIO);
    espias.verifyPassword.mockResolvedValue(false);
    const malaClave = await authService.login({ username: 'juan', password: 'x' }).catch((e) => e);

    expect(sinUsuario.message).toBe(malaClave.message);
    expect(sinUsuario.statusCode).toBe(malaClave.statusCode);
  });

  it('pero el REGISTRO sí distingue los dos casos', async () => {
    // Es la asimetría buscada: al atacante se le oculta, al operador no. Saber
    // si atacan una cuenta que existe o prueban nombres al azar son dos cosas
    // distintas.
    espias.findByUsername.mockResolvedValue(null);
    await authService.login({ username: 'nadie', password: 'x' }).catch(() => {});

    espias.findByUsername.mockResolvedValue(USUARIO);
    await authService.login({ username: 'juan', password: 'x' }).catch(() => {});

    const motivos = eventos()
      .filter((e) => e.evento === 'login.fallido')
      .map((e) => e.motivo);

    expect(motivos).toEqual(['usuario-inexistente', 'credenciales-invalidas']);
  });

  it('el registro de un login fallido NO lleva la contraseña', async () => {
    espias.findByUsername.mockResolvedValue(USUARIO);

    await authService
      .login({ username: 'juan', password: 'Cafe con leche y 2 tostadas!' })
      .catch(() => {});

    expect(JSON.stringify(eventos())).not.toContain('Cafe con leche');
  });

  it('con credenciales correctas abre sesión y lo registra', async () => {
    espias.findByUsername.mockResolvedValue(USUARIO);
    espias.verifyPassword.mockResolvedValue(true);

    const resultado = await authService.login({ username: 'juan', password: 'la buena' });

    expect(resultado.accessToken).toBeTruthy();
    expect(espias.crearFamilia).toHaveBeenCalledTimes(1);
    expect(eventos().map((e) => e.evento)).toContain('login.correcto');
  });

  it('la respuesta del login NO lleva el hash de la contraseña', async () => {
    espias.findByUsername.mockResolvedValue(USUARIO);
    espias.verifyPassword.mockResolvedValue(true);

    const resultado = await authService.login({ username: 'juan', password: 'la buena' });

    expect(JSON.stringify(resultado.user)).not.toContain('$2b$');
  });

  it('recorta los espacios del nombre antes de buscarlo', async () => {
    espias.findByUsername.mockResolvedValue(null);

    await authService.login({ username: '  juan  ', password: 'x' }).catch(() => {});

    expect(espias.findByUsername).toHaveBeenCalledWith('juan');
  });
});

describe('registro', () => {
  /**
   * El alta corre dos riesgos que se cubren aquí: que el conflicto de usuario
   * repetido se convierta en un 500, y que la contraseña o su hash acaben en el
   * registro de seguridad. Lo segundo es lo que hace que estos logs se puedan
   * dejar encendidos en producción.
   */

  /**
   * Tal y como lo devuelve `usersRepository.create`: **sin `passwordHash`**. La
   * poda la hace `toPublic()` en el repositorio, no el servicio, así que aquí
   * el doble tiene que reflejarlo o los tests probarían un contrato que no
   * existe. (Escribí el doble con el hash dentro y el test de más abajo lo
   * cazó: buena señal de que ese test sirve para algo.)
   */
  const NUEVO = { id: 'user-9', username: 'nuevo', role: 'user' as const, createdAt: USUARIO.createdAt };

  it('crea el usuario y abre sesión de una vez', async () => {
    const create = vi.spyOn(usersRepository, 'create').mockResolvedValue(NUEVO);

    const r = await authService.register({ username: 'nuevo', password: 'Clave-Larguisima-2026!' });

    expect(create).toHaveBeenCalledWith('nuevo', 'Clave-Larguisima-2026!');
    expect(r.accessToken).toBeTruthy();
    expect(r.refreshToken).toBeTruthy();
    expect(espias.crearFamilia).toHaveBeenCalledTimes(1);
  });

  it('un usuario repetido da 409, no un error de PostgreSQL', async () => {
    // El repositorio devuelve null ante el choque del índice único; sin
    // traducirlo, el usuario vería un 500.
    vi.spyOn(usersRepository, 'create').mockResolvedValue(null);

    await expect(
      authService.register({ username: 'juan', password: 'Clave-Larguisima-2026!' }),
    ).rejects.toMatchObject({ statusCode: 409 });
  });

  it('recorta el nombre antes de crearlo', async () => {
    // Si no, «juan » y «juan» serían dos cuentas distintas y el índice único no
    // lo impediría.
    const create = vi.spyOn(usersRepository, 'create').mockResolvedValue(NUEVO);

    await authService.register({ username: '  nuevo  ', password: 'Clave-Larguisima-2026!' });

    expect(create).toHaveBeenCalledWith('nuevo', expect.any(String));
  });

  it('registra el alta como evento de seguridad', async () => {
    vi.spyOn(usersRepository, 'create').mockResolvedValue(NUEVO);

    await authService.register({ username: 'nuevo', password: 'Clave-Larguisima-2026!' });

    expect(eventos().map((e) => e.evento)).toContain('registro.correcto');
  });

  it('el evento NO contiene la contraseña ni el hash', async () => {
    vi.spyOn(usersRepository, 'create').mockResolvedValue(NUEVO);

    await authService.register({ username: 'nuevo', password: 'Clave-Larguisima-2026!' });

    const todo = JSON.stringify(eventos());
    expect(todo).not.toContain('Clave-Larguisima-2026!');
    expect(todo).not.toContain('$2b$');
  });

  it('tampoco contiene el token de refresco recién emitido', async () => {
    // El refresco es una credencial de siete días: en un log es tan grave como
    // la contraseña.
    vi.spyOn(usersRepository, 'create').mockResolvedValue(NUEVO);

    const r = await authService.register({ username: 'nuevo', password: 'Clave-Larguisima-2026!' });

    expect(JSON.stringify(eventos())).not.toContain(r.refreshToken);
  });

  it('un conflicto no deja una sesión abierta a medias', async () => {
    vi.spyOn(usersRepository, 'create').mockResolvedValue(null);

    await expect(
      authService.register({ username: 'juan', password: 'Clave-Larguisima-2026!' }),
    ).rejects.toThrow();
    expect(espias.crearFamilia).not.toHaveBeenCalled();
  });

  it('no añade campos al usuario que le da el repositorio', async () => {
    // El controlador serializa `user` tal cual. Si el servicio le pegara algo
    // por el camino —el hash, el token—, saldría en la respuesta.
    vi.spyOn(usersRepository, 'create').mockResolvedValue(NUEVO);

    const r = await authService.register({ username: 'nuevo', password: 'Clave-Larguisima-2026!' });

    expect(r.user).toEqual(NUEVO);
    expect(Object.keys(r.user)).not.toContain('passwordHash');
  });
});

describe('cambio de contraseña', () => {
  /**
   * Las cinco garantías que hacen que esta función sirva para algo. Cuatro de
   * ellas fallan en silencio si se rompen: la contraseña se cambiaría igual y
   * el usuario creería estar protegido.
   */

  const ACTUAL = 'La-que-tenia-antes-2026!';
  const NUEVA = 'Café con leche y 2 tostadas!';

  /**
   * El doble de `verifyPassword` mira **qué contraseña** le pasan.
   *
   * Escrito como `mockResolvedValue(true)` a secas decía que sí a todo, y eso
   * incluía la comprobación de «¿la nueva es igual que la actual?», con lo que
   * el caso feliz fallaba por un motivo inventado. El real compara un texto
   * concreto contra el hash guardado: si el doble no distingue, no está
   * imitando nada.
   */
  beforeEach(() => {
    espias.verifyPassword.mockImplementation(
      async (_user: unknown, password: unknown) => password === ACTUAL,
    );
    vi.spyOn(usersRepository, 'updatePassword').mockResolvedValue(true);
  });

  it('cambia la contraseña cuando la actual es correcta', async () => {
    const update = vi.spyOn(usersRepository, 'updatePassword').mockResolvedValue(true);

    await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    expect(update).toHaveBeenCalledWith(USUARIO.id, NUEVA);
  });

  it('exige la contraseña actual aunque ya haya sesión', async () => {
    // Sin esto, un token de acceso robado bastaría para quedarse con la cuenta
    // para siempre. Con esto, el robo solo dura lo que dure el token.
    espias.verifyPassword.mockResolvedValue(false);

    await expect(
      authService.changePassword(USUARIO.id, 'la-equivocada', NUEVA),
    ).rejects.toMatchObject({ statusCode: 401 });
  });

  it('si la actual falla, NO se toca la contraseña', async () => {
    const update = vi.spyOn(usersRepository, 'updatePassword').mockResolvedValue(true);
    espias.verifyPassword.mockResolvedValue(false);

    await authService.changePassword(USUARIO.id, 'mal', NUEVA).catch(() => {});

    expect(update).not.toHaveBeenCalled();
  });

  it('revoca TODAS las sesiones con su propio motivo', async () => {
    // El motivo importa: una avalancha de 'password-changed' en poco tiempo
    // significa algo muy distinto de una avalancha de 'logout'.
    await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    expect(espias.revocarTodas).toHaveBeenCalledWith(USUARIO.id, 'password-changed');
  });

  it('y deja al usuario dentro con credenciales nuevas', async () => {
    // Revocar todas incluiría la suya. Sin abrir una sesión nueva, el usuario
    // quedaría expulsado justo después de hacer lo correcto — y una medida de
    // seguridad incómoda es una medida que la gente evita.
    const r = await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    expect(r.accessToken).toBeTruthy();
    expect(r.refreshToken).toBeTruthy();
    expect(espias.crearFamilia).toHaveBeenCalledTimes(1);
  });

  it('la sesión nueva se abre DESPUÉS de revocar, no antes', async () => {
    // Al revés se revocaría la que se acaba de crear y el usuario saldría
    // igualmente. El orden es el único que funciona.
    const orden: string[] = [];
    espias.revocarTodas.mockImplementation(async () => {
      orden.push('revocar');
      return 2;
    });
    espias.crearFamilia.mockImplementation(async () => {
      orden.push('crear');
      return sesion();
    });

    await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    expect(orden).toEqual(['revocar', 'crear']);
  });

  it('rechaza una contraseña nueva que no cumple la política', async () => {
    await expect(
      authService.changePassword(USUARIO.id, ACTUAL, 'corta'),
    ).rejects.toMatchObject({ statusCode: 400 });
  });

  it('la política se aplica CON el nombre de usuario', async () => {
    // Una contraseña que contiene el nombre de usuario se rechaza. El nombre
    // sale de la base de datos, no del cuerpo de la petición.
    await expect(
      authService.changePassword(USUARIO.id, ACTUAL, `${USUARIO.username}Aa1!${USUARIO.username}`),
    ).rejects.toMatchObject({ statusCode: 400 });
  });

  it('rechaza repetir la contraseña que ya tenía', async () => {
    // Se compara con bcrypt contra el hash guardado, no con los textos: el
    // texto de la actual es lo único que tenemos, y el de la nueva podría
    // coincidir sin ser literalmente igual. Aquí el doble dice que sí a las
    // dos, que es lo que haría bcrypt si fueran la misma.
    espias.verifyPassword.mockResolvedValue(true);

    await expect(
      authService.changePassword(USUARIO.id, ACTUAL, NUEVA),
    ).rejects.toMatchObject({ statusCode: 400 });
  });

  it('si la cuenta ya no existe, 401 y no 500', async () => {
    espias.findById.mockResolvedValue(null);

    await expect(
      authService.changePassword('fantasma', 'x', NUEVA),
    ).rejects.toMatchObject({ statusCode: 401 });
  });

  it('si la cuenta desaparece justo antes del UPDATE, tampoco es 500', async () => {
    // La carrera: existía al comprobar y ya no al escribir.
    vi.spyOn(usersRepository, 'updatePassword').mockResolvedValue(false);

    await expect(
      authService.changePassword(USUARIO.id, ACTUAL, NUEVA),
    ).rejects.toMatchObject({ statusCode: 401 });
  });

  it('registra el cambio como evento de seguridad', async () => {
    await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    expect(eventos()).toContainEqual(
      expect.objectContaining({ evento: 'password.cambiada', usuario: USUARIO.username }),
    );
  });

  it('registra también el intento fallido, que es la señal que importa', async () => {
    // Varios de estos seguidos con un token válido significan que alguien está
    // probando la contraseña actual a ciegas.
    espias.verifyPassword.mockResolvedValue(false);

    await authService.changePassword(USUARIO.id, 'mal', NUEVA).catch(() => {});

    expect(eventos()).toContainEqual(
      expect.objectContaining({
        evento: 'password.cambio-rechazado',
        motivo: 'actual-incorrecta',
      }),
    );
  });

  it('ningún registro contiene las contraseñas', async () => {
    await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    const todo = JSON.stringify(eventos());
    expect(todo).not.toContain(NUEVA);
    expect(todo).not.toContain(ACTUAL);
  });

  it('el usuario devuelto no lleva el hash', async () => {
    const r = await authService.changePassword(USUARIO.id, ACTUAL, NUEVA);

    expect(JSON.stringify(r.user)).not.toContain('$2b$');
  });
});
