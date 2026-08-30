import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Copia a dist/ lo que tsc no toca: el playground y el build del cliente.
 *
 * Está en un script aparte y no en un -e "..." dentro de package.json porque
 * las comillas anidadas se comportan distinto en cmd, PowerShell y bash, y el
 * comando acababa fallando solo en algunos entornos.
 */
const here = path.dirname(fileURLToPath(import.meta.url));
const serverDir = path.join(here, '..');

// 1. Playground: src/public -> dist/public
const playgroundSrc = path.join(serverDir, 'src', 'public');
const playgroundOut = path.join(serverDir, 'dist', 'public');
fs.cpSync(playgroundSrc, playgroundOut, { recursive: true });
console.log('playground -> dist/public');

// 2. Cliente React: client/dist -> dist/client
//
// Si no está compilado no se corta el build: el servidor funciona igual y
// simplemente no sirve la aplicación, que es lo que pasa en desarrollo.
const clientBuild = path.join(serverDir, '..', 'client', 'dist');
const clientOut = path.join(serverDir, 'dist', 'client');

if (fs.existsSync(clientBuild)) {
  // Se limpia antes de copiar para no acumular assets de builds anteriores:
  // Vite les pone un hash en el nombre, así que cada compilación deja
  // ficheros nuevos y los viejos se quedarían ahí para siempre.
  //
  // Si el borrado falla —un fichero bloqueado por un antivirus o por un
  // editor abierto, cosa habitual en Windows— no se corta el build: se copia
  // encima y como mucho sobra basura antigua, que no rompe nada.
  try {
    fs.rmSync(clientOut, { recursive: true, force: true });
  } catch (err) {
    console.warn(`aviso      -> no se pudo limpiar dist/client (${err.code}); se copia encima`);
  }

  fs.cpSync(clientBuild, clientOut, { recursive: true, force: true });
  console.log('cliente    -> dist/client');
} else {
  console.log('cliente    -> omitido (no hay client/dist; compílalo con npm run build en client/)');
}
