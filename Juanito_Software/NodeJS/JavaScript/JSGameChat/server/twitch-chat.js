/**
 * Módulo opcional: escucha el chat de Twitch y reenvía comandos al juego vía Socket.io.
 * Configuración: variables de entorno o archivo .env
 *   TWITCH_CHANNEL=tu_canal
 *   TWITCH_USER=tu_bot_o_cuenta
 *   TWITCH_OAUTH=oauth:xxx  (generar en https://twitchapps.com/tmi/)
 */

const tmi = require('tmi.js');

// Comandos que el chat puede usar → se envían al juego con el mismo nombre de evento
const COMANDOS = {
  '!jump': 'playerJump',
  '!salta': 'playerJump',
  '!left': 'moveLeft',
  '!izquierda': 'moveLeft',
  '!right': 'moveRight',
  '!derecha': 'moveRight',
  '!attack': 'attack',
  '!ataca': 'attack',
  '!vote izquierda': 'vote',
  '!vote derecha': 'vote',
  '!vote': 'vote',
};

function parseVote(message) {
  const m = message.trim().toLowerCase();
  if (m.includes('izquierda')) return { option: 'izquierda' };
  if (m.includes('derecha')) return { option: 'derecha' };
  return { option: null };
}

function start(serverExports) {
  const { broadcastToGame } = serverExports;
  const channel = process.env.TWITCH_CHANNEL || 'tu_canal';
  const username = process.env.TWITCH_USER || 'tu_bot';
  const oauth = process.env.TWITCH_OAUTH || '';

  if (!oauth || oauth === '') {
    console.warn('[Twitch] No hay TWITCH_OAUTH. Chat desactivado. Usa .env o variables de entorno.');
    return;
  }

  const client = new tmi.Client({
    options: { debug: false },
    connection: { reconnect: true },
    identity: { username, password: oauth },
    channels: [channel],
  });

  client.connect().then(() => {
    console.log('[Twitch] Conectado al canal:', channel);
  }).catch((err) => {
    console.error('[Twitch] Error al conectar:', err.message);
  });

  client.on('message', (channel, tags, message, self) => {
    if (self) return;
    const msg = message.trim().toLowerCase();

    for (const [cmd, eventName] of Object.entries(COMANDOS)) {
      if (!msg.startsWith(cmd)) continue;
      const data = { user: tags['display-name'] || tags.username };
      if (eventName === 'vote') Object.assign(data, parseVote(message));
      broadcastToGame(eventName, data);
      break;
    }
  });
}

module.exports = { start };
