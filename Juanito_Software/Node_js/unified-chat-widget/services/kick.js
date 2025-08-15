import { createClient } from "../libs/kick-js/dist/index.js"; 
//import { addMessage, getMessages } from "../utils/globalMessages.js";
//import { appendLatestJson } from "../utils/saveMessage.js";
import { KICK_CHANNEL, KICK_BEARER_TOKEN, KICK_COOKIES } from './config.js';

let conectado = false;

export async function connectKick(onMessage) {
  console.log("🔧 [Kick] Iniciando servicio...");

  if (!KICK_CHANNEL || !KICK_BEARER_TOKEN || !KICK_COOKIES) {
    console.error("❌ Faltan credenciales Kick en .env");
    return;
  }

  let client;
  try {
    client = createClient(KICK_CHANNEL, { logger: false, readOnly: true });
    console.log("✅ [Kick] Cliente creado para canal:", KICK_CHANNEL);
  } catch (err) {
    console.error("❌ [Kick] Error creando cliente:", err);
    return;
  }

  try {
    client.on("ChatMessage", (msg) => {
      const formattedMessage = {
        platform: "kick",
        username: msg.sender?.username || "anon",
        message: msg.content || "",
        timestamp: Date.now()
      };
      onMessage(formattedMessage);
      //addMessage(formattedMessage);
      //appendLatestJson(getMessages());
      console.log("💬 [Kick] Nuevo mensaje:", formattedMessage.message);
    });

    client.on("event", (ev) => {
      console.log(`📡 [Kick] Evento '${ev.event}'`, ev);
      if (ev.event === "pusher_internal:subscription_succeeded" && !conectado) {
        conectado = true;
        console.log(`✅ [Kick] Conectado al chat de ${KICK_CHANNEL}`);
      }
    });

    const knownEvents = ["ready", "connected", "error", "disconnect", "close"];
    knownEvents.forEach(evt => {
      client.on(evt, (...args) => {
        console.log(`📡 [Kick] ${evt}`, ...args);
        if (evt === "ready" && !conectado) {
          conectado = true;
          console.log(`✅ [Kick] Ready en ${KICK_CHANNEL}`);
        }
      });
    });
  } catch(e) {
    console.error('❌ Error en Kick:', e);
  }
}
