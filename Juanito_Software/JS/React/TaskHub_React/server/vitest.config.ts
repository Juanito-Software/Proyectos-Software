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
      /**
       * Umbrales como trinquete, igual que en el cliente.
       *
       * El número es **bajo a propósito** y no hay que leerlo como «el
       * servidor está mal probado». Lo que mide esta suite es solo la lógica
       * pura; todo lo que necesita base de datos —servicios, controladores,
       * repositorios— lo ejercita `npm run verify` con 130 comprobaciones
       * contra PostgreSQL real, y eso no aparece aquí.
       *
       * Aun así el umbral hace falta. Hasta ahora esta cobertura **no se medía
       * en ninguna parte**: el cliente tenía trinquete y el servidor no, así
       * que una rama nueva sin cubrir entraba sin que nada avisara. Vale más un
       * suelo modesto que se defiende que ninguno.
       *
       * Va justo por debajo de lo real (37,19 / 50,31 / 31,46 / 36,46). Cuando
       * suba, hay que subirlo.
       */
      thresholds: {
        statements: 36,
        branches: 49,
        functions: 30,
        lines: 35,
      },
    },
  },
});
