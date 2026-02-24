"""
Launcher: instala dependencias, muestra selector de dispositivo de SALIDA de audio
(lo que suena en altavoces) y ejecuta el túnel.
"""
from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)
    req = os.path.join(base, "requirements.txt")

    # 1) Instalar dependencias
    print("Comprobando dependencias...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req, "-q"],
            check=False,
            capture_output=True,
        )
    except Exception:
        pass
    print("Dependencias listas.\n")

    # 2) Listar dispositivos de SALIDA (altavoces) para capturar lo que suena
    try:
        from audio_capture import list_output_devices, has_loopback
    except Exception:
        list_output_devices = lambda: []
        has_loopback = lambda: False

    devices = list_output_devices()
    device_index = None

    if not devices:
        print("No se encontraron dispositivos de SALIDA de audio (loopback).")
        print("En Windows hace falta PyAudioWPatch para capturar lo que suena.")
        print("Se usará audio simulado (--demo-audio).\n")
        args_extra = ["--demo-audio"]
    else:
        print("Dispositivos de SALIDA de audio (captura lo que suena por este dispositivo):")
        print("-" * 60)
        for i, name in devices:
            print("  [%d] %s" % (i, name))
        print("-" * 60)
        try:
            inp = input("Número de dispositivo (Enter = usar el primero): ").strip()
            if inp:
                device_index = int(inp)
                valid = [d[0] for d in devices]
                if device_index not in valid:
                    device_index = devices[0][0]
            else:
                device_index = devices[0][0]
        except (ValueError, EOFError, KeyboardInterrupt):
            device_index = devices[0][0] if devices else None
        if device_index is not None:
            args_extra = ["--device", str(device_index)]
        else:
            args_extra = []

    # 3) Ejecutar tunnel.py
    print("\nIniciando túnel...\n")
    try:
        return subprocess.run(
            [sys.executable, os.path.join(base, "tunnel.py")] + args_extra,
            cwd=base,
        ).returncode
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
