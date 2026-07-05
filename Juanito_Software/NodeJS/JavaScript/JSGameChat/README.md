# GameChat2

Juego en navegador controlado por el **chat** (Twitch, Kick, YouTube...) y mostrado en **OBS** como **Browser Source**.

## Esquema del flujo

```
Chat (Twitch/Kick/YouTube) → Node.js (bot) → Socket.io → Juego (HTML5/Canvas)
                                                              ↓
                                              OBS Browser Source (localhost:3000/game)
```

## Requisitos

- Node.js 18+
- (Opcional) Cuenta Twitch y [token OAuth](https://twitchapps.com/tmi/) para el chat

## Instalación

```bash
npm install
```

## Uso

### 1. Arrancar el servidor y el juego

```bash
npm start
```

Se abre el servidor en **http://localhost:3000**. La ruta del juego es **http://localhost:3000/game**.

### 2. Añadir el juego en OBS

1. En OBS: **Fuentes** → **Añadir** → **Fuente de navegador (Browser Source)**.
2. URL: `http://localhost:3000/game`
3. Ajusta ancho/alto (ej: 1920x1080) y acepta.

El canvas del juego se verá en escena. Si no usas Twitch aún, puedes probar eventos desde la consola del servidor o añadiendo un cliente de prueba.

### 3. (Opcional) Conectar Twitch para que el chat controle el juego

1. Crea un archivo `.env` a partir de `.env.example`.
2. Rellena `TWITCH_CHANNEL`, `TWITCH_USER` y `TWITCH_OAUTH` (generar en [twitchapps.com/tmi](https://twitchapps.com/tmi/)).
3. Arranca con Twitch:

```bash
npm run twitch
```

Los comandos del chat se reenvían al juego en tiempo real.

## Comandos de chat (ejemplo)

| Chat       | Acción en el juego |
|-----------|---------------------|
| `!jump` / `!salta` | El personaje salta |
| `!left` / `!izquierda` | Mueve a la izquierda |
| `!right` / `!derecha` | Mueve a la derecha |
| `!attack` / `!ataca` | Ataque |
| `!vote izquierda` / `!vote derecha` | Votación (ejemplo) |

Los comandos se definen en `server/twitch-chat.js` y los eventos en `public/game.js`.

## Estructura del proyecto

```
GameChat2/
├── server/
│   ├── index.js        # Express + Socket.io + ruta /game
│   └── twitch-chat.js  # Escucha Twitch y emite eventos al juego
├── public/
│   ├── game.html       # Página del juego (Browser Source)
│   └── game.js         # Lógica y Canvas, escucha Socket.io
├── package.json
├── .env.example
└── README.md
```

## Ampliar el juego

- **Más comandos**: edita `COMANDOS` en `server/twitch-chat.js` y añade los `socket.on(...)` correspondientes en `public/game.js`.
- **Otra plataforma (Kick, YouTube)**: crea un módulo similar a `twitch-chat.js` que escuche el chat y llame a `broadcastToGame(nombreEvento, datos)`.
- **Motor de juego**: puedes sustituir el Canvas vanilla por **Phaser.js** o **Three.js** y seguir usando los mismos eventos de Socket.io.

## Licencia

MIT
