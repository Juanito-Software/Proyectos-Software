import WebSocket from "ws";
//import { addMessage, getMessages } from "../utils/globalMessages.js";
//import { appendLatestJson } from "../utils/saveMessage.js";
import { KICK_CHANNEL, KICK_BEARER_TOKEN, KICK_COOKIES } from './config.js';

// Kick cambió la clave de Pusher y @retconned/kick-js la lleva fija en el código
// (la vieja da "App key not in this cluster" y nunca llega un mensaje). Por eso
// la conexión se hace aquí: la clave se pide a Kick en cada conexión y la de
// abajo solo se usa si esa petición falla.
const PUSHER_RESPALDO = { app_key: "34bf7a0ff419a2a775b9", cluster: "us2" };
const RECONEXION_TRAS_CAIDA_MS = 10 * 1000;

let conectado = false;
let client = null; // WebSocket activo
let reconnectInterval = null;
let reconnectTimeout = null;
let messageHandler = null;
let isReconnecting = false; // Bandera para evitar múltiples reconexiones simultáneas
let processedMessages = new Set(); // Set para deduplicar mensajes
const MAX_PROCESSED_MESSAGES = 1000; // Límite de mensajes en el set

const RECONNECT_INTERVAL = 2 * 60 * 60 * 1000; // 2 horas en milisegundos

/**
 * Crea un ID único para un mensaje para deduplicación
 */
function createMessageId(msg) {
  if (msg.id) return msg.id; // Kick manda un id propio por mensaje
  const username = msg.sender?.username || 'anon';
  const content = msg.content || '';
  const timestamp = Date.parse(msg.created_at) || Date.now();
  // Redondear timestamp a segundos para agrupar mensajes del mismo segundo
  const roundedTimestamp = Math.floor(timestamp / 1000);
  return `${username}:${content}:${roundedTimestamp}`;
}

/**
 * Cierra el WebSocket anterior (sin disparar la reconexión por caída)
 */
function cleanupPreviousClient() {
  if (client) {
    try {
      console.log("🧹 [Kick] Cerrando conexión anterior");
      client.removeAllListeners();
      client.on("error", () => {}); // un error tardío del socket viejo no debe tumbar el proceso
      client.terminate();
    } catch (e) {
      console.warn("⚠️ [Kick] Error al limpiar cliente anterior:", e.message);
    }
    client = null;
  }
  conectado = false;

  // Limpiar algunos mensajes procesados para evitar que el set crezca indefinidamente
  if (processedMessages.size > MAX_PROCESSED_MESSAGES) {
    const messagesArray = Array.from(processedMessages);
    processedMessages = new Set(messagesArray.slice(-MAX_PROCESSED_MESSAGES / 2));
  }
}

/**
 * Obtiene el id del chatroom del canal (la API pública de Kick)
 */
async function getChatroomId(channel) {
  const res = await fetch(`https://kick.com/api/v2/channels/${channel}`, {
    headers: { Accept: "application/json", "User-Agent": "Mozilla/5.0" }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} al pedir el canal ${channel}`);
  const data = await res.json();
  if (!data.chatroom?.id) throw new Error(`El canal ${channel} no tiene chatroom`);
  return data.chatroom.id;
}

/**
 * Pide a Kick la clave y el cluster de Pusher vigentes; si falla, usa el respaldo
 */
async function getPusherCredentials() {
  try {
    const res = await fetch("https://web.kick.com/api/v1/realtime/connection", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "x-app-platform": "web",
        Origin: "https://kick.com",
        Referer: "https://kick.com/",
        "User-Agent": "Mozilla/5.0"
      },
      body: JSON.stringify({
        client: { id: crypto.randomUUID(), type: "web" },
        capabilities: { accepted_providers: [{ provider: "pusher" }] }
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const { data } = await res.json();
    const creds = data?.connections?.find(c => c.provider === "pusher")?.credentials;
    if (!creds?.app_key || !creds?.cluster) throw new Error("respuesta sin credenciales de Pusher");
    return creds;
  } catch (err) {
    console.warn(`⚠️ [Kick] No se pudo obtener la clave de Pusher (${err.message}); se usa la de respaldo`);
    return PUSHER_RESPALDO;
  }
}

/**
 * Programa una reconexión tras una caída del socket
 */
function scheduleReconnect(onMessage) {
  if (reconnectTimeout) return;
  console.log(`⚠️ [Kick] Desconectado, reintentando en ${RECONEXION_TRAS_CAIDA_MS / 1000}s`);
  reconnectTimeout = setTimeout(async () => {
    reconnectTimeout = null;
    client = await createKickConnection(onMessage);
    if (!client) scheduleReconnect(onMessage);
  }, RECONEXION_TRAS_CAIDA_MS);
}

async function createKickConnection(onMessage) {
  if (!KICK_CHANNEL || !KICK_BEARER_TOKEN || !KICK_COOKIES) {
    console.error("❌ Faltan credenciales Kick en .env");
    return null;
  }

  // Limpiar cliente anterior antes de crear uno nuevo
  cleanupPreviousClient();

  let chatroomId, pusher;
  try {
    [chatroomId, pusher] = await Promise.all([getChatroomId(KICK_CHANNEL), getPusherCredentials()]);
  } catch (err) {
    console.error("❌ [Kick] Error obteniendo datos del canal:", err.message);
    return null;
  }

  const canal = `chatrooms.${chatroomId}.v2`;
  const url = `wss://ws-${pusher.cluster}.pusher.com/app/${pusher.app_key}?protocol=7&client=js&version=8.4.0&flash=false`;
  const socket = new WebSocket(url);
  console.log(`✅ [Kick] Cliente creado para canal: ${KICK_CHANNEL} (chatroom ${chatroomId})`);

  // Handler con deduplicación para evitar mensajes duplicados
  const chatMessageHandler = (msg) => {
    // Crear ID único para el mensaje
    const messageId = createMessageId(msg);

    // Verificar si ya procesamos este mensaje
    if (processedMessages.has(messageId)) {
      console.log(`⚠️ [Kick] Mensaje duplicado ignorado: ${msg.sender?.username || 'anon'}: ${(msg.content || '').substring(0, 30)}`);
      return; // Ignorar mensaje duplicado
    }

    // Marcar como procesado
    processedMessages.add(messageId);

    const formattedMessage = {
      platform: "kick",
      username: msg.sender?.username || "anon",
      // Emotes "[emote:123:nombre]" → "nombre" (lo que hacía kick-js con plainEmote)
      message: (msg.content || "").replace(/\[emote:(\d+):(\w+)\]/g, (_, __, nombre) => nombre),
      timestamp: Date.now()
    };
    onMessage(formattedMessage);
    console.log("💬 [Kick] Nuevo mensaje:", formattedMessage.message);
  };

  socket.on("open", () => {
    socket.send(JSON.stringify({ event: "pusher:subscribe", data: { auth: "", channel: canal } }));
  });

  socket.on("message", (raw) => {
    let ev;
    try {
      ev = JSON.parse(raw.toString());
    } catch {
      return;
    }
    switch (ev.event) {
      case "pusher:ping":
        socket.send(JSON.stringify({ event: "pusher:pong", data: {} }));
        break;
      case "pusher_internal:subscription_succeeded":
        // Solo aquí el chat está realmente enganchado (antes se marcaba al abrir el socket)
        conectado = true;
        console.log(`✅ [Kick] Conectado al chat de ${KICK_CHANNEL}`);
        break;
      case "pusher:error":
        console.error("❌ [Kick] Error de Pusher:", ev.data);
        break;
      case "App\\Events\\ChatMessageEvent":
        try {
          chatMessageHandler(typeof ev.data === "string" ? JSON.parse(ev.data) : ev.data);
        } catch (e) {
          console.error("❌ [Kick] Mensaje con formato inesperado:", e.message);
        }
        break;
    }
  });

  socket.on("error", (err) => {
    console.error("❌ [Kick] Error del WebSocket:", err.message);
  });

  socket.on("close", (code) => {
    conectado = false;
    console.log(`📡 [Kick] close (${code})`);
    if (client === socket) {
      client = null;
      scheduleReconnect(onMessage);
    }
  });

  return socket;
}

export async function connectKick(onMessage) {
  console.log("🔧 [Kick] Iniciando servicio...");

  messageHandler = onMessage;

  // Crear conexión inicial
  client = await createKickConnection(onMessage);

  if (!client) {
    return;
  }

  // Configurar reconexión automática cada 2 horas
  reconnectInterval = setInterval(async () => {
    // Evitar múltiples reconexiones simultáneas
    if (isReconnecting) {
      console.log("⚠️ [Kick] Reconexión ya en progreso, saltando...");
      return;
    }

    isReconnecting = true;
    console.log("🔄 [Kick] Reconexión programada (cada 2 horas)...");

    try {
      // Limpiar cliente anterior completamente
      cleanupPreviousClient();

      // Esperar un momento antes de reconectar para asegurar que todo se limpió
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Crear nueva conexión (createKickConnection ya limpia el cliente anterior)
      client = await createKickConnection(onMessage);
      if (client) {
        console.log("✅ [Kick] Reconectado exitosamente");
      } else {
        console.warn("⚠️ [Kick] No se pudo reconectar, se intentará en la próxima vez");
      }
    } catch (err) {
      console.error("❌ [Kick] Error en reconexión automática:", err.message);
    } finally {
      isReconnecting = false;
    }
  }, RECONNECT_INTERVAL);

  console.log(`✅ [Kick] Servicio iniciado. Reconexión automática cada 2 horas`);
}
