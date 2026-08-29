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
} as const;

export const isProduction = env.nodeEnv === 'production';
