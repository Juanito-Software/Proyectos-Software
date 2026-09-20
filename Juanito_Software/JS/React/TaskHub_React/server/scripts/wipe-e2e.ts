import { query, closePool } from '../src/config/db.js';

/**
 * Elimina los usuarios `e2e-*` que dejan los tests end-to-end.
 *
 * Los tests de navegador crean un usuario con un prefijo `e2e-` y un sufijo
 * aleatorio por ejecución. Cuando el .env apuntaba a la base de datos
 * desplegada, una tanda de ejecuciones dejaba decenas de estos usuarios como
 * basura: no rompían nada (el borrado llega al usuario de turno), pero ensuciaban
 * la base de datos real.
 *
 * Este script borra SOLO ese prefijo: sus tareas y sesiones de refresco se van
 * solas por el borrado en cascada. Un usuario normal nunca empieza por `e2e-`,
 * así que una cuenta legítima no puede resultar afectada aunque el script se
 * ejecute contra la base de datos en uso.
 */
const host = new URL(process.env.DATABASE_URL ?? '').host;
console.log(`Limpiando usuarios e2e-* en ${host} …`);

const eliminados = await query<{ id: string }>(
  `DELETE FROM users WHERE username LIKE 'e2e-%' RETURNING id`,
);

console.log(`Eliminados ${eliminados.length} usuario(s) e2e-* (sus tareas y sesiones, en cascada).`);
await closePool();