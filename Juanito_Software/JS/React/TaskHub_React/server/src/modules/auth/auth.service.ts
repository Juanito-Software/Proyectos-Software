import { usersRepository } from '../users/users.repository.js';
import { tokenService } from './token.service.js';
import {
  sessionsRepository,
  generarRefreshToken,
  hashRefreshToken,
} from './sessions.repository.js';
import { ApiError } from '../../utils/api-error.js';
import { registrarEventoSeguridad } from '../../utils/security-log.js';
import { env } from '../../config/env.js';
import { RegisterDTO, LoginDTO } from './auth.types.js';

/**
 * Credenciales que se devuelven al cliente.
 *
 * El refresco viaja aparte del sobre de datos: el controlador lo mete en una
 * cookie HttpOnly y nunca aparece en el cuerpo de la respuesta, para que
 * ningún JavaScript pueda leerlo.
 */
interface Credenciales {
  accessToken: string;
  refreshToken: string;
}

async function abrirSesion(userId: string, username: string): Promise<Credenciales> {
  const refreshToken = generarRefreshToken();
  await sessionsRepository.crearFamilia(userId, refreshToken);
  return {
    accessToken: tokenService.generateAccessToken({ userId, username }),
    refreshToken,
  };
}

export const authService = {
  async register({ username, password }: RegisterDTO) {
    const user = await usersRepository.create(username.trim(), password);
    if (!user) {
      throw ApiError.conflict('El usuario ya existe');
    }
    const credenciales = await abrirSesion(user.id, user.username);
    registrarEventoSeguridad('registro.correcto', { usuario: user.username, userId: user.id });
    return { user, ...credenciales };
  },

  async login({ username, password }: LoginDTO) {
    const user = await usersRepository.findByUsername(username.trim());
    if (!user) {
      // El motivo se distingue en el REGISTRO pero no en la respuesta: al
      // atacante se le da siempre el mismo mensaje, y quien revisa los logs sí
      // puede separar "atacan una cuenta que existe" de "prueban nombres al
      // azar", que son dos ataques distintos.
      registrarEventoSeguridad('login.fallido', {
        usuario: username.trim(),
        motivo: 'usuario-inexistente',
      });
      throw ApiError.unauthorized('Usuario o contraseña incorrectos');
    }
    const valid = await usersRepository.verifyPassword(user, password);
    if (!valid) {
      // Mismo mensaje que "usuario no existe": evita que un atacante use la
      // respuesta para averiguar qué nombres de usuario están registrados.
      registrarEventoSeguridad('login.fallido', {
        usuario: user.username,
        userId: user.id,
        motivo: 'credenciales-invalidas',
      });
      throw ApiError.unauthorized('Usuario o contraseña incorrectos');
    }
    const credenciales = await abrirSesion(user.id, user.username);
    registrarEventoSeguridad('login.correcto', { usuario: user.username, userId: user.id });
    return { user: usersRepository.toPublic(user), ...credenciales };
  },

  /**
   * Rota un token de refresco y devuelve credenciales nuevas.
   *
   * El orden importa y no es negociable: **primero se revoca el token viejo y
   * solo después se crea el nuevo**. Al revés, un fallo entre las dos
   * operaciones dejaría dos tokens válidos a la vez sobre la misma sesión.
   *
   * Los casos que hay que separar cuando el token presentado no está activo:
   *
   * - No existe → alguien se lo ha inventado, o la sesión ya se limpió. 401 y
   *   nada que revocar.
   * - Caducado → 401. Toca volver a entrar.
   * - Revocado por logout o por una reutilización anterior → la sesión ya está
   *   muerta, no hay nada más que revocar.
   * - Revocado por rotación **hace muy poco** → casi con seguridad son dos
   *   peticiones simultáneas del mismo usuario, no un ataque. Se rechaza esta,
   *   pero la familia sigue viva y el cliente reintenta con la cookie nueva.
   * - Revocado por rotación **hace rato** → reutilización. Alguien está usando
   *   un token que ya se gastó, así que hay que asumir que tiene también el
   *   siguiente de la cadena: se revoca la familia entera.
   */
  async refresh(refreshToken: string | undefined) {
    if (!refreshToken || typeof refreshToken !== 'string') {
      registrarEventoSeguridad('refresh.rechazado', { motivo: 'sin-cookie' });
      throw ApiError.unauthorized('No hay sesión que renovar');
    }

    const hash = hashRefreshToken(refreshToken);
    const rotado = await sessionsRepository.marcarRotado(hash);

    if (!rotado) {
      await this.analizarFalloDeRotacion(hash);
      throw ApiError.unauthorized('Sesión inválida o expirada');
    }
    registrarEventoSeguridad('refresh.correcto', {
      userId: rotado.user_id,
      familia: rotado.family_id,
    });

    // El usuario pudo haberse borrado con la sesión abierta. Sin esto se
    // emitiría un token de acceso a nombre de una fila que ya no existe.
    const user = await usersRepository.findById(rotado.user_id);
    if (!user) {
      await sessionsRepository.revocarFamilia(rotado.family_id, 'logout');
      registrarEventoSeguridad('refresh.rechazado', {
        userId: rotado.user_id,
        motivo: 'cuenta-borrada',
      });
      throw ApiError.unauthorized('Sesión inválida o expirada');
    }

    const nuevoRefresh = generarRefreshToken();
    await sessionsRepository.encadenar(rotado.family_id, user.id, nuevoRefresh, rotado.id);

    return {
      user: usersRepository.toPublic(user),
      accessToken: tokenService.generateAccessToken({
        userId: user.id,
        username: user.username,
      }),
      refreshToken: nuevoRefresh,
    };
  },

  /**
   * Decide si un token de refresco que ya no está activo es una reutilización
   * maliciosa o simplemente el perdedor de una carrera entre dos pestañas.
   *
   * Separado del método anterior para que la regla se lea de un vistazo y se
   * pueda probar por su cuenta.
   */
  async analizarFalloDeRotacion(hash: string): Promise<void> {
    const sesion = await sessionsRepository.buscarPorHash(hash);

    // No existe, o ya estaba revocado por algo que no es una rotación: en
    // ninguno de los dos casos hay familia que salvar ni ataque que atajar.
    if (!sesion || sesion.revoked_reason !== 'rotated') return;

    const revocadoHace = Date.now() - new Date(sesion.revoked_at!).getTime();
    if (revocadoHace <= env.refreshGraceMs) {
      // Ventana de tolerancia: dos peticiones legítimas a la vez. Se deja
      // rastro igualmente: si estas líneas se disparan en avalancha, algo va
      // mal en el cliente y conviene enterarse.
      registrarEventoSeguridad('refresh.rechazado', {
        userId: sesion.user_id,
        familia: sesion.family_id,
        motivo: 'rotacion-simultanea',
      });
      return;
    }

    // Reutilización de verdad. Quien presenta este token tiene una copia de la
    // cadena, así que el siguiente eslabón también está comprometido.
    const revocados = await sessionsRepository.revocarFamilia(sesion.family_id, 'reuse-detected');
    registrarEventoSeguridad('refresh.reutilizacion', {
      userId: sesion.user_id,
      familia: sesion.family_id,
      gastadoHaceSegundos: Math.round(revocadoHace / 1000),
      tokensRevocados: revocados,
    });
  },

  /** Cierra una sesión concreta. Las demás del mismo usuario siguen abiertas. */
  async logout(refreshToken: string | undefined): Promise<void> {
    if (!refreshToken || typeof refreshToken !== 'string') return;

    const sesion = await sessionsRepository.buscarPorHash(hashRefreshToken(refreshToken));
    // Se revoca la familia y no solo la fila: si quedara viva la última de la
    // cadena, el logout no habría cerrado nada.
    if (sesion) {
      const revocados = await sessionsRepository.revocarFamilia(sesion.family_id, 'logout');
      registrarEventoSeguridad('logout', {
        userId: sesion.user_id,
        familia: sesion.family_id,
        tokensRevocados: revocados,
      });
    }
  },

  /** Cierra todas las sesiones del usuario, en todos sus dispositivos. */
  async logoutAll(userId: string): Promise<number> {
    const revocados = await sessionsRepository.revocarTodasDelUsuario(userId, 'logout-all');
    registrarEventoSeguridad('logout.global', { userId, tokensRevocados: revocados });
    return revocados;
  },
};
