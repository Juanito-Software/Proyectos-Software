import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';

/**
 * Configuración única para todo el proyecto: el servidor en TypeScript y el
 * cliente en JSX tienen reglas distintas, pero un solo fichero evita que las
 * dos configuraciones se desincronicen.
 *
 * El criterio es que el linter señale errores reales, no cuestiones de estilo:
 * el formato no rompe nada en producción y discutirlo en cada revisión gasta
 * atención que hace falta en otro sitio.
 */
export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/coverage/**', // informes generados, no código fuente
      'server/src/public/**', // playground: HTML de una pieza, no es un módulo
    ],
  },

  // ── Servidor: TypeScript ───────────────────────────────────────────────
  {
    files: ['server/src/**/*.ts'],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: { ecmaVersion: 2022, sourceType: 'module' },
      globals: { ...globals.node },
    },
    plugins: { '@typescript-eslint': tseslint.plugin },
    rules: {
      ...js.configs.recommended.rules,
      ...tseslint.configs.recommended.rules,

      // La versión base no entiende tipos ni sobrecargas: en TypeScript hay
      // que apagarla y usar la del plugin, o marca falsos positivos.
      'no-unused-vars': 'off',

      // Las variables sin usar suelen ser restos de un refactor a medias. Se
      // permite el prefijo _ para los parámetros que Express obliga a declarar
      // aunque no se usen, como el `next` de los manejadores de error.
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],

      // `any` desactiva el tipado justo donde más falta hace.
      '@typescript-eslint/no-explicit-any': 'error',

      // Una promesa sin await en un manejador de Express hace que el error se
      // pierda: no llega al middleware y el cliente se queda esperando.
      'no-floating-decimal': 'off',
      'require-await': 'off',

      'no-console': 'off', // el logging del servidor va por consola a propósito
      eqeqeq: ['error', 'always'],
      'no-var': 'error',
      'prefer-const': 'error',
    },
  },

  // ── Cliente: React ─────────────────────────────────────────────────────
  {
    files: ['client/src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: { ...globals.browser },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: { 'react-hooks': reactHooks },
    rules: {
      ...js.configs.recommended.rules,

      // Las dos reglas que de verdad importan en React: usar hooks solo donde
      // se puede, y declarar todas las dependencias de un efecto. La segunda
      // caza bugs de estado obsoleto que son difíciles de reproducir a mano.
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',

      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      eqeqeq: ['error', 'always'],
      'no-var': 'error',
      'prefer-const': 'error',
    },
  },

  // ── Ficheros de test del cliente ───────────────────────────────────────
  {
    files: ['client/src/**/*.test.{js,jsx}', 'client/src/test/**/*.js'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node, // `global` al sustituir fetch en los tests
        ...globals.vitest, // describe, it, expect, vi…
      },
    },
    rules: {
      // En un test es normal preparar datos que no se usan en todas las
      // aserciones, y la consola sirve para depurar cuando algo falla.
      'no-console': 'off',
    },
  },

  // ── Suite de verificación ──────────────────────────────────────────────
  {
    files: ['server/src/verify.ts'],
    rules: {
      // La suite hace muchas comprobaciones con datos de forma flexible; no
      // merece la pena tipar cada respuesta intermedia.
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
];
