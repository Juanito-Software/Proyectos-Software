// utils/globalMessages.js
// import { appendLatestJson } from './saveMessage.js'; // ← Importa la función correctamente

const MAX_MESSAGES = 100;
const MESSAGE_LIFETIME_MS = 40 * 1000; // 40 segundos en milisegundos
const messages = [];

//Para HTTP
/*
export function addMessage(msg) {
  const now = Date.now();
  messages.push(msg);

  // Filtrar mensajes que no hayan expirado (menos de 40 segundos)
  while (messages.length > 0 && now - messages[0].timestamp > MESSAGE_LIFETIME_MS) {
    messages.shift();
  }

  // Si superamos el máximo, eliminamos el más antiguo
  if (messages.length > MAX_MESSAGES) {
    messages.shift();
  }
  appendLatestJson(messages)
}

export function getMessages() {
  return messages;
}
*/
