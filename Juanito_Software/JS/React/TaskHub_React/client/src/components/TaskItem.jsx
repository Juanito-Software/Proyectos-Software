import { useState } from 'react';
import TaskForm from './TaskForm';
import { updateTask, deleteTask, toggleCompleted } from '../services/api';
import { statusLabel, priorityLabel } from '../constants';

/**
 * Cómo quedaría la tarea si se marcara o desmarcara, sin preguntar al servidor.
 *
 * Reproduce la traducción que hace el backend: `completed` es un campo
 * calculado a partir de `status`, así que cambiar uno sin el otro dejaría la
 * tarjeta incoherente durante el instante en que se pinta —el distintivo
 * diría «Pendiente» con la casilla ya marcada—.
 *
 * La regla es la misma que aplica `resolveStatus` en el servidor: marcar lleva
 * a `completed`, desmarcar vuelve a `pending`. Está duplicada, y el test de
 * navegador que marca una tarea y comprueba el distintivo es lo que detectaría
 * que las dos se separen.
 */
function conCompletadaCambiada(task) {
  const completed = !task.completed;
  return { ...task, completed, status: completed ? 'completed' : 'pending' };
}

export default function TaskItem({ task, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Marcar como completada, pintando el cambio antes de que responda el
   * servidor.
   *
   * Antes se esperaba a la respuesta para repintar. Con la base de datos en la
   * misma región son 40-80 ms y apenas se nota, pero desde una conexión lenta
   * la casilla se quedaba quieta el tiempo suficiente para que pareciera que
   * el clic no había funcionado, y la gente vuelve a pulsar.
   *
   * Si la petición falla se revierte al estado que había y se avisa: es la
   * contrapartida obligatoria de adelantarse: enseñar un cambio que no llegó a
   * guardarse sería peor que tardar en enseñarlo.
   */
  async function handleToggle() {
    const original = task;
    const optimista = conCompletadaCambiada(task);

    setError(null);
    onUpdate(optimista, { silencioso: true });

    try {
      // El checkbox sigue mandando `completed`, y el servidor lo traduce a
      // status. Es el atajo de un clic para el caso más frecuente; el estado
      // intermedio "en progreso" se elige al editar.
      const updated = await toggleCompleted(task.id, optimista.completed);
      // Se repinta con lo que devuelve el servidor y no con lo que se supuso:
      // si allí cambió algo más, esta es la versión buena.
      onUpdate(updated, { silencioso: true });
    } catch (err) {
      onUpdate(original, { silencioso: true });
      setError('No se pudo guardar el cambio');
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

      {error && (
        <p className="task-error" role="alert">
          {error}
        </p>
      )}

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
