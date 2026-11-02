/**
 * Tipos del dominio de usuarios: el registro completo de la base de datos y
 * las vistas recortadas que salen hacia el cliente.
 */

/** Roles posibles. La única fuente: el tipo `UserRole` se deriva de aquí. */
export const USER_ROLES = ['user', 'admin'] as const;
/** `'user' | 'admin'`. */
export type UserRole = (typeof USER_ROLES)[number];

/**
 * Comprueba si un valor desconocido (p. ej. leído de la base o de un token)
 * es un rol válido. Sirve también de guarda de tipo para TypeScript.
 *
 * @param value valor a comprobar
 * @returns `true` si es `'user'` o `'admin'`
 */
export function isUserRole(value: unknown): value is UserRole {
  return typeof value === 'string' && (USER_ROLES as readonly string[]).includes(value);
}

/**
 * Usuario tal como está en la tabla `users`. Contiene el hash de la
 * contraseña: **nunca** se envía al cliente; para eso está `PublicUser`.
 */
export interface User {
  /** UUID generado por PostgreSQL. */
  id: string;
  /** Nombre único con el que inicia sesión. */
  username: string;
  /** Hash bcrypt de la contraseña. */
  passwordHash: string;
  /** Rol del usuario. */
  role: UserRole;
  /** Fecha de alta en formato ISO 8601. */
  createdAt: string;
}

/**
 * Lo que sale hacia el cliente. Incluye el rol porque la interfaz necesita
 * saber si mostrar las opciones de administración — pero enseñarlas o no es
 * cosmética: quien decide de verdad es el middleware del servidor.
 */
export interface PublicUser {
  id: string;
  username: string;
  role: UserRole;
}

/** Ficha de usuario para el panel de administración. */
export interface AdminUserView extends PublicUser {
  createdAt: string;
  taskCount: number;
}
