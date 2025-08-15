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
import 'dotenv/config';  // carga .env primero
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

import axios from "axios";

// import { addMessage, getMessages } from './utils/globalMessages.js';
// import { appendLatestJson } from './utils/saveMessage.js';

let ttsEnabled = true;
// Lista de usuarios autorizados para controlar el TTS
const TTS_ADMINS = ["juanitocanuto", "ameloblastos"];


const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
app.use(express.json());
app.use(express.static(join(__dirname, "public")));
const server = http.createServer(app); // ⬅ necesario para compartir HTTP y WS

const PORT = process.env.PORT || 3000;

const messagesDir = join(__dirname, "messages");
if (!fs.existsSync(messagesDir)) {
  fs.mkdirSync(messagesDir, { recursive: true });
}

const messagesFile = join(messagesDir, "latest.json");
if (!fs.existsSync(messagesFile)) {
  fs.writeFileSync(messagesFile, "[]", "utf-8");
}

app.use(express.static(join(__dirname, "public")));

//Para mensajes via HTTP con polling
/*app.get("/messages", (req, res) => {
  fs.readFile(messagesFile, "utf-8", (err, data) => {
    if (err) {
      console.error("Error leyendo latest.json:", err);
      return res.json([]);
    }
    try {
      console.log("📤 Sirviendo mensajes:", data);
      return res.json(JSON.parse(data));
    } catch (e) {
      console.error("Error parseando latest.json:", e);
      return res.json([]);
    }
  });
});*/

/*
app.listen(PORT, () => {
  console.log(`Servidor chat unificado en http://127.0.0.1:${PORT}`);
});
*/

// ⬅ WebSocket se manejará manualmente
const wss = new WebSocketServer({ noServer: true });

// Conjunto de clientes conectados
const clients = new Set();

server.on('upgrade', (request, socket, head) => {
  const { url } = request;

  if (url === '/message') {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request);
    });
  } else {
    socket.destroy(); // Rechaza otras rutas
  }
});

wss.on('connection', ws => {
  clients.add(ws);
  console.log('🔌 Cliente WebSocket conectado');

  ws.on('close', () => {
    clients.delete(ws);
    console.log('❌ Cliente WebSocket desconectado');
  });
});

// Broadcast a todos los clientes conectados
function broadcastMessage(messageObj) {
  const data = JSON.stringify(messageObj);
  for (const client of clients) {
    if (client.readyState === client.OPEN) {
      client.send(data);
    }
  }

  /* // Forma de ejemplo
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(messageObj));
    }
  });
  */
}


function sendToTTS(message) {
  axios.post("http://localhost:5002/speak", {
    text: message
  }).catch(err => {
    console.error("❌ Error TTS:", err.message);
  });
}


// Guardar mensaje + emitirlo por WebSocket (versión async/await)
export async function saveAndBroadcastMessage(message) {
  try {
    // Leer mensajes anteriores
    let messages = [];
    try {
      const data = await fsp.readFile(messagesFile, "utf-8");
      messages = JSON.parse(data || "[]");
    } catch (err) {
      if (err.code !== 'ENOENT') {
        console.error("Error leyendo latest.json:", err);
      }
      
    }

    // Mantener solo los últimos 99 + el nuevo
    const newMessages = [...messages.slice(-99), message];

    // Guardar el nuevo array de mensajes
    await fsp.writeFile(messagesFile, JSON.stringify(newMessages, null, 2), "utf-8");
    
    //addMessage(msg);
    //appendLatestJson(getMessages());
    
    // Emitir mensaje por WebSocket
    broadcastMessage(message);
    
  } catch (err) {
    console.error("Error en saveAndBroadcastMessage:", err);
  }
}

// Función para manejar mensajes entrantes
function handleMessage(msg) {
  saveAndBroadcastMessage(msg);
  console.log(`💬 [${msg.platform}] ${msg.user}: ${msg.message}`);
  
  const autor = (msg.user || "").toLowerCase();

  // 🔌 Comandos especiales desde chat
  if (msg.message.toUpperCase() === "/TTS_OFF") {
    if (TTS_ADMINS.includes(autor)) {
      ttsEnabled = false;
      console.log(`🔇 TTS desactivado por ${autor}`);
    } else {
      console.log(`⛔ ${autor} intentó usar /TTS_OFF sin permiso`);
    }
    return;
  }

  if (msg.message.toUpperCase() === "/TTS_ON") {
    if (TTS_ADMINS.includes(autor)) {
      ttsEnabled = true;
      console.log(`🔊 TTS activado por ${autor}`);
    } else {
      console.log(`⛔ ${autor} intentó usar /TTS_ON sin permiso`);
    }
    return;
  }

  // Evitar que lea comandos (opcional)
  // Generar y reproducir audio TTS a partir del mensaje
  if (ttsEnabled && !msg.message.startsWith("/") && !msg.message.startsWith("!")) {
    const textoParaLeer = `${msg.username} dijo: ${msg.message}`;
    console.log(" " + textoParaLeer);  // Aquí imprimes el texto en consola
    sendToTTS(textoParaLeer);
  }
}

// Inicia todas las conexiones de chat
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