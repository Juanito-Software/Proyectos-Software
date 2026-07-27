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

// Proyecto: Unified Chat Widget para OBS (Twitch + YouTube + Kick + Rumble)
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
// │   ├── kick.js
// │   └── rumble.js
// ├── public/
// │   └── chat.html
// └── messages/
//     └── latest.json

// Paso 1: package.json (dependencias)
// Ejecuta: npm init -y && npm install express tmi.js dotenv axios @pagoru/kick_live_ws

// index.js (main server)

import {
  loadTwitchAccounts,
  YOUTUBE_API_KEY,
  YOUTUBE_CHANNEL_ID,
  KICK_CHANNEL,
  KICK_BEARER_TOKEN,
  KICK_COOKIES,
  PORT
} from './services/config.js';

import express from 'express';
import { connectKick } from './services/kick.js';
import { connectYouTube } from './services/youtube.js';
import { connectTwitchAccount } from './services/twitch.js';
import { connectRumble } from './services/rumble.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import * as fsp from 'fs/promises';
import { WebSocketServer } from 'ws';
import http from 'http';
import axios from 'axios';
import rateLimit from 'express-rate-limit';

// -------------------
let ttsEnabled = true;
const TTS_ADMINS = ['juanitocanutos', 'juanitocanuto'];  // Nombres de usuario permitidos para comandos TTS
// -------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();

// Limite de peticiones.
//
// El widget lo consume la fuente de navegador de OBS, que sondea /messages cada
// pocos segundos, asi que el limite tiene que ser holgado. Su funcion aqui no es
// frenar abusos deliberados sino evitar que un cliente descontrolado —una
// pestaña recargando en bucle, un script mal hecho— sature el proceso, que es de
// un solo hilo y tambien atiende los websockets del chat.
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 600,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(express.json());
app.use(express.static(join(__dirname, 'public')));

const server = http.createServer(app);

// 👉 CORRECTO: usar PORT importado o 3000 si no existe
const finalPort = PORT || 3000;

// Asegura que el directorio y archivo de mensajes existen
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
// --- Objeto de comandos ---
const commands = {
  TTS_ON: (autor, msg) => {
    if (isAdmin(autor)) {
      ttsEnabled = true;
      console.log(`🔊 TTS activado por ${autor}`);
      sendSystemMessage(`TTS activado por ${autor}`, msg.platform || 'system');
      sendToTTS(`${autor} ha activado el TTS.`);
    } else {
      console.log(`⛔ ${autor} intentó usar TTS_ON sin permiso`);
      sendSystemMessage(`⛔ ${autor} intentó usar TTS_ON sin permiso`, msg.platform || 'system');
      sendToTTS(`Alerta de seguridad: ${autor} intentó activar el TTS sin permiso.`);
    }
  },
  TTS_OFF: (autor, msg) => {
    if (isAdmin(autor)) {
      ttsEnabled = false;
      console.log(`🔇 TTS desactivado por ${autor}`);
      sendSystemMessage(`TTS desactivado por ${autor}`, msg.platform || 'system');
      sendToTTS(`${autor} ha desactivado el TTS.`);
    } else {
      console.log(`⛔ ${autor} intentó usar TTS_OFF sin permiso`);
      sendSystemMessage(`⛔ ${autor} intentó usar TTS_OFF sin permiso`, msg.platform || 'system');
      sendToTTS(`Alerta de seguridad: ${autor} intentó desactivar el TTS sin permiso.`);
    }
  },
  SALUDO: (autor, msg) => {
      const platform = msg.platform || 'web'; // usar 'web' si no hay plataforma
      console.log(`¡Hola ${autor}! 👋`, platform);
      sendSystemMessage(`¡Hola ${autor}! 👋`, platform);
      sendToTTS(`¡Hola ${autor}!`);
  },
  HELP: (autor, msg) => {
      const platform = msg.platform || 'web';
      const comandosDisponibles = Object.keys(commands).join(', ');
      console.log(`Comandos disponibles para ${autor}: ${comandosDisponibles}`, platform);
      sendSystemMessage(`Comandos disponibles: ${comandosDisponibles}`, platform);
      sendToTTS(`Hola ${autor}, los comandos disponibles son: ${comandosDisponibles}`);
  }
};

// --- Función para parsear comandos ---
function parseCommand(text) {
  if (!text) return null;
  const token = text.trim().split(/\s+/)[0];
  const match = token.match(/^([!\\])(.+)/); // solo acepta ! o \
  if (!match) return null;
  return match[2].toUpperCase(); // devuelve solo el nombre del comando en mayúsculas
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

// Devuelve los últimos mensajes en JSON
app.get('/messages', apiLimiter, async (req, res) => {
  try {
    const data = await fsp.readFile(messagesFile, 'utf-8');
    const messages = JSON.parse(data || '[]');
    res.json(messages);
  } catch (err) {
    console.error('Error leyendo latest.json:', err);
    res.status(500).json({ error: 'No se pudo leer messages' });
  }
});


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

// ---------- TTS queue + sanitización (index.js) ----------

// Cola FIFO para TTS
const ttsQueue = [];
let ttsProcessing = false;

// Configurables
const TTS_MAX_LENGTH = 300;         // limitar texto enviado al TTS
const TTS_POST_TIMEOUT = 120000;    // 120s timeout para la petición al microservicio
const TTS_DELAY_BETWEEN = 300;      // ms entre audios (pequeña pausa)

// Sanitización ligera (normaliza, elimina caracteres cero-width y saltos de línea)
function sanitizeForTTS(s) {
  if (!s) return '';
  let t = normUnicode(s);
  t = t.replace(/[\r\n]+/g, ' ');         // unifica saltos de línea

  // Quita etiquetas HTML repitiendo hasta que no quede ninguna.
  //
  // Una sola pasada es burlable: en "<<span>script>" el replace elimina el
  // "<span>" del centro y el resultado es "<script>", que ya ha pasado el
  // filtro. Repetir hasta que el texto deje de cambiar cierra ese hueco.
  let anterior;
  do {
    anterior = t;
    t = t.replace(/<[^>]*>/g, '');
  } while (t !== anterior);

  // Y se eliminan los signos de mayor/menor sueltos que hayan sobrevivido,
  // para que no puedan volver a formar una etiqueta más adelante.
  t = t.replace(/[<>]/g, '');

  t = t.replace(/[^\x20-\x7EÁÉÍÓÚÜÑáéíóúüñ¿¡€£¥·çÇàèìòùÄÖäöß—–]+/g, ''); // restringe a caracteres comunes + algunos acentos
  if (t.length > TTS_MAX_LENGTH) t = t.slice(0, TTS_MAX_LENGTH) + '...';
  return t.trim();
}

function sendToTTS(message) {
  /*axios.post('http://localhost:5002/speak', { text: message })
    .catch((err) => {
      console.error('❌ Error TTS:', err?.message ?? err);
    });
  */
  const safe = sanitizeForTTS(message);
  if (!safe) return;
  ttsQueue.push(safe);
  processTTSQueue().catch(err => console.error("TTS queue error:", err));
}

// Procesador: envía cada item al microservicio y espera su finalización
async function processTTSQueue() {
  if (ttsProcessing) return;
  ttsProcessing = true;

  while (ttsQueue.length > 0) {
    const texto = ttsQueue.shift();
    try {
      console.log('TTS => Enviando texto al servicio:', texto.slice(0, 120));
      // Post hacia el microservicio. Espera hasta que Flask haya terminado de reproducir.
      await axios.post('http://localhost:5002/speak', { text: texto }, { timeout: TTS_POST_TIMEOUT });
    } catch (err) {
      // Log detallado (no rompas la cola)
      console.error('❌ Error al enviar/leer TTS:', err?.message ?? err);
    }

    // Pequeña pausa entre audios para evitar colisiones
    await new Promise(res => setTimeout(res, TTS_DELAY_BETWEEN));
  }

  ttsProcessing = false;
}

// Lock para evitar condiciones de carrera al escribir latest.json
let fileWriteLock = false;
const writeQueue = [];

export async function saveAndBroadcastMessage(message) {
  // Añadir a la cola si hay una escritura en progreso
  if (fileWriteLock) {
    writeQueue.push(message);
    return;
  }

  fileWriteLock = true;

  try {
    let messages = [];
    try {
      const data = await fsp.readFile(messagesFile, 'utf-8');
      // Limpiar datos corruptos: intentar parsear, si falla usar array vacío
      try {
        messages = JSON.parse(data || '[]');
        if (!Array.isArray(messages)) {
          console.warn('⚠️ latest.json no es un array, reiniciando...');
          messages = [];
        }
      } catch (parseErr) {
        console.warn('⚠️ Error parseando latest.json, reiniciando archivo:', parseErr.message);
        messages = [];
      }
    } catch (err) {
      if (err.code !== 'ENOENT') {
        console.error('Error leyendo latest.json:', err.message);
      }
      messages = [];
    }

    const newMessages = [...messages.slice(-99), message];
    
    // Escribir de forma atómica usando un archivo temporal
    const tempFile = messagesFile + '.tmp';
    await fsp.writeFile(tempFile, JSON.stringify(newMessages, null, 2), 'utf-8');
    await fsp.rename(tempFile, messagesFile);
    
    broadcastMessage(message);
  } catch (err) {
    console.error('Error en saveAndBroadcastMessage:', err.message);
  } finally {
    fileWriteLock = false;
    
    // Procesar mensajes en cola
    if (writeQueue.length > 0) {
      const nextMessage = writeQueue.shift();
      setImmediate(() => saveAndBroadcastMessage(nextMessage));
    }
  }
}

/* -------------------------
   handleMessage: robusto y con debug
   ------------------------- */
function handleMessage(msg) {
    try {
        const autor = msg.username || 'Desconocido';
        const texto = msg.message.trim();
        const cmdName = parseCommand(texto);

        // Ejecuta comando si existe
        if (cmdName && commands[cmdName]) {
            commands[cmdName](autor, msg);
            return; // no procesamos mensaje normal si era comando
        }

        // Procesamiento normal TTS
        if (ttsEnabled) {
            const who = msg.username || msg.user || autor || 'alguien';
            sendToTTS(`${who} dijo: ${texto}`);
        }

        // Guardar y difundir
        const mensajeParaGuardar = {
            ...msg,
            user: autor,
            message: texto,
            received_at: new Date().toISOString()
        };
        saveAndBroadcastMessage(mensajeParaGuardar);

    } catch (err) {
        console.error('Error en handleMessage:', err);
    }
}

/* -------------------------
   Iniciar conexiones a plataformas
   ------------------------- */
async function iniciarChats() {
  console.log('🔄 Iniciando conexiones de chat...');

  const twitchAccounts = loadTwitchAccounts();

  const conexiones = [
    ...twitchAccounts.map(acc => ({
      nombre: `Twitch (${acc.username})`,
      conectar: () => connectTwitchAccount(acc, handleMessage),
    })),
    { nombre: 'Kick', conectar: () => connectKick(handleMessage) },
    { nombre: 'YouTube', conectar: () => connectYouTube(handleMessage) },
    { nombre: 'Rumble', conectar: () => connectRumble(handleMessage) },
  ];

  const resultados = await Promise.allSettled(
    conexiones.map(({ conectar }) => conectar())
  );

  console.log('⚙️ Inicialización completa');

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
server.listen(finalPort, () => {
  console.log(`🚀 Servidor corriendo en http://127.0.0.1:${finalPort}`);
});