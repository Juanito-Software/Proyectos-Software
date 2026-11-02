/**
 * Datos de entrada de los casos de uso de autenticación (`auth.service.ts`).
 *
 * Llegan ya validados y normalizados por `auth.validation.ts`: el nombre de
 * usuario viene recortado y la contraseña ha pasado la política de
 * `password-policy.ts` (solo en el registro).
 */

/** Cuerpo de `POST /api/auth/register`. */
export interface RegisterDTO {
  /** Nombre de usuario único. */
  username: string;
  /** Contraseña en claro; el servicio la guarda solo como hash bcrypt. */
  password: string;
}

/** Cuerpo de `POST /api/auth/login`. */
export interface LoginDTO {
  /** Nombre de usuario. */
  username: string;
  /** Contraseña en claro, que se compara con el hash guardado. */
  password: string;
}
