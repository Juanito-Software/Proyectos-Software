// services/config.js
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Carga la configuración sólo una vez
dotenv.config({ path: path.resolve(__dirname, '../.env') });

export const KICK_CHANNEL = process.env.KICK_CHANNEL;
export const KICK_BEARER_TOKEN = process.env.KICK_BEARER_TOKEN;
export const KICK_COOKIES = process.env.KICK_COOKIES;

export const TWITCH_CHANNEL = process.env.TWITCH_CHANNEL;
export const TWITCH_CLIENT_ID = process.env.TWITCH_CLIENT_ID;
export const TWITCH_OAUTH_TOKEN = process.env.TWITCH_OAUTH_TOKEN;

export const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
export const YOUTUBE_CHANNEL_ID = process.env.YOUTUBE_CHANNEL_ID;
