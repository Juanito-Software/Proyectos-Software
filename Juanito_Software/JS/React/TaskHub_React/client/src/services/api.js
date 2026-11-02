/**
 * Cliente HTTP de las tareas (`/api/tasks`).
 *
 * Guarda el token de acceso en memoria del módulo, lo pone en cada petición
 * y, si el servidor responde 401 porque caducó, renueva la sesión con la
 * cookie de refresco y repite la petición una vez. Los componentes solo ven
 * los datos o un `Error` con el mensaje del servidor.
 */
import { refreshSession } from './authApi';

/** Prefijo de las rutas de tareas. */
const API_BASE = '/api/tasks';

/** Token de acceso actual; lo fija AuthContext con `setAuthToken`. */
let apiAuthToken = null;

/** Avisos hacia AuthContext: uno cuando se renuevan credenciales, otro cuando
 *  la sesión se pierde definitivamente. Se registran en lugar de importar el
 *  contexto para no crear una dependencia circular entre servicio y contexto. */
let alRenovar = null;
let alPerderSesion = null;

/**
 * Fija el token de acceso que se enviará en las siguientes peticiones.
 *
 * @param {string | null} token `null` al cerrar sesión
 */
export function setAuthToken(token) {
  apiAuthToken = token;
}

/**
 * Registra los avisos hacia AuthContext.
 *
 * @param {object} callbacks
 * @param {(datos: {user: object, accessToken: string}) => void} [callbacks.alRenovar]
 *        se llama tras cada renovación correcta
 * @param {() => void} [callbacks.alPerderSesion] se llama si la renovación
 *        falla y la sesión está perdida
 */
export function configurarAuth({ alRenovar: renovar, alPerderSesion: perder } = {}) {
  alRenovar = renovar ?? null;
  alPerderSesion = perder ?? null;
}

/** Cabeceras comunes: JSON y, si hay token, `Authorization: Bearer`. */
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

/**
 * Renueva la sesión, reutilizando la renovación en curso si ya hay una.
 *
 * @returns {Promise<object>} datos de la sesión renovada
 */
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
 *
 * @param {string} url
 * @param {RequestInit} [options] método y cuerpo
 * @param {string} [fallbackError] mensaje si el servidor no da uno
 * @param {boolean} [reintentado] uso interno
 * @returns {Promise<unknown>} el campo `data` de la respuesta
 * @throws {Error} con el mensaje del servidor, o «Sesión expirada»
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

/**
 * @param {{status?: string, priority?: string, search?: string}} [filters]
 * @returns {Promise<object[]>} tareas del usuario, más recientes primero
 */
export async function getTasks(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.priority) params.append('priority', filters.priority);
  if (filters.search) params.append('search', filters.search);

  const query = params.toString();
  return request(`${API_BASE}${query ? `?${query}` : ''}`, {}, 'Error al cargar tareas');
}

/** @returns {Promise<{total: number, pending: number, inProgress: number, completed: number}>} */
export async function getTaskStats() {
  return request(`${API_BASE}/stats`, {}, 'Error al cargar el resumen');
}

/** @returns {Promise<object>} una tarea por id */
export async function getTask(id) {
  return request(`${API_BASE}/${id}`, {}, 'Tarea no encontrada');
}

/**
 * @param {{title: string, description?: string, status?: string, priority?: string}} task
 * @returns {Promise<object>} la tarea creada
 */
export async function createTask(task) {
  return request(
    API_BASE,
    { method: 'POST', body: JSON.stringify(task) },
    'Error al crear tarea',
  );
}

/**
 * Actualización parcial (PATCH): solo se cambian los campos enviados.
 *
 * @param {string} id
 * @param {object} updates
 * @returns {Promise<object>} la tarea actualizada
 */
export async function updateTask(id, updates) {
  return request(
    `${API_BASE}/${id}`,
    { method: 'PATCH', body: JSON.stringify(updates) },
    'Error al actualizar tarea',
  );
}

/** @returns {Promise<{id: string}>} */
export async function deleteTask(id) {
  return request(
    `${API_BASE}/${id}`,
    { method: 'DELETE' },
    'Error al eliminar tarea',
  );
}

/**
 * Marca o desmarca una tarea. El servidor traduce `completed` a `status`.
 *
 * @param {string} id
 * @param {boolean} completed
 * @returns {Promise<object>} la tarea actualizada
 */
export async function toggleCompleted(id, completed) {
  return updateTask(id, { completed });
}
