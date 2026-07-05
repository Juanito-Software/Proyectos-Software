/**
 * Juego mínimo: un cuadro que reacciona a comandos del chat vía Socket.io.
 * Eventos: playerJump, moveLeft, moveRight, attack, vote
 * Ideal para OBS como Browser Source (http://localhost:3000/game)
 */

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');
const lastEventEl = document.getElementById('lastEvent');

// Ajustar canvas al tamaño de la ventana (y a la fuente de OBS)
function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

// Estado del "personaje" (un rectángulo)
const player = {
  x: 100,
  y: 200,
  w: 60,
  h: 60,
  vy: 0,
  jumpForce: -14,
  gravity: 0.6,
  groundY: 200,
  color: '#7bed9f',
  lastAction: '',
};

// Conectar Socket.io
const socket = io();

socket.on('connect', () => {
  statusEl.textContent = 'Conectado';
  statusEl.style.color = '#7bed9f';
});

socket.on('disconnect', () => {
  statusEl.textContent = 'Desconectado';
  statusEl.style.color = '#ff6b6b';
});

// Mapeo de eventos del chat → acciones en el juego
socket.on('playerJump', (data) => {
  if (Math.abs(player.vy) < 0.1) player.vy = player.jumpForce;
  showEvent('JUMP', data.user);
});

socket.on('moveLeft', (data) => {
  player.x = Math.max(20, player.x - 40);
  showEvent('LEFT', data.user);
});

socket.on('moveRight', (data) => {
  player.x = Math.min(canvas.width - player.w - 20, player.x + 40);
  showEvent('RIGHT', data.user);
});

socket.on('attack', (data) => {
  player.lastAction = 'attack';
  setTimeout(() => { player.lastAction = ''; }, 400);
  showEvent('ATTACK', data.user);
});

socket.on('vote', (data) => {
  if (data.option) showEvent(`VOTE ${data.option.toUpperCase()}`, data.user);
});

function showEvent(action, user) {
  lastEventEl.textContent = `${user || '?'}: ${action}`;
  lastEventEl.style.opacity = '1';
  setTimeout(() => { lastEventEl.style.opacity = '0.5'; }, 1500);
}

// Física y dibujo
function update() {
  player.vy += player.gravity;
  player.y += player.vy;
  if (player.y >= player.groundY) {
    player.y = player.groundY;
    player.vy = 0;
  }
}

function draw() {
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Suelo
  ctx.fillStyle = '#16213e';
  ctx.fillRect(0, player.groundY + player.h, canvas.width, canvas.height);

  // Personaje
  ctx.fillStyle = player.color;
  ctx.fillRect(player.x, player.y, player.w, player.h);

  if (player.lastAction === 'attack') {
    ctx.fillStyle = '#ff6b6b';
    ctx.fillRect(player.x + player.w, player.y + player.h / 2 - 10, 25, 20);
  }
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

loop();
