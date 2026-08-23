export default function TaskCard({ task, onToggle, onEdit, onDelete }) {
  return (
    <div className={`task-card ${task.completed ? "completed" : ""}`}>
      <div className="task-header">
        <label className="checkbox-wrapper">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => onToggle(task)}
          />
          <span className="task-title">{task.title}</span>
        </label>
        <div className="task-actions">
          <button className="btn-icon" title="Editar" onClick={() => onEdit(task)}>
            ✏️
          </button>
          <button className="btn-icon btn-danger" title="Eliminar" onClick={() => onDelete(task.id)}>
            🗑️
          </button>
        </div>
      </div>

      {task.description && (
        <p className="task-description">{task.description}</p>
      )}

      {task.tags.length > 0 && (
        <div className="tag-list">
          {task.tags.map((tag) => (
            <span key={tag.id} className="tag">
              {tag.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
