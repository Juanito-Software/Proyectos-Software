import WebSocket from 'ws';
import axios from 'axios';
import { 
  ODYSEE_CHANNEL_NAME,
  ODYSEE_CLAIM_ID,
  ODYSEE_SERVER_URL 
} from './config.js';

let ws = null;
let isConnected = false;
let reconnectTimeout = null;
let pingInterval = null;
let messageHandler = null;
let pollInterval = null;
let claimIdAttempts = 0;
const MAX_CLAIM_ID_ATTEMPTS = 2; // Máximo de intentos para obtener claim_id

const WS_URL = 'wss://sockety.odysee.com/ws/commentron';
const API_BASE_URL = 'https://api.odysee.live';
const DEFAULT_PING_INTERVAL = 30000; // 30 segundos
const RECONNECT_DELAY = 5000; // 5 segundos
const POLL_INTERVAL = 3000; // 3 segundos para polling si WebSocket falla

/**
 * Obtiene el claim_id del canal si no está configurado
 */
async function getClaimId(channelName) {
  if (ODYSEE_CLAIM_ID) {
    return ODYSEE_CLAIM_ID;
  }

  if (!channelName) {
    throw new Error('Se requiere ODYSEE_CHANNEL_NAME o ODYSEE_CLAIM_ID en .env');
  }

  try {
    // Intentar obtener el claim_id desde la API de Odysee
    const response = await axios.get(`${API_BASE_URL}/claim/resolve`, {
      params: {
        name: channelName
      }
    });

    if (response.data && response.data.claim_id) {
      return response.data.claim_id;
    }

    // Si no funciona, intentar con el formato @channelName
    const response2 = await axios.get(`${API_BASE_URL}/claim/resolve`, {
      params: {
        name: `@${channelName}`
      }
    });

    if (response2.data && response2.data.claim_id) {
      return response2.data.claim_id;
    }

    throw new Error('No se pudo obtener el claim_id del canal');
  } catch (err) {
    console.error('❌ [Odysee] Error obteniendo claim_id:', err.message);
    throw err;
  }
}

/**
 * Conecta al WebSocket de Odysee
 */
async function connectOdyseeWebSocket(onMessage) {
  return new Promise(async (resolve, reject) => {
    try {
      let claimId = ODYSEE_CLAIM_ID;
      
      // Obtener claim_id si no está configurado
      if (!claimId && ODYSEE_CHANNEL_NAME && claimIdAttempts < MAX_CLAIM_ID_ATTEMPTS) {
        try {
          claimId = await getClaimId(ODYSEE_CHANNEL_NAME);
          console.log(`✅ [Odysee] Claim ID obtenido: ${claimId}`);
          claimIdAttempts = 0; // Resetear contador si tiene éxito
        } catch (err) {
          claimIdAttempts++;
          if (claimIdAttempts >= MAX_CLAIM_ID_ATTEMPTS) {
            console.error('❌ [Odysee] No se pudo obtener claim_id después de varios intentos.');
            console.error('💡 [Odysee] Verifica que ODYSEE_CHANNEL_NAME sea correcto o usa ODYSEE_CLAIM_ID directamente.');
            console.warn('⚠️ [Odysee] Intentando con polling como último recurso...');
          } else {
            console.warn(`⚠️ [Odysee] No se pudo obtener claim_id (intento ${claimIdAttempts}/${MAX_CLAIM_ID_ATTEMPTS}), intentando con polling...`);
          }
          // Si falla, usar método de polling alternativo
          startPollingMethod(onMessage);
          return;
        }
      } else if (!claimId && !ODYSEE_CHANNEL_NAME && !ODYSEE_CLAIM_ID) {
        throw new Error('Se requiere ODYSEE_CLAIM_ID o ODYSEE_CHANNEL_NAME en .env');
      }

      if (!claimId) {
        throw new Error('Se requiere ODYSEE_CLAIM_ID o ODYSEE_CHANNEL_NAME en .env');
      }

      // Crear conexión WebSocket
      const wsUrl = `${WS_URL}?claim_id=${claimId}`;
      ws = new WebSocket(wsUrl);

      ws.on('open', () => {
        console.log('🔗 [Odysee] WebSocket conectado');
        isConnected = true;
        resolve(ws);
        
        // Iniciar ping-pong
        startPingPong();
      });

      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          handleWebSocketMessage(message, onMessage);
        } catch (err) {
          console.error('❌ [Odysee] Error parseando mensaje:', err.message);
        }
      });

      ws.on('error', (err) => {
        console.error('❌ [Odysee] Error en WebSocket:', err.message);
        isConnected = false;
        
        // Si falla el WebSocket, intentar método de polling
        if (!pollInterval) {
          console.log('🔄 [Odysee] Cambiando a método de polling...');
          startPollingMethod(onMessage);
        }
      });

      ws.on('close', () => {
        console.log('⚠️ [Odysee] WebSocket cerrado');
        isConnected = false;
        stopPingPong();
        
        // Intentar reconectar después de un delay
        if (messageHandler) {
          reconnectTimeout = setTimeout(() => {
            console.log('🔄 [Odysee] Intentando reconectar WebSocket...');
            connectOdyseeWebSocket(messageHandler).catch(err => {
              console.error('❌ [Odysee] Error en reconexión:', err.message);
            });
          }, RECONNECT_DELAY);
        }
      });

    } catch (err) {
      reject(err);
    }
  });
}

/**
 * Maneja mensajes del WebSocket
 */
function handleWebSocketMessage(message, onMessage) {
  try {
    // La estructura del mensaje puede variar según la API de Odysee
    // Ajustar según la documentación real
    if (message.type === 'comment' || message.comment) {
      const comment = message.comment || message;
      const formatted = {
        platform: 'odysee',
        username: comment.author || comment.name || 'anon',
        message: comment.text || comment.message || comment.body || '',
        timestamp: comment.timestamp ? comment.timestamp * 1000 : Date.now()
      };
      
      if (formatted.message.trim()) {
        onMessage(formatted);
        console.log(`💬 [Odysee] Mensaje: ${formatted.username}: ${formatted.message}`);
      }
    } else if (message.messages && Array.isArray(message.messages)) {
      // Si viene un array de mensajes
      message.messages.forEach(msg => {
        const formatted = {
          platform: 'odysee',
          username: msg.author || msg.name || 'anon',
          message: msg.text || msg.message || msg.body || '',
          timestamp: msg.timestamp ? msg.timestamp * 1000 : Date.now()
        };
        
        if (formatted.message.trim()) {
          onMessage(formatted);
        }
      });
    }
  } catch (err) {
    console.error('❌ [Odysee] Error procesando mensaje:', err.message);
  }
}

/**
 * Método alternativo: polling de mensajes usando API REST
 */
async function fetchMessagesFromAPI(onMessage) {
  try {
    let claimId = ODYSEE_CLAIM_ID;
    
    // Solo intentar obtener claim_id si no hemos excedido el máximo de intentos
    if (!claimId && ODYSEE_CHANNEL_NAME && claimIdAttempts < MAX_CLAIM_ID_ATTEMPTS) {
      try {
        claimId = await getClaimId(ODYSEE_CHANNEL_NAME);
        claimIdAttempts = 0; // Resetear si tiene éxito
      } catch (err) {
        claimIdAttempts++;
        if (claimIdAttempts >= MAX_CLAIM_ID_ATTEMPTS) {
          console.error('❌ [Odysee] No se pudo obtener claim_id después de varios intentos. Deteniendo polling.');
          console.error('💡 [Odysee] Verifica que ODYSEE_CHANNEL_NAME sea correcto o usa ODYSEE_CLAIM_ID directamente.');
          stopPollingMethod(); // Detener el polling si falla
          return;
        }
        // No loguear cada intento para evitar spam
        return;
      }
    } else if (!claimId && claimIdAttempts >= MAX_CLAIM_ID_ATTEMPTS) {
      // Ya intentamos demasiadas veces, no seguir intentando
      return;
    }

    if (!claimId) {
      return;
    }

    // Intentar obtener comentarios del livestream
    // Nota: La estructura exacta de la API puede variar
    const response = await axios.get(`${API_BASE_URL}/comment/list`, {
      params: {
        claim_id: claimId,
        page_size: 50
      },
      timeout: 5000
    });

    if (response.data && response.data.items) {
      response.data.items.forEach(item => {
        const formatted = {
          platform: 'odysee',
          username: item.author || item.channel_name || 'anon',
          message: item.comment || item.text || item.body || '',
          timestamp: item.timestamp ? item.timestamp * 1000 : Date.now()
        };
        
        if (formatted.message.trim()) {
          onMessage(formatted);
        }
      });
    }
  } catch (err) {
    // Solo loguear si no es un timeout o conexión rechazada
    if (err.code !== 'ECONNREFUSED' && err.code !== 'ETIMEDOUT' && err.response?.status !== 404) {
      console.error('⚠️ [Odysee] Error obteniendo mensajes (polling):', err.message);
    }
  }
}

/**
 * Inicia el método de polling como alternativa al WebSocket
 */
function startPollingMethod(onMessage) {
  if (pollInterval) {
    return; // Ya está corriendo
  }

  console.log('🔄 [Odysee] Iniciando método de polling...');
  
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
}

/**
 * Inicia el ping-pong para mantener la conexión activa
 */
function startPingPong() {
  stopPingPong();
  
  pingInterval = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      // Enviar ping si el servidor lo requiere
      // Ajustar según la implementación real de Odysee
      try {
        ws.ping();
      } catch (err) {
        // Ignorar errores de ping
      }
    }
  }, DEFAULT_PING_INTERVAL);
}

/**
 * Detiene el ping-pong
 */
function stopPingPong() {
  if (pingInterval) {
    clearInterval(pingInterval);
    pingInterval = null;
  }
}

/**
 * Conecta al chat de Odysee
 */
export async function connectOdysee(onMessage) {
  console.log('🔧 [Odysee] Iniciando servicio...');
  
  messageHandler = onMessage;
  
  if (!ODYSEE_CHANNEL_NAME && !ODYSEE_CLAIM_ID) {
    console.error('❌ [Odysee] Faltan credenciales en .env (ODYSEE_CHANNEL_NAME o ODYSEE_CLAIM_ID son requeridos)');
    return;
  }

  try {
    // Intentar conectar vía WebSocket primero
    await connectOdyseeWebSocket(onMessage);
    console.log('✅ [Odysee] Servicio iniciado (WebSocket)');
  } catch (err) {
    console.error('❌ [Odysee] Error conectando vía WebSocket:', err.message);
    console.log('🔄 [Odysee] Intentando método de polling...');
    
    // Si falla el WebSocket, usar polling
    startPollingMethod(onMessage);
    console.log('✅ [Odysee] Servicio iniciado (Polling)');
    
    // Intentar reconectar WebSocket después de un delay
    reconnectTimeout = setTimeout(() => {
      console.log('🔄 [Odysee] Intentando reconectar WebSocket...');
      connectOdyseeWebSocket(onMessage).catch(err => {
        console.error('❌ [Odysee] Error en reconexión:', err.message);
      });
    }, RECONNECT_DELAY * 2);
  }
}

/**
 * Desconecta del chat de Odysee
 */
export async function disconnectOdysee() {
  stopPingPong();
  stopPollingMethod();
  
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  
  if (ws) {
    ws.close();
    ws = null;
  }
  
  isConnected = false;
  messageHandler = null;
  console.log('🛑 [Odysee] Desconectado');
}

