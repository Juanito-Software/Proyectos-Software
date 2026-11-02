/**
 * Configuración de Vite (servidor de desarrollo y build) y de Vitest (tests).
 *
 * En desarrollo el cliente se sirve en el 5173 y todo lo que empieza por
 * `/api` se reenvía al servidor Express del 3001. Así el navegador ve un solo
 * origen: no hace falta relajar CORS y la cookie de refresco viaja sin más.
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
  // ── Tests (Vitest) ──────────────────────────────────────────────────────
  // jsdom simula el DOM del navegador; `globals` permite usar describe/it/expect
  // sin importarlos.
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.{js,jsx}'],
      exclude: ['src/main.jsx', 'src/test/**', 'src/constants.js'],
      // Umbrales mínimos de cobertura (`npm run test:coverage` falla si se
      // baja de ellos). No son un objetivo, son un suelo: su única función es
      // que la cobertura no baje sin que nadie se entere. SUBIRLOS conforme
      // se añadan tests; un umbral inalcanzable acaba desactivándose, que es
      // peor que no tenerlo.
      //
      // Los umbrales van justo por debajo de la cobertura real (96.95 / 95.93 /
      // 95.65 / 98.09) para que funcionen como trinquete: si un cambio la baja,
      // el CI se entera. Cuando suba, hay que volver a subirlos — un umbral muy
      // por debajo de lo real deja de proteger nada.
      thresholds: {
        statements: 95,
        branches: 94,
        functions: 93,
        lines: 96,
      },
    },
  },
});
