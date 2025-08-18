/**  Copyright (C) 2025 Juanito Software
 * 
 Este programa está protegido por una Licencia de Uso No Comercial.
 Puedes utilizarlo y compartirlo de forma gratuita, siempre que no se modifique
 y se incluya este aviso completo.

 Queda prohibido su uso con fines comerciales, así como su modificación,
 ingeniería inversa o redistribución alterada.

 Este software se proporciona “tal cual”, sin garantía de ningún tipo, ya sea
 expresa o implícita, incluyendo, pero no limitado a, garantías de comerciabilidad
 o idoneidad para un propósito particular.

 Para más detalles, consulta el archivo LICENSE.txt incluido con este programa
 o contacta a bernaldezperedaj@gmail.com.
*/

// Proyecto: Unified Chat Widget para OBS (Twitch + YouTube + Kick)
// Requisitos: Node.js, OBS, credenciales API

// Estructura del proyecto:
// unified-chat-widget/
// ├── libs/
// |   └── kick-js
// ├── utils/
// |   └── saveMessage.js
// ├── package.json
// ├── .env
// ├── index.js
// ├── services/
// │   ├── twitch.js
// │   ├── youtube.js
// │   └── kick.js
// ├── public/
// │   └── chat.html
// └── messages/
//     └── latest.json

// Paso 1: package.json (dependencias)
// Ejecuta: npm init -y && npm install express tmi.js dotenv axios @pagoru/kick_live_ws

// index.js (main server)
import 'dotenv/config';
import express from 'express';
import { connectKick } from './services/kick.js';
import { connectYouTube } from './services/youtube.js';
import { connectTwitch } from './services/twitch.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import * as fsp from 'fs/promises';
import { WebSocketServer } from 'ws';
import http from 'http';
import axios from 'axios';

let ttsEnabled = true;
const TTS_ADMINS = ['juanitocanuto', 'ameloblastos'];

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
app.use(express.json());
app.use(express.static(join(__dirname, 'public')));
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

const messagesDir = join(__dirname, 'messages');
if (!fs.existsSync(messagesDir)) {
  fs.mkdirSync(messagesDir, { recursive: true });
}

const messagesFile = join(messagesDir, 'latest.json');
if (!fs.existsSync(messagesFile)) {
  fs.writeFileSync(messagesFile, '[]', 'utf-8');
}

/* -------------------------
   Helpers: normalización / parsing
   - elimina caracteres zero-width
   - obtiene autor/texto con fallbacks
   - detecta comando con tolerancia a prefijos
   ------------------------- */
const ZERO_WIDTH = /[\u200B-\u200D\uFEFF]/g;
function normUnicode(s) {
  return s == null ? '' : s.toString().normalize('NFKC').replace(ZERO_WIDTH, '');
}
function getAuthor(msg) {
  // fallbacks comunes
  const candidate = msg.user ?? msg.username ?? msg.author?.name ?? msg.author?.username ?? msg.displayName ?? '';
  return normUnicode(candidate).toLowerCase().trim();
}
function getText(msg) {
  // soporta varios esquemas (twitch: message, yt: text, kick: content...)
  const candidate = msg.message ?? msg.text ?? msg.content ?? msg.body ?? '';
  return normUnicode(candidate).trim();
}
function isAdmin(name) {
  if (!name) return false;
  return TTS_ADMINS.some(a => a.toLowerCase() === name.toLowerCase());
}
/**
 * parseCommand(text)
 * devuelve { isCommand: bool, token: string|null, cmd: string|null }
 * token = primer "palabra" tal cual (con prefijo si existe)
 * cmd = token sin prefijos (/ ! - \) y en mayúsculas
 */
function parseCommand(text) {
  if (!text) return { isCommand: false, token: null, cmd: null };
  const t = text.trim();
  if (t === '') return { isCommand: false, token: null, cmd: null };
  const token = t.split(/\s+/)[0]; // primer "word"
  // detecta si empieza por uno de los prefijos comunes
  const hasPrefix = /^[\/!\\-]/.test(token);
  if (!hasPrefix) return { isCommand: false, token: null, cmd: null };
  const cmd = token.replace(/^[/!\\-]+/, '').toUpperCase();
  return { isCommand: true, token, cmd };
}

/* -------------------------
   WebSocket / HTTP server
   ------------------------- */
const wss = new WebSocketServer({ noServer: true });
const clients = new Set();

server.on('upgrade', (request, socket, head) => {
  const { url } = request;
  if (url === '/message') {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

wss.on('connection', (ws) => {
  clients.add(ws);
  console.log('🔌 Cliente WebSocket conectado');

  ws.on('close', () => {
    clients.delete(ws);
    console.log('❌ Cliente WebSocket desconectado');
  });

  ws.on('error', (error) => {
    console.error(`❌ Error en WebSocket: ${error.message}`);
  });
});

function broadcastMessage(messageObj) {
  const data = JSON.stringify(messageObj);
  for (const client of clients) {
    if (client.readyState === client.OPEN) {
      try {
        client.send(data);
      } catch (err) {
        console.error('Error enviando a cliente WS:', err.message);
      }
    }
  }
}

// Envía un mensaje tipo "sistema" al widget/chat (se guarda + broadcast)
// ahora acepta opcionalmente la platform original para que el overlay no lo filtre.
function sendSystemMessage(text, platform = 'system') {
  const systemMsg = {
    platform: platform || 'system',   // importante: mantener la platform esperada por el cliente
    user: 'Sistema',
    username: 'Sistema',
    message: text,
    system: true,
    received_at: new Date().toISOString()
  };

  // Persistir en latest.json y delegar el broadcast a saveAndBroadcastMessage
  saveAndBroadcastMessage(systemMsg).catch(err => {
    console.error('DEBUG: error saving systemMsg:', err);
  });
}



function sendToTTS(message) {
  axios.post('http://localhost:5002/speak', { text: message })
    .catch((err) => {
      console.error('❌ Error TTS:', err?.message ?? err);
    });
}

export async function saveAndBroadcastMessage(message) {
  try {
    let messages = [];
    try {
      const data = await fsp.readFile(messagesFile, 'utf-8');
      messages = JSON.parse(data || '[]');
    } catch (err) {
      if (err.code !== 'ENOENT') console.error('Error leyendo latest.json:', err);
    }

    const newMessages = [...messages.slice(-99), message];
    await fsp.writeFile(messagesFile, JSON.stringify(newMessages, null, 2), 'utf-8');
    broadcastMessage(message);
  } catch (err) {
    console.error('Error en saveAndBroadcastMessage:', err);
  }
}

/* -------------------------
   handleMessage: robusto y con debug
   ------------------------- */
function handleMessage(msg) {
  try {
    // Normalizar autor y texto
    const autor = getAuthor(msg);            // siempre minúsculas
    const texto = getText(msg);              // texto normalizado
    const tokenInfo = parseCommand(texto);   // detección de comando

    // DEBUG: muestra exactamente lo que llega
    console.log('DEBUG handleMessage:', {
      platform: msg.platform ?? 'unknown',
      rawUser: msg.user ?? msg.username,
      autor,
      texto,
      token: tokenInfo.token,
      cmd: tokenInfo.cmd,
      ttsEnabled
    });

    // --- comandos TTS ---
    if (tokenInfo.isCommand && tokenInfo.cmd === 'TTS_OFF') {
      if (isAdmin(autor)) {
        ttsEnabled = false;
        console.log(`🔇 TTS desactivado por ${autor}`);
        sendSystemMessage(`TTS desactivado por ${autor}`, msg.platform || 'system');
      } else {
        console.log(`⛔ ${autor} intentó usar TTS_OFF sin permiso`);
        sendSystemMessage(`⛔ ${autor} intentó usar TTS_OFF sin permiso`, msg.platform || 'system');
      }
      // No guardamos ni leemos comandos
      return;
    }

    if (tokenInfo.isCommand && tokenInfo.cmd === 'TTS_ON') {
      if (isAdmin(autor)) {
        ttsEnabled = true;
        console.log(`🔊 TTS activado por ${autor}`);
        sendSystemMessage(`TTS activado por ${autor}`, msg.platform || 'system');
      } else {
        console.log(`⛔ ${autor} intentó usar TTS_ON sin permiso`);
        sendSystemMessage(`⛔ ${autor} intentó usar TTS_ON sin permiso`, msg.platform || 'system');
      }
      return;
    }

    // Guardar y difundir (guardamos siempre el mensaje normalizado)
    const mensajeParaGuardar = {
      ...msg,
      user: autor || msg.user || msg.username,
      message: texto,
      received_at: new Date().toISOString()
    };
    saveAndBroadcastMessage(mensajeParaGuardar);

    // Si es comando diferente, no se leerá (ya parseado). Solo leer si TTS activado y no es comando
    if (ttsEnabled && !tokenInfo.isCommand) {
      // usa msg.username si existe para lectura más natural; si no, usamos autor
      const who = msg.username || msg.user || autor || 'alguien';
      const textoParaLeer = `${who} dijo: ${texto}`;
      console.log('TTS ▶', textoParaLeer);
      sendToTTS(textoParaLeer);
    }
  } catch (err) {
    console.error('Error en handleMessage:', err);
  }
}

/* -------------------------
   Iniciar conexiones a plataformas
   ------------------------- */
async function iniciarChats() {
  console.log('🔄 Iniciando conexiones de chat...');

  const conexiones = [
    { nombre: 'Kick', conectar: connectKick },
    { nombre: 'YouTube', conectar: connectYouTube },
    { nombre: 'Twitch', conectar: connectTwitch },
  ];

  const resultados = await Promise.allSettled(
    conexiones.map(({ conectar }) => conectar(handleMessage))
  );
  console.log('✅ Chats inicializados');

  resultados.forEach((resultado, i) => {
    const { nombre } = conexiones[i];
    if (resultado.status === 'fulfilled') {
      console.log(`✅ Conectado a ${nombre}`);
    } else {
      console.error(`❌ Error al conectar a ${nombre}:`, resultado.reason);
    }
  });
}

iniciarChats();
server.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en http://127.0.0.1:${PORT}`);
});