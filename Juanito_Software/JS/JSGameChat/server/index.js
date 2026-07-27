/**
 * Servidor GameChat2
 * - Sirve el juego en /game (para OBS browser source)
 * - Socket.io: recibe conexiones del juego y emite eventos desde el chat
 * - Opcional: conecta con Twitch (tmi.js) y reenvía comandos al juego
 */

require('dotenv').config();
const path = require('path');
const http = require('http');
const express = require('express');
const rateLimit = require('express-rate-limit');
const { Server } = require('socket.io');

const app = express();

// Limite de peticiones.
//
// El juego lo carga la fuente de navegador de OBS, asi que en uso normal son
// unas pocas peticiones al arrancar. El limite es holgado a proposito: no
// pretende frenar un ataque, sino que una pestaña recargando en bucle no sature
// el proceso, que es de un solo hilo y atiende tambien los websockets del juego.
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 300,
  standardHeaders: true,
  legacyHeaders: false,
});
const server = http.createServer(app);
const io = new Server(server);

const PORT = process.env.PORT || 3000;

// Carpeta pública (HTML, CSS, JS del juego)
app.use(express.static(path.join(__dirname, '..', 'public')));

// Ruta principal → redirige al juego
app.get('/', apiLimiter, (req, res) => {
  res.redirect('/game');
});

// Ruta del juego (OBS: añadir como Browser Source → http://localhost:3000/game)
app.get('/game', apiLimiter, (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'game.html'));
});

// --- Socket.io: comunicación en tiempo real con el juego ---

io.on('connection', (socket) => {
  console.log('[Socket] Cliente conectado:', socket.id);

  socket.on('disconnect', () => {
    console.log('[Socket] Cliente desconectado:', socket.id);
  });
});

// Función para enviar un comando del chat al juego (todos los clientes)
function broadcastToGame(eventName, data = {}) {
  io.emit(eventName, { ...data, timestamp: Date.now() });
  console.log('[Game] Evento enviado:', eventName, data);
}

// Exportar para que el módulo de chat pueda usarlo
module.exports = { io, broadcastToGame, server };

// --- Inicio del servidor ---

server.listen(PORT, () => {
  console.log(`\n  GameChat2 corriendo en http://localhost:${PORT}`);
  console.log(`  OBS: Añade Browser Source → http://localhost:${PORT}/game\n`);
});

// --- Opcional: conectar Twitch si se pasa --twitch ---
const useTwitch = process.argv.includes('--twitch');
if (useTwitch) {
  const twitch = require('./twitch-chat');
  twitch.start(module.exports);
}
