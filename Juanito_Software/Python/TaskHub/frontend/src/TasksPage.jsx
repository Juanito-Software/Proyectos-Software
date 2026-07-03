import { useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { api } from "./api";
import TaskCard from "./TaskCard";
import TaskForm from "./TaskForm";

export default function TasksPage() {
  const { logout } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [filterCompleted, setFilterCompleted] = useState(null);
  const [filterTag, setFilterTag] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [error, setError] = useState("");

  const loadTasks = useCallback(async () => {
    try {
      const filters = {};
      if (filterCompleted !== null) filters.completed = filterCompleted;
      if (filterTag) filters.tag = filterTag;
      const data = await api.getTasks(filters);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    }
  }, [filterCompleted, filterTag]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  async function handleSave(data) {
    setFormLoading(true);
    try {
      if (editingTask) {
        await api.updateTask(editingTask.id, data);
      } else {
        await api.createTask(data);
      }
      setShowForm(false);
      setEditingTask(null);
      await loadTasks();
    } catch (err) {
      setError(err.message);
    } finally {
      setFormLoading(false);
    }
  }

  async function handleToggle(task) {
    try {
      await api.updateTask(task.id, { completed: !task.completed });
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm("¿Eliminar esta tarea?")) return;
    try {
      await api.deleteTask(id);
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  }

  function openEdit(task) {
    setEditingTask(task);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingTask(null);
  }

  function applyTagFilter(e) {
    e.preventDefault();
    setFilterTag(tagInput.trim().toLowerCase());
  }

  function clearFilters() {
    setFilterCompleted(null);
    setFilterTag("");
    setTagInput("");
  }

  const pending = tasks.filter((t) => !t.completed).length;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>TaskHub</h1>
          <span className="task-count">{pending} pendiente{pending !== 1 ? "s" : ""}</span>
        </div>
        <button className="btn-ghost" onClick={logout}>Cerrar sesión</button>
      </header>

      <div className="toolbar">
        <div className="filter-group">
          <span className="filter-label">Estado:</span>
          <button
            className={`filter-btn ${filterCompleted === null ? "active" : ""}`}
            onClick={() => setFilterCompleted(null)}
          >
            Todas
          </button>
          <button
            className={`filter-btn ${filterCompleted === false ? "active" : ""}`}
            onClick={() => setFilterCompleted(false)}
          >
            Pendientes
          </button>
          <button
            className={`filter-btn ${filterCompleted === true ? "active" : ""}`}
            onClick={() => setFilterCompleted(true)}
          >
            Completadas
          </button>
        </div>

        <form className="tag-filter" onSubmit={applyTagFilter}>
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            placeholder="Filtrar por etiqueta…"
          />
          <button type="submit" className="btn-secondary">Filtrar</button>
          {filterTag && (
            <button type="button" className="btn-ghost" onClick={clearFilters}>
              Limpiar
            </button>
          )}
        </form>

        <button className="btn-primary" onClick={() => setShowForm(true)}>
          + Nueva tarea
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button className="btn-ghost" onClick={() => setError("")}>✕</button>
        </div>
      )}

      <div className="task-list">
        {tasks.length === 0 ? (
          <div className="empty-state">
            <p>No hay tareas{filterTag ? ` con la etiqueta "${filterTag}"` : ""}.</p>
            {!filterTag && (
              <button className="btn-primary" onClick={() => setShowForm(true)}>
                Crear mi primera tarea
              </button>
            )}
          </div>
        ) : (
          tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggle={handleToggle}
              onEdit={openEdit}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      {showForm && (
        <TaskForm
          initial={editingTask}
          onSave={handleSave}
          onCancel={closeForm}
          loading={formLoading}
        />
      )}
    </div>
  );
}
