import { usersRepository } from '../users/users.repository.js';
import { query } from '../../config/db.js';
import { ApiError } from '../../utils/api-error.js';

export const adminService = {
  listUsers() {
    return usersRepository.listAll();
  },

  /**
   * Borra un usuario y, por la clave foránea en cascada, todas sus tareas.
   *
   * Dos salvaguardas, y las dos existen por lo mismo: que un clic no deje la
   * aplicación sin nadie que pueda administrarla.
   */
  async removeUser(targetId: string, requesterId: string) {
    if (targetId === requesterId) {
      throw ApiError.badRequest('No puedes borrar tu propia cuenta de administrador');
    }

    const target = await usersRepository.findById(targetId);
    if (!target) {
      throw ApiError.notFound('Usuario no encontrado');
    }

    if (target.role === 'admin') {
      const admins = await usersRepository.countByRole('admin');
      if (admins <= 1) {
        throw ApiError.badRequest('No puedes borrar al único administrador');
      }
    }

    await usersRepository.deleteById(targetId);
    return { id: targetId, username: target.username };
  },

  /** Resumen de toda la instancia, no de un usuario concreto. */
  async globalStats() {
    const rows = await query<{
      users: number;
      admins: number;
      tasks: number;
      pending: number;
      in_progress: number;
      completed: number;
    }>(
      `SELECT
         (SELECT COUNT(*) FROM users)                                   AS users,
         (SELECT COUNT(*) FROM users WHERE role = 'admin')              AS admins,
         (SELECT COUNT(*) FROM tasks)                                   AS tasks,
         (SELECT COUNT(*) FROM tasks WHERE status = 'pending')          AS pending,
         (SELECT COUNT(*) FROM tasks WHERE status = 'in-progress')      AS in_progress,
         (SELECT COUNT(*) FROM tasks WHERE status = 'completed')        AS completed`,
    );

    const row = rows[0];
    return {
      users: row.users,
      admins: row.admins,
      tasks: row.tasks,
      pending: row.pending,
      inProgress: row.in_progress,
      completed: row.completed,
    };
  },
};
