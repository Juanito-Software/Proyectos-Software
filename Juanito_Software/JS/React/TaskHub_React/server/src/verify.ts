import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import type { Server } from 'node:http';

// Aísla la suite del mundo real: fuerza el repositorio a leer/escribir en una
// carpeta temporal ANTES de crear la app (por eso el import de ./app es
// dinámico, después de fijar DATA_DIR). Sin esto, cada "npm run verify"
// dejaría usuarios de prueba para siempre en data/users.json.
const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'taskhub-verify-'));
process.env.DATA_DIR = tempDir;
fs.writeFileSync(path.join(tempDir, 'users.json'), '[]');
fs.writeFileSync(path.join(tempDir, 'tasks.json'), '[]');

const { createApp } = await import('./app.js');

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

    const playground = await fetch(`${BASE}/`);
    const playgroundHtml = await playground.text();
    check(
      'GET / sirve el playground HTML',
      playground.status === 200 && playgroundHtml.includes('TaskHub') && playgroundHtml.includes('authFetch'),
      `${playgroundHtml.length} bytes`,
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

    console.log(`\n${passed} passed, ${failed} failed\n`);
  } catch (err) {
    console.error('💥 La suite de verificación falló al ejecutarse:', err);
    failed++;
  } finally {
    server?.close();
    fs.rmSync(tempDir, { recursive: true, force: true });
    process.exitCode = failed > 0 ? 1 : 0;
  }
}

await run();
