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

import soundcard as sc
import tkinter as tk
from tkinter import ttk
import numpy as np
import queue
import threading

class WaveformApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizer Audio Multi")

        # Lista de altavoces
        self.speakers = sc.all_speakers()
        valores = [f"{i} - {s.name}" for i, s in enumerate(self.speakers)]
        self.combo = ttk.Combobox(root, values=valores, width=80, state="readonly")
        self.combo.pack(padx=10, pady=(10,5))

        btn_play = tk.Button(root, text="Play", command=self.iniciar_visualizacion)
        btn_play.pack(pady=5)

        self.q = queue.Queue(maxsize=8)
        self._update_job = None
        self.window_visual = None
        self.recorder = None

    def _get_selected_speaker(self):
        idx = self.combo.current()
        if idx < 0:
            return None
        return self.speakers[idx]

    def iniciar_visualizacion(self):
        speaker = self._get_selected_speaker()
        if not speaker:
            return

        ritmo = 44100
        bloque = 8192

        self.window_visual = tk.Toplevel(self.root)
        self.window_visual.title("Visualización")

        # Canvases: forma de onda, espectro FFT, onda ASCII, espectro por bandas
        self.canvas_fft = tk.Canvas(self.window_visual, bg="black", height=100)
        self.canvas_wave_ascii = tk.Canvas(self.window_visual, bg="black", height=100)
        self.canvas_wave = tk.Canvas(self.window_visual, bg="black", height=200)
        self.canvas_fft_bandas = tk.Canvas(self.window_visual, bg="black", height=100)
        self.canvas_linea = tk.Canvas(self.window_visual, bg="black", height=100)
        
        # Empaquetar
        self.canvas_fft.pack(fill="both", expand=True)
        self.canvas_wave_ascii.pack(fill="both", expand=True)
        self.canvas_wave.pack(fill="both", expand=True)
        self.canvas_fft_bandas.pack(fill="both", expand=True)
        self.canvas_linea.pack(fill="both", expand=True) 

        # Para la línea continua tipo ECG
        self.linea_buffer = []  # Mantener histórico de amplitudes
        self.linea_max_length = 800  # Ancho máximo de puntos a dibujar

        # Crear recorder usando loopback
        speaker_name = speaker.name
        self.recorder = sc.get_microphone(speaker_name, include_loopback=True).recorder(
            samplerate=ritmo, blocksize=bloque
        )

        self._schedule_update()
        self.window_visual.protocol("WM_DELETE_WINDOW", self.parar_stream)

        # Hilo de captura de audio
        def grabar():
            with self.recorder as rec:
                while True:
                    data = rec.record(numframes=bloque)
                    mono = data.mean(axis=1)  # Convertir a mono
                    mono = np.nan_to_num(mono)  # reemplazar NaN por 0
                    try:
                        self.q.put_nowait(mono)
                    except queue.Full:
                        pass

        threading.Thread(target=grabar, daemon=True).start()

    def _schedule_update(self):
        self._update_plot()
        self._update_job = self.root.after(30, self._schedule_update)

    def _update_plot(self):
        last = None
        try:
            while True:
                last = self.q.get_nowait()
        except queue.Empty:
            pass

        if last is not None:
            last = np.nan_to_num(last)  # evitar NaN en todas las visualizaciones
            self.dibujar_wave(self.canvas_wave, last)
            self.dibujar_fft(self.canvas_fft, last)
            self.dibujar_wave_ascii(self.canvas_wave_ascii, last)
            self.dibujar_fft_bandas(self.canvas_fft_bandas, last)
            self.dibujar_linea_continua(self.canvas_linea, last)

    def dibujar_wave(self, canvas, data):
        canvas.delete("plot")
        w = canvas.winfo_width() or 800
        h = canvas.winfo_height() or 200

        if len(data) == 0:
            return

        # Normalizar y aplicar ganancia
        muestras = np.nan_to_num(data)
        ganancia = 50   # factor de ganancia
        muestras *= ganancia
        max_val = np.max(np.abs(muestras))
        if max_val == 0:
            max_val = 1
        muestras /= max_val  # ahora están entre -1 y 1

        step = max(1, len(muestras)//w)
        muestras = muestras[::step]

        centro = h // 2
        factor = centro * 0.9  # 0.9 para dejar margen
        coords = [(x, int(centro - v*factor)) for x, v in enumerate(muestras)]

        if len(coords) >= 2:
            flat = [c for xy in coords for c in xy]
            canvas.create_line(flat, fill="lime", tag="plot", width=1.5, smooth=True)


    def dibujar_fft(self, canvas, data):
        canvas.delete("plot")
        w = canvas.winfo_width() or 800
        h = canvas.winfo_height() or 100
        if len(data) == 0:
            return

        data = np.nan_to_num(data)
        fft_vals = np.fft.rfft(data)
        fft_mag = np.abs(fft_vals)

        if np.max(fft_mag) > 0:
            fft_mag = fft_mag / np.max(fft_mag)
        ganancia = 25
        fft_mag = np.clip(fft_mag * ganancia, 0, 1)

        step = max(1, len(fft_mag)//w)
        muestras = fft_mag[::step]
        coords = [(x, h - int(v*h)) for x, v in enumerate(muestras)]
        if len(coords) >= 2:
            flat = [c for xy in coords for c in xy]
            canvas.create_line(flat, fill="orange", tag="plot", width=1.5, smooth=True)

    def dibujar_wave_ascii(self, canvas, data):
        canvas.delete("plot")
        w = canvas.winfo_width() or 800
        h = canvas.winfo_height() or 100
        if len(data) == 0:
            return
        step = max(1, len(data)//w)
        muestras = np.nan_to_num(data[::step])
        centro = h//2
        factor = centro * 0.9 / max(1e-6, np.max(np.abs(muestras)))
        for x, v in enumerate(muestras):
            y = int(centro - v*factor)
            canvas.create_line(x, centro, x, y, fill="cyan", tag="plot")

    def dibujar_fft_bandas(self, canvas, data):
        canvas.delete("plot")
        w = canvas.winfo_width() or 800
        h = canvas.winfo_height() or 100
        if len(data) == 0:
            return

        data = np.nan_to_num(data)
        fft_vals = np.fft.rfft(data)
        fft_mag = np.abs(fft_vals)

        if np.max(fft_mag) > 0:
            fft_mag = fft_mag / np.max(fft_mag)
        ganancia = 25
        fft_mag = np.clip(fft_mag * ganancia, 0, 1)

        freqs = np.fft.rfftfreq(len(data), 1/44100)
        bandas = [100, 500, 1000, 2000, 5000, 10000]
        valores = []

        for i in range(len(bandas)):
            if i == 0:
                mask = freqs <= bandas[i]
            else:
                mask = (freqs > bandas[i-1]) & (freqs <= bandas[i])
            if np.any(mask):
                valores.append(np.mean(fft_mag[mask]))
            else:
                valores.append(0)

        ancho_barra = w // len(valores)
        for i, v in enumerate(valores):
            x0 = i * ancho_barra + 5
            y0 = h
            x1 = (i + 1) * ancho_barra - 5
            y1 = h - int(v * h)

            # Definir color según valor
            if v < 0.33:
                color = "green"      # banda baja
            elif v < 0.66:
                color = "yellow"     # banda media
            else:
                color = "red"        # banda alta

            canvas.create_rectangle(x0, y0, x1, y1, fill=color, tag="plot")
            canvas.create_text((x0 + x1) // 2, h - 10, text=f"{bandas[i]}Hz", fill="Grey", font=("Arial", 8), tag="plot")
 

    def dibujar_linea_continua(self, canvas, data):
        canvas.delete("plot")
        w = canvas.winfo_width() or 800
        h = canvas.winfo_height() or 100
        if len(data) == 0:
            return

        # Procesamos los datos
        data = np.nan_to_num(data)
        fft_vals = np.fft.rfft(data)
        fft_mag = np.abs(fft_vals)
        if np.max(fft_mag) > 0:
            fft_mag = fft_mag / np.max(fft_mag)

        ganancia = 35  # escala para que no toque los bordes
        valor = np.mean(fft_mag) * ganancia

        # centramos verticalmente
        y = h//2 - int(valor * (h//2))

        # Añadimos el nuevo valor al buffer
        self.linea_buffer.append(y)

        # Calculamos el ancho máximo visible antes de empezar a desplazar
        max_visible_points = w // 2

        # Si superamos el límite visible, desplazamos todo a la izquierda
        if len(self.linea_buffer) > max_visible_points:
            self.linea_buffer.pop(0)  # eliminar el más antiguo

        # Dibujamos la línea
        if len(self.linea_buffer) >= 2:
            coords = []
            for i, y_val in enumerate(self.linea_buffer):
                # Calculamos la posición x relativa
                x_pos = i if len(self.linea_buffer) < max_visible_points else (w//2 - len(self.linea_buffer) + i)
                coords.extend([x_pos, y_val])
            canvas.create_line(coords, fill="#FF00FF", width=2, smooth=True, tag="plot")



    def parar_stream(self):
        if self._update_job:
            self.root.after_cancel(self._update_job)
            self._update_job = None
        if self.window_visual:
            self.window_visual.destroy()
            self.window_visual = None
        with self.q.mutex:
            self.q.queue.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = WaveformApp(root)
    root.mainloop()
