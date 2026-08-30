import { env } from './env.js';
import { usersRepository } from '../modules/users/users.repository.js';

const MIN_ADMIN_PASSWORD_LENGTH = 12;

/**
 * Crea el administrador a partir de las variables de entorno.
 *
 * Es la única vía para conseguir el rol admin: el registro público siempre
 * crea usuarios normales y no hay ningún endpoint que promueva a nadie. Quien
 * controla las variables de entorno del despliegue controla quién administra,
 * que es exactamente donde debe estar esa decisión.
 *
 * Se ejecuta en cada arranque y es idempotente: si el usuario ya existe, se
 * asegura de que siga siendo admin y actualiza su contraseña a la configurada.
 * Eso convierte un redespliegue en la forma de recuperar el acceso si se
 * pierde la contraseña, sin tocar la base de datos a mano.
 */
export async function seedAdmin(): Promise<void> {
  const { adminUsername, adminPassword } = env;

  if (!adminUsername || !adminPassword) {
    // Sin configuración no hay administrador, y es una situación válida: la
    // aplicación funciona igual, simplemente nadie puede administrar.
    return;
  }

  if (adminPassword.length < MIN_ADMIN_PASSWORD_LENGTH) {
    throw new Error(
      `ADMIN_PASSWORD debe tener al menos ${MIN_ADMIN_PASSWORD_LENGTH} caracteres. ` +
        'Es la cuenta con más permisos de la aplicación: no arranco con una contraseña débil.',
    );
  }

  const admin = await usersRepository.upsertAdmin(adminUsername, adminPassword);
  console.log(`Administrador listo: ${admin.username}`);
}
