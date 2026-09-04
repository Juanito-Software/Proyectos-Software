import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ThemeToggle from './ThemeToggle';

/**
 * El conmutador de tema.
 *
 * Lo que importa aquí no es el icono sino tres cosas que se rompen en silencio:
 *
 * 1. **Que sin elección previa se respete la preferencia del sistema.** Es la
 *    diferencia entre «no ha elegido» y «ha elegido claro», y confundirlas
 *    significa abrir en blanco a quien tiene el sistema en oscuro.
 * 2. **Que el botón tenga nombre accesible.** No lleva texto, solo un símbolo,
 *    así que sin `aria-label` es un botón mudo para un lector de pantalla.
 * 3. **Que un `localStorage` que lanza no tumbe la aplicación.** Pasa en
 *    navegación privada y con el almacenamiento de terceros bloqueado.
 */

/** Finge la respuesta de `prefers-color-scheme: dark`. */
function sistemaEnOscuro(activo) {
  window.matchMedia = vi.fn().mockImplementation((consulta) => ({
    matches: activo && consulta.includes('dark'),
    media: consulta,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
}

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute('data-tema');
  sistemaEnOscuro(false);
});

afterEach(() => {
  vi.restoreAllMocks();
});

const boton = () => screen.getByRole('button');

describe('estado inicial', () => {
  it('sin preferencia guardada y sistema en claro, arranca en claro', () => {
    render(<ThemeToggle />);
    expect(document.documentElement.getAttribute('data-tema')).toBe('claro');
  });

  it('sin preferencia guardada y sistema en oscuro, arranca en oscuro', () => {
    // Sin esto, alguien con el sistema en oscuro recibiría un fogonazo blanco
    // al abrir la página.
    sistemaEnOscuro(true);

    render(<ThemeToggle />);

    expect(document.documentElement.getAttribute('data-tema')).toBe('oscuro');
  });

  it('la elección guardada gana sobre la preferencia del sistema', () => {
    // Quien ha pulsado el botón ha dicho algo más concreto que su configuración
    // general del sistema.
    sistemaEnOscuro(true);
    localStorage.setItem('taskhub-tema', 'claro');

    render(<ThemeToggle />);

    expect(document.documentElement.getAttribute('data-tema')).toBe('claro');
  });

  it('un valor corrupto en el almacenamiento se ignora', () => {
    localStorage.setItem('taskhub-tema', 'fucsia');

    render(<ThemeToggle />);

    expect(document.documentElement.getAttribute('data-tema')).toBe('claro');
  });
});

describe('al pulsar', () => {
  it('pasa de claro a oscuro', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await user.click(boton());

    expect(document.documentElement.getAttribute('data-tema')).toBe('oscuro');
  });

  it('y de oscuro a claro', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await user.click(boton());
    await user.click(boton());

    expect(document.documentElement.getAttribute('data-tema')).toBe('claro');
  });

  it('guarda la elección para la próxima visita', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await user.click(boton());

    expect(localStorage.getItem('taskhub-tema')).toBe('oscuro');
  });
});

describe('accesibilidad', () => {
  it('el botón tiene nombre accesible aunque no tenga texto', () => {
    render(<ThemeToggle />);
    expect(screen.getByRole('button', { name: /activar modo oscuro/i })).toBeInTheDocument();
  });

  it('el nombre describe la ACCIÓN, no el estado actual', async () => {
    // «Modo oscuro» a secas sería ambiguo: no se sabe si informa de dónde estás
    // o de dónde vas a ir. El verbo lo resuelve sin ver el icono.
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await user.click(boton());

    expect(screen.getByRole('button', { name: /activar modo claro/i })).toBeInTheDocument();
  });

  it('el símbolo queda oculto a los lectores de pantalla', () => {
    // Si no, la voz leería el carácter de la luna, que no significa nada.
    const { container } = render(<ThemeToggle />);
    expect(container.querySelector('[aria-hidden="true"]')).toBeInTheDocument();
  });

  it('acepta clases extra sin perder la suya', () => {
    render(<ThemeToggle className="tema-flotante" />);

    expect(boton()).toHaveClass('btn-tema');
    expect(boton()).toHaveClass('tema-flotante');
  });
});

describe('almacenamiento no disponible', () => {
  it('si leer lanza, se usa la preferencia del sistema sin romperse', () => {
    // Navegación privada, almacenamiento de terceros bloqueado, cuota llena.
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('acceso denegado');
    });
    sistemaEnOscuro(true);

    expect(() => render(<ThemeToggle />)).not.toThrow();
    expect(document.documentElement.getAttribute('data-tema')).toBe('oscuro');
  });

  it('si escribir lanza, el tema se aplica igual en esta sesión', async () => {
    // No se recordará al recargar, y eso es aceptable. Lo que no lo es sería
    // que la página se quedara en blanco por no poder guardar una preferencia.
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('cuota excedida');
    });
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await user.click(boton());

    expect(document.documentElement.getAttribute('data-tema')).toBe('oscuro');
  });
});
