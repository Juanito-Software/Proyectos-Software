import { Request, Response, NextFunction } from 'express';
import { authService } from './auth.service.js';
import { ApiResponse } from '../../utils/api-response.js';
import { setRefreshCookie, clearRefreshCookie, readRefreshCookie } from './auth.cookie.js';

/**
 * Separa el token de refresco del resto de la respuesta.
 *
 * El refresco sale por la cookie y **nunca** por el cuerpo: si apareciera en el
 * JSON, el cliente podría leerlo con JavaScript y `HttpOnly` no habría servido
 * de nada. El token de acceso sí va en el cuerpo, porque el cliente tiene que
 * ponerlo en la cabecera `Authorization` de cada petición.
 */
function responder(
  res: Response,
  estado: number,
  resultado: { refreshToken: string } & Record<string, unknown>,
  mensaje: string,
): void {
  const { refreshToken, ...cuerpo } = resultado;
  setRefreshCookie(res, refreshToken);
  res.status(estado).json(ApiResponse.success(cuerpo, mensaje));
}

export const authController = {
  async register(req: Request, res: Response, next: NextFunction) {
    try {
      const result = await authService.register(req.body);
      responder(res, 201, result, 'Cuenta creada correctamente');
    } catch (err) {
      next(err);
    }
  },

  async login(req: Request, res: Response, next: NextFunction) {
    try {
      const result = await authService.login(req.body);
      responder(res, 200, result, 'Sesión iniciada correctamente');
    } catch (err) {
      next(err);
    }
  },

  /**
   * Renueva las credenciales a partir de la cookie de refresco.
   *
   * No lleva `authMiddleware`: se llama precisamente cuando el token de acceso
   * ha caducado, así que exigirlo haría el endpoint inalcanzable justo cuando
   * hace falta. La autenticación aquí la aporta el propio token de refresco.
   */
  async refresh(req: Request, res: Response, next: NextFunction) {
    try {
      const result = await authService.refresh(readRefreshCookie(req));
      responder(res, 200, result, 'Sesión renovada');
    } catch (err) {
      // Si la renovación falla, la cookie que traía el cliente ya no sirve para
      // nada. Borrarla evita que siga reintentando con una credencial muerta.
      clearRefreshCookie(res);
      next(err);
    }
  },

  /**
   * Cierra la sesión en el servidor.
   *
   * Responde 200 aunque no hubiera sesión: el cliente solo necesita saber que
   * puede olvidarse de sus credenciales, y distinguir "no había sesión" de
   * "la había" solo serviría para que alguien sondeara tokens ajenos.
   */
  async logout(req: Request, res: Response, next: NextFunction) {
    try {
      await authService.logout(readRefreshCookie(req));
      clearRefreshCookie(res);
      res.json(ApiResponse.success(null, 'Sesión cerrada'));
    } catch (err) {
      next(err);
    }
  },

  /**
   * Cierra todas las sesiones del usuario. Va detrás de `authMiddleware`, así
   * que solo puede cerrar las suyas: el identificador sale del token, no del
   * cuerpo de la petición.
   */
  async logoutAll(req: Request, res: Response, next: NextFunction) {
    try {
      const revocadas = await authService.logoutAll(req.userId!);
      clearRefreshCookie(res);
      res.json(ApiResponse.success({ revocadas }, 'Todas las sesiones han sido cerradas'));
    } catch (err) {
      next(err);
    }
  },

  /**
   * Cambia la contraseña y deja al usuario dentro.
   *
   * Usa `responder`, el mismo ayudante que register y login, porque devuelve
   * credenciales nuevas: el refresco tiene que salir por `Set-Cookie` y no en
   * el cuerpo. Si esto respondiera con un `res.json` corriente, el token de
   * refresco acabaría en el JSON y el `HttpOnly` no habría servido de nada.
   */
  async changePassword(req: Request, res: Response, next: NextFunction) {
    try {
      const { actual, nueva } = req.body ?? {};
      const result = await authService.changePassword(req.userId!, actual, nueva);
      responder(res, 200, result, 'Contraseña cambiada. Las demás sesiones se han cerrado');
    } catch (err) {
      next(err);
    }
  },
};
