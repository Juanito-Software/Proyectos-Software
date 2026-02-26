import axios from 'axios';
import { 
  RUMBLE_SERVER_URL, 
  RUMBLE_API_URL, 
  RUMBLE_CHANNEL, 
  RUMBLE_STREAM_URL,
  RUMBLE_POLL_INTERVAL 
} from './config.js';

let isConnected = false;
let pollInterval = null;
const processedMessageIds = new Set();
const MAX_PROCESSED_IDS = 1000;

/**
 * Crea un ID único para deduplicar mensajes (por si el servidor envía el mismo dos veces)
 */
function createMessageId(msg) {
  const username = msg.username || 'anon';
  const message = msg.message || '';
  const ts = msg.timestamp || Date.now();
  const rounded = Math.floor(ts / 1000);
  return `${username}:${message}:${rounded}`;
}

/**
 * Inicia la conexión al chat de Rumble
 */
async function startRumbleConnection() {
  if (!RUMBLE_API_URL) {
    console.error("❌ [Rumble] Falta RUMBLE_API_URL en .env");
    return false;
  }

  try {
    const response = await axios.post(`${RUMBLE_SERVER_URL}/start`, {
      api_url: RUMBLE_API_URL,
      channel: RUMBLE_CHANNEL,
      stream_url: RUMBLE_STREAM_URL  // URL opcional del stream específico
    });

    if (response.data.status === 'ok') {
      console.log(`✅ [Rumble] Conectado: ${RUMBLE_API_URL}`);
      return true;
    }
  } catch (err) {
    console.error("❌ [Rumble] Error iniciando conexión:", err.message);
    return false;
  }
  return false;
}

/**
 * Obtiene mensajes del servidor de Rumble
 */
async function fetchMessages(onMessage) {
  try {
    const response = await axios.get(`${RUMBLE_SERVER_URL}/messages`, {
      timeout: 5000
    });

    const messages = response.data.messages || [];
    
    messages.forEach(msg => {
      const formatted = {
        platform: 'rumble',
        username: msg.username || 'anon',
        message: msg.message || '',
        timestamp: msg.timestamp || Date.now()
      };
      
      const msgId = createMessageId(formatted);
      if (processedMessageIds.has(msgId)) {
        return; // Evitar duplicados
      }
      processedMessageIds.add(msgId);
      if (processedMessageIds.size > MAX_PROCESSED_IDS) {
        const arr = [...processedMessageIds];
        processedMessageIds.clear();
        arr.slice(-MAX_PROCESSED_IDS / 2).forEach(id => processedMessageIds.add(id));
      }
      
      onMessage(formatted);
    });
  } catch (err) {
    // Solo loguear si no es un timeout o conexión rechazada (servidor no iniciado)
    if (err.code !== 'ECONNREFUSED' && err.code !== 'ETIMEDOUT') {
      console.error("⚠️ [Rumble] Error obteniendo mensajes:", err.message);
    }
  }
}

/**
 * Conecta al chat de Rumble y comienza a recibir mensajes
 */
export async function connectRumble(onMessage) {
  console.log("🔧 [Rumble] Iniciando servicio...");
  processedMessageIds.clear(); // Limpiar al iniciar nueva conexión

  // Intentar conectar
  const connected = await startRumbleConnection();
  
  if (!connected) {
    console.warn("⚠️ [Rumble] No se pudo conectar. Asegúrate de que el servidor Python esté corriendo.");
    return;
  }

  isConnected = true;

  // Polling para obtener mensajes periódicamente
  pollInterval = setInterval(() => {
    fetchMessages(onMessage);
  }, RUMBLE_POLL_INTERVAL);

  console.log(`✅ [Rumble] Servicio iniciado. Polling cada ${RUMBLE_POLL_INTERVAL}ms`);
  
  // Verificar estado periódicamente
  setInterval(async () => {
    try {
      const status = await axios.get(`${RUMBLE_SERVER_URL}/status`);
      if (!status.data.connected && isConnected) {
        console.warn("⚠️ [Rumble] Conexión perdida, intentando reconectar...");
        await startRumbleConnection();
      }
    } catch (err) {
      // Servidor no disponible, no hacer nada
    }
  }, 30000); // Verificar cada 30 segundos
}

/**
 * Detiene la conexión a Rumble
 */
export async function disconnectRumble() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
  
  isConnected = false;
  processedMessageIds.clear();
  
  try {
    await axios.post(`${RUMBLE_SERVER_URL}/stop`);
    console.log("🛑 [Rumble] Desconectado");
  } catch (err) {
    // Ignorar errores al desconectar
  }
}

