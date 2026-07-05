import tmi from 'tmi.js';

export async function connectTwitchAccount(account, onMessage) {
  const { username, channel, oauth } = account;

  console.log(`🔧 [Twitch] Iniciando servicio para cuenta: ${username}`);

  if (!username || !channel || !oauth) {
    console.error(`❌ [Twitch] Credenciales incompletas para cuenta: ${username}`);
    throw new Error(`Credenciales incompletas para cuenta: ${username}`);
  }

  const client = new tmi.Client({
    options: { debug: true },
    identity: {
      username,
      password: oauth
    },
    channels: [channel.toLowerCase()]
  });

  try {
    await client.connect();
    console.log(`✅ [Twitch] Conectado correctamente: ${username} → #${channel}`);
  } catch (err) {
    const errorMsg = err.message || err.toString();
    console.error(`❌ [Twitch] Error conectando ${username} → #${channel}: ${errorMsg}`);
    throw err; // Propagar el error para que Promise.allSettled lo capture
  }

  client.on('message', (chan, tags, message, self) => {
    if (self) return;

    const formatted = {
      platform: 'twitch',
      account: username,
      channel,
      username: tags['display-name'] || tags.username || 'anon',
      message,
      timestamp: Date.now()
    };

    console.log(`💬 [Twitch] ${formatted.username}: ${formatted.message}`);
    onMessage(formatted);
  });

  client.on('disconnected', (reason) => {
    console.warn(`⚠️ [Twitch] Desconectado ${username}: ${reason}`);
  });

  client.on('notice', (channel, msgid, message) => {
    console.log(`ℹ️ [Twitch] Notice en ${channel}: ${message}`);
  });
}