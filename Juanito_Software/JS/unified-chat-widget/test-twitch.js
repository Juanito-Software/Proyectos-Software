import dotenv from 'dotenv';
dotenv.config();
import tmi from 'tmi.js';

// Se informa de si cada variable esta definida, nunca de su valor.
//
// Antes se imprimia el token de OAuth completo por consola. Ese token da
// control sobre la cuenta de Twitch, y una vez escrito en la salida queda en el
// historial del terminal y en el log de cualquier sistema que ejecute el
// script. Para saber si el .env carga correctamente basta con saber si la
// variable existe y cuanto mide; el valor no aporta nada al diagnostico.
function estado(nombre) {
  const valor = process.env[nombre];
  if (!valor) return "NO DEFINIDA";
  return `definida (${valor.length} caracteres)`;
}

console.log("TWITCH_USERNAME:", estado("TWITCH_USERNAME"));
console.log("TWITCH_OAUTH_TOKEN:", estado("TWITCH_OAUTH_TOKEN"));
console.log("TWITCH_CHANNEL:", estado("TWITCH_CHANNEL"));

const client = new tmi.Client({
  options: { debug: true },
  identity: {
    username: process.env.TWITCH_USERNAME,
    password: process.env.TWITCH_OAUTH_TOKEN
  },
  channels: [process.env.TWITCH_CHANNEL]
});

client.connect()
  .then(() => console.log("CONEXIÓN OK"))
  .catch(err => console.log("ERROR EN CONEXIÓN:", err));
