/**
 * Tipos del dominio de tareas: el registro guardado, lo que sale por la API,
 * lo que se acepta al crear/editar y los filtros del listado.
 */

/** Estados posibles de una tarea. El tipo `TaskStatus` se deriva de aquí. */
export const TASK_STATUSES = ['pending', 'in-progress', 'completed'] as const;
/** Prioridades posibles. El tipo `TaskPriority` se deriva de aquí. */
export const TASK_PRIORITIES = ['low', 'medium', 'high'] as const;

/** `'pending' | 'in-progress' | 'completed'`. */
export type TaskStatus = (typeof TASK_STATUSES)[number];
/** `'low' | 'medium' | 'high'`. */
export type TaskPriority = (typeof TASK_PRIORITIES)[number];

/**
 * Cómo se guarda una tarea (tabla `tasks` de PostgreSQL). `status` es la
 * fuente de verdad.
 */
export interface Task {
  /** UUID generado por la base. */
  id: string;
  /** Título; obligatorio y no vacío. */
  title: string;
  /** Descripción libre; cadena vacía si no se dio. */
  description: string;
  /** Estado de la tarea. */
  status: TaskStatus;
  /** Prioridad de la tarea. */
  priority: TaskPriority;
  /** Id del usuario dueño. Cada usuario solo ve y toca las suyas. */
  userId: string;
  /** Fecha de creación, ISO 8601. */
  createdAt: string;
  /** Fecha de la última modificación, ISO 8601. */
  updatedAt: string;
}

/**
 * Lo que sale por la API. Añade `completed` derivado de `status`.
 *
 * El cliente React existente (TaskItem.jsx, filtros de TaskList) trabaja con
 * un booleano `completed`; el modelo nuevo tiene tres estados. En vez de
 * romper el frontend o duplicar la verdad en disco, `completed` se calcula al
 * serializar y se acepta como entrada traduciéndolo a `status`.
 */
export interface TaskDto extends Task {
  completed: boolean;
}

/**
 * Cuerpo de `POST` (crear) y de `PUT` (reemplazar). Los campos opcionales que
 * no se envían toman su valor por defecto (`''`, `pending`, `medium`).
 * `completed` es la forma antigua de indicar el estado y se traduce a `status`.
 */
export interface CreateTaskDTO {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  completed?: boolean;
}

/** Cuerpo de `PATCH`: solo se modifican los campos que vienen. */
export interface UpdateTaskDTO {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  completed?: boolean;
}

/** Filtros opcionales de `GET /api/tasks` (query string). */
export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  search?: string;
}

/**
 * @param value valor a comprobar (p. ej. un parámetro de la query)
 * @returns `true` si es un estado válido; actúa como guarda de tipo
 */
export function isTaskStatus(value: unknown): value is TaskStatus {
  return typeof value === 'string' && (TASK_STATUSES as readonly string[]).includes(value);
}

/**
 * @param value valor a comprobar
 * @returns `true` si es una prioridad válida; actúa como guarda de tipo
 */
export function isTaskPriority(value: unknown): value is TaskPriority {
  return typeof value === 'string' && (TASK_PRIORITIES as readonly string[]).includes(value);
}
