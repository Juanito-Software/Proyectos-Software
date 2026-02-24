"""
Stub de audio para el túnel psicodélico.
Reemplazar más adelante por captura real (PyAudio + FFT, aubio, etc.)
y llamar a tunnel.set_audio(energy=..., bass=..., beat=...).
"""
from __future__ import annotations

import math
import time


def fake_audio_generator():
    """
    Generador que simula valores de audio (para pruebas sin micrófono).
    Produce energy/bass/beat con ritmo ficticio.
    """
    t0 = time.perf_counter()
    while True:
        t = time.perf_counter() - t0
        # Simula "beat" cada ~0.5 s
        beat = 0.9 * (0.5 + 0.5 * math.sin(t * 12)) if math.sin(t * 4) > 0.7 else 0.0
        energy = 0.3 + 0.4 * (0.5 + 0.5 * math.sin(t * 2))
        bass = 0.2 + 0.5 * (0.5 + 0.5 * math.sin(t * 1.3))
        yield (max(0, min(1, energy)), max(0, min(1, bass)), max(0, min(1, beat)))


def run_with_fake_audio():
    """Ejemplo: ejecutar el túnel con audio simulado."""
    import tunnel

    gen = fake_audio_generator()
    # En un bucle real, antes de engine.update(dt) harías:
    # e, b, beat = next(gen)
    # tunnel.set_audio(energy=e, bass=b, beat=beat)
    # Por ahora solo documenta el uso.
    return gen
