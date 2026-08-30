import { useState, useEffect, useCallback } from 'react';
import { getTasks, createTask } from '../services/api';
import TaskItem from './TaskItem';
import TaskForm from './TaskForm';
import { STATUSES, PRIORITIES } from '../constants';

export default function TaskList({ user, onLogout }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);

  // Los filtros los resuelve la API, no el navegador: se mandan como
  // parámetros de consulta y solo viajan las tareas que se piden. Antes se
  // traían todas y se descartaban aquí, que no escala.
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [search, setSearch] = useState('');

  function showNotification(message) {
    setNotification(message);
    setTimeout(() => setNotification(null), 3000);
  }

  // useCallback para que la función no se recree en cada render y el efecto
  // pueda declararla como dependencia sin dispararse en bucle.
  const loadTasks = useCallback(
    async (filters) => {
      setLoading(true);
      setError(null);
      try {
        const data = await getTasks(filters);
        setTasks(data);
      } catch (err) {
        if (err.message === 'Sesión expirada') onLogout?.();
        setError(err.message || 'Error al cargar tareas');
      } finally {
        setLoading(false);
      }
    },
    [onLogout],
  );

  // La búsqueda espera 300 ms desde la última tecla para no lanzar una
  // petición por cada carácter escrito.
  useEffect(() => {
    const id = setTimeout(() => loadTasks({ status, priority, search }), 300);
    return () => clearTimeout(id);
  }, [status, priority, search, loadTasks]);

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

  const hayFiltros = status || priority || search;

  return (
    <div className="task-list">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1>TaskHub</h1>
            <p className="subtitle">Tus tareas, solo tuyas</p>
          </div>
          <div className="user-bar">
            {/* El playground comparte el token con la aplicación, así que se
                entra ya autenticado. Se abre en otra pestaña para no perder
                lo que se esté haciendo aquí. */}
            <a
              className="playground-link"
              href="/playground"
              target="_blank"
              rel="noopener noreferrer"
              title="Probar la API en vivo"
            >
              API Playground
            </a>
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
        <input
          type="search"
          className="filter-search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar en título y descripción…"
          aria-label="Buscar tareas"
        />

        <select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filtrar por estado">
          <option value="">Todos los estados</option>
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          aria-label="Filtrar por prioridad"
        >
          <option value="">Todas las prioridades</option>
          {PRIORITIES.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>

        {hayFiltros && (
          <button
            type="button"
            className="btn-clear-filters"
            onClick={() => {
              setStatus('');
              setPriority('');
              setSearch('');
            }}
          >
            Limpiar
          </button>
        )}
      </div>

      {loading ? (
        <p>Cargando tareas…</p>
      ) : (
        <ul className="tasks">
          {tasks.length === 0 ? (
            <li className="empty">
              {hayFiltros ? 'Ninguna tarea coincide con los filtros.' : 'Todavía no tienes tareas.'}
            </li>
          ) : (
            tasks.map((task) => (
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
