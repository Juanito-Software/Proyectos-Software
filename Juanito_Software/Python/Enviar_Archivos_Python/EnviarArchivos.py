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
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import threading
import socket
import hashlib
import random
import string
import json
import os
import subprocess
import sys
import re

# Configuración global
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 30  # segundos para conexión y operaciones


def copiar_al_portapapeles(texto):
    """Copia texto al portapapeles (multi-plataforma)."""
    try:
        root = tk._default_root
        if root:
            root.clipboard_clear()
            root.clipboard_append(texto)
            root.update()
            return True
    except Exception:
        pass
    return False


def es_ip_valida(ip):
    """Comprueba si una cadena es una IPv4 válida."""
    if not ip or not ip.strip():
        return False
    patron = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
    m = re.match(patron, ip.strip())
    if not m:
        return False
    return all(0 <= int(g) <= 255 for g in m.groups())

def run_matrix_effect():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__) )
    exe_path = os.path.join(base_path, "matrix_effect.exe")
    try:
        subprocess.run([exe_path], check=True)
    except Exception as e:
        print(f"Error ejecutando matrix_effect.exe: {e}")


def intercalar_nombre(nombre):
    """
    Toma el nombre del usuario e intercale 5 caracteres aleatorios después de cada letra.
    """
    resultado = ""
    for letra in nombre:
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        resultado += letra + random_chars
    return resultado

def get_local_ip():
        """
        Intenta obtener la IP local del equipo de forma más robusta.
        Si falla, retorna '127.0.0.1'.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Conectar a un servidor externo; no se envían datos, solo se usa para obtener la IP local
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip


class FileTransferApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Transferencia de Archivos - Versión TCP")
        self.hash_direccion = None
        self.selected_file = None
        self.progress_bar = None
        self.label_estado = None
        self.label_archivo_info = None
        self.servidor_ok = None  # True si el servidor arrancó correctamente

        self.frame_inicio = tk.Frame(master)
        self.frame_inicio.pack(padx=20, pady=20)

        tk.Label(self.frame_inicio, text="Introduce tu nombre:").pack(pady=5)
        self.entry_nombre = tk.Entry(self.frame_inicio, width=30)
        self.entry_nombre.pack(pady=5)

        self.btn_continuar = tk.Button(self.frame_inicio, text="Continuar", command=self.procesar_nombre)
        self.btn_continuar.pack(pady=10)

        self.frame_principal = tk.Frame(master)

        threading.Thread(target=self.start_server, daemon=True).start()

    def procesar_nombre(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Debes introducir un nombre")
            return
        
        # Genera la dirección (hash) propia a partir del nombre
        nombre_intercalado = intercalar_nombre(nombre)
        self.hash_direccion = hashlib.sha256(nombre_intercalado.encode()).hexdigest()
        
        # Actualiza la interfaz para mostrar el panel principal
        self.frame_inicio.pack_forget()
        self.mostrar_panel_principal()

    def mostrar_panel_principal(self):
        ip_local = get_local_ip()

        # --- Dirección (hash) con botón copiar ---
        tk.Label(self.frame_principal, text="Tu dirección para recibir archivos:",
                 font=("Helvetica", 10, "bold")).pack(pady=5)
        f_hash = tk.Frame(self.frame_principal)
        f_hash.pack(pady=(0, 5))
        self.entry_hash_local = ttk.Entry(f_hash, width=60, state="readonly")
        self.entry_hash_local.pack(side=tk.LEFT, padx=(0, 5))
        self.entry_hash_local.configure(state="normal")
        self.entry_hash_local.delete(0, tk.END)
        self.entry_hash_local.insert(0, self.hash_direccion)
        self.entry_hash_local.configure(state="readonly")
        btn_copiar_hash = tk.Button(f_hash, text="Copiar", command=lambda: self._copiar_y_avisar(self.hash_direccion, "Dirección"))
        btn_copiar_hash.pack(side=tk.LEFT)

        # --- IP local con botón copiar ---
        tk.Label(self.frame_principal, text="Tu IP para recibir archivos:",
                 font=("Helvetica", 10, "bold"), fg="blue").pack(pady=5)
        f_ip = tk.Frame(self.frame_principal)
        f_ip.pack(pady=(0, 10))
        self.entry_ip_local = ttk.Entry(f_ip, width=25, state="readonly")
        self.entry_ip_local.pack(side=tk.LEFT, padx=(0, 5))
        self.entry_ip_local.configure(state="normal")
        self.entry_ip_local.delete(0, tk.END)
        self.entry_ip_local.insert(0, ip_local)
        self.entry_ip_local.configure(state="readonly")
        btn_copiar_ip = tk.Button(f_ip, text="Copiar", command=lambda: self._copiar_y_avisar(ip_local, "IP"))
        btn_copiar_ip.pack(side=tk.LEFT)

        # --- Estado y progreso ---
        self.label_estado = tk.Label(self.frame_principal, text="Listo", fg="green")
        self.label_estado.pack(pady=2)
        self.progress_bar = ttk.Progressbar(self.frame_principal, length=320, mode="determinate")
        self.progress_bar.pack(pady=2)
        self.label_archivo_info = tk.Label(self.frame_principal, text="Ningún archivo seleccionado", fg="gray")
        self.label_archivo_info.pack(pady=2)

        # --- Selección de archivo ---
        self.btn_seleccionar = tk.Button(self.frame_principal, text="Seleccionar archivo", command=self.seleccionar_archivo)
        self.btn_seleccionar.pack(pady=5)

        tk.Label(self.frame_principal, text="IP del destinatario:").pack(pady=5)
        self.entry_direccion_envio = tk.Entry(self.frame_principal, width=40)
        self.entry_direccion_envio.pack(pady=5)

        tk.Label(self.frame_principal, text="Hash (dirección) del destinatario:").pack(pady=5)
        self.entry_hash_destino = tk.Entry(self.frame_principal, width=70)
        self.entry_hash_destino.pack(pady=5)

        self.btn_enviar = tk.Button(self.frame_principal, text="Enviar", command=self.enviar_archivo)
        self.btn_enviar.pack(pady=10)

        self.frame_principal.pack(padx=20, pady=20)

    def _copiar_y_avisar(self, texto, nombre_campo):
        if copiar_al_portapapeles(texto):
            messagebox.showinfo("Copiado", f"{nombre_campo} copiado al portapapeles.")
        else:
            messagebox.showwarning("Copiar", "No se pudo copiar al portapapeles.")

    def _actualizar_estado(self, texto, color="green"):
        if self.label_estado:
            self.label_estado.config(text=texto, fg=color)

    def _actualizar_progreso(self, valor):
        if self.progress_bar is not None:
            self.progress_bar["value"] = valor
            self.master.update_idletasks()

    def _formatear_tamaño(self, bytes_size):
        for u in ("B", "KB", "MB", "GB"):
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {u}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"

    def seleccionar_archivo(self):
        file_path = filedialog.askopenfilename(title="Selecciona un archivo para enviar")
        if file_path:
            self.selected_file = file_path
            nombre = os.path.basename(file_path)
            tam = os.path.getsize(file_path)
            if self.label_archivo_info:
                self.label_archivo_info.config(
                    text=f"Archivo: {nombre} ({self._formatear_tamaño(tam)})",
                    fg="black"
                )
            messagebox.showinfo("Archivo seleccionado", f"Archivo seleccionado:\n{file_path}")

    def enviar_archivo(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Debes seleccionar un archivo")
            return
        direccion = self.entry_direccion_envio.get().strip()
        if not direccion:
            messagebox.showerror("Error", "Debes introducir la IP del destinatario")
            return
        if not es_ip_valida(direccion):
            messagebox.showerror("Error", "La IP del destinatario no es válida.")
            return
        dest_hash = self.entry_hash_destino.get().strip()
        if not dest_hash:
            messagebox.showerror("Error", "Debes introducir el hash (dirección) del destinatario")
            return

        self.btn_enviar.config(state=tk.DISABLED)
        threading.Thread(target=self.procesar_envio, args=(direccion, dest_hash), daemon=True).start()

    def _habilitar_envio(self):
        if self.btn_enviar:
            self.btn_enviar.config(state=tk.NORMAL)
        self._actualizar_estado("Listo", "green")
        self._actualizar_progreso(0)

    def procesar_envio(self, direccion, dest_hash):
        try:
            self.master.after(0, lambda: self._actualizar_estado("Conectando...", "orange"))
            self.master.after(0, lambda: self._actualizar_progreso(0))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(SOCKET_TIMEOUT)
                s.connect((direccion, SERVER_PORT))

                file_size = os.path.getsize(self.selected_file)
                file_name = os.path.basename(self.selected_file)
                header = {
                    "dest_hash": dest_hash,
                    "filename": file_name,
                    "filesize": file_size
                }
                header_json = json.dumps(header)
                header_bytes = header_json.encode()
                header_length = len(header_bytes)

                s.sendall(header_length.to_bytes(4, byteorder="big"))
                s.sendall(header_bytes)

                self.master.after(0, lambda: self._actualizar_estado("Enviando...", "blue"))
                enviados = 0
                with open(self.selected_file, "rb") as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        s.sendall(bytes_read)
                        enviados += len(bytes_read)
                        pct = min(100, int(100 * enviados / file_size))
                        self.master.after(0, lambda v=pct: self._actualizar_progreso(v))

                self.master.after(0, lambda: self._actualizar_progreso(100))
                self.master.after(0, lambda: messagebox.showinfo("Éxito", f"Archivo '{file_name}' enviado correctamente"))
        except Exception as e:
            self.master.after(0, lambda err=str(e): messagebox.showerror("Error al enviar", err))
        finally:
            self.master.after(0, self._habilitar_envio)

    def start_server(self):
        if not os.path.exists("received_files"):
            os.makedirs("received_files")
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Enlace a "" (todas las interfaces) de forma deliberada: la funcion
            # de este programa es recibir ficheros de otro equipo de la red
            # local, asi que restringirlo a 127.0.0.1 lo dejaria inservible.
            # A diferencia del servidor FTP de este mismo repositorio, aqui si
            # hay una comprobacion de destinatario: handle_client rechaza todo
            # lo que no traiga el dest_hash correcto.
            server_socket.bind(("", SERVER_PORT))
            server_socket.listen(5)
            self.servidor_ok = True
            print(f"[Servidor] Escuchando en el puerto {SERVER_PORT}...")
            while True:
                conn, addr = server_socket.accept()
                print(f"[Servidor] Conexión desde {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except OSError as e:
            self.servidor_ok = False
            if e.errno == 10048 or "Address already in use" in str(e):
                self.master.after(0, lambda: messagebox.showerror(
                    "Puerto en uso",
                    f"El puerto {SERVER_PORT} está en uso. Cierra otras instancias o cambia SERVER_PORT."
                ))
            else:
                self.master.after(0, lambda: messagebox.showerror("Servidor", str(e)))
        except Exception as e:
            self.servidor_ok = False
            self.master.after(0, lambda: messagebox.showerror("Servidor", str(e)))

    def handle_client(self, conn, addr):
        try:
            conn.settimeout(SOCKET_TIMEOUT)
            raw_header_len = self.recvall(conn, 4)
            if not raw_header_len:
                return
            header_len = int.from_bytes(raw_header_len, byteorder="big")
            header_bytes = self.recvall(conn, header_len)
            header = json.loads(header_bytes.decode())

            if header.get("dest_hash") != self.hash_direccion:
                print("[Servidor] Hash no coincide. Rechazando archivo.")
                conn.close()
                return

            # El nombre del fichero lo elige quien envia, asi que es una entrada
            # no fiable. Sin sanear, un emisor podria mandar "../../algo.txt" y
            # escribir fuera de received_files: es path traversal.
            #
            # basename se queda solo con el ultimo componente y descarta
            # cualquier ruta o "..". La comprobacion posterior con os.path.abspath
            # es el cinturon de seguridad: verifica que la ruta final resuelta
            # cuelga realmente del directorio de destino.
            filename = os.path.basename(header.get("filename", "archivo_recibido"))
            if not filename or filename in (".", ".."):
                filename = "archivo_recibido"

            filesize = header.get("filesize", 0)

            carpeta_destino = os.path.abspath("received_files")
            save_path = os.path.abspath(os.path.join(carpeta_destino, filename))
            if os.path.commonpath([carpeta_destino, save_path]) != carpeta_destino:
                print("[Servidor] Nombre de archivo no permitido. Rechazando.")
                conn.close()
                return

            def actualizar_ui_recibir(pct, estado_texto):
                if self.progress_bar is not None and self.label_estado is not None:
                    self.progress_bar["value"] = pct
                    self.label_estado.config(text=estado_texto, fg="blue")
                    self.master.update_idletasks()

            self.master.after(0, lambda: actualizar_ui_recibir(0, "Recibiendo..."))
            with open(save_path, "wb") as f:
                bytes_received = 0
                while bytes_received < filesize:
                    chunk = conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_received += len(chunk)
                    pct = min(100, int(100 * bytes_received / filesize)) if filesize else 0
                    self.master.after(0, lambda v=pct: actualizar_ui_recibir(v, "Recibiendo..."))
            self.master.after(0, lambda: actualizar_ui_recibir(100, "Listo"))
            self.master.after(0, lambda: self._actualizar_estado("Listo", "green"))
            self.master.after(0, lambda: self._actualizar_progreso(0))
            print(f"[Servidor] Archivo recibido: {save_path}")
            self.master.after(0, lambda: messagebox.showinfo("Archivo recibido", f"Se ha recibido el archivo:\n{filename}"))
        except Exception as e:
            print(f"[Servidor] Error al recibir archivo: {e}")
            self.master.after(0, lambda: self._actualizar_estado("Listo", "green"))
            self.master.after(0, lambda: self._actualizar_progreso(0))
        finally:
            conn.close()

    def recvall(self, sock, n):
        """
        Función auxiliar para recibir n bytes o hasta que se complete la transmisión.
        """
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

if __name__ == "__main__":
    try:
        run_matrix_effect()
    except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X o con space): {e}")
    except Exception as e:
        print(f"Error inesperado ejecutando matrix_effect.exe: {e}")
    finally:
        try:
            root = tk.Tk()
            root.withdraw()  # Oculta la ventana principal por seguridad inicial
            app = FileTransferApp(root)
            root.deiconify()  # Ahora la muestra
            root.mainloop()
        except tk.TclError as tcl_err:
             print(f"No se pudo inicializar la interfaz gráfica de tkinter: {tcl_err}")