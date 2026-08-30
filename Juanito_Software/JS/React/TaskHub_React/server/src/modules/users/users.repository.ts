import bcrypt from 'bcrypt';
import { query } from '../../config/db.js';
import { User, PublicUser, AdminUserView, UserRole } from './users.types.js';

const SALT_ROUNDS = 10;

/**
 * Fila tal y como la devuelve Postgres: columnas en snake_case y fechas como
 * objetos Date. El resto de la aplicación trabaja con camelCase y fechas en
 * texto ISO, así que la traducción se hace aquí y no sale de este fichero.
 */
interface UserRow {
  id: string;
  username: string;
  password_hash: string;
  role: UserRole;
  created_at: Date;
}

const COLUMNS = 'id, username, password_hash, role, created_at';

function toUser(row: UserRow): User {
  return {
    id: row.id,
    username: row.username,
    passwordHash: row.password_hash,
    role: row.role,
    createdAt: row.created_at.toISOString(),
  };
}

function toPublic(user: User): PublicUser {
  return { id: user.id, username: user.username, role: user.role };
}

export const usersRepository = {
  toPublic,

  async findByUsername(username: string): Promise<User | null> {
    // Todos los valores viajan como parámetros ($1), nunca concatenados en la
    // cadena SQL: es lo que hace imposible la inyección.
    const rows = await query<UserRow>(
      `SELECT ${COLUMNS} FROM users WHERE LOWER(username) = LOWER($1)`,
      [username],
    );
    return rows[0] ? toUser(rows[0]) : null;
  },

  async findById(id: string): Promise<User | null> {
    const rows = await query<UserRow>(`SELECT ${COLUMNS} FROM users WHERE id = $1`, [id]);
    return rows[0] ? toUser(rows[0]) : null;
  },

  async create(username: string, password: string): Promise<PublicUser | null> {
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    // El rol no se acepta como parámetro: cae siempre al 'user' por defecto de
    // la tabla. Aunque alguien mande {"role":"admin"} en el registro, no hay
    // ninguna ruta desde aquí hasta ese valor.
    //
    // ON CONFLICT DO NOTHING resuelve el duplicado en la propia inserción: si
    // el nombre ya existe no devuelve ninguna fila y se responde null, sin
    // necesidad de un SELECT previo que dejaría una ventana para que dos
    // registros simultáneos con el mismo nombre pasaran los dos.
    const rows = await query<UserRow>(
      `INSERT INTO users (username, password_hash)
       VALUES ($1, $2)
       ON CONFLICT (LOWER(username)) DO NOTHING
       RETURNING ${COLUMNS}`,
      [username.trim(), passwordHash],
    );

    return rows[0] ? toPublic(toUser(rows[0])) : null;
  },

  async verifyPassword(user: User, password: string): Promise<boolean> {
    return bcrypt.compare(password, user.passwordHash);
  },

  // ── Administración ───────────────────────────────────────────────────────

  /**
   * Crea el usuario administrador, o lo promueve si ya existía con ese nombre.
   * Solo la llama la semilla de arranque, nunca una petición HTTP.
   */
  async upsertAdmin(username: string, password: string): Promise<PublicUser> {
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);
    const rows = await query<UserRow>(
      `INSERT INTO users (username, password_hash, role)
       VALUES ($1, $2, 'admin')
       ON CONFLICT (LOWER(username))
       DO UPDATE SET role = 'admin', password_hash = EXCLUDED.password_hash
       RETURNING ${COLUMNS}`,
      [username.trim(), passwordHash],
    );
    return toPublic(toUser(rows[0]));
  },

  /** Listado para el panel, con el número de tareas de cada usuario. */
  async listAll(): Promise<AdminUserView[]> {
    const rows = await query<UserRow & { task_count: number }>(
      `SELECT u.id, u.username, u.role, u.created_at, u.password_hash,
              COUNT(t.id) AS task_count
         FROM users u
         LEFT JOIN tasks t ON t.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at ASC`,
    );
    return rows.map((row) => ({
      id: row.id,
      username: row.username,
      role: row.role,
      createdAt: row.created_at.toISOString(),
      taskCount: row.task_count,
    }));
  },

  async countByRole(role: UserRole): Promise<number> {
    const rows = await query<{ count: number }>(
      'SELECT COUNT(*) AS count FROM users WHERE role = $1',
      [role],
    );
    return rows[0].count;
  },

  /** Las tareas del usuario se van solas por el ON DELETE CASCADE. */
  async deleteById(id: string): Promise<boolean> {
    const rows = await query<{ id: string }>('DELETE FROM users WHERE id = $1 RETURNING id', [id]);
    return rows.length > 0;
  },
};
