import 'dotenv/config';

function required(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (value === undefined) {
    throw new Error(`Falta la variable de entorno obligatoria: ${name}`);
  }
  return value;
}

const nodeEnv = required('NODE_ENV', 'development');
const isProd = nodeEnv === 'production';

/**
 * Secreto de firma de los tokens.
 *
 * En desarrollo hay un valor por defecto para que el proyecto arranque recién
 * clonado. En producción NO puede haberlo: ese valor está publicado en el
 * repositorio, así que cualquiera podría firmar un token válido para cualquier
 * usuario, administrador incluido. Si falta, es preferible que la aplicación
 * no arranque a que arranque siendo suplantable.
 */
const DEV_JWT_SECRET = 'clave-solo-para-desarrollo-no-usar-en-produccion';
const MIN_SECRET_LENGTH = 32;

function resolveJwtSecret(): string {
  const fromEnv = process.env.JWT_SECRET;

  if (!isProd) return fromEnv || DEV_JWT_SECRET;

  if (!fromEnv) {
    throw new Error(
      'JWT_SECRET es obligatoria en producción. Genérala con:\n' +
        '  node -e "console.log(require(\'crypto\').randomBytes(48).toString(\'hex\'))"',
    );
  }

  if (fromEnv === DEV_JWT_SECRET) {
    throw new Error(
      'JWT_SECRET tiene el valor de desarrollo, que es público. Genera uno propio para producción.',
    );
  }

  if (fromEnv.length < MIN_SECRET_LENGTH) {
    throw new Error(
      `JWT_SECRET debe tener al menos ${MIN_SECRET_LENGTH} caracteres en producción ` +
        `(tiene ${fromEnv.length}). Un secreto corto se puede romper por fuerza bruta.`,
    );
  }

  return fromEnv;
}

/**
 * Orígenes autorizados a llamar a la API desde un navegador.
 *
 * Se declaran en ALLOWED_ORIGINS separados por comas. En producción, si no se
 * declara ninguno, no se permite ningún origen externo: la aplicación y la API
 * se sirven desde el mismo dominio, así que el cliente propio funciona igual.
 */
function resolveAllowedOrigins(): string[] {
  const raw = process.env.ALLOWED_ORIGINS;
  if (raw) return raw.split(',').map((o) => o.trim()).filter(Boolean);

  // En desarrollo, Vite sirve el cliente en otro puerto y necesita permiso.
  return isProd ? [] : ['http://localhost:5173', 'http://localhost:3001'];
}

export const env = {
  nodeEnv,
  port: Number(required('PORT', '3001')),
  jwtSecret: resolveJwtSecret(),
  jwtExpiresIn: required('JWT_EXPIRES_IN', '7d'),
  allowedOrigins: resolveAllowedOrigins(),

  // Sin valor por defecto a propósito: es preferible que la aplicación no
  // arranque a que apunte en silencio a una base de datos equivocada.
  databaseUrl: required('DATABASE_URL'),

  // Semilla del administrador. Opcionales: si no están, la aplicación arranca
  // sin ningún admin, que es lo correcto por defecto. El rol solo se concede
  // desde aquí, nunca a través de la API.
  adminUsername: process.env.ADMIN_USERNAME?.trim() || null,
  adminPassword: process.env.ADMIN_PASSWORD || null,
} as const;

export const isProduction = isProd;
