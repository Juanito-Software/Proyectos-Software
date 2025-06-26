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

import tkinter as tk
import random

CHARS = "01アイウエオカキクケコサシスセソﾊﾋﾌﾍﾎ"

class MatrixRainGraphics(tk.Canvas):
    def __init__(self, master, width, height, font_size=15, *args, **kwargs):
        super().__init__(master, width=width, height=height, bg="black", *args, **kwargs)
        self.font_size = font_size
        self.cols = width // font_size
        self.rows = height // font_size

        self.drops = [random.randint(0, self.rows) for _ in range(self.cols)]

        self.font = ("Courier", self.font_size, "bold")

        self.running = True

        self.frame_count = 0  # Contador de frames

        self.after(0, self.update_rain)

    def update_rain(self):
        if not self.running:
            return

        self.frame_count += 1

        # Pintar el fondo negro cada 10 frames para simular desvanecimiento lento
        if self.frame_count % 25 == 0:
            self.create_rectangle(0, 0, self.winfo_width(), self.winfo_height(), fill="black", outline="")

        for i in range(self.cols):
            char = random.choice(CHARS)
            x = i * self.font_size
            y = self.drops[i] * self.font_size

            self.create_text(x, y, text=char, fill="#00FF00", font=self.font, anchor="nw")

            self.drops[i] += 1

            if self.drops[i] * self.font_size > self.winfo_height() or random.random() > 0.95:
                self.drops[i] = 0

        self.after(100, self.update_rain)

    def stop(self):
        self.running = False


def main():
    root = tk.Tk()
    root.title("Matrix Rain en Tkinter - JuanitoSoftware&Games")

    WIDTH, HEIGHT = 800, 600
    matrix = MatrixRainGraphics(root, width=WIDTH, height=HEIGHT, font_size=15)
    matrix.pack()

    stop_button = tk.Button(root, text="Detener", command=matrix.stop)
    stop_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
