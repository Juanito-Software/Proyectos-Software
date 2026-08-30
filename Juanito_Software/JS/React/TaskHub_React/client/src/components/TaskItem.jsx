import { useState } from 'react';
import TaskForm from './TaskForm';
import { updateTask, deleteTask, toggleCompleted } from '../services/api';
import { statusLabel, priorityLabel } from '../constants';

export default function TaskItem({ task, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);

  async function handleToggle() {
    try {
      // El checkbox sigue mandando `completed`, y el servidor lo traduce a
      // status. Es el atajo de un clic para el caso más frecuente; el estado
      // intermedio "en progreso" se elige al editar.
      const updated = await toggleCompleted(task.id, !task.completed);
      onUpdate(updated);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDelete() {
    if (!confirm('¿Eliminar esta tarea?')) return;
    try {
      await deleteTask(task.id);
      onDelete(task.id);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleEditSubmit(values) {
    try {
      const updated = await updateTask(task.id, values);
      onUpdate(updated);
      setEditing(false);
    } catch (err) {
      console.error(err);
    }
  }

  if (editing) {
    return (
      <li className="task-item task-item--editing">
        <TaskForm
          initialValues={{
            id: task.id,
            title: task.title,
            description: task.description,
            status: task.status,
            priority: task.priority,
          }}
          onSubmit={handleEditSubmit}
          onCancel={() => setEditing(false)}
        />
      </li>
    );
  }

  return (
    <li className={`task-item ${task.completed ? 'task-item--completed' : ''}`}>
      <label className="task-checkbox">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          aria-label="Marcar como completada"
        />
        <span className="task-title">{task.title}</span>
      </label>

      <div className="task-badges">
        <span className={`badge badge--status-${task.status}`}>{statusLabel(task.status)}</span>
        <span className={`badge badge--priority-${task.priority}`}>
          {priorityLabel(task.priority)}
        </span>
      </div>

      {task.description && <p className="task-description">{task.description}</p>}

      <div className="task-actions">
        <button type="button" onClick={() => setEditing(true)}>
          Editar
        </button>
        <button type="button" onClick={handleDelete} className="btn-danger">
          Eliminar
        </button>
      </div>
    </li>
  );
}
