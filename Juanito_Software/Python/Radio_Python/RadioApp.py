# Copyright (C) 2025 JuanitoSoftware
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
from tkinter import messagebox
import vlc  # Asegúrate de tener instalado python-vlc
import csv
import os
import subprocess
import sys

def run_matrix_effect():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_path, "matrix_effect.exe")

    # Ejecutamos el .exe y esperamos a que termine (sin ventana de consola si usas noconsole)
    # creationflags para abrir sin ventana, opcional si usas --noconsole en PyInstaller
    # Aquí dejamos que se abra la consola porque es el efecto matrix
    subprocess.run([exe_path], check=True)

def cargar_emisoras(archivo):
    emisoras = []
    if not os.path.exists(archivo):
        messagebox.showerror("Error", f"No se encontró el archivo de emisoras:\n{archivo}")
        return emisoras

    try:
        with open(archivo, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Saltar cabecera si existe
            cabecera = next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                nombre = row[0].strip()
                url = row[1].strip()
                if not nombre or not url or url == "?":
                    continue
                emisoras.append({"nombre": nombre, "url": url})
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar las emisoras:\n{e}")
    return emisoras

class RadioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radio Player")

        # Modo noche activado o no
        self.night_mode = False

        # Estado de reproducción
        self.is_playing = False
        
        # Inicializamos VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Cargar emisoras desde el CSV
        self.emisoras = cargar_emisoras("Radios.csv")
        print("Emisoras cargadas:", self.emisoras)

        # Lista filtrada que se muestra en el Listbox
        self.emisoras_filtradas = list(self.emisoras)

        # Frame superior para controles (modo noche y búsqueda)
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=5, fill="x")

        # Botón para alternar modo noche/día
        self.night_button = tk.Button(self.top_frame, text="🌙", width=3, command=self.toggle_night_mode)
        self.night_button.pack(side="left", padx=5)

        # Campo de búsqueda
        tk.Label(self.top_frame, text="Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.top_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Crear un Listbox para mostrar las emisoras
        self.listbox = tk.Listbox(root, height=12, width=50)
        self.refrescar_listbox()
        self.listbox.pack(pady=10, fill="both", expand=True)

        # Asignar evento de doble clic
        self.listbox.bind("<Double-Button-1>", self.on_double_click)
        
        # Frame inferior para botones y volumen
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(pady=5)

        # Botón para reproducir la emisora seleccionada
        self.play_button = tk.Button(self.bottom_frame, text="Reproducir", command=self.play_selected)
        self.play_button.grid(row=0, column=0, padx=5)

        # Botón para detener la reproducción
        self.stop_button = tk.Button(self.bottom_frame, text="Detener", command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Control de volumen
        tk.Label(self.bottom_frame, text="Volumen").grid(row=0, column=2, padx=5)
        self.volume_var = tk.IntVar(value=70)
        self.volume_scale = tk.Scale(
            self.bottom_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume_var,
            command=self.on_volume_change,
            length=150,
        )
        self.volume_scale.grid(row=0, column=3, padx=5)
        self.player.audio_set_volume(self.volume_var.get())

        # Etiqueta de estado
        self.status_var = tk.StringVar(value="Listo")
        self.status_label = tk.Label(root, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", padx=5, pady=(0, 5))

        # Vincular la tecla Space y Enter para iniciar/pausar
        self.root.bind("<space>", self.toggle_play_pause)
        self.root.bind("<Return>", self.toggle_play_pause)

        # Iniciar con modo claro y aplicar tema
        self.toggle_night_mode()

        # Cerrar limpiamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def refrescar_listbox(self):
        self.listbox.delete(0, tk.END)
        for emisora in self.emisoras_filtradas:
            self.listbox.insert(tk.END, emisora["nombre"])

    def on_search_change(self, event=None):
        texto = self.search_var.get().strip().lower()
        if not texto:
            self.emisoras_filtradas = list(self.emisoras)
        else:
            self.emisoras_filtradas = [
                e for e in self.emisoras if texto in e["nombre"].lower()
            ]
        self.refrescar_listbox()

    def toggle_night_mode(self):
        if not self.night_mode:
            # Activar modo noche
            bg = "black"
            fg = "lime"
            self.root.configure(bg=bg)
            self.top_frame.configure(bg=bg)
            self.listbox.configure(bg=bg, fg=fg, selectbackground="#444", selectforeground="white")
            self.play_button.configure(bg="#222", fg=fg)
            self.stop_button.configure(bg="#222", fg=fg)
            self.night_button.configure(bg="#222", fg=fg)
        else:
            # Activar modo día
            bg = "SystemButtonFace"
            fg = "black"
            self.root.configure(bg=bg)
            self.top_frame.configure(bg=bg)
            self.listbox.configure(bg="white", fg=fg, selectbackground="#0078d7", selectforeground="white")
            self.play_button.configure(bg=bg, fg=fg)
            self.stop_button.configure(bg=bg, fg=fg)
            self.night_button.configure(bg=bg, fg=fg)

        # Alternar estado
        self.night_mode = not self.night_mode

    def obtener_emisora_seleccionada(self):
        selection = self.listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        if index < 0 or index >= len(self.emisoras_filtradas):
            return None
        return self.emisoras_filtradas[index]

    def play_selected(self):
        emisora = self.obtener_emisora_seleccionada()
        if emisora is None:
            messagebox.showinfo("Información", "Por favor, selecciona una emisora.")
            return

        stream_url = emisora["url"]
        print(f"Reproduciendo {emisora['nombre']} desde {stream_url}")

        try:
            media = self.instance.media_new(stream_url)
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True
            self.status_var.set(f"Reproduciendo: {emisora['nombre']}")
        except Exception as e:
            self.is_playing = False
            self.status_var.set("Error al reproducir")
            messagebox.showerror(
                "Error",
                f"No se pudo reproducir la emisora:\n{emisora['nombre']}\n\nDetalle: {e}",
            )
        
    def stop(self):
        try:
            self.player.stop()
        finally:
            self.is_playing = False
            self.status_var.set("Detenido")
    
    def toggle_play_pause(self, event):
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.status_var.set("Pausado")
        else:
            self.player.play()
            self.is_playing = True
            self.status_var.set("Reproduciendo")
    
    def on_double_click(self, event):
        self.stop()  # Detener la reproducción actual
        self.play_selected()  # Reproducir la nueva emisora seleccionada

    def on_volume_change(self, value):
        try:
            self.player.audio_set_volume(int(float(value)))
        except Exception:
            pass

    def on_close(self):
        try:
            self.player.stop()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    try:
        run_matrix_effect()
    except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
    except Exception as e:
        print(f"Error inesperado ejecutando matrix_effect.exe: {e}")
    finally:
        root = tk.Tk()
        app = RadioApp(root)
        root.mainloop()
