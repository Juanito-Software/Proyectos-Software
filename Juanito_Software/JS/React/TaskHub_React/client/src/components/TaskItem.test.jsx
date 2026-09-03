import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskItem from './TaskItem';
import * as api from '../services/api';

/**
 * Las llamadas a la API se interceptan con espías sobre el módulo real.
 *
 * `vi.mock('../services/api')` sustituía el módulo entero en el registro, que
 * se comparte entre archivos cuando la suite corre sin aislamiento: según el
 * orden de ejecución, dejaba a `api.refresh.test.js` sin el módulo de verdad.
 * Un espía se instala y se retira dentro de este archivo.
 */
let apiEspias;

const tarea = {
  id: 'abc-123',
  title: 'Comprar pan',
  description: 'En la panadería de la esquina',
  status: 'pending',
  priority: 'high',
  completed: false,
};

beforeEach(() => {
  apiEspias = {
    toggleCompleted: vi.spyOn(api, 'toggleCompleted').mockResolvedValue(undefined),
    updateTask: vi.spyOn(api, 'updateTask').mockResolvedValue(undefined),
    deleteTask: vi.spyOn(api, 'deleteTask').mockResolvedValue(undefined),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('TaskItem: presentación', () => {
  it('muestra título, descripción y los dos distintivos', () => {
    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText('Comprar pan')).toBeInTheDocument();
    expect(screen.getByText(/panadería/)).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
    expect(screen.getByText('Alta')).toBeInTheDocument();
  });

  it('traduce los valores de la API a etiquetas en castellano', () => {
    render(
      <TaskItem
        task={{ ...tarea, status: 'in-progress', priority: 'low' }}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
      />,
    );

    // El usuario nunca debería ver 'in-progress' ni 'low'.
    expect(screen.getByText('En progreso')).toBeInTheDocument();
    expect(screen.getByText('Baja')).toBeInTheDocument();
    expect(screen.queryByText('in-progress')).not.toBeInTheDocument();
  });

  it('el checkbox refleja si la tarea está completada', () => {
    const { rerender } = render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByRole('checkbox')).not.toBeChecked();

    rerender(
      <TaskItem
        task={{ ...tarea, completed: true, status: 'completed' }}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
      />,
    );
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  it('no rompe cuando la tarea no tiene descripción', () => {
    render(<TaskItem task={{ ...tarea, description: '' }} onUpdate={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText('Comprar pan')).toBeInTheDocument();
  });
});

describe('TaskItem: acciones', () => {
  it('el checkbox manda el valor contrario al actual', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    apiEspias.toggleCompleted.mockResolvedValue({ ...tarea, completed: true, status: 'completed' });

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    expect(apiEspias.toggleCompleted).toHaveBeenCalledWith('abc-123', true);
    expect(onUpdate).toHaveBeenCalled();
  });

  it('eliminar pide confirmación y respeta un "no"', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValue(false);

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /eliminar/i }));

    // Cancelar la confirmación no debe borrar nada.
    expect(apiEspias.deleteTask).not.toHaveBeenCalled();
    expect(onDelete).not.toHaveBeenCalled();
  });

  it('eliminar borra cuando se confirma', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    apiEspias.deleteTask.mockResolvedValue({ id: 'abc-123' });

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /eliminar/i }));

    expect(apiEspias.deleteTask).toHaveBeenCalledWith('abc-123');
    expect(onDelete).toHaveBeenCalledWith('abc-123');
  });

  it('editar abre el formulario con los datos actuales', async () => {
    const user = userEvent.setup();
    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /editar/i }));

    expect(screen.getByDisplayValue('Comprar pan')).toBeInTheDocument();
    expect(screen.getByLabelText(/prioridad/i)).toHaveValue('high');
  });

  it('guardar la edición envía los cambios y cierra el formulario', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    apiEspias.updateTask.mockResolvedValue({ ...tarea, title: 'Comprar pan integral' });

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /editar/i }));

    const titulo = screen.getByDisplayValue('Comprar pan');
    await user.clear(titulo);
    await user.type(titulo, 'Comprar pan integral');
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    expect(apiEspias.updateTask).toHaveBeenCalledWith(
      'abc-123',
      expect.objectContaining({ title: 'Comprar pan integral' }),
    );
    expect(onUpdate).toHaveBeenCalled();
  });

  it('un fallo de la API al borrar no elimina la tarea de la lista', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.spyOn(console, 'error').mockImplementation(() => {});
    apiEspias.deleteTask.mockRejectedValue(new Error('Error de red'));

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /eliminar/i }));

    // Si se quitara de la lista igualmente, el usuario creería que se borró.
    expect(onDelete).not.toHaveBeenCalled();
  });
});

describe('TaskItem: actualización optimista del checkbox', () => {
  /**
   * El checkbox pinta el cambio antes de que responda el servidor.
   *
   * Antes esperaba a la respuesta para repintar. Con la base de datos en la
   * misma región son 40-80 ms y apenas se nota, pero desde una conexión lenta
   * la casilla se quedaba quieta lo suficiente para que pareciera que el clic
   * no había funcionado, y la gente vuelve a pulsar.
   */

  /** Promesa que se resuelve cuando se quiera, para congelar la petición. */
  function peticionCongelada() {
    let resolver, rechazar;
    const promesa = new Promise((res, rej) => {
      resolver = res;
      rechazar = rej;
    });
    return { promesa, resolver, rechazar };
  }

  it('avisa del cambio ANTES de que responda el servidor', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const { promesa } = peticionCongelada();
    apiEspias.toggleCompleted.mockReturnValue(promesa);

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    // La petición sigue en el aire y el padre ya sabe el valor nuevo.
    expect(onUpdate).toHaveBeenCalledWith(
      expect.objectContaining({ completed: true }),
      expect.anything(),
    );
  });

  it('el estado optimista también traduce el status, no solo completed', async () => {
    // `completed` es un campo calculado a partir de `status`. Cambiar uno sin
    // el otro dejaría la tarjeta incoherente: casilla marcada y distintivo
    // diciendo "Pendiente".
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const { promesa } = peticionCongelada();
    apiEspias.toggleCompleted.mockReturnValue(promesa);

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    expect(onUpdate.mock.calls[0][0]).toMatchObject({
      completed: true,
      status: 'completed',
    });
  });

  it('desmarcar devuelve el status a pending, como hace el servidor', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const completada = { ...tarea, completed: true, status: 'completed' };
    const { promesa } = peticionCongelada();
    apiEspias.toggleCompleted.mockReturnValue(promesa);

    render(<TaskItem task={completada} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    expect(onUpdate.mock.calls[0][0]).toMatchObject({
      completed: false,
      status: 'pending',
    });
  });

  it('repinta con lo que devuelve el servidor, no con lo que supuso', async () => {
    // Si allí cambió algo más —una fecha, otro campo—, la versión buena es la
    // del servidor.
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const delServidor = { ...tarea, completed: true, status: 'completed', title: 'Renombrada fuera' };
    apiEspias.toggleCompleted.mockResolvedValue(delServidor);

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    expect(onUpdate).toHaveBeenCalledTimes(2);
    expect(onUpdate.mock.calls[1][0]).toEqual(delServidor);
  });

  it('si la petición falla, revierte al estado original', async () => {
    // La contrapartida obligatoria de adelantarse: enseñar un cambio que no
    // llegó a guardarse sería peor que tardar en enseñarlo.
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    vi.spyOn(console, 'error').mockImplementation(() => {});
    apiEspias.toggleCompleted.mockRejectedValue(new Error('Error de red'));

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    expect(onUpdate).toHaveBeenCalledTimes(2);
    expect(onUpdate.mock.calls[0][0]).toMatchObject({ completed: true });
    expect(onUpdate.mock.calls[1][0]).toEqual(tarea);
  });

  it('avisa al usuario cuando el cambio no se pudo guardar', async () => {
    const user = userEvent.setup();
    vi.spyOn(console, 'error').mockImplementation(() => {});
    apiEspias.toggleCompleted.mockRejectedValue(new Error('Error de red'));

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    // Revertir en silencio dejaría al usuario pensando que sí se guardó.
    expect(await screen.findByRole('alert')).toHaveTextContent(/no se pudo guardar/i);
  });

  it('marca el cambio como silencioso: el checkbox ya es la confirmación', async () => {
    // Sin esto saldría el aviso "Tarea actualizada" dos o tres veces por clic,
    // una por cada llamada del ciclo optimista.
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    apiEspias.toggleCompleted.mockResolvedValue({ ...tarea, completed: true });

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    for (const llamada of onUpdate.mock.calls) {
      expect(llamada[1]).toMatchObject({ silencioso: true });
    }
  });

  it('la edición NO es silenciosa: allí el aviso sí hace falta', async () => {
    // El formulario se cierra al guardar y sin el mensaje no queda claro que
    // el cambio haya llegado.
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    apiEspias.updateTask.mockResolvedValue({ ...tarea, title: 'Comprar leche' });

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /editar/i }));
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    expect(onUpdate).toHaveBeenCalledTimes(1);
    expect(onUpdate.mock.calls[0][1]).toBeUndefined();
  });
});
