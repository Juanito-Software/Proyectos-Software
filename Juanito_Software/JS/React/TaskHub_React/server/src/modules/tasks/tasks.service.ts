import { tasksRepository, toDto } from './tasks.repository.js';
import { ApiError } from '../../utils/api-error.js';
import { CreateTaskDTO, UpdateTaskDTO, TaskFilters, TaskStatus, TaskPriority } from './tasks.types.js';

/**
 * El cliente puede mandar `status` (modelo nuevo) o `completed` (modelo
 * antiguo, que sigue usando el frontend React). Si llegan los dos manda
 * `status`, por ser el más expresivo.
 */
function resolveStatus(input: { status?: TaskStatus; completed?: boolean }): TaskStatus | undefined {
  if (input.status !== undefined) return input.status;
  if (input.completed !== undefined) return input.completed ? 'completed' : 'pending';
  return undefined;
}

/**
 * 23505 es el código de Postgres para "violación de restricción única".
 *
 * Hace falta porque comprobar el duplicado y escribir son dos operaciones
 * distintas: dos peticiones a la vez pueden pasar las dos la comprobación y
 * chocar después en la inserción. Sin esto, la segunda respondería un 500
 * cuando lo correcto es el mismo 409 que recibe cualquier otro duplicado.
 */
function isUniqueViolation(err: unknown): boolean {
  return typeof err === 'object' && err !== null && (err as { code?: string }).code === '23505';
}

export const tasksService = {
  async listForUser(userId: string, filters?: TaskFilters) {
    const tasks = await tasksRepository.findAllByUser(userId, filters);
    return tasks.map(toDto);
  },

  async getById(id: string, userId: string) {
    const task = await tasksRepository.findById(id, userId);
    if (!task) throw ApiError.notFound('Tarea no encontrada');
    return toDto(task);
  },

  async create(input: CreateTaskDTO, userId: string) {
    const title = input.title.trim();

    // Regla de negocio: no permitir dos tareas con el mismo título para el
    // mismo usuario. Es por usuario, no global, porque las tareas siempre
    // estuvieron aisladas por userId — que Ana y Juan tengan los dos una
    // tarea "Comprar pan" no es un conflicto real.
    //
    // La comprobación previa existe para devolver un 409 con un mensaje
    // entendible; la garantía real la da el índice único de la base de datos,
    // que además cierra la ventana entre comprobar y escribir.
    if (await tasksRepository.findByTitleForUser(title, userId)) {
      throw ApiError.conflict('Ya tienes una tarea con este título');
    }

    try {
      const created = await tasksRepository.create(
        {
          title,
          description: input.description?.trim() ?? '',
          status: resolveStatus(input) ?? 'pending',
          priority: (input.priority ?? 'medium') as TaskPriority,
        },
        userId,
      );
      return toDto(created);
    } catch (err) {
      if (isUniqueViolation(err)) {
        throw ApiError.conflict('Ya tienes una tarea con este título');
      }
      throw err;
    }
  },

  async update(id: string, userId: string, input: UpdateTaskDTO) {
    const existing = await tasksRepository.findById(id, userId);
    if (!existing) throw ApiError.notFound('Tarea no encontrada');

    if (input.title !== undefined) {
      const title = input.title.trim();
      if (title.toLowerCase() !== existing.title.toLowerCase()) {
        if (await tasksRepository.findByTitleForUser(title, userId, id)) {
          throw ApiError.conflict('Ya tienes una tarea con este título');
        }
      }
    }

    const updates: Partial<typeof existing> = {};
    if (input.title !== undefined) updates.title = input.title.trim();
    if (input.description !== undefined) updates.description = input.description.trim();
    if (input.priority !== undefined) updates.priority = input.priority;

    const status = resolveStatus(input);
    if (status !== undefined) updates.status = status;

    try {
      const updated = await tasksRepository.update(id, userId, updates);
      if (!updated) throw ApiError.internal('No se pudo actualizar la tarea');
      return toDto(updated);
    } catch (err) {
      if (isUniqueViolation(err)) {
        throw ApiError.conflict('Ya tienes una tarea con este título');
      }
      throw err;
    }
  },

  async remove(id: string, userId: string) {
    if (!(await tasksRepository.delete(id, userId))) {
      throw ApiError.notFound('Tarea no encontrada');
    }
  },

  async statsForUser(userId: string) {
    return tasksRepository.countByUser(userId);
  },
};
