import { useState, useEffect } from "react";

export default function TaskForm({ initial = null, onSave, onCancel, loading }) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [tagInput, setTagInput] = useState(initial?.tags?.map((t) => t.name).join(", ") ?? "");

  useEffect(() => {
    if (initial) {
      setTitle(initial.title);
      setDescription(initial.description ?? "");
      setTagInput(initial.tags?.map((t) => t.name).join(", ") ?? "");
    }
  }, [initial]);

  function handleSubmit(e) {
    e.preventDefault();
    const tag_names = tagInput
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);
    onSave({ title, description: description || null, tag_names });
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{initial ? "Editar tarea" : "Nueva tarea"}</h2>
        <form onSubmit={handleSubmit} className="form">
          <label>Título *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Título de la tarea"
            required
            autoFocus
          />
          <label>Descripción</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Descripción opcional…"
            rows={3}
          />
          <label>Etiquetas (separadas por coma)</label>
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            placeholder="trabajo, urgente, personal"
          />
          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onCancel}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Guardando…" : initial ? "Guardar cambios" : "Crear tarea"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
