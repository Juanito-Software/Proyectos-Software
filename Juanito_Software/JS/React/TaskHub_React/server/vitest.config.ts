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
        // `app.ts` es cableado de Express —helmet, la CSP, los estáticos, el
        // montaje de rutas—, la misma categoría que los routers: no se puede
        // ejercitar sin levantar el servidor, y quien lo levanta es
        // `npm run verify`. Los `*.types.ts` son solo declaraciones, sin
        // código que ejecutar.
        'src/app.ts',
        'src/**/*.types.ts',
      ],
      /**
       * Umbrales como trinquete, igual que en el cliente.
       *
       * Qué mide este número y qué no: **solo la lógica que corre sin base de
       * datos**. Los repositorios, los routers y el cableado de Express están
       * excluidos arriba y los ejercita `npm run verify` con 130 comprobaciones
       * contra PostgreSQL real. Un 99% aquí no significa «el servidor entero
       * está probado al 99%»; significa que de la lógica pura no queda casi
       * nada sin tocar.
       *
       * Va justo por debajo de lo real (99,54 / 98,95 / 98,73 / 99,51), que es
       * como debe funcionar un trinquete: si alguien añade una rama y no la
       * cubre, el CI se pone rojo en lugar de dejarla pasar en silencio.
       *
       * Lo que queda fuera son cuatro ramas defensivas que no se pueden forzar
       * desde el exterior sin retorcer los dobles hasta que el test deje de
       * significar nada: un `if` de guarda en `auth.controller`, dos ramas de
       * normalización en los validadores y una en `password-policy`. Queda
       * anotado por si algún día se encuentra la manera de llegar a ellas.
       *
       * Un aviso para quien suba estos números: **el 100% no es el objetivo**.
       * Llegar al último punto obliga a escribir tests que existen para mover
       * el contador, no para detectar fallos, y esos son peores que la línea
       * sin cubrir que sustituyen.
       */
      thresholds: {
        statements: 99,
        branches: 98,
        functions: 98,
        lines: 99,
      },
    },
  },
});
