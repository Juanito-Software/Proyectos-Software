import { createClient } from "@retconned/kick-js";
//import { addMessage, getMessages } from "../utils/globalMessages.js";
//import { appendLatestJson } from "../utils/saveMessage.js";
import { KICK_CHANNEL, KICK_BEARER_TOKEN, KICK_COOKIES } from './config.js';

let conectado = false;
let client = null;
let reconnectInterval = null;
let messageHandler = null;
let isReconnecting = false; // Bandera para evitar múltiples reconexiones simultáneas
let processedMessages = new Set(); // Set para deduplicar mensajes
const MAX_PROCESSED_MESSAGES = 1000; // Límite de mensajes en el set

const RECONNECT_INTERVAL = 2 * 60 * 60 * 1000; // 2 horas en milisegundos

/**
 * Crea un ID único para un mensaje para deduplicación
 */
function createMessageId(msg) {
  const username = msg.sender?.username || 'anon';
  const content = msg.content || '';
  const timestamp = msg.created_at || Date.now();
  // Redondear timestamp a segundos para agrupar mensajes del mismo segundo
  const roundedTimestamp = Math.floor(timestamp / 1000);
  return `${username}:${content}:${roundedTimestamp}`;
}

/**
 * Elimina todos los listeners y desconecta el cliente anterior
 * Como el cliente de Kick no expone métodos de limpieza, simplemente lo marcamos como null
 * y confiamos en la deduplicación de mensajes
 */
function cleanupPreviousClient() {
  if (client) {
    try {
      // El cliente de Kick no expone métodos públicos para desconectar o eliminar listeners
      // Simplemente marcamos como null y confiamos en la deduplicación
      // El WebSocket interno se cerrará cuando el objeto se recolecte como basura
      console.log("🧹 [Kick] Limpiando referencia al cliente anterior");
      client = null;
    } catch (e) {
      console.warn("⚠️ [Kick] Error al limpiar cliente anterior:", e.message);
    }
  }
  conectado = false;
  
  // Limpiar algunos mensajes procesados para evitar que el set crezca indefinidamente
  if (processedMessages.size > MAX_PROCESSED_MESSAGES) {
    const messagesArray = Array.from(processedMessages);
    processedMessages = new Set(messagesArray.slice(-MAX_PROCESSED_MESSAGES / 2));
  }
}

async function createKickConnection(onMessage) {
  if (!KICK_CHANNEL || !KICK_BEARER_TOKEN || !KICK_COOKIES) {
    console.error("❌ Faltan credenciales Kick en .env");
    return null;
  }

  // Limpiar cliente anterior antes de crear uno nuevo
  cleanupPreviousClient();

  let newClient;
  try {
    newClient = createClient(KICK_CHANNEL, { logger: false, readOnly: true });
    console.log("✅ [Kick] Cliente creado para canal:", KICK_CHANNEL);
  } catch (err) {
    console.error("❌ [Kick] Error creando cliente:", err);
    return null;
  }

  try {
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
        message: msg.content || "",
        timestamp: Date.now()
      };
      onMessage(formattedMessage);
      console.log("💬 [Kick] Nuevo mensaje:", formattedMessage.message);
    };
    
    newClient.on("ChatMessage", chatMessageHandler);

    newClient.on("event", (ev) => {
      console.log(`📡 [Kick] Evento '${ev.event}'`, ev);
      if (ev.event === "pusher_internal:subscription_succeeded" && !conectado) {
        conectado = true;
        console.log(`✅ [Kick] Conectado al chat de ${KICK_CHANNEL}`);
      }
    });

    const knownEvents = ["ready", "connected", "error", "disconnect", "close"];
    knownEvents.forEach(evt => {
      newClient.on(evt, (...args) => {
        console.log(`📡 [Kick] ${evt}`, ...args);
        if (evt === "ready" && !conectado) {
          conectado = true;
          console.log(`✅ [Kick] Ready en ${KICK_CHANNEL}`);
        }
        // Si se desconecta, marcar como desconectado
        if (evt === "disconnect" || evt === "close") {
          conectado = false;
          console.log(`⚠️ [Kick] Desconectado, se intentará reconectar automáticamente`);
        }
      });
    });
    
    return newClient;
  } catch(e) {
    console.error('❌ Error configurando eventos de Kick:', e);
    return null;
  }
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
