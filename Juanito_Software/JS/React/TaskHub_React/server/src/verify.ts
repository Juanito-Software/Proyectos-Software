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
const ADMIN_PASS = 'clave larga del administrador de pruebas';
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
    const password = 'frase de paso para verificar';

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

    // ── Política de contraseñas (NIST SP 800-63B Rev 4) ──────────────────

    const registrar = (u: string, p: string) =>
      fetch(`${BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p }),
      });

    const nuevo = () => `pol-${crypto.randomUUID().slice(0, 8)}`;

    const corta = await registrar(nuevo(), 'melon y sandia'); // 14
    check(
      'Registro con contraseña de 14 caracteres -> 400',
      corta.status === 400,
      `status ${corta.status}`,
    );

    // El caso que define la política: larga, sin mayúsculas, sin números y
    // sin símbolos. Cualquier sistema con reglas de composición la rechazaría.
    const fraseUser = nuevo();
    const frase = await registrar(fraseUser, 'caballo correcto grapa pila');
    check(
      'Registro con frase larga sin mayúsculas, números ni símbolos -> 201',
      frase.status === 201,
      `status ${frase.status}`,
    );

    // Y debe poder entrar después con esa misma contraseña.
    const fraseLogin = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: fraseUser, password: 'caballo correcto grapa pila' }),
    });
    check(
      'Se puede iniciar sesión con la frase de paso',
      fraseLogin.status === 200,
      `status ${fraseLogin.status}`,
    );

    const comun = await registrar(nuevo(), 'passwordpassword');
    check(
      'Registro con contraseña de la lista de bloqueo -> 400',
      comun.status === 400,
      `status ${comun.status}`,
    );

    const conNombre = await registrar('pedrito', 'pedrito y su contraseña');
    check(
      'Registro con la contraseña conteniendo el usuario -> 400',
      conNombre.status === 400,
      `status ${conNombre.status}`,
    );

    const excesiva = await registrar(nuevo(), 'x'.repeat(73));
    check(
      'Registro con más de 72 caracteres -> 400, no se recorta en silencio',
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

    // Compatibilidad: una cuenta con una contraseña que hoy no pasaría la
    // política debe seguir pudiendo iniciar sesión. Se simula insertando el
    // hash directamente, como haría una cuenta creada antes del cambio.
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

    // El contrato del registro no incluye la confirmación: es del formulario.
    const conConfirmacion = await fetch(`${BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: nuevo(),
        password: 'otra frase de paso valida',
        passwordConfirmation: 'algo completamente distinto',
      }),
    });
    check(
      'La API ignora passwordConfirmation: la comparación es del formulario',
      conConfirmacion.status === 201,
      `status ${conConfirmacion.status}`,
    );

    // ── Cabeceras de seguridad ───────────────────────────────────────────

    const cabeceras = await fetch(`${BASE}/playground`);
    const csp = cabeceras.headers.get('content-security-policy') ?? '';

    check(
      'La CSP está presente y restringe el origen por defecto',
      csp.includes("default-src 'self'"),
      csp ? 'presente' : 'AUSENTE',
    );

    // El playground engancha sus botones con atributos onclick. Con
    // script-src-attr 'none' —el valor por defecto de helmet— la página carga
    // pero ningún botón responde, y no hay error visible salvo en la consola
    // del navegador. Pasó, y ninguna de las otras comprobaciones lo detectó
    // porque todas hablan con la API, no con la interfaz.
    check(
      'La CSP no bloquea los manejadores onclick del playground',
      !/script-src-attr\s+'none'/.test(csp),
      /script-src-attr\s+'none'/.test(csp) ? "script-src-attr 'none' los bloquea" : 'permitidos',
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
    const ghost = jwtLib.sign({ userId: crypto.randomUUID(), username: 'fantasma' }, secret);
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
