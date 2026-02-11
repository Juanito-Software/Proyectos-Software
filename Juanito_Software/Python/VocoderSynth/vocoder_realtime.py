"""
Procesamiento de voz en tiempo real con efecto tipo "robot / vocoder-like"
usando la entrada de micrófono y un oscilador como portador.

Implementado con:
- sounddevice: E/S de audio en tiempo real.
- numpy: procesamiento de bloques de audio.
"""

import math
from typing import Any, Tuple

import numpy as np
import sounddevice as sd


def create_ringmod_processor(
    samplerate: int,
    carrier_freq: float = 120.0,
) -> Tuple[sd.CallbackFlags, Any]:
    """
    Crea un callback de sounddevice que aplica ring modulation (multiplicación
    por un seno) a la señal de entrada, produciendo un efecto tipo voz robótica.
    """
    # Fase del oscilador portador, mantenida entre llamadas al callback.
    phase = 0.0
    two_pi = 2.0 * math.pi
    phase_increment = two_pi * carrier_freq / float(samplerate)

    def audio_callback(indata, outdata, frames, time, status):  # type: ignore[override]
        nonlocal phase
        if status:
            # Imprime cualquier warning/underrun/overrun en consola.
            print(status)

        # Aseguramos float32.
        x = indata[:, 0].astype(np.float32)  # canal 0 (mono)

        # Generamos el portador seno para este bloque.
        # Usamos numpy.arange para un bloque de longitud `frames`.
        t = np.arange(frames, dtype=np.float32)
        carrier = np.sin(phase + phase_increment * t)

        # Actualizamos fase, envuelta a [0, 2pi].
        phase = (phase + phase_increment * frames) % two_pi

        # Ring modulation: multiplicamos señal por portador.
        y = x * carrier

        # Pequeño factor de volumen para evitar clipping.
        y *= 1.2

        # Copiamos la señal procesada a todas las salidas disponibles (estéreo).
        outdata[:] = np.tile(y.reshape(-1, 1), (1, outdata.shape[1]))

    return audio_callback, None


def main() -> None:
    # Parámetros básicos de audio.
    samplerate = 48000  # Hz
    blocksize = 1024    # Tamaño de bloque en frames.

    print("Iniciando vocoder-like en tiempo real (ring modulation).")
    print("Habla por el micrófono y escucharás tu voz robotizada.")
    print("Pulsa Ctrl+C en la consola para salir.\n")

    # Creamos el callback de procesamiento.
    callback, _ = create_ringmod_processor(samplerate=samplerate, carrier_freq=120.0)

    # Abrimos un stream full-dúplex (entrada + salida).
    with sd.Stream(
        samplerate=samplerate,
        blocksize=blocksize,
        dtype="float32",
        channels=1,      # mono -> se replicará a estéreo en el callback
        callback=callback,
    ):
        try:
            # Mantener vivo hasta Ctrl+C.
            print("Procesando audio... (Ctrl+C para detener)")
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("\nDetenido por el usuario.")


if __name__ == "__main__":
    main()



