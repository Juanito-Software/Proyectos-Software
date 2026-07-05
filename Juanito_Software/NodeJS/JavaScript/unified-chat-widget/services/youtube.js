import axios from "axios";
//import { addMessage, getMessages } from "../utils/globalMessages.js";
//import { appendLatestJson } from "../utils/saveMessage.js";
import { YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID } from "./config.js";

let nextPageToken = null;

async function fetchLiveChatId() {
  if (!YOUTUBE_API_KEY || !YOUTUBE_CHANNEL_ID) {
    console.error("❌ Faltan credenciales YouTube en .env");
    return null;
  }
  
  try {
    const searchRes = await axios.get("https://www.googleapis.com/youtube/v3/search", {
      params: {
        part: "snippet",
        channelId: YOUTUBE_CHANNEL_ID,
        eventType: "live",
        type: "video",
        key: YOUTUBE_API_KEY,
      },
    });

    //Youtube solo permite leer y escribir en el chat cuando hay una emision activa
    if (!searchRes.data.items?.length) {
      console.log("🔴 No hay transmisión activa en YouTube.");
      return null;
    }

    const videoId = searchRes.data.items[0].id.videoId;

    const videoRes = await axios.get("https://www.googleapis.com/youtube/v3/videos", {
      params: {
        part: "liveStreamingDetails",
        id: videoId,
        key: YOUTUBE_API_KEY,
      },
    });

    const liveChatId = videoRes.data.items?.[0]?.liveStreamingDetails?.activeLiveChatId;

    if (!liveChatId) {
      console.log("❌ No se encontró liveChatId.");
      return null;
    }

    return liveChatId;
  } catch (err) {
    console.error("🛑 Error al obtener liveChatId:", err.response?.data?.error?.message || err.message);
    return null;
  }
}

async function fetchNewMessages(liveChatId, onMessage) {
  try {
    const response = await axios.get("https://www.googleapis.com/youtube/v3/liveChat/messages", {
      params: {
        liveChatId,
        part: "snippet,authorDetails",
        pageToken: nextPageToken,
        key: YOUTUBE_API_KEY,
      },
    });

    nextPageToken = response.data.nextPageToken;

    const messages = response.data.items
      .filter(item => item.snippet.type === "textMessageEvent")
      .map(item => ({
        platform: "YouTube",
        username: item.authorDetails.displayName,
        message: item.snippet.displayMessage,
        timestamp: Date.now()
      }));

    //return messages;
    messages.forEach(onMessage);
  } catch (err) {
    console.error("⚠️ Error al obtener mensajes:", err.response?.data?.error?.message || err.message);
    return [];
  }
}

// Para HTTP
/*
async function pollMessages(liveChatId) {
  setInterval(async () => {
    const newMessages = await fetchNewMessages(liveChatId);
    newMessages.forEach(msg => addMessage(msg));
    appendLatestJson(getMessages());
  }, 5000);
}
*/

export async function connectYouTube(onMessage) {
  const liveChatId = await fetchLiveChatId();
  if (liveChatId) {
    console.log("✅ Conectado al chat en vivo de YouTube.");
    //pollMessages(liveChatId);
    setInterval(() => fetchNewMessages(liveChatId, onMessage), 60000);
  }
}
