const AUTH_BASE = '/api/auth';

/**
 * Igual que en api.js: la API devuelve { success, data, timestamp }, así que
 * aquí se abre el sobre y se devuelve { user, token } directamente, que es lo
 * que AuthContext espera desestructurar.
 */
async function post(path, body, fallbackError) {
  const res = await fetch(`${AUTH_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const payload = await res.json().catch(() => null);

  if (!res.ok || !payload?.success) {
    throw new Error(payload?.error || fallbackError);
  }

  return payload.data;
}

export async function login(username, password) {
  return post('/login', { username, password }, 'Error al iniciar sesión');
}

export async function register(username, password) {
  return post('/register', { username, password }, 'Error al registrarse');
}
