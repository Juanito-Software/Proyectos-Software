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
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.{js,jsx}'],
      exclude: ['src/main.jsx', 'src/test/**', 'src/constants.js'],
      /**
       * Umbrales fijados POR DEBAJO de la cobertura medida hoy (~36% de
       * sentencias, ~43% de ramas). No son un objetivo, son un suelo: su
       * única función es que la cobertura no baje sin que nadie se entere.
       *
       * Están así de bajos a propósito. Lo cubierto es la capa de servicios
       * (96%) y los dos componentes de tarea (100% y 86%), que es donde los
       * fallos rompen cosas de verdad. Lo que queda a cero —App, AuthForm,
       * TaskList y AuthContext— necesita montar el contexto de sesión, y se
       * cubrirá en el siguiente paso.
       *
       * SUBIR estos números conforme se añadan tests. Un umbral inalcanzable
       * acaba desactivándose, que es peor que no tenerlo.
       */
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
