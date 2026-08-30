import { pool, closePool } from './src/config/db.js';
const r = await pool.query(`SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'verify_%'`);
console.log('  esquemas verify_ huérfanos:', r.rows.length);
const u = await pool.query(`SELECT COUNT(*) c FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('users','tasks')`);
console.log('  tablas users/tasks en el esquema public:', u.rows[0].c);
if (Number(u.rows[0].c) > 0) {
  const a = await pool.query(`SELECT role, COUNT(*) c FROM public.users GROUP BY role`);
  console.log('  usuarios en public:', JSON.stringify(a.rows));
}
await closePool();
