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

export const tasksService = {
  listForUser(userId: string, filters?: TaskFilters) {
    return tasksRepository.findAllByUser(userId, filters).map(toDto);
  },

  getById(id: string, userId: string) {
    const task = tasksRepository.findById(id, userId);
    if (!task) throw ApiError.notFound('Tarea no encontrada');
    return toDto(task);
  },

  create(input: CreateTaskDTO, userId: string) {
    const title = input.title.trim();

    // Regla de negocio: no permitir dos tareas con el mismo título para el
    // mismo usuario. Es por usuario, no global, porque las tareas siempre
    // estuvieron aisladas por userId — que Ana y Juan tengan los dos una
    // tarea "Comprar pan" no es un conflicto real.
    if (tasksRepository.findByTitleForUser(title, userId)) {
      throw ApiError.conflict('Ya tienes una tarea con este título');
    }

    const created = tasksRepository.create(
      {
        title,
        description: input.description?.trim() ?? '',
        status: resolveStatus(input) ?? 'pending',
        priority: (input.priority ?? 'medium') as TaskPriority,
      },
      userId,
    );
    return toDto(created);
  },

  update(id: string, userId: string, input: UpdateTaskDTO) {
    const existing = tasksRepository.findById(id, userId);
    if (!existing) throw ApiError.notFound('Tarea no encontrada');

    if (input.title !== undefined) {
      const title = input.title.trim();
      if (title.toLowerCase() !== existing.title.toLowerCase()) {
        if (tasksRepository.findByTitleForUser(title, userId, id)) {
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

    const updated = tasksRepository.update(id, userId, updates);
    if (!updated) throw ApiError.internal('No se pudo actualizar la tarea');
    return toDto(updated);
  },

  remove(id: string, userId: string) {
    if (!tasksRepository.delete(id, userId)) {
      throw ApiError.notFound('Tarea no encontrada');
    }
  },

  statsForUser(userId: string) {
    return tasksRepository.countByUser(userId);
  },
};
