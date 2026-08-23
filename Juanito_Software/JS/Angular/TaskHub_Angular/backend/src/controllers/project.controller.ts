import { Request, Response } from 'express';
import { projectService } from '../services/project.service';
import { asyncHandler } from '../utils/asyncHandler';
import { ApiError } from '../utils/ApiError';

function getProjectId(req: Request): string {
  const id = req.params.id;
  if (typeof id !== 'string' || !id.trim()) {
    throw ApiError.badRequest('Parámetro de proyecto inválido');
  }
  return id;
}

export const projectController = {
  create: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const project = await projectService.create(req.user.id, req.body);
    res.status(201).json(project);
  }),

  list: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 20);
    const search = typeof req.query.search === 'string' ? req.query.search : undefined;
    const projects = await projectService.listForUser(req.user.id, page, limit, search);
    res.json(projects);
  }),

  getById: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const project = await projectService.getById(getProjectId(req), req.user.id);
    res.json(project);
  }),

  update: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const project = await projectService.update(getProjectId(req), req.user.id, req.body);
    res.json(project);
  }),

  remove: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    await projectService.remove(getProjectId(req), req.user.id);
    res.status(204).send();
  }),

  addMember: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const member = await projectService.addMember(getProjectId(req), req.user.id, req.body);
    res.status(201).json(member);
  }),
};
