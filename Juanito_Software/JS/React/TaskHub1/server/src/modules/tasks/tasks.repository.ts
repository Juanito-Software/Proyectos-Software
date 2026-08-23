import fs from 'node:fs';
import crypto from 'node:crypto';
import { getTasksFile } from '../../config/paths.js';
import { Task, TaskDto, TaskFilters, TaskStatus, TaskPriority, isTaskStatus, isTaskPriority } from './tasks.types.js';

/**
 * Migración perezosa: las tareas guardadas antes de introducir status/priority
 * solo tienen `completed`. Se normalizan al leer, así que los datos existentes
 * siguen funcionando sin script de migración ni pérdida de información.
 */
function normalize(raw: Record<string, unknown>): Task {
  const status: TaskStatus = isTaskStatus(raw.status)
    ? raw.status
    : raw.completed === true
      ? 'completed'
      : 'pending';

  const priority: TaskPriority = isTaskPriority(raw.priority) ? raw.priority : 'medium';

  return {
    id: String(raw.id),
    title: String(raw.title ?? ''),
    description: String(raw.description ?? ''),
    status,
    priority,
    userId: String(raw.userId),
    createdAt: String(raw.createdAt ?? new Date().toISOString()),
    updatedAt: String(raw.updatedAt ?? new Date().toISOString()),
  };
}

export function toDto(task: Task): TaskDto {
  return { ...task, completed: task.status === 'completed' };
}

function readTasks(): Task[] {
  try {
    const parsed = JSON.parse(fs.readFileSync(getTasksFile(), 'utf-8'));
    return Array.isArray(parsed) ? parsed.map(normalize) : [];
  } catch {
    return [];
  }
}

function writeTasks(tasks: Task[]): void {
  fs.writeFileSync(getTasksFile(), JSON.stringify(tasks, null, 2), 'utf-8');
}

export const tasksRepository = {
  findAllByUser(userId: string, filters?: TaskFilters): Task[] {
    let result = readTasks().filter((t) => t.userId === userId);

    if (filters?.status) {
      result = result.filter((t) => t.status === filters.status);
    }
    if (filters?.priority) {
      result = result.filter((t) => t.priority === filters.priority);
    }
    if (filters?.search) {
      const query = filters.search.toLowerCase();
      result = result.filter(
        (t) => t.title.toLowerCase().includes(query) || t.description.toLowerCase().includes(query),
      );
    }

    // Más recientes primero, igual que TaskHub2.
    return result.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  },

  findById(id: string, userId: string): Task | null {
    const task = readTasks().find((t) => t.id === id);
    return task?.userId === userId ? task : null;
  },

  // excludeId permite comprobar duplicados al actualizar sin que una tarea
  // choque consigo misma cuando no cambia el título.
  findByTitleForUser(title: string, userId: string, excludeId?: string): Task | null {
    const normalized = title.trim().toLowerCase();
    return (
      readTasks().find(
        (t) => t.userId === userId && t.id !== excludeId && t.title.trim().toLowerCase() === normalized,
      ) ?? null
    );
  },

  create(
    input: { title: string; description: string; status: TaskStatus; priority: TaskPriority },
    userId: string,
  ): Task {
    const tasks = readTasks();
    const now = new Date().toISOString();
    const newTask: Task = {
      id: crypto.randomUUID(),
      title: input.title,
      description: input.description,
      status: input.status,
      priority: input.priority,
      userId,
      createdAt: now,
      updatedAt: now,
    };
    tasks.push(newTask);
    writeTasks(tasks);
    return newTask;
  },

  update(id: string, userId: string, updates: Partial<Omit<Task, 'id' | 'userId' | 'createdAt'>>): Task | null {
    const tasks = readTasks();
    const index = tasks.findIndex((t) => t.id === id && t.userId === userId);
    if (index === -1) return null;
    tasks[index] = { ...tasks[index], ...updates, updatedAt: new Date().toISOString() };
    writeTasks(tasks);
    return tasks[index];
  },

  delete(id: string, userId: string): boolean {
    const tasks = readTasks();
    const index = tasks.findIndex((t) => t.id === id && t.userId === userId);
    if (index === -1) return false;
    tasks.splice(index, 1);
    writeTasks(tasks);
    return true;
  },

  countByUser(userId: string) {
    const tasks = readTasks().filter((t) => t.userId === userId);
    return {
      total: tasks.length,
      pending: tasks.filter((t) => t.status === 'pending').length,
      inProgress: tasks.filter((t) => t.status === 'in-progress').length,
      completed: tasks.filter((t) => t.status === 'completed').length,
    };
  },
};
