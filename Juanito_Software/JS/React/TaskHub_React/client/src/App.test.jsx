import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import * as authApi from './services/authApi';
import * as api from './services/api';

/**
 * El enrutado de la aplicación: formulario de acceso o lista de tareas, según
 * haya sesión.
 *
 * Es poco código pero decide qué ve el usuario, y guarda el modo del formulario
 * —entrar o registrarse—, que es de donde salía uno de los fallos de
 * experiencia de uso que se arreglan aquí.
 */

const PASSWORD = 'Cafe con leche y 2 tostadas!';
const STORAGE_KEY = 'taskhub_auth';

let espias;

beforeEach(() => {
  localStorage.clear();
  espias = {
    login: vi.spyOn(authApi, 'login').mockResolvedValue(undefined),
    register: vi.spyOn(authApi, 'register').mockResolvedValue(undefined),
    logout: vi.spyOn(authApi, 'logout').mockResolvedValue(undefined),
    refreshSession: vi.spyOn(authApi, 'refreshSession').mockResolvedValue(undefined),
    getTasks: vi.spyOn(api, 'getTasks').mockResolvedValue([]),
  };
});

afterEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

/** Rellena el formulario de acceso y envía. */
async function entrar(user, { registrando = false } = {}) {
  await user.type(screen.getByLabelText('Usuario'), 'juan');
  await user.type(screen.getByLabelText('Contraseña'), PASSWORD);
  if (registrando) {
    await user.type(screen.getByLabelText('Repite la contraseña'), PASSWORD);
  }
  await user.click(
    screen.getByRole('button', { name: registrando ? /registrarse/i : /entrar/i }),
  );
}

describe('qué pantalla se ve', () => {
  it('sin sesión, el formulario de acceso', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: /iniciar sesión/i })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'TaskHub' })).not.toBeInTheDocument();
  });

  it('arranca en modo entrar, no en registro', () => {
    render(<App />);
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument();
    expect(screen.queryByLabelText('Repite la contraseña')).not.toBeInTheDocument();
  });

  it('con sesión, la lista de tareas', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });

    render(<App />);
    await entrar(user);

    expect(await screen.findByRole('heading', { name: 'TaskHub' })).toBeInTheDocument();
    expect(screen.queryByLabelText('Usuario')).not.toBeInTheDocument();
  });
});

describe('cambiar entre entrar y registrarse', () => {
  it('el enlace lleva al registro', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /regístrate/i }));

    expect(screen.getByRole('heading', { name: /crear cuenta/i })).toBeInTheDocument();
    expect(screen.getByLabelText('Repite la contraseña')).toBeInTheDocument();
  });

  it('y vuelve al inicio de sesión', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /regístrate/i }));
    await user.click(screen.getByRole('button', { name: /inicia sesión/i }));

    expect(screen.getByRole('heading', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('en modo entrar llama a login, no a register', async () => {
    const user = userEvent.setup();
    espias.login.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });

    render(<App />);
    await entrar(user);

    expect(espias.login).toHaveBeenCalledWith('juan', PASSWORD);
    expect(espias.register).not.toHaveBeenCalled();
  });

  it('en modo registro llama a register, no a login', async () => {
    const user = userEvent.setup();
    espias.register.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });

    render(<App />);
    await user.click(screen.getByRole('button', { name: /regístrate/i }));
    await entrar(user, { registrando: true });

    expect(espias.register).toHaveBeenCalledWith('juan', PASSWORD);
    expect(espias.login).not.toHaveBeenCalled();
  });
});

describe('errores de acceso', () => {
  it('muestra el mensaje que devuelve el servidor', async () => {
    const user = userEvent.setup();
    espias.login.mockRejectedValue(new Error('Usuario o contraseña incorrectos'));

    render(<App />);
    await entrar(user);

    expect(await screen.findByText('Usuario o contraseña incorrectos')).toBeInTheDocument();
  });

  it('el error se borra al cambiar de modo', async () => {
    // Arrastrar "usuario o contraseña incorrectos" a la pantalla de registro
    // no tiene sentido: es de la operación anterior.
    const user = userEvent.setup();
    espias.login.mockRejectedValue(new Error('Usuario o contraseña incorrectos'));

    render(<App />);
    await entrar(user);
    await screen.findByText('Usuario o contraseña incorrectos');

    await user.click(screen.getByRole('button', { name: /regístrate/i }));

    expect(screen.queryByText('Usuario o contraseña incorrectos')).not.toBeInTheDocument();
  });

  it('un registro fallido deja al usuario en el formulario', async () => {
    const user = userEvent.setup();
    espias.register.mockRejectedValue(new Error('El usuario ya existe'));

    render(<App />);
    await user.click(screen.getByRole('button', { name: /regístrate/i }));
    await entrar(user, { registrando: true });

    expect(await screen.findByText('El usuario ya existe')).toBeInTheDocument();
    expect(screen.getByLabelText('Usuario')).toBeInTheDocument();
  });
});

describe('al cerrar sesión, el formulario vuelve a modo entrar', () => {
  /**
   * El fallo que se arregla aquí.
   *
   * Antes el modo se quedaba como estuviera: quien acababa de registrarse y
   * pulsaba Salir se encontraba otra vez «Crear cuenta», con su campo de
   * confirmación y sus cuatro requisitos de contraseña, cuando lo que casi
   * siempre quiere en ese momento es volver a entrar.
   */
  async function registrarseYSalir(user) {
    espias.register.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });

    render(<App />);
    await user.click(screen.getByRole('button', { name: /regístrate/i }));
    await entrar(user, { registrando: true });
    await screen.findByRole('heading', { name: 'TaskHub' });

    await user.click(screen.getByRole('button', { name: /salir/i }));
    await screen.findByLabelText('Usuario');
  }

  it('el botón dice Entrar y no Registrarse', async () => {
    const user = userEvent.setup();
    await registrarseYSalir(user);

    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Registrarse' })).not.toBeInTheDocument();
  });

  it('no queda el campo de confirmación', async () => {
    const user = userEvent.setup();
    await registrarseYSalir(user);

    expect(screen.queryByLabelText('Repite la contraseña')).not.toBeInTheDocument();
  });

  it('tampoco la lista de requisitos de contraseña', async () => {
    const user = userEvent.setup();
    await registrarseYSalir(user);

    expect(screen.queryByText(/al menos una letra mayúscula/i)).not.toBeInTheDocument();
  });

  it('lo mismo si la sesión caduca estando dentro', async () => {
    // No solo al pulsar Salir: si el refresco falla, se acaba en la misma
    // pantalla y debe estar igual de limpia.
    const user = userEvent.setup();
    espias.register.mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt' });

    render(<App />);
    await user.click(screen.getByRole('button', { name: /regístrate/i }));
    await entrar(user, { registrando: true });
    await screen.findByRole('heading', { name: 'TaskHub' });

    // La renovación automática falla: la sesión se pierde.
    espias.refreshSession.mockRejectedValue(new Error('Sesión inválida o expirada'));
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: { username: 'juan' }, token: 'x' }));
    await user.click(screen.getByRole('button', { name: /salir/i }));

    await waitFor(() => expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument());
  });

  it('estando fuera, seguir en registro NO se revierte solo', async () => {
    // El reinicio es al perder la sesión, no en cada render: quien pulsa
    // "Regístrate" tiene que poder quedarse ahí.
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /regístrate/i }));
    await user.type(screen.getByLabelText('Usuario'), 'juan');

    expect(screen.getByRole('button', { name: 'Registrarse' })).toBeInTheDocument();
  });
});
