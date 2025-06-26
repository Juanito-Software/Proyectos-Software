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

import tkinter as tk
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
        with open(archivo, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Saltar la cabecera
            for row in reader:
                emisoras.append({"nombre": row[0], "url": row[1]})
        return emisoras

class RadioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radio Player")

        # Modo noche activado o no
        self.night_mode = False
        
        # Inicializamos VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        # Cargar emisoras desde el CSV
        self.emisoras = cargar_emisoras("Radios.csv")
        print("Emisoras cargadas:", self.emisoras)

        # Frame superior para el botón de modo noche
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=5)

        # Botón para alternar modo noche/día
        self.night_button = tk.Button(self.top_frame, text="🌙", command=self.toggle_night_mode)
        self.night_button.pack(side="left", padx=10)
        
        # Crear un Listbox para mostrar las emisoras
        self.listbox = tk.Listbox(root, height=10, width=50)
        for emisora in self.emisoras:
            self.listbox.insert(tk.END, emisora["nombre"])
        self.listbox.pack(pady=10)

        # Asignar evento de doble clic
        self.listbox.bind("<Double-Button-1>", self.on_double_click)
        
        # Botón para reproducir la emisora seleccionada
        self.play_button = tk.Button(root, text="Reproducir Seleccionada", command=self.play_selected)
        self.play_button.pack(pady=5)
        
        # Botón para detener la reproducción
        self.stop_button = tk.Button(root, text="Detener", command=self.stop)
        self.stop_button.pack(pady=5)

        # Vincular la tecla Space para iniciar/pausar
        self.root.bind("<space>", self.toggle_play_pause)

        # Vincular la tecla enter para iniciar/pausar
        self.root.bind("<Return>", self.toggle_play_pause)

        # Iniciar con modo claro y aplicar tema
        self.toggle_night_mode()

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

    def play_selected(self):
        # Obtener la emisora seleccionada del Listbox
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            stream_url = self.emisoras[index]["url"]
            print(f"Reproduciendo {self.emisoras[index]['nombre']} desde {stream_url}")
            media = self.instance.media_new(stream_url)
            self.player.set_media(media)
            self.is_playing = True
            self.player.play()
        else:
            print("Por favor, selecciona una emisora.")
        
    def stop(self):
        self.player.stop()
        self.is_playing = False
    
    def toggle_play_pause(self, event):
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
        else:
            self.player.play()
            self.is_playing = True
    
    def on_double_click(self, event):
        self.stop()  # Detener la reproducción actual
        self.play_selected()  # Reproducir la nueva emisora seleccionada


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
