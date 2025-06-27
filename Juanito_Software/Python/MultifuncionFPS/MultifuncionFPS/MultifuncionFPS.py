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
import cv2
import numpy as np
import mss
from FloatTrans.src.main import setup_window, read_config



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

# ---------------------------------------------------------
# Helpers de aceleración del ratón
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Paths y constantes
# ---------------------------------------------------------

# Ruta relativa al script actual
crosshair_folder = Path(__file__).parent / "crosshairs"
crosshair_images = [f for f in os.listdir(crosshair_folder) if f.endswith(".png")]# Cargar imágenes de crosshair

SPI_SETMOUSESPEED = 0x0071
SPI_GETMOUSESPEED = 0x0070

NIGHT_BG = "#000000"  # negro
NIGHT_FG = "#00FF00"  # verde lima (estilo consola)

# ---------------------------------------------------------
# Overlay de la mira
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Overlay de detección de movimiento (queda igual)
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Aplicación principal
# ---------------------------------------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("MultifuncionFPS")
        self.root.configure(bg=NIGHT_BG)
        fuente_grande = tkFont.Font(family="TkDefaultFont", size=12)

         # Leemos config y preparamos   con wrapper
        cfg = read_config()
        alpha = float(cfg.get("transparency", 1.0)) 
        hotkey = cfg.get("hotkey", None)

        # Selección de imagen
        img_cfg = cfg.get("image_path", "")
        if os.path.exists(img_cfg):
            path = img_cfg
        else:
            if not crosshair_images:
                raise RuntimeError("No crosshairs found")
            path = str(crosshair_folder / crosshair_images[0])
        print("Usando:", path)

        # Configuramos FloatTrans (se inicia oculto)
        self.ft_win = setup_window(self.root, path, alpha, hotkey)
        self.ft_win.withdraw()

    
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCheckbutton", background=NIGHT_BG, foreground=NIGHT_FG)
        style.configure("TButton", background=NIGHT_BG, foreground=NIGHT_FG)
        style.configure("TLabel", background=NIGHT_BG, foreground=NIGHT_FG)
        style.configure("TScale", background=NIGHT_BG, troughcolor="#333333", sliderthickness=15)
        
        self.float_overlay_proc = None  # Para el proceso del exe

        # Deteccion movimiento
        self.motion_var_Static = tk.BooleanVar()

        # Deteccion movimiento
        self.motion_var = tk.BooleanVar()

        ttk.Label(root, text="------- AYUDAS 🙏 --------", font=fuente_grande).grid(row=6, column=0, pady=10)
        
        self.motion_toggle = ttk.Checkbutton(root, text="Detección Movimiento Estatica", variable=self.motion_var_Static, command=self.toggle_motion_static)
        self.motion_toggle.grid(row=7, column=0, padx=20, pady=10)

        self.motion_toggle = ttk.Checkbutton(root, text="Detección Movimiento", variable=self.motion_var, command=self.toggle_motion)
        self.motion_toggle.grid(row=7, column=1, padx=20, pady=10)

        self.motion_overlay = None
        self.motion_thread_running = False

        
        # Mira
        self.crosshair_index = 0
        self.crosshair_scale = tk.DoubleVar(value=0.2)
        self.crosshair_alpha = tk.DoubleVar(value=1.0)  # 1.0 = opaco, 0.1 = muy transparente
        self.toggle_var = tk.BooleanVar()
        
        ttk.Label(root, text="-------- MIRA ⊕ --------", font=fuente_grande).grid(row=0, column=0, pady=5)
        
        # Boton mostrar mira
        self.toggle = ttk.Checkbutton(root, text="Mostrar mira", variable=self.toggle_var, command=self.toggle_crosshair)
        self.toggle.grid(row=1, column=0, padx=5, pady=10)

        # Boton siguiente mira
        self.next_btn = ttk.Button(root, text="Siguiente mira", command=self.next_crosshair)
        self.next_btn.grid(row=1, column=1, padx=5, pady=10)

        # Slider tamaño de mira
        ttk.Label(root, text="Tamaño de mira:").grid(row=1, column=3)
        self.scale_slider = ttk.Scale(root, from_=0.1, to=2.0, value=0.2, orient="horizontal",
                                        variable=self.crosshair_scale, command=self.update_crosshair_scale_final)
        self.scale_slider.grid(row=2, column=3, padx=5, pady=(0,10))
        self.scale_slider.bind("<ButtonRelease-1>", self.update_crosshair_scale_final)

        # Slider trasparencia de mira
        self.crosshair_alpha = tk.DoubleVar(value=alpha)
        ttk.Label(root, text="Transparencia de la mira:").grid(row=1, column=4)
        self.alpha_slider = ttk.Scale(
            root, from_=0.1, to=1.0,
            variable=self.crosshair_alpha,
            command=self.update_overlay_alpha
        )
        self.alpha_slider.grid(row=2, column=4, padx=5, pady=(0,10))


        # Aceleración del ratón
        self.acceleration_var = tk.BooleanVar(value=aceleracion_activada())

        ttk.Label(root, text="-------- RATÓN ⇧ --------", font=fuente_grande).grid(row=3, column=0)

        self.acceleration_toggle = ttk.Checkbutton(root, text="Aceleración del ratón", variable=self.acceleration_var, command=self.toggle_acceleration)
        self.acceleration_toggle.grid(row=4, column=0, padx=20, pady=10)

        # sensibilidad del raton
        self.mouse_sensitivity = tk.DoubleVar(value=1.0)
        ttk.Label(root, text="Sensibilidad del ratón:").grid(row=4, column=1)
        self.sens_slider = ttk.Scale(root, from_=0.1, to=5.0, value=1.0, orient="horizontal", command=self.update_sensitivity)
        self.sens_slider.grid(row=5, column=1, padx=10, pady=10)

        self.current_crosshair = os.path.join(crosshair_folder, crosshair_images[self.crosshair_index])  

    def update_overlay_alpha(self, event=None):
        nuevo_alpha = self.crosshair_alpha.get()
        # Si estás usando la overlay propia de Tkinter
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.set_alpha(nuevo_alpha)
        # Si estás usando el proceso externo
        elif self.float_overlay_proc:
            self.close_floattrans()
            self.launch_floattrans()


    def launch_floattrans(self):
        # Asegúrate de cerrar si ya estaba corriendo
        self.close_floattrans()

        # Modifica el config.ini con el alpha actual
        config_path = r"C:\Users\User\Desktop\Proyectos\Juanito_Software\Python\MultifuncionFPS\MultifuncionFPS\FloatTrans\config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)
        if "General" not in config:
            config["General"] = {}
        config["General"]["transparency"] = str(self.crosshair_alpha.get())
        with open(config_path, "w") as configfile:
            config.write(configfile)

        # Lanza el EXE pidiendo elevación
        exe_path = r"C:\Users\User\Desktop\Proyectos\Juanito_Software\Python\MultifuncionFPS\MultifuncionFPS\FloatTrans\FloatTrans.exe"
        try:
            # 'runas' = pedir permisos de administrador
            ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, None, 1)
        except Exception as e:
            print(f"No se pudo lanzar FloatTrans.exe con elevación: {e}")

    def close_floattrans(self):
        if self.float_overlay_proc:
            self.float_overlay_proc.terminate()
            self.float_overlay_proc = None

    def toggle_acceleration(self):
        if self.acceleration_var.get():
            activar_aceleracion()
        else:
            desactivar_aceleracion()


    # funciones Deteccion movimiento
    def toggle_motion(self):
        if self.motion_var.get():
            if not self.motion_thread_running:
                self.motion_overlay = MotionOverlay()
                self.motion_thread_running = True 
                self.motion_thread = threading.Thread(target=self.run_motion_detection, daemon=True)
                self.motion_thread.start()
        else:
            self.stop_motion_thread()

    def toggle_motion_static(self):
        if self.motion_var_Static.get():
            if not self.motion_thread_running:
                self.motion_overlay = MotionOverlay()
                self.motion_thread_running = True 
                self.motion_thread = threading.Thread(target=self.run_motion_detection_static, daemon=True)
                self.motion_thread.start()
        else:
            self.stop_motion_thread()

    def run_motion_detection_static(self):    
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            w, h = monitor["width"], monitor["height"]
            self.motion_overlay.move_and_resize(w, h)

            prev_frame = None

            while self.motion_thread_running:
                # código de captura, detección, actualización del overlay
                sct_img = sct.grab(monitor)
                frame = np.array(sct_img)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if prev_frame is None:
                    prev_frame = gray
                    continue

                frame_delta = cv2.absdiff(prev_frame, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Crear imagen negra con fondo transparente
                overlay_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay_img)

                for c in contours:
                    if cv2.contourArea(c) < 500:
                        continue
                    (x, y, cw, ch) = cv2.boundingRect(c)
                    draw.rectangle([x, y, x + cw, y + ch], outline=(0, 255, 0, 255), width=2)

                if self.motion_overlay!=None:
                    try:
                        self.motion_overlay.update_image(overlay_img)
                    except Exception as e:
                        print(f"Error actualizando imagen del overlay desde el hilo: {e}")
                else:
                    print("motion_overlay es None, no se puede actualizar la imagen.")

                prev_frame = gray
                time.sleep(0.03)  # ~30 FPS
    
    def run_motion_detection(self):
        model = YOLO('yolov8s.pt')  # Usa el modelo mediano para mejor rendimiento
        model.to('cuda')  # Asegura que usa la GPU
        # Usar video
        """results = model.predict(source="video.mp4", conf=0.25, iou=0.4, stream=True)

        for r in results:
            # Aquí puedes visualizar o procesar cada frame
            boxes = r.boxes
            print(boxes.xyxy)"""
        
        # Usar fotogramas
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            w, h = monitor["width"], monitor["height"]
            self.motion_overlay.move_and_resize(w, h)

            while self.motion_thread_running:
                sct_img = sct.grab(monitor)
                frame = np.array(sct_img)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)

                # Detección con parámetros ajustados
                results = model.predict(
                    source=frame_rgb,
                    classes=[0],       # Solo personas
                    conf=0.25,         # Más sensible
                    iou=0.4,           # Evita solapamientos excesivos
                    verbose=False
                )

                # Dibuja los rectángulos
                draw = Image.fromarray(frame_rgb)
                overlay = Image.new("RGBA", draw.size, (0, 0, 0, 0))
                draw_overlay = ImageDraw.Draw(overlay)

                for r in results:
                    for box in r.boxes.xyxy.cpu().numpy():
                        x1, y1, x2, y2 = map(int, box)
                        draw_overlay.rectangle([x1, y1, x2, y2], outline="green", width=3)

                composed = Image.alpha_composite(draw.convert("RGBA"), overlay)
                self.motion_overlay.update_image(composed)


        
    # Funciones Mira
    def update_crosshair_scale_final(self, event=None):
        if self.overlay:
            self.overlay.update_scale(self.crosshair_scale.get())

    def update_crosshair_alpha(self, val=None):
        if self.overlay:
            self.overlay.update_alpha(float(val))

    def show_crosshair(self):
        try:
            # Cerrar overlay anterior
            if hasattr(self, 'overlay') and self.overlay:
                self.overlay.destroy()

            # Crear nuevo overlay
            scale_value = self.crosshair_scale.get()
            self.overlay = CrosshairOverlay(self.current_crosshair,
                                            scale=scale_value,
                                            alpha=self.crosshair_alpha.get())
        except Exception as e:
            print("Error al mostrar el crosshair:", e)

    def set_alpha(self, alpha):
        self.attributes("-alpha", alpha)

    def change_image(self, image_path):
        self.original_img = Image.open(image_path)
        self.update_scale(self.crosshair_scale.get())

    def toggle_crosshair(self):
        if self.toggle_var.get():
            self.show_crosshair()
            self.launch_floattrans()
        else:
            self.close_floattrans()

    def next_crosshair(self):
        self.crosshair_index = (self.crosshair_index + 1) % len(crosshair_images)
        self.current_crosshair = os.path.join(crosshair_folder, crosshair_images[self.crosshair_index])
        if self.overlay:
            self.overlay.destroy()
            self.overlay = CrosshairOverlay(self.current_crosshair, scale=self.crosshair_scale.get())


    # funciones sensibilidad del raton  
    def update_sensitivity(self, val):
        sensitivity = float(val)
        self.mouse_sensitivity.set(sensitivity)
        
        # Mapear 0.1–5.0 en el rango 1–20
        min_slider = 0.1
        max_slider = 5.0
        speed = int(((sensitivity - min_slider) / (max_slider - min_slider)) * (20 - 1) + 1)
        
        speed = max(1, min(speed, 20))
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)
        print(f"Sensibilidad ajustada en el sistema a: {speed}/20 (desde {sensitivity})")    
        
    
        
    # funciones cierre 
    """
    def stop_motion_thread(self):
        if self.motion_thread_running:
            self.motion_thread_running = False
            if self.motion_thread.is_alive():
                self.motion_thread.join(timeout=1)  # espera a que termine
            if self.motion_overlay:
                self.motion_overlay.destroy()
                self.motion_overlay = None


    def on_closing(self): 
        self.stop_motion_thread()
        if hasattr(self, 'motion_thread'):
            self.motion_thread.join(timeout=1)  # espera hasta 1 segundo
        if self.motion_overlay:
            self.motion_overlay.destroy()
        if self.overlay:
            self.overlay.destroy()
        self.root.destroy()
    """

    def stop_motion_thread(self):
        if getattr(self, 'motion_thread_running', False):
            self.motion_thread_running = False
            if hasattr(self, 'motion_thread') and self.motion_thread.is_alive():
                self.motion_thread.join(timeout=1)  # espera a que termine
        if hasattr(self, 'motion_overlay') and self.motion_overlay:
            self.motion_overlay.destroy()
            self.motion_overlay = None


    def on_closing(self):
        self.stop_motion_thread()

        # Cierra overlay si existe y no ha sido destruida ya
        if hasattr(self, 'overlay') and self.overlay:
            try:
                self.overlay.destroy()
            except tk.TclError:
                pass  # Ya está destruida

        # Finalmente cierra la ventana principal
        try:
            self.root.destroy()
        except tk.TclError:
            pass


    # funciones Toggle para atajos de teclado
    def toggle_motion_from_hotkey(self):
        # Alternar el valor de la variable y llamar al método
        self.motion_var.set(not self.motion_var.get())
        self.toggle_motion()

    def toggle_crosshair_from_hotkey(self):
        self.toggle_var.set(not self.toggle_var.get())
        self.toggle_crosshair()

    def next_crosshair_from_hotkey(self):
        self.next_crosshair()


# En el final del archivo
if __name__ == "__main__":
    import threading
    import keyboard
    import tkinter as tk

    try:
        run_matrix_effect()
    except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
    except Exception as e:
        print(f"Error inesperado ejecutando matrix_effect.exe: {e}")

    # Crear la ventana raíz antes de instanciar App
    root = tk.Tk()
    app = App(root)
    app_instance = app  # Necesario para el hilo de hotkeys

    # Definir hotkeys globales en hilo separado para no bloquear UI
    def global_hotkeys(app):
        keyboard.add_hotkey("ctrl+i", lambda: app.toggle_motion_from_hotkey())
        keyboard.add_hotkey("ctrl+o", lambda: app.toggle_crosshair_from_hotkey())
        keyboard.add_hotkey("ctrl+p", lambda: app.next_crosshair_from_hotkey())

    threading.Thread(target=lambda: global_hotkeys(app), daemon=True).start()

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
