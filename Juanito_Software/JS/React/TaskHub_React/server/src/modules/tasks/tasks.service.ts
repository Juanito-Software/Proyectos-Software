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

/**
 * 23503 es «violación de clave foránea».
 *
 * En este servicio solo puede significar una cosa: se intenta crear una tarea
 * para un `user_id` que ya no está en `users`. Y eso solo pasa en un escenario
 * — el usuario se borró mientras tenía la sesión abierta, y su token de acceso
 * sigue siendo criptográficamente válido hasta que caduque.
 *
 * Sin traducirlo, la petición acababa en **500** con el mensaje de PostgreSQL:
 * el servidor daba a entender que había fallado él, cuando lo que ocurre es que
 * la cuenta que pide ya no existe. El 401 es la respuesta correcta y además
 * coincide con la que da `requireAdmin` en el mismo escenario, que hasta ahora
 * era la única parte de la aplicación que lo trataba bien.
 *
 * La alternativa —comprobar en cada petición que el usuario existe— cerraría
 * también el hueco de la lectura, pero cuesta una consulta más por petición.
 * Ver la nota en `authMiddleware` sobre por qué no se hace.
 */
function isForeignKeyViolation(err: unknown): boolean {
  return typeof err === 'object' && err !== null && (err as { code?: string }).code === '23503';
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
      if (isForeignKeyViolation(err)) {
        throw ApiError.unauthorized('La cuenta ya no existe');
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

  /**
   * PUT es un reemplazo COMPLETO, y por eso no comparte método con `update`.
   *
   * PATCH actualiza solo lo que llega y deja el resto como estaba; PUT declara
   * «esta es la tarea entera a partir de ahora», así que los campos que no se
   * envían vuelven a sus valores por defecto, igual que al crear (título
   * obligatorio, descripción vacía, pendiente, prioridad media). Antes ambos
   * métodos hablaban con el mismo controlador y un PUT de una sola esquina no
   * era ningún reemplazo; era un PATCH con otro nombre.
   */
  async replace(id: string, userId: string, input: CreateTaskDTO) {
    const existing = await tasksRepository.findById(id, userId);
    if (!existing) throw ApiError.notFound('Tarea no encontrada');

    const title = input.title.trim();
    if (title.toLowerCase() !== existing.title.toLowerCase()) {
      if (await tasksRepository.findByTitleForUser(title, userId, id)) {
        throw ApiError.conflict('Ya tienes una tarea con este título');
      }
    }

    try {
      const updated = await tasksRepository.update(id, userId, {
        title,
        description: input.description?.trim() ?? '',
        status: resolveStatus(input) ?? 'pending',
        priority: (input.priority ?? 'medium') as TaskPriority,
      });
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
