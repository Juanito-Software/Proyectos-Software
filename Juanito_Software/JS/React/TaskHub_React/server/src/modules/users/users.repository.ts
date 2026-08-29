import bcrypt from 'bcrypt';
import { query } from '../../config/db.js';
import { User, PublicUser } from './users.types.js';

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
  created_at: Date;
}

function toUser(row: UserRow): User {
  return {
    id: row.id,
    username: row.username,
    passwordHash: row.password_hash,
    createdAt: row.created_at.toISOString(),
  };
}

function toPublic(user: User): PublicUser {
  return { id: user.id, username: user.username };
}

export const usersRepository = {
  toPublic,

  async findByUsername(username: string): Promise<User | null> {
    // Todos los valores viajan como parámetros ($1), nunca concatenados en la
    // cadena SQL: es lo que hace imposible la inyección.
    const rows = await query<UserRow>(
      'SELECT id, username, password_hash, created_at FROM users WHERE LOWER(username) = LOWER($1)',
      [username],
    );
    return rows[0] ? toUser(rows[0]) : null;
  },

  async findById(id: string): Promise<User | null> {
    const rows = await query<UserRow>(
      'SELECT id, username, password_hash, created_at FROM users WHERE id = $1',
      [id],
    );
    return rows[0] ? toUser(rows[0]) : null;
  },

  async create(username: string, password: string): Promise<PublicUser | null> {
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    // ON CONFLICT DO NOTHING resuelve el duplicado en la propia inserción: si
    // el nombre ya existe no devuelve ninguna fila y se responde null, sin
    // necesidad de un SELECT previo que dejaría una ventana para que dos
    // registros simultáneos con el mismo nombre pasaran los dos.
    const rows = await query<UserRow>(
      `INSERT INTO users (username, password_hash)
       VALUES ($1, $2)
       ON CONFLICT (LOWER(username)) DO NOTHING
       RETURNING id, username, password_hash, created_at`,
      [username.trim(), passwordHash],
    );

    return rows[0] ? toPublic(toUser(rows[0])) : null;
  },

  async verifyPassword(user: User, password: string): Promise<boolean> {
    return bcrypt.compare(password, user.passwordHash);
  },
};
