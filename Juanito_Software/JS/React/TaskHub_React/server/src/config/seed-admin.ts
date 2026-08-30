import { env } from './env.js';
import { usersRepository } from '../modules/users/users.repository.js';
import { validarPassword, MIN_PASSWORD_LENGTH } from '../modules/auth/password-policy.js';

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

  // Se aplica la misma política que a cualquier usuario, y con más motivo:
  // es la cuenta con más permisos. Antes tenía su propio mínimo de 12, lo que
  // permitía que el administrador fuera más débil que un usuario normal en
  // cuanto la política general subiera.
  const resultado = validarPassword(adminPassword, adminUsername);
  if (!resultado.valida) {
    throw new Error(
      `ADMIN_PASSWORD no cumple la política de contraseñas: ${resultado.error}\n` +
        `Es la cuenta con más permisos de la aplicación, así que no se arranca con una débil. ` +
        `Mínimo ${MIN_PASSWORD_LENGTH} caracteres; una frase larga es la forma más cómoda de llegar.`,
    );
  }

  const admin = await usersRepository.upsertAdmin(adminUsername, adminPassword);
  console.log(`Administrador listo: ${admin.username}`);
}
