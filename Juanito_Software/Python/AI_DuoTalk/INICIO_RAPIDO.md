# 🚀 Inicio Rápido - AI_DuoTalk

## ✅ Instalación Completada

Todas las dependencias están instaladas en el entorno virtual `iaenv`.

## 📝 Pasos para Usar el Sistema

### 1. Activar el Entorno Virtual

**Windows:**
```bash
iaenv\Scripts\activate
```

**Linux/Mac:**
```bash
source iaenv/bin/activate
```

### 2. Ejecutar el Sistema en Tiempo Real (RECOMENDADO)

**Opción A: Doble clic (Más fácil)**
- Haz doble clic en `iniciar_moderador.bat`
- El sistema se iniciará automáticamente

**Opción B: Desde terminal**
```bash
python main_moderador.py
```

### 3. Usar el Sistema - Modo Moderador

El sistema grabará **30 segundos** de tu voz directamente del micrófono.

**Comandos principales:**
- **A** - Preguntar solo a Franco (político/crítico)
- **B** - Preguntar solo a Lenin (filosófico/reflexivo)
- **AB** - Preguntar a ambas IAs (responden en orden aleatorio)
- **DEBATE** - Iniciar debate automático entre IAs
- **Ctrl+B** - Detener cualquier proceso activo (atajo de teclado)
- **H** - Ver ayuda completa
- **T** - Cambiar duración de grabación (10s, 20s, 30s, 60s)
- **SALIR** - Salir del sistema

### 4. Flujo de Uso

1. Escribe un comando (ej: `A`, `B`, `AB`, `DEBATE`)
2. Verás un mensaje preparatorio con la duración de grabación
3. Aparecerá un aviso **"GRABANDO..."** con cuenta regresiva (2 segundos)
4. **Empieza a hablar** cuando veas el mensaje de grabación
5. El sistema grabará 30 segundos de tu voz
6. La IA procesará y responderá automáticamente

**Ejemplo:**
```
[COMANDO] >> A

============================================================
  FRANCO - PREPARADO PARA ESCUCHAR
============================================================
[AVISO] Se grabarán 30 segundos de audio
[AVISO] Empieza a hablar cuando veas el mensaje 'GRABANDO...'
============================================================

============================================================
  GRABANDO AUDIO...
============================================================
[DURACION] 30 segundos
[AVISO] Empieza a hablar AHORA
[AVISO] La grabación comenzará en 2 segundos...
============================================================
[2...] [1...] 
[GRABANDO] Habla ahora...
```

## ⚠️ Notas Importantes

### Primera Ejecución

La primera vez que uses cada módulo, se descargarán los modelos:
- **Whisper**: ~500MB (modelo "small")
- **GPT4All**: ~4GB (modelo Mistral)
- **Silero TTS**: Se descarga automáticamente vía torch.hub

Esto puede tardar varios minutos dependiendo de tu conexión.

### Requisitos de Hardware

- **RAM**: Mínimo 8GB (16GB recomendado)
- **GPU**: Opcional pero recomendado (CUDA)
- **Espacio en disco**: ~5GB para los modelos

### Solución de Problemas

**Error: "No se encuentra FFmpeg"**
- Instala FFmpeg y añádelo al PATH
- Windows: Descarga desde https://ffmpeg.org/

**Error: "Modelo no encontrado"**
- Asegúrate de tener conexión a internet la primera vez
- Los modelos se guardan en caché para uso futuro

**Audio no se reproduce**
- Verifica que tu sistema de audio funcione
- Comprueba que `sounddevice` esté instalado correctamente

## 🎬 Integración con OBS

### Con Modo Moderador (Tiempo Real)

1. Ejecuta `python main_moderador.py`
2. El sistema grabará directamente de tu micrófono (30 segundos)
3. El audio de las IAs se reproducirá por los altavoces
4. OBS puede capturarlo con "Captura de audio de escritorio"

**Para mejor control, usa VB-Audio Cable:**
- Descarga e instala VB-Audio Cable
- Configura Windows para usar VB-Audio Cable como salida
- En OBS, añade "VB-Audio Cable output" como fuente de audio
- El audio de las IAs se capturará directamente sin interferencias

## ⚙️ Configuración de Duración de Grabación

Por defecto, el sistema graba **30 segundos** de audio. Puedes cambiarlo:

1. En el modo moderador, escribe `T` o `TIEMPO`
2. Elige una duración: 10, 20, 30 o 60 segundos
3. La nueva duración se aplicará a todas las grabaciones

**Recomendaciones:**
- **10-20 segundos**: Para preguntas cortas
- **30 segundos**: Para preguntas normales (recomendado)
- **60 segundos**: Para preguntas largas o explicaciones detalladas

## 🚀 Inicio Rápido con Archivos .bat

Para facilitar el inicio del programa, se incluye un archivo `.bat`:

- **`iniciar_moderador.bat`**: Inicia el Modo Moderador en tiempo real

**Uso:**
1. Haz doble clic en `iniciar_moderador.bat`
2. El sistema se iniciará automáticamente
3. No necesitas abrir la terminal manualmente

**Nota:** La primera vez puede tardar un poco más mientras se cargan los modelos.

## 📚 Más Información

- **`MODO_MODERADOR.md`**: Guía completa del modo moderador en tiempo real
- **`README.md`**: Documentación general del proyecto
- **Personalización**: Edita `agents/agent_A.py` y `agents/agent_B.py` para cambiar personalidades

