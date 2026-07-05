import dotenv from 'dotenv';
dotenv.config();
import tmi from 'tmi.js';

console.log("USUARIO:", process.env.TWITCH_USERNAME);
console.log("TOKEN:", process.env.TWITCH_OAUTH_TOKEN);
console.log("CANAL:", process.env.TWITCH_CHANNEL);

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
