import { refreshSession } from './authApi';

const API_BASE = '/api/tasks';

let apiAuthToken = null;

/** Avisos hacia AuthContext: uno cuando se renuevan credenciales, otro cuando
 *  la sesión se pierde definitivamente. Se registran en lugar de importar el
 *  contexto para no crear una dependencia circular entre servicio y contexto. */
let alRenovar = null;
let alPerderSesion = null;

export function setAuthToken(token) {
  apiAuthToken = token;
}

export function configurarAuth({ alRenovar: renovar, alPerderSesion: perder } = {}) {
  alRenovar = renovar ?? null;
  alPerderSesion = perder ?? null;
}

function getHeaders(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

/**
 * Renovación en curso, si la hay.
 *
 * Sirve para que varias peticiones que se topen con un 401 a la vez compartan
 * una sola llamada de renovación. Sin esto, cargar la pantalla dispararía tres
 * o cuatro renovaciones simultáneas con la misma cookie, y el servidor las
 * tomaría por reutilización del token: la sesión se cerraría sola.
 */
let renovacionEnCurso = null;

function renovar() {
  if (!renovacionEnCurso) {
    renovacionEnCurso = refreshSession()
      .then((datos) => {
        apiAuthToken = datos.accessToken;
        alRenovar?.(datos);
        return datos;
      })
      .catch((err) => {
        // El refresco tampoco vale: la sesión está muerta de verdad.
        alPerderSesion?.();
        throw err;
      })
      .finally(() => {
        renovacionEnCurso = null;
      });
  }
  return renovacionEnCurso;
}

/**
 * La API responde siempre con el sobre { success, data, timestamp } (o
 * { success:false, error } si falla). Este helper lo abre y devuelve solo
 * `data`, para que los componentes sigan recibiendo la tarea o el array de
 * tareas tal cual, sin enterarse del envoltorio.
 *
 * Ante un 401 intenta renovar y repite la petición **una sola vez**. El límite
 * importa: si el servidor devolviera 401 por cualquier otro motivo, reintentar
 * sin tope dejaría el cliente dando vueltas indefinidamente.
 */
async function request(url, options = {}, fallbackError = 'Error en la petición', reintentado = false) {
  const res = await fetch(url, { ...options, headers: getHeaders(apiAuthToken) });

  if (res.status === 401) {
    if (reintentado) throw new Error('Sesión expirada');

    try {
      await renovar();
    } catch {
      throw new Error('Sesión expirada');
    }

    return request(url, options, fallbackError, true);
  }

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
