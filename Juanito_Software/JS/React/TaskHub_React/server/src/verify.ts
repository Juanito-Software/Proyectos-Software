import crypto from 'node:crypto';
import type { Server } from 'node:http';

// Aísla la suite del mundo real: cada ejecución crea un esquema propio dentro
// de la misma base de datos y lo destruye al terminar. Se hace con un esquema
// y no con una base de datos aparte porque no requiere permisos especiales y
// funciona igual en local que en Neon o en un runner de CI.
//
// El nombre se fija ANTES de importar ./app, porque el pool lee DB_SCHEMA al
// construirse; por eso los imports de la app son dinámicos.
const testSchema = `verify_${crypto.randomUUID().replace(/-/g, '').slice(0, 12)}`;
process.env.DB_SCHEMA = testSchema;

// Credenciales del administrador de prueba. Se fijan antes de importar la
// configuración, que las lee al cargarse.
const ADMIN_USER = `admin-${crypto.randomUUID().slice(0, 8)}`;
const ADMIN_PASS = 'admin-password-de-prueba-larga';
process.env.ADMIN_USERNAME = ADMIN_USER;
process.env.ADMIN_PASSWORD = ADMIN_PASS;

const { pool, query, initSchema, closePool } = await import('./config/db.js');
const { seedAdmin } = await import('./config/seed-admin.js');
const { createApp } = await import('./app.js');

await pool.query(`CREATE SCHEMA IF NOT EXISTS ${testSchema}`);
await initSchema();
await seedAdmin();

const PORT = 4050;
const BASE = `http://localhost:${PORT}`;

let passed = 0;
let failed = 0;

function check(name: string, ok: boolean, details?: string): void {
  console.log(`${ok ? '✅' : '❌'} ${name}${details ? ` — ${details}` : ''}`);
  ok ? passed++ : failed++;
}

interface Envelope<T> {
  success: boolean;
  data: T;
  error?: string;
}

async function run(): Promise<void> {
  console.log('\n--- TaskHub API verification ---\n');
  let server: Server | null = null;

  try {
    const app = createApp();
    server = app.listen(PORT);

    const username = `verify-${crypto.randomUUID().slice(0, 8)}`;
    const password = 'verify-pass-123';

    // ── Autenticación ────────────────────────────────────────────────────

    const reg = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const regBody = (await reg.json()) as Envelope<{ token: string }>;
    check(
      'POST /api/auth/register',
      reg.status === 201 && regBody.success === true && !!regBody.data?.token,
      `status ${reg.status}`,
    );
    const token = regBody.data?.token ?? '';
    const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };

    const login = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    check('POST /api/auth/login', login.status === 200, `status ${login.status}`);

    const noAuth = await fetch(`${BASE}/api/tasks`);
    const noAuthBody = (await noAuth.json()) as Envelope<unknown>;
    check(
      'GET /api/tasks sin token -> 401 con success:false',
      noAuth.status === 401 && noAuthBody.success === false,
      `status ${noAuth.status}`,
    );

    // ── CRUD ─────────────────────────────────────────────────────────────

    const empty = await fetch(`${BASE}/api/tasks`, { headers: auth });
    const emptyBody = (await empty.json()) as Envelope<unknown[]>;
    check(
      'GET /api/tasks (usuario nuevo, vacío)',
      empty.status === 200 && Array.isArray(emptyBody.data) && emptyBody.data.length === 0,
    );

    const create = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: 'Tarea de verificación', description: 'smoke test', priority: 'high' }),
    });
    const created = (await create.json()) as Envelope<{ id: string; status: string; priority: string; completed: boolean }>;
    check('POST /api/tasks (válida) -> 201', create.status === 201 && !!created.data?.id, `status ${create.status}`);
    check(
      'La tarea nace pending/high y completed:false',
      created.data?.status === 'pending' && created.data?.priority === 'high' && created.data?.completed === false,
      `status=${created.data?.status} priority=${created.data?.priority}`,
    );
    const taskId = created.data?.id ?? '';

    const invalid = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: '   ' }),
    });
    check('POST /api/tasks (título vacío) -> 400', invalid.status === 400, `status ${invalid.status}`);

    const badStatus = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: 'Estado inválido', status: 'no-existe' }),
    });
    check('POST /api/tasks (status inválido) -> 400', badStatus.status === 400, `status ${badStatus.status}`);

    const dup = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: 'Tarea de verificación' }),
    });
    check('POST /api/tasks (título duplicado) -> 409', dup.status === 409, `status ${dup.status}`);

    const getOne = await fetch(`${BASE}/api/tasks/${taskId}`, { headers: auth });
    check('GET /api/tasks/:id', getOne.status === 200);

    // ── completed <-> status ─────────────────────────────────────────────

    const patch = await fetch(`${BASE}/api/tasks/${taskId}`, {
      method: 'PATCH',
      headers: auth,
      body: JSON.stringify({ completed: true }),
    });
    const patchBody = (await patch.json()) as Envelope<{ completed: boolean; status: string }>;
    check(
      'PATCH completed:true traduce a status:completed',
      patch.status === 200 && patchBody.data?.completed === true && patchBody.data?.status === 'completed',
      `status=${patchBody.data?.status}`,
    );

    const patchStatus = await fetch(`${BASE}/api/tasks/${taskId}`, {
      method: 'PATCH',
      headers: auth,
      body: JSON.stringify({ status: 'in-progress' }),
    });
    const patchStatusBody = (await patchStatus.json()) as Envelope<{ completed: boolean; status: string }>;
    check(
      'PATCH status:in-progress deja completed:false',
      patchStatusBody.data?.status === 'in-progress' && patchStatusBody.data?.completed === false,
      `completed=${patchStatusBody.data?.completed}`,
    );

    // ── Filtros ──────────────────────────────────────────────────────────

    await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: 'Comprar pan', description: 'panadería', priority: 'low' }),
    });

    const byStatus = await fetch(`${BASE}/api/tasks?status=in-progress`, { headers: auth });
    const byStatusBody = (await byStatus.json()) as Envelope<{ id: string }[]>;
    check(
      'GET /api/tasks?status=in-progress',
      byStatusBody.data?.length === 1 && byStatusBody.data[0].id === taskId,
      `${byStatusBody.data?.length} resultado(s)`,
    );

    const byPriority = await fetch(`${BASE}/api/tasks?priority=low`, { headers: auth });
    const byPriorityBody = (await byPriority.json()) as Envelope<{ title: string }[]>;
    check(
      'GET /api/tasks?priority=low',
      byPriorityBody.data?.length === 1 && byPriorityBody.data[0].title === 'Comprar pan',
      `${byPriorityBody.data?.length} resultado(s)`,
    );

    const bySearch = await fetch(`${BASE}/api/tasks?search=PANADER`, { headers: auth });
    const bySearchBody = (await bySearch.json()) as Envelope<{ title: string }[]>;
    check(
      'GET /api/tasks?search= (busca en descripción, sin distinguir mayúsculas)',
      bySearchBody.data?.length === 1 && bySearchBody.data[0].title === 'Comprar pan',
      `${bySearchBody.data?.length} resultado(s)`,
    );

    const badFilter = await fetch(`${BASE}/api/tasks?status=inventado`, { headers: auth });
    check('GET /api/tasks?status=inventado -> 400', badFilter.status === 400, `status ${badFilter.status}`);

    // ── Estadísticas ─────────────────────────────────────────────────────

    const taskStats = await fetch(`${BASE}/api/tasks/stats`, { headers: auth });
    const taskStatsBody = (await taskStats.json()) as Envelope<{ total: number; inProgress: number; pending: number }>;
    check(
      'GET /api/tasks/stats (resumen del usuario)',
      taskStats.status === 200 && taskStatsBody.data?.total === 2 && taskStatsBody.data?.inProgress === 1,
      JSON.stringify(taskStatsBody.data),
    );

    const sysStats = await fetch(`${BASE}/api/system/stats`);
    const sysStatsBody = (await sysStats.json()) as Envelope<{ totalRequests: number; uptimeFormatted: string }>;
    check(
      'GET /api/system/stats (uptime y contador)',
      sysStats.status === 200 && typeof sysStatsBody.data?.totalRequests === 'number' && !!sysStatsBody.data?.uptimeFormatted,
      `${sysStatsBody.data?.totalRequests} peticiones`,
    );

    // ── Playground ───────────────────────────────────────────────────────

    const playground = await fetch(`${BASE}/playground`);
    const playgroundHtml = await playground.text();
    check(
      'GET /playground sirve el playground HTML',
      playground.status === 200 && playgroundHtml.includes('TaskHub') && playgroundHtml.includes('authFetch'),
      `${playgroundHtml.length} bytes`,
    );

    // Una ruta inventada del cliente devuelve el index.html para que sea el
    // enrutador de React quien decida, pero una ruta inventada de la API
    // sigue devolviendo 404 en JSON: si no, un error de escritura en una
    // llamada devolvería HTML y el cliente fallaría al parsearlo.
    const apiNotFound = await fetch(`${BASE}/api/ruta-que-no-existe`, { headers: auth });
    const apiNotFoundBody = (await apiNotFound.json().catch(() => null)) as Envelope<unknown> | null;
    check(
      'Una ruta inexistente de /api/ devuelve 404 en JSON, no el HTML del cliente',
      apiNotFound.status === 404 && apiNotFoundBody?.success === false,
      `status ${apiNotFound.status}`,
    );

    // ── Aislamiento entre usuarios ───────────────────────────────────────

    const otherUsername = `verify-${crypto.randomUUID().slice(0, 8)}`;
    const otherReg = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: otherUsername, password }),
    });
    const otherToken = ((await otherReg.json()) as Envelope<{ token: string }>).data?.token ?? '';
    const otherAuth = { 'Content-Type': 'application/json', Authorization: `Bearer ${otherToken}` };

    const otherList = await fetch(`${BASE}/api/tasks`, { headers: otherAuth });
    const otherListBody = (await otherList.json()) as Envelope<unknown[]>;
    check('Aislamiento: el otro usuario no ve las tareas', otherListBody.data?.length === 0);

    const otherGet = await fetch(`${BASE}/api/tasks/${taskId}`, { headers: otherAuth });
    check('Aislamiento: 404 al leer una tarea ajena', otherGet.status === 404, `status ${otherGet.status}`);

    // El título duplicado es por usuario: otro usuario SÍ puede repetirlo.
    const otherSameTitle = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: otherAuth,
      body: JSON.stringify({ title: 'Tarea de verificación' }),
    });
    check(
      'El título duplicado se comprueba por usuario, no globalmente',
      otherSameTitle.status === 201,
      `status ${otherSameTitle.status}`,
    );

    // ── Garantía en la base de datos ─────────────────────────────────────

    // El servicio comprueba el duplicado antes de insertar, pero comprobar y
    // escribir son dos operaciones: con ficheros JSON, dos peticiones a la vez
    // podían pasar ambas la comprobación y crear la tarea las dos. El índice
    // único cierra esa ventana, y además normaliza — así que ni cambiando
    // mayúsculas ni añadiendo espacios se cuela un duplicado.
    //
    // Se prueba directamente contra la base de datos, saltándose la API, para
    // verificar la garantía real y no la comprobación previa del servicio.
    const owner = (
      await query<{ id: string }>('SELECT id FROM users WHERE LOWER(username) = LOWER($1)', [username])
    )[0];

    let rejectedByIndex = false;
    let rejectionCode = '';
    try {
      await pool.query(
        'INSERT INTO tasks (title, status, priority, user_id) VALUES ($1, $2, $3, $4)',
        ['  COMPRAR PAN  ', 'pending', 'medium', owner.id],
      );
    } catch (err) {
      rejectionCode = (err as { code?: string }).code ?? '';
      rejectedByIndex = rejectionCode === '23505';
    }
    check(
      'El índice único rechaza el duplicado aunque cambien mayúsculas y espacios',
      rejectedByIndex,
      rejectionCode ? `código ${rejectionCode}` : 'no se rechazó',
    );

    // ── Administración ───────────────────────────────────────────────────

    const regRole = (regBody.data as unknown as { user?: { role?: string } })?.user?.role;
    check(
      'Registrarse crea un usuario con rol "user", nunca admin',
      regRole === 'user',
      `rol recibido: ${regRole}`,
    );

    // Aunque el cliente mande role:"admin" en el registro, el rol lo pone la
    // base de datos por defecto y el repositorio no lo acepta como parámetro.
    const sneakyUser = `sneaky-${crypto.randomUUID().slice(0, 8)}`;
    const sneaky = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: sneakyUser, password, role: 'admin' }),
    });
    const sneakyBody = (await sneaky.json()) as Envelope<{ user: { role: string } }>;
    check(
      'Mandar role:"admin" al registrarse no concede el rol',
      sneakyBody.data?.user?.role === 'user',
      `rol recibido: ${sneakyBody.data?.user?.role}`,
    );

    const userAdminAttempt = await fetch(`${BASE}/api/admin/users`, { headers: auth });
    check(
      'Un usuario normal recibe 403 en /api/admin',
      userAdminAttempt.status === 403,
      `status ${userAdminAttempt.status}`,
    );

    const noTokenAdmin = await fetch(`${BASE}/api/admin/users`);
    check(
      'Sin token, /api/admin devuelve 401 y no 403',
      noTokenAdmin.status === 401,
      `status ${noTokenAdmin.status}`,
    );

    // El administrador entra con la contraseña de la semilla, no registrándose.
    const adminLogin = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: ADMIN_USER, password: ADMIN_PASS }),
    });
    const adminBody = (await adminLogin.json()) as Envelope<{
      token: string;
      user: { id: string; role: string };
    }>;
    check(
      'El administrador de la semilla existe y entra con rol admin',
      adminLogin.status === 200 && adminBody.data?.user?.role === 'admin',
      `status ${adminLogin.status}, rol ${adminBody.data?.user?.role}`,
    );
    const adminAuth = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${adminBody.data?.token ?? ''}`,
    };
    const adminId = adminBody.data?.user?.id ?? '';

    const adminUsers = await fetch(`${BASE}/api/admin/users`, { headers: adminAuth });
    const adminUsersBody = (await adminUsers.json()) as Envelope<
      { username: string; taskCount: number }[]
    >;
    check(
      'GET /api/admin/users lista a todos con su número de tareas',
      adminUsers.status === 200 && (adminUsersBody.data?.length ?? 0) >= 3,
      `${adminUsersBody.data?.length} usuarios`,
    );

    check(
      'El listado de administración no expone ningún hash de contraseña',
      !JSON.stringify(adminUsersBody.data).includes('$2b$'),
    );

    const selfDelete = await fetch(`${BASE}/api/admin/users/${adminId}`, {
      method: 'DELETE',
      headers: adminAuth,
    });
    check(
      'Un administrador no puede borrarse a sí mismo',
      selfDelete.status === 400,
      `status ${selfDelete.status}`,
    );

    const adminStats = await fetch(`${BASE}/api/admin/stats`, { headers: adminAuth });
    const adminStatsBody = (await adminStats.json()) as Envelope<{ users: number; admins: number }>;
    check(
      'GET /api/admin/stats devuelve el resumen global',
      adminStats.status === 200 && adminStatsBody.data?.admins === 1,
      JSON.stringify(adminStatsBody.data),
    );

    // Borrar al usuario colado se lleva por delante la tarea que creó.
    const sneakyId = (
      await query<{ id: string }>('SELECT id FROM users WHERE LOWER(username) = LOWER($1)', [
        sneakyUser,
      ])
    )[0].id;
    const adminDelete = await fetch(`${BASE}/api/admin/users/${sneakyId}`, {
      method: 'DELETE',
      headers: adminAuth,
    });
    const stillThere = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM users WHERE id = $1',
      [sneakyId],
    );
    check(
      'El administrador borra a otro usuario y desaparece de la base de datos',
      adminDelete.status === 200 && stillThere[0].count === 0,
      `status ${adminDelete.status}`,
    );

    // ── Borrado ──────────────────────────────────────────────────────────

    const del = await fetch(`${BASE}/api/tasks/${taskId}`, { method: 'DELETE', headers: auth });
    const delBody = (await del.json()) as Envelope<{ id: string }>;
    check(
      'DELETE /api/tasks/:id -> 200 con success:true',
      del.status === 200 && delBody.success === true && delBody.data?.id === taskId,
      `status ${del.status}`,
    );

    const getAfterDelete = await fetch(`${BASE}/api/tasks/${taskId}`, { headers: auth });
    check('GET tras borrar -> 404', getAfterDelete.status === 404, `status ${getAfterDelete.status}`);

    // ── Integridad referencial ───────────────────────────────────────────

    // La clave foránea con ON DELETE CASCADE garantiza que no queden tareas
    // huérfanas apuntando a un usuario que ya no existe. Con ficheros JSON
    // esto no lo aseguraba nada.
    const orphanUser = ((await query<{ id: string }>(
      'SELECT id FROM users WHERE LOWER(username) = LOWER($1)',
      [otherUsername],
    )) ?? [])[0];
    await pool.query('DELETE FROM users WHERE id = $1', [orphanUser.id]);
    const orphanTasks = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM tasks WHERE user_id = $1',
      [orphanUser.id],
    );
    check(
      'Borrar un usuario arrastra sus tareas (ON DELETE CASCADE)',
      orphanTasks[0].count === 0,
      `${orphanTasks[0].count} tarea(s) huérfana(s)`,
    );

    console.log(`\n${passed} passed, ${failed} failed\n`);
  } catch (err) {
    console.error('💥 La suite de verificación falló al ejecutarse:', err);
    failed++;
  } finally {
    server?.close();
    // El esquema se borra pase lo que pase, incluso si la suite revienta a
    // mitad: si no, cada ejecución fallida dejaría tablas de prueba atrás.
    await pool.query(`DROP SCHEMA IF EXISTS ${testSchema} CASCADE`);
    await closePool();
    process.exitCode = failed > 0 ? 1 : 0;
  }
}

await run();
