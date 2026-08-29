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
  fs.rmSync(clientOut, { recursive: true, force: true });
  fs.cpSync(clientBuild, clientOut, { recursive: true });
  console.log('cliente    -> dist/client');
} else {
  console.log('cliente    -> omitido (no hay client/dist; compílalo con npm run build en client/)');
}
