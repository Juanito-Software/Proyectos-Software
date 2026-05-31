import configparser
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw
import os
import ctypes
import win32con
import win32gui
import winreg
from pathlib import Path
import threading
import time
import subprocess
import sys
from ultralytics import YOLO
import mss
from FloatTrans.src.main import setup_window, read_config 
from torchaudio.models.wav2vec2 import wav2vec2_base
from progress_bar_utils import show_fancy_progress_bar
import cv2
import numpy as np
import keyboard
from PIL import Image, ImageDraw, ImageFont
import dxcam 

def run_matrix_effect():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(base_path, "matrix_effect.exe")
    subprocess.run([exe_path], check=True)

def aceleracion_activada():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse") as key:
            speed, _ = winreg.QueryValueEx(key, "MouseSpeed")
            th1, _ = winreg.QueryValueEx(key, "MouseThreshold1")
            th2, _ = winreg.QueryValueEx(key, "MouseThreshold2")
            return speed == "1" and th1 == "6" and th2 == "10"
    except:
        return False

def activar_aceleracion():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "1")
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "6")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "10")
    except Exception as e:
        print("Error activando aceleración:", e)

def desactivar_aceleracion():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
    except Exception as e:
        print("Error desactivando aceleración:", e)

# Paths y constantes
if hasattr(sys, '_MEIPASS'):
    crosshair_folder = Path(sys._MEIPASS) / "crosshairs"
else:
    crosshair_folder = Path(__file__).parent / "crosshairs"
crosshair_images = [f for f in os.listdir(crosshair_folder) if f.endswith(".png")]

SPI_SETMOUSESPEED = 0x0071
NIGHT_BG = "#000000"  # negro
NIGHT_FG = "#00FF00"  # verde lima

class CrosshairOverlay(tk.Toplevel):
    def __init__(self, image_path, scale=1.0, alpha=1.0):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.attributes("-alpha", alpha)
        self.original_img = Image.open(image_path)
        self.scale = scale
        self.label = tk.Label(self, bg="black")
        self.label.pack()
        self._render()
        self.center()
        self.after(100, self._make_clickthrough)

    def _render(self):
        w, h = self.original_img.size
        nw, nh = int(w*self.scale), int(h*self.scale)
        img = self.original_img.resize((nw, nh), Image.Resampling.LANCZOS).convert("RGBA")
        self.tk_img = ImageTk.PhotoImage(img)
        self.label.config(image=self.tk_img)
        self.center()

    def center(self):
        w, h = self.tk_img.width(), self.tk_img.height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw-w)//2, (sh-h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def update_scale(self, scale):
        self.scale = scale
        self._render()

    def set_alpha(self, alpha):
        self.attributes("-alpha", alpha)

    def change_image(self, path):
        self.original_img = Image.open(path)
        self._render()

    def _make_clickthrough(self):
        hwnd = ctypes.windll.user32.FindWindowW(None, self.title())
        if hwnd:
            ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   ex | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
            win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 255, win32con.LWA_COLORKEY)

class MotionOverlay(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.canvas = tk.Label(self, bg="black")
        self.canvas.pack()
        self.geometry("+0+0")

    def update_image(self, img):
        self.tk_img = ImageTk.PhotoImage(image=img)
        self.canvas.config(image=self.tk_img)

    def move_and_resize(self, w, h):
        self.geometry(f"{w}x{h}+0+0")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("MultifuncionFPS")
        self.motion_thread_running = False
        self.motion_overlay = None
        self.overlay = None

        # Configuración inicial
        root.configure(bg=NIGHT_BG)
        fuente_grande = tkFont.Font(family="TkDefaultFont", size=12)

        # Leer configuración
        cfg = read_config()
        alpha = float(cfg.get("transparency", 1.0))
        hotkey = cfg.get("hotkey", None)

        img_cfg = cfg.get("image_path", "")
        if os.path.exists(img_cfg):
            path = img_cfg
        else:
            if not crosshair_images:
                raise RuntimeError("No crosshairs found")
            path = str(crosshair_folder / crosshair_images[0])
        print("Usando:", path)
        self.current_crosshair = path
        self.ft_win = setup_window(self.root, path, alpha, hotkey)
        self.ft_win.withdraw()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCheckbutton", background=NIGHT_BG, foreground=NIGHT_FG)
        style.configure("TButton", background=NIGHT_BG, foreground=NIGHT_FG)
        style.configure("TLabel", background=NIGHT_BG, foreground=NIGHT_FG)
        style.configure("TScale", background=NIGHT_BG, troughcolor="#333333", sliderthickness=15)

        self.float_overlay_proc = None

        # Variables y widgets para *Mira*
        self.crosshair_index = 0
        self.crosshair_scale = tk.DoubleVar(value=0.2)
        self.crosshair_alpha = tk.DoubleVar(value=alpha)
        self.toggle_var = tk.BooleanVar()

        ttk.Label(root, text="-------- MIRA ⊕ --------", font=fuente_grande) \
            .grid(row=0, column=0, pady=5)

        self.crosshair_toggle = ttk.Checkbutton(root, text="Mostrar mira",
                                               variable=self.toggle_var,
                                               command=self.toggle_crosshair)
        self.crosshair_toggle.grid(row=1, column=0, padx=5, pady=10)

        self.next_btn = ttk.Button(root, text="Siguiente mira",
                                   command=self.next_crosshair)
        self.next_btn.grid(row=1, column=1, padx=5, pady=10)

        ttk.Label(root, text="Tamaño de mira:") \
            .grid(row=2, column=0, sticky="e")
        self.scale_slider = ttk.Scale(root, from_=0.1, to=2.0, value=self.crosshair_scale.get(),
                                      orient="horizontal", variable=self.crosshair_scale,
                                      command=self.update_crosshair_scale_final)
        self.scale_slider.grid(row=2, column=1, padx=5, pady=10)

        ttk.Label(root, text="Transparencia de la mira:") \
            .grid(row=3, column=0, sticky="e")
        self.alpha_slider = ttk.Scale(root, from_=0.1, to=1.0,
                                      variable=self.crosshair_alpha,
                                      command=self.update_overlay_alpha)
        self.alpha_slider.set(self.crosshair_alpha.get())
        self.alpha_slider.grid(row=3, column=1, padx=5, pady=10)

        # Widgets para *Ratón*
        ttk.Label(root, text="-------- RATÓN ⇧ --------", font=fuente_grande) \
            .grid(row=4, column=0, pady=5)

        self.acceleration_var = tk.BooleanVar(value=aceleracion_activada())
        self.acceleration_toggle = ttk.Checkbutton(root, text="Aceleración del ratón",
                                                  variable=self.acceleration_var,
                                                  command=self.toggle_acceleration)
        self.acceleration_toggle.grid(row=5, column=0, padx=20, pady=10)

        ttk.Label(root, text="Sensibilidad del ratón:") \
            .grid(row=5, column=1, sticky="e", padx=5)
        self.sens_slider = ttk.Scale(root, from_=0.1, to=5.0, value=1.0,
                                    orient="horizontal", command=self.update_sensitivity)
        self.sens_slider.grid(row=6, column=1, padx=10, pady=10)

        # Widgets para *Detección de Movimiento*
        ttk.Label(root, text="-------- AYUDAS 🙏 --------", font=fuente_grande) \
            .grid(row=7, column=0, pady=10)
        # Detección de Movimiento CS2
        self.motion_cs2_var = tk.BooleanVar(value=False)
        self.motion_toggle_cs2 = ttk.Checkbutton(
            root, text="Detectar movimiento (CS2)",
            variable=self.motion_cs2_var,
            command=self.toggle_motion_CS2
        )
        self.motion_toggle_cs2.grid(row=8, column=0, padx=20, pady=10)

        # Detección de Movimiento Personas
        self.motion_people_var = tk.BooleanVar(value=False)
        self.motion_toggle_people = ttk.Checkbutton(
            root, text="Detectar movimiento (Personas)",
            variable=self.motion_people_var,
            command=self.toggle_motion_people
        )
        self.motion_toggle_people.grid(row=9, column=0, padx=20, pady=10)


    def update_overlay_alpha(self, event=None):
        nuevo_alpha = self.crosshair_alpha.get()
        if self.overlay:
            self.overlay.set_alpha(nuevo_alpha)
        elif self.float_overlay_proc:
            self.close_floattrans()
            self.launch_floattrans()

    def launch_floattrans(self):
        self.close_floattrans()
        config_path = Path(__file__).parent / "FloatTrans" / "config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)
        if "General" not in config:
            config["General"] = {}
        config["General"]["transparency"] = str(self.crosshair_alpha.get())
        with open(config_path, "w") as configfile:
            config.write(configfile)
        exe_path = Path(__file__).parent / "FloatTrans" / "FloatTrans.exe"
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", str(exe_path), None, None, 1)
        except Exception as e:
            print(f"No se pudo lanzar FloatTrans.exe con elevación: {e}")

    def close_floattrans(self):
        if self.float_overlay_proc:
            self.float_overlay_proc.terminate()
            self.float_overlay_proc = None

    def toggle_crosshair(self):
        if self.toggle_var.get():
            try:
                if self.overlay:
                    self.overlay.destroy()
                scale_value = self.crosshair_scale.get()
                self.overlay = CrosshairOverlay(self.current_crosshair, scale=scale_value,
                                               alpha=self.crosshair_alpha.get())
            except Exception as e:
                print("Error al mostrar el crosshair:", e)
        else:
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None
            self.close_floattrans()

    def next_crosshair(self):
        self.crosshair_index = (self.crosshair_index + 1) % len(crosshair_images)
        self.current_crosshair = os.path.join(crosshair_folder,
                                              crosshair_images[self.crosshair_index])
        if self.overlay:
            self.overlay.change_image(self.current_crosshair)

    def update_crosshair_scale_final(self, event=None):
        if self.overlay:
            self.overlay.update_scale(self.crosshair_scale.get())

    def toggle_acceleration(self):
        if self.acceleration_var.get():
            activar_aceleracion()
        else:
            desactivar_aceleracion()

    def update_sensitivity(self, val):
        sensitivity = float(val)
        min_slider = 0.1
        max_slider = 5.0
        speed = int(((sensitivity - min_slider) / (max_slider - min_slider)) * (20 - 1) + 1)
        speed = max(1, min(speed, 20))
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)
        print(f"Sensibilidad ajustada en el sistema a: {speed}/20 (desde {sensitivity})")

    def toggle_motion_CS2(self):
        if self.motion_cs2_var.get():
            if not self.motion_thread_running:
                self.motion_overlay = MotionOverlay()
                self.motion_thread_running = True
                self.motion_thread = threading.Thread(target=self.run_motion_detection_CS2, daemon=True)
                self.motion_thread.start()
        else:
            self.stop_motion_thread()

    def toggle_motion_people(self):
        if self.motion_people_var.get():
            if not self.motion_thread_running:
                self.motion_overlay = MotionOverlay()
                self.motion_thread_running = True
                self.motion_thread = threading.Thread(target=self.run_motion_detection_people, daemon=True)
                self.motion_thread.start()
        else:
            self.stop_motion_thread()


    def stop_motion_thread(self):
        self.motion_thread_running = False
        if hasattr(self, 'motion_thread') and self.motion_thread.is_alive():
            self.motion_thread.join()
        cv2.destroyAllWindows()

    def on_closing(self):
        self.stop_motion_thread()
        if self.motion_overlay:
            # Limpieza extra de seguridad
            clean_img = Image.new("RGBA", (self.motion_overlay.winfo_width(), self.motion_overlay.winfo_height()), (0, 0, 0, 0))
            self.motion_overlay.update_image(clean_img)
            self.motion_overlay.destroy()
        self.root.destroy()

    # Atajos de teclado
    def toggle_motion_from_hotkey(self):
        self.motion_cs2_var.set(not self.motion_cs2_var.get())
        self.toggle_motion_CS2()

    def toggle_crosshair_from_hotkey(self):
        self.toggle_var.set(not self.toggle_var.get())
        self.toggle_crosshair()

    def next_crosshair_from_hotkey(self):
        self.next_crosshair()

    def run_motion_detection_CS2(self):
    # Cargar modelo YOLO
        model = YOLO("yolov8s.pt")
        #model = YOLO("runs/detect/train/weights/best.pt")
        model.to('cuda')  # usar GPU si está disponible

        # Fuente para overlay
        font = ImageFont.load_default()

        # Iniciamos cámara de pantalla
        camera = dxcam.create(output_idx=0)  # pantalla principal
        camera.start(target_fps=30)

        def detection_loop(): 
            num_detections = 0

            # Obtenemos un frame inicial para calcular dimensiones
            frame_bgr = None
            while frame_bgr is None:
                frame_bgr = camera.get_latest_frame()
                time.sleep(0.01)

            screen_height, screen_width, _ = frame_bgr.shape

            # Si hay overlay, lo ajustamos al tamaño de pantalla
            if self.motion_overlay:
                self.motion_overlay.move_and_resize(screen_width, screen_height)

            while self.motion_thread_running:
                frame_bgr = camera.get_latest_frame()
                if frame_bgr is None:
                    continue

                # Ajuste dinámico del threshold según número de detecciones
                if num_detections <= 3:
                    conf_threshold = 0.3
                elif 3 < num_detections <= 6:
                    conf_threshold = 0.4
                else:
                    conf_threshold = 0.5

                # Inferencia
                results = model(frame_bgr, classes=[0, 1, 2], conf=conf_threshold, iou=0.5)

                # Contar detecciones para la próxima iteración
                num_detections = sum(len(result.boxes) for result in results)

                # Imagen transparente para overlay
                h, w, _ = frame_bgr.shape
                overlay_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay_img)

                # Mapeo de clases
                class_info = {
                    0: {"label": "Antiterrorista", "color": (0, 0, 255)},
                    1: {"label": "Cabeza", "color": (255, 0, 0)},
                    2: {"label": "Terrorista", "color": (0, 255, 0)},
                }

                # Dibujar cajas
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())

                        info = class_info.get(cls_id, {"label": "Unknown", "color": (255, 255, 255)})
                        label = f"{info['label']} {conf:.2f}"
                        color = info['color'] + (200,)

                        # Rectángulo
                        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

                        # Texto
                        bbox = draw.textbbox((0, 0), label, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        draw.rectangle([x1, y1 - text_height - 2, x1 + text_width, y1], fill=color)
                        draw.text((x1, y1 - text_height - 2), label, fill=(255, 255, 255, 255), font=font)

                # Actualizar overlay
                if self.motion_overlay:
                    try:
                        self.motion_overlay.update_image(overlay_img)
                    except Exception as e:
                        print(f"Error actualizando overlay: {e}")

                time.sleep(0.03)

            # 🔹 Cuando se detiene el bucle → limpiar overlay
            if self.motion_overlay:
                clean_img = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
                self.motion_overlay.update_image(clean_img)

            camera.stop()

        # Iniciar hilo de detección
        thread = threading.Thread(target=detection_loop, daemon=True)
        thread.start()


    def run_motion_detection_people(self):
        # YOLOv8 estándar para personas
        model = YOLO("yolov8s.pt")  # Modelo general
        model.to('cuda')
        font = ImageFont.load_default()
        camera = dxcam.create(output_idx=0)
        camera.start(target_fps=30)

        def detection_loop():
            num_detections = 0
            frame_bgr = None
            while frame_bgr is None:
                frame_bgr = camera.get_latest_frame()
                time.sleep(0.01)

            screen_height, screen_width, _ = frame_bgr.shape
            if self.motion_overlay:
                self.motion_overlay.move_and_resize(screen_width, screen_height)

            while self.motion_thread_running:
                frame_bgr = camera.get_latest_frame()
                if frame_bgr is None:
                    continue

                # Threshold dinámico
                if num_detections <= 3:
                    conf_threshold = 0.3
                elif 3 < num_detections <= 6:
                    conf_threshold = 0.4
                else:
                    conf_threshold = 0.5

                results = model(frame_bgr, classes=[0], conf=conf_threshold, iou=0.5)  # class 0 = persona
                num_detections = sum(len(r.boxes) for r in results)

                overlay_img = Image.new("RGBA", (screen_width, screen_height), (0,0,0,0))
                draw = ImageDraw.Draw(overlay_img)

                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        color = (0,255,0,200)  # verde con transparencia
                        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
                        label = f"Persona {float(box.conf[0].item()):.2f}"
                        bbox = draw.textbbox((0,0), label, font=font)
                        draw.rectangle([x1, y1-bbox[3], x1+bbox[2], y1], fill=color)
                        draw.text((x1, y1-bbox[3]), label, fill=(255,255,255,255), font=font)

                if self.motion_overlay:
                    try:
                        self.motion_overlay.update_image(overlay_img)
                    except Exception as e:
                        print(f"Error actualizando overlay: {e}")

                time.sleep(0.03)

            if self.motion_overlay:
                clean_img = Image.new("RGBA", (screen_width, screen_height), (0,0,0,0))
                self.motion_overlay.update_image(clean_img)
            camera.stop()

        threading.Thread(target=detection_loop, daemon=True).start()
        

if __name__ == "__main__":
    try:
        run_matrix_effect()
        for i in range(101):
            show_fancy_progress_bar(i, 100)
            time.sleep(0.01)
    except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
    except Exception as e:
        print(f"Error inesperado ejecutando matrix_effect.exe: {e}")

    root = tk.Tk()
    app = App(root)

    def global_hotkeys(app):
        keyboard.add_hotkey("ctrl+i", lambda: app.toggle_motion_from_hotkey())
        keyboard.add_hotkey("ctrl+o", lambda: app.toggle_crosshair_from_hotkey())
        keyboard.add_hotkey("ctrl+p", lambda: app.next_crosshair_from_hotkey())

    threading.Thread(target=lambda: global_hotkeys(app), daemon=True).start()
    root.mainloop()
