import { defineConfig, devices } from '@playwright/test';

/**
 * Salvaguarda: estos tests crean usuarios y borran datos de verdad, así que
 * no pueden apuntar a la base de datos de producción.
 *
 * Pasó: al tener el .env local apuntando a Neon, una tanda de ejecuciones dejó
 * decenas de usuarios `e2e-*` en la base de datos desplegada. No rompió nada
 * por suerte, pero uno de los tests elimina usuarios.
 *
 * Se aborta si la cadena de conexión parece gestionada. Para saltárselo a
 * propósito —por ejemplo en un entorno de pruebas remoto— basta con definir
 * E2E_ALLOW_REMOTE_DB=1.
 */
const url = process.env.DATABASE_URL ?? '';
const pareceProduccion = /neon\.tech|render\.com|supabase\.co|amazonaws\.com/.test(url);

if (pareceProduccion && process.env.E2E_ALLOW_REMOTE_DB !== '1') {
  throw new Error(
    'DATABASE_URL apunta a una base de datos gestionada y los tests end-to-end escriben datos reales.\n' +
      'Usa tu PostgreSQL local:\n' +
      '  set DATABASE_URL=postgresql://usuario:clave@localhost:5432/taskhub_e2e\n' +
      'Si de verdad quieres ejecutarlos contra esa base de datos, define E2E_ALLOW_REMOTE_DB=1.',
  );
}

/**
 * Tests end-to-end de navegador.
 *
 * Prueban la aplicación entera como la usa una persona: navegador real,
 * React montado, peticiones reales a Express y datos reales en Postgres. Es
 * la única capa que verifica que las tres partes encajan; los otros tests
 * comprueban cada una por separado.
 *
 * Requisitos: un Postgres accesible en DATABASE_URL y el proyecto compilado.
 * El `webServer` de abajo arranca el servidor y espera a que responda.
 */
export default defineConfig({
  testDir: './e2e',

  // Sin ejecución en paralelo: todos los tests comparten la misma base de
  // datos, y en paralelo se pisarían los datos entre ellos. Con esta cantidad
  // de tests, la velocidad no compensa la intermitencia.
  fullyParallel: false,
  workers: 1,

  // En CI, un `test.only` olvidado haría que el resto no se ejecutara y el
  // pipeline saldría verde sin haber probado casi nada.
  forbidOnly: !!process.env.CI,

  // Un reintento en CI absorbe la intermitencia propia de un entorno
  // compartido; en local, cero, para que un fallo se vea a la primera.
  retries: process.env.CI ? 1 : 0,

  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',

  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3001',
    // Solo se guardan rastro y captura cuando algo falla: si no, cada
    // ejecución dejaría cientos de megas de vídeo sin ningún valor.
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },

  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],

  // No se arranca el servidor si ya hay uno escuchando: así se puede depurar
  // con `npm run dev` abierto en otra terminal.
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: 'npm start --prefix server',
        url: 'http://localhost:3001/api/health',
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
        stdout: 'ignore',
        stderr: 'pipe',
      },
});
