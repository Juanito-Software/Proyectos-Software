import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskList from './TaskList';
import * as api from '../services/api';

/**
 * La pantalla principal: lista, filtros, búsqueda con retardo y notificaciones.
 *
 * Es el componente más grande de la aplicación y el que más estado coordina.
 * Lo que más importa fijar aquí es que **los filtros los resuelve la API**: si
 * alguien los reimplementara en el navegador, la lista seguiría pareciendo
 * correcta con pocas tareas y dejaría de escalar sin que nada avisara.
 */

const tareas = [
  {
    id: 't1',
    title: 'Comprar pan',
    description: 'En la panadería',
    status: 'pending',
    priority: 'high',
    completed: false,
  },
  {
    id: 't2',
    title: 'Llamar al fontanero',
    description: '',
    status: 'in-progress',
    priority: 'low',
    completed: false,
  },
];

let espias;

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  espias = {
    getTasks: vi.spyOn(api, 'getTasks').mockResolvedValue(tareas),
    createTask: vi.spyOn(api, 'createTask').mockResolvedValue(undefined),
    toggleCompleted: vi.spyOn(api, 'toggleCompleted').mockResolvedValue(undefined),
    deleteTask: vi.spyOn(api, 'deleteTask').mockResolvedValue(undefined),
    updateTask: vi.spyOn(api, 'updateTask').mockResolvedValue(undefined),
  };
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

const usuario = { username: 'juan' };

const montar = (props = {}) =>
  render(<TaskList user={usuario} onLogout={vi.fn()} {...props} />);

/** El primer render dispara la carga tras el retardo de 300 ms. */
async function montarYEsperar(props = {}) {
  const resultado = montar(props);
  await vi.advanceTimersByTimeAsync(350);
  await waitFor(() => expect(espias.getTasks).toHaveBeenCalled());
  return resultado;
}

describe('carga inicial', () => {
  it('muestra el indicador mientras carga', () => {
    montar();
    expect(screen.getByText(/cargando tareas/i)).toBeInTheDocument();
  });

  it('pinta las tareas que devuelve la API', async () => {
    await montarYEsperar();

    expect(await screen.findByText('Comprar pan')).toBeInTheDocument();
    expect(screen.getByText('Llamar al fontanero')).toBeInTheDocument();
  });

  it('muestra el nombre del usuario en la cabecera', async () => {
    await montarYEsperar();
    expect(screen.getByText('juan')).toBeInTheDocument();
  });

  it('sin tareas y sin filtros, invita a crear la primera', async () => {
    espias.getTasks.mockResolvedValue([]);
    await montarYEsperar();

    expect(await screen.findByText(/todavía no tienes tareas/i)).toBeInTheDocument();
  });

  it('enseña el error si la carga falla', async () => {
    espias.getTasks.mockRejectedValue(new Error('Error al cargar tareas'));
    await montarYEsperar();

    expect(await screen.findByText('Error al cargar tareas')).toBeInTheDocument();
  });
});

describe('sesión expirada', () => {
  it('cierra la sesión cuando la API dice que expiró', async () => {
    // Es el único error que no se limita a enseñarse: hay que sacar al usuario
    // de una pantalla que ya no puede cargar nada.
    const onLogout = vi.fn();
    espias.getTasks.mockRejectedValue(new Error('Sesión expirada'));

    await montarYEsperar({ onLogout });

    await waitFor(() => expect(onLogout).toHaveBeenCalledTimes(1));
  });

  it('un error normal NO cierra la sesión', async () => {
    const onLogout = vi.fn();
    espias.getTasks.mockRejectedValue(new Error('Error del servidor'));

    await montarYEsperar({ onLogout });

    await screen.findByText('Error del servidor');
    expect(onLogout).not.toHaveBeenCalled();
  });

  it('el botón Salir avisa al componente padre', async () => {
    const onLogout = vi.fn();
    await montarYEsperar({ onLogout });

    await userEvent.click(screen.getByRole('button', { name: /salir/i }));
    expect(onLogout).toHaveBeenCalled();
  });
});

describe('filtros: los resuelve la API, no el navegador', () => {
  it('la primera carga va sin filtros', async () => {
    await montarYEsperar();
    expect(espias.getTasks).toHaveBeenCalledWith({ status: '', priority: '', search: '' });
  });

  it('filtrar por estado manda el parámetro al servidor', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();

    await user.selectOptions(screen.getByLabelText(/filtrar por estado/i), 'completed');
    await vi.advanceTimersByTimeAsync(350);

    await waitFor(() =>
      expect(espias.getTasks).toHaveBeenLastCalledWith(
        expect.objectContaining({ status: 'completed' }),
      ),
    );
  });

  it('filtrar por prioridad manda el parámetro al servidor', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();

    await user.selectOptions(screen.getByLabelText(/filtrar por prioridad/i), 'high');
    await vi.advanceTimersByTimeAsync(350);

    await waitFor(() =>
      expect(espias.getTasks).toHaveBeenLastCalledWith(
        expect.objectContaining({ priority: 'high' }),
      ),
    );
  });

  it('con filtros y sin resultados, el mensaje vacío es otro', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();

    espias.getTasks.mockResolvedValue([]);
    await user.selectOptions(screen.getByLabelText(/filtrar por estado/i), 'completed');
    await vi.advanceTimersByTimeAsync(350);

    // "Todavía no tienes tareas" sería engañoso: sí las tiene, pero no de ese
    // estado.
    expect(await screen.findByText(/ninguna tarea coincide con los filtros/i)).toBeInTheDocument();
  });

  it('el botón de limpiar solo aparece cuando hay algún filtro', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();

    expect(screen.queryByRole('button', { name: /limpiar/i })).not.toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText(/filtrar por estado/i), 'pending');
    expect(screen.getByRole('button', { name: /limpiar/i })).toBeInTheDocument();
  });

  it('limpiar devuelve los tres filtros a vacío de una vez', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();

    await user.selectOptions(screen.getByLabelText(/filtrar por estado/i), 'pending');
    await user.selectOptions(screen.getByLabelText(/filtrar por prioridad/i), 'high');
    await user.type(screen.getByLabelText(/buscar tareas/i), 'pan');
    await vi.advanceTimersByTimeAsync(350);

    await user.click(screen.getByRole('button', { name: /limpiar/i }));
    await vi.advanceTimersByTimeAsync(350);

    await waitFor(() =>
      expect(espias.getTasks).toHaveBeenLastCalledWith({ status: '', priority: '', search: '' }),
    );
  });
});

describe('búsqueda con retardo', () => {
  it('no lanza una petición por cada tecla', async () => {
    // Escribir "panadería" son nueve teclas. Sin el retardo serían nueve
    // peticiones para un solo término de búsqueda.
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();
    espias.getTasks.mockClear();

    await user.type(screen.getByLabelText(/buscar tareas/i), 'panadería');
    // Todavía no ha pasado el tiempo de espera.
    expect(espias.getTasks).not.toHaveBeenCalled();

    await vi.advanceTimersByTimeAsync(350);
    await waitFor(() => expect(espias.getTasks).toHaveBeenCalledTimes(1));
  });

  it('busca con el texto completo, no con lo que hubiera a medias', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await montarYEsperar();
    espias.getTasks.mockClear();

    await user.type(screen.getByLabelText(/buscar tareas/i), 'pan');
    await vi.advanceTimersByTimeAsync(350);

    await waitFor(() =>
      expect(espias.getTasks).toHaveBeenLastCalledWith(expect.objectContaining({ search: 'pan' })),
    );
  });
});

describe('crear una tarea', () => {
  it('la añade al principio de la lista', async () => {
    // Arriba y no abajo: la API devuelve las más recientes primero, así que
    // meterla al final la dejaría fuera de sitio hasta la siguiente carga.
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const nueva = { id: 't3', title: 'Tarea nueva', description: '', status: 'pending', priority: 'medium', completed: false };
    espias.createTask.mockResolvedValue(nueva);

    await montarYEsperar();
    await screen.findByText('Comprar pan');

    const formulario = screen.getByRole('button', { name: /agregar tarea/i }).closest('form');
    await user.type(within(formulario).getByPlaceholderText(/título/i), 'Tarea nueva');
    await user.click(within(formulario).getByRole('button', { name: /agregar tarea/i }));

    const titulos = await screen.findAllByText(/Tarea nueva|Comprar pan/);
    expect(titulos[0]).toHaveTextContent('Tarea nueva');
  });

  it('avisa de que se ha creado', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    espias.createTask.mockResolvedValue({ id: 't3', title: 'Otra', description: '', status: 'pending', priority: 'medium', completed: false });

    await montarYEsperar();
    const formulario = screen.getByRole('button', { name: /agregar tarea/i }).closest('form');
    await user.type(within(formulario).getByPlaceholderText(/título/i), 'Otra');
    await user.click(within(formulario).getByRole('button', { name: /agregar tarea/i }));

    expect(await screen.findByRole('status')).toHaveTextContent(/tarea creada/i);
  });

  it('el aviso desaparece solo a los tres segundos', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    espias.createTask.mockResolvedValue({ id: 't3', title: 'Otra', description: '', status: 'pending', priority: 'medium', completed: false });

    await montarYEsperar();
    const formulario = screen.getByRole('button', { name: /agregar tarea/i }).closest('form');
    await user.type(within(formulario).getByPlaceholderText(/título/i), 'Otra');
    await user.click(within(formulario).getByRole('button', { name: /agregar tarea/i }));

    await screen.findByRole('status');
    await vi.advanceTimersByTimeAsync(3100);

    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
  });

  it('un fallo al crear muestra el error y no añade nada', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    espias.createTask.mockRejectedValue(new Error('El título ya existe'));

    await montarYEsperar();
    const formulario = screen.getByRole('button', { name: /agregar tarea/i }).closest('form');
    await user.type(within(formulario).getByPlaceholderText(/título/i), 'Comprar pan');
    await user.click(within(formulario).getByRole('button', { name: /agregar tarea/i }));

    expect(await screen.findByText('El título ya existe')).toBeInTheDocument();
    expect(screen.getAllByText('Comprar pan')).toHaveLength(1);
  });
});

describe('actualizar y borrar desde la lista', () => {
  it('borrar quita la tarea sin volver a pedir la lista', async () => {
    // Recargar entera tras cada borrado sería una petición de más y un
    // parpadeo: basta con quitarla del estado.
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    await montarYEsperar();
    await screen.findByText('Comprar pan');
    espias.getTasks.mockClear();

    const item = screen.getByText('Comprar pan').closest('li');
    await user.click(within(item).getByRole('button', { name: /eliminar/i }));

    await waitFor(() => expect(screen.queryByText('Comprar pan')).not.toBeInTheDocument());
    expect(espias.getTasks).not.toHaveBeenCalled();
  });

  it('marcar como completada no saca el aviso de "Tarea actualizada"', async () => {
    // El propio checkbox ya es la confirmación visual, y el ciclo optimista
    // llama a onUpdate dos veces: el aviso saldría duplicado.
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    espias.toggleCompleted.mockResolvedValue({ ...tareas[0], completed: true, status: 'completed' });

    await montarYEsperar();
    await screen.findByText('Comprar pan');

    const item = screen.getByText('Comprar pan').closest('li');
    await user.click(within(item).getByRole('checkbox'));

    await waitFor(() => expect(espias.toggleCompleted).toHaveBeenCalled());
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('el cambio del checkbox se ve al instante en la lista', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    // Petición congelada: si la lista solo se actualizara al responder, el
    // distintivo seguiría diciendo "Pendiente".
    espias.toggleCompleted.mockReturnValue(new Promise(() => {}));

    await montarYEsperar();
    await screen.findByText('Comprar pan');

    const item = screen.getByText('Comprar pan').closest('li');
    await user.click(within(item).getByRole('checkbox'));

    await waitFor(() => {
      expect(within(screen.getByText('Comprar pan').closest('li')).getByText('Completada')).toBeInTheDocument();
    });
  });

  it('editar sí saca el aviso: el formulario se cierra y hay que confirmarlo', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    espias.updateTask.mockResolvedValue({ ...tareas[0], title: 'Comprar leche' });

    await montarYEsperar();
    await screen.findByText('Comprar pan');

    const item = screen.getByText('Comprar pan').closest('li');
    await user.click(within(item).getByRole('button', { name: /editar/i }));
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    expect(await screen.findByRole('status')).toHaveTextContent(/tarea actualizada/i);
  });
});

describe('enlace al playground', () => {
  it('se abre en otra pestaña y sin filtrar el referente', async () => {
    // target="_blank" sin rel="noopener" deja que la página abierta manipule
    // la de origen a través de window.opener.
    await montarYEsperar();

    const enlace = screen.getByRole('link', { name: /playground/i });
    expect(enlace).toHaveAttribute('href', '/playground');
    expect(enlace).toHaveAttribute('target', '_blank');
    expect(enlace).toHaveAttribute('rel', expect.stringContaining('noopener'));
  });
});
