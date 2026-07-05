// debug-env.js
import 'dotenv/config';
console.log('TWITCH_USERNAME=', process.env.TWITCH_USERNAME);
console.log('TWITCH_CHANNEL=', process.env.TWITCH_CHANNEL);
console.log('TWITCH_OAUTH_TOKEN=', (process.env.TWITCH_OAUTH_TOKEN || '').slice(0,12) + '...'); // mostrando sólo inicio
