import { defineConfig } from 'vitest/config';

/**
 * Tests unitarios del servidor: solo lógica pura, sin base de datos ni
 * servidor HTTP. Lo que necesita Postgres vive en `npm run verify`, que es
 * otra cosa y se ejecuta en su propio job de CI.
 *
 * La ventaja de separarlos es que estos corren en milisegundos y en cualquier
 * máquina sin nada instalado, así que se pueden lanzar constantemente mientras
 * se programa.
 */
export default defineConfig({
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.ts'],
      // Se excluye lo que no es lógica pura: la suite end-to-end, la
      // configuración, los routers y todo lo que solo habla con la base de
      // datos. Medir su cobertura aquí daría un número engañoso, porque quien
      // los ejercita es `npm run verify`.
      exclude: [
        'src/verify.ts',
        'src/server.ts',
        'src/config/**',
        'src/**/*.router.ts',
        'src/**/*.repository.ts',
        'src/types/**',
      ],
    },
  },
});
