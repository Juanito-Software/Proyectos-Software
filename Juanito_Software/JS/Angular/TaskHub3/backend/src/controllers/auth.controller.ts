import { Request, Response, CookieOptions } from 'express';
import { authService } from '../services/auth.service';
import { parseExpiryToMs } from '../services/token.service';
import { asyncHandler } from '../utils/asyncHandler';
import { ApiError } from '../utils/ApiError';
import { env, isProduction } from '../config/env';

const REFRESH_COOKIE_NAME = 'refreshToken';

// Opciones de la cookie del refresh token.
//
// Cada opcion cubre un ataque distinto:
//
// - httpOnly: el JavaScript de la pagina no puede leerla. Es la razon de que el
//   refresh token viaje en cookie y no en el cuerpo de la respuesta: asi un XSS
//   no puede robarlo.
// - secure: en produccion solo viaja por HTTPS.
// - sameSite 'strict': el navegador no envia la cookie en peticiones originadas
//   en otro sitio web. Esto es lo que protege de CSRF. Las rutas
//   POST /api/auth/refresh y /logout se autentican SOLO con esta cookie, es
//   decir, con credenciales que el navegador adjunta por su cuenta, que es
//   justo la condicion que un ataque CSRF necesita. El access token no tiene
//   este problema porque va en la cabecera Authorization y esa el navegador no
//   la anade solo.
//   'strict' en lugar de 'lax' porque 'lax' deja pasar las navegaciones GET de
//   nivel superior, y no hay ningun flujo aqui que lo necesite: la cookie solo
//   la usa la SPA, que es same-site.
// - path: la cookie solo se envia a /api/auth, no al resto de la API.
function refreshCookieOptions(): CookieOptions {
  return {
    httpOnly: true,
    secure: isProduction,
    sameSite: 'strict',
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
