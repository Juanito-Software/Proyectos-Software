import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AuthForm from './AuthForm';
import { MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH } from '../constants';

/**
 * El formulario de acceso, con dos comportamientos distintos según el modo.
 *
 * Lo que más importa comprobar aquí es que la confirmación **no llega a la
 * API**: es una preocupación del formulario y no forma parte del contrato.
 */

const FRASE = 'caballo correcto grapa pila';

const renderRegistro = (props = {}) =>
  render(<AuthForm mode="register" onSubmit={vi.fn()} onSwitch={vi.fn()} {...props} />);

const renderLogin = (props = {}) =>
  render(<AuthForm mode="login" onSubmit={vi.fn()} onSwitch={vi.fn()} {...props} />);

describe('modo login', () => {
  it('no muestra el campo de confirmación', () => {
    renderLogin();
    expect(screen.queryByLabelText('Repite la contraseña')).not.toBeInTheDocument();
  });

  it('no impone longitud mínima: las cuentas antiguas deben poder entrar', () => {
    renderLogin();
    // Si el formulario exigiera 15 aquí, quien se registró con la política
    // anterior no podría iniciar sesión.
    expect(screen.getByLabelText('Contraseña')).not.toHaveAttribute('minLength');
  });

  it('entrega usuario y contraseña al enviar', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderLogin({ onSubmit });

    await user.type(screen.getByLabelText('Usuario'), 'juan');
    await user.type(screen.getByLabelText('Contraseña'), 'lo que sea');
    await user.click(screen.getByRole('button', { name: /entrar/i }));

    expect(onSubmit).toHaveBeenCalledWith('juan', 'lo que sea');
  });
});

describe('modo registro', () => {
  it('muestra el campo de confirmación', () => {
    renderRegistro();
    expect(screen.getByLabelText('Repite la contraseña')).toBeInTheDocument();
  });

  it(`exige la longitud mínima de ${MIN_PASSWORD_LENGTH}`, () => {
    renderRegistro();
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute(
      'minLength',
      String(MIN_PASSWORD_LENGTH),
    );
  });

  it(`limita al máximo técnico de ${MAX_PASSWORD_LENGTH}`, () => {
    renderRegistro();
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute(
      'maxLength',
      String(MAX_PASSWORD_LENGTH),
    );
  });

  it('NO usa pattern: exigir composición contradiría la política', () => {
    // Este test existe para impedir que alguien añada un pattern con
    // "al menos una mayúscula, un número y un símbolo" más adelante.
    renderRegistro();
    expect(screen.getByLabelText('Contraseña')).not.toHaveAttribute('pattern');
  });

  it('sugiere usar una frase, porque 15 caracteres lo piden', () => {
    renderRegistro();
    expect(screen.getByText(/frase que recuerdes/i)).toBeInTheDocument();
  });

  it('entrega SOLO usuario y contraseña: la confirmación no viaja', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await user.type(screen.getByLabelText('Usuario'), 'nueva');
    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(screen.getByLabelText('Repite la contraseña'), FRASE);
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(onSubmit).toHaveBeenCalledWith('nueva', FRASE);
    expect(onSubmit).toHaveBeenCalledTimes(1);
    // Dos argumentos exactos: nada de un tercero con la confirmación.
    expect(onSubmit.mock.calls[0]).toHaveLength(2);
  });

  it('acepta una frase larga sin mayúsculas, números ni símbolos', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await user.type(screen.getByLabelText('Usuario'), 'nueva');
    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(screen.getByLabelText('Repite la contraseña'), FRASE);
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(onSubmit).toHaveBeenCalled();
  });
});

describe('confirmación de contraseña', () => {
  it('avisa en cuanto las contraseñas dejan de coincidir', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'otra cosa');

    expect(screen.getByText(/no coinciden/i)).toBeInTheDocument();
  });

  it('no avisa mientras el segundo campo está vacío', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), FRASE);

    // Avisar antes de que se escriba nada sería ruido.
    expect(screen.queryByText(/no coinciden/i)).not.toBeInTheDocument();
  });

  it('deshabilita el botón mientras no coincidan', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'distinta');

    expect(screen.getByRole('button', { name: /registrarse/i })).toBeDisabled();
  });

  it('no llama a onSubmit si no coinciden', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await user.type(screen.getByLabelText('Usuario'), 'nueva');
    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'distinta');
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('vuelve a habilitar el botón cuando se corrige', async () => {
    const user = userEvent.setup();
    renderRegistro();

    const confirmacion = screen.getByLabelText('Repite la contraseña');
    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(confirmacion, 'distinta');
    expect(screen.getByRole('button', { name: /registrarse/i })).toBeDisabled();

    await user.clear(confirmacion);
    await user.type(confirmacion, FRASE);
    expect(screen.getByRole('button', { name: /registrarse/i })).toBeEnabled();
  });

  it('marca el campo como inválido para lectores de pantalla', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), FRASE);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'distinta');

    expect(screen.getByLabelText('Repite la contraseña')).toHaveAttribute('aria-invalid', 'true');
  });
});

describe('errores del servidor', () => {
  it('muestra el error recibido por props', () => {
    renderLogin({ error: 'Usuario o contraseña incorrectos' });
    expect(screen.getByText('Usuario o contraseña incorrectos')).toBeInTheDocument();
  });

  it('una contraseña corta no llega a enviarse', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    const corta = 'melon y sandia'; // 14, uno menos del mínimo
    await user.type(screen.getByLabelText('Usuario'), 'nueva');
    await user.type(screen.getByLabelText('Contraseña'), corta);
    await user.type(screen.getByLabelText('Repite la contraseña'), corta);
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    // Lo bloquea el minLength del propio campo, antes incluso de llegar al
    // manejador. La comprobación que hay en el manejador se mantiene como
    // segunda barrera —por si el atributo se pierde o el navegador autocompleta
    // el campo— pero no es la que actúa aquí.
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
