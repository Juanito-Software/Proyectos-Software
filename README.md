# Proyectos-Software — © 2025 Juanito Software

Monorepo personal con los proyectos de software de **Juanito Software**: aplicaciones,
utilidades y herramientas en Java, Python, JavaScript/TypeScript, PHP y Rust.

Antes de utilizar, distribuir o modificar cualquier proyecto, revisa la licencia específica
que lo acompaña. Este repositorio no implica por sí mismo derechos de uso sobre todo su
contenido: las condiciones varían según el programa.

---

## 📁 Estructura del repositorio

```
Proyectos-Software/
├── Doc/                    # Vault de Obsidian: apuntes, plantillas y documentación transversal
├── Juanito_Software/       # Todos los proyectos, agrupados por lenguaje/plataforma
│   ├── Java/
│   ├── Laravel/
│   ├── NodeJS/
│   ├── Python/
│   ├── Rust/
│   └── libraries/          # Librerías compartidas entre proyectos
└── README.md
```

Convención por proyecto: cada proyecto es autocontenido e incluye su `README.md`,
su licencia (`LICENSE.txt` / `Licencia/`), sus dependencias declaradas
(`requirements.txt`, `pom.xml`, `package.json`, `composer.json`, `Cargo.toml`)
y, cuando aplica, una carpeta `docs/` con notas y documentación adicional.

---

## 📦 Catálogo de proyectos

### ☕ Java

| Proyecto | Descripción |
|---|---|
| `BatchProcessor` | Procesamiento por lotes con Spring Boot / Spring Batch |
| `HashTools` | Utilidades de hashing y criptografía (validación de contraseñas, AES) |
| `RadioStack` | Emisora de radio por internet multi-módulo (core, api, persistence, stream, admin) sobre Icecast |
| `Spring/` | Ejercicios y pruebas con Spring Boot y Spring Batch |
| `SpringlessEasyBatcher` | Motor de batching sin Spring — software propietario, código no incluido (ver su README) |
| `others/` | Utilidades varias: `EscribirNombresArchivos`, `ServidorJuegos`, `XlsxToCsvConverter` |

### 🐘 PHP / Laravel

| Proyecto | Descripción |
|---|---|
| `gym-app` | Aplicación de gestión de gimnasio (Laravel + Vite + Tailwind). Documentación de entrega y dumps SQL en `docs/` |

### 🟨 JavaScript / TypeScript (NodeJS)

| Proyecto | Descripción |
|---|---|
| `JavaScript/JSGameChat` | Chat en tiempo real orientado a juegos |
| `JavaScript/TaskHub` | Gestor de tareas (variante JavaScript) |
| `JavaScript/unified-chat-widget` | Widget de chat embebible |
| `TypeScript/Angular/TaskHub` | Frontend del gestor de tareas en Angular |
| `TypeScript/React/TaskHubPro` | Frontend del gestor de tareas en React |

### 🐍 Python

| Proyecto | Descripción |
|---|---|
| `AI_DuoTalk` | Conversación por voz entre agentes de IA locales |
| `AudioEffects/` | Visualizaciones y efectos de audio: `AudioSpaceEffect`, `MusicWave`, `TunelAnimation` |
| `cuajaos_voice_chat` | Chat de voz LAN (variantes grupal y 1v1) |
| `Enviar_Archivos_Python` | Envío de archivos entre equipos |
| `FFMPEG_UI` | Convertidor de audio con interfaz Qt sobre FFmpeg |
| `Flask/LeaderBoard_Unity` | API web de puntuaciones para juegos Unity |
| `FPS-AI-Toolkit` | Herramientas de IA para juegos FPS |
| `GPTDevTeam` | Pipeline multi-agente de generación y testeo de código con LLMs locales (Ollama) |
| `MisServidores/` | Servidores FTP y WEB básicos |
| `OmniForge` | Sistema de agentes con visión por computador |
| `PC_Health_Sistema` | Monitorización de salud del sistema |
| `PyGameChat` | Chat para juegos en Python |
| `Radio_Python` | Radio por software |
| `Reproductor_Python` | Reproductor multimedia |
| `Simulaciones/` | Simulaciones: juego de la vida de Conway, Fibonacci |
| `SpotifyDownloader` | Descarga de audio |
| `SpringlessEasyBatcher` | Versión Python del motor de batching (propietario) |
| `StreamTools/` | Utilidades para streamers: `BackCount`, `ContadorOBS`, `ClipsGeneration`, `VODsGeneration` |
| `TaskHub` | Backend del gestor de tareas estilo Kanban (FastAPI, JWT) |
| `ToDoList` | Lista de tareas de escritorio |
| `VocoderSynth` | Vocoder en tiempo real |
| `YoutubeToMp3` / `YoutubeToMp4` | Descarga y conversión de vídeo/audio |

### 🦀 Rust

| Proyecto | Descripción |
|---|---|
| `MisServidores/` | Servidores FTP y WEB básicos |
| `motorIndexado` | Motor de indexado y búsqueda de texto |

### 📚 Librerías compartidas

| Proyecto | Descripción |
|---|---|
| `libraries/shared-py/pyseed` | Utilidades Python compartidas entre proyectos |

> Las tecnologías en aprendizaje y el plan de estudio se mantienen en [`ROADMAP.md`](ROADMAP.md).

---

## ⚖️ Licencias

- Este repositorio **no tiene una licencia general única**.
- Cada proyecto incluye su propia licencia individual en su directorio
  (`LICENSE.txt`, `LICENSE_ES.txt` y/o `README.md`).

Tipos de software incluidos:

- **Software libre** — proyectos bajo licencias abiertas como GNU GPL v3.
- **Software de libre uso (no comercial)** — uso gratuito con limitaciones según se indique.
- **Software comercial** — licencias personalizadas que regulan su explotación.

Si tienes dudas sobre el uso permitido de un proyecto concreto, consulta su
documentación o contáctame.

## ⚠️ Advertencia

Este repositorio contiene proyectos de investigación y experimentales. Las dependencias
no se mantienen activamente a menos que se especifique lo contrario.

---

©️ 2025 JuanitoSoftware · [bernaldezperedaj@gmail.com](mailto:bernaldezperedaj@gmail.com)
