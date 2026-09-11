import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: false,
    setupFiles: ['./src/tests/setup.ts'],
    include: ['src/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      // Todo src/, no solo services/ y utils/. Con el filtro anterior el
      // informe daba un 81 % mientras middlewares, controladores y rutas estaban
      // al 0 %: la cifra medía la parte cubierta y callaba el resto.
      include: ['src/**'],
      exclude: ['src/tests/**', 'src/server.ts'],
    },
  },
});
