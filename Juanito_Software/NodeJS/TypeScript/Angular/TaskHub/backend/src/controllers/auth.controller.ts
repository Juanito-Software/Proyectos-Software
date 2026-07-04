import { Request, Response, CookieOptions } from 'express';
import { authService } from '../services/auth.service';
import { parseExpiryToMs } from '../services/token.service';
import { asyncHandler } from '../utils/asyncHandler';
import { ApiError } from '../utils/ApiError';
import { env, isProduction } from '../config/env';

const REFRESH_COOKIE_NAME = 'refreshToken';

function refreshCookieOptions(): CookieOptions {
  return {
    httpOnly: true,
    secure: isProduction,
    sameSite: 'lax',
    path: '/api/auth',
    maxAge: parseExpiryToMs(env.jwt.refreshExpiresIn),
  };
}

function setRefreshCookie(res: Response, refreshToken: string): void {
  res.cookie(REFRESH_COOKIE_NAME, refreshToken, refreshCookieOptions());
}

export const authController = {
  register: asyncHandler(async (req: Request, res: Response) => {
    const { user, accessToken, refreshToken } = await authService.register(req.body);
    setRefreshCookie(res, refreshToken);
    res.status(201).json({ user, accessToken });
  }),

  login: asyncHandler(async (req: Request, res: Response) => {
    const { user, accessToken, refreshToken } = await authService.login(req.body);
    setRefreshCookie(res, refreshToken);
    res.status(200).json({ user, accessToken });
  }),

  refresh: asyncHandler(async (req: Request, res: Response) => {
    const refreshToken = req.cookies?.[REFRESH_COOKIE_NAME];
    if (!refreshToken) throw ApiError.unauthorized('No hay sesión activa');

    try {
      const result = await authService.refresh(refreshToken);
      setRefreshCookie(res, result.refreshToken);
      res.status(200).json({ user: result.user, accessToken: result.accessToken });
    } catch (err) {
      res.clearCookie(REFRESH_COOKIE_NAME, { path: '/api/auth' });
      throw err;
    }
  }),

  logout: asyncHandler(async (req: Request, res: Response) => {
    const refreshToken = req.cookies?.[REFRESH_COOKIE_NAME];
    if (refreshToken) await authService.logout(refreshToken);
    res.clearCookie(REFRESH_COOKIE_NAME, { path: '/api/auth' });
    res.status(204).send();
  }),
};
