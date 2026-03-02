import { useState } from 'react';

export default function TaskForm({ onSubmit, initialValues, onCancel }) {
  const [title, setTitle] = useState(initialValues?.title ?? '');
  const [description, setDescription] = useState(initialValues?.description ?? '');
  const isEditing = !!initialValues?.id;

  function handleSubmit(e) {
    e.preventDefault();
    const t = title.trim();
    if (!t) return;
    onSubmit({ title: t, description: description.trim() });
    if (!isEditing) {
      setTitle('');
      setDescription('');
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
