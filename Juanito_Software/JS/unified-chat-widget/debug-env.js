// debug-env.js
//
// Comprueba que el fichero .env se esta cargando.
//
// Se informa de si cada variable esta definida y de su longitud, nunca de su
// valor. La version anterior imprimia los primeros 12 caracteres del token de
// OAuth: es menos que el token entero, pero sigue siendo material secreto que
// queda en el historial del terminal y en el log de quien ejecute esto. Para
// diagnosticar si el .env carga, el valor no hace falta.
import 'dotenv/config';

const VARIABLES = [
  'TWITCH_USERNAME',
  'TWITCH_CHANNEL',
  'TWITCH_OAUTH_TOKEN',
];

for (const nombre of VARIABLES) {
  const valor = process.env[nombre];
  console.log(
    `${nombre}=`,
    valor ? `definida (${valor.length} caracteres)` : 'NO DEFINIDA'
  );
}
