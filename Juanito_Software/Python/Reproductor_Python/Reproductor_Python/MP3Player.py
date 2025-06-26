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
from tkinter import filedialog, ttk, messagebox
import vlc
import random
import threading
import keyboard
import urllib.parse  # Importa el módulo para manejar URLs
import os
import subprocess
import sys
#import pygame.mixer

#pygame.mixer.init()

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

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Audio")

        # Instancia y reproductor VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.selected_folder = None # Variable para almacenar la carpeta seleccionada

        self.current_media = None
        self.is_paused = False  # Variable para rastrear el estado de pausa

        self.night_mode = False # Variable para alternar modo noche/dia

        # Atajos que solo funcionan con el foco de atencion en esta ventana
        # Configurar el evento de la barra espaciadora  
        self.root.bind("<space>", self.toggle_play_pause)
        # Configurar el evento del enter
        self.root.bind("<Return>", self.on_enter)

        # Agregar atajos globales
        keyboard.add_hotkey('ctrl+space', self.toggle_play_pause)
        keyboard.add_hotkey('ctrl+enter', self.on_enter)

        # Variables para los modos de reproducción
        self.play_in_order = False
        self.play_random = False
        self.play_loop = False
        self.last_index = None  # Índice de la pista reproducida (para los modos orden y aleatorio)
        self.songs = []         # Lista de todas las canciones (IDs del tree) (para el modo aleatorio)
        self.played_random = [] # Canciones ya reproducidas en modo aleatorio (para el modo aleatorio)
        
        # Configuramos el event manager para detectar el fin de la reproducción
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.handle_end_reached)

        # Marco para los controles superiores
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=5)

        # Botón para alternar modo noche
        self.night_button = tk.Button(self.top_frame, text="🌙", command=self.toggle_night_mode)
        self.night_button.pack(side="left")

        # Botón para seleccionar carpeta
        self.choose_folder_btn = tk.Button(self.top_frame, text="Seleccionar carpeta", command=self.select_folder)
        self.choose_folder_btn.pack(side="left")

        # Campo de texto para ingresar la búsqueda
        self.search_entry = tk.Entry(self.top_frame)
        self.search_entry.pack(side="left", padx=(200,5))

        # Botón de búsqueda
        self.search_button = tk.Button(self.top_frame, text="Buscar", command=self.search_files)
        self.search_button.pack(side="right")

        # Treeview para mostrar el árbol de archivos
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = ("path",)
        self.tree.column("#0", width=300)
        self.tree.heading("#0", text="Nombre")
        self.tree.heading("path", text="Ruta")
        self.tree.pack(expand=True, fill="both")
        # Vinculamos doble clic para reproducir la canción
        self.tree.bind("<Double-1>", self.on_double_click)

        # Botones de control: anterior, Play, pause, Stop y siguiente
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=5)
        
        self.prev_button = tk.Button(self.controls_frame, text="⏮", command=self.play_previous)
        self.prev_button.pack(side="left", anchor="sw", padx=(0,20))
        self.play_button = tk.Button(self.controls_frame, text="▶️", command=self.play_selected)
        self.play_button.pack(side="left", padx=(0, 20))
        self.next_button = tk.Button(self.controls_frame, text="⏭", command=self.play_next)
        self.next_button.pack(side="left", padx=(0,20))
        self.pause_button = tk.Button(self.controls_frame, text="⏸️", command=self.pause)
        self.pause_button.pack(side="left", padx=(0, 20))
        self.stop_button = tk.Button(self.controls_frame, text="⏹️", command=self.stop)
        self.stop_button.pack(side="right", padx=(0, 20))


        # Botones de modos de reproducción
        self.mode_frame = tk.Frame(root)
        self.mode_frame.pack(pady=5)

        self.order_button = tk.Button(self.mode_frame, text="Reproducción en Orden", command=self.toggle_order_mode)
        self.order_button.pack(side="left", padx=(0, 20))
        self.random_button = tk.Button(self.mode_frame, text="Reproducción Aleatoria", command=self.toggle_random_mode)
        self.random_button.pack(side="left", padx=(0, 20))
        self.loop_button = tk.Button(self.mode_frame, text="Reproducción en Bucle", command=self.toggle_loop_mode)
        self.loop_button.pack(side="left", padx=(0, 20))

        # Inicializar configuraciones al arrancar
        self.init_settings()
    
    def init_settings(self):
        self.night_mode = False
        self.toggle_night_mode()  # Ejecuta el método para aplicar el modo noche/día

    def toggle_night_mode(self):
        style = ttk.Style()

        if not self.night_mode:
            bg_color = "black"
            fg_color = "lime"
            button_bg = "#222"
            header_bg = "white"
            header_fg = "black"

            style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color)

            style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground=header_fg,
                        font=('TkDefaultFont', 10, 'bold'))

            style.map("Treeview",
                    background=[("selected", "#444")],
                    foreground=[("selected", "white")])

            self.root.configure(bg=bg_color)

        else:
            bg_color = "SystemButtonFace"
            fg_color = "black"
            button_bg = "SystemButtonFace"
            header_bg = "SystemButtonFace"
            header_fg = "black"

            style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color)

            style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground=header_fg,
                        font=('TkDefaultFont', 10, 'bold'))

            style.map("Treeview",
                    background=[("selected", "#0078d7")],
                    foreground=[("selected", "white")])

            self.root.configure(bg=bg_color)

        # Aplicar color de fondo a root y frames
        self.root.configure(bg=bg_color)
        self.top_frame.configure(bg=bg_color)
        self.controls_frame.configure(bg=bg_color)
        self.mode_frame.configure(bg=bg_color)

        # Aplicar color de fondo a botones
        for widget in [self.play_button, self.pause_button, self.stop_button,
                    self.prev_button, self.next_button, self.night_button,
                    self.choose_folder_btn, self.search_button,
                    self.order_button, self.random_button, self.loop_button]:
            widget.configure(bg=button_bg, fg=fg_color)

        # Campo de búsqueda (entrada)
        self.search_entry.configure(bg=button_bg, fg=fg_color, insertbackground=fg_color)

        self.night_mode = not self.night_mode

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.populate_tree(folder)
            # Cuando se selecciona una carpeta, obtenemos todas las canciones del árbol
            self.songs = self.get_all_audio_items()
            # print("Total canciones encontradas:", len(self.songs), flush=True)
            self.played_random = []

    def populate_tree(self, folder):
        # Limpiar el treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Llenar el treeview recursivamente
        self.insert_items("", folder)

    def insert_items(self, parent, path):
        try:
            items = os.listdir(path)
        except PermissionError:
            # En caso de no tener permisos para acceder a alguna carpeta
            return
        for item in sorted(items, key=str.lower):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                # Insertamos la carpeta y llamamos recursivamente para sus contenidos
                node = self.tree.insert(parent, "end", text=item, values=(abs_path,))
                self.insert_items(node, abs_path)
            elif os.path.isfile(abs_path) and item.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
                # Insertamos solo los archivos de audio soportados
                self.tree.insert(parent, "end", text=item, values=(abs_path,))

    def get_all_audio_items(self):
        items = []
        def recurse(parent=""):
            for child in self.tree.get_children(parent):
                file_path = self.tree.item(child, "values")[0]
                if file_path.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
                    items.append(child)
                else:
                    recurse(child)
        recurse("")
        return items

    def search_files(self):
        query = self.search_entry.get().lower()
        if self.selected_folder and query:
            # Limpiar el treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Buscar archivos que coincidan con la consulta
            self.search_in_directory("", self.selected_folder, query)
        elif not self.selected_folder:
            print("Por favor, selecciona una carpeta primero.")
        elif not query:
            # Si la consulta está vacía, repoblar el treeview con todos los archivos
            self.populate_tree(self.selected_folder)

    def search_in_directory(self, parent, path, query):
        try:
            items = os.listdir(path)
        except PermissionError:
            # En caso de no tener permisos para acceder a alguna carpeta
            return
        for item in sorted(items, key=str.lower):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                # Insertamos la carpeta y llamamos recursivamente para sus contenidos
                node = self.tree.insert(parent, "end", text=item, values=(abs_path,))
                self.search_in_directory(node, abs_path, query)
            elif os.path.isfile(abs_path) and item.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
                if query in item.lower():
                    self.tree.insert(parent, "end", text=item, values=(abs_path,))

    def play_selected(self):
        # Obtenemos el elemento seleccionado
        selected = self.tree.selection()
        if selected:
            file_path = self.tree.item(selected[0], "values")[0]
            self.current_file = file_path  # Guardamos la ruta actual


            # Crear un nuevo objeto Media para obtener el MRL correspondiente al file_path
            new_media = self.instance.media_new(file_path)
            new_mrl = new_media.get_mrl()

            if self.is_paused and self.current_media and self.current_media.get_mrl() == new_mrl:
                # Si está en pausa y se selecciona la misma canción, reanudar
                print("Reanudando:", file_path)
                self.player.set_pause(False)
            else:
                # Reproducir nueva canción
                self.current_media = new_media
                self.player.set_media(self.current_media)
                print("Reproduciendo:", file_path)
                self.player.play()
            self.is_paused = False
        else:
            print("Por favor, selecciona un archivo de audio.")

    def pause(self):
        if self.player.is_playing():
            self.player.set_pause(True)
            self.is_paused = True

    def stop(self):
        self.player.stop()
    
    def toggle_play_pause(self, event=None):
        if self.player.is_playing():
            self.pause()
        else:
            self.play_selected()

    def on_double_click(self, event):
        self.play_selected()

    def on_enter(self, event):
        self.search_files()

    def play_next(self):
        if not self.songs:
            return

        if self.current_file:
            current_index = next((i for i, item in enumerate(self.songs)
                                if self.tree.item(item, "values")[0] == self.current_file), None)
            if current_index is not None and current_index + 1 < len(self.songs):
                next_item = self.songs[current_index + 1]
                self.tree.selection_set(next_item)
                self.tree.see(next_item)
                self.play_selected()
            else:
                print("No hay una siguiente canción.")

    def play_previous(self):
        if not self.songs:
            return

        if self.current_file:
            current_index = next((i for i, item in enumerate(self.songs)
                                if self.tree.item(item, "values")[0] == self.current_file), None)
            if current_index is not None and current_index > 0:
                prev_item = self.songs[current_index - 1]
                self.tree.selection_set(prev_item)
                self.tree.see(prev_item)
                self.play_selected()
            else:
                print("No hay una canción anterior.")


    def disable_other_modes(self, exclude):
        if exclude != 'order':
            self.play_in_order = False
            self.order_button.config(relief="raised")
        if exclude != 'random':
            self.play_random = False
            self.random_button.config(relief="raised")
        if exclude != 'loop':
            self.play_loop = False
            self.loop_button.config(relief="raised")

    def toggle_order_mode(self):
        if not self.play_in_order:
            self.disable_other_modes('order')
            self.play_in_order = True
            self.order_button.config(relief="sunken")
            messagebox.showinfo("Modo Reproducción", "Activando reproduccion en orden")
        else:
            self.play_in_order = False
            self.order_button.config(relief="raised")
            messagebox.showinfo("Modo Reproducción", "Desactivando reproduccion en orden")

    def toggle_random_mode(self):
        if not self.play_random:
            self.disable_other_modes('random')
            self.play_random = True
            self.random_button.config(relief="sunken")
            # Al activar el modo aleatorio, volvemos a cargar la lista completa de canciones y reiniciamos el tracking
            self.songs = self.get_all_audio_items()
            self.played_random = []
            messagebox.showinfo("Modo Reproducción", "Activando reproduccion en aleatoria")
        else:
            self.play_random = False
            self.random_button.config(relief="raised")
            messagebox.showinfo("Modo Reproducción", "Desactivando reproduccion en aleatoria")

    def toggle_loop_mode(self):
        if not self.play_loop:
            self.disable_other_modes('loop')
            self.play_loop = True
            self.loop_button.config(relief="sunken")
            messagebox.showinfo("Modo Reproducción", "Activando reproduccion en bucle")
        else:
            self.play_loop = False
            self.loop_button.config(relief="raised")
            messagebox.showinfo("Modo Reproducción", "Desactivando reproduccion en bucle")

    # Funciones para reproducir según el modo activo al terminar una pista
    def handle_end_reached(self, event):
        print("Evento fin de pista detectado, estado random:", self.play_random, flush=True)
        self.root.after(0, self._handle_end)

    def _handle_end(self):
        if self.play_in_order:
            self.play_next_in_order()
        elif self.play_random:
            self.play_random_after()
        elif self.play_loop:
            self.play_loop_current()

    def play_next_in_order(self):
        # Obtener todas las pistas de audio disponibles
        all_songs = self.get_all_audio_items()
        if not all_songs:
            print("No hay pistas disponibles para reproducir.")
            return

        # Obtener el índice de la pista actual
        current_index = None
        if hasattr(self, 'current_file') and self.current_file:
            for index, item in enumerate(all_songs):
                file_path = self.tree.item(item, "values")[0]
                if file_path == self.current_file:
                    current_index = index
                    break

        # Determinar el índice de la siguiente pista
        if current_index is not None:
            next_index = current_index + 1
            if next_index < len(all_songs):
                next_item = all_songs[next_index]
                next_file_path = self.tree.item(next_item, "values")[0]
                self.current_file = next_file_path  # Actualizar la pista actual
                new_media = self.instance.media_new(next_file_path)
                self.current_media = new_media
                self.player.set_media(new_media)
                print("Reproduciendo en orden:", next_file_path)
                self.player.play()
            else:
                print("No hay más pistas para reproducir en orden. Reinciando")
                # Si ya se reprodujeron todas, reiniciamos el tracking
                next_index=0
        else:
            print("No se pudo determinar la pista actual.")

    def play_random_after(self):
        if not self.play_random or not self.songs:
            return
        # Seleccionamos las canciones disponibles que aún no han sido reproducidas
        available = [item for item in self.songs if item not in self.played_random]
        if not available:
            # Si ya se reprodujeron todas, reiniciamos el tracking
            self.played_random = []
            available = self.songs.copy()
        chosen = random.choice(available)
        file_path = self.tree.item(chosen, "values")[0]
        self.played_random.append(chosen)
        self.last_index = self.songs.index(chosen)
        new_media = self.instance.media_new(file_path)
        self.current_media = new_media
        self.player.set_media(new_media)
        print("Reproduciendo de forma aleatoria:", file_path)
        self.player.play()

    def play_loop_current(self):
        if hasattr(self, 'current_file') and self.current_file:
            print("Reproduciendo en bucle:", self.current_file)
            self.root.after( 0, self._restart_loop)

    def _restart_loop(self):
        new_media = self.instance.media_new(self.current_file)
        self.current_media = new_media
        self.player.set_media(new_media)
        self.player.play()

        # Atajos globales
    def toggle_play_pause_hotkey(self):
        if self.player.is_playing():
            self.pause()
        else:
            self.play_selected()

    def play_next_hotkey(self):
        self.play_next()

    def play_previous_hotkey(self):
        self.play_previous()

    def stop_hotkey(self):
        self.stop()

    def toggle_loop_mode_hotkey(self):
        self.toggle_loop_mode()

    def toggle_random_mode_hotkey(self):
        self.toggle_random_mode()
    
    def toggle_order_mode_hotkey(self):
        self.toggle_order_mode()

def setup_global_hotkeys(app):
        keyboard.add_hotkey("ctrl+space", lambda: app.toggle_play_pause_hotkey())
        keyboard.add_hotkey("ctrl+right", lambda: app.play_next_hotkey())
        keyboard.add_hotkey("ctrl+left", lambda: app.play_previous_hotkey())
        keyboard.add_hotkey("ctrl+s", lambda: app.stop_hotkey())
        keyboard.add_hotkey("ctrl+l", lambda: app.toggle_loop_mode_hotkey())
        keyboard.add_hotkey("ctrl+r", lambda: app.toggle_random_mode_hotkey())
        keyboard.add_hotkey("ctrl+t", lambda: app.toggle_order_mode_hotkey())

if __name__ == "__main__":
    try:
        run_matrix_effect()
    except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
    except Exception as e:
        print(f"Error inesperado ejecutando matrix_effect.exe: {e}")
    finally:
        root = tk.Tk()
        app = MP3Player(root)
        threading.Thread(target=setup_global_hotkeys, args=(app,), daemon=True).start()   
        root.mainloop()