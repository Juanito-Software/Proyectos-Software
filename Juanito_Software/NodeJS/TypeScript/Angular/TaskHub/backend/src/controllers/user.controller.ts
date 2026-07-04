import { Request, Response } from 'express';
import { userService } from '../services/user.service';
import { asyncHandler } from '../utils/asyncHandler';
import { ApiError } from '../utils/ApiError';

function getUserId(req: Request): string {
  const id = req.params.id;
  if (typeof id !== 'string' || !id.trim()) {
    throw ApiError.badRequest('Parámetro de usuario inválido');
  }
  return id;
}

export const userController = {
  list: asyncHandler(async (req: Request, res: Response) => {
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 20);
    const result = await userService.list(page, limit);
    res.json(result);
  }),

  getById: asyncHandler(async (req: Request, res: Response) => {
    const user = await userService.getById(getUserId(req));
    res.json(user);
  }),

  updateProfile: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    const user = await userService.updateProfile(req.user.id, req.body);
    res.json(user);
  }),

  changePassword: asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) throw ApiError.unauthorized();
    await userService.changePassword(req.user.id, req.body);
    res.status(204).send();
  }),

  remove: asyncHandler(async (req: Request, res: Response) => {
    await userService.remove(getUserId(req));
    res.status(204).send();
  }),
};
