import tmi from 'tmi.js';
//import { addMessage, getMessages } from '../utils/globalMessages.js';
//import { appendLatestJson } from '../utils/saveMessage.js';
import { TWITCH_CHANNEL, TWITCH_CLIENT_ID, TWITCH_OAUTH_TOKEN } from './config.js';

const client = new tmi.Client({
  options: { debug: true },
  identity: {
    username: TWITCH_CLIENT_ID,
    password: TWITCH_OAUTH_TOKEN,
  },
  channels: [TWITCH_CHANNEL],
});

export async function connectTwitch(onMessage) {
  if (!TWITCH_CHANNEL || !TWITCH_CLIENT_ID || !TWITCH_OAUTH_TOKEN) {
    console.error("❌ Faltan credenciales Twitch en .env");
    return;
  }

  try {
    await client.connect();
    console.log("✅ Conectado a Twitch en canal:", TWITCH_CHANNEL);
  } catch (err) {
    console.error("❌ Error conectando a Twitch:", err);
  }

    client.on('message', (channel, tags, message, self) => {
    if (self) return;

    const formatted = {
      platform: 'twitch',
      username: tags['display-name'] || tags.username || 'anon',
      message: message,
      timestamp: Date.now()
    };
    onMessage(formatted);
    //addMessage(formatted);
    //appendLatestJson(getMessages());
  });
}
