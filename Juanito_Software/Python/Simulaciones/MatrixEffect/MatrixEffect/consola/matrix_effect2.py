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
import threading

from wcwidth import wcwidth

from progress_bar_utils import show_fancy_progress_bar
from colorama import init, Fore, Style

should_exit = threading.Event()  # señal para cerrar desde cualquier parte

init()

GREEN_GRADIENT = [
    "\033[38;5;118m",  # verde muy claro
    "\033[38;5;82m",   # verde claro
    "\033[38;5;46m",   # verde medio
    "\033[38;5;40m",   # verde algo oscuro
    "\033[38;5;34m",   # verde más oscuro
    "\033[38;5;28m",   # verde muy oscuro
]
RESET = "\033[0m"


# Mapeo de mutaciones visuales similares (puedes extenderlo)
char_mutations = {
    '1': ['|', 'I', 'l'],
        '0': ['O', 'Q', '@'],
        '2': ['Z'], 
        '3': ['E','Ξ'], 
        '4': ['A'],
        '5': ['S'], 
        '6': ['G'], 
        '7': ['T'], 
        '8': ['B'], 
        '9': ['P'], 
        'S': ['5', '$'],
        'Z': ['2'],
        'A': ['4', '^', 'Λ'],
        'B': ['8', 'ß'],
        'C': ['<', '('], 
        'D': [')'],
        'E': ['3','F','Ξ'],
        'F': ['E'],
        'G': ['6'], 
        'H': ['#'],
        'I': ['1', '|', '!', '¡', 'l'],
        'J': ['¿'],
        'K': ['X'], 
        'L': ['1', '|','I'], 
        'M': ['^', 'n'], 
        'N': ['^'],
        'O': ['0', 'Q', '@'], 
        'P': ['9'], 
        'Q': ['O', '0'],
        'R': ['Я', '®'], 
        'S': ['5', '$'],
        'T': ['7', '+'],
        'U': ['µ', 'v'], 
        'V': ['V'], 
        'W': ['V'],
        'X': ['%', '*'],
        'Y': ['¥'], 
        'Z': ['2'],  
        ' ': [' ', '-', '_']  # sometimes underscore
}

def mutate_char(c):
    upper = c.upper()
    if upper in char_mutations:
        return random.choice(char_mutations[upper])
    else:
        return c  # No cambio si no está en el mapa

def glitch_text(text, glitch_chance=0.3):
    return ''.join(mutate_char(c) if random.random() < glitch_chance else c for c in text)

def glitch_animation(text, frames=20, delay=0.1):
    BRIGHT_GREEN = "\033[38;2;0;255;0m"
    RESET_COLOR = "\033[0m"
    for _ in range(frames):
        if should_exit.is_set():
            return
        # Más seguro que limpiar la pantalla completa: solo borra línea actual
        sys.stdout.write("\r" + " " * shutil.get_terminal_size().columns + "\r")
        sys.stdout.write(f"{BRIGHT_GREEN}{glitch_text(text, glitch_chance=0.4)}{RESET_COLOR}")
        sys.stdout.flush()
        time.sleep(delay)
    print()  # salto de línea al final

def glitch_char(c):
    similares = {
        '1': ['|', 'I', 'l'],
        '0': ['O', 'Q', '@'],
        '2': ['Z'], 
        '3': ['E','Ξ'], 
        '4': ['A'],
        '5': ['S'], 
        '6': ['G'], 
        '7': ['T'], 
        '8': ['B'], 
        '9': ['P'], 
        'S': ['5', '$'],
        'Z': ['2'],
        'A': ['4', '^', 'Λ'],
        'B': ['8', 'ß'],
        'C': ['<', '('], 
        'D': [')'],
        'E': ['3','F','Ξ'],
        'F': ['E'],
        'G': ['6'], 
        'H': ['#'],
        'I': ['1', '|', '!', '¡', 'l'],
        'J': ['¿'],
        'K': ['X'], 
        'L': ['1', '|','I'], 
        'M': ['^', 'n'], 
        'N': ['^'],
        'O': ['0', 'Q', '@'], 
        'P': ['9'], 
        'Q': ['O', '0'],
        'R': ['Я', '®'], 
        'S': ['5', '$'],
        'T': ['7', '+'],
        'U': ['µ', 'v'], 
        'V': ['V'], 
        'W': ['V'],
        'X': ['%', '*'],
        'Y': ['¥'], 
        'Z': ['2'],  
        ' ': [' ', '-', '_']  # sometimes underscore
    }
    if c in similares:
        return random.choice(similares[c])
    else:
        return random.choice(['#', '%', '&', '=', '-', '_'])

def escucha_tecla_salida():
    while not should_exit.is_set():
        if keyboard.is_pressed('space'):
            should_exit.set()
            clear()
            print(">>> Programa interrumpido por el usuario (tecla ESPACIO)")
            break
        time.sleep(0.05)  # Para no saturar la CPU


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

# Caracteres inspirados en el código original de Matrix
katakana = list("MATRIXWXYZアイウエオカキクケコサシスセソﾊﾋﾌﾍﾎｶｷｸｹｺｶパガニーチェントネディソナタナクソスクラシックキュレションｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜｶｷｸｹｺｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜｶｷｸｹｺ第番長調第番長調第番長調第番長調日日日日日日日日日日日日日日日日日日日日")
CHARS = list("Z010101010101012345789232388") + list(':."===***+++---????!!!!||___+++---') + katakana

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def matrix_rain(duration):
    minTrail=23
    maxTrail=123
    minGaps=2
    maxGaps=16
    minSpeed=0.02
    maxSpeed=0.24
    cols, rows = 90, 80
    drops = [random.randint(0, rows - 1) for _ in range(cols)]
    trail_lengths = [random.randint(minTrail, maxTrail) for _ in range(cols)]
    gaps = [random.randint(minGaps, maxGaps) for _ in range(cols)]
    next_tick = [time.time() for _ in range(cols)]
    speed = [random.uniform(minSpeed, maxSpeed) for _ in range(cols)]
    trails = [[] for _ in range(cols)]  # historial de cada columna

    glitch_animation("THE MATRIX HAS YOU", frames=32, delay=0.16)
    glitch_animation("THE MATRIX IS ON EVERYTHING YOU SEE", frames=32, delay=0.12)
    glitch_animation("FOLLOW THE WHITE RABBIT", frames=32, delay=0.10)
    glitch_animation("WAKE UP NEO", frames=24, delay=0.08)

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            if should_exit.is_set():
                return
            screen = [[(' ', '') for _ in range(cols)] for _ in range(rows)]
            now = time.time()

            for col in range(cols):
                if now >= next_tick[col]:
                    next_tick[col] = now + speed[col]

                    # Si aún no ha llegado al inicio del trazo
                    if drops[col] < gaps[col]:
                        drops[col] += 1
                        continue

                    # Agregar un nuevo carácter al inicio del trazo
                    char = random.choice(CHARS)
                    if char in katakana and random.random() < 0.5:
                        char = char[::-1]
                    if random.random() < 0.2:
                        char = glitch_char(char)

                    trails[col].insert(0, char)

                    # Cortar el trazo para que no exceda su longitud
                    if len(trails[col]) > trail_lengths[col]:
                        trails[col].pop()

                    drops[col] += 1

                    # Cuando el trazo completo desaparece fuera de la pantalla, reiniciamos
                    if drops[col] - len(trails[col]) > rows:
                        drops[col] = 0
                        trails[col] = []
                        trail_lengths[col] = random.randint(minTrail, maxTrail)
                        gaps[col] = random.randint(minGaps, maxGaps)
                        speed[col] = random.uniform(minSpeed, maxSpeed)

                # Pintar la columna con degradado
                for t, c in enumerate(trails[col]):
                    y = drops[col] - t
                    if 0 <= y < rows:
                        if t == 0:
                            color = Fore.LIGHTGREEN_EX
                        else:
                            grad_index = min(t, len(GREEN_GRADIENT) - 1)
                            color = GREEN_GRADIENT[grad_index]
                        screen[y][col] = (c, color)

            clear()
            #for row in screen:
            #    print(''.join(color + char + RESET for char, color in row))
            for row in screen:
                line = ''
                for char, color in row:
                    ancho = wcwidth(char)
                    if ancho == 1:
                        line += color + char + ' ' + RESET
                    else:
                        line += color + char + RESET
                print(line)
            time.sleep(0.02)
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

def parpadeo(msg, max_width):
    # 1. Parpadeo a la izquierda (dos veces)
    for _ in range(2):
        if should_exit.is_set():
            return
        sys.stdout.write("\r" + msg.ljust(max_width))
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write("\r" + " " * max_width)
        sys.stdout.flush()
        time.sleep(0.6)
    print(msg.ljust(max_width))
    time.sleep(0.6)

def despazamiento(msg, max_width):
    if should_exit.is_set():
            return
    # 2. Movimiento hacia la derecha progresivo
    # Empieza en posición 0 y va desplazándose hasta max_width - len(msg)
    max_pos = max_width - len(msg)
    for pos in range(max_pos + 1):
        sys.stdout.write("\r" + " " * pos + msg)
        sys.stdout.flush()
        time.sleep(0.03)
    print()  # Salto de línea al acabar
    time.sleep(0.4)

def intro_boot_sequence():
    BRIGHT_GREEN = "\033[38;2;0;255;0m"
    RESET_COLOR = "\033[0m"
    sys.stdout.write(BRIGHT_GREEN)
    sys.stdout.flush()

    # Mensajes de arranque con parpadeo
    boot_msgs = [
        ">>> [INIT ZION-NΞUROCORΞ-SO_Λ SYSTEM]",
        ">>> [BOOT SEQUENCE INITIATED]",
        ">>> [CHECKING SYSTEM INTEGRITY...█]",
        ">>> [SYSTEM HEALTH: GOOD 7/10]",
        ">>> [LOADING CORE DRIVERS...█]",
        ">>> [DRIVERS LOADED CORRECTLY]",
        ">>> [INITIALIZING MEMORY ALLOCATIONS...█]",
        ">>> [WARN][3 MEMORY ALLOCATIONS CAN'T BE FINDED]",
        ">>> [MEMORY ALLOCATIONS CORRECTLY INITIALIZED",
        ">>> [VERIFYING ENCRYPTION KEYS...█]",
        ">>> [ENCRYPTION KEYS SUCCESSFULLY VERIFIED]",
        ">>> [UPLOADING MODULES...█]",
        ">>> [MODULES UPLOADED SUCCESSFULLY]",
        ">>> [DECRYPTING DATA STREAM...█]",
        ">>> [DATA STREAM DECRYPTED SUCCESSFULLY]",
        ">>> [LOADING NETWORK PROTOCOLS...█]",
        ">>> [NETWORK PROTOCOLS LOADED SUCCESSFULLY]",
        ">>> [SYNCHRONIZING NETWORK NODES...█]",
        ">>> [NETWORK NODES SYNCHRONIZED SUCCESSFULLY]",
        ">>> [LOADING AI PROTOCOLS...█]",
        ">>> [AI PROTOCOLS LOADED SUCCESSFULLY]",
        ">>> [RUNNING DIAGNOSTICS...█]",
        ">>> [DIAGNOSTICS RESULTS:]",
        ">>> [FRAMEWORK: MATRIXCODEX, VERSION: 2.0, COPYRIGHT: THE CREATOR αω]",
        ">>> [MATRIX: MATRIX_2.3, VERSION: 2.3, COPYRIGHT: THE CREATOR αω]",
        ">>> [CONFIGURING ENVIRONMENT VARIABLES...█]",
        ">>> [ENVIRONMENT VARIABLES SUCCESSFULLY CONFIGURED]",
        ">>> [COMPILING MATRIX KERNEL MODULES AND NODES...█]",
        ">>> [KERNEL COMPILATION COMPLETE]",
        ">>> [DEPLOYING MATRIX VIRTUAL MACHINE...█]",
    ]

    max_width = max(len(msg) for msg in boot_msgs + [">>> [__LOADING VISUAL SYSTEM (BRAIN UI)...] █████▒▒▒▒▒▒▒▒▒▒ 100%"])

    # Mostrar logo de Juanito Software primero
    ascii_logo = r"""
                   ^
	          / \
        	 /   \
        	/     \
       	       /   ^   \
      	      /   / \   \
     	     /   /   \   \
    	    /	/     \	  \
	   /__ /____   \   \
	  / \ /		\   \
	 /   /   |------ \  /\
	/   / \  |  --- | \/  \
       /   /   \   | @  | /\   \
      /	  /	\  L---- /  \	\
     /	 /	 \ 	/    \	 \
    /	/_________\____/______\	  \
   /		   \  /		   \
  /_________________\/______________\      
            JUANITO SOFTWARE
    """
    print(ascii_logo)
    time.sleep(2)

    parpadeo("\n>>> [PRESS SPACE TO SKIP THE INTRO]".ljust(max_width), max_width)
    time.sleep(0.4)
    for msg in boot_msgs:
        if should_exit.is_set():
            return
        for _ in range(2):
            sys.stdout.write("\r" + msg.ljust(max_width))
            sys.stdout.flush()
            time.sleep(0.3)
            sys.stdout.write("\r" + " " * max_width)
            sys.stdout.flush()
            time.sleep(0.2)
        print(msg.ljust(max_width))
        time.sleep(0.4) 

    print("\n>>> [INITIAL BOOT LOADED SUCCESSFULLY]".ljust(max_width))

    # Carga con barra visual tipo █▒
    print(">>> [ESTABLISHING ENCRYPTED LINK...]", end="", flush=True)
    time.sleep(0.5)

    for i in range(0, 101, 2):
        bar_length = 20
        filled_length = int(i / 100 * bar_length)
        bar = "█" * filled_length + "▒" * (bar_length - filled_length)
        sys.stdout.write(f"\r>>> [ESTABLISHING ENCRYPTED LINK...]  {bar} {i}%".ljust(max_width))
        sys.stdout.flush()
        time.sleep(0.03)

    print("\n>>> [LINK ESTABLISHED CORRECTLY]".ljust(max_width))
    time.sleep(0.4)
    parpadeo(">>> [AUTHENTICATING USER...]".ljust(max_width), max_width)
    time.sleep(0.4)
    parpadeo(">>> [USER AUTHENTICATED SUCCESSFULLY...]".ljust(max_width), max_width)
    time.sleep(0.4)
    parpadeo("\n>>> [ESTABLISHING SECURE CONNECTION...█]".ljust(max_width), max_width)
    time.sleep(0.4)
    parpadeo("\n>>> [SECURE CONNECTION ESTABLISHED...█]".ljust(max_width), max_width)
    time.sleep(0.4)

    # Carga con barra visual tipo █▒
    print(">>> [CONNECTING TO ZION MAINFRAME...]", end="", flush=True)
    time.sleep(0.5)

    for i in range(0, 101, 2):
        bar_length = 20
        filled_length = int(i / 100 * bar_length)
        bar = "█" * filled_length + "▒" * (bar_length - filled_length)
        sys.stdout.write(f"\r>>> [CONNECTING TO ZION MAINFRAME...]  {bar} {i}%".ljust(max_width))
        sys.stdout.flush()
        time.sleep(0.03)

    print("\n>>> [CONNECTED SUCCESSFULLY TO ZION MAINFRAME WITH THIS CREDENTIALS:\nUSER : Admin\nPassword: 4394e9b89dc2d56fce27562f139d61c6e862c4ff921bd9552c604e7fe36bd399f3d04a3f0c9deba35118bb3309416ca9582832a5133f482e2f1142008012b2fdaf4bed349107800c783463c6920b1d115bf9059380139d5a07e3b29c5dcdd7d6b8795a35979a43be1684108135076dcc8b7fe402fd5ab55f2bce6ccf0d2ac5ce SHA-1024]".ljust(max_width))

    print()  # salto de línea final limpio
    time.sleep(0.5)
    print(">>> [ACCESS GRANTED]".ljust(max_width))

    # Carga con barra visual tipo █▒
    print(">>> [LOADING VISUAL SYSTEM (BRAIN UI)...]", end="", flush=True)
    time.sleep(0.5)

 
    for i in range(0, 101, 2):
        bar_length = 20
        filled_length = int(i / 100 * bar_length)
        bar = "█" * filled_length + "▒" * (bar_length - filled_length)
        sys.stdout.write(f"\r>>> [LOADING VISUAL SYSTEM (BRAIN UI)...]  {bar} {i}%".ljust(max_width))
        sys.stdout.flush()
        time.sleep(0.03)

    print("\n>>> [VISUAL SYSTEM (BRAIN UI) LOADED SUCCESSFULLY]".ljust(max_width))
    
    # Carga con barra visual tipo █▒
    print(">>> [LOADING ENVIRONMENT...]", end="", flush=True)
    time.sleep(0.5)

    for i in range(0, 101, 2):
        bar_length = 20
        filled_length = int(i / 100 * bar_length)
        bar = "█" * filled_length + "▒" * (bar_length - filled_length)
        sys.stdout.write(f"\r>>> [LOADING ENVIRONMENT...]  {bar} {i}%".ljust(max_width))
        sys.stdout.flush()
        time.sleep(0.085)

    print("\n>>> [ENVIRONMENT LOADED SUCCESSFULLY]".ljust(max_width))

    
    time.sleep(0.6)
    print(">>> [READY TO EXECUTE...]\n")
    time.sleep(0.6)
    print()

    # --- INICIO EFECTO DE CARGA CON BARRA ---
    print("INIT MATRIX SIMULATION...\n")
    time.sleep(0.6)
    glitch_animation("01MATRIX10_2.3.RUN", frames=20, delay=0.05)
    despazamiento("____", max_width)
    total = 100
    for i in range(total + 1):
        sys.stdout.write(BRIGHT_GREEN)
        sys.stdout.flush()
        show_fancy_progress_bar(i, total)
        time.sleep(0.02)
    print("\nMATRIX SYSTEM LOAD SUCCESSFULLY. RUNNING MATRIX...")
    time.sleep(0.9)
    # ----------------------------------------

    sys.stdout.write(RESET_COLOR)
    sys.stdout.flush() 

def es_monoespaciado(char):
    ancho = wcwidth(char)
    if ancho == 1:
        return True
    else:
        return False

def mostrar_caracteres_y_ancho(chars):
    for c in chars:
        ancho = wcwidth(c)
        monoesp = es_monoespaciado(c)
        print(f"'{c}' (U+{ord(c):04X}) -> ancho: {ancho} -> {'Monoespaciado' if monoesp else 'No monoespaciado'}")

if __name__ == "__main__": 
    # Iniciar hilo de escucha de la tecla space
    escucha_thread = threading.Thread(target=escucha_tecla_salida, daemon=True)
    escucha_thread.start()

    duration=768 # Valor por defecto

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

    # mostrar_caracteres_y_ancho(CHARS)

    should_exit.clear()   

    # Guardar tiempo antes de la intro
    intro_start = time.time()
    intro_boot_sequence()
    intro_end = time.time()

    
    # Si se presionó espacio, no continuar
    if should_exit.is_set():
        sys.exit()      

    # Calcular cuánto tiempo duró la intro
    intro_duration = intro_end - intro_start

    # Calcular la nueva duración para matrix_rain
    remaining_duration = max(0, duration - intro_duration)

    matrix_rain(remaining_duration)