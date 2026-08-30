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

const COLUMNS = 'id, title, description, status, priority, user_id, created_at, updated_at';

/**
 * Neutraliza los comodines de LIKE en el texto que escribe el usuario.
 *
 * En un patrón de LIKE, `%` significa "cualquier secuencia" y `_` "cualquier
 * carácter". Alguien que busque "100%" espera encontrar ese texto, no todas
 * las tareas. La barra invertida se escapa primero, porque es el carácter que
 * escapa a los otros dos y hacerlo al revés rompería el resultado.
 */
export function escapeLikePattern(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/%/g, '\\%').replace(/_/g, '\\_');
}

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

export const tasksRepository = {
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

  async delete(id: string, userId: string): Promise<boolean> {
    const rows = await query<{ id: string }>(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, userId],
    );
    return rows.length > 0;
  },

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
