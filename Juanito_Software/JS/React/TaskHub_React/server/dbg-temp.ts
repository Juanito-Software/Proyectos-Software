import { pool, initSchema } from './src/config/db.js';
await initSchema();
await pool.query(`INSERT INTO users (id, username, password_hash)
  VALUES ('22222222-2222-2222-2222-222222222222','norm','x') ON CONFLICT DO NOTHING`);
// Primero el título normalizado, después SOLO la variante con ruido.
await pool.query(
  'INSERT INTO tasks (title, status, priority, user_id) VALUES ($1,$2,$3,$4)',
  ['comprar pan', 'pending', 'medium', '22222222-2222-2222-2222-222222222222'],
);
try {
  await pool.query(
    'INSERT INTO tasks (title, status, priority, user_id) VALUES ($1,$2,$3,$4)',
    ['  COMPRAR PAN  ', 'pending', 'medium', '22222222-2222-2222-2222-222222222222'],
  );
  console.log('FALLO: la variante con mayúsculas y espacios se coló');
} catch (e: any) {
  console.log('variante "  COMPRAR PAN  " rechazada. code:', e.code, '| índice:', e.constraint);
}
await pool.end();
