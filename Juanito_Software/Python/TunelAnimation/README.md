# Túnel psicodélico infinito

Animación en tiempo real de un túnel infinito con colores HSV y rotación, renderizada en ventana. Optimizada con NumPy y preparada para reaccionar a la música (energía, graves, beat).

## Requisitos

- Python 3.9+
- pygame, numpy, pyaudio

## Instalación

```bash
pip install -r requirements.txt
```

En Windows, si `pip install pyaudio` falla, instala primero [PyAudio wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) o usa:

```bash
pip install pipwin
pipwin install pyaudio
```

## Uso

```bash
python tunnel.py
```

Por defecto usa el **micrófono** en tiempo real (PyAudio + FFT). El túnel reacciona a la energía, los graves y los golpes (beat).

- **ESC** o cerrar ventana: salir.
- **`--demo-audio`**: no usa micrófono; simula audio para probar la reacción.

## Reacción al audio

- **AUDIO_ENERGY** (RMS): velocidad del túnel y brillo.
- **AUDIO_BASS** (FFT 20–250 Hz): grosor de líneas.
- **AUDIO_BEAT** (detección de picos): rotación y pulso del centro.

La captura corre en un hilo y actualiza `tunnel.set_audio()`. Si no hay micrófono o PyAudio falla, se usa automáticamente el generador simulado de `audio_stub.py`.

## Estructura

- `tunnel.py`: motor del túnel y bucle principal.
- `audio_capture.py`: captura con PyAudio, FFT y detección de beat.
- `audio_stub.py`: generador de audio simulado (fallback y `--demo-audio`).
- `requirements.txt`: dependencias.
