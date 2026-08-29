import { pool } from './src/config/db.js';
const r = await pool.query(`SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'verify_%'`);
console.log(r.rows.length === 0 ? 'ninguno: la suite limpia bien' : `quedan ${r.rows.length}: ${r.rows.map((x:any)=>x.schema_name).join(', ')}`);
await pool.end();
