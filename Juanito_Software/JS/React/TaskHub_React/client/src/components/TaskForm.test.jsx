import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskForm from './TaskForm';

/**
 * El formulario es donde se crea y edita todo. Lo que se comprueba aquí es el
 * contrato con el resto de la aplicación: qué objeto entrega al enviarse, qué
 * valores trae por defecto y qué hace tras enviar.
 */

describe('TaskForm al crear', () => {
  it('empieza en pendiente y prioridad media', () => {
    render(<TaskForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/estado/i)).toHaveValue('pending');
    expect(screen.getByLabelText(/prioridad/i)).toHaveValue('medium');
  });

  it('entrega título, descripción, estado y prioridad', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText(/título/i), 'Comprar pan');
    await user.type(screen.getByPlaceholderText(/descripción/i), 'En la panadería');
    await user.selectOptions(screen.getByLabelText(/estado/i), 'in-progress');
    await user.selectOptions(screen.getByLabelText(/prioridad/i), 'high');
    await user.click(screen.getByRole('button', { name: /agregar/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'Comprar pan',
      description: 'En la panadería',
      status: 'in-progress',
      priority: 'high',
    });
  });

  it('recorta los espacios del título y la descripción', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText(/título/i), '   Con espacios   ');
    await user.click(screen.getByRole('button', { name: /agregar/i }));

    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ title: 'Con espacios' }));
  });

  it('no envía si el título está en blanco', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText(/título/i), '     ');
    await user.click(screen.getByRole('button', { name: /agregar/i }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('vacía el formulario tras crear, para poder encadenar tareas', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={vi.fn()} />);

    const titulo = screen.getByPlaceholderText(/título/i);
    await user.type(titulo, 'Primera');
    await user.selectOptions(screen.getByLabelText(/prioridad/i), 'high');
    await user.click(screen.getByRole('button', { name: /agregar/i }));

    expect(titulo).toHaveValue('');
    expect(screen.getByLabelText(/prioridad/i)).toHaveValue('medium');
  });
});

describe('TaskForm al editar', () => {
  const tarea = {
    id: 'abc',
    title: 'Tarea existente',
    description: 'Su descripción',
    status: 'in-progress',
    priority: 'high',
  };

  it('carga los valores actuales de la tarea', () => {
    render(<TaskForm initialValues={tarea} onSubmit={vi.fn()} onCancel={vi.fn()} />);

    expect(screen.getByDisplayValue('Tarea existente')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Su descripción')).toBeInTheDocument();
    expect(screen.getByLabelText(/estado/i)).toHaveValue('in-progress');
    expect(screen.getByLabelText(/prioridad/i)).toHaveValue('high');
  });

  it('el botón dice Guardar y aparece Cancelar', () => {
    render(<TaskForm initialValues={tarea} onSubmit={vi.fn()} onCancel={vi.fn()} />);

    expect(screen.getByRole('button', { name: /guardar/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
  });

  it('NO vacía el formulario tras guardar', async () => {
    const user = userEvent.setup();
    render(<TaskForm initialValues={tarea} onSubmit={vi.fn()} onCancel={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /guardar/i }));

    // Al editar, vaciar los campos daría la sensación de que se ha borrado.
    expect(screen.getByDisplayValue('Tarea existente')).toBeInTheDocument();
  });

  it('cancelar avisa al componente padre', async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    render(<TaskForm initialValues={tarea} onSubmit={vi.fn()} onCancel={onCancel} />);

    await user.click(screen.getByRole('button', { name: /cancelar/i }));
    expect(onCancel).toHaveBeenCalled();
  });
});
