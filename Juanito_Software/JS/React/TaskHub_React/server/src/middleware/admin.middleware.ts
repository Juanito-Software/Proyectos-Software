import { Request, Response, NextFunction } from 'express';
import { usersRepository } from '../modules/users/users.repository.js';
import { ApiError } from '../utils/api-error.js';
import { registrarEventoSeguridad } from '../utils/security-log.js';

/**
 * Exige rol de administrador. Va siempre después de authMiddleware, que es
 * quien deja el userId en la petición.
 *
 * El rol se consulta en la base de datos en cada petición, y no se lee del
 * JWT, a propósito. Si estuviera dentro del token, quitarle el rol a alguien
 * no tendría efecto hasta que su token de acceso caducara — hasta quince
 * minutos con la configuración actual, y siete días con la anterior a los
 * refresh tokens. Cuesta una consulta, pero el permiso que se comprueba es
 * siempre el permiso actual.
 *
 * Devuelve 403 y no 404 porque aquí el recurso no es secreto: quien pregunta
 * ya está autenticado y sabe que existe una zona de administración. Ocultarla
 * no aportaría nada y confundiría el diagnóstico.
 */
export async function requireAdmin(
  req: Request,
  _res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const user = await usersRepository.findById(req.userId!);

    if (!user) {
      // El token es válido pero el usuario ya no existe: por ejemplo, otro
      // administrador lo borró mientras tenía la sesión abierta.
      next(ApiError.unauthorized('La cuenta ya no existe'));
      return;
    }

    if (user.role !== 'admin') {
      // Un usuario normal llamando a /api/admin no es necesariamente un
      // ataque —puede ser un enlace guardado—, pero repetido sí lo es, y sin
      // registrarlo no hay forma de distinguir una cosa de la otra.
      registrarEventoSeguridad('autorizacion.denegada', {
        usuario: user.username,
        userId: user.id,
        motivo: 'se-requiere-admin',
        ruta: req.originalUrl,
      });
      next(ApiError.forbidden('Se requieren permisos de administrador'));
      return;
    }

    next();
  } catch (err) {
    next(err);
  }
}
