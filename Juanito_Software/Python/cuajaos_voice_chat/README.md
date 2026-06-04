# 🎙️ Cuajaos Voice Chat — Sistema de Chat de Voz RTP

**Autor:** JuanitoSoftware&Games · **Versión:** 0.9 (EN DESARROLLO) · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## ⚠️ ESTADO DEL PROYECTO: WORK IN PROGRESS

Este proyecto **está en desarrollo activo** y no se considera completamente estable. Se esperan:
- Cambios significativos en la arquitectura
- Refactorización de componentes
- Posibles errores y fallos no documentados
- APIs y formatos que pueden cambiar sin aviso

**Se recomienda usar solo con fines educativos y experimentales en este momento.**

---

## 🧾 Descripción

Suite de sistemas de **comunicación de voz en tiempo real** sobre redes locales, utilizando el protocolo **RTP (Real-time Transport Protocol)** sobre UDP. Incluye múltiples versiones, desde simples comunicaciones 1v1 hasta arquitecturas P2P descentralizadas con gestión dinámica de hosts.

Todas las versiones implementan **compresión de audio con codec Opus** para minimizar ancho de banda mientras se mantiene baja latencia.

---

## 🚀 Características Principales

### Versiones Disponibles

| Versión | Tipo | Usuarios | Complejidad | Estado |
|---|---|---|---|---|
| **CuajaosFamilyVoiceChat1v1** | Point-to-Point | 2 | Baja | Estable |
| **CuajaosFamilyVoiceChat** | Hub/Servidor | 4-8 | Media | Funcional |
| **God Loquete** | P2P Descentralizado | 4+ | Alta | En desarrollo |

### Características Generales
- 🎧 **Compresión Opus**: códec de audio de alta calidad y bajo ancho de banda
- 📡 **Protocolo RTP**: encapsulación estándar para transmisión de audio con timestamps y secuenciación
- 🎙️ **Captura y reproducción de audio en tiempo real**: via `pyaudio`
- 🖥️ **Interfaz gráfica intuitiva**: Tkinter con indicadores de estado
- 🔊 **Control de volumen y calidad**: ajustables en tiempo real

### Características Avanzadas (God Loquete)
- 🔄 **Arquitectura descentralizada P2P**: sin servidor central obligatorio
- 💓 **Heartbeat y detección de caída de host**: recuperación automática
- 🎚️ **Mezcla de audio multi-cliente**: el host mezcla y redistribuye
- 📦 **Buffer inteligente con deque**: manejo de jitter y pérdidas
- 🌐 **Servidor TCP**: coordinación y descubrimiento de IPs
- 📊 **Logging estructurado**: registro detallado de eventos

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.9 o superior
- **Audio hardware:** micrófono y altavoces/auriculares conectados
- **Red:** conectividad LAN entre dispositivos

### Dependencias Python

```bash
pip install numpy pyaudio pyogg Pillow pyrtp
```

**Nota sobre instalación:** `pyaudio` requiere dependencias del sistema:
- **Windows**: debería funcionar con pip install
- **macOS**: `brew install portaudio` + `pip install pyaudio`
- **Linux**: `sudo apt install portaudio19-dev python3-dev` + `pip install pyaudio`

---

## 📦 Instalación

```bash
cd CuajaoVoiceChat

# Instalar dependencias
pip install numpy pyaudio pyogg Pillow pyrtp

# Verificar instalación de pyaudio
python -c "import pyaudio; print('PyAudio OK')"
```

---

## 📁 Estructura del Proyecto

```plaintext
CuajaoVoiceChat/
├── CuajaosFamilyVoiceChat1v1/
│   ├── CuajaosFamilyVoiceChat.py    # Versión point-to-point simple
│   └── README_local.md
├── CuajaosFamilyVoiceChat/
│   ├── CuajaosFamilyVoiceChat.py    # Versión multiusuario con hub
│   └── README_local.md
├── god_loquete/
│   ├── god_loquete.py               # Sistema P2P descentralizado
│   ├── rtp_handler.py               # Manejo de paquetes RTP
│   └── README_local.md
├── requirements.txt
└── README.md
```

---

## 💻 Uso y Ejecución

### 🔗 Versión 1v1 (Point-to-Point Simple)

Para comunicación directa entre **dos personas**:

```bash
cd CuajaosFamilyVoiceChat1v1
python CuajaosFamilyVoiceChat.py
```

**Flujo:**
1. Ejecuta en dos máquinas diferentes (o mismo ordenador en puertos diferentes)
2. Introduce la IP del otro participante
3. Presiona "Conectar"
4. El audio se transmite automáticamente en ambas direcciones
5. Presiona "Desconectar" para terminar

---

### 👥 Versión Multiusuario (Hub/Servidor)

Para comunicación entre **múltiples participantes** con un host centralizado:

```bash
cd CuajaosFamilyVoiceChat
python CuajaosFamilyVoiceChat.py
```

**Flujo:**
1. **Host**: ejecuta y la aplicación se pone en modo host
2. **Clientes**: ejecutan, introducen IP del host y se conectan
3. El host recibe audio de todos los clientes y redistribuye
4. Todos escuchan a todos

**Limitaciones actuales:**
- ⚠️ Máximo 4-8 usuarios (dependiendo del ancho de banda)
- ⚠️ Host debe estar siempre activo
- ⚠️ No hay fallback si el host cae

---

### 🌐 God Loquete (P2P Descentralizado - EN DESARROLLO)

Sistema avanzado con **arquitectura descentralizada** y gestión dinámica de hosts:

```bash
cd god_loquete
python god_loquete.py
```

**Flujo:**
1. Los clientes se descubren automáticamente via UDP broadcast
2. Se elige dinámicamente un host (generalmente el primero en conectarse)
3. Si el host cae, se elige un nuevo host automáticamente
4. El audio se mezcla en el host y se redistribuye
5. Presiona "Entrar" para unirse, "Salir" para desconectar

**⚠️ ESTADO:** Este módulo está **en desarrollo activo** con limitaciones conocidas:
- Detección de host caído puede ser lenta
- La mezcla de audio puede generar artefactos con muchos usuarios
- El cambio de host puede causar interrupciones temporales
- Logging y manejo de errores incompleto

---

## 🔧 Arquitectura Técnica

### Protocolos y Puertos (God Loquete)

| Funcionalidad | Protocolo | Puerto | Descripción |
|---|---|---|---|
| Gestión de conexiones | TCP | 12345 | Servidor para intercambio de IPs |
| Heartbeat / Elección de host | UDP Broadcast | 12346 | Detección de host y fallover |
| Transmisión de audio RTP | UDP | 12347 | Paquetes de audio Opus |

### Flujo de Datos (God Loquete)

```
Cliente A (RTP)
    ↓
    └→ [HOST] → mezcla audio → redistribuye → Cliente B
    ↑                                         ↓
Cliente C (RTP) ←─────────────────────────────┘
```

### Formato de Paquete RTP

```
[RTP Header (12 bytes)]
├─ Version (V): 2
├─ Padding (P): 1 bit
├─ Extension (X): 1 bit
├─ CSRC Count (CC): 4 bits
├─ Marker (M): 1 bit
├─ Payload Type (PT): 7 bits (Opus = 111)
├─ Sequence Number: 16 bits
├─ Timestamp: 32 bits
├─ SSRC: 32 bits
└─ CSRC list (variable)

[Payload - Audio Opus comprimido]
```

---

## 📊 Parámetros Configurables

Edita los scripts para ajustar:

```python
# Configuración de audio
SAMPLE_RATE = 48000         # Hz (recomendado para Opus)
CHUNK_SIZE = 960            # muestras (20ms a 48kHz)
AUDIO_FORMAT = "int16"      # formato de audio

# Compresión Opus
OPUS_BITRATE = 128000       # bits/segundo (128 kbps)
OPUS_COMPLEXITY = 9         # 0-10 (mayor = mejor pero más CPU)

# RTP
RTP_PAYLOAD_TYPE = 111      # Tipo de payload para Opus
RTP_SSRC = 12345            # Identificador de origen de sincronización

# Red
HOST_PORT = 12347           # Puerto UDP para audio
BROADCAST_PORT = 12346      # Puerto UDP para heartbeat
TCP_PORT = 12345            # Puerto TCP para coordinación
HEARTBEAT_INTERVAL = 1.0    # segundos

# Buffering
BUFFER_SIZE = 5             # paquetes en el buffer
JITTER_BUFFER = True        # habilitar buffer anti-jitter
```

---

## ⚠️ Limitaciones Conocidas

### Versión 1v1
- Sin manejo automático de desconexiones
- Latencia puede aumentar si los routers tienen restricciones

### Versión Multiusuario
- Host centralizado = punto único de fallo
- Máximo ~8 usuarios antes de problemas de ancho de banda
- Sin re-sincronización si se pierden paquetes

### God Loquete (EN DESARROLLO)
- 🔴 **Crítica**: Cambio de host causa interrupción temporal de audio
- 🟡 **Mayor**: Mezcla de audio puede generar clipping con muchos usuarios
- 🟡 **Mayor**: Heartbeat timeout no siempre confiable en redes con jitter
- 🟢 **Menor**: Logging incompleto
- 🟢 **Menor**: Sin indicador visual de quién está hablando

---

## 🐛 Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| "No se encuentra pyaudio" | Dependencia no instalada | `pip install pyaudio` + librerías del sistema |
| "Micrófono no funciona" | Dispositivo no seleccionado | Selecciona el micrófono correcto en configuración |
| "Audio distorsionado" | Buffer pequeño o CPU saturada | Aumenta CHUNK_SIZE, reduce usuarios o cierra aplicaciones |
| "Conexión rechazada" | Firewall bloqueando puertos | Permite puertos 12345-12347 en firewall |
| "Latencia muy alta" | Ruta de red lenta | Verifica conexión, acerca los dispositivos, usa 5GHz WiFi |
| "Host muere, audio se corta" | God Loquete no recupera (EN DEV) | Reinicia manualmente, mejor usar v1v1 o Multiusuario |

---

## 🔮 Próximos Pasos / TODO

- [ ] **Estabilidad God Loquete**: mejorar detección de host caído
- [ ] **UI mejorada**: indicador de quién está hablando, VU meters
- [ ] **Criptografía**: soporte para audio encriptado (SRTP)
- [ ] **Grabación**: opción para grabar llamadas
- [ ] **Android/iOS**: extensión a aplicaciones móviles
- [ ] **Transcodificación**: soporte para múltiples codecs
- [ ] **Estadísticas**: latencia, pérdida de paquetes, jitter

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
