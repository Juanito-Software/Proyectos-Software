import { Request, Response, NextFunction } from 'express';
import { tasksService } from './tasks.service.js';
import { ApiResponse } from '../../utils/api-response.js';
import { TaskFilters, isTaskStatus, isTaskPriority } from './tasks.types.js';

/**
 * Extrae los filtros del listado de la query string, quedándose solo con los
 * valores válidos. Un `status` o `priority` desconocido se ignora (no se
 * filtra por él) y `search` se recorta; si queda vacío, tampoco se aplica.
 *
 * @param req petición con `?status=&priority=&search=`
 * @returns filtros listos para el servicio
 */
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
/** Manejadores HTTP de `/api/tasks/*` (ver la nota de arriba sobre el try/catch). */
export const tasksController = {
  /** `GET /api/tasks` — tareas del usuario, con filtros opcionales. */
  async list(req: Request, res: Response, next: NextFunction) {
    try {
      const tasks = await tasksService.listForUser(req.userId!, readFilters(req));
      res.json(ApiResponse.success(tasks, 'Tareas obtenidas correctamente'));
    } catch (err) {
      next(err);
    }
  },

  /** `GET /api/tasks/stats` — recuento de tareas del usuario por estado. */
  async stats(req: Request, res: Response, next: NextFunction) {
    try {
      const stats = await tasksService.statsForUser(req.userId!);
      res.json(ApiResponse.success(stats, 'Resumen de tareas'));
    } catch (err) {
      next(err);
    }
  },

  /** `GET /api/tasks/:id` — una tarea del usuario; 404 si no existe o es de otro. */
  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.getById(req.params.id, req.userId!);
      res.json(ApiResponse.success(task, 'Tarea obtenida correctamente'));
    } catch (err) {
      next(err);
    }
  },

  /** `POST /api/tasks` — crea una tarea y responde 201 con ella. */
  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.create(req.body, req.userId!);
      res.status(201).json(ApiResponse.success(task, 'Tarea creada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  /** `PATCH /api/tasks/:id` — modifica solo los campos enviados. */
  async update(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.update(req.params.id, req.userId!, req.body);
      res.json(ApiResponse.success(task, 'Tarea actualizada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  /** `PUT /api/tasks/:id` — reemplaza la tarea entera (los campos omitidos vuelven a su valor por defecto). */
  async replace(req: Request, res: Response, next: NextFunction) {
    try {
      const task = await tasksService.replace(req.params.id, req.userId!, req.body);
      res.json(ApiResponse.success(task, 'Tarea reemplazada correctamente'));
    } catch (err) {
      next(err);
    }
  },

  /** `DELETE /api/tasks/:id` — borra la tarea y devuelve su id. */
  async remove(req: Request, res: Response, next: NextFunction) {
    try {
      await tasksService.remove(req.params.id, req.userId!);
      res.json(ApiResponse.success({ id: req.params.id }, 'Tarea eliminada correctamente'));
    } catch (err) {
      next(err);
    }
  },
};
