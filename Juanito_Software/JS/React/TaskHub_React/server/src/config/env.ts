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

/**
 * Convierte "15m", "7d", "30s" o "12h" a milisegundos.
 *
 * Hace falta porque el mismo valor se usa en tres sitios que esperan formatos
 * distintos: jsonwebtoken acepta la cadena tal cual, pero la fecha de
 * caducidad que se guarda en la tabla de sesiones necesita un Date, y el
 * `maxAge` de la cookie necesita milisegundos. Tenerlo en un solo sitio evita
 * que los tres se desincronicen.
 */
export function ttlEnMilisegundos(valor: string): number {
  const m = /^(\d+)\s*(s|m|h|d)$/.exec(valor.trim());
  if (!m) {
    throw new Error(
      `Duración inválida: "${valor}". Se espera un número seguido de s, m, h o d (por ejemplo "15m").`,
    );
  }
  const cantidad = Number(m[1]);
  const factor = { s: 1000, m: 60_000, h: 3_600_000, d: 86_400_000 }[m[2] as 's' | 'm' | 'h' | 'd'];
  return cantidad * factor;
}

/**
 * Duración del token de acceso.
 *
 * Corta a propósito. Un JWT firmado sigue siendo criptográficamente válido
 * hasta que caduca, aunque se revoque la sesión en la base de datos: no hay
 * forma de retirarlo sin consultar una lista negra en cada petición, que es
 * justo el coste que este diseño evita. La respuesta correcta no es una lista
 * negra sino que la ventana sea pequeña, y quince minutos lo es.
 */
const accessTokenTtl = required('ACCESS_TOKEN_TTL', '15m');

/**
 * Duración del token de refresco.
 *
 * Siete días, los mismos que duraba el token único anterior, para que la
 * sesión del usuario no se acorte con este cambio. La diferencia es que ahora
 * sí se puede revocar: vive en la base de datos y el logout lo invalida.
 */
const refreshTokenTtl = required('REFRESH_TOKEN_TTL', '7d');

/**
 * Margen de tolerancia para rotaciones simultáneas.
 *
 * Con rotación estricta, dos peticiones que salgan a la vez con el mismo token
 * de refresco —dos pestañas, o la aplicación y el playground abiertos— harían
 * que la segunda pareciera una reutilización maliciosa y se revocara la sesión
 * entera. Dentro de este margen la segunda se rechaza sin matar la familia, y
 * el cliente reintenta con la cookie ya rotada.
 *
 * Es un compromiso explícito: estrecha la detección de reutilización en esos
 * segundos a cambio de no echar a la calle a un usuario legítimo. Un atacante
 * que reproduzca un token robado lo hará mucho después.
 */
const refreshGraceMs = Number(required('REFRESH_GRACE_SECONDS', '10')) * 1000;

export const env = {
  nodeEnv,
  port: Number(required('PORT', '3001')),
  jwtSecret: resolveJwtSecret(),
  accessTokenTtl,
  accessTokenTtlMs: ttlEnMilisegundos(accessTokenTtl),
  refreshTokenTtl,
  refreshTokenTtlMs: ttlEnMilisegundos(refreshTokenTtl),
  refreshGraceMs,
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
