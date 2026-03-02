const API_BASE = '/api/tasks';

function getHeaders(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

export function setAuthToken(token) {
  apiAuthToken = token;
}

let apiAuthToken = null;

export async function getTasks() {
  const res = await fetch(API_BASE, { headers: getHeaders(apiAuthToken) });
  if (res.status === 401) throw new Error('Sesión expirada');
  if (!res.ok) throw new Error('Error al cargar tareas');
  return res.json();
}

export async function getTask(id) {
  const res = await fetch(`${API_BASE}/${id}`, { headers: getHeaders(apiAuthToken) });
  if (res.status === 401) throw new Error('Sesión expirada');
  if (!res.ok) throw new Error('Tarea no encontrada');
  return res.json();
}

export async function createTask(task) {
  const res = await fetch(API_BASE, {
    method: 'POST',
    headers: getHeaders(apiAuthToken),
    body: JSON.stringify(task),
  });
  if (res.status === 401) throw new Error('Sesión expirada');
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || 'Error al crear tarea');
  }
  return res.json();
}

export async function updateTask(id, updates) {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: 'PATCH',
    headers: getHeaders(apiAuthToken),
    body: JSON.stringify(updates),
  });
  if (res.status === 401) throw new Error('Sesión expirada');
  if (!res.ok) throw new Error('Error al actualizar tarea');
  return res.json();
}

export async function deleteTask(id) {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: 'DELETE',
    headers: getHeaders(apiAuthToken),
  });
  if (res.status === 401) throw new Error('Sesión expirada');
  if (!res.ok) throw new Error('Error al eliminar tarea');
}

export async function toggleCompleted(id, completed) {
  return updateTask(id, { completed });
}
