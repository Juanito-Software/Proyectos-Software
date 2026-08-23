import { Request, Response } from 'express';
import { TaskStatus } from '@prisma/client';
import { taskService } from '../services/task.service';
import { asyncHandler } from '../utils/asyncHandler';
import { ApiError } from '../utils/ApiError';

function getTaskId(req: Request): string {
  const id = req.params.id;
  if (typeof id !== 'string' || !id.trim()) {
    throw ApiError.badRequest('Parámetro de tarea inválido');
  }
  return id;
}

export const taskController = {
  create: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const task = await taskService.create(req.user.id, req.body);
    res.status(201).json(task);
  }),

  list: asyncHandler(async (req: Request, res: Response) => {
    const { projectId, status, assigneeId } = req.query as Record<string, string | undefined>;
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 20);
    const tasks = await taskService.list(
      { projectId, status: status as TaskStatus | undefined, assigneeId },
      page,
      limit,
    );
    res.json(tasks);
  }),

  getById: asyncHandler(async (req: Request, res: Response) => {
    const task = await taskService.getById(getTaskId(req));
    res.json(task);
  }),

  update: asyncHandler(async (req: Request, res: Response) => {
    const task = await taskService.update(getTaskId(req), req.body);
    res.json(task);
  }),

  remove: asyncHandler(async (req: Request, res: Response) => {
    await taskService.remove(getTaskId(req));
    res.status(204).send();
  }),

  addComment: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const comment = await taskService.addComment(getTaskId(req), req.user.id, req.body);
    res.status(201).json(comment);
  }),

  dashboard: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const summary = await taskService.dashboardSummary(req.user.id);
    res.json(summary);
  }),
};
