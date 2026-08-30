import 'dotenv/config';

function required(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (value === undefined) {
    throw new Error(`Falta la variable de entorno obligatoria: ${name}`);
  }
  return value;
}

export const env = {
  nodeEnv: required('NODE_ENV', 'development'),
  port: Number(required('PORT', '3001')),
  jwtSecret: required('JWT_SECRET', 'clave-secreta-desarrollo-cambiar-en-produccion'),
  jwtExpiresIn: required('JWT_EXPIRES_IN', '7d'),
  // Sin valor por defecto a propósito: es preferible que la aplicación no
  // arranque a que apunte en silencio a una base de datos equivocada.
  databaseUrl: required('DATABASE_URL'),

  // Semilla del administrador. Opcionales: si no están, la aplicación arranca
  // sin ningún admin, que es lo correcto por defecto. El rol solo se concede
  // desde aquí, nunca a través de la API.
  adminUsername: process.env.ADMIN_USERNAME?.trim() || null,
  adminPassword: process.env.ADMIN_PASSWORD || null,
} as const;

export const isProduction = env.nodeEnv === 'production';
