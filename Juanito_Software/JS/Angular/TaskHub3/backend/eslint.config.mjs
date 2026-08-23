// Configuración de ESLint en formato "flat config", obligatorio desde
// ESLint 9 y única opción a partir de la 10.
// Sustituye al antiguo .eslintrc.*
import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: ['dist/**', 'node_modules/**', 'prisma/migrations/**'],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    rules: {
      // El proyecto usa console para el arranque del servidor
      'no-console': 'off',
      // Permite argumentos sin usar si empiezan por _
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
);
