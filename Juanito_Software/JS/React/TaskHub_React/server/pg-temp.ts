process.env.DB_SCHEMA = 'pgcheck';
const { pool, initSchema, closePool } = await import('./src/config/db.js');
await pool.query('CREATE SCHEMA IF NOT EXISTS pgcheck');
await initSchema();
const { createApp } = await import('./src/app.js');
const s = createApp().listen(4102);
const html = await (await fetch('http://localhost:4102/playground')).text();
for (const t of ['/api/admin/users', '/api/admin/stats', 'deleteUserPrompt', "role === 'admin'", 'admin-panel']) {
  console.log(`  ${html.includes(t) ? 'OK ' : 'FALTA'}  ${t}`);
}
console.log('  tamaño:', html.length, 'bytes');
s.close();
await pool.query('DROP SCHEMA IF EXISTS pgcheck CASCADE');
await closePool();
