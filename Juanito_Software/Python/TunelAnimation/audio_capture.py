"""
Captura de audio en tiempo real para el túnel psicodélico.
En Windows usa PyAudioWPatch (WASAPI) para capturar la SALIDA de audio
(lo que suena en altavoces). Calcula energía, graves y beat.
"""
from __future__ import annotations

import threading
import time
from collections import deque

import numpy as np

try:
    import pyaudiowpatch as pyaudio
    HAS_LOOPBACK = True
except ImportError:
    try:
        import pyaudio
        HAS_LOOPBACK = False
    except ImportError:
        pyaudio = None
        HAS_LOOPBACK = False

# Configuración
CHUNK = 2048
CHANNELS = 1

# FFT: graves ~20–250 Hz
BASS_BIN_START = 1
BASS_BIN_END = 13

# Suavizado
ENERGY_SMOOTH = 0.35
BASS_SMOOTH = 0.35
BEAT_DECAY = 0.88
BEAT_THRESHOLD = 1.5
BEAT_MIN_INTERVAL = 0.12

# Sensibilidad: ganancia alta para que cualquier reproducción se vea
GAIN_ENERGY = 35.0
GAIN_BASS = 20000.0
RUNNING_MAX_DECAY = 0.995  # adaptación rápida al subir el volumen

_running = False
_thread = None
_stream = None
_pa = None
_sample_rate = 44100

_smooth_energy = 0.0
_smooth_bass = 0.0
_beat_value = 0.0
_energy_history = deque(maxlen=40)
_last_beat_time = 0.0
_running_max_energy = 0.05
_running_max_bass = 0.05


def _analyze_chunk(samples: np.ndarray) -> tuple[float, float, float]:
    """Analiza un chunk: (energy, bass, beat) con normalización adaptativa."""
    global _smooth_energy, _smooth_bass, _beat_value, _energy_history, _last_beat_time
    global _running_max_energy, _running_max_bass

    if len(samples) < 2:
        return (_smooth_energy, _smooth_bass, _beat_value)

    x = samples.astype(np.float64) / 32768.0
    window = np.hanning(len(x))
    x = x * window

    # Energía (RMS) con ganancia alta
    rms = np.sqrt(np.mean(x ** 2))
    energy_raw = min(3.0, rms * GAIN_ENERGY)
    _running_max_energy = max(_running_max_energy * RUNNING_MAX_DECAY, energy_raw, 0.03)
    energy = min(1.0, energy_raw / max(_running_max_energy, 0.01))

    # Graves (FFT)
    fft = np.fft.rfft(x)
    mag = np.abs(fft)
    bass_mag = np.sum(mag[BASS_BIN_START:BASS_BIN_END])
    bass_raw = min(3.0, bass_mag / GAIN_BASS)
    _running_max_bass = max(_running_max_bass * RUNNING_MAX_DECAY, bass_raw, 0.03)
    bass = min(1.0, bass_raw / max(_running_max_bass, 0.01))

    _smooth_energy = _smooth_energy * (1 - ENERGY_SMOOTH) + energy * ENERGY_SMOOTH
    _smooth_bass = _smooth_bass * (1 - BASS_SMOOTH) + bass * BASS_SMOOTH

    # Beat
    _energy_history.append(_smooth_energy)
    avg = sum(_energy_history) / len(_energy_history)
    now = time.perf_counter()
    _beat_value *= BEAT_DECAY
    if _smooth_energy > avg * BEAT_THRESHOLD and (now - _last_beat_time) > BEAT_MIN_INTERVAL:
        _beat_value = 1.0
        _last_beat_time = now

    return (_smooth_energy, _smooth_bass, _beat_value)


def _get_set_audio():
    """Devuelve la función set_audio del módulo que se está ejecutando (__main__), no el importado."""
    import sys
    main_mod = sys.modules.get("__main__")
    if main_mod is not None and hasattr(main_mod, "set_audio"):
        return main_mod.set_audio
    try:
        import tunnel
        return tunnel.set_audio
    except Exception:
        return lambda **kw: None


def _capture_loop() -> None:
    global _stream, _pa, _running

    if not pyaudio or _stream is None:
        return

    set_audio = _get_set_audio()
    set_audio(energy=0, bass=0, beat=0)

    while _running and _stream is not None:
        try:
            data = _stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)
            # Si el dispositivo es estéreo, promediar a mono
            if len(samples) > CHUNK:
                samples = samples.reshape(-1, 2).mean(axis=1).astype(np.int16)
            elif len(samples) < CHUNK:
                continue
            e, b, beat = _analyze_chunk(samples)
            set_audio(energy=e, bass=b, beat=beat)
        except Exception:
            if _running:
                try:
                    set_audio(energy=0, bass=0, beat=0)
                except Exception:
                    pass
            break

    try:
        _stream.stop_stream()
        _stream.close()
    except Exception:
        pass
    _stream = None
    if _pa:
        try:
            _pa.terminate()
        except Exception:
            pass


def list_output_devices() -> list[tuple[int, str]]:
    """
    Lista dispositivos de SALIDA de audio (altavoces) sobre los que se puede capturar.
    En Windows con PyAudioWPatch son dispositivos WASAPI loopback.
    """
    if pyaudio is None:
        return []
    result = []
    try:
        pa = pyaudio.PyAudio()
        if HAS_LOOPBACK:
            try:
                pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            except OSError:
                pa.terminate()
                return []
            for dev in pa.get_loopback_device_info_generator():
                idx = dev["index"]
                name = dev.get("name", "Salida %d" % idx)
                # Quitar sufijo [Loopback] para mostrar nombre limpio
                if " [Loopback]" in name:
                    name = name.replace(" [Loopback]", "")
                result.append((idx, name))
        else:
            # Sin WASAPI: listar salidas normales (maxOutputChannels > 0) por si acaso
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info.get("maxOutputChannels", 0) > 0:
                    result.append((i, info.get("name", "Salida %d" % i)))
        pa.terminate()
    except Exception:
        pass
    return result


def start(device_index: int | None = None) -> bool:
    """
    Inicia la captura desde un dispositivo de SALIDA (loopback).
    device_index: índice del dispositivo de salida (None = salida por defecto).
    """
    global _running, _thread, _stream, _pa, _sample_rate

    if pyaudio is None:
        return False
    if _running:
        return True

    _running = True
    try:
        _pa = pyaudio.PyAudio()
        if HAS_LOOPBACK:
            # Buscar dispositivo loopback: el elegido o la salida por defecto
            dev_info = None
            if device_index is not None:
                for dev in _pa.get_loopback_device_info_generator():
                    if dev["index"] == device_index:
                        dev_info = dev
                        break
            if dev_info is None:
                try:
                    wasapi = _pa.get_host_api_info_by_type(pyaudio.paWASAPI)
                    default_out = _pa.get_device_info_by_index(wasapi["defaultOutputDevice"])
                    for dev in _pa.get_loopback_device_info_generator():
                        if default_out["name"] in dev["name"]:
                            dev_info = dev
                            break
                except Exception:
                    pass
            if dev_info is not None:
                _sample_rate = int(dev_info.get("defaultSampleRate", 44100))
                ch = min(2, dev_info.get("maxInputChannels", 1))
                _stream = _pa.open(
                    format=pyaudio.paInt16,
                    channels=ch,
                    rate=_sample_rate,
                    input=True,
                    input_device_index=dev_info["index"],
                    frames_per_buffer=CHUNK,
                )
            else:
                raise RuntimeError("No se encontró dispositivo de salida (loopback)")
        else:
            # Sin loopback o dispositivo por defecto: intentar default
            _sample_rate = 44100
            _stream = _pa.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=_sample_rate,
                input=True,
                frames_per_buffer=CHUNK,
            )
        _thread = threading.Thread(target=_capture_loop, daemon=True)
        _thread.start()
        return True
    except Exception:
        _running = False
        if _pa:
            try:
                _pa.terminate()
            except Exception:
                pass
            _pa = None
        return False


def stop() -> None:
    global _running, _thread, _stream
    _running = False
    if _thread is not None:
        _thread.join(timeout=1.0)
        _thread = None


def is_available() -> bool:
    return pyaudio is not None


def has_loopback() -> bool:
    """True si se puede capturar la salida de audio (WASAPI loopback)."""
    return HAS_LOOPBACK and pyaudio is not None
