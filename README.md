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
│   ├── JS/                 # Ecosistema JavaScript/TypeScript (Node, Angular, React)
│   ├── PHP/
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

### 🐘 PHP

| Proyecto | Descripción |
|---|---|
| `PHP/Laravel/gym-app` | Aplicación de gestión de gimnasio (Laravel + Vite + Tailwind). Documentación de entrega y dumps SQL en `docs/` |

### 🟨 JS — JavaScript / TypeScript

| Proyecto | Descripción |
|---|---|
| `JS/JSGameChat` | juego para el chat en tiempo real |
| `JS/TaskHub` | Gestor de tareas (variante JavaScript, cliente + servidor) |
| `JS/unified-chat-widget` | Widget de chat multiplataforma embebible |
| `JS/Angular/TaskHub` | Gestor de tareas fullstack en TypeScript (frontend Angular + backend Express/Prisma) |
| `JS/React/TaskHubPro` | Gestor de tareas en TypeScript (variante React) |

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
| `PyGameChat` | juego para el chat en tiempo real |
| `Radio_Python` | Radio por software |
| `Reproductor_Python` | Reproductor multimedia |
| `Simulaciones/` | Simulaciones: juego de la vida de Conway, Fibonacci |
| `SpotifyDownloader` | Descarga de audio |
| `SpringlessEasyBatcher` | Versión gratuita en Python del motor de batching (no comercial) |
| `StreamTools/` | Utilidades para streamers: `BackCount`, `ClipsGeneration`, `VODsGeneration` |
| `FastApi/TaskHub` | Gestor de tareas estilo Kanban (backend FastAPI con JWT + frontend React) |
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
| `libraries/shared-py/pyseed` | Libreria para la generación de la estructura de proyectos en python |

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

## 🔒 Mantenimiento y seguridad

Las dependencias y las alertas de seguridad **se mantienen de forma activa**. El
análisis estático (CodeQL), Dependabot y el escaneo de secretos están habilitados
sobre `main`, y el criterio de trabajo es **corregir en lugar de silenciar**: una
alerta solo se descarta cuando no tiene arreglo posible, y siempre con el motivo
registrado.

Estado actual:

| Sistema | Estado |
| --- | --- |
| Análisis de código (CodeQL) | **0 abiertas** de 256 · las diez familias de problemas corregidas |
| Escaneo de secretos | Revisado · credenciales expuestas retiradas y revocadas |
| Dependabot (npm, Maven) | Saneado · quedan alertas bloqueadas aguas arriba, deliberadamente abiertas |
| Dependabot (pip) | **En curso** — es el bloque pendiente |

De las 256 alertas de análisis de código, la inmensa mayoría se cerró porque el
código dejó de tener el problema, no por descarte manual.

El historial completo de cada intervención, con las alternativas consideradas y
el motivo de cada decisión, está en [`MAINTENANCE.md`](MAINTENANCE.md).

## ⚠️ Advertencia

Este repositorio contiene proyectos de investigación y experimentales. Varios son
ejercicios de aprendizaje y no están pensados para uso en producción; cuando un
proyecto tiene limitaciones conocidas, están documentadas en su propio código.

---

©️ 2025–2026 JuanitoSoftware · [bernaldezperedaj@gmail.com](mailto:bernaldezperedaj@gmail.com)
