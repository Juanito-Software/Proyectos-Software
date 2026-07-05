# 🎙️ AI_DuoTalk - Sistema de Debate con Dos IAs de Voz

Sistema completo para crear debates entre dos IAs de voz usando tecnologías locales y gratuitas.

## 🚀 Características

- **Speech-to-Text**: Usa Whisper para transcribir voz a texto
- **LLM Local**: Usa GPT4All (Mistral) para generar respuestas inteligentes
- **Text-to-Speech**: Usa Silero para convertir texto a voz natural
- **Dos Personalidades**: Franco (político/crítico) y Lenin (filosófico/reflexivo)
- **Integración OBS**: Listo para usar en directos

## 📋 Requisitos

### Hardware
- Windows o Linux
- RAM: 8GB mínimo (16GB recomendado)
- GPU con CUDA (opcional pero recomendado)

### Software
- Python 3.10 o 3.11
- FFmpeg instalado
- Git
- OBS (opcional, para directos)

## 🔧 Instalación

### 1. Crear entorno virtual

**Windows:**
```bash
python -m venv iaenv
iaenv\Scripts\activate
```

**Linux:**
```bash
python -m venv iaenv
source iaenv/bin/activate
```

### 2. Instalar dependencias

```bash
# Instalar PyTorch con CUDA (recomendado)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# O instalar PyTorch para CPU solamente
pip install torch

# Instalar el resto de dependencias
pip install -r requirements.txt
```

### 3. Verificar instalación

```bash
python main_moderador.py
```

## 📁 Estructura del Proyecto

```
AI_DuoTalk/
├── agents/
│   ├── agent_A.py      # Franco (político/crítico)
│   └── agent_B.py      # Lenin (filosófico/reflexivo)
├── modules/
│   ├── stt_whisper.py  # Speech-to-Text con Whisper
│   ├── llm_local.py    # LLM local con GPT4All
│   └── tts_silero.py   # Text-to-Speech con Silero
├── main_moderador.py   # Sistema principal (modo moderador en tiempo real)
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## 🎮 Uso Básico

### Modo Moderador en Tiempo Real (main_moderador.py)

1. **Ejecutar el sistema:**
   ```bash
   python main_moderador.py
   ```

2. **Usar comandos:**
   - `A` - Preguntar solo a Franco
   - `B` - Preguntar solo a Lenin
   - `AB` - Preguntar a ambas IAs
   - `DEBATE` - Iniciar debate automático
   - `Ctrl+B` - Detener cualquier proceso (atajo de teclado)
   - `Ctrl+N` - Interrumpir debate y añadir tu voz (atajo de teclado)
   - `H` - Ver ayuda completa

**Ver documentación completa en `MODO_MODERADOR.md`**

## 🎬 Integración con OBS

### Configuración de Audio de Entrada

1. **Grabar audio en OBS:**
   - Configura OBS para grabar tu micrófono
   - Guarda el audio como `input.wav` en la raíz del proyecto

2. **Configuración de Audio de Salida (Windows):**

   **Opción 1: VB-Audio Cable (Recomendado)**
   - Descarga e instala VB-Audio Cable
   - En Windows: Configuración → Sonido → "Escuchar este dispositivo"
   - Selecciona "VB-Audio Cable" como dispositivo de salida
   - En OBS: Añade fuente de audio → "VB-Audio Cable output"

   **Opción 2: Audio Directo**
   - El audio se reproduce directamente por los altavoces
   - OBS puede capturarlo con "Captura de audio de escritorio"

### Flujo de Trabajo en Directo

1. Ejecutas `python main_moderador.py`
2. Hablas en tu micrófono cuando el sistema te lo indique
3. El sistema graba tu voz directamente (30 segundos por defecto)
4. La IA procesa y responde automáticamente
5. El audio se reproduce y OBS lo captura

## ⚙️ Personalización

### Cambiar Personalidades

Edita los archivos `agents/agent_A.py` y `agents/agent_B.py` para modificar las personalidades:

```python
PERSONALIDAD = """Tu nueva personalidad aquí..."""
```

### Ajustar Parámetros del LLM

En `modules/llm_local.py`, puedes modificar:
- `max_tokens`: Longitud máxima de la respuesta
- `temperature`: Creatividad (0.0-1.0)
- `top_k`, `top_p`: Parámetros de muestreo

### Cambiar Speaker de TTS

En `modules/tts_silero.py`, puedes cambiar el `speaker_id`:
- `'es_0'`, `'es_1'`, etc. para diferentes voces en español

## 🐛 Solución de Problemas

### Error: "No se encuentra FFmpeg"
- Instala FFmpeg y añádelo al PATH
- Windows: Descarga desde https://ffmpeg.org/
- Linux: `sudo apt install ffmpeg`

### Error: "Modelo no encontrado"
- Los modelos se descargan automáticamente la primera vez
- Asegúrate de tener conexión a internet
- Whisper descarga el modelo "small" (~500MB)
- GPT4All descarga Mistral (~4GB)

### Audio no se reproduce
- Verifica que `sounddevice` esté instalado correctamente
- Comprueba que tu sistema de audio funcione
- En Linux, puede necesitar: `sudo apt install portaudio19-dev`

### Respuestas muy lentas
- Usa GPU con CUDA si es posible
- Reduce `max_tokens` en el LLM
- Usa un modelo Whisper más pequeño (ej: "tiny" o "base")

## 📝 Notas

- La primera ejecución será más lenta (descarga de modelos)
- Los modelos se guardan en caché para ejecuciones futuras
- El sistema funciona completamente offline después de la primera descarga
- Puedes modificar fácilmente las personalidades y parámetros

## 🔄 Próximas Mejoras

- [ ] Interfaz gráfica (GUI)
- [ ] Captura de audio en tiempo real
- [ ] Soporte para múltiples idiomas
- [ ] Historial de conversación
- [ ] Integración directa con OBS vía plugin

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

---

**¡Disfruta creando debates con tus IAs!** 🎉

