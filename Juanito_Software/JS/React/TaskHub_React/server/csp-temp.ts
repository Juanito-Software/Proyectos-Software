process.env.DB_SCHEMA = 'csptmp';
const { pool, initSchema, closePool } = await import('./src/config/db.js');
await pool.query('CREATE SCHEMA IF NOT EXISTS csptmp');
await initSchema();
const { createApp } = await import('./src/app.js');
const s = createApp().listen(4111);
const res = await fetch('http://localhost:4111/playground');
const csp = res.headers.get('content-security-policy') ?? '';
console.log('CSP completa:\n  ' + csp.split(';').join(';\n  '));
console.log('\n¿bloquea los onclick?  script-src-attr:',
  /script-src-attr\s+'none'/.test(csp) ? "SÍ ('none') ← ese es el fallo" : 'no');
s.close();
await pool.query('DROP SCHEMA IF EXISTS csptmp CASCADE');
await closePool();
