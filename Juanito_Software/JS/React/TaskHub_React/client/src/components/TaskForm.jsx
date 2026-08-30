import { useState } from 'react';
import { STATUSES, PRIORITIES } from '../constants';

export default function TaskForm({ onSubmit, initialValues, onCancel }) {
  const [title, setTitle] = useState(initialValues?.title ?? '');
  const [description, setDescription] = useState(initialValues?.description ?? '');
  const [status, setStatus] = useState(initialValues?.status ?? 'pending');
  const [priority, setPriority] = useState(initialValues?.priority ?? 'medium');
  const isEditing = !!initialValues?.id;

  function handleSubmit(e) {
    e.preventDefault();
    const t = title.trim();
    if (!t) return;

    onSubmit({ title: t, description: description.trim(), status, priority });

    if (!isEditing) {
      setTitle('');
      setDescription('');
      setStatus('pending');
      setPriority('medium');
    }
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Título de la tarea"
        required
        autoFocus
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Descripción (opcional)"
        rows={2}
      />

      <div className="form-selects">
        <label>
          <span>Estado</span>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Prioridad</span>
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            {PRIORITIES.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="form-actions">
        {onCancel && (
          <button type="button" onClick={onCancel}>
            Cancelar
          </button>
        )}
        <button type="submit">{isEditing ? 'Guardar' : 'Agregar tarea'}</button>
      </div>
    </form>
  );
}
