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

// La suite prueba una decena de contraseñas que deben ser rechazadas, y cada
// rechazo cuenta como intento fallido de autenticación. Con el límite de
// producción (10 por cuarto de hora) la propia suite se estrangularía y todo lo
// que viniera después fallaría por 429 en vez de por lo que se está probando.
// La variable se ignora cuando NODE_ENV es production; ver rateLimit.middleware.
process.env.AUTH_RATE_LIMIT = '1000';

// El tope duro por cuenta es 200 en producción. Aquí se baja a 20 para poder
// comprobar el mecanismo sin lanzar doscientas peticiones, y los retrasos
// progresivos se apagan del todo: con la curva puesta, esos veintiún intentos
// tardarían siete minutos en vez de dos segundos. Ambas variables se ignoran
// cuando NODE_ENV es 'production'.
//
// Lo que se prueba aquí es que la clave del contador es la CUENTA y no la
// dirección. La curva de retrasos se fija aparte, con tests unitarios sobre la
// función pura que la calcula: medir esperas reales daría un test lento y
// frágil sin comprobar nada más.
process.env.ACCOUNT_RATE_LIMIT = '20';
process.env.ACCOUNT_SLOWDOWN_AFTER = '10000';

// Credenciales del administrador de prueba. Se fijan antes de importar la
// configuración, que las lee al cargarse.
const ADMIN_USER = `admin-${crypto.randomUUID().slice(0, 8)}`;
const ADMIN_PASS = 'Clave larga del Admin 7!';
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
    const password = 'Frase de paso para verificar 7!';

    // ── Autenticación ────────────────────────────────────────────────────

    const reg = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const regBody = (await reg.json()) as Envelope<{ accessToken: string }>;
    check(
      'POST /api/auth/register',
      reg.status === 201 && regBody.success === true && !!regBody.data?.accessToken,
      `status ${reg.status}`,
    );
    const token = regBody.data?.accessToken ?? '';
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
      playground.status === 200 && playgroundHtml.includes('TaskHub') && /<script[^>]+src=/.test(playgroundHtml),
      `${playgroundHtml.length} bytes`,
    );

    // La lógica ya no viaja dentro del HTML: vive en un fichero aparte, que es
    // lo que permite que la CSP no tenga que admitir código en línea.
    //
    // La URL NO se escribe aquí a mano: se saca del propio marcado y se
    // resuelve contra la dirección de la página igual que haría el navegador.
    // Escribirla a mano fue justo el fallo que dejó el playground inerte: el
    // src era relativo, la página se sirve en "/playground" sin barra final, y
    // el navegador pedía "/app.js" mientras la comprobación pedía
    // "/playground/app.js" y la daba por buena. Resolviéndola así, la
    // comprobación solo puede pasar si el navegador encuentra el fichero.
    const srcDelScript = /<script[^>]+src="([^"]+)"/.exec(playgroundHtml)?.[1];
    const urlDelScript = new URL(srcDelScript ?? '', `${BASE}/playground`).href;
    const playgroundJs = await fetch(urlDelScript);
    const playgroundJsBody = await playgroundJs.text();
    check(
      'El navegador encuentra la lógica en la URL que resuelve el src',
      playgroundJs.status === 200 &&
        (playgroundJs.headers.get('content-type') ?? '').includes('javascript') &&
        playgroundJsBody.includes('authFetch'),
      `${urlDelScript} -> ${playgroundJs.status}, ${playgroundJs.headers.get('content-type')}`,
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
    const otherToken =
      ((await otherReg.json()) as Envelope<{ accessToken: string }>).data?.accessToken ?? '';
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

    // ── Política de contraseñas ──────────────────────────────────────────
    //
    // Longitud mínima, admitir contraseñas largas, no truncar y comparar contra
    // una lista de bloqueo vienen de NIST SP 800-63B Rev 4. Exigir mayúscula,
    // número y símbolo es decisión propia de TaskHub y es MÁS restrictivo que
    // la norma, que dice que no deberían imponerse reglas de composición.
    //
    // Lo que se comprueba aquí es que la validación existe en la API y no solo
    // en el formulario: estas peticiones no pasan por el navegador.

    const registrar = (u: string, p: string) =>
      fetch(`${BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p }),
      });

    const nuevo = () => `pol-${crypto.randomUUID().slice(0, 8)}`;

    const corta = await registrar(nuevo(), 'Corto-Horse12!'); // 14
    check(
      'Registro con contraseña de 14 caracteres -> 400',
      corta.status === 400,
      `status ${corta.status}`,
    );

    // Justo en el mínimo, cumpliendo los cuatro requisitos.
    const quinceUser = nuevo();
    const quince = await registrar(quinceUser, 'Correct-Horse2!');
    const cuerpoRegistro = await quince.text();
    check(
      'Registro con exactamente 15 caracteres y composición válida -> 201',
      quince.status === 201,
      `status ${quince.status}`,
    );

    // Y debe poder entrar después con esa misma contraseña.
    const quinceLogin = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: quinceUser, password: 'Correct-Horse2!' }),
    });
    check(
      'Se puede iniciar sesión después de registrarse',
      quinceLogin.status === 200,
      `status ${quinceLogin.status}`,
    );

    // Una contraseña larga y válida, con espacios: la norma exige admitirlos.
    const largaUser = nuevo();
    const largaOk = await registrar(largaUser, 'Una frase larga de paso con 2 espacios!');
    check(
      'Registro con contraseña larga y con espacios -> 201',
      largaOk.status === 201,
      `status ${largaOk.status}`,
    );

    // ── Las tres reglas de composición, una a una ────────────────────────

    const sinMayuscula = await registrar(nuevo(), 'correct-horse-2026!');
    check(
      'Registro sin mayúscula -> 400',
      sinMayuscula.status === 400,
      `status ${sinMayuscula.status}`,
    );

    const sinNumero = await registrar(nuevo(), 'Correct-Horse-Battery!');
    check('Registro sin número -> 400', sinNumero.status === 400, `status ${sinNumero.status}`);

    const sinSimbolo = await registrar(nuevo(), 'Correct Horse Battery 2026');
    check('Registro sin símbolo -> 400', sinSimbolo.status === 400, `status ${sinSimbolo.status}`);

    // El espacio no cuenta como símbolo: si contara, esta pasaría.
    const soloEspacios = await registrar(nuevo(), 'Frase Con Espacios 2026');
    check(
      'El espacio no cuenta como símbolo -> 400',
      soloEspacios.status === 400,
      `status ${soloEspacios.status}`,
    );

    // El caso que antes definía la política y que ahora deja de valer: una
    // frase larga sin mayúsculas, números ni símbolos. Queda como registro
    // explícito del cambio de criterio.
    const fraseSinComposicion = await registrar(nuevo(), 'caballo correcto grapa pila');
    check(
      'Una frase sin composición ya no basta para registrarse -> 400',
      fraseSinComposicion.status === 400,
      `status ${fraseSinComposicion.status}`,
    );

    // ── Lista de bloqueo y patrones previsibles ──────────────────────────

    const comun = await registrar(nuevo(), 'passwordpassword');
    check(
      'Registro con contraseña de la lista de bloqueo -> 400',
      comun.status === 400,
      `status ${comun.status}`,
    );

    // Cumple los cuatro requisitos y aun así es de las primeras que se prueban:
    // es literalmente lo que produce obligar a mezclar tipos de carácter. Sin
    // esta comprobación, la regla de composición dejaría la aplicación peor.
    const previsible = await registrar(nuevo(), 'Password123456!');
    check(
      'Registro con "palabra común + adornos" -> 400 pese a cumplir composición',
      previsible.status === 400,
      `status ${previsible.status}`,
    );

    const conNombre = await registrar('pedrito', 'Pedrito y su clave 7!');
    check(
      'Registro con la contraseña conteniendo el usuario -> 400',
      conNombre.status === 400,
      `status ${conNombre.status}`,
    );

    const excesiva = await registrar(nuevo(), 'A1!' + 'x'.repeat(73));
    check(
      'Registro con más de 72 bytes -> 400, no se recorta en silencio',
      excesiva.status === 400,
      `status ${excesiva.status}`,
    );

    // Ninguno de los rechazados puede haber creado usuario.
    const colados = await query<{ count: number }>(
      `SELECT COUNT(*) AS count FROM users WHERE LOWER(username) IN ('pedrito')`,
    );
    check(
      'Un registro rechazado por la política no crea el usuario',
      colados[0].count === 0,
      `${colados[0].count} usuario(s)`,
    );

    // Y la respuesta de un registro correcto no puede llevar el hash ni la
    // contraseña: es lo que se guarda, no algo que se devuelva.
    check(
      'La respuesta del registro no expone contraseña ni hash',
      !cuerpoRegistro.includes('Correct-Horse2!') &&
        !/password_hash|passwordHash|\$2[aby]\$/.test(cuerpoRegistro),
      `${cuerpoRegistro.length} bytes de respuesta revisados`,
    );

    // ── Compatibilidad con cuentas anteriores a la política ──────────────
    //
    // Endurecer la política no invalida cuentas existentes. Se simula
    // insertando el hash directamente, como haría una cuenta creada antes.

    const bcryptLib = (await import('bcrypt')).default;

    const antiguoUser = `antiguo-${crypto.randomUUID().slice(0, 8)}`;
    const antiguaPass = 'corta12'; // 7 caracteres: imposible de registrar hoy
    await pool.query('INSERT INTO users (username, password_hash) VALUES ($1, $2)', [
      antiguoUser,
      await bcryptLib.hash(antiguaPass, 10),
    ]);
    const loginAntiguo = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: antiguoUser, password: antiguaPass }),
    });
    check(
      'Una cuenta anterior a la política entra con su contraseña de siempre',
      loginAntiguo.status === 200,
      `status ${loginAntiguo.status}`,
    );

    // El caso concreto del cambio de hoy: una cuenta creada cuando bastaba una
    // frase de paso sin composición sigue entrando con ella.
    const fraseUser = `frase-${crypto.randomUUID().slice(0, 8)}`;
    const fraseAntigua = 'caballo correcto grapa pila';
    await pool.query('INSERT INTO users (username, password_hash) VALUES ($1, $2)', [
      fraseUser,
      await bcryptLib.hash(fraseAntigua, 10),
    ]);
    const loginFrase = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: fraseUser, password: fraseAntigua }),
    });
    check(
      'Una cuenta con frase sin composición sigue pudiendo entrar',
      loginFrase.status === 200,
      `status ${loginFrase.status}`,
    );

    // ── La confirmación no forma parte del contrato de la API ────────────

    const confirmacionUser = nuevo();
    const conConfirmacion = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: confirmacionUser,
        password: 'Otra frase de paso 7!',
        passwordConfirmation: 'algo completamente distinto',
      }),
    });
    check(
      'La API ignora passwordConfirmation: la comparación es del formulario',
      conConfirmacion.status === 201,
      `status ${conConfirmacion.status}`,
    );

    // Y no se guarda en ninguna parte: la tabla de usuarios no tiene dónde.
    const columnas = await query<{ column_name: string }>(
      `SELECT column_name FROM information_schema.columns
       WHERE table_schema = $1 AND table_name = 'users'`,
      [testSchema],
    );
    check(
      'passwordConfirmation no se persiste: no existe tal columna',
      !columnas.some((c) => /confirm/i.test(c.column_name)),
      columnas.map((c) => c.column_name).join(', '),
    );

    // El login sigue con su contrato de siempre: usuario y contraseña.
    const loginConConfirmacion = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: confirmacionUser,
        password: 'Otra frase de paso 7!',
        passwordConfirmation: 'irrelevante',
      }),
    });
    check(
      'El login funciona con username y password, e ignora la confirmación',
      loginConConfirmacion.status === 200,
      `status ${loginConConfirmacion.status}`,
    );

    // ── Autorización: recursos de otro usuario ───────────────────────────
    //
    // Hasta ahora solo se comprobaba la LECTURA: que el listado ajeno viniera
    // vacío y que un GET de una tarea ajena devolviera 404. La escritura no se
    // probaba en ningún sitio.
    //
    // Es el hueco más grave que sacó la auditoría. El código mete `user_id` en
    // el WHERE de las tres operaciones, así que funciona; pero si alguien
    // quitara esa condición en un refactor, la suite entera seguiría en verde
    // mientras cualquier usuario podría editar y borrar las tareas de los
    // demás. Es el patrón OWASP A01, y no basta con mirar el código de
    // estado: hay que comprobar en la base de datos que la fila no cambió.

    /** Estado de una tarea directamente en la base de datos, sin pasar por la API. */
    const filaDeTarea = async (id: string) => {
      const filas = await query<{ title: string; status: string; user_id: string }>(
        'SELECT title, status, user_id FROM tasks WHERE id = $1',
        [id],
      );
      return filas[0] ?? null;
    };

    const victimaUser = `victima-${crypto.randomUUID().slice(0, 8)}`;
    const atacanteUser = `atacante-${crypto.randomUUID().slice(0, 8)}`;

    const victimaReg = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: victimaUser, password }),
    });
    const victimaToken =
      ((await victimaReg.json()) as Envelope<{ accessToken: string }>).data?.accessToken ?? '';

    const atacanteReg = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: atacanteUser, password }),
    });
    const atacanteToken =
      ((await atacanteReg.json()) as Envelope<{ accessToken: string }>).data?.accessToken ?? '';

    const cabeceraVictima = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${victimaToken}`,
    };
    const cabeceraAtacante = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${atacanteToken}`,
    };

    const tareaVictima = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: cabeceraVictima,
      body: JSON.stringify({ title: 'Secreto de la víctima', description: 'no tocar' }),
    });
    const idVictima =
      ((await tareaVictima.json()) as Envelope<{ id: string }>).data?.id ?? '';

    // ── Lectura ──────────────────────────────────────────────────────────

    const leerAjena = await fetch(`${BASE}/api/tasks/${idVictima}`, { headers: cabeceraAtacante });
    check(
      'IDOR · GET de una tarea ajena -> 404',
      leerAjena.status === 404,
      `status ${leerAjena.status}`,
    );

    // ── PATCH ────────────────────────────────────────────────────────────

    const patchAjena = await fetch(`${BASE}/api/tasks/${idVictima}`, {
      method: 'PATCH',
      headers: cabeceraAtacante,
      body: JSON.stringify({ title: 'Secuestrada', status: 'completed' }),
    });
    check(
      'IDOR · PATCH de una tarea ajena -> 404',
      patchAjena.status === 404,
      `status ${patchAjena.status}`,
    );

    const trasPatch = await filaDeTarea(idVictima);
    check(
      'IDOR · el PATCH ajeno NO modificó la fila',
      trasPatch?.title === 'Secreto de la víctima' && trasPatch?.status === 'pending',
      `title="${trasPatch?.title}" status=${trasPatch?.status}`,
    );

    // ── PUT ──────────────────────────────────────────────────────────────
    //
    // PUT no tenía ni un solo test en ninguna capa, y comparte controlador con
    // PATCH: si el aislamiento se rompiera solo en uno de los dos, nadie se
    // enteraría.

    const putAjena = await fetch(`${BASE}/api/tasks/${idVictima}`, {
      method: 'PUT',
      headers: cabeceraAtacante,
      body: JSON.stringify({ title: 'Reemplazada', description: 'por el atacante' }),
    });
    check(
      'IDOR · PUT de una tarea ajena -> 404',
      putAjena.status === 404,
      `status ${putAjena.status}`,
    );

    const trasPut = await filaDeTarea(idVictima);
    check(
      'IDOR · el PUT ajeno NO modificó la fila',
      trasPut?.title === 'Secreto de la víctima',
      `title="${trasPut?.title}"`,
    );

    // ── DELETE ───────────────────────────────────────────────────────────

    const borrarAjena = await fetch(`${BASE}/api/tasks/${idVictima}`, {
      method: 'DELETE',
      headers: cabeceraAtacante,
    });
    check(
      'IDOR · DELETE de una tarea ajena -> 404',
      borrarAjena.status === 404,
      `status ${borrarAjena.status}`,
    );

    const trasBorradoAjeno = await filaDeTarea(idVictima);
    check(
      'IDOR · el DELETE ajeno NO borró la fila',
      trasBorradoAjeno !== null,
      trasBorradoAjeno ? 'la tarea sigue ahí' : 'LA TAREA HA DESAPARECIDO',
    );

    // Y la dueña sigue pudiendo hacerlo todo: el aislamiento no puede estar
    // bloqueando también al legítimo.
    const patchPropia = await fetch(`${BASE}/api/tasks/${idVictima}`, {
      method: 'PATCH',
      headers: cabeceraVictima,
      body: JSON.stringify({ status: 'completed' }),
    });
    check(
      'La dueña sí puede modificar su propia tarea',
      patchPropia.status === 200,
      `status ${patchPropia.status}`,
    );

    // ── Administración ───────────────────────────────────────────────────

    const borrarUsuarioAjeno = await fetch(`${BASE}/api/admin/users/${crypto.randomUUID()}`, {
      method: 'DELETE',
      headers: cabeceraAtacante,
    });
    check(
      'Un usuario normal no puede borrar cuentas -> 403',
      borrarUsuarioAjeno.status === 403,
      `status ${borrarUsuarioAjeno.status}`,
    );

    // ── Identificadores mal formados ─────────────────────────────────────
    //
    // Antes de validar la forma, cualquiera de estos llegaba a una consulta
    // donde la columna es UUID y acababa en 500 con el error de PostgreSQL.

    const malFormado = 'no-soy-un-uuid';
    for (const [metodo, cuerpo] of [
      ['GET', null],
      ['PATCH', JSON.stringify({ title: 'x' })],
      ['PUT', JSON.stringify({ title: 'x' })],
      ['DELETE', null],
    ] as [string, string | null][]) {
      const res = await fetch(`${BASE}/api/tasks/${malFormado}`, {
        method: metodo,
        headers: cabeceraVictima,
        ...(cuerpo ? { body: cuerpo } : {}),
      });
      check(
        `${metodo} /api/tasks/<no-uuid> -> 400, nunca 500`,
        res.status === 400,
        `status ${res.status}`,
      );
    }

    // ── Límites de entrada ───────────────────────────────────────────────

    const descripcionEnorme = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: cabeceraVictima,
      body: JSON.stringify({ title: 'Con descripción enorme', description: 'x'.repeat(5001) }),
    });
    check(
      'POST con descripción de más de 5 000 caracteres -> 400',
      descripcionEnorme.status === 400,
      `status ${descripcionEnorme.status}`,
    );

    const descripcionEnLimite = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: cabeceraVictima,
      body: JSON.stringify({ title: 'Descripción justa', description: 'x'.repeat(5000) }),
    });
    check(
      'POST con descripción de exactamente 5 000 -> 201',
      descripcionEnLimite.status === 201,
      `status ${descripcionEnLimite.status}`,
    );

    const busquedaEnorme = await fetch(`${BASE}/api/tasks?search=${'a'.repeat(201)}`, {
      headers: cabeceraVictima,
    });
    check(
      'Búsqueda de más de 200 caracteres -> 400',
      busquedaEnorme.status === 400,
      `status ${busquedaEnorme.status}`,
    );

    // ── Tokens de acceso y refresco ──────────────────────────────────────
    //
    // El grueso de esta sección no comprueba que la renovación funcione, sino
    // que NO funcione cuando no debe: token gastado, revocado, de otro usuario,
    // usado como token de acceso. La rotación solo aporta seguridad si la
    // reutilización se detecta.

    /** Saca el token de refresco de la cabecera Set-Cookie de una respuesta. */
    const cookieDeRespuesta = (res: Response): string | null => {
      for (const cookie of res.headers.getSetCookie()) {
        const m = /^taskhub_refresh=([^;]*)/.exec(cookie);
        // Una cookie de borrado llega con el valor vacío: no es un token.
        if (m && m[1]) return decodeURIComponent(m[1]);
      }
      return null;
    };

    /**
     * Atributos declarados en la cabecera Set-Cookie del refresco, **sin el
     * valor del token**.
     *
     * La censura no es cosmética. Esta cadena acaba en `console.log` a través
     * del detalle de cada comprobación, y esa salida queda guardada en el
     * registro del CI, que es visible para cualquiera que pueda ver el
     * repositorio. Imprimir la cabecera entera dejaría allí un token de
     * refresco utilizable durante siete días. Lo detectó CodeQL con
     * «clear-text logging of sensitive information».
     */
    const atributosCookie = (res: Response): string => {
      for (const cookie of res.headers.getSetCookie()) {
        if (cookie.startsWith('taskhub_refresh=')) {
          return cookie.replace(/^taskhub_refresh=[^;]*/, 'taskhub_refresh=<censurado>');
        }
      }
      return '';
    };

    const entrar = (u: string, p: string) =>
      fetch(`${BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p }),
      });

    const renovar = (refresco: string | null) =>
      fetch(`${BASE}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(refresco ? { Cookie: `taskhub_refresh=${refresco}` } : {}),
        },
      });

    const cerrarSesion = (refresco: string | null) =>
      fetch(`${BASE}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(refresco ? { Cookie: `taskhub_refresh=${refresco}` } : {}),
        },
      });

    // ── Forma de las credenciales ────────────────────────────────────────

    const sesion = await entrar(username, password);
    const sesionBody = (await sesion.json()) as Envelope<{ accessToken: string; refreshToken?: string }>;
    const refrescoInicial = cookieDeRespuesta(sesion);

    check(
      'El login devuelve un token de acceso en el cuerpo',
      !!sesionBody.data?.accessToken,
      sesionBody.data?.accessToken ? 'presente' : 'AUSENTE',
    );

    check(
      'El token de refresco llega por cookie, no en el cuerpo',
      !!refrescoInicial && sesionBody.data?.refreshToken === undefined,
      `cookie ${refrescoInicial ? 'presente' : 'ausente'}, cuerpo ${sesionBody.data?.refreshToken === undefined ? 'limpio' : 'CONTIENE EL REFRESCO'}`,
    );

    const atributos = atributosCookie(sesion);
    check(
      'La cookie de refresco es HttpOnly: el JavaScript de la página no la ve',
      /HttpOnly/i.test(atributos),
      atributos || 'sin cabecera',
    );
    check(
      'La cookie va con SameSite=Strict, que es lo que cierra el CSRF',
      /SameSite=Strict/i.test(atributos),
      atributos || 'sin cabecera',
    );
    check(
      'La cookie se limita a /api/auth y no viaja al resto de la API',
      /Path=\/api\/auth/i.test(atributos),
      atributos || 'sin cabecera',
    );

    const jwtDecode = (await import('jsonwebtoken')).default;
    const claims = jwtDecode.decode(sesionBody.data?.accessToken ?? '') as {
      typ?: string;
      exp: number;
      iat: number;
    } | null;

    check(
      'El token de acceso se identifica como tal con typ=access',
      claims?.typ === 'access',
      `typ=${claims?.typ}`,
    );

    const duracionMin = claims ? (claims.exp - claims.iat) / 60 : -1;
    check(
      'El token de acceso dura minutos, no días',
      duracionMin > 0 && duracionMin <= 60,
      `${duracionMin} minutos`,
    );

    // ── El token guardado no es el token ─────────────────────────────────

    const hashes = await query<{ token_hash: string }>(
      `SELECT token_hash FROM refresh_sessions ORDER BY created_at DESC LIMIT 1`,
    );
    check(
      'En la base de datos se guarda el hash del refresco, nunca el token',
      hashes.length > 0 &&
        hashes[0].token_hash !== refrescoInicial &&
        /^[0-9a-f]{64}$/.test(hashes[0].token_hash),
      hashes[0]?.token_hash?.slice(0, 16) + '…',
    );

    // ── Rotación ─────────────────────────────────────────────────────────

    const rot1 = await renovar(refrescoInicial);
    const rot1Body = (await rot1.json()) as Envelope<{ accessToken: string }>;
    const refrescoB = cookieDeRespuesta(rot1);

    check('Renovar con un refresco válido -> 200', rot1.status === 200, `status ${rot1.status}`);
    check(
      'La renovación entrega un token de acceso nuevo',
      !!rot1Body.data?.accessToken && rot1Body.data.accessToken !== sesionBody.data?.accessToken,
      'distinto del anterior',
    );
    check(
      'La renovación entrega también un refresco nuevo: el token es de un solo uso',
      !!refrescoB && refrescoB !== refrescoInicial,
      refrescoB ? 'rotado' : 'NO SE ROTÓ',
    );

    const accesoTrasRenovar = await fetch(`${BASE}/api/tasks`, {
      headers: { Authorization: `Bearer ${rot1Body.data?.accessToken}` },
    });
    check(
      'El token de acceso recién renovado sirve para pedir datos',
      accesoTrasRenovar.status === 200,
      `status ${accesoTrasRenovar.status}`,
    );

    const familias = await query<{ family_id: string; total: number }>(
      `SELECT family_id, COUNT(*)::int AS total
         FROM refresh_sessions
        GROUP BY family_id
        HAVING COUNT(*) > 1
        LIMIT 1`,
    );
    check(
      'La rotación encadena el token nuevo a la misma familia',
      familias.length === 1 && familias[0].total === 2,
      `${familias[0]?.total ?? 0} eslabones en la familia`,
    );

    // ── Detección de reutilización ───────────────────────────────────────
    //
    // El token A ya se gastó. Presentarlo otra vez significa que alguien tiene
    // una copia, y por tanto también el B que salió de él: hay que revocar la
    // familia entera, no solo rechazar esta petición.
    //
    // Se retrasa artificialmente `revoked_at` para salir de la ventana de
    // tolerancia, que existe para no confundir dos pestañas simultáneas con un
    // ataque. Sin este retroceso habría que esperar diez segundos reales.
    await pool.query(
      `UPDATE refresh_sessions
          SET revoked_at = now() - interval '1 hour'
        WHERE token_hash = $1`,
      [crypto.createHash('sha256').update(refrescoInicial ?? '').digest('hex')],
    );

    const reutilizado = await renovar(refrescoInicial);
    check(
      'Reutilizar un refresco ya gastado -> 401',
      reutilizado.status === 401,
      `status ${reutilizado.status}`,
    );

    const trasReuso = await renovar(refrescoB);
    check(
      'La reutilización revoca la familia entera: el refresco vigente tampoco vale',
      trasReuso.status === 401,
      `status ${trasReuso.status}`,
    );

    const motivos = await query<{ revoked_reason: string; total: number }>(
      `SELECT revoked_reason, COUNT(*)::int AS total
         FROM refresh_sessions
        WHERE revoked_reason = 'reuse-detected'
        GROUP BY revoked_reason`,
    );
    check(
      'La revocación por reutilización queda registrada con su motivo',
      motivos.length === 1 && motivos[0].total >= 1,
      `${motivos[0]?.total ?? 0} fila(s) marcadas como reuse-detected`,
    );

    // ── Renovaciones simultáneas ─────────────────────────────────────────
    //
    // Dos pestañas del mismo usuario, o la aplicación y el playground a la vez,
    // pueden renovar con la misma cookie. Solo una debe ganar, pero eso NO es
    // un ataque: si la perdedora matara la familia, el usuario se quedaría
    // fuera por el simple hecho de tener dos pestañas abiertas.
    //
    // Lo que hace segura la carrera es la condición `revoked_at IS NULL` dentro
    // del propio UPDATE. PostgreSQL serializa las escrituras sobre una misma
    // fila, así que de dos rotaciones del mismo token solo una la encuentra sin
    // revocar. Eso se comprueba aquí de forma DETERMINISTA, llamando dos veces
    // seguidas: si el guardián no estuviera, la segunda también encontraría
    // fila y las dos rotaciones saldrían adelante.
    //
    // Se hace secuencial y no con Promise.all a propósito. Lanzar peticiones en
    // paralelo aquí daba un falso positivo: el driver del entorno de desarrollo
    // solo admite una conexión, tumbaba la segunda con "connection terminated"
    // y el test pasaba porque solo una había respondido 200 — no porque el
    // guardián funcionara. Un test que pasa por el motivo equivocado es peor
    // que no tenerlo.

    const concUser = `conc-${crypto.randomUUID().slice(0, 8)}`;
    await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: concUser, password }),
    });
    const concLogin = await entrar(concUser, password);
    const concRefresco = cookieDeRespuesta(concLogin);
    const concHash = crypto.createHash('sha256').update(concRefresco ?? '').digest('hex');

    const { sessionsRepository } = await import('./modules/auth/sessions.repository.js');

    const primeraRotacion = await sessionsRepository.marcarRotado(concHash);
    const segundaRotacion = await sessionsRepository.marcarRotado(concHash);

    check(
      'La rotación es atómica: el mismo token no puede rotarse dos veces',
      primeraRotacion !== null && segundaRotacion === null,
      `primera ${primeraRotacion ? 'gana' : 'falla'}, segunda ${segundaRotacion ? 'GANA TAMBIÉN' : 'rechazada'}`,
    );

    // La perdedora, dentro de la ventana de tolerancia, se rechaza pero NO
    // revoca la familia: es el escenario de las dos pestañas.
    const perdedora = await renovar(concRefresco);
    check(
      'La renovación perdedora se rechaza con 401',
      perdedora.status === 401,
      `status ${perdedora.status}`,
    );

    const familiaConc = await query<{ revoked_reason: string }>(
      `SELECT revoked_reason FROM refresh_sessions
        WHERE user_id = (SELECT id FROM users WHERE username = $1)
          AND revoked_reason = 'reuse-detected'`,
      [concUser],
    );
    check(
      'Dentro de la ventana de tolerancia NO se marca como reutilización',
      familiaConc.length === 0,
      `${familiaConc.length} fila(s) marcadas por error`,
    );

    // ── Entradas inválidas en la renovación ──────────────────────────────

    const sinCookie = await renovar(null);
    check('Renovar sin cookie -> 401', sinCookie.status === 401, `status ${sinCookie.status}`);

    const inventado = await renovar('token-que-nunca-ha-existido-jamas');
    check(
      'Renovar con un refresco inventado -> 401',
      inventado.status === 401,
      `status ${inventado.status}`,
    );

    const malformado = await renovar('%%%no-es-base64url%%%');
    check(
      'Renovar con un refresco malformado -> 401',
      malformado.status === 401,
      `status ${malformado.status}`,
    );

    // El token de acceso es un JWT; el de refresco, bytes aleatorios. Ninguno
    // de los dos puede hacer el papel del otro.
    const accesoComoRefresco = await renovar(rot1Body.data?.accessToken ?? '');
    check(
      'Un token de acceso NO sirve como refresco',
      accesoComoRefresco.status === 401,
      `status ${accesoComoRefresco.status}`,
    );

    const refrescoComoAcceso = await fetch(`${BASE}/api/tasks`, {
      headers: { Authorization: `Bearer ${concRefresco}` },
    });
    check(
      'Un token de refresco NO sirve como token de acceso',
      refrescoComoAcceso.status === 401,
      `status ${refrescoComoAcceso.status}`,
    );

    // Los tokens de la versión anterior no llevaban typ y duraban siete días.
    const antiguo = jwtDecode.sign(
      { userId: crypto.randomUUID(), username: 'antiguo' },
      process.env.JWT_SECRET ?? 'clave-solo-para-desarrollo-no-usar-en-produccion',
      { expiresIn: '7d' },
    );
    const conTokenAntiguo = await fetch(`${BASE}/api/tasks`, {
      headers: { Authorization: `Bearer ${antiguo}` },
    });
    check(
      'Un token de la política anterior (sin typ, 7 días) queda invalidado',
      conTokenAntiguo.status === 401,
      `status ${conTokenAntiguo.status}`,
    );

    // ── Cierre de sesión ─────────────────────────────────────────────────

    const salidaUser = `salida-${crypto.randomUUID().slice(0, 8)}`;
    await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: salidaUser, password }),
    });

    const sesion1 = await entrar(salidaUser, password);
    const refresco1 = cookieDeRespuesta(sesion1);
    const sesion2 = await entrar(salidaUser, password);
    const refresco2 = cookieDeRespuesta(sesion2);

    check(
      'Dos inicios de sesión del mismo usuario abren sesiones independientes',
      !!refresco1 && !!refresco2 && refresco1 !== refresco2,
      'refrescos distintos',
    );

    const salida = await cerrarSesion(refresco1);
    check('POST /api/auth/logout -> 200', salida.status === 200, `status ${salida.status}`);
    check(
      'El logout borra la cookie del navegador',
      /taskhub_refresh=;/.test(salida.headers.getSetCookie().join('|')),
      // Sin volcar la cabecera: la de borrado va vacía, pero imprimirla tal
      // cual invitaría a copiar el mismo patrón donde sí lleva token.
      `${salida.headers.getSetCookie().length} cabecera(s) Set-Cookie`,
    );

    const trasSalir = await renovar(refresco1);
    check(
      'Tras cerrar sesión, su refresco deja de valer',
      trasSalir.status === 401,
      `status ${trasSalir.status}`,
    );

    const otraSesion = await renovar(refresco2);
    check(
      'Cerrar una sesión no afecta a las demás del mismo usuario',
      otraSesion.status === 200,
      `status ${otraSesion.status}`,
    );
    // La renovación anterior rotó el token: para seguir usando esa sesión hay
    // que quedarse con la cookie nueva.
    const refresco2Rotado = cookieDeRespuesta(otraSesion);

    // El logout revoca en el SERVIDOR, no solo en el navegador: es la
    // diferencia con la implementación anterior.
    const revocadas = await query<{ count: number }>(
      `SELECT COUNT(*) AS count FROM refresh_sessions
        WHERE user_id = (SELECT id FROM users WHERE username = $1)
          AND revoked_reason = 'logout'`,
      [salidaUser],
    );
    check(
      'La revocación se registra en el servidor, no depende del cliente',
      revocadas[0].count >= 1,
      `${revocadas[0].count} fila(s) revocadas por logout`,
    );

    // ── Cierre de todas las sesiones ─────────────────────────────────────

    const globalUser = `global-${crypto.randomUUID().slice(0, 8)}`;
    await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: globalUser, password }),
    });

    const gs1 = await entrar(globalUser, password);
    const gs2 = await entrar(globalUser, password);
    const gs3 = await entrar(globalUser, password);
    const gr1 = cookieDeRespuesta(gs1);
    const gr2 = cookieDeRespuesta(gs2);
    const gr3 = cookieDeRespuesta(gs3);
    const gAcceso = ((await gs3.json()) as Envelope<{ accessToken: string }>).data?.accessToken;

    const sinAutenticar = await fetch(`${BASE}/api/auth/logout-all`, { method: 'POST' });
    check(
      'Cerrar todas las sesiones exige estar autenticado',
      sinAutenticar.status === 401,
      `status ${sinAutenticar.status}`,
    );

    const todas = await fetch(`${BASE}/api/auth/logout-all`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${gAcceso}` },
    });
    check(
      'POST /api/auth/logout-all -> 200',
      todas.status === 200,
      `status ${todas.status}`,
    );

    // Secuencial y no en paralelo: lo que se comprueba es que las tres estén
    // revocadas, no la concurrencia, y el driver del entorno de desarrollo solo
    // admite una conexión.
    const resultados = [await renovar(gr1), await renovar(gr2), await renovar(gr3)];
    check(
      'Tras cerrar todas, ninguna de las tres sesiones puede renovar',
      resultados.every((r) => r.status === 401),
      resultados.map((r) => r.status).join(', '),
    );

    // El identificador sale del token, no del cuerpo: nadie puede cerrar las
    // sesiones de otro.
    const ajenoSesiones = await renovar(refresco2Rotado);
    check(
      'Cerrar todas las sesiones propias no toca las de otro usuario',
      ajenoSesiones.status === 200,
      `status ${ajenoSesiones.status}`,
    );

    // ── Renovación de una cuenta que ya no existe ────────────────────────

    const borrableUser = `borrable-${crypto.randomUUID().slice(0, 8)}`;
    await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: borrableUser, password }),
    });
    const sesionBorrable = await entrar(borrableUser, password);
    const refrescoBorrable = cookieDeRespuesta(sesionBorrable);
    await pool.query('DELETE FROM users WHERE username = $1', [borrableUser]);

    const trasBorrar = await renovar(refrescoBorrable);
    check(
      'Renovar con la cuenta ya borrada -> 401',
      trasBorrar.status === 401,
      `status ${trasBorrar.status}`,
    );

    // El token de ACCESO de esa cuenta sigue siendo válido hasta que caduque:
    // es la contrapartida asumida de no consultar la base de datos en cada
    // petición. Lo que no puede pasar es que el servidor reviente al usarlo.
    const accesoBorrable =
      ((await sesionBorrable.json()) as Envelope<{ accessToken: string }>).data?.accessToken ?? '';
    const cabeceraBorrable = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accesoBorrable}`,
    };

    const crearBorrado = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: cabeceraBorrable,
      body: JSON.stringify({ title: 'Tarea de una cuenta que ya no existe' }),
    });
    check(
      'Crear una tarea con la cuenta borrada -> 401, no 500 por clave foránea',
      crearBorrado.status === 401,
      `status ${crearBorrado.status}`,
    );

    // ── Limpieza de sesiones caducadas ───────────────────────────────────
    //
    // `limpiarCaducadas()` existía desde el primer día y no la llamaba nadie:
    // la tabla crecía sin techo. Aquí se comprueba que hace lo que dice y, más
    // importante, que NO se lleva por delante las sesiones vivas.

    const antesDeLimpiar = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM refresh_sessions WHERE expires_at < now()',
    );

    // Se caduca a mano una sesión viva para tener algo que limpiar.
    const limpiezaUser = `limpieza-${crypto.randomUUID().slice(0, 8)}`;
    await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: limpiezaUser, password }),
    });
    await pool.query(
      `UPDATE refresh_sessions SET expires_at = now() - interval '1 day'
        WHERE user_id = (SELECT id FROM users WHERE username = $1)`,
      [limpiezaUser],
    );

    const vivasAntes = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM refresh_sessions WHERE expires_at > now()',
    );

    const { sessionsRepository: repoSesiones } = await import(
      './modules/auth/sessions.repository.js'
    );
    const borradas = await repoSesiones.limpiarCaducadas();

    check(
      'limpiarCaducadas() elimina las sesiones ya caducadas',
      borradas >= antesDeLimpiar[0].count + 1,
      `${borradas} eliminada(s)`,
    );

    const vivasDespues = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM refresh_sessions WHERE expires_at > now()',
    );
    check(
      'limpiarCaducadas() NO toca las sesiones vivas',
      vivasDespues[0].count === vivasAntes[0].count,
      `${vivasAntes[0].count} antes, ${vivasDespues[0].count} después`,
    );

    const caducadasDespues = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM refresh_sessions WHERE expires_at < now()',
    );
    check(
      'Tras limpiar no queda ninguna caducada',
      caducadasDespues[0].count === 0,
      `${caducadasDespues[0].count} restante(s)`,
    );

    // ── Cabeceras de seguridad ───────────────────────────────────────────

    const cabeceras = await fetch(`${BASE}/playground`);
    const csp = cabeceras.headers.get('content-security-policy') ?? '';

    check(
      'La CSP está presente y restringe el origen por defecto',
      csp.includes("default-src 'self'"),
      csp ? 'presente' : 'AUSENTE',
    );

    // Aquí se comprobaba antes justo lo contrario: que la CSP NO bloqueara los
    // manejadores onclick, porque el playground dependía de ellos. Ya no queda
    // ninguno, así que la comprobación se invierte y pasa a ser la que de
    // verdad interesa.
    check(
      'script-src no admite código en línea',
      !/script-src\s[^;]*'unsafe-inline'/.test(csp),
      csp.match(/script-src\s[^;]*/)?.[0] ?? 'AUSENTE',
    );

    check(
      'script-src-attr bloquea los manejadores en atributos',
      /script-src-attr\s+'none'/.test(csp),
      csp.match(/script-src-attr\s[^;]*/)?.[0] ?? 'AUSENTE',
    );

    // Las dos de arriba solo valen si la página no depende de lo que prohíben.
    // Una política estricta sobre un documento que la incumple no protege:
    // rompe. Y rompe en silencio, porque el HTML carga igual y lo único que
    // deja de funcionar son los botones — que es exactamente lo que pasó la
    // primera vez y lo que ninguna comprobación de API puede ver.
    const htmlDelPlayground = await (await fetch(`${BASE}/playground`)).text();
    const enLinea = htmlDelPlayground.match(/\son(click|change|submit|input|load|mouse\w+)=/g) ?? [];

    check(
      'El marcado del playground no trae ningún manejador en atributos',
      enLinea.length === 0,
      enLinea.length ? `${enLinea.length} encontrado(s)` : 'ninguno',
    );

    // Lo que importa aquí es que NO quede código en línea y que lo que haya
    // sea un script externo. La ruta concreta no se comprueba con una cadena
    // escrita a mano —eso ya obligó a tocar esta línea al cambiarla—: de que
    // el navegador la encuentre se ocupa la comprobación que la resuelve.
    const scriptExterno = /<script[^>]+src="[^"]+"[^>]*>\s*<\/script>/.exec(htmlDelPlayground)?.[0];
    check(
      'El playground carga su lógica desde un fichero, no desde un bloque en línea',
      !!scriptExterno && scriptExterno.includes('defer') && !/<script>/.test(htmlDelPlayground),
      scriptExterno ?? 'no hay ningún script externo',
    );

    // ── El cableado de eventos, entero ──────────────────────────────────
    //
    // Al quitar los onclick, cada botón pasó a depender de que su acción
    // exista en la tabla ACCIONES. Si alguien añade un data-accion y olvida
    // el manejador, el botón queda muerto: no hay error, no hay aviso en la
    // consola, simplemente no pasa nada al pulsarlo. Es el mismo silencio que
    // tuvo el playground entero mientras el script no se cargaba, y por eso
    // se comprueba aquí en vez de fiarlo a que un e2e pulse ese botón
    // concreto: los e2e prueban unos pocos, esto los cubre todos.
    const srcAqui = /<script[^>]+src="([^"]+)"/.exec(htmlDelPlayground)?.[1];
    const js = await (await fetch(new URL(srcAqui ?? '', `${BASE}/playground`).href)).text();

    const declaradas = new Set(
      [...(/const ACCIONES = \{([\s\S]*?)\n\};/.exec(js)?.[1] ?? '').matchAll(/^\s+'([a-z-]+)'/gm)].map((m) => m[1]),
    );
    const usadas = new Set(
      [...htmlDelPlayground.matchAll(/data-accion="([a-z-]+)"/g), ...js.matchAll(/data-accion="([a-z-]+)"/g)].map(
        (m) => m[1],
      ),
    );

    const sinManejador = [...usadas].filter((a) => !declaradas.has(a));
    const sinUsar = [...declaradas].filter((a) => !usadas.has(a));

    check(
      'Toda acción del marcado tiene manejador: ningún botón queda muerto',
      sinManejador.length === 0,
      sinManejador.length ? `sin manejador: ${sinManejador.join(', ')}` : `${usadas.size} acciones, todas cubiertas`,
    );

    check(
      'No sobra ningún manejador: la tabla no arrastra acciones que ya no existen',
      sinUsar.length === 0,
      sinUsar.length ? `declaradas y sin usar: ${sinUsar.join(', ')}` : `${declaradas.size} manejadores, todos en uso`,
    );

    // Los cinco oyentes que no van por delegación se enganchan por id nada más
    // cargar. Si un id desaparece del marcado, getElementById devuelve null y
    // el TypeError corta el resto del arranque: los formularios dejan de
    // enviarse y los filtros de buscar. Tampoco daría error visible en la
    // página, solo una línea en la consola que nadie mira.
    const idsEnganchados = [...js.matchAll(/document\.getElementById\('([a-z-]+)'\)\.addEventListener/g)].map(
      (m) => m[1],
    );
    const idsQueFaltan = idsEnganchados.filter((id) => !htmlDelPlayground.includes(`id="${id}"`));

    check(
      'Los oyentes directos encuentran su elemento: el arranque no se corta',
      idsEnganchados.length > 0 && idsQueFaltan.length === 0,
      idsQueFaltan.length ? `no están en el marcado: ${idsQueFaltan.join(', ')}` : `${idsEnganchados.length} ids, todos presentes`,
    );

    check(
      'La CSP impide que la página se cargue dentro de un iframe ajeno',
      csp.includes("frame-ancestors 'none'"),
    );

    check(
      'Se envía X-Content-Type-Options: nosniff',
      cabeceras.headers.get('x-content-type-options') === 'nosniff',
    );

    // ── CORS ─────────────────────────────────────────────────────────────
    //
    // El navegador manda `Origin` también en las peticiones POST del mismo
    // sitio. Una configuración que solo acepte una lista blanca deja fuera al
    // propio cliente y rompe el inicio de sesión en producción — pasó, y por
    // eso existe esta comprobación.
    const mismoOrigen = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Origin: BASE },
      body: JSON.stringify({ username, password }),
    });
    check(
      'Una petición del mismo origen no la bloquea CORS',
      mismoOrigen.status === 200,
      `status ${mismoOrigen.status}`,
    );

    const ajeno = await fetch(`${BASE}/api/health`, {
      headers: { Origin: 'https://sitio-que-no-deberia-poder.example' },
    });
    check(
      'Un origen desconocido no recibe la cabecera que autoriza la respuesta',
      ajeno.headers.get('access-control-allow-origin') === null,
      `cabecera: ${ajeno.headers.get('access-control-allow-origin') ?? 'ausente'}`,
    );

    // ── Manipulación de tokens ───────────────────────────────────────────
    //
    // Un JWT es texto firmado que viaja por el cliente: hay que asumir que el
    // atacante lo lee y lo modifica a voluntad. Estas comprobaciones fijan que
    // ninguna alteración cuele.

    const jwtLib = (await import('jsonwebtoken')).default;
    const secret = process.env.JWT_SECRET ?? 'clave-solo-para-desarrollo-no-usar-en-produccion';

    const withToken = (t: string) => ({ headers: { Authorization: `Bearer ${t}` } });

    const forged = jwtLib.sign({ userId: crypto.randomUUID(), username: 'falso' }, 'otro-secreto');
    const forgedRes = await fetch(`${BASE}/api/tasks`, withToken(forged));
    check(
      'Token firmado con otro secreto -> 401',
      forgedRes.status === 401,
      `status ${forgedRes.status}`,
    );

    const expired = jwtLib.sign({ userId: crypto.randomUUID(), username: 'x' }, secret, {
      expiresIn: '-1h',
    });
    const expiredRes = await fetch(`${BASE}/api/tasks`, withToken(expired));
    check('Token caducado -> 401', expiredRes.status === 401, `status ${expiredRes.status}`);

    // Ataque "alg: none": se quita la firma y se declara que no hay algoritmo,
    // esperando que el verificador acepte el contenido sin comprobar nada.
    const b64 = (o: unknown) => Buffer.from(JSON.stringify(o)).toString('base64url');
    const algNone = `${b64({ alg: 'none', typ: 'JWT' })}.${b64({ userId: crypto.randomUUID(), username: 'x' })}.`;
    const algNoneRes = await fetch(`${BASE}/api/tasks`, withToken(algNone));
    check('Token sin firmar con alg:none -> 401', algNoneRes.status === 401, `status ${algNoneRes.status}`);

    const noSub = jwtLib.sign({ username: 'sin-id' }, secret);
    const noSubRes = await fetch(`${BASE}/api/tasks`, withToken(noSub));
    check(
      'Token válido pero sin userId -> 401',
      noSubRes.status === 401,
      `status ${noSubRes.status}`,
    );

    // Firma correcta y userId con formato de UUID, pero que no existe en la
    // base de datos: no debe devolver datos de nadie ni reventar.
    // Con typ:'access' a propósito: el objetivo es que el token SEA válido y
    // llegue al repositorio, para comprobar que un usuario inexistente no
    // devuelve datos ajenos. Sin el claim lo pararía antes el middleware y el
    // test no probaría lo que dice probar.
    const ghost = jwtLib.sign(
      { userId: crypto.randomUUID(), username: 'fantasma', typ: 'access' },
      secret,
    );
    const ghostRes = await fetch(`${BASE}/api/tasks`, withToken(ghost));
    const ghostBody = (await ghostRes.json()) as Envelope<unknown[]>;
    check(
      'Token de un usuario inexistente no devuelve datos ajenos',
      ghostRes.status === 200 && Array.isArray(ghostBody.data) && ghostBody.data.length === 0,
      `status ${ghostRes.status}`,
    );

    const malformed = await fetch(`${BASE}/api/tasks`, withToken('esto.no.es-un-jwt'));
    check('Token con formato inválido -> 401', malformed.status === 401, `status ${malformed.status}`);

    // ── Regresión de inyección SQL ───────────────────────────────────────
    //
    // Estas cargas romperían la consulta si algún valor se concatenara en el
    // SQL en lugar de viajar como parámetro. Deben tratarse como texto normal.

    const payloads = [
      "'; DROP TABLE tasks; --",
      "' OR '1'='1",
      "\\'; DELETE FROM users WHERE '1'='1",
      '%',       // comodín de LIKE: no debe ampliar la búsqueda
      '_',       // comodín de un carácter en LIKE
    ];

    let injectionOk = true;
    let injectionDetail = '';
    for (const payload of payloads) {
      const res = await fetch(`${BASE}/api/tasks?search=${encodeURIComponent(payload)}`, {
        headers: auth,
      });
      const body = (await res.json()) as Envelope<unknown[]>;
      // Se espera 200 con cero resultados: la carga se busca como texto y no
      // coincide con ninguna tarea. Un 500 delataría SQL roto.
      if (res.status !== 200 || !Array.isArray(body.data) || body.data.length !== 0) {
        injectionOk = false;
        injectionDetail = `"${payload}" -> ${res.status}, ${(body.data as unknown[])?.length} resultado(s)`;
        break;
      }
    }
    check(
      'Cargas de inyección SQL en el filtro de búsqueda se tratan como texto',
      injectionOk,
      injectionDetail || `${payloads.length} cargas probadas`,
    );

    // Los comodines de LIKE deben buscarse literalmente. Se crea una tarea que
    // sí los contiene para comprobar que la búsqueda los encuentra a ellos y
    // no a todo lo demás.
    await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: 'Descuento del 50% aplicado' }),
    });
    const literal = await fetch(`${BASE}/api/tasks?search=${encodeURIComponent('50%')}`, {
      headers: auth,
    });
    const literalBody = (await literal.json()) as Envelope<{ title: string }[]>;
    check(
      'Buscar "50%" encuentra ese texto y no todas las tareas',
      literalBody.data?.length === 1 && literalBody.data[0].title.includes('50%'),
      `${literalBody.data?.length} resultado(s)`,
    );

    // La tabla debe seguir existiendo después de todo lo anterior.
    const tablaViva = await query<{ count: number }>('SELECT COUNT(*) AS count FROM tasks');
    check(
      'La tabla tasks sigue intacta tras las cargas de inyección',
      typeof tablaViva[0].count === 'number',
      `${tablaViva[0].count} tareas`,
    );

    // Un título con comillas y punto y coma debe guardarse tal cual.
    const tituloRaro = "Tarea '; DROP TABLE tasks; --";
    const rareRes = await fetch(`${BASE}/api/tasks`, {
      method: 'POST',
      headers: auth,
      body: JSON.stringify({ title: tituloRaro }),
    });
    const rareBody = (await rareRes.json()) as Envelope<{ id: string; title: string }>;
    check(
      'Un título con sintaxis SQL se almacena literalmente',
      rareRes.status === 201 && rareBody.data?.title === tituloRaro,
      `guardado como: ${rareBody.data?.title}`,
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
      accessToken: string;
      user: { id: string; role: string };
    }>;
    check(
      'El administrador de la semilla existe y entra con rol admin',
      adminLogin.status === 200 && adminBody.data?.user?.role === 'admin',
      `status ${adminLogin.status}, rol ${adminBody.data?.user?.role}`,
    );
    const adminAuth = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${adminBody.data?.accessToken ?? ''}`,
    };
    const adminId = adminBody.data?.user?.id ?? '';

    // El identificador mal formado se comprueba AQUÍ y no antes, con el token
    // de administrador de verdad.
    //
    // La primera versión de este test usaba un usuario normal y afirmaba que
    // la respuesta "no era 500". Pasaba, pero por el motivo equivocado:
    // `requireAdmin` devolvía 403 antes de que la petición llegara siquiera al
    // validador de UUID, así que no comprobaba nada de lo que decía comprobar.
    const adminMalFormado = await fetch(`${BASE}/api/admin/users/no-soy-un-uuid`, {
      method: 'DELETE',
      headers: adminAuth,
    });
    check(
      'DELETE /api/admin/users/<no-uuid> -> 400, nunca 500',
      adminMalFormado.status === 400,
      `status ${adminMalFormado.status}`,
    );

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

    // ── Cambio de contraseña ─────────────────────────────────────────────
    //
    // Es la ruta que más cosas tiene que hacer bien a la vez: comprobar la
    // contraseña actual, aplicar la política a la nueva, revocar todas las
    // sesiones y abrir una limpia. Aquí se comprueba contra PostgreSQL real,
    // porque varias de esas garantías solo se ven mirando las filas.

    const cambUser = `cambio-${crypto.randomUUID().slice(0, 8)}`;
    const cambActual = password;
    const cambNueva = 'Café con leche y 2 tostadas!';

    await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: cambUser, password: cambActual }),
    });

    // Tres sesiones, como si fueran tres dispositivos.
    const cs1 = await entrar(cambUser, cambActual);
    const cs2 = await entrar(cambUser, cambActual);
    const cs3 = await entrar(cambUser, cambActual);
    const cr1 = cookieDeRespuesta(cs1);
    const cr2 = cookieDeRespuesta(cs2);
    const cAcceso = ((await cs3.json()) as Envelope<{ accessToken: string }>).data?.accessToken;

    const cambiar = (cuerpo: unknown, token?: string) =>
      fetch(`${BASE}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(cuerpo),
      });

    const sinToken = await cambiar({ actual: cambActual, nueva: cambNueva });
    check(
      'Cambiar la contraseña exige estar autenticado',
      sinToken.status === 401,
      `status ${sinToken.status}`,
    );

    const actualMal = await cambiar({ actual: 'no-es-la-suya', nueva: cambNueva }, cAcceso);
    check(
      'Con la contraseña actual equivocada -> 401',
      actualMal.status === 401,
      `status ${actualMal.status}`,
    );

    // Y, sobre todo, que ese intento fallido no cambió nada.
    const siguePudiendoEntrar = await entrar(cambUser, cambActual);
    check(
      'Un intento con la actual equivocada NO cambia la contraseña',
      siguePudiendoEntrar.status === 200,
      `status ${siguePudiendoEntrar.status}`,
    );

    const nuevaDebil = await cambiar({ actual: cambActual, nueva: 'corta' }, cAcceso);
    check(
      'La contraseña nueva pasa la política -> 400 si no',
      nuevaDebil.status === 400,
      `status ${nuevaDebil.status}`,
    );

    const nuevaIgual = await cambiar({ actual: cambActual, nueva: cambActual }, cAcceso);
    check(
      'Repetir la contraseña actual -> 400',
      nuevaIgual.status === 400,
      `status ${nuevaIgual.status}`,
    );

    const cambiada = await cambiar({ actual: cambActual, nueva: cambNueva }, cAcceso);
    check(
      'POST /api/auth/change-password -> 200',
      cambiada.status === 200,
      `status ${cambiada.status}`,
    );

    // El refresco sale por cookie, nunca en el cuerpo. Es la cuarta ruta que
    // emite credenciales y la más fácil de escribir mal.
    const cuerpoCambio = await cambiada.clone().text();
    check(
      'El cambio no filtra el token de refresco en el cuerpo',
      !cuerpoCambio.includes('refreshToken'),
      cuerpoCambio.includes('refreshToken') ? 'APARECE en el cuerpo' : 'solo en la cookie',
    );
    check(
      'El cambio entrega la cookie de refresco nueva',
      cookieDeRespuesta(cambiada) !== null,
      cookieDeRespuesta(cambiada) !== null ? 'Set-Cookie presente' : 'sin Set-Cookie',
    );

    // Las otras dos sesiones quedan fuera.
    const otras = [await renovar(cr1), await renovar(cr2)];
    check(
      'Al cambiar la contraseña, las demás sesiones dejan de renovar',
      otras.every((r) => r.status === 401),
      otras.map((r) => r.status).join(', '),
    );

    // Y quedan marcadas con su propio motivo, que es lo que permite
    // distinguir un cambio de contraseña de un cierre de sesión normal.
    const motivosCambio = await query<{ count: number }>(
      `SELECT COUNT(*) AS count FROM refresh_sessions s
         JOIN users u ON u.id = s.user_id
        WHERE u.username = $1 AND s.revoked_reason = 'password-changed'`,
      [cambUser],
    );
    check(
      "Las sesiones revocadas llevan el motivo 'password-changed'",
      motivosCambio[0].count > 0,
      `${motivosCambio[0].count} filas`,
    );

    const conVieja = await entrar(cambUser, cambActual);
    check(
      'La contraseña vieja ya no sirve para entrar',
      conVieja.status === 401,
      `status ${conVieja.status}`,
    );

    const conNueva = await entrar(cambUser, cambNueva);
    check(
      'La contraseña nueva sí sirve para entrar',
      conNueva.status === 200,
      `status ${conNueva.status}`,
    );

    // El hash cambió de verdad en la base de datos, y sigue siendo un hash.
    const hashTras = await query<{ password_hash: string }>(
      'SELECT password_hash FROM users WHERE username = $1',
      [cambUser],
    );
    check(
      'La contraseña se guarda hasheada, nunca en claro',
      !hashTras[0].password_hash.includes(cambNueva) &&
        hashTras[0].password_hash.startsWith('$2'),
      // Solo el prefijo del algoritmo y el coste: identifica bcrypt sin sacar
      // material del hash al registro.
      hashTras[0].password_hash.slice(0, 7),
    );

    // ── Límite por cuenta ────────────────────────────────────────────────
    //
    // Va al final a propósito: agota la cuota de una cuenta concreta, y
    // hacerlo antes contaminaría cualquier prueba posterior con ese usuario.
    //
    // La suite sube AUTH_RATE_LIMIT a 1000, así que el limitador por IP no
    // interfiere y lo que se mide aquí es únicamente el contador por cuenta,
    // que usa su valor por defecto.

    const victima = `limite-${crypto.randomUUID().slice(0, 8)}`;
    const atacada = `otra-${crypto.randomUUID().slice(0, 8)}`;
    for (const u of [victima, atacada]) {
      await fetch(`${BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password }),
      });
    }

    // Veintiuno: uno más que el límite que fija esta suite arriba.
    let ultimo = 0;
    for (let i = 0; i < 21; i++) {
      const r = await entrar(victima, 'contraseña-que-no-es-2026!');
      ultimo = r.status;
    }
    check(
      'Tras agotar los intentos de una cuenta -> 429',
      ultimo === 429,
      `status ${ultimo}`,
    );

    // La prueba de que la clave es la CUENTA y no la dirección: desde esta
    // misma IP, que acaba de ser bloqueada para `victima`, otra cuenta sigue
    // respondiendo con normalidad. Si el contador fuera por IP, esto también
    // daría 429 y el limitador nuevo no aportaría nada sobre el que ya había.
    const otraCuenta = await entrar(atacada, 'tampoco-es-esta-2026!');
    check(
      'El bloqueo es por cuenta, no por dirección: otra cuenta sigue respondiendo',
      otraCuenta.status === 401,
      `status ${otraCuenta.status}`,
    );

    // Y alternar mayúsculas no abre un cubo nuevo: la clave se normaliza igual
    // que el índice único de la base de datos.
    const conMayusculas = await entrar(victima.toUpperCase(), 'da-igual-2026!');
    check(
      'Alternar mayúsculas no esquiva el límite por cuenta',
      conMayusculas.status === 429,
      `status ${conMayusculas.status}`,
    );

    // La cuenta bloqueada tampoco entra con la contraseña BUENA mientras dure
    // la ventana. Es el precio del mecanismo, y conviene que esté fijado por un
    // test para que nadie lo descubra por sorpresa en producción.
    const conLaBuena = await entrar(victima, password);
    check(
      'Mientras dura el bloqueo, ni siquiera la contraseña correcta entra',
      conLaBuena.status === 429,
      `status ${conLaBuena.status}`,
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
