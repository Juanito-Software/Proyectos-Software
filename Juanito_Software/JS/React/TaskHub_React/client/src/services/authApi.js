/**
 * Cliente HTTP de autenticación (`/api/auth`). Funciones sin estado: el token
 * de acceso lo guarda AuthContext y el de refresco, el navegador (cookie).
 *
 * Todas devuelven el campo `data` de la respuesta o lanzan un `Error` con el
 * mensaje del servidor.
 */
const AUTH_BASE = '/api/auth';

/**
 * Igual que en api.js: la API devuelve { success, data, timestamp }, así que
 * aquí se abre el sobre y se devuelve `data` directamente.
 *
 * El token de refresco no aparece en ninguna de estas respuestas: viaja en una
 * cookie HttpOnly que el navegador guarda y reenvía solo. Por eso no hay que
 * pasarle `credentials`: al ser mismo origen —en producción directamente, y en
 * desarrollo a través del proxy de Vite—, `fetch` ya manda las cookies por
 * defecto.
 *
 * @param {string} path ruta bajo /api/auth
 * @param {object} [body] cuerpo JSON
 * @param {string} fallbackError mensaje si el servidor no da uno
 * @returns {Promise<unknown>}
 */
async function post(path, body, fallbackError) {
  const res = await fetch(`${AUTH_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const payload = await res.json().catch(() => null);

  if (!res.ok || !payload?.success) {
    throw new Error(payload?.error || fallbackError);
  }

  return payload.data;
}

/** @returns {Promise<{user: object, accessToken: string}>} */
export async function login(username, password) {
  return post('/login', { username, password }, 'Error al iniciar sesión');
}

/** @returns {Promise<{user: object, accessToken: string}>} */
export async function register(username, password) {
  return post('/register', { username, password }, 'Error al registrarse');
}

/**
 * Cambia la cookie de refresco por credenciales nuevas.
 *
 * No recibe ningún argumento porque el token va en la cookie y el JavaScript
 * de la página no puede leerlo — que es justamente el objetivo.
 */
export async function refreshSession() {
  return post('/refresh', undefined, 'No se pudo renovar la sesión');
}

/**
 * Cierra la sesión **en el servidor**.
 *
 * Borrar el token del navegador no basta: hasta que el servidor revoca el
 * token de refresco, quien tuviera una copia podría seguir sacando tokens de
 * acceso nuevos durante días.
 */
export async function logout() {
  return post('/logout', undefined, 'No se pudo cerrar la sesión');
}

/**
 * Cierra todas las sesiones del usuario, en todos sus dispositivos.
 *
 * @param {string} accessToken token de acceso actual
 * @returns {Promise<{revocadas: number}>}
 */
export async function logoutAll(accessToken) {
  const res = await fetch(`${AUTH_BASE}/logout-all`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
  });

  const payload = await res.json().catch(() => null);

  if (!res.ok || !payload?.success) {
    throw new Error(payload?.error || 'No se pudieron cerrar las sesiones');
  }

  return payload.data;
}

/**
 * Cambia la contraseña de quien ya ha iniciado sesión.
 *
 * Devuelve **credenciales nuevas**, no un simple «hecho». El servidor revoca
 * todas las sesiones al cambiar la contraseña —incluida la de este navegador—
 * y abre una limpia a continuación, así que quien llame a esto tiene que
 * guardar el token de acceso que vuelve o se quedará fuera en la siguiente
 * petición.
 *
 * Necesita la cabecera `Authorization` porque la ruta exige sesión: el usuario
 * se saca del token, nunca del cuerpo.
 *
 * @param {string} accessToken token de acceso actual
 * @param {string} actual contraseña actual
 * @param {string} nueva contraseña nueva
 * @returns {Promise<{user: object, accessToken: string}>}
 */
export async function changePassword(accessToken, actual, nueva) {
  const res = await fetch(`${AUTH_BASE}/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({ actual, nueva }),
  });

  const payload = await res.json().catch(() => null);

  if (!res.ok || !payload?.success) {
    throw new Error(payload?.error || 'No se pudo cambiar la contraseña');
  }

  return payload.data;
}
