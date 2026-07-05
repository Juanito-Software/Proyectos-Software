import { Request, Response, NextFunction } from 'express';
import { TasksService } from './tasks.service';
import { ApiResponse } from '../../utils/api-response';
import { CreateTaskDTO, UpdateTaskDTO, TaskFilters } from './tasks.types';

export class TasksController {
  private service: TasksService;

  constructor() {
    this.service = new TasksService();
  }

  public getAllTasks = async (
    req: Request<any, any, any, TaskFilters>,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const { status, priority, search } = req.query;
      const tasks = await this.service.getAllTasks({ status, priority, search });
      res.json(ApiResponse.success(tasks, 'Tasks retrieved successfully'));
    } catch (error) {
      next(error);
    }
  };

  public getTaskById = async (
    req: Request<{ id: string }>,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const { id } = req.params;
      const task = await this.service.getTaskById(id);
      res.json(ApiResponse.success(task, 'Task retrieved successfully'));
    } catch (error) {
      next(error);
    }
  };

  public createTask = async (
    req: Request<any, any, CreateTaskDTO>,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const task = await this.service.createTask(req.body);
      res.status(201).json(ApiResponse.success(task, 'Task created successfully'));
    } catch (error) {
      next(error);
    }
  };

  public updateTask = async (
    req: Request<{ id: string }, any, UpdateTaskDTO>,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const { id } = req.params;
      const task = await this.service.updateTask(id, req.body);
      res.json(ApiResponse.success(task, 'Task updated successfully'));
    } catch (error) {
      next(error);
    }
  };

  public deleteTask = async (
    req: Request<{ id: string }>,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const { id } = req.params;
      await this.service.deleteTask(id);
      res.json(ApiResponse.success({ id }, 'Task deleted successfully'));
    } catch (error) {
      next(error);
    }
  };
}
