import pg from 'pg';
import { env } from './env.js';
import { SCHEMA_SQL } from './schema.js';

/**
 * Postgres devuelve NUMERIC como cadena para no perder precisión. Los conteos
 * de COUNT() vienen como BIGINT (OID 20) y llegarían como "3" en vez de 3, así
 * que se convierten a número aquí, una sola vez, en lugar de recordar hacerlo
 * en cada consulta.
 */
pg.types.setTypeParser(20, (value: string) => Number(value));

/**
 * La suite de verificación crea un esquema temporal y pasa su nombre por
 * DB_SCHEMA. Fijar el search_path en las opciones de conexión hace que todas
 * las consultas apunten ahí sin tocar ni una línea de los repositorios.
 */
const schema = process.env.DB_SCHEMA;

export const pool = new pg.Pool({
  connectionString: env.databaseUrl,
  // Neon y la mayoría de proveedores gestionados exigen TLS. No se desactiva
  // la verificación del certificado: son certificados válidos y aceptar
  // cualquiera dejaría la conexión expuesta a un intermediario.
  ssl: env.databaseUrl.includes('sslmode=require') ? { rejectUnauthorized: true } : undefined,
  ...(schema ? { options: `-c search_path=${schema}` } : {}),
});

/** Atajo para consultas sueltas; devuelve directamente las filas tipadas. */
export async function query<T extends pg.QueryResultRow>(
  text: string,
  params: unknown[] = [],
): Promise<T[]> {
  const result = await pool.query<T>(text, params);
  return result.rows;
}

/** Crea las tablas si no existen. Se llama una vez al arrancar el servidor. */
export async function initSchema(): Promise<void> {
  await pool.query(SCHEMA_SQL);
}

export async function closePool(): Promise<void> {
  await pool.end();
}
