# 💬🖥️ Unified Chat Widget + TTS - Ficha Técnica

**Licencia:** Uso No Comercial  

---

## 🧾 Descripción  

Unified Chat Widget es una aplicación desarrollada en Node.js que permite centralizar en tiempo real los mensajes de chat de Twitch, YouTube y Kick en un único widget web, ideal para streamers que quieran mostrar todos sus chats en OBS y, además, ofrecer lectura automática de mensajes mediante TTS (Text-to-Speech).

Combina servidor HTTP + WebSocket, persistencia de mensajes en JSON y un sistema de TTS opcional para crear una experiencia interactiva completa.

---

## 📦🛠️ Características principales

- 🌐 Unificación de chats de Twitch, YouTube y Kick.
- 💻 Widget HTML para incrustar en OBS como fuente de navegador.
- 🔄 Comunicación en tiempo real mediante WebSockets.
- 🗣️ TTS en español opcional mediante servidor Flask + librería TTS.
- 🗂️ Historial persistente de mensajes en messages/latest.json (hasta 100 últimos mensajes).
- 🎛️ **Comandos de control desde chat:**
  - `\TTS_ON` → Activar locución (solo admins autorizados).  
  - `\TTS_OFF` → Desactivar locución. 
- 🔒 Administradores autorizados configurables (TTS_ADMINS).
- 🚫 Filtrado de comandos y prefijos especiales (/, !, \, -) para evitar lecturas innecesarias.
- ⚡ Compatible con Windows, Linux y macOS.
- 📝 Registro de mensajes en consola para depuración y seguimiento.

---

## 🔧 Requisitos

- Node.js 18 o superior.
- OBS Studio para incrustar el widget.
- Credenciales de API de Twitch, YouTube y Kick.
- Servidor TTS opcional: Python + Flask + librería TTS.

---

## 📚 Estructura del proyecto
- unified-chat-widget/
- ├── libs/
- │   └── kick-js
- ├── utils/
- │   └── saveMessage.js
- ├── package.json
- ├── .env
- ├── index.js
- ├── services/
- │   ├── twitch.js
- │   ├── youtube.js
- │   └── kick.js
- ├── public/
- │   └── chat.html
- └── messages/
-     └── latest.json

- index.js → Servidor principal, manejo de WebSockets y TTS.
- services/ → Conexiones con cada plataforma (Twitch, YouTube, Kick).
- public/chat.html → Widget web para incrustar en OBS.
- messages/latest.json → Almacena los últimos 100 mensajes recibidos.

---

## 🛠️ Dependencias principales

| Módulo                 | Descripción                                         |
| ---------------------- | --------------------------------------------------- |
| express                | Servidor HTTP y gestión de rutas estáticas          |
| tmi.js                 | Conexión y escucha de chat de Twitch                |
| dotenv                 | Gestión de variables de entorno                     |
| axios                  | Realizar peticiones HTTP (TTS y APIs)               |
| @pagoru/kick\_live\_ws | Conexión a chat de Kick vía WebSocket               |
| ws                     | Servidor WebSocket para comunicación en tiempo real |

---

## 🚀 Instalación

1.Clonar repositorio:

git clone https://github.com/tuusuario/unified-chat-widget.git
cd unified-chat-widget

2. Instalar dependencias:

npm install express tmi.js dotenv axios @pagoru/kick_live_ws

3. Configurar archivo .env con credenciales de las plataformas.

---

## ▶️ Ejecución

node index.js

- El servidor se ejecuta por defecto en http://127.0.0.1:3000.
- Inicia la conexión a todos los chats y WebSocket para el widget.
- Si TTS está habilitado, los mensajes se leen automáticamente a través del servidor TTS.

---

## 📃 Licencia

Este programa tiene un licencia perosnalizada de uso no comercial

Consulta la licencia completa para más detalles. Más información: LICENSE.txt

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com

---

