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
import os
import subprocess
import sys
from pynput import keyboard as pynput_keyboard

def run_matrix_effect():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_path, "matrix_effect.exe")
    subprocess.run([exe_path], check=True)

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Audio")
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.selected_folder = None
        self.current_media = None
        self.current_file = None
        self.is_paused = False
        self.night_mode = False

        self.play_in_order = False
        self.play_random = False
        self.play_loop = False
        self.last_index = None
        self.songs = []
        self.played_random = []

        self.player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached, self.handle_end_reached
        )

        self.build_ui()
        self.init_settings()

    def build_ui(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=5)

        self.night_button = tk.Button(self.top_frame, text="🌙", command=self.toggle_night_mode)
        self.night_button.pack(side="left")
        self.choose_folder_btn = tk.Button(self.top_frame, text="Seleccionar carpeta", command=self.select_folder)
        self.choose_folder_btn.pack(side="left")
        self.search_entry = tk.Entry(self.top_frame)
        self.search_entry.pack(side="left", padx=(200, 5))
        self.search_button = tk.Button(self.top_frame, text="Buscar", command=self.search_files)
        self.search_button.pack(side="right")

        self.tree = ttk.Treeview(self.root, columns=("path",))
        self.tree.column("#0", width=300)
        self.tree.heading("#0", text="Nombre")
        self.tree.heading("path", text="Ruta")
        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<Double-1>", self.on_double_click)

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=5)
        self.prev_button = tk.Button(self.controls_frame, text="⏮", command=self.play_previous)
        self.prev_button.pack(side="left", padx=(0, 20))
        self.play_button = tk.Button(self.controls_frame, text="▶️", command=self.play_selected)
        self.play_button.pack(side="left", padx=(0, 20))
        self.next_button = tk.Button(self.controls_frame, text="⏭", command=self.play_next)
        self.next_button.pack(side="left", padx=(0, 20))
        self.pause_button = tk.Button(self.controls_frame, text="⏸️", command=self.pause)
        self.pause_button.pack(side="left", padx=(0, 20))
        self.stop_button = tk.Button(self.controls_frame, text="⏹️", command=self.stop)
        self.stop_button.pack(side="right", padx=(0, 20))

        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(pady=5)
        self.order_button = tk.Button(self.mode_frame, text="Reproducción en Orden", command=self.toggle_order_mode)
        self.order_button.pack(side="left", padx=(0, 20))
        self.random_button = tk.Button(self.mode_frame, text="Reproducción Aleatoria", command=self.toggle_random_mode)
        self.random_button.pack(side="left", padx=(0, 20))
        self.loop_button = tk.Button(self.mode_frame, text="Reproducción en Bucle", command=self.toggle_loop_mode)
        self.loop_button.pack(side="left", padx=(0, 20))

        self.root.bind("<space>", self.toggle_play_pause)
        self.root.bind("<Return>", self.on_enter)

    def init_settings(self):
        self.night_mode = False
        self.toggle_night_mode()

    def toggle_night_mode(self):
        style = ttk.Style()
        if not self.night_mode:
            bg, fg, btn_bg = "black", "lime", "#222"
            sel_bg, sel_fg = "black", "white"
        else:
            bg, fg, btn_bg = "SystemButtonFace", "black", "SystemButtonFace"
            sel_bg, sel_fg = "#0078d7", "white"

        style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg)
        style.configure("Treeview.Heading", background=bg, foreground=fg, font=('TkDefaultFont', 10, 'bold'))
        style.map("Treeview", background=[("selected", sel_bg)], foreground=[("selected", sel_fg)])

        for frame in [self.root, self.top_frame, self.controls_frame, self.mode_frame]:
            frame.configure(bg=bg)

        for widget in [
            self.play_button, self.pause_button, self.stop_button, self.prev_button, self.next_button,
            self.night_button, self.choose_folder_btn, self.search_button,
            self.order_button, self.random_button, self.loop_button
        ]:
            widget.configure(bg=btn_bg, fg=fg)

        self.search_entry.configure(bg=btn_bg, fg=fg, insertbackground=fg)
        self.night_mode = not self.night_mode

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.populate_tree(folder)
            self.songs = self.get_all_audio_items()
            self.played_random = []

    def populate_tree(self, folder):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.insert_items("", folder)

    def insert_items(self, parent, path):
        try:
            items = os.listdir(path)
        except PermissionError:
            return
        for item in sorted(items, key=str.lower):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                node = self.tree.insert(parent, "end", text=item, values=(abs_path,))
                self.insert_items(node, abs_path)
            elif os.path.isfile(abs_path) and abs_path.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
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
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.search_in_directory("", self.selected_folder, query)
        elif not self.selected_folder:
            print("Selecciona una carpeta primero.")
        else:
            self.populate_tree(self.selected_folder)

    def search_in_directory(self, parent, path, query):
        try:
            items = os.listdir(path)
        except PermissionError:
            return
        has_match = False
        for item in sorted(items, key=str.lower):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                node = self.tree.insert(parent, "end", text=item, values=(abs_path,))
                self.search_in_directory(node, abs_path, query)
            elif os.path.isfile(abs_path) and query in item.lower() and abs_path.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
                self.tree.insert(parent, "end", text=item, values=(abs_path,))
                has_match = True
        if not has_match and parent:
            self.tree.delete(parent)

    def play_selected(self):
        selected = self.tree.selection()
        if selected:
            file_path = self.tree.item(selected[0], "values")[0]
            if not os.path.isfile(file_path):
                print("Archivo no encontrado:", file_path)
                return
            self.current_file = file_path
            new_media = self.instance.media_new(file_path)
            if self.is_paused and self.current_media and self.current_media.get_mrl() == new_media.get_mrl():
                self.player.set_pause(False)
            else:
                self.current_media = new_media
                self.player.set_media(new_media)
                self.player.play()
            self.is_paused = False

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

    def on_double_click(self, event): self.play_selected()
    def on_enter(self, event): self.search_files()
    def play_next(self): self._play_relative(1)
    def play_previous(self): self._play_relative(-1)

    def _play_relative(self, direction):
        if not self.songs or not self.current_file:
            return
        current_index = next((i for i, item in enumerate(self.songs)
                              if self.tree.item(item, "values")[0] == self.current_file), None)
        if current_index is not None:
            new_index = current_index + direction
            if 0 <= new_index < len(self.songs):
                target = self.songs[new_index]
                self.tree.selection_set(target)
                self.tree.see(target)
                self.play_selected()

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
        self.play_in_order = not self.play_in_order
        self.disable_other_modes('order' if self.play_in_order else '')
        self.order_button.config(relief="sunken" if self.play_in_order else "raised")
        messagebox.showinfo("Modo Reproducción", f"{'Activando' if self.play_in_order else 'Desactivando'} reproducción en orden")

    def toggle_random_mode(self):
        self.play_random = not self.play_random
        self.disable_other_modes('random' if self.play_random else '')
        self.random_button.config(relief="sunken" if self.play_random else "raised")
        if self.play_random:
            self.songs = self.get_all_audio_items()
            self.played_random = []
        messagebox.showinfo("Modo Reproducción", f"{'Activando' if self.play_random else 'Desactivando'} reproducción aleatoria")

    def toggle_loop_mode(self):
        self.play_loop = not self.play_loop
        self.disable_other_modes('loop' if self.play_loop else '')
        self.loop_button.config(relief="sunken" if self.play_loop else "raised")
        messagebox.showinfo("Modo Reproducción", f"{'Activando' if self.play_loop else 'Desactivando'} reproducción en bucle")

    def handle_end_reached(self, event):
        self.root.after(0, self._handle_end)

    def _handle_end(self):
        if self.play_in_order:
            self.play_next()
        elif self.play_random:
            self.play_random_after()
        elif self.play_loop:
            self.play_loop_current()

    def play_random_after(self):
        available = [item for item in self.songs if item not in self.played_random]
        if not available:
            self.played_random = []
            available = self.songs.copy()
        chosen = random.choice(available)
        file_path = self.tree.item(chosen, "values")[0]
        self.played_random.append(chosen)
        self.tree.selection_set(chosen)
        self.tree.see(chosen)
        self.play_selected()

    def play_loop_current(self):
        if self.current_file:
            self.tree.selection_set(self.current_file)
            self.play_selected()


class HotkeyListener:
    def __init__(self, app):
        self.app = app
        self.ctrl_pressed = False

    def on_press(self, key):
        try:
            if key == pynput_keyboard.Key.ctrl_l or key == pynput_keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif self.ctrl_pressed:
                if key == pynput_keyboard.Key.space:
                    self.app.toggle_play_pause()
                elif key == pynput_keyboard.Key.right:
                    self.app.play_next()
                elif key == pynput_keyboard.Key.left:
                    self.app.play_previous()
                elif key == pynput_keyboard.KeyCode.from_char('s'):
                    self.app.stop()
                elif key == pynput_keyboard.KeyCode.from_char('l'):
                    self.app.toggle_loop_mode()
                elif key == pynput_keyboard.KeyCode.from_char('r'):
                    self.app.toggle_random_mode()
                elif key == pynput_keyboard.KeyCode.from_char('t'):
                    self.app.toggle_order_mode()
                elif key == pynput_keyboard.Key.up:
                    vol = min(self.app.player.audio_get_volume() + 10, 100)
                    self.app.player.audio_set_volume(vol)
                elif key == pynput_keyboard.Key.down:
                    vol = max(self.app.player.audio_get_volume() - 10, 0)
                    self.app.player.audio_set_volume(vol)
        except AttributeError:
            pass

    def on_release(self, key):
        if key == pynput_keyboard.Key.ctrl_l or key == pynput_keyboard.Key.ctrl_r:
            self.ctrl_pressed = False

    def start(self):
        listener = pynput_keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()


if __name__ == "__main__":
    try:
        run_matrix_effect()
    except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error: {e}")
    except Exception as e:
        print(f"Error ejecutando matrix_effect.exe: {e}")
    finally:
        root = tk.Tk()
        app = MP3Player(root)
        hotkey_listener = HotkeyListener(app)
        threading.Thread(target=hotkey_listener.start, daemon=True).start()
        root.mainloop()
