import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChangePasswordForm from './ChangePasswordForm';
import { AuthProvider } from '../context/AuthContext';
import * as authApi from '../services/authApi';

/**
 * El formulario de cambio de contraseña.
 *
 * Lo que importa aquí no es que los campos existan, sino tres cosas que se
 * rompen sin hacer ruido:
 *
 * 1. **Que se pida la contraseña actual.** Es lo que impide que un token
 *    robado se convierta en la pérdida definitiva de la cuenta. Si alguien
 *    quitara ese campo «porque ya estás dentro», el formulario seguiría
 *    funcionando y la protección desaparecería.
 * 2. **Que se avise de que se cerrarán las demás sesiones antes de enviar.**
 *    Una acción que expulsa dispositivos tiene que anunciarse mientras todavía
 *    se puede cancelar.
 * 3. **Que un fallo no deje el formulario en estado de éxito.**
 */

const VALIDA = 'Café con leche y 2 tostadas!';

function montar() {
  return render(
    <AuthProvider>
      <ChangePasswordForm />
    </AuthProvider>,
  );
}

/** Rellena los tres campos y envía. */
async function enviar(user, { actual = 'La-de-antes-2026!', nueva = VALIDA, repetir = null } = {}) {
  await user.type(screen.getByLabelText('Contraseña actual'), actual);
  await user.type(screen.getByLabelText('Contraseña nueva'), nueva);
  await user.type(screen.getByLabelText('Repite la contraseña nueva'), repetir ?? nueva);
  await user.click(screen.getByRole('button', { name: /cambiar contraseña/i }));
}

beforeEach(() => {
  localStorage.clear();
  vi.spyOn(authApi, 'refreshSession').mockRejectedValue(new Error('sin sesión'));
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('lo que el formulario exige', () => {
  it('pide la contraseña actual, no solo la nueva', () => {
    // Sin este campo, un token de acceso robado bastaría para quedarse con la
    // cuenta para siempre.
    montar();

    expect(screen.getByLabelText('Contraseña actual')).toBeInTheDocument();
  });

  it('pide la nueva dos veces', () => {
    montar();

    expect(screen.getByLabelText('Contraseña nueva')).toBeInTheDocument();
    expect(screen.getByLabelText('Repite la contraseña nueva')).toBeInTheDocument();
  });

  it('los tres campos son de tipo password', () => {
    // Un `type="text"` dejaría la contraseña a la vista de quien pase por
    // detrás, y el gestor de contraseñas no la reconocería.
    montar();

    for (const etiqueta of ['Contraseña actual', 'Contraseña nueva', 'Repite la contraseña nueva']) {
      expect(screen.getByLabelText(etiqueta)).toHaveAttribute('type', 'password');
    }
  });

  it('avisa de que se cerrarán las demás sesiones ANTES de enviar', () => {
    montar();

    expect(screen.getByText(/se cerrarán tus sesiones en el resto de dispositivos/i))
      .toBeInTheDocument();
  });
});

describe('validación antes de gastar una petición', () => {
  it('no envía si las dos nuevas no coinciden', async () => {
    const user = userEvent.setup();
    const api = vi.spyOn(authApi, 'changePassword');
    montar();

    await user.type(screen.getByLabelText('Contraseña actual'), 'La-de-antes-2026!');
    await user.type(screen.getByLabelText('Contraseña nueva'), VALIDA);
    await user.type(screen.getByLabelText('Repite la contraseña nueva'), 'otra-cosa');

    expect(screen.getByRole('button', { name: /cambiar contraseña/i })).toBeDisabled();
    expect(api).not.toHaveBeenCalled();
  });

  it('avisa en cuanto dejan de coincidir', async () => {
    const user = userEvent.setup();
    montar();

    await user.type(screen.getByLabelText('Contraseña nueva'), VALIDA);
    await user.type(screen.getByLabelText('Repite la contraseña nueva'), 'x');

    expect(await screen.findByRole('alert')).toHaveTextContent(/no coinciden/i);
  });

  it('no avisa antes de que se escriba nada en el segundo campo', async () => {
    // Saldría un error nada más empezar a teclear, que es ruido.
    const user = userEvent.setup();
    montar();

    await user.type(screen.getByLabelText('Contraseña nueva'), VALIDA);

    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('rechaza una contraseña nueva que no cumple la política', async () => {
    const user = userEvent.setup();
    const api = vi.spyOn(authApi, 'changePassword');
    montar();

    await enviar(user, { nueva: 'corta' });

    expect(api).not.toHaveBeenCalled();
  });

  it('rechaza repetir la contraseña actual', async () => {
    // Cambiar por la misma expulsaría todos los dispositivos para nada.
    const user = userEvent.setup();
    const api = vi.spyOn(authApi, 'changePassword');
    montar();

    await enviar(user, { actual: VALIDA, nueva: VALIDA });

    expect(await screen.findByText(/debe ser distinta de la actual/i)).toBeInTheDocument();
    expect(api).not.toHaveBeenCalled();
  });

  it('la lista de requisitos se va marcando al escribir', async () => {
    const user = userEvent.setup();
    const { container } = montar();

    expect(container.querySelectorAll('[data-cumplido="si"]')).toHaveLength(0);

    await user.type(screen.getByLabelText('Contraseña nueva'), VALIDA);

    expect(container.querySelectorAll('[data-cumplido="si"]')).toHaveLength(4);
  });
});

describe('envío', () => {
  it('manda actual y nueva, en ese orden', async () => {
    const user = userEvent.setup();
    const api = vi
      .spyOn(authApi, 'changePassword')
      .mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt-nuevo' });
    montar();

    await enviar(user, { actual: 'La-de-antes-2026!', nueva: VALIDA });

    expect(api).toHaveBeenCalledWith(null, 'La-de-antes-2026!', VALIDA);
  });

  it('al terminar confirma y vacía el formulario', async () => {
    const user = userEvent.setup();
    vi.spyOn(authApi, 'changePassword')
      .mockResolvedValue({ user: { username: 'juan' }, accessToken: 'jwt-nuevo' });
    montar();

    await enviar(user);

    expect(await screen.findByRole('status')).toHaveTextContent(/contraseña cambiada/i);
    expect(screen.queryByLabelText('Contraseña actual')).not.toBeInTheDocument();
  });

  it('un fallo del servidor se muestra y NO da por hecho el cambio', async () => {
    const user = userEvent.setup();
    vi.spyOn(authApi, 'changePassword').mockRejectedValue(
      new Error('La contraseña actual no es correcta'),
    );
    montar();

    await enviar(user);

    expect(await screen.findByText('La contraseña actual no es correcta')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    // El formulario sigue ahí para reintentar.
    expect(screen.getByLabelText('Contraseña actual')).toBeInTheDocument();
  });

  it('no se puede enviar dos veces mientras va la primera', async () => {
    // Dos cambios simultáneos dejarían al usuario con credenciales de la
    // primera respuesta y la contraseña de la segunda.
    const user = userEvent.setup();
    let resolver;
    const api = vi
      .spyOn(authApi, 'changePassword')
      .mockReturnValue(new Promise((r) => { resolver = r; }));
    montar();

    await enviar(user);
    await user.click(screen.getByRole('button', { name: /cambiando/i }));

    expect(api).toHaveBeenCalledTimes(1);
    resolver({ user: { username: 'juan' }, accessToken: 'jwt' });
  });

  it('los campos se deshabilitan mientras se envía', async () => {
    const user = userEvent.setup();
    vi.spyOn(authApi, 'changePassword').mockReturnValue(new Promise(() => {}));
    montar();

    await enviar(user);

    expect(screen.getByLabelText('Contraseña actual')).toBeDisabled();
  });
});

describe('botón de cancelar', () => {
  it('no aparece si no se pasa onDone', () => {
    montar();
    expect(screen.queryByRole('button', { name: /cancelar/i })).not.toBeInTheDocument();
  });

  it('y llama a onDone cuando se pulsa', async () => {
    const user = userEvent.setup();
    const onDone = vi.fn();
    render(
      <AuthProvider>
        <ChangePasswordForm onDone={onDone} />
      </AuthProvider>,
    );

    await user.click(screen.getByRole('button', { name: /cancelar/i }));

    expect(onDone).toHaveBeenCalledTimes(1);
  });
});
