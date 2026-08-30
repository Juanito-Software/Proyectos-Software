import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskItem from './TaskItem';
import * as api from '../services/api';

vi.mock('../services/api');

const tarea = {
  id: 'abc-123',
  title: 'Comprar pan',
  description: 'En la panadería de la esquina',
  status: 'pending',
  priority: 'high',
  completed: false,
};

beforeEach(() => {
  vi.clearAllMocks();
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
    api.toggleCompleted.mockResolvedValue({ ...tarea, completed: true, status: 'completed' });

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('checkbox'));

    expect(api.toggleCompleted).toHaveBeenCalledWith('abc-123', true);
    expect(onUpdate).toHaveBeenCalled();
  });

  it('eliminar pide confirmación y respeta un "no"', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValue(false);

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /eliminar/i }));

    // Cancelar la confirmación no debe borrar nada.
    expect(api.deleteTask).not.toHaveBeenCalled();
    expect(onDelete).not.toHaveBeenCalled();
  });

  it('eliminar borra cuando se confirma', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    api.deleteTask.mockResolvedValue({ id: 'abc-123' });

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /eliminar/i }));

    expect(api.deleteTask).toHaveBeenCalledWith('abc-123');
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
    api.updateTask.mockResolvedValue({ ...tarea, title: 'Comprar pan integral' });

    render(<TaskItem task={tarea} onUpdate={onUpdate} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /editar/i }));

    const titulo = screen.getByDisplayValue('Comprar pan');
    await user.clear(titulo);
    await user.type(titulo, 'Comprar pan integral');
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    expect(api.updateTask).toHaveBeenCalledWith(
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
    api.deleteTask.mockRejectedValue(new Error('Error de red'));

    render(<TaskItem task={tarea} onUpdate={vi.fn()} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /eliminar/i }));

    // Si se quitara de la lista igualmente, el usuario creería que se borró.
    expect(onDelete).not.toHaveBeenCalled();
  });
});
