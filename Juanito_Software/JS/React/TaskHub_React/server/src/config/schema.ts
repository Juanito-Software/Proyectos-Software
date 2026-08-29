/**
 * Esquema de la base de datos.
 *
 * Va como cadena en TypeScript y no como fichero .sql para que el build no
 * tenga que copiarlo a dist/: al compilar queda dentro del JavaScript
 * generado y no hay riesgo de desplegar sin él.
 *
 * Todo el script es idempotente (IF NOT EXISTS), así que se puede ejecutar en
 * cada arranque sin comprobar antes si las tablas ya están.
 */
export const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username      TEXT        NOT NULL,
  password_hash TEXT        NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- El nombre de usuario es único sin distinguir mayúsculas. Se hace con un
-- índice sobre LOWER(username) en lugar de un UNIQUE normal porque el registro
-- ya comparaba en minúsculas: sin esto, "Juan" y "juan" serían dos cuentas.
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_idx
  ON users (LOWER(username));

CREATE TABLE IF NOT EXISTS tasks (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT        NOT NULL,
  description TEXT        NOT NULL DEFAULT '',
  status      TEXT        NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending', 'in-progress', 'completed')),
  priority    TEXT        NOT NULL DEFAULT 'medium'
              CHECK (priority IN ('low', 'medium', 'high')),
  user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Casi todas las consultas filtran por usuario, así que el índice cubre el
-- caso normal; el orden por fecha descendente evita ordenar en memoria.
CREATE INDEX IF NOT EXISTS tasks_user_created_idx
  ON tasks (user_id, created_at DESC);

-- La regla "no puedes tener dos tareas con el mismo título" pasa a estar
-- garantizada por la base de datos. El servicio la sigue comprobando antes
-- para devolver un 409 con mensaje claro, pero este índice es lo que la hace
-- infalible: con ficheros JSON, dos peticiones simultáneas podían colarse
-- entre la comprobación y la escritura.
CREATE UNIQUE INDEX IF NOT EXISTS tasks_user_title_lower_idx
  ON tasks (user_id, LOWER(TRIM(title)));
`;
