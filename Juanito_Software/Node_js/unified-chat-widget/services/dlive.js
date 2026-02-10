import WebSocket from 'ws';
import axios from 'axios';
import { 
  DLIVE_ACCESS_TOKEN,
  DLIVE_STREAMER_USERNAME
} from './config.js';

let ws = null;
let isConnected = false;
let reconnectTimeout = null;
let keepAliveInterval = null;
let messageHandler = null;
let subscriptionId = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 3; // Máximo de intentos de reconexión antes de parar

const WS_URL = 'wss://api-ws.dlive.tv';
const WS_PROTOCOLS = ['graphql-ws']; // Subprotocol requerido por DLive
const RECONNECT_DELAY = 5000; // 5 segundos
const KEEP_ALIVE_TIMEOUT = 30000; // 30 segundos (si no recibimos "ka" en este tiempo, reconectar)
let lastKeepAlive = Date.now();

/**
 * Conecta al WebSocket de DLive y autentica
 */
async function connectDLiveWebSocket(onMessage) {
  return new Promise(async (resolve, reject) => {
    try {
      if (!DLIVE_STREAMER_USERNAME) {
        throw new Error('Se requiere DLIVE_STREAMER_USERNAME en .env');
      }

      // Crear conexión WebSocket con subprotocol requerido
      ws = new WebSocket(WS_URL, WS_PROTOCOLS);

      ws.on('open', () => {
        console.log('🔗 [DLive] WebSocket conectado, autenticando...');
        lastKeepAlive = Date.now();
        
        // Enviar mensaje de inicialización con token (si existe)
        const initMessage = {
          type: 'connection_init',
          payload: {}
        };

        // Solo añadir authorization si tenemos token
        if (DLIVE_ACCESS_TOKEN) {
          initMessage.payload.authorization = DLIVE_ACCESS_TOKEN;
        } else {
          console.warn('⚠️ [DLive] No se proporcionó token, intentando conexión sin autenticación...');
          console.warn('⚠️ [DLive] Nota: Algunas funcionalidades pueden requerir autenticación');
        }

        ws.send(JSON.stringify(initMessage));
      });

      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          handleWebSocketMessage(message, onMessage);
        } catch (err) {
          console.error('❌ [DLive] Error parseando mensaje:', err.message);
        }
      });

      ws.on('error', (err) => {
        console.error('❌ [DLive] Error en WebSocket:', err.message);
        isConnected = false;
        reject(err);
      });

      ws.on('close', (code, reason) => {
        console.log(`⚠️ [DLive] WebSocket cerrado (código: ${code})`);
        isConnected = false;
        stopKeepAlive();
        
        // Si se cierra inmediatamente sin autenticación, probablemente requiere token
        if (code === 1006 && !DLIVE_ACCESS_TOKEN) {
          console.error('❌ [DLive] El WebSocket se cerró inmediatamente. DLive probablemente requiere autenticación.');
          console.error('💡 [DLive] Necesitas obtener un DLIVE_ACCESS_TOKEN. Consulta DLIVE_SETUP.md');
          reconnectAttempts = MAX_RECONNECT_ATTEMPTS; // Marcar como alcanzado el máximo
          return;
        }
        
        // Intentar reconectar solo si no hemos excedido el máximo de intentos
        if (messageHandler && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++;
          reconnectTimeout = setTimeout(() => {
            console.log(`🔄 [DLive] Intentando reconectar... (intento ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
            connectDLiveWebSocket(messageHandler).catch(err => {
              console.error('❌ [DLive] Error en reconexión:', err.message);
            });
          }, RECONNECT_DELAY);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
          console.error('❌ [DLive] Máximo de intentos de reconexión alcanzado. Deteniendo intentos.');
          console.error('💡 [DLive] Verifica tus credenciales o que DLive esté disponible.');
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
    // Manejar diferentes tipos de mensajes
    if (message.type === 'connection_ack') {
          // Confirmación de conexión - ahora suscribirse al chat
          console.log('✅ [DLive] Autenticación exitosa, suscribiéndose al chat...');
          isConnected = true;
          reconnectAttempts = 0; // Resetear contador de intentos al conectar exitosamente
          subscribeToChat();
          startKeepAlive();
    } else if (message.type === 'ka') {
      // Keep-alive del servidor
      lastKeepAlive = Date.now();
    } else if (message.type === 'data' && message.payload) {
      // Mensaje de datos (chat)
      handleChatData(message.payload, onMessage);
    } else if (message.type === 'error') {
      console.error('❌ [DLive] Error del servidor:', message.payload);
    } else if (message.type === 'complete') {
      // Suscripción completada
      console.log('✅ [DLive] Suscripción completada');
    }
  } catch (err) {
    console.error('❌ [DLive] Error procesando mensaje:', err.message);
  }
}

/**
 * Suscribe al chat del streamer
 */
function subscribeToChat() {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }

  // Generar ID único para la suscripción
  subscriptionId = `sub_${Date.now()}`;

  // Query GraphQL para suscribirse a mensajes de chat
  const subscriptionQuery = `subscription {
    streamMessageReceived(streamer: "${DLIVE_STREAMER_USERNAME}") {
      __typename
      ... on ChatText {
        type
        id
        content
        createdAt
        sender {
          username
          displayname
          avatar
        }
        role
        roomRole
        subscribing
      }
    }
  }`;

  const subscribeMessage = {
    id: subscriptionId,
    type: 'start',
    payload: {
      query: subscriptionQuery
    }
  };

  ws.send(JSON.stringify(subscribeMessage));
  console.log(`📡 [DLive] Suscrito al chat de ${DLIVE_STREAMER_USERNAME}`);
}

/**
 * Maneja datos de chat recibidos
 */
function handleChatData(payload, onMessage) {
  try {
    if (payload.data && payload.data.streamMessageReceived) {
      const messages = payload.data.streamMessageReceived;
      
      // Puede ser un array o un objeto único
      const messageArray = Array.isArray(messages) ? messages : [messages];
      
      messageArray.forEach(msg => {
        // Solo procesar mensajes tipo ChatText
        if (msg.__typename === 'ChatText' && msg.content) {
          const formatted = {
            platform: 'dlive',
            username: msg.sender?.displayname || msg.sender?.username || 'anon',
            message: msg.content || '',
            timestamp: msg.createdAt ? new Date(msg.createdAt).getTime() : Date.now()
          };
          
          if (formatted.message.trim()) {
            onMessage(formatted);
            console.log(`💬 [DLive] Mensaje: ${formatted.username}: ${formatted.message}`);
          }
        }
      });
    }
  } catch (err) {
    console.error('❌ [DLive] Error procesando datos de chat:', err.message);
  }
}

/**
 * Inicia el keep-alive para verificar la conexión
 */
function startKeepAlive() {
  stopKeepAlive();
  
  keepAliveInterval = setInterval(() => {
    const timeSinceLastKeepAlive = Date.now() - lastKeepAlive;
    
    // Si no recibimos "ka" en más de 30 segundos, reconectar
    if (timeSinceLastKeepAlive > KEEP_ALIVE_TIMEOUT) {
      console.warn('⚠️ [DLive] No se recibió keep-alive, reconectando...');
      if (ws) {
        ws.close();
      }
    }
  }, 10000); // Verificar cada 10 segundos
}

/**
 * Detiene el keep-alive
 */
function stopKeepAlive() {
  if (keepAliveInterval) {
    clearInterval(keepAliveInterval);
    keepAliveInterval = null;
  }
}

/**
 * Conecta al chat de DLive
 */
export async function connectDLive(onMessage) {
  console.log('🔧 [DLive] Iniciando servicio...');
  
  messageHandler = onMessage;
  
  if (!DLIVE_STREAMER_USERNAME) {
    console.error('❌ [DLive] Falta DLIVE_STREAMER_USERNAME en .env');
    return;
  }

  if (!DLIVE_ACCESS_TOKEN) {
    console.warn('⚠️ [DLive] No se proporcionó DLIVE_ACCESS_TOKEN');
    console.warn('⚠️ [DLive] Intentando conectar sin token (puede fallar si DLive requiere autenticación)');
    console.warn('💡 [DLive] Para obtener un token, consulta DLIVE_SETUP.md o usa el script helper');
  }

  try {
    reconnectAttempts = 0; // Resetear contador al iniciar
    await connectDLiveWebSocket(onMessage);
    console.log('✅ [DLive] Servicio iniciado');
  } catch (err) {
    console.error('❌ [DLive] Error conectando:', err.message);
    
    // Solo intentar reconectar si no hemos excedido el máximo
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      reconnectTimeout = setTimeout(() => {
        console.log(`🔄 [DLive] Intentando reconectar... (intento ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        connectDLive(onMessage).catch(err => {
          console.error('❌ [DLive] Error en reconexión:', err.message);
        });
      }, RECONNECT_DELAY);
    } else {
      console.error('❌ [DLive] Máximo de intentos de reconexión alcanzado. Deteniendo.');
      console.error('💡 [DLive] Verifica tus credenciales o que DLive esté disponible.');
    }
  }
}

/**
 * Desconecta del chat de DLive
 */
export async function disconnectDLive() {
  stopKeepAlive();
  
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  
  // Cancelar suscripción si existe
  if (ws && ws.readyState === WebSocket.OPEN && subscriptionId) {
    try {
      const stopMessage = {
        id: subscriptionId,
        type: 'stop'
      };
      ws.send(JSON.stringify(stopMessage));
    } catch (err) {
      // Ignorar errores al cancelar suscripción
    }
  }
  
  if (ws) {
    ws.close();
    ws = null;
  }
  
  isConnected = false;
  messageHandler = null;
  subscriptionId = null;
  console.log('🛑 [DLive] Desconectado');
}

