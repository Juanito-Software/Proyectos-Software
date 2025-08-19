
# Copyright (C) 2025 Juanito Software
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
import pygame
import threading
import os
import sys
import time
import ctypes
from pygame import Surface

CHARS = "01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎ"

def play_music(filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"No se pudo reproducir la canción: {e}")

def get_desktop_size():
    return ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

def make_window_clickthrough(hwnd):
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x80000
    WS_EX_TRANSPARENT = 0x20

    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

def send_window_to_back(hwnd):
    HWND_BOTTOM = 1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010

    ctypes.windll.user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                                       SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

def matrix_animation(surface: Surface, font, cols, rows, font_size):
    drops = [random.randint(0, rows) for _ in range(cols)]
    while True:
        if not pygame.display.get_active():
            time.sleep(0.1)
            continue

        surface.fill((0, 0, 0))
        for i in range(cols):
            char = random.choice(CHARS)
            char_surface = font.render(char, True, (0, 255, 0))
            x = i * font_size
            y = drops[i] * font_size
            surface.blit(char_surface, (x, y))
            if y > surface.get_height() or random.random() > 0.95:
                drops[i] = 0
            else:
                drops[i] += 1
        pygame.display.update()
        pygame.time.delay(50)

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    music_file = os.path.join(base_path, "MatrixSoundtrack.mp3")
    threading.Thread(target=play_music, args=(music_file,), daemon=True).start()

    pygame.init()
    screen_width, screen_height = get_desktop_size()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Matrix Desktop")

    hwnd = pygame.display.get_wm_info()["window"]
    make_window_clickthrough(hwnd)
    send_window_to_back(hwnd)

    font_size = 18
    try:
        font = pygame.font.SysFont("MS Gothic", font_size)
    except:
        print("Fuente no soportada, usando Consolas.")
        font = pygame.font.SysFont("Consolas", font_size)

    cols = screen_width // font_size
    rows = screen_height // font_size

    try:
        matrix_animation(screen, font, cols, rows, font_size)
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
