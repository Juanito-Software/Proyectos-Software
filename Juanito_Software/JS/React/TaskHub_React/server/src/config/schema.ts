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
  -- El rol por defecto es 'user' y el registro nunca lo cambia: un
  -- administrador solo puede nacer de la semilla de arranque. Así no existe
  -- ningún camino desde la API pública hacia el rol admin.
  role          TEXT        NOT NULL DEFAULT 'user'
                CHECK (role IN ('user', 'admin')),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Para bases de datos creadas antes de que existiera el rol.
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'user';

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'users_role_check'
  ) THEN
    ALTER TABLE users ADD CONSTRAINT users_role_check
      CHECK (role IN ('user', 'admin'));
  END IF;
END $$;

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

-- ── Sesiones y tokens de refresco ──────────────────────────────────────────
--
-- Cada fila es un token de refresco concreto, no una sesión entera. Al rotar,
-- la fila vieja se marca revocada y nace una nueva con el mismo family_id, así
-- que una sesión es la cadena de filas que comparten familia.
--
-- Esa cadena es lo que permite detectar reutilización: si aparece un token ya
-- rotado, no basta con rechazarlo —el atacante tendría igualmente el siguiente
-- de la cadena—, hay que revocar la familia completa.
--
-- El token NO se guarda: se guarda su SHA-256. Para localizar una sesión basta
-- con hashear lo que llega y buscar, sin necesidad de tener el secreto. Si
-- alguien se lleva un volcado de la tabla, no obtiene tokens utilizables.
-- No lleva sal ni bcrypt a propósito: son 32 bytes aleatorios, no una
-- contraseña, así que no hay diccionario que probar y el hash tiene que ser
-- determinista para poder buscar por él.
CREATE TABLE IF NOT EXISTS refresh_sessions (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  family_id    UUID        NOT NULL,
  user_id      UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash   TEXT        NOT NULL UNIQUE,
  -- Fila de la que salió esta por rotación. Sirve para reconstruir la cadena
  -- al depurar un incidente.
  parent_id    UUID        REFERENCES refresh_sessions(id) ON DELETE SET NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at   TIMESTAMPTZ NOT NULL,
  revoked_at   TIMESTAMPTZ,
  -- Por qué dejó de valer: 'rotated' es el ciclo normal; 'logout', 'logout-all'
  -- y 'reuse-detected' son revocaciones. Distinguirlos importa: un token
  -- 'rotated' que reaparece es sospechoso, uno 'logout' solo está caducado.
  revoked_reason TEXT      CHECK (revoked_reason IN ('rotated', 'logout', 'logout-all', 'reuse-detected'))
);

-- La búsqueda de cada refresco es por hash; el UNIQUE de la columna ya crea el
-- índice, así que aquí solo hacen falta los dos accesos restantes: revocar una
-- familia entera y revocar todas las sesiones de un usuario.
CREATE INDEX IF NOT EXISTS refresh_sessions_family_idx
  ON refresh_sessions (family_id);

CREATE INDEX IF NOT EXISTS refresh_sessions_user_idx
  ON refresh_sessions (user_id);

-- Para la limpieza periódica de filas caducadas.
CREATE INDEX IF NOT EXISTS refresh_sessions_expires_idx
  ON refresh_sessions (expires_at);
`;
