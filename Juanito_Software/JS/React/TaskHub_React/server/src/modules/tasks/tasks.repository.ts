/**
 * Acceso a la tabla `tasks`. Único sitio con SQL de tareas.
 *
 * Todas las consultas filtran por `user_id` en el propio `WHERE`: para este
 * repositorio, una tarea de otro usuario simplemente no existe.
 */
import { query } from '../../config/db.js';
import { Task, TaskDto, TaskFilters, TaskStatus, TaskPriority } from './tasks.types.js';

/**
 * Fila tal y como la devuelve Postgres: snake_case y fechas como Date. La
 * traducción a la forma que usa el resto de la aplicación (camelCase, fechas
 * en texto ISO) vive solo aquí.
 */
interface TaskRow {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  user_id: string;
  created_at: Date;
  updated_at: Date;
}

/** Columnas que se leen siempre, en el orden de `TaskRow`. */
const COLUMNS = 'id, title, description, status, priority, user_id, created_at, updated_at';

/**
 * Neutraliza los comodines de LIKE en el texto que escribe el usuario.
 *
 * En un patrón de LIKE, `%` significa "cualquier secuencia" y `_` "cualquier
 * carácter". Alguien que busque "100%" espera encontrar ese texto, no todas
 * las tareas. La barra invertida se escapa primero, porque es el carácter que
 * escapa a los otros dos y hacerlo al revés rompería el resultado.
 *
 * @param value texto tal como lo escribió el usuario
 * @returns texto con `\`, `%` y `_` escapados
 */
export function escapeLikePattern(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/%/g, '\\%').replace(/_/g, '\\_');
}

/** Convierte una fila de Postgres en el `Task` de la aplicación. */
function toTask(row: TaskRow): Task {
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    status: row.status,
    priority: row.priority,
    userId: row.user_id,
    createdAt: row.created_at.toISOString(),
    updatedAt: row.updated_at.toISOString(),
  };
}

/**
 * `completed` es un campo calculado, no una columna. El cliente React lo sigue
 * usando para su checkbox, así que se deriva de `status` al salir; la base de
 * datos solo guarda el estado, que es la fuente de verdad.
 */
export function toDto(task: Task): TaskDto {
  return { ...task, completed: task.status === 'completed' };
}

/** Consultas SQL sobre `tasks`, siempre acotadas al usuario. */
export const tasksRepository = {
  /**
   * @param userId  dueño
   * @param filters estado, prioridad y texto (en título o descripción, sin
   *                distinguir mayúsculas); todos opcionales y acumulativos
   * @returns tareas ordenadas de la más reciente a la más antigua
   */
  async findAllByUser(userId: string, filters?: TaskFilters): Promise<Task[]> {
    // Los filtros se montan como condiciones acumulativas con parámetros
    // numerados. Antes se filtraba en memoria después de leer todas las
    // tareas; ahora el trabajo lo hace la base de datos y solo viajan las
    // filas que realmente se piden.
    const conditions = ['user_id = $1'];
    const params: unknown[] = [userId];

    if (filters?.status) {
      params.push(filters.status);
      conditions.push(`status = $${params.length}`);
    }
    if (filters?.priority) {
      params.push(filters.priority);
      conditions.push(`priority = $${params.length}`);
    }
    if (filters?.search) {
      // ILIKE es la comparación de texto que ignora mayúsculas en Postgres.
      //
      // Parametrizar evita la inyección, pero NO evita que los comodines de
      // LIKE se interpreten: sin escaparlos, buscar "%" devuelve todas las
      // tareas y buscar "50%" no encuentra el texto "50%". Por eso se escapan
      // los tres caracteres especiales y se declara ESCAPE explícitamente.
      params.push(`%${escapeLikePattern(filters.search)}%`);
      conditions.push(
        `(title ILIKE $${params.length} ESCAPE '\\' OR description ILIKE $${params.length} ESCAPE '\\')`,
      );
    }

    const rows = await query<TaskRow>(
      `SELECT ${COLUMNS} FROM tasks
       WHERE ${conditions.join(' AND ')}
       ORDER BY created_at DESC`,
      params,
    );
    return rows.map(toTask);
  },

  /** @returns la tarea si existe y es del usuario; si no, `null` */
  async findById(id: string, userId: string): Promise<Task | null> {
    // El user_id va en el WHERE, no en una comprobación posterior: una tarea
    // ajena simplemente no existe para esta consulta.
    const rows = await query<TaskRow>(
      `SELECT ${COLUMNS} FROM tasks WHERE id = $1 AND user_id = $2`,
      [id, userId],
    );
    return rows[0] ? toTask(rows[0]) : null;
  },

  // excludeId permite comprobar duplicados al actualizar sin que una tarea
  // choque consigo misma cuando no cambia el título.
  /**
   * Busca una tarea del usuario con el mismo título, comparando sin
   * mayúsculas y sin espacios en los extremos (igual que el índice único).
   *
   * @returns la tarea coincidente, o `null` si el título está libre
   */
  async findByTitleForUser(title: string, userId: string, excludeId?: string): Promise<Task | null> {
    const params: unknown[] = [userId, title];
    let sql = `SELECT ${COLUMNS} FROM tasks
               WHERE user_id = $1 AND LOWER(TRIM(title)) = LOWER(TRIM($2))`;

    if (excludeId) {
      params.push(excludeId);
      sql += ` AND id <> $${params.length}`;
    }

    const rows = await query<TaskRow>(sql, params);
    return rows[0] ? toTask(rows[0]) : null;
  },

  /**
   * Inserta una tarea; id y fechas los pone la base.
   *
   * @throws el error de `pg` con código 23505 si el título está repetido
   *         (índice único) o 23503 si el usuario ya no existe
   */
  async create(
    input: { title: string; description: string; status: TaskStatus; priority: TaskPriority },
    userId: string,
  ): Promise<Task> {
    const rows = await query<TaskRow>(
      `INSERT INTO tasks (title, description, status, priority, user_id)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING ${COLUMNS}`,
      [input.title, input.description, input.status, input.priority, userId],
    );
    return toTask(rows[0]);
  },

  /**
   * Actualiza los campos indicados (solo título, descripción, estado y
   * prioridad) y pone `updated_at` a la hora actual.
   *
   * @returns la tarea actualizada, o `null` si no existe o es de otro usuario
   */
  async update(
    id: string,
    userId: string,
    updates: Partial<Omit<Task, 'id' | 'userId' | 'createdAt'>>,
  ): Promise<Task | null> {
    const allowed = ['title', 'description', 'status', 'priority'] as const;
    const assignments: string[] = [];
    const params: unknown[] = [];

    for (const field of allowed) {
      if (updates[field] !== undefined) {
        params.push(updates[field]);
        assignments.push(`${field} = $${params.length}`);
      }
    }

    // Sin campos que cambiar no hay nada que hacer, pero el contrato del
    // método es devolver la tarea si existe: se consulta y se devuelve igual.
    if (assignments.length === 0) return this.findById(id, userId);

    assignments.push('updated_at = now()');
    params.push(id, userId);

    const rows = await query<TaskRow>(
      `UPDATE tasks SET ${assignments.join(', ')}
       WHERE id = $${params.length - 1} AND user_id = $${params.length}
       RETURNING ${COLUMNS}`,
      params,
    );
    return rows[0] ? toTask(rows[0]) : null;
  },

  /** @returns `true` si borró la tarea; `false` si no existía o era de otro usuario */
  async delete(id: string, userId: string): Promise<boolean> {
    const rows = await query<{ id: string }>(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, userId],
    );
    return rows.length > 0;
  },

  /** @returns `{ total, pending, inProgress, completed }` del usuario */
  async countByUser(userId: string) {
    // Una sola consulta con agregación en lugar de traerse todas las tareas y
    // contarlas en Node. FILTER es la forma de Postgres de contar por
    // condición sin repetir la consulta una vez por estado.
    const rows = await query<{
      total: number;
      pending: number;
      in_progress: number;
      completed: number;
    }>(
      `SELECT
         COUNT(*)                                          AS total,
         COUNT(*) FILTER (WHERE status = 'pending')        AS pending,
         COUNT(*) FILTER (WHERE status = 'in-progress')    AS in_progress,
         COUNT(*) FILTER (WHERE status = 'completed')      AS completed
       FROM tasks WHERE user_id = $1`,
      [userId],
    );

    const row = rows[0];
    return {
      total: row.total,
      pending: row.pending,
      inProgress: row.in_progress,
      completed: row.completed,
    };
  },
};
