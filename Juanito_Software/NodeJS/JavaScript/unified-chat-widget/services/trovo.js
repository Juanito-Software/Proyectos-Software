import WebSocket from 'ws';
import axios from 'axios';
import { 
  TROVO_CLIENT_ID, 
  TROVO_CHANNEL_ID 
} from './config.js';

let ws = null;
let isConnected = false;
let reconnectTimeout = null;
let pingInterval = null;
let messageHandler = null;
let tokenRefreshInterval = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 3; // Máximo de intentos de reconexión antes de parar

const WS_URL = 'wss://open-chat.trovo.live/chat';
const TOKEN_URL = 'https://open-api.trovo.live/openplatform/chat/channel-token';
const DEFAULT_PING_INTERVAL = 30000; // 30 segundos por defecto
const RECONNECT_DELAY = 5000; // 5 segundos
const TOKEN_REFRESH_INTERVAL = 15 * 1000; // Renovar token cada 15 segundos (válido 20s)

let currentPingInterval = DEFAULT_PING_INTERVAL;

/**
 * Genera un nonce único para las solicitudes
 */
function generateNonce() {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

/**
 * Obtiene un token de servicio de chat de Trovo
 * Usa el endpoint channel-token que NO requiere OAuth (solo Client-ID)
 */
async function getChatToken() {
  if (!TROVO_CLIENT_ID || !TROVO_CHANNEL_ID) {
    throw new Error('Faltan credenciales de Trovo en .env (TROVO_CLIENT_ID y TROVO_CHANNEL_ID son requeridos)');
  }

  try {
    // Usar GET /openplatform/chat/channel-token/{channelID}
    // No requiere OAuth, solo Client-ID
    const response = await axios.get(`${TOKEN_URL}/${TROVO_CHANNEL_ID}`, {
      headers: {
        'Accept': 'application/json',
        'Client-ID': TROVO_CLIENT_ID
      }
    });

    if (response.data && response.data.token) {
      return response.data.token;
    }
    
    throw new Error('No se recibió token en la respuesta');
  } catch (err) {
    if (err.response) {
      throw new Error(`Error obteniendo token: ${err.response.status} - ${JSON.stringify(err.response.data)}`);
    }
    throw new Error(`Error obteniendo token: ${err.message}`);
  }
}

/**
 * Conecta al WebSocket de Trovo y autentica
 */
async function connectTrovoWebSocket(onMessage) {
  return new Promise(async (resolve, reject) => {
    try {
      // Obtener token antes de conectar
      const token = await getChatToken();
      console.log('✅ [Trovo] Token obtenido');

      // Crear conexión WebSocket
      ws = new WebSocket(WS_URL);

      ws.on('open', async () => {
        console.log('🔗 [Trovo] WebSocket conectado, autenticando...');
        
        // Enviar mensaje de autenticación
        const authMessage = {
          type: 'AUTH',
          nonce: generateNonce(),
          data: {
            token: token
          }
        };

        ws.send(JSON.stringify(authMessage));
      });

      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          
          // Manejar diferentes tipos de mensajes
          if (message.type === 'RESPONSE') {
            // Respuesta a AUTH (éxito si no hay error)
            if (message.error) {
              console.error('❌ [Trovo] Autenticación fallida:', message.error);
              isConnected = false;
              reject(new Error(`Autenticación fallida: ${message.error}`));
            } else {
              console.log('✅ [Trovo] Autenticación exitosa');
              isConnected = true;
              reconnectAttempts = 0; // Resetear contador al conectar exitosamente
              resolve(ws);
              
              // Iniciar ping-pong
              startPingPong();
              
              // Iniciar renovación de token
              startTokenRefresh(onMessage);
            }
          } else if (message.type === 'PONG') {
            // Respuesta al ping - ajustar intervalo según recomendación del servidor
            if (message.data && message.data.gap) {
              const recommendedGap = message.data.gap * 1000; // convertir a milisegundos
              if (recommendedGap !== currentPingInterval) {
                console.log(`🔄 [Trovo] Ajustando ping interval a ${recommendedGap}ms (recomendado por servidor)`);
                currentPingInterval = recommendedGap;
                startPingPong(); // Reiniciar con nuevo intervalo
              }
            }
          } else if (message.type === 'CHAT') {
            // Mensaje de chat recibido
            handleChatMessage(message, onMessage);
          } else if (message.error) {
            console.error('❌ [Trovo] Error del servidor:', message.error);
          } else {
            // Otros tipos de mensajes (log para debugging)
            if (message.type !== 'PING') { // No loguear PING
              console.log('📨 [Trovo] Mensaje recibido:', message.type);
            }
          }
        } catch (err) {
          console.error('❌ [Trovo] Error parseando mensaje:', err.message);
        }
      });

      ws.on('error', (err) => {
        console.error('❌ [Trovo] Error en WebSocket:', err.message);
        isConnected = false;
        reject(err);
      });

      ws.on('close', () => {
        console.log('⚠️ [Trovo] WebSocket cerrado');
        isConnected = false;
        stopPingPong();
        stopTokenRefresh();
        
        // Intentar reconectar solo si no hemos excedido el máximo de intentos
        if (messageHandler && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++;
          reconnectTimeout = setTimeout(() => {
            console.log(`🔄 [Trovo] Intentando reconectar... (intento ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
            connectTrovoWebSocket(messageHandler).catch(err => {
              console.error('❌ [Trovo] Error en reconexión:', err.message);
            });
          }, RECONNECT_DELAY);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
          console.error('❌ [Trovo] Máximo de intentos de reconexión alcanzado. Deteniendo intentos.');
          console.error('💡 [Trovo] Verifica tus credenciales o que Trovo esté disponible.');
        }
      });

    } catch (err) {
      reject(err);
    }
  });
}

/**
 * Maneja mensajes de chat recibidos
 * Según la documentación oficial de Trovo
 */
function handleChatMessage(message, onMessage) {
  try {
    // Estructura según documentación: message.data.chats es un array
    if (message.data && message.data.chats && Array.isArray(message.data.chats)) {
      message.data.chats.forEach(chat => {
        // Solo procesar mensajes tipo 0 (normales) y algunos tipos relevantes
        // Tipo 0 = mensajes normales de chat
        const chatType = chat.type || 0;
        
        // Filtrar mensajes de sistema (5001+)
        if (chatType >= 5001) {
          // Mensajes de sistema (suscripciones, follows, etc.) - opcional procesarlos
          // Por ahora los ignoramos, pero puedes añadirlos si quieres
          return;
        }
        
        // Procesar mensaje normal
        const formatted = {
          platform: 'trovo',
          username: chat.nick_name || chat.user_name || 'anon',
          message: chat.content || '',
          timestamp: chat.send_time ? chat.send_time * 1000 : Date.now() // send_time está en segundos
        };
        
        // Solo enviar si tiene contenido
        if (formatted.message.trim()) {
          onMessage(formatted);
          console.log(`💬 [Trovo] Mensaje: ${formatted.username}: ${formatted.message}`);
        }
      });
    }
  } catch (err) {
    console.error('❌ [Trovo] Error procesando mensaje de chat:', err.message);
  }
}

/**
 * Inicia el ping-pong para mantener la conexión activa
 * Usa el intervalo recomendado por el servidor (ajustado dinámicamente)
 */
function startPingPong() {
  stopPingPong();
  
  pingInterval = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const pingMessage = {
        type: 'PING',
        nonce: generateNonce()
      };
      ws.send(JSON.stringify(pingMessage));
    }
  }, currentPingInterval);
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
 * Inicia la renovación automática del token
 */
function startTokenRefresh(onMessage) {
  stopTokenRefresh();
  
  tokenRefreshInterval = setInterval(async () => {
    if (!isConnected || !ws || ws.readyState !== WebSocket.OPEN) {
      return;
    }
    
    try {
      const token = await getChatToken();
      const authMessage = {
        type: 'AUTH',
        nonce: generateNonce(),
        data: {
          token: token
        }
      };
      
      ws.send(JSON.stringify(authMessage));
      console.log('🔄 [Trovo] Token renovado');
    } catch (err) {
      console.error('❌ [Trovo] Error renovando token:', err.message);
    }
  }, TOKEN_REFRESH_INTERVAL);
}

/**
 * Detiene la renovación de token
 */
function stopTokenRefresh() {
  if (tokenRefreshInterval) {
    clearInterval(tokenRefreshInterval);
    tokenRefreshInterval = null;
  }
}

/**
 * Conecta al chat de Trovo
 */
export async function connectTrovo(onMessage) {
  console.log('🔧 [Trovo] Iniciando servicio...');
  
  messageHandler = onMessage;
  
  if (!TROVO_CLIENT_ID || !TROVO_CHANNEL_ID) {
    console.error('❌ [Trovo] Faltan credenciales en .env (TROVO_CLIENT_ID y TROVO_CHANNEL_ID son requeridos)');
    console.log('💡 Nota: TROVO_CLIENT_SECRET ya no es necesario con el endpoint channel-token');
    return;
  }

  // Solo resetear contador si es la primera vez o si se conectó exitosamente antes
  if (reconnectAttempts === 0 || isConnected) {
    reconnectAttempts = 0;
  }

  try {
    await connectTrovoWebSocket(onMessage);
    console.log('✅ [Trovo] Servicio iniciado');
  } catch (err) {
    console.error('❌ [Trovo] Error conectando:', err.message);
    
    // Solo intentar reconectar si no hemos excedido el máximo
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      reconnectTimeout = setTimeout(() => {
        console.log(`🔄 [Trovo] Intentando reconectar... (intento ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        connectTrovo(onMessage).catch(err => {
          console.error('❌ [Trovo] Error en reconexión:', err.message);
        });
      }, RECONNECT_DELAY);
    } else {
      console.error('❌ [Trovo] Máximo de intentos de reconexión alcanzado. Deteniendo.');
      console.error('💡 [Trovo] Verifica tus credenciales (TROVO_CLIENT_ID y TROVO_CHANNEL_ID) o que el servidor de Trovo esté disponible.');
      reconnectAttempts = 0; // Resetear para permitir reintento manual más tarde
    }
  }
}

/**
 * Desconecta del chat de Trovo
 */
export async function disconnectTrovo() {
  stopPingPong();
  stopTokenRefresh();
  
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
  console.log('🛑 [Trovo] Desconectado');
}

