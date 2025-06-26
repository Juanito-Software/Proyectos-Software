# Copyright (C) 2025 JuanitoSoftware&Games
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.
import random
import shutil
import time
import os
import sys
import threading
import keyboard

from progress_bar_utils import show_basic_progress_bar, show_fancy_progress_bar

# Redirigir stdout y stderr temporalmente para silenciar pygame
class NullWriter:
    def write(self, _): pass
    def flush(self): pass

sys.stdout = NullWriter()
sys.stderr = NullWriter()

import pygame

# Restaurar stdout y stderr
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

CHARS = "01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎｶﾞｷｸｹｺアイウエオカキクケコサシスセソﾊﾋﾌﾍﾎ01ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#$%^&*アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎｶﾞｷｸｹｺアイウエオカキクケコサシスセソﾊﾋﾌﾍﾎ              "
cols, rows = shutil.get_terminal_size()
drops = [random.randint(0, rows) for _ in range(cols)]  # Posición inicial random para cada columna

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def matrix_rain(duration):
    """ 
    Muestra la lluvia Matrix durante 'duration' segundos.
    """
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            if keyboard.is_pressed('space'):
                clear()
                break
            print("\033[1;32m", end="")  # Verde brillante
            line = ""
            for i in range(cols):
                if random.random() > 0.666:
                    drops[i] = 0
                char = random.choice(CHARS)
                line += char if drops[i] == 0 else " "
                drops[i] += 1
            print(line)
            time.sleep(0.05)
        clear()
    except KeyboardInterrupt:
        clear()

def play_music(filename):
    """
    Reproduce una canción de forma bloqueante usando pygame.
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        # Espera hasta que termine la canción para no cerrar la música prematuramente
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"No se pudo reproducir la canción: {e}")

def intro_boot_sequence():
    # Mensajes de arranque con parpadeo
    boot_msgs = [
        ">>> [BOOT SEQUENCE INITIATED]",
        ">>> [ESTABLISHING ENCRYPTED LINK...]",
        ">>> [CONNECTING TO ZION MAINFRAME...]",
        ">>> [UPLOADING MODULES █]",
        ">>> [LOADING VISUAL SYSTEM...]"
    ]

    max_width = max(len(msg) for msg in boot_msgs + [">>> [LOADING VISUAL SYSTEM...] █████▒▒▒▒▒▒▒▒▒▒ 100%"])


    for msg in boot_msgs:
        for _ in range(2):
            sys.stdout.write("\r" + msg.ljust(max_width))
            sys.stdout.flush()
            time.sleep(0.3)
            sys.stdout.write("\r" + " " * max_width)
            sys.stdout.flush()
            time.sleep(0.2)
        print(msg.ljust(max_width))
        time.sleep(0.4) 

    # Carga con barra visual tipo █▒
    print(">>> [LOADING VISUAL SYSTEM...]", end="", flush=True)
    time.sleep(0.5)
 
    for i in range(0, 101, 2):
        bar_length = 20
        filled_length = int(i / 100 * bar_length)
        bar = "█" * filled_length + "▒" * (bar_length - filled_length)
        sys.stdout.write(f"\r>>> [LOADING VISUAL SYSTEM...]  {bar} {i}%".ljust(max_width))
        sys.stdout.flush()
        time.sleep(0.03)

    print()  # salto de línea final limpio
    time.sleep(0.5)
    print(">>> [ACCESS GRANTED]".ljust(max_width))
    time.sleep(0.6)
    print()

    # --- INICIO EFECTO DE CARGA CON BARRA ---
    print("Iniciando simulación Matrix...\n")
    total = 100
    for i in range(total + 1):
        show_fancy_progress_bar(i, total)
        time.sleep(0.02)  # Más rápido que en el main.py
    print("\nSistema cargado. Ejecutando Matrix...\n")
    time.sleep(0.5)
    # ----------------------------------------

if __name__ == "__main__": 

    duration=264 # Valor por defecto

    # Leer duración desde argumento si existe
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Argumento inválido para duración, usando valor por defecto (10 seg).")

    # Si el script está compilado con PyInstaller, obtener ruta especial
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    music_file = os.path.join(base_path, "MatrixSoundtrack.mp3")

    # Reproducir la música en un hilo para no bloquear la animación
    music_thread = threading.Thread(target=play_music, args=(music_file,), daemon=True)
    music_thread.start()

    intro_boot_sequence()

    matrix_rain(duration)