import bcrypt from 'bcrypt';
import { query } from '../../config/db.js';
import { User, PublicUser, AdminUserView, UserRole } from './users.types.js';

/**
 * Coste de bcrypt.
 *
 * Cada ronda dobla el trabajo. Medido en esta máquina: 10 rondas son 48 ms por
 * hash, 11 son 94 y 12 son 189. Se elige **12**, que es la recomendación
 * habitual desde hace años y sigue siendo cómodo: doscientos milisegundos solo
 * se pagan al entrar o al registrarse, nunca en el resto de peticiones.
 *
 * El salto de 10 a 12 no era urgente aquí, y conviene decir por qué: la
 * política obliga a quince caracteres con mayúscula, número y símbolo, y
 * rechaza los patrones previsibles, así que ya no hay contraseñas que un
 * diccionario vaya a encontrar por muchos hashes por segundo que calcule.
 * Subirlo es cinturón sobre tirantes, y cuesta poco.
 *
 * **Los hashes antiguos siguen funcionando.** El coste va codificado dentro del
 * propio hash (`$2b$10$…`), así que `bcrypt.compare` usa el que tenga cada uno.
 * Quien se registró con 10 rondas entra igual; su hash pasará a 12 la próxima
 * vez que cambie la contraseña — cuando exista esa funcionalidad.
 */
const SALT_ROUNDS = 12;

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
    const rows = await query<Omit<UserRow, 'password_hash'> & { task_count: number }>(
      // El hash NO se selecciona. El mapeo de abajo lo descartaba igualmente,
      // pero traerlo desde la base de datos sin necesitarlo es una fuga
      // esperando a que alguien añada un `...row` al objeto de salida.
      `SELECT u.id, u.username, u.role, u.created_at,
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

  /**
   * Sustituye el hash de la contraseña.
   *
   * Recibe la contraseña en claro y hashea aquí, igual que `create`, para que
   * bcrypt viva en un solo sitio: si mañana se sube el coste o se cambia de
   * algoritmo, se toca una línea y no tres.
   *
   * Devuelve si encontró la fila. Un `false` significa que el usuario ya no
   * existe —lo borraron mientras cambiaba la contraseña—, y quien llama debe
   * distinguirlo de un cambio correcto en lugar de dar por hecho que fue bien.
   */
  async updatePassword(id: string, password: string): Promise<boolean> {
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);
    const rows = await query<{ id: string }>(
      'UPDATE users SET password_hash = $1 WHERE id = $2 RETURNING id',
      [passwordHash, id],
    );
    return rows.length > 0;
  },

  /** Las tareas del usuario se van solas por el ON DELETE CASCADE. */
  async deleteById(id: string): Promise<boolean> {
    const rows = await query<{ id: string }>('DELETE FROM users WHERE id = $1 RETURNING id', [id]);
    return rows.length > 0;
  },
};
