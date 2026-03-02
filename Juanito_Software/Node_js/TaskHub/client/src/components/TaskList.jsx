import { useState, useEffect } from 'react';
import { getTasks, createTask } from '../services/api';
import TaskItem from './TaskItem';
import TaskForm from './TaskForm';

const FILTER_ALL = 'all';
const FILTER_PENDING = 'pending';
const FILTER_COMPLETED = 'completed';

export default function TaskList({ user, onLogout }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState(FILTER_ALL);
  const [notification, setNotification] = useState(null);

  function showNotification(message) {
    setNotification(message);
    setTimeout(() => setNotification(null), 3000);
  }

  async function loadTasks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      if (err.message === 'Sesión expirada') onLogout?.();
      setError(err.message || 'Error al cargar tareas');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  async function handleCreateTask(task) {
    try {
      const created = await createTask(task);
      setTasks((prev) => [created, ...prev]);
      showNotification('Tarea creada');
    } catch (err) {
      setError(err.message);
    }
  }

  function handleUpdateTask(updated) {
    setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    showNotification('Tarea actualizada');
  }

  function handleDeleteTask(id) {
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }

  const filteredTasks =
    filter === FILTER_PENDING
      ? tasks.filter((t) => !t.completed)
      : filter === FILTER_COMPLETED
        ? tasks.filter((t) => t.completed)
        : tasks;

  return (
    <div className="task-list">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1>TaskHub</h1>
            <p className="subtitle">Gestor de tareas colaborativo</p>
          </div>
          <div className="user-bar">
            <span className="user-name">{user?.username}</span>
            <button type="button" className="btn-logout" onClick={onLogout}>
              Salir
            </button>
          </div>
        </div>
      </header>

      {notification && <div className="notification" role="status">{notification}</div>}
      {error && <div className="error">{error}</div>}

      <TaskForm onSubmit={handleCreateTask} />

      <div className="filters">
        <button
          type="button"
          className={filter === FILTER_ALL ? 'active' : ''}
          onClick={() => setFilter(FILTER_ALL)}
        >
          Todas
        </button>
        <button
          type="button"
          className={filter === FILTER_PENDING ? 'active' : ''}
          onClick={() => setFilter(FILTER_PENDING)}
        >
          Pendientes
        </button>
        <button
          type="button"
          className={filter === FILTER_COMPLETED ? 'active' : ''}
          onClick={() => setFilter(FILTER_COMPLETED)}
        >
          Completadas
        </button>
      </div>

      {loading ? (
        <p>Cargando tareas…</p>
      ) : (
        <ul className="tasks">
          {filteredTasks.length === 0 ? (
            <li className="empty">No hay tareas{filter !== FILTER_ALL ? ' en este filtro' : ''}.</li>
          ) : (
            filteredTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={handleUpdateTask}
                onDelete={handleDeleteTask}
              />
            ))
          )}
        </ul>
      )}
    </div>
  );
}
