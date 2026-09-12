/**
 * Variables de entorno mínimas para que `config/env.ts` no lance al importarse
 * durante los tests. Se cargan antes de cualquier suite (ver vitest.config.ts).
 */
process.env.NODE_ENV = 'test';
process.env.PORT = '3000';
/**
 * `??=` y no `=`, y esta es la única línea del fichero donde la diferencia
 * importa.
 *
 * Los 162 tests con dobles no se conectan a ninguna base de datos, así que les
 * da igual lo que valga esta variable: solo necesitan que exista, porque
 * `config/env.ts` la valida al importarse. Pero db.repositories.test.ts sí se
 * conecta, y con `=` este fichero pisaría la URL real —la del servicio de
 * PostgreSQL en el CI, o la del PostgreSQL local— por una base «test» que no
 * existe. Los tests fallarían con un error de conexión y el servicio del
 * workflow no habría servido de nada.
 *
 * Con `??=` el valor de abajo es solo el respaldo para quien no define nada.
 */
process.env.DATABASE_URL ??= 'postgresql://test:test@localhost:5432/test';
process.env.JWT_SECRET = 'test-access-secret';
process.env.JWT_EXPIRES_IN = '15m';
process.env.JWT_REFRESH_SECRET = 'test-refresh-secret';
process.env.JWT_REFRESH_EXPIRES_IN = '7d';
process.env.CORS_ORIGIN = 'http://localhost:4200';
