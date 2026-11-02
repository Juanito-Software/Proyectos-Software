import { useState } from 'react';
import { STATUSES, PRIORITIES } from '../constants';

/**
 * Formulario de tarea, para crear y para editar.
 *
 * - **Crear** (sin `initialValues.id`): empieza vacío y, tras enviar, se
 *   vacía para la siguiente tarea.
 * - **Editar** (con `initialValues.id`): empieza relleno y conserva los datos
 *   al enviar; quien lo usa decide cuándo cerrarlo.
 *
 * El título se recorta y no se envía si queda vacío. La validación de verdad
 * (longitudes, duplicados) la hace el servidor.
 *
 * @param {object} props
 * @param {(datos: {title: string, description: string, status: string, priority: string}) => void} props.onSubmit
 *        recibe los datos ya recortados
 * @param {object} [props.initialValues] tarea a editar
 * @param {() => void} [props.onCancel] si se da, aparece el botón «Cancelar»
 */
export default function TaskForm({ onSubmit, initialValues, onCancel }) {
  const [title, setTitle] = useState(initialValues?.title ?? '');
  const [description, setDescription] = useState(initialValues?.description ?? '');
  const [status, setStatus] = useState(initialValues?.status ?? 'pending');
  const [priority, setPriority] = useState(initialValues?.priority ?? 'medium');
  const isEditing = !!initialValues?.id;

  /** Envía los datos y, si se está creando, deja el formulario limpio. */
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
