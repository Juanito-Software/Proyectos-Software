import { query } from '../../config/db.js';
import { env } from '../../config/env.js';
import { hashRefreshToken } from './refresh-token.js';

// Se reexportan para que quien trabaje con sesiones no tenga que saber que la
// generación del token vive en otro módulo. Está separado solo para poder
// probarlo sin base de datos.
export { generarRefreshToken, hashRefreshToken } from './refresh-token.js';

/**
 * Persistencia de los tokens de refresco.
 *
 * Una fila por token, no por sesión: al rotar, la vieja se marca revocada y
 * nace otra con el mismo `family_id`. La sesión es la cadena de filas que
 * comparten familia, y esa cadena es lo que permite distinguir una rotación
 * normal de una reutilización.
 */

export interface RefreshSession {
  id: string;
  family_id: string;
  user_id: string;
  created_at: Date;
  expires_at: Date;
  revoked_at: Date | null;
  revoked_reason: string | null;
}

/** Motivo por el que un token de refresco dejó de valer. */
export type MotivoRevocacion = 'rotated' | 'logout' | 'logout-all' | 'reuse-detected';

export const sessionsRepository = {
  /**
   * Crea la primera fila de una familia nueva. Es lo que ocurre al iniciar
   * sesión o al registrarse: cada login abre una sesión independiente, de modo
   * que cerrar una en el móvil no cierra la del portátil.
   */
  async crearFamilia(userId: string, token: string): Promise<RefreshSession> {
    const filas = await query<RefreshSession>(
      `INSERT INTO refresh_sessions (family_id, user_id, token_hash, expires_at)
       VALUES (gen_random_uuid(), $1, $2, now() + ($3 || ' milliseconds')::interval)
       RETURNING id, family_id, user_id, created_at, expires_at, revoked_at, revoked_reason`,
      [userId, hashRefreshToken(token), String(env.refreshTokenTtlMs)],
    );
    return filas[0];
  },

  /**
   * Marca un token como rotado **si y solo si** seguía activo, y devuelve la
   * fila. Si devuelve `null`, o el token no existe, o alguien se adelantó.
   *
   * La condición `revoked_at IS NULL` dentro del propio UPDATE es lo que hace
   * la operación segura frente a concurrencia: PostgreSQL serializa las
   * escrituras sobre la misma fila, así que de dos peticiones simultáneas con
   * el mismo token solo una encuentra la fila sin revocar y la otra actualiza
   * cero filas. No hace falta transacción explícita ni bloqueo: una única
   * sentencia ya es atómica.
   */
  async marcarRotado(tokenHash: string): Promise<RefreshSession | null> {
    const filas = await query<RefreshSession>(
      `UPDATE refresh_sessions
          SET revoked_at = now(), revoked_reason = 'rotated'
        WHERE token_hash = $1
          AND revoked_at IS NULL
          AND expires_at > now()
        RETURNING id, family_id, user_id, created_at, expires_at, revoked_at, revoked_reason`,
      [tokenHash],
    );
    return filas[0] ?? null;
  },

  /**
   * Busca un token sin modificarlo. Se usa cuando `marcarRotado` no encuentra
   * nada, para averiguar por qué: si no existe, si ya estaba revocado, si
   * caducó, o si es una reutilización que obliga a matar la familia.
   */
  async buscarPorHash(tokenHash: string): Promise<RefreshSession | null> {
    const filas = await query<RefreshSession>(
      `SELECT id, family_id, user_id, created_at, expires_at, revoked_at, revoked_reason
         FROM refresh_sessions
        WHERE token_hash = $1`,
      [tokenHash],
    );
    return filas[0] ?? null;
  },

  /** Encadena el token nuevo al que acaba de rotarse, dentro de la misma familia. */
  async encadenar(
    familyId: string,
    userId: string,
    token: string,
    parentId: string,
  ): Promise<RefreshSession> {
    const filas = await query<RefreshSession>(
      `INSERT INTO refresh_sessions (family_id, user_id, token_hash, parent_id, expires_at)
       VALUES ($1, $2, $3, $4, now() + ($5 || ' milliseconds')::interval)
       RETURNING id, family_id, user_id, created_at, expires_at, revoked_at, revoked_reason`,
      [familyId, userId, hashRefreshToken(token), parentId, String(env.refreshTokenTtlMs)],
    );
    return filas[0];
  },

  /**
   * Revoca todos los tokens vivos de una familia. Es lo que se hace al cerrar
   * sesión y, sobre todo, al detectar una reutilización: en ese momento hay que
   * asumir que el atacante tiene también el token siguiente de la cadena, así
   * que rechazar solo el presentado no serviría de nada.
   */
  async revocarFamilia(familyId: string, motivo: MotivoRevocacion): Promise<number> {
    const filas = await query<{ id: string }>(
      `UPDATE refresh_sessions
          SET revoked_at = now(), revoked_reason = $2
        WHERE family_id = $1 AND revoked_at IS NULL
        RETURNING id`,
      [familyId, motivo],
    );
    return filas.length;
  },

  /**
   * Revoca todas las sesiones de un usuario, en todos sus dispositivos.
   * Pensado para cuando se sospecha que la cuenta está comprometida.
   */
  async revocarTodasDelUsuario(userId: string, motivo: MotivoRevocacion): Promise<number> {
    const filas = await query<{ id: string }>(
      `UPDATE refresh_sessions
          SET revoked_at = now(), revoked_reason = $2
        WHERE user_id = $1 AND revoked_at IS NULL
        RETURNING id`,
      [userId, motivo],
    );
    return filas.length;
  },

  /** Cuántas sesiones activas tiene un usuario ahora mismo. */
  async contarActivasDelUsuario(userId: string): Promise<number> {
    const filas = await query<{ count: number }>(
      `SELECT COUNT(*) AS count
         FROM refresh_sessions
        WHERE user_id = $1 AND revoked_at IS NULL AND expires_at > now()`,
      [userId],
    );
    return filas[0].count;
  },

  /**
   * Borra las filas ya caducadas.
   *
   * Sin esto la tabla crece indefinidamente: cada renovación deja atrás una
   * fila revocada. Se conservan hasta que el token habría caducado de todas
   * formas, porque antes de esa fecha todavía hacen falta para detectar una
   * reutilización.
   */
  async limpiarCaducadas(): Promise<number> {
    const filas = await query<{ id: string }>(
      `DELETE FROM refresh_sessions WHERE expires_at < now() RETURNING id`,
    );
    return filas.length;
  },
};
