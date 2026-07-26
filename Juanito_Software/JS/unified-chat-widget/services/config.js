// services/config.js
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Cargar .env
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// ==========================
//   VARIABLES GENERALES
// ==========================
export const PORT = process.env.PORT || 3000;

// ==========================
//        YOUTUBE
// ==========================
export const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
export const YOUTUBE_CHANNEL_ID = process.env.YOUTUBE_CHANNEL_ID;

// ==========================
//          KICK
// ==========================
export const KICK_CHANNEL = process.env.KICK_CHANNEL;
export const KICK_BEARER_TOKEN = process.env.KICK_BEARER_TOKEN;
export const KICK_COOKIES = process.env.KICK_COOKIES;

// ==========================
//         RUMBLE
// ==========================
export const RUMBLE_API_URL = process.env.RUMBLE_API_URL;
export const RUMBLE_CHANNEL = process.env.RUMBLE_CHANNEL;
export const RUMBLE_STREAM_URL = process.env.RUMBLE_STREAM_URL; // URL opcional del stream específico
export const RUMBLE_SERVER_URL = process.env.RUMBLE_SERVER_URL || 'http://localhost:5003';
export const RUMBLE_POLL_INTERVAL = parseInt(process.env.RUMBLE_POLL_INTERVAL || '3000', 10);

// ==========================
//         TWITCH
//  (modo multi-cuentas)
// ==========================
export function loadTwitchAccounts() {
  const total = parseInt(process.env.TWITCH_ACCOUNTS || "2", 10);
  const accounts = [];

  for (let i = 1; i <= total; i++) {
    const prefix = `TWITCH_${i}`;

    const acc = {
      username: process.env[`${prefix}_USERNAME`],
      channel: process.env[`${prefix}_CHANNEL`],
      oauth: process.env[`${prefix}_OAUTH`],
      clientId: process.env[`${prefix}_CLIENT_ID`]
    };

    if (!acc.username || !acc.channel || !acc.oauth) {
      console.warn(`⚠️ Twitch account ${i} está incompleta y será ignorada`);
      continue;
    }

    accounts.push(acc);
  }

  return accounts;
}
