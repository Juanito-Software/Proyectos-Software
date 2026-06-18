"""
Launcher: instala dependencias, muestra selector de dispositivo de SALIDA de audio
(lo que suena en altavoces) y ejecuta el túnel.
"""
from __future__ import annotations

import os
import subprocess
import sys


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)

    print("Dependencias ya incluidas en el build.")

    # =========================
    # 2) IMPORT SEGURO AUDIO
    # =========================
    try:
        from audio_capture import list_output_devices
    except Exception:
        list_output_devices = lambda: []

    devices = list_output_devices()
    device_index = None
    args_extra = []

    # =========================
    # 3) SELECCIÓN DISPOSITIVO
    # =========================
    if not devices:
        print("No se detectan dispositivos de salida (loopback).")
        print("Usando audio simulado.\n")
        args_extra = ["--demo-audio"]

    else:
        print("Dispositivos de salida disponibles:")
        print("-" * 50)

        for i, name in devices:
            print(f"[{i}] {name}")

        print("-" * 50)

        try:
            inp = input("Selecciona dispositivo (Enter = 0): ").strip()
            device_index = int(inp) if inp else devices[0][0]
        except Exception:
            device_index = devices[0][0]

        args_extra = ["--device", str(device_index)]

    # =========================
    # 4) EJECUCIÓN TUNNEL
    # =========================
    print("\nIniciando túnel...\n")

    if is_frozen():
        try:
            # En modo compilado (frozen), sys.executable es el propio ejecutable (.exe).
            # Para evitar un bucle infinito, importamos y ejecutamos tunnel directamente.
            sys.argv = [sys.argv[0]] + args_extra
            import tunnel
            return tunnel.main()
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            print(f"Error lanzando túnel en modo build: {e}")
            return 1
    else:
        try:
            return subprocess.run(
                [sys.executable, os.path.join(base, "tunnel.py")] + args_extra,
                cwd=base
            ).returncode
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            print(f"Error lanzando túnel: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
