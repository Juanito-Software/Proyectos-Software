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

CHARS = "01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎｶﾞｷｸｹｺ01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#$%^&*       "

class Trail:
    def __init__(self, col, rows, max_length):
        self.col = col
        self.rows = rows
        self.max_length = max_length
        self.chars = []
        self.head_pos = random.randint(0, rows-22)  # empieza en una posición aleatoria
        self.timer = random.randint(0, 100)  # randomiza también el tiempo interno
        self.initial_delay = random.randint(0, 100)  # Retardo antes de empezar a actualizar
        self.speed = random.randint(2, 15)
        self.restart_delay = random.randint(30, 120)
        self.out_time = None
        self.finished = False  # Marca si la cabeza salió del área visible

    def update(self):
        if self.timer < self.initial_delay:
            self.timer += 1
            return  # Aún no comienza esta traza
        self.timer += 1
        if self.timer % self.speed == 0:
            if not self.finished:
                if self.head_pos < self.rows:
                    # Añade un nuevo carácter al final (cabeza blanca)
                    self.chars.insert(0, random.choice(CHARS))
                    self.head_pos += 1

                    # Limita el tamaño de la traza
                    if len(self.chars) > self.max_length:
                        self.chars = self.chars[:self.max_length]
                else:
                    # La cabeza ha salido: empieza la fase pasiva
                        self.finished = True
            else:
                # Fase pasiva: desplaza la cola hacia arriba
                if self.chars:
                    self.chars.pop()  # Desaparece el último carácter
                else:
                    # Ya no queda nada en pantalla, podemos reiniciar
                    self.reset()

    def reset(self):
        self.chars = []
        self.head_pos = 0
        self.timer = 0
        self.speed = random.randint(2, 15)
        self.restart_delay = random.randint(30, 120)
        self.out_time = None
        self.finished = False

    def draw(self, surface, font, font_size):
        for i, char in enumerate(self.chars):
            row = self.head_pos - i
            if 0 <= row < self.rows:
                x = self.col * font_size
                y = row * font_size

                if i == 0:
                    color = (255, 255, 255)  # Cabeza blanca
                else:
                    # Verde decreciente (efecto desvanecimiento)
                    fade = max(0, 255 - i * (255 // self.max_length))
                    color = (0, fade, 0)

                char_surface = font.render(char, True, color)
                surface.blit(char_surface, (x, y))


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
    trails = [Trail(col, rows, 20) for col in range(cols)]

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()     

        surface.fill((0, 0, 0))

        for trail in trails:
            trail.update()
            trail.draw(surface, font, font_size)

        pygame.display.update()
        clock.tick(165)

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
    font = pygame.font.SysFont("MS Gothic", font_size, bold=True)
    cols = screen_width // font_size
    rows = screen_height // font_size

    try:
        matrix_animation(screen, font, cols, rows, font_size)
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
