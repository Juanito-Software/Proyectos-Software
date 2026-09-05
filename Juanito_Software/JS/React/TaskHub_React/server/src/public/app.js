/**
 * Lógica del playground de la API.
 *
 * ── Por qué es un fichero aparte ────────────────────────────────────────────
 *
 * Vivía dentro de un <script> en index.html, y eso obligaba a que la CSP
 * llevara 'unsafe-inline' en script-src. Con esa directiva puesta la política
 * deja de defender de la inyección de scripts, que es prácticamente lo único
 * que se le pide: un atacante que lograra inyectar una etiqueta de script en
 * la página la vería ejecutarse igual.
 *
 * Sacarlo aquí permite servirlo bajo 'self' y retirar esa concesión. Se pierde
 * la propiedad de «herramienta de un solo fichero» que tenía el playground; a
 * cambio, su CSP pasa a valer para algo.
 *
 * Se carga con el atributo defer, así que el DOM está construido antes de que
 * esto corra y los oyentes de eventos encuentran los elementos.
 */

let activeTasks = [];
let selectedTaskId = null;
let authMode = 'login';

// TaskHub1 es multiusuario: cada petición a /api/tasks necesita el JWT.
// Se guarda con la misma clave que usa el cliente React, así que si ya
// has iniciado sesión allí, el playground entra directamente.
const STORAGE_KEY = 'taskhub_auth';

function getAuth() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null;
  } catch {
    return null;
  }
}

function setAuth(auth) {
  if (auth) localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
  else localStorage.removeItem(STORAGE_KEY);
}

/**
 * Renovación en curso, para que dos peticiones que caduquen a la vez no
 * disparen dos renovaciones con la misma cookie. El servidor tomaría la
 * segunda por reutilización del token y cerraría la sesión entera.
 */
let renovacionEnCurso = null;

/**
 * Cambia la cookie de refresco por un token de acceso nuevo.
 *
 * El token de refresco no se ve desde aquí: va en una cookie HttpOnly que
 * el navegador manda sola. Por eso esta función no recibe nada.
 */
function renovarSesion() {
  if (!renovacionEnCurso) {
    renovacionEnCurso = fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (res) => {
        const payload = await res.json().catch(() => null);
        if (!res.ok || !payload?.success) throw new Error('sesión no renovable');
        setAuth({ user: payload.data.user, token: payload.data.accessToken });
        return payload.data;
      })
      .finally(() => {
        renovacionEnCurso = null;
      });
  }
  return renovacionEnCurso;
}

/**
 * fetch con el token puesto.
 *
 * El token de acceso dura quince minutos, así que caducar es lo normal, no
 * la excepción: ante un 401 se renueva y se repite la petición una sola
 * vez. Solo si la renovación también falla se vuelve al formulario.
 */
async function authFetch(url, options = {}, reintentado = false) {
  const auth = getAuth();
  const headers = { ...(options.headers || {}) };
  if (auth?.token) headers['Authorization'] = `Bearer ${auth.token}`;

  const res = await fetch(url, { ...options, headers });

  if (res.status === 401 && !reintentado) {
    try {
      await renovarSesion();
      return authFetch(url, options, true);
    } catch {
      // Cae al bloque de abajo: la sesión está muerta de verdad.
    }
  }

  if (res.status === 401) {
    setAuth(null);
    showAuthOverlay();
    showToast('Sesión expirada, vuelve a entrar', true);
  }
  return res;
}

// ── Autenticación ────────────────────────────────────────────────────

function showAuthOverlay() {
  document.getElementById('auth-overlay').classList.add('active');
  document.getElementById('user-badge').style.display = 'none';
  document.getElementById('admin-panel').style.display = 'none';
}

function hideAuthOverlay() {
  document.getElementById('auth-overlay').classList.remove('active');
  const auth = getAuth();
  if (auth?.user) {
    document.getElementById('current-user').innerText = auth.user.username;
    document.getElementById('user-badge').style.display = 'flex';
    // El panel de administración solo se enseña a quien tiene el rol. Es
    // una comodidad visual: si alguien lo forzara desde la consola del
    // navegador, el servidor seguiría respondiendo 403.
    document.getElementById('admin-panel').style.display =
      auth.user.role === 'admin' ? 'block' : 'none';
  }
}

/**
 * Borrado de un usuario. Pide el id en lugar de ofrecer una lista porque
 * el flujo natural es mirar antes GET /api/admin/users, copiar el id de
 * ahí y pegarlo: así se ve el efecto de las dos llamadas en la consola.
 */
async function deleteUserPrompt() {
  const id = prompt('Id del usuario a eliminar (lo ves en GET /api/admin/users):');
  if (!id) return;

  const confirmar = confirm(
    `Se eliminará el usuario ${id} y TODAS sus tareas.\n\nEsta acción no se puede deshacer.`,
  );
  if (!confirmar) return;

  await simulateAPI('DELETE', `/api/admin/users/${id.trim()}`);
}

function toggleAuthMode() {
  authMode = authMode === 'login' ? 'register' : 'login';
  const isLogin = authMode === 'login';
  document.getElementById('auth-title').innerText = isLogin ? 'Iniciar sesión' : 'Crear cuenta';
  document.getElementById('auth-sub').innerText = isLogin
    ? 'Accede para gestionar tus tareas desde el playground.'
    : 'Regístrate para empezar a crear tareas.';
  document.getElementById('auth-submit').innerText = isLogin ? 'Entrar' : 'Registrarse';
  document.getElementById('auth-switch-text').innerText = isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?';
  document.getElementById('auth-switch-btn').innerText = isLogin ? 'Regístrate' : 'Inicia sesión';
  document.getElementById('auth-error').classList.remove('active');
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const username = document.getElementById('auth-username').value;
  const password = document.getElementById('auth-password').value;
  const errorBox = document.getElementById('auth-error');
  const url = `/api/auth/${authMode === 'login' ? 'login' : 'register'}`;

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const payload = await res.json();
    updateConsole('POST', url, `${res.status} ${res.statusText}`, payload, !res.ok);

    if (res.ok && payload.success) {
      // El token de refresco no viene en el cuerpo: el servidor lo pone en
      // una cookie HttpOnly. Aquí solo se guarda el de acceso.
      setAuth({ user: payload.data.user, token: payload.data.accessToken });
      errorBox.classList.remove('active');
      document.getElementById('auth-form').reset();
      hideAuthOverlay();
      showToast(`Bienvenido, ${payload.data.user.username}`);
      fetchTasks();
    } else {
      errorBox.innerText = payload.error || 'No se pudo completar la operación';
      errorBox.classList.add('active');
    }
  } catch (err) {
    errorBox.innerText = 'Error de red: ' + err.message;
    errorBox.classList.add('active');
  }
}

/**
 * Cierra la sesión también en el servidor.
 *
 * Vaciar el localStorage no bastaría: el token de refresco vive en una
 * cookie y seguiría sirviendo para sacar tokens de acceso nuevos durante
 * días. La llamada revoca la familia entera.
 */
async function logout() {
  const url = '/api/auth/logout';
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const payload = await res.json().catch(() => null);
    updateConsole('POST', url, `${res.status} ${res.statusText}`, payload, !res.ok);
  } catch (err) {
    // Si la red falla se cierra igualmente en local: dejar al usuario
    // dentro por un fallo de red sería peor.
    updateConsole('POST', url, 'error de red', { error: err.message }, true);
  }

  setAuth(null);
  activeTasks = [];
  selectedTaskId = null;
  renderTasksList([]);
  showAuthOverlay();
  showToast('Sesión cerrada');
}

// ── Arranque ─────────────────────────────────────────────────────────

window.addEventListener('DOMContentLoaded', () => {
  if (getAuth()?.token) {
    hideAuthOverlay();
    fetchTasks();
  } else {
    showAuthOverlay();
  }
  fetchSystemStats();
  setInterval(fetchSystemStats, 3000);
});

function showToast(message, isError = false) {
  const toast = document.getElementById('toast');
  const msgSpan = document.getElementById('toast-message');
  toast.style.borderLeftColor = isError ? 'var(--danger)' : 'var(--primary)';
  msgSpan.innerText = message;
  toast.style.display = 'flex';
  setTimeout(() => { toast.style.display = 'none'; }, 3000);
}

async function fetchSystemStats() {
  try {
    const res = await fetch('/api/system/stats');
    const payload = await res.json();
    if (payload.success) {
      document.getElementById('req-count').innerText = payload.data.totalRequests;
      document.getElementById('uptime-count').innerText = payload.data.uptimeFormatted;
    }
  } catch (e) {
    // silencioso: no queremos ruido cada 3 segundos si el server se cae
  }
}

// Se construye el DOM en lugar de asignar innerHTML.
//
// La url incluye los filtros que escribe el usuario y prettyJson viene de
// la respuesta del servidor: con innerHTML, cualquier etiqueta dentro de
// esos textos se interpretaría como HTML y podría ejecutar código.
// textContent inserta el texto tal cual, sin interpretarlo nunca.
function updateConsole(method, url, status, data, isError = false) {
  const terminal = document.getElementById('terminal');
  const statusSpan = document.getElementById('response-status');

  statusSpan.innerText = `HTTP ${status}`;
  statusSpan.className = isError ? 'console-error' : 'console-success';

  const header = document.createElement('span');
  header.className = 'console-info';
  header.textContent = `>> ${method} ${url}\n`;

  terminal.replaceChildren(header, document.createTextNode(JSON.stringify(data, null, 2)));
  terminal.scrollTop = 0;
}

// ── Tareas ───────────────────────────────────────────────────────────

async function fetchTasks(manual = false) {
  if (!getAuth()?.token) { showAuthOverlay(); return; }

  const search = document.getElementById('search-input').value;
  const status = document.getElementById('status-filter').value;
  const priority = document.getElementById('priority-filter').value;

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (status) params.append('status', status);
  if (priority) params.append('priority', priority);

  const url = `/api/tasks?${params.toString()}`;
  try {
    const res = await authFetch(url);
    const payload = await res.json();

    if (res.ok && payload.success) {
      activeTasks = payload.data;
      renderTasksList(activeTasks);
      if (manual) {
        updateConsole('GET', url, `${res.status} ${res.statusText}`, payload);
        showToast('Lista actualizada');
      }
    } else {
      updateConsole('GET', url, `${res.status} ${res.statusText}`, payload, true);
    }
  } catch (err) {
    updateConsole('GET', url, 'ERROR', { error: err.message }, true);
  }
}

function renderTasksList(tasks) {
  const container = document.getElementById('tasks-container');
  document.getElementById('task-counter').innerText = tasks.length;

  if (!tasks || tasks.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        <p>No hay tareas que coincidan con los filtros.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = '';
  tasks.forEach(task => {
    const statusClass = `badge-${escapeHTML(task.status.replace('-', ''))}`;
    const createdDate = new Date(task.updatedAt).toLocaleString();

    const card = document.createElement('div');
    card.className = 'task-card';
    card.id = `card-${encodeURIComponent(task.id)}`;
    card.innerHTML = `
      <div class="task-content">
        <div class="task-header">
          <span class="task-title">${escapeHTML(task.title)}</span>
          <span class="badge ${statusClass}">${escapeHTML(task.status)}</span>
          <span class="badge badge-${escapeHTML(task.priority)}">${escapeHTML(task.priority)}</span>
        </div>
        <p class="task-desc">${escapeHTML(task.description || '—')}</p>
        <div class="task-footer">
          <span>ID: <strong>${escapeHTML(task.id.substring(0, 8))}…</strong></span>
          <span>•</span>
          <span>Actualizada: ${createdDate}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="icon-btn" data-accion="editar-tarea" data-id="${escapeHTML(task.id)}" title="Editar">
          <svg style="width:14px; height:14px" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125"></path></svg>
        </button>
        <button class="icon-btn delete" data-accion="borrar-tarea" data-id="${escapeHTML(task.id)}" title="Eliminar">
          <svg style="width:14px; height:14px" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"></path></svg>
        </button>
      </div>
    `;

    card.addEventListener('click', (e) => {
      if (e.target.closest('.task-actions') || e.target.closest('.icon-btn')) return;
      selectTask(task.id);
    });

    container.appendChild(card);
  });

  if (selectedTaskId && !tasks.some(t => t.id === selectedTaskId)) {
    selectedTaskId = null;
  }
  updateSelectedLabels();
}

function selectTask(id) {
  selectedTaskId = id;
  document.querySelectorAll('.task-card').forEach(c => c.style.borderColor = 'var(--card-border)');
  const selectedCard = document.getElementById(`card-${id}`);
  if (selectedCard) selectedCard.style.borderColor = 'var(--primary)';
  updateSelectedLabels();
  showToast(`Tarea seleccionada: ${id.substring(0, 8)}…`);
}

function updateSelectedLabels() {
  const suffix = selectedTaskId || ':id';
  ['btn-get-specific', 'btn-put-specific', 'btn-delete-specific'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.querySelector('.path').innerText = `/api/tasks/${suffix}`;
  });
}

// ── Modal ────────────────────────────────────────────────────────────

function openCreateModal() {
  if (!getAuth()?.token) { showAuthOverlay(); return; }
  document.getElementById('modal-title').innerText = 'Nueva tarea';
  document.getElementById('task-id').value = '';
  document.getElementById('task-form').reset();
  document.getElementById('form-submit-btn').innerText = 'Crear tarea';
  document.getElementById('task-modal').classList.add('active');
}

function openEditModal(id) {
  const task = activeTasks.find(t => t.id === id);
  if (!task) return;
  document.getElementById('modal-title').innerText = 'Editar tarea';
  document.getElementById('task-id').value = task.id;
  document.getElementById('form-title').value = task.title;
  document.getElementById('form-desc').value = task.description;
  document.getElementById('form-status').value = task.status;
  document.getElementById('form-priority').value = task.priority;
  document.getElementById('form-submit-btn').innerText = 'Guardar cambios';
  document.getElementById('task-modal').classList.add('active');
}

function closeModal() {
  document.getElementById('task-modal').classList.remove('active');
}

async function handleFormSubmit(e) {
  e.preventDefault();

  const id = document.getElementById('task-id').value;
  const body = {
    title: document.getElementById('form-title').value,
    description: document.getElementById('form-desc').value,
    status: document.getElementById('form-status').value,
    priority: document.getElementById('form-priority').value,
  };

  const isEdit = !!id;
  const url = isEdit ? `/api/tasks/${id}` : '/api/tasks';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await authFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const payload = await res.json();
    updateConsole(method, url, `${res.status} ${res.statusText}`, payload, !res.ok);

    if (res.ok && payload.success) {
      closeModal();
      showToast(isEdit ? 'Tarea actualizada' : 'Tarea creada');
      fetchTasks();
    } else {
      showToast(payload.error || 'La operación ha fallado', true);
    }
  } catch (err) {
    updateConsole(method, url, 'ERROR', { error: err.message }, true);
    showToast('Error de red', true);
  }
}

async function deleteTask(id) {
  if (!confirm('¿Eliminar esta tarea?')) return;

  const url = `/api/tasks/${id}`;
  try {
    const res = await authFetch(url, { method: 'DELETE' });
    const payload = await res.json();
    updateConsole('DELETE', url, `${res.status} ${res.statusText}`, payload, !res.ok);

    if (res.ok && payload.success) {
      showToast('Tarea eliminada');
      fetchTasks();
    } else {
      showToast(payload.error || 'No se pudo eliminar', true);
    }
  } catch (err) {
    updateConsole('DELETE', url, 'ERROR', { error: err.message }, true);
    showToast('Error de red', true);
  }
}

// ── Botones del panel lateral ────────────────────────────────────────

async function simulateAPI(method, url) {
  try {
    const res = await authFetch(url, { method });
    const payload = await res.json();
    updateConsole(method, url, `${res.status} ${res.statusText}`, payload, !res.ok);
    showToast(`Petición enviada a ${url}`);
  } catch (err) {
    updateConsole(method, url, 'ERROR', { error: err.message }, true);
  }
}

function requireSelection() {
  if (!selectedTaskId) {
    showToast('Selecciona antes una tarea de la lista', true);
    return false;
  }
  return true;
}

function simulateGetSpecific() {
  if (requireSelection()) simulateAPI('GET', `/api/tasks/${selectedTaskId}`);
}

function simulateDeleteSpecific() {
  if (requireSelection()) deleteTask(selectedTaskId);
}

function simulatePutSpecific() {
  if (requireSelection()) openEditModal(selectedTaskId);
}

function escapeHTML(str) {
  return String(str).replace(/[&<>'"]/g, tag => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
  }[tag] || tag));
}
/**
 * Enganche de eventos.
 *
 * ── Por qué no hay ni un onclick en el marcado ──────────────────────────────
 *
 * Cada acción viajaba antes en un atributo del HTML. Funcionaba, pero obligaba
 * a que la CSP permitiera script-src-attr 'unsafe-inline', y el navegador no
 * distingue el onclick que escribiste tú del que inyecta un atacante:
 * permitir uno es permitir los dos.
 *
 * Ahora el marcado declara QUÉ quiere hacer con data-accion, y aquí se decide
 * CÓMO. El HTML deja de contener código.
 *
 * ── Por qué un solo oyente y no uno por botón ───────────────────────────────
 *
 * Los botones de editar y borrar de cada tarea se crean y se destruyen en cada
 * repintado de la lista; con delegación no hay que volver a engancharlos, que
 * es el error clásico al hacer esta conversión. Y `closest` reproduce lo que
 * ya hacían las tarjetas de endpoint, donde el clic caía en un elemento hijo y
 * subía hasta el div que llevaba el manejador.
 */
const ACCIONES = {
  'cambiar-modo-auth': () => toggleAuthMode(),
  'salir': () => logout(),
  'simular': (el) => simulateAPI(el.dataset.metodo, el.dataset.url),
  'get-especifico': () => simulateGetSpecific(),
  'put-especifico': () => simulatePutSpecific(),
  'borrar-especifico': () => simulateDeleteSpecific(),
  'abrir-crear': () => openCreateModal(),
  'borrar-usuario': () => deleteUserPrompt(),
  'recargar': () => fetchTasks(true),
  'cerrar-modal': () => closeModal(),
  'editar-tarea': (el) => openEditModal(el.dataset.id),
  'borrar-tarea': (el) => deleteTask(el.dataset.id),
};

document.addEventListener('click', (evento) => {
  const elemento = evento.target.closest('[data-accion]');
  if (!elemento) return;

  const accion = ACCIONES[elemento.dataset.accion];
  if (accion) accion(elemento);
});

// Los envíos sí reciben el evento: sus manejadores lo necesitan para el
// preventDefault.
document.getElementById('auth-form').addEventListener('submit', handleAuthSubmit);
document.getElementById('task-form').addEventListener('submit', handleFormSubmit);

// Estos tres van envueltos en una función a propósito. `fetchTasks` recibe un
// primer argumento `manual` que decide si se muestra el aviso de recarga.
// Pasarlo directamente como oyente le entregaría el objeto Event, que es
// verdadero, y cada tecla escrita en el buscador sacaría un aviso.
document.getElementById('search-input').addEventListener('input', () => fetchTasks());
document.getElementById('status-filter').addEventListener('change', () => fetchTasks());
document.getElementById('priority-filter').addEventListener('change', () => fetchTasks());
