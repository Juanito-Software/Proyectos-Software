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

export const tasksController = {
  list(req: Request, res: Response, next: NextFunction) {
    try {
      const tasks = tasksService.listForUser(req.userId!, readFilters(req));
      res.json(ApiResponse.success(tasks, 'Tareas obtenidas correctamente'));
    } catch (err) {
      next(err);
    }
  },

  stats(req: Request, res: Response, next: NextFunction) {
    try {
      res.json(ApiResponse.success(tasksService.statsForUser(req.userId!), 'Resumen de tareas'));
    } catch (err) {
      next(err);
    }
  },

  getById(req: Request, res: Response, next: NextFunction) {
    try {
      const task = tasksService.getById(req.params.id, req.userId!);
      res.json(ApiResponse.success(task, 'Tarea obtenida correctamente'));
    } catch (err) {
      next(err);
    }
  },

  create(req: Request, res: Response, next: NextFunction) {
    try {
      const task = tasksService.create(req.body, req.userId!);
      res.status(201).json(ApiResponse.success(task, 'Tarea creada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  update(req: Request, res: Response, next: NextFunction) {
    try {
      const task = tasksService.update(req.params.id, req.userId!, req.body);
      res.json(ApiResponse.success(task, 'Tarea actualizada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  remove(req: Request, res: Response, next: NextFunction) {
    try {
      tasksService.remove(req.params.id, req.userId!);
      res.json(ApiResponse.success({ id: req.params.id }, 'Tarea eliminada correctamente'));
    } catch (err) {
      next(err);
    }
  },
};
