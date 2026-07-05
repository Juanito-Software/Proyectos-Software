import axios from 'axios';
import { 
  BITCHUTE_CHANNEL_NAME,
  BITCHUTE_VIDEO_ID,
  BITCHUTE_SERVER_URL 
} from './config.js';

let isConnected = false;
let pollInterval = null;
let messageHandler = null;
let lastMessageIds = new Set(); // Para evitar duplicados

const API_BASE_URL = 'https://www.bitchute.com';
const POLL_INTERVAL = 5000; // 5 segundos para polling
const BITCHUTE_SERVER_DEFAULT = 'http://localhost:5005';

/**
 * Obtiene el video ID del canal si no está configurado
 * BitChute no tiene una API pública, así que esto es experimental
 */
async function getVideoId(channelName) {
  if (BITCHUTE_VIDEO_ID) {
    return BITCHUTE_VIDEO_ID;
  }

  if (!channelName) {
    throw new Error('Se requiere BITCHUTE_CHANNEL_NAME o BITCHUTE_VIDEO_ID en .env');
  }

  // Intentar obtener el video ID más reciente del canal
  // Nota: Esto es experimental ya que BitChute no tiene API pública
  try {
    // La estructura de BitChute puede variar
    // Por ahora, requerimos que se proporcione el VIDEO_ID directamente
    throw new Error('BITCHUTE_VIDEO_ID es requerido. BitChute no tiene API pública para obtenerlo automáticamente.');
  } catch (err) {
    console.error('❌ [BitChute] Error obteniendo video ID:', err.message);
    throw err;
  }
}

/**
 * Método de polling: obtener mensajes usando scraping o servidor intermedio
 */
async function fetchMessagesFromAPI(onMessage) {
  try {
    let videoId = BITCHUTE_VIDEO_ID;
    
    // Obtener video ID si no está configurado
    if (!videoId && BITCHUTE_CHANNEL_NAME) {
      try {
        videoId = await getVideoId(BITCHUTE_CHANNEL_NAME);
      } catch (err) {
        console.error('❌ [BitChute] Error obteniendo video ID para polling:', err.message);
        return;
      }
    }

    if (!videoId) {
      return;
    }

    // Intentar obtener mensajes del servidor intermedio de BitChute (si existe)
    const serverUrl = BITCHUTE_SERVER_URL || BITCHUTE_SERVER_DEFAULT;
    
    try {
      const response = await axios.get(`${serverUrl}/messages`, {
        params: {
          video_id: videoId,
          channel: BITCHUTE_CHANNEL_NAME
        },
        timeout: 5000
      });

      if (response.data && response.data.messages) {
        const messages = response.data.messages;
        
        messages.forEach(msg => {
          // Evitar duplicados usando ID único
          const msgId = msg.id || `${msg.username}_${msg.timestamp}_${msg.message}`;
          
          if (!lastMessageIds.has(msgId)) {
            lastMessageIds.add(msgId);
            
            // Limitar el tamaño del set para no consumir mucha memoria
            if (lastMessageIds.size > 1000) {
              const firstId = lastMessageIds.values().next().value;
              lastMessageIds.delete(firstId);
            }
            
            const formatted = {
              platform: 'bitchute',
              username: msg.username || msg.author || 'anon',
              message: msg.message || msg.text || msg.body || '',
              timestamp: msg.timestamp ? (typeof msg.timestamp === 'number' ? msg.timestamp : new Date(msg.timestamp).getTime()) : Date.now()
            };
            
            if (formatted.message.trim()) {
              onMessage(formatted);
              console.log(`💬 [BitChute] Mensaje: ${formatted.username}: ${formatted.message}`);
            }
          }
        });
      }
    } catch (serverErr) {
      // Si el servidor intermedio no está disponible, intentar método directo (experimental)
      if (serverErr.code === 'ECONNREFUSED' || serverErr.code === 'ETIMEDOUT') {
        console.warn('⚠️ [BitChute] Servidor intermedio no disponible. BitChute requiere un servidor Python para scraping.');
        console.warn('💡 [BitChute] Consulta BITCHUTE_SETUP.md para configurar el servidor intermedio.');
      } else if (serverErr.response?.status !== 404) {
        console.error('⚠️ [BitChute] Error obteniendo mensajes (polling):', serverErr.message);
      }
    }
  } catch (err) {
    // Solo loguear si no es un timeout o conexión rechazada
    if (err.code !== 'ECONNREFUSED' && err.code !== 'ETIMEDOUT' && err.response?.status !== 404) {
      console.error('⚠️ [BitChute] Error obteniendo mensajes:', err.message);
    }
  }
}

/**
 * Inicia el método de polling
 */
function startPollingMethod(onMessage) {
  if (pollInterval) {
    return; // Ya está corriendo
  }

  console.log('🔄 [BitChute] Iniciando método de polling...');
  
  pollInterval = setInterval(() => {
    fetchMessagesFromAPI(onMessage);
  }, POLL_INTERVAL);
}

/**
 * Detiene el método de polling
 */
function stopPollingMethod() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
  
  lastMessageIds.clear();
}

/**
 * Conecta al chat de BitChute
 */
export async function connectBitChute(onMessage) {
  console.log('🔧 [BitChute] Iniciando servicio...');
  
  messageHandler = onMessage;
  
  if (!BITCHUTE_CHANNEL_NAME && !BITCHUTE_VIDEO_ID) {
    console.error('❌ [BitChute] Faltan credenciales en .env (BITCHUTE_CHANNEL_NAME o BITCHUTE_VIDEO_ID son requeridos)');
    return;
  }

  if (!BITCHUTE_VIDEO_ID) {
    console.warn('⚠️ [BitChute] BITCHUTE_VIDEO_ID no está configurado');
    console.warn('💡 [BitChute] BitChute requiere el ID del video en vivo. Consulta BITCHUTE_SETUP.md');
    return;
  }

  isConnected = true;
  
  // BitChute no tiene WebSocket público, usar polling
  startPollingMethod(onMessage);
  console.log('✅ [BitChute] Servicio iniciado (Polling)');
  console.log('💡 [BitChute] Nota: BitChute requiere un servidor Python intermedio para scraping. Consulta BITCHUTE_SETUP.md');
}

/**
 * Desconecta del chat de BitChute
 */
export async function disconnectBitChute() {
  stopPollingMethod();
  
  isConnected = false;
  messageHandler = null;
  console.log('🛑 [BitChute] Desconectado');
}

