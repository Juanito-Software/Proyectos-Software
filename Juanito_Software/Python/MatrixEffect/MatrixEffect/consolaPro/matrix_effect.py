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

from rich.console import Console
from rich.style import Style
from rich.text import Text
import random
import time
import shutil

console = Console()

CHARS = "01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎｶﾞｷｸｹｺ01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#$%^&*       "

class Trail:
    def __init__(self, col, rows):
        self.col = col
        self.rows = rows
        self.reset()

    def reset(self):
        self.max_length = random.randint(5, 20)
        self.speed = random.randint(1, 4)
        self.timer = 0
        self.head_pos = random.randint(-self.max_length, 0)
        self.chars = []
        self.finished = False

    def update(self):
        self.timer += 1
        if self.timer % self.speed != 0:
            return
        if not self.finished:
            self.head_pos += 1
            if 0 <= self.head_pos < self.rows:
                self.chars.insert(0, random.choice(CHARS))
            if len(self.chars) > self.max_length:
                self.finished = True
        else:
            if self.chars:
                self.chars.pop()
            else:
                self.reset()

def matrix_rain_rich(duration=30):
    cols, rows = shutil.get_terminal_size()
    trails = [Trail(c, rows) for c in range(cols)]
    start = time.time()

    while time.time() - start < duration:
        console.clear()
        # Construir cada fila como un objeto Text para controlar colores
        for row in range(rows):
            line = Text()
            col_index = 0
            while col_index < cols:
                trail = trails[col_index]
                chs = trail.chars
                # posición del char en esa columna y fila
                char_index = trail.head_pos - row
                if 0 <= char_index < len(chs):
                    ch = chs[char_index]
                    if char_index == 0:
                        style = Style(color="white", bold=True)
                    else:
                        style = Style(color="green")
                    line.append(ch, style=style)
                    # Avanzar por el ancho del carácter
                    w = console.measure(ch).maximum
                    if w == 0:
                        w = 1
                    col_index += w
                else:
                    line.append(" ")
                    col_index += 1
            console.print(line, end="")
        for trail in trails:
            trail.update()
        time.sleep(0.05)

if __name__ == "__main__":
    matrix_rain_rich(60)
