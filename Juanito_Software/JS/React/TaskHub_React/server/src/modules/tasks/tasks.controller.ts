import { Request, Response, NextFunction } from 'express';
import { tasksService } from './tasks.service.js';
import { ApiResponse } from '../../utils/api-response.js';
import { TaskFilters, isTaskStatus, isTaskPriority } from './tasks.types.js';

function readFilters(req: Request): TaskFilters {
  const { status, priority, search } = req.query;
  return {
    ...(isTaskStatus(status) ? { status } : {}),
    ...(isTaskPriority(priority) ? { priority } : {}),
    ...(typeof search === 'string' && search.trim() ? { search: search.trim() } : {}),
  };
}

/**
 * Los controladores pasan a ser asíncronos porque el repositorio ahora habla
 * con la base de datos. El try/catch sigue siendo necesario: en Express 4 una
 * promesa rechazada no llega al middleware de errores por sí sola, así que el
 * `await` va dentro del try y el fallo se reenvía con next().
 */
export const tasksController = {
  async list(req: Request, res: Response, next: NextFunction) {
    try {
      const tasks = await tasksService.listForUser(req.userId!, readFilters(req));
      res.json(ApiResponse.success(tasks, 'Tareas obtenidas correctamente'));
    } catch (err) {
      next(err);
    }
  },

  async stats(req: Request, res: Response, next: NextFunction) {
    try {
      const stats = await tasksService.statsForUser(req.userId!);
      res.json(ApiResponse.success(stats, 'Resumen de tareas'));
    } catch (err) {
      next(err);
    }
  },

  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.getById(req.params.id, req.userId!);
      res.json(ApiResponse.success(task, 'Tarea obtenida correctamente'));
    } catch (err) {
      next(err);
    }
  },

  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.create(req.body, req.userId!);
      res.status(201).json(ApiResponse.success(task, 'Tarea creada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  async update(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.update(req.params.id, req.userId!, req.body);
      res.json(ApiResponse.success(task, 'Tarea actualizada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  async remove(req: Request, res: Response, next: NextFunction) {
    try {
      await tasksService.remove(req.params.id, req.userId!);
      res.json(ApiResponse.success({ id: req.params.id }, 'Tarea eliminada correctamente'));
    } catch (err) {
      next(err);
    }
  },
};
