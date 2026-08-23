const API_BASE = '/api/tasks';

let apiAuthToken = null;

export function setAuthToken(token) {
  apiAuthToken = token;
}

function getHeaders(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

/**
 * La API responde siempre con el sobre { success, data, timestamp } (o
 * { success:false, error } si falla). Este helper lo abre y devuelve solo
 * `data`, para que los componentes sigan recibiendo la tarea o el array de
 * tareas tal cual, sin enterarse del envoltorio.
 */
async function request(url, options = {}, fallbackError = 'Error en la petición') {
  const res = await fetch(url, { ...options, headers: getHeaders(apiAuthToken) });

  if (res.status === 401) throw new Error('Sesión expirada');

  const payload = await res.json().catch(() => null);

  if (!res.ok || !payload?.success) {
    throw new Error(payload?.error || fallbackError);
  }

  return payload.data;
}

export async function getTasks(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.priority) params.append('priority', filters.priority);
  if (filters.search) params.append('search', filters.search);

  const query = params.toString();
  return request(`${API_BASE}${query ? `?${query}` : ''}`, {}, 'Error al cargar tareas');
}

export async function getTaskStats() {
  return request(`${API_BASE}/stats`, {}, 'Error al cargar el resumen');
}

export async function getTask(id) {
  return request(`${API_BASE}/${id}`, {}, 'Tarea no encontrada');
}

export async function createTask(task) {
  return request(
    API_BASE,
    { method: 'POST', body: JSON.stringify(task) },
    'Error al crear tarea',
  );
}

export async function updateTask(id, updates) {
  return request(
    `${API_BASE}/${id}`,
    { method: 'PATCH', body: JSON.stringify(updates) },
    'Error al actualizar tarea',
  );
}

export async function deleteTask(id) {
  return request(
    `${API_BASE}/${id}`,
    { method: 'DELETE' },
    'Error al eliminar tarea',
  );
}

export async function toggleCompleted(id, completed) {
  return updateTask(id, { completed });
}
