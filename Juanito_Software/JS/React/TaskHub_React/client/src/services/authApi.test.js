import { describe, it, expect, vi } from 'vitest';
import { login, register, refreshSession, logout, logoutAll } from './authApi';

/**
 * Autenticación: la parte del cliente donde un fallo silencioso es más caro.
 * Si el envoltorio de respuesta no se abre bien, el contexto guarda un objeto
 * sin token y la sesión parece iniciada pero ninguna petición funciona.
 */

function mockFetch(status, body) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
}

const sobre = (data) => ({ success: true, data, timestamp: '2026-01-01T00:00:00.000Z' });

describe('login', () => {
  it('devuelve { user, token } desenvuelto', async () => {
    const data = { user: { id: '1', username: 'juan', role: 'user' }, accessToken: 'jwt-abc' };
    global.fetch = mockFetch(200, sobre(data));

    const resultado = await login('juan', 'Frase de paso valida 7!');

    expect(resultado.accessToken).toBe('jwt-abc');
    expect(resultado.user.username).toBe('juan');
    expect(resultado.success).toBeUndefined();
  });

  it('manda usuario y contraseña como JSON al endpoint correcto', async () => {
    global.fetch = mockFetch(200, sobre({ user: {}, accessToken: 't' }));
    await login('juan', 'Frase de paso valida 7!');

    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/auth/login');
    expect(options.method).toBe('POST');
    expect(JSON.parse(options.body)).toEqual({ username: 'juan', password: 'Frase de paso valida 7!' });
  });

  it('propaga el mensaje del servidor cuando las credenciales fallan', async () => {
    global.fetch = mockFetch(401, {
      success: false,
      error: 'Usuario o contraseña incorrectos',
    });

    await expect(login('juan', 'mala')).rejects.toThrow('Usuario o contraseña incorrectos');
  });

  it('no manda la cabecera de autorización: aún no hay token', async () => {
    global.fetch = mockFetch(200, sobre({ user: {}, accessToken: 't' }));
    await login('juan', 'Frase de paso valida 7!');

    const { headers } = global.fetch.mock.calls[0][1];
    expect(headers.Authorization).toBeUndefined();
  });
});

describe('register', () => {
  it('devuelve el usuario creado con su rol', async () => {
    const data = { user: { id: '2', username: 'nueva', role: 'user' }, accessToken: 'jwt-x' };
    global.fetch = mockFetch(201, sobre(data));

    const resultado = await register('nueva', 'Frase de paso valida 7!');
    expect(resultado.user.role).toBe('user');
    expect(resultado.accessToken).toBe('jwt-x');
  });

  it('llama al endpoint de registro, no al de login', async () => {
    global.fetch = mockFetch(201, sobre({ user: {}, accessToken: 't' }));
    await register('nueva', 'Frase de paso valida 7!');

    expect(global.fetch.mock.calls[0][0]).toBe('/api/auth/register');
  });

  it('propaga el 409 de usuario ya existente', async () => {
    global.fetch = mockFetch(409, { success: false, error: 'El usuario ya existe' });
    await expect(register('juan', 'Frase de paso valida 7!')).rejects.toThrow('El usuario ya existe');
  });

  it('usa un mensaje por defecto si el servidor no manda ninguno', async () => {
    global.fetch = mockFetch(500, { success: false });
    await expect(register('x', 'Frase de paso valida 7!')).rejects.toThrow('Error al registrarse');
  });
});

describe('refreshSession', () => {
  it('devuelve las credenciales nuevas desenvueltas', async () => {
    global.fetch = mockFetch(200, sobre({ user: { id: '1' }, accessToken: 'jwt-nuevo' }));

    const resultado = await refreshSession();

    expect(resultado.accessToken).toBe('jwt-nuevo');
    expect(resultado.success).toBeUndefined();
  });

  it('no manda ningún cuerpo: el token va en la cookie', async () => {
    // Si el token de refresco viajara en el cuerpo, el JavaScript de la página
    // tendría que poder leerlo, y entonces HttpOnly no serviría de nada.
    global.fetch = mockFetch(200, sobre({ accessToken: 't' }));
    await refreshSession();

    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/auth/refresh');
    expect(options.method).toBe('POST');
    expect(options.body).toBeUndefined();
  });

  it('propaga el error cuando la sesión ya no vale', async () => {
    global.fetch = mockFetch(401, { success: false, error: 'Sesión inválida o expirada' });
    await expect(refreshSession()).rejects.toThrow('Sesión inválida o expirada');
  });

  it('usa un mensaje por defecto si el servidor no manda ninguno', async () => {
    global.fetch = mockFetch(500, { success: false });
    await expect(refreshSession()).rejects.toThrow('No se pudo renovar la sesión');
  });
});

describe('logout', () => {
  it('llama al endpoint de cierre de sesión', async () => {
    // Es la diferencia con la versión anterior, que solo vaciaba el estado
    // local: sin esta llamada el token de refresco seguiría vivo en el
    // servidor durante días.
    global.fetch = mockFetch(200, sobre(null));
    await logout();

    expect(global.fetch.mock.calls[0][0]).toBe('/api/auth/logout');
    expect(global.fetch.mock.calls[0][1].method).toBe('POST');
  });

  it('propaga el error si el servidor falla', async () => {
    global.fetch = mockFetch(500, { success: false });
    await expect(logout()).rejects.toThrow('No se pudo cerrar la sesión');
  });
});

describe('logoutAll', () => {
  it('manda el token de acceso: el servidor saca de ahí de quién son las sesiones', async () => {
    // El identificador nunca viaja en el cuerpo. Si lo hiciera, cualquiera
    // podría cerrar las sesiones de otro usuario.
    global.fetch = mockFetch(200, sobre({ revocadas: 3 }));
    const resultado = await logoutAll('jwt-abc');

    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/auth/logout-all');
    expect(options.headers.Authorization).toBe('Bearer jwt-abc');
    expect(options.body).toBeUndefined();
    expect(resultado.revocadas).toBe(3);
  });

  it('sin token no manda la cabecera de autorización', async () => {
    global.fetch = mockFetch(401, { success: false, error: 'Token de autenticación requerido' });
    await expect(logoutAll(null)).rejects.toThrow('Token de autenticación requerido');
    expect(global.fetch.mock.calls[0][1].headers.Authorization).toBeUndefined();
  });
});
