# 🎙️ Modo Moderador Absoluto - Sistema en Tiempo Real

## ⭐ Características

El **Modo Moderador Absoluto** es un sistema en tiempo real donde:
- ✅ Los agentes escuchan **SIEMPRE** tu micrófono
- ✅ Solo hablan cuando **TÚ** lo ordenas
- ✅ Control total sobre quién habla y cuándo
- ✅ Sistema de debate automático entre IAs

## 🚀 Inicio Rápido

### 1. Activar Entorno Virtual

```bash
iaenv\Scripts\activate  # Windows
source iaenv/bin/activate  # Linux/Mac
```

### 2. Ejecutar Modo Moderador

```bash
python main_moderador.py
```

## 📋 Comandos Disponibles

### Comandos Principales

| Comando | Descripción |
|---------|-------------|
| **A** | Preguntar solo a Franco (político/crítico) |
| **B** | Preguntar solo a Lenin (filosófico/reflexivo) |
| **AB** o **AMBAS** | Preguntar a ambas IAs (responden en orden aleatorio) |
| **DEBATE** | Iniciar debate entre IAs (se contestan entre sí) |
| **Ctrl+B** | Detener debate o cualquier proceso activo (atajo de teclado) |
| **SALIR** | Salir del sistema |

### Comandos Adicionales

| Comando | Descripción |
|---------|-------------|
| **H** o **AYUDA** | Mostrar ayuda de comandos |
| **D** o **DISPOSITIVOS** | Listar dispositivos de audio disponibles |
| **T** o **TIEMPO** | Cambiar duración de grabación (3s, 5s, 10s) |

## 🎮 Modos de Uso

### 1. Preguntar Solo a Franco

```
[COMANDO] >> A
[FRANCO] Grabando audio...
[GRABANDO] Escuchando 3 segundos...
```

Franco escuchará tu pregunta, la procesará y responderá.

### 2. Preguntar Solo a Lenin

```
[COMANDO] >> B
[LENIN] Grabando audio...
[GRABANDO] Escuchando 3 segundos...
```

Lenin escuchará tu pregunta, la procesará y responderá.

### 3. Preguntar a Ambas IAs

```
[COMANDO] >> AB
[AMBAS IAs] Grabando audio...
[GRABANDO] Escuchando 3 segundos...
[AMBAS] Ambas IAs van a responder en orden aleatorio...
```

Ambas IAs escucharán la misma pregunta y responderán en orden aleatorio.

### 4. Modo Debate

```
[COMANDO] >> DEBATE
[DEBATE] Grabando tema inicial...
[GRABANDO] Escuchando 3 segundos...

============================================================
  DEBATE INICIADO
============================================================
[TEMA] ¿Qué opinas sobre la inteligencia artificial?
[RONDAS] Máximo 4 rondas

[AVISO] Las IAs debatirán entre sí.
[AVISO] El debate se detendrá automáticamente después de las rondas.
============================================================

[Ronda 1] Respuestas iniciales...
[DEBATE] Ronda 2/4
[DEBATE] Ronda 3/4
[DEBATE] Ronda 4/4
[DEBATE] Debate completado (4 rondas)
```

En modo debate:
- Ambas IAs responden al tema inicial
- Luego se contestan entre sí automáticamente
- Por defecto, 4 rondas (configurable)
- Puedes detener con **Ctrl+B** en cualquier momento (atajo de teclado)

## ⚙️ Configuración

### Cambiar Duración de Grabación

```
[COMANDO] >> T
[Tiempo actual: 3s] Nueva duración (3, 5, 10): 5
[OK] Duración configurada a 5s
```

### Ver Dispositivos de Audio

```
[COMANDO] >> D
[DEVICES] Dispositivos de audio disponibles:
   0 Microsoft Sound Mapper - Input, MME (2 in, 0 out)
   1 Microphone (Realtek Audio), MME (1 in, 0 out)
   ...
```

## 🔧 Flujo Técnico

### Proceso de una Pregunta

1. **Grabación**: Captura audio del micrófono (3s por defecto)
2. **Transcripción**: Whisper convierte audio → texto
3. **Procesamiento**: LLM (GPT4All) genera respuesta
4. **Voz**: Silero convierte texto → voz y reproduce

### Flujo de Debate

1. **Tema Inicial**: Se graba y transcribe el tema
2. **Ronda 1**: Ambas IAs responden al tema inicial
3. **Rondas Siguientes**: 
   - Franco responde a lo que dijo Lenin
   - Lenin responde a lo que dijo Franco
   - Se repite hasta completar rondas o parar

## 🎬 Integración con OBS

### Configuración Básica

1. **Entrada de Audio**: Tu micrófono → OBS
2. **Salida de Audio**: 
   - El audio de las IAs se reproduce por los altavoces
   - OBS puede capturarlo con "Captura de audio de escritorio"

### Configuración Avanzada (VB-Audio Cable)

1. Instala VB-Audio Cable
2. Configura Windows para usar VB-Audio Cable como salida
3. En OBS, añade "VB-Audio Cable output" como fuente
4. El audio de las IAs se capturará directamente

## ⚠️ Solución de Problemas

### No se detecta el micrófono

- Verifica que el micrófono esté conectado
- Usa `D` para ver dispositivos disponibles
- En Windows, verifica permisos de micrófono

### Audio no se graba correctamente

- Verifica que el micrófono no esté silenciado
- Aumenta la duración de grabación con `T`
- Prueba con diferentes dispositivos

### Las IAs no responden

- Verifica que Whisper haya transcrito correctamente
- Revisa los mensajes de error en consola
- Asegúrate de que los modelos estén descargados

### El debate no se detiene

- Presiona **Ctrl+B** para detener inmediatamente (atajo de teclado)
- El debate se detiene automáticamente después de las rondas

## 💡 Consejos de Uso

1. **Habla Claro**: Para mejor transcripción, habla claro y pausado
2. **Ajusta Duración**: Si hablas más, aumenta la duración con `T`
3. **Controla el Debate**: El debate tiene límite de rondas para evitar loops infinitos
4. **Prueba Primero**: Prueba con comandos simples (A, B) antes de usar DEBATE

## 📝 Ejemplo de Sesión Completa

```
[INICIO] Sistema iniciado. Los agentes están escuchando...

[COMANDO] >> A
[FRANCO] Grabando audio...
[GRABANDO] Escuchando 3 segundos...
[OK] Audio guardado en live.wav
[PROCESANDO] FRANCO está pensando...
[TEXTO] Usuario dijo: ¿Qué opinas de la política actual?
[OK] FRANCO respondió correctamente

[COMANDO] >> B
[LENIN] Grabando audio...
...

[COMANDO] >> DEBATE
[DEBATE] Grabando tema inicial...
...
[DEBATE] Debate completado (4 rondas)

[COMANDO] >> SALIR
[SALIR] Saliendo del sistema...
```

---

**¡Disfruta del control total sobre tus IAs!** 🎉

