import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AuthForm from './AuthForm';
import { MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH } from '../passwordPolicy';

/**
 * El formulario de acceso, con dos comportamientos distintos según el modo.
 *
 * Dos cosas importan por encima del resto:
 *
 * - Que la confirmación **no llega a la API**: es una preocupación del
 *   formulario y no forma parte del contrato.
 * - Que las cuatro reglas se exigen al registrarse y **ninguna** al entrar,
 *   porque las cuentas anteriores tienen que poder seguir accediendo.
 */

// Cumple los cuatro requisitos: 15+, mayúscula, número y símbolo.
const VALIDA = 'Cafe con leche y 2 tostadas!';

const renderRegistro = (props = {}) =>
  render(<AuthForm mode="register" onSubmit={vi.fn()} onSwitch={vi.fn()} {...props} />);

const renderLogin = (props = {}) =>
  render(<AuthForm mode="login" onSubmit={vi.fn()} onSwitch={vi.fn()} {...props} />);

/** Rellena el registro entero y envía. */
async function registrar(user, password, confirmacion = password) {
  await user.type(screen.getByLabelText('Usuario'), 'nueva');
  await user.type(screen.getByLabelText('Contraseña'), password);
  await user.type(screen.getByLabelText('Repite la contraseña'), confirmacion);
  await user.click(screen.getByRole('button', { name: /registrarse/i }));
}

describe('modo login', () => {
  it('no muestra el campo de confirmación', () => {
    renderLogin();
    expect(screen.queryByLabelText('Repite la contraseña')).not.toBeInTheDocument();
  });

  it('no impone longitud mínima: las cuentas antiguas deben poder entrar', () => {
    renderLogin();
    expect(screen.getByLabelText('Contraseña')).not.toHaveAttribute('minLength');
  });

  it('no impone composición: las cuentas antiguas deben poder entrar', () => {
    // Si el formulario exigiera aquí mayúscula, número y símbolo, quien se
    // registró con una frase de paso antes del cambio se quedaría fuera.
    renderLogin();
    expect(screen.getByLabelText('Contraseña')).not.toHaveAttribute('pattern');
  });

  it('no muestra la lista de requisitos', () => {
    renderLogin();
    expect(screen.queryByText(/al menos una letra mayúscula/i)).not.toBeInTheDocument();
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

describe('modo registro: atributos de la política', () => {
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

  it('usa pattern para las tres reglas de composición', () => {
    // La composición es una decisión propia de TaskHub, más estricta que NIST.
    // El pattern la traslada al navegador para avisar antes de enviar; el
    // servidor la vuelve a comprobar de todas formas.
    renderRegistro();
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('pattern');
  });

  it('el pattern acepta una contraseña válida y rechaza las que incumplen', () => {
    renderRegistro();
    const campo = screen.getByLabelText('Contraseña');

    campo.value = VALIDA;
    expect(campo.validity.patternMismatch).toBe(false);

    for (const mala of [
      'cafe con leche y 2 tostadas!', // sin mayúscula
      'Cafe con leche y tostadas!', // sin número
      'Cafe con leche y 2 tostadas', // sin símbolo
    ]) {
      campo.value = mala;
      expect(campo.validity.patternMismatch).toBe(true);
    }
  });

  it('describe el campo con la lista de requisitos para lectores de pantalla', () => {
    renderRegistro();
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute(
      'aria-describedby',
      'requisitos-password',
    );
  });
});

describe('lista de requisitos', () => {
  it('muestra los cuatro requisitos', () => {
    renderRegistro();
    expect(screen.getByText(/al menos 15 caracteres/i)).toBeInTheDocument();
    expect(screen.getByText(/al menos una letra mayúscula/i)).toBeInTheDocument();
    expect(screen.getByText(/al menos un número/i)).toBeInTheDocument();
    expect(screen.getByText(/al menos un símbolo/i)).toBeInTheDocument();
  });

  it('arranca con los cuatro sin cumplir', () => {
    renderRegistro();
    const cumplidos = document.querySelectorAll('[data-cumplido="si"]');
    expect(cumplidos).toHaveLength(0);
  });

  it('marca cada requisito según se va cumpliendo', async () => {
    const user = userEvent.setup();
    renderRegistro();
    const campo = screen.getByLabelText('Contraseña');

    // Solo minúsculas y suficientemente larga: cumple longitud, nada más.
    await user.type(campo, 'cafeconlecheytostadas');
    expect(document.querySelectorAll('[data-cumplido="si"]')).toHaveLength(1);

    await user.type(campo, 'A'); // ya hay mayúscula
    expect(document.querySelectorAll('[data-cumplido="si"]')).toHaveLength(2);

    await user.type(campo, '2'); // ya hay número
    expect(document.querySelectorAll('[data-cumplido="si"]')).toHaveLength(3);

    await user.type(campo, '!'); // ya hay símbolo
    expect(document.querySelectorAll('[data-cumplido="si"]')).toHaveLength(4);
  });

  it('el espacio no marca el requisito de símbolo', async () => {
    // Si lo marcara, una frase con espacios parecería cumplir sin llevar un
    // solo símbolo, y el usuario recibiría un rechazo del servidor sin
    // entender por qué.
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), 'Frase Con Espacios 2026');
    const pendientes = [...document.querySelectorAll('[data-cumplido="no"]')];

    expect(pendientes).toHaveLength(1);
    expect(pendientes[0].textContent).toMatch(/símbolo/i);
  });

  it('no transmite el estado solo con el color', () => {
    // Cada línea lleva un símbolo y un texto para lectores de pantalla, porque
    // distinguir verde de gris no está al alcance de todo el mundo.
    renderRegistro();
    expect(screen.getAllByText(/^Pendiente:$/)).toHaveLength(4);
  });
});

describe('modo registro: envío', () => {
  it('entrega SOLO usuario y contraseña: la confirmación no viaja', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await registrar(user, VALIDA);

    expect(onSubmit).toHaveBeenCalledWith('nueva', VALIDA);
    expect(onSubmit).toHaveBeenCalledTimes(1);
    // Dos argumentos exactos: nada de un tercero con la confirmación.
    expect(onSubmit.mock.calls[0]).toHaveLength(2);
  });

  it('acepta una contraseña de exactamente 15 caracteres', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    const quince = 'Correct-Horse2!';
    expect(quince).toHaveLength(MIN_PASSWORD_LENGTH);
    await registrar(user, quince);

    expect(onSubmit).toHaveBeenCalledWith('nueva', quince);
  });

  it('acepta una contraseña larga', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    const larga = 'Una frase larga de paso que recuerdo sin esfuerzo 2026!';
    await registrar(user, larga);

    expect(onSubmit).toHaveBeenCalledWith('nueva', larga);
  });

  it.each([
    ['demasiado corta', 'Corto-Horse12!'],
    ['sin mayúscula', 'cafe con leche y 2 tostadas!'],
    ['sin número', 'Cafe con leche y tostadas!'],
    ['sin símbolo', 'Cafe con leche y 2 tostadas'],
    ['sin varios requisitos', 'cafe con leche y tostadas'],
  ])('una contraseña %s no llega a enviarse', async (_caso, password) => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await registrar(user, password);

    // Lo para la validación del propio campo (minLength o pattern) antes de
    // llegar al manejador. La comprobación que hay dentro del manejador se
    // mantiene como segunda barrera, por si el atributo se pierde o el
    // navegador autocompleta el campo.
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

describe('confirmación de contraseña', () => {
  it('avisa en cuanto las contraseñas dejan de coincidir', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), VALIDA);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'otra cosa');

    expect(screen.getByText(/no coinciden/i)).toBeInTheDocument();
  });

  it('no avisa mientras el segundo campo está vacío', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), VALIDA);

    expect(screen.queryByText(/no coinciden/i)).not.toBeInTheDocument();
  });

  it('deshabilita el botón mientras no coincidan', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), VALIDA);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'distinta');

    expect(screen.getByRole('button', { name: /registrarse/i })).toBeDisabled();
  });

  it('no llama a onSubmit si no coinciden', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await registrar(user, VALIDA, 'Distinta pero valida 7!');

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('sí llama a onSubmit cuando coinciden', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderRegistro({ onSubmit });

    await registrar(user, VALIDA, VALIDA);

    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it('vuelve a habilitar el botón cuando se corrige', async () => {
    const user = userEvent.setup();
    renderRegistro();

    const confirmacion = screen.getByLabelText('Repite la contraseña');
    await user.type(screen.getByLabelText('Contraseña'), VALIDA);
    await user.type(confirmacion, 'distinta');
    expect(screen.getByRole('button', { name: /registrarse/i })).toBeDisabled();

    await user.clear(confirmacion);
    await user.type(confirmacion, VALIDA);
    expect(screen.getByRole('button', { name: /registrarse/i })).toBeEnabled();
  });

  it('marca el campo como inválido para lectores de pantalla', async () => {
    const user = userEvent.setup();
    renderRegistro();

    await user.type(screen.getByLabelText('Contraseña'), VALIDA);
    await user.type(screen.getByLabelText('Repite la contraseña'), 'distinta');

    expect(screen.getByLabelText('Repite la contraseña')).toHaveAttribute('aria-invalid', 'true');
  });
});

describe('errores del servidor', () => {
  it('muestra el error recibido por props', () => {
    renderLogin({ error: 'Usuario o contraseña incorrectos' });
    expect(screen.getByText('Usuario o contraseña incorrectos')).toBeInTheDocument();
  });
});
