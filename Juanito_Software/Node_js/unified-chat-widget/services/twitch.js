import tmi from 'tmi.js';

export async function connectTwitchAccount(account, onMessage) {
  const { username, channel, oauth } = account;

  if (!username || !channel || !oauth) {
    console.error("❌ Credenciales de Twitch incompletas para esta cuenta", account);
    return;
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
    console.log(`✅ Conectado a Twitch: ${username} → #${channel}`);
  } catch (err) {
    console.error("❌ Error conectando a Twitch:", err);
    return;
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

    onMessage(formatted);
  });
}