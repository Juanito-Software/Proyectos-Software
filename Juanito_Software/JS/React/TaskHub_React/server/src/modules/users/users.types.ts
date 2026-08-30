export const USER_ROLES = ['user', 'admin'] as const;
export type UserRole = (typeof USER_ROLES)[number];

export function isUserRole(value: unknown): value is UserRole {
  return typeof value === 'string' && (USER_ROLES as readonly string[]).includes(value);
}

export interface User {
  id: string;
  username: string;
  passwordHash: string;
  role: UserRole;
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
