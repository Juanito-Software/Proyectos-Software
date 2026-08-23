export const TASK_STATUSES = ['pending', 'in-progress', 'completed'] as const;
export const TASK_PRIORITIES = ['low', 'medium', 'high'] as const;

export type TaskStatus = (typeof TASK_STATUSES)[number];
export type TaskPriority = (typeof TASK_PRIORITIES)[number];

/** Cómo se guarda una tarea en disco. `status` es la fuente de verdad. */
export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  userId: string;
  createdAt: string;
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

export interface CreateTaskDTO {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  completed?: boolean;
}

export interface UpdateTaskDTO {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  completed?: boolean;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  search?: string;
}

export function isTaskStatus(value: unknown): value is TaskStatus {
  return typeof value === 'string' && (TASK_STATUSES as readonly string[]).includes(value);
}

export function isTaskPriority(value: unknown): value is TaskPriority {
  return typeof value === 'string' && (TASK_PRIORITIES as readonly string[]).includes(value);
}
