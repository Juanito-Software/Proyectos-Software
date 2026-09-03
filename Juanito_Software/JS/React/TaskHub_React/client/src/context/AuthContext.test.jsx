import { useState } from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './AuthContext';

/**
 * El contexto de sesión.
 *
 * Con tokens de acceso de quince minutos, este componente pasa a tener
 * responsabilidades que antes no tenía: renovar al arrancar, mantener el token
 * guardado al día cuando la capa de servicios renueva por su cuenta, y cerrar
 * sesión **en el servidor** y no solo en el navegador.
 */

import * as authApi from '../services/authApi';
import * as api from '../services/api';

/**
 * Las llamadas a la red se interceptan con espías sobre el módulo real, no con
 * `vi.mock`.
 *
 * `vi.mock` registra la sustitución en el registro de módulos, que se comparte
 * entre archivos cuando la suite corre sin aislamiento. Eso hacía que este
 * archivo rompiera a `api.refresh.test.js`, que necesita el módulo de verdad, y
 * el resultado dependía del orden en que se ejecutaran. Un espía se instala y
 * se retira dentro de este archivo y no puede afectar a ningún otro.
 */
function espiar() {
  return {
    login: vi.spyOn(authApi, 'login').mockResolvedValue(undefined),
    register: vi.spyOn(authApi, 'register').mockResolvedValue(undefined),
    logout: vi.spyOn(authApi, 'logout').mockResolvedValue(undefined),
    refreshSession: vi.spyOn(authApi, 'refreshSession').mockResolvedValue(undefined),
    setAuthToken: vi.spyOn(api, 'setAuthToken').mockImplementation(() => {}),
    configurarAuth: vi.spyOn(api, 'configurarAuth').mockImplementation(() => {}),
  };
}

let espias;
const setAuthToken = () => espias.setAuthToken;
const configurarAuth = () => espias.configurarAuth;

const STORAGE_KEY = 'taskhub_auth';

/**
 * Componente de prueba que muestra el estado y expone las acciones.
 *
 * Los errores se recogen aquí, igual que hace `App.jsx` en la aplicación real:
 * el contexto los propaga a propósito para que el componente decida qué
 * enseñar. Sin este `catch`, un login fallido acabaría en una promesa
 * rechazada sin capturar.
 */
function Sonda() {
  const { user, token, isAuthenticated, login, register, logout } = useAuth();
  const [error, setError] = useState(null);

  const intentar = (accion) => () => {
    setError(null);
    accion().catch((err) => setError(err.message));
  };

  return (
    <div>
      <span data-testid="usuario">{user?.username ?? 'sin usuario'}</span>
      <span data-testid="token">{token ?? 'sin token'}</span>
      <span data-testid="autenticado">{isAuthenticated ? 'sí' : 'no'}</span>
      <span data-testid="error">{error ?? 'sin error'}</span>
      <button onClick={intentar(() => login('juan', 'Clave larga 7!'))}>entrar</button>
      <button onClick={intentar(() => register('nueva', 'Clave larga 7!'))}>registrarse</button>
      <button onClick={intentar(() => logout())}>salir</button>
    </div>
  );
}

const montar = () =>
  render(
    <AuthProvider>
      <Sonda />
    </AuthProvider>,
  );

beforeEach(() => {
  localStorage.clear();
  espias = espiar();
});

afterEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe('estado inicial', () => {
  it('empieza sin sesión cuando no hay nada guardado', () => {
    montar();
    expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
    expect(screen.getByTestId('usuario')).toHaveTextContent('sin usuario');
  });

  it('no intenta renovar si no había sesión', () => {
    montar();
    expect(espias.refreshSession).not.toHaveBeenCalled();
  });

  it('sobrevive a un localStorage corrupto en lugar de romper la aplicación', () => {
    localStorage.setItem(STORAGE_KEY, '{no es json');
    expect(() => montar()).not.toThrow();
    expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
  });

  it('registra sus avisos en la capa de servicios', () => {
    // Sin esto, la renovación automática de api.js no llegaría nunca a React.
    montar();
    expect(configurarAuth()).toHaveBeenCalledWith(
      expect.objectContaining({
        alRenovar: expect.any(Function),
        alPerderSesion: expect.any(Function),
      }),
    );
  });
});

describe('renovación al arrancar', () => {
  it('con una sesión guardada, renueva antes de nada', async () => {
    // El token de acceso dura quince minutos, así que el guardado casi siempre
    // estará caducado al volver a la aplicación. Sin esta renovación, la
    // primera petición fallaría y se vería un parpadeo.
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: { username: 'juan' }, token: 'viejo' }));
    espias.refreshSession.mockResolvedValue({
      user: { username: 'juan' },
      accessToken: 'recien-renovado',
    });

    montar();

    await waitFor(() => {
      expect(screen.getByTestId('token')).toHaveTextContent('recien-renovado');
    });
    expect(espias.refreshSession).toHaveBeenCalledTimes(1);
  });

  it('si la renovación falla al arrancar, cierra la sesión sin ruido', async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: { username: 'juan' }, token: 'viejo' }));
    espias.refreshSession.mockRejectedValue(new Error('Sesión inválida o expirada'));

    montar();

    await waitFor(() => {
      expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
    });
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it('renueva una sola vez, no en bucle', async () => {
    // La renovación cambia el estado, y el estado es lo que dispara el efecto:
    // sin la lista de dependencias vacía, esto se realimentaría sin parar.
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: { username: 'juan' }, token: 'viejo' }));
    espias.refreshSession.mockResolvedValue({
      user: { username: 'juan' },
      accessToken: 'nuevo',
    });

    montar();

    await waitFor(() => expect(screen.getByTestId('token')).toHaveTextContent('nuevo'));
    await new Promise((r) => setTimeout(r, 50));
    expect(espias.refreshSession).toHaveBeenCalledTimes(1);
  });
});

describe('entrar y registrarse', () => {
  it('guarda usuario y token de acceso al entrar', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({
      user: { username: 'juan' },
      accessToken: 'jwt-acceso',
    });

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    expect(screen.getByTestId('usuario')).toHaveTextContent('juan');
    expect(screen.getByTestId('token')).toHaveTextContent('jwt-acceso');
    expect(screen.getByTestId('autenticado')).toHaveTextContent('sí');
  });

  it('persiste la sesión en localStorage', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt-acceso' });

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    await waitFor(() => {
      const guardado = JSON.parse(localStorage.getItem(STORAGE_KEY));
      expect(guardado.token).toBe('jwt-acceso');
    });
  });

  it('NO guarda el token de refresco: ni siquiera llega hasta aquí', async () => {
    // Viene en una cookie HttpOnly. Que no aparezca en localStorage es el
    // objetivo de todo el cambio.
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt-acceso' });

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    await waitFor(() => {
      expect(localStorage.getItem(STORAGE_KEY)).toContain('jwt-acceso');
    });
    expect(localStorage.getItem(STORAGE_KEY)).not.toContain('refresh');
  });

  it('avisa a la capa de servicios del token nuevo', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt-acceso' });

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    expect(setAuthToken()).toHaveBeenCalledWith('jwt-acceso');
  });

  it('registrarse deja la sesión iniciada igual que entrar', async () => {
    const user = userEvent.setup();
    espias.register.mockResolvedValue({ user: { username: 'nueva' }, accessToken: 'jwt-alta' });

    montar();
    await user.click(screen.getByRole('button', { name: 'registrarse' }));

    expect(screen.getByTestId('usuario')).toHaveTextContent('nueva');
    expect(screen.getByTestId('token')).toHaveTextContent('jwt-alta');
  });

  it('un login fallido no deja sesión a medias', async () => {
    const user = userEvent.setup();
    espias.login.mockRejectedValue(new Error('Usuario o contraseña incorrectos'));

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Usuario o contraseña incorrectos');
    });
    expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
  });
});

describe('cerrar sesión', () => {
  it('avisa al servidor antes de olvidar la sesión', async () => {
    // Lo importante del cambio: sin esta llamada, el token de refresco seguiría
    // sirviendo para sacar tokens de acceso nuevos durante días.
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });
    espias.logout.mockResolvedValue(null);

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));
    await user.click(screen.getByRole('button', { name: 'salir' }));

    expect(espias.logout).toHaveBeenCalledTimes(1);
    await waitFor(() => {
      expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
    });
  });

  it('cierra en local aunque el servidor no responda', async () => {
    // Dejar al usuario dentro porque falló la red sería peor: la sesión
    // huérfana del servidor caduca sola.
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });
    espias.logout.mockRejectedValue(new Error('Error de red'));
    vi.spyOn(console, 'warn').mockImplementation(() => {});

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));
    await user.click(screen.getByRole('button', { name: 'salir' }));

    await waitFor(() => {
      expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
    });
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it('limpia el token de la capa de servicios', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });
    espias.logout.mockResolvedValue(null);

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));
    await user.click(screen.getByRole('button', { name: 'salir' }));

    await waitFor(() => expect(setAuthToken()).toHaveBeenCalledWith(null));
  });
});

describe('avisos desde la capa de servicios', () => {
  /** Recupera los callbacks que el contexto registró en configurarAuth. */
  const avisos = () => configurarAuth().mock.calls.find(([arg]) => arg?.alRenovar)?.[0];

  it('una renovación automática actualiza el token guardado', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'viejo' });

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    act(() => {
      avisos().alRenovar({ user: { username: 'juan' }, accessToken: 'renovado' });
    });

    expect(screen.getByTestId('token')).toHaveTextContent('renovado');
  });

  it('perder la sesión devuelve al formulario', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });

    montar();
    await user.click(screen.getByRole('button', { name: 'entrar' }));

    act(() => avisos().alPerderSesion());

    expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
  });

  it('una renovación sin sesión activa no resucita nada', async () => {
    // Si llegara un aviso tardío después de cerrar sesión, no debe volver a
    // meter al usuario dentro.
    montar();

    act(() => {
      avisos().alRenovar({ user: { username: 'fantasma' }, accessToken: 'jwt' });
    });

    expect(screen.getByTestId('autenticado')).toHaveTextContent('no');
  });
});

describe('useAuth fuera del proveedor', () => {
  it('avisa con un error claro en lugar de devolver undefined', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<Sonda />)).toThrow(/dentro de AuthProvider/i);
  });
});
