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
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk  # Para usar Entry en modo readonly
import threading
import socket
import hashlib
import random
import string
import json
import os
import os
import subprocess
import sys

# Configuración global
SERVER_PORT = 5001  # Puerto para recibir archivos
BUFFER_SIZE = 4096  # Tamaño de bloque para enviar/recibir

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
        self.hash_direccion = None  # Aquí se almacenará el hash generado (del usuario local, receptor)
        self.selected_file = None   # Ruta del archivo seleccionado para enviar
        
        # Frame inicial: pedir nombre (para generar la propia "dirección")
        self.frame_inicio = tk.Frame(master)
        self.frame_inicio.pack(padx=20, pady=20)
        
        tk.Label(self.frame_inicio, text="Introduce tu nombre:").pack(pady=5)
        self.entry_nombre = tk.Entry(self.frame_inicio, width=30)
        self.entry_nombre.pack(pady=5)
        
        self.btn_continuar = tk.Button(self.frame_inicio, text="Continuar", command=self.procesar_nombre)
        self.btn_continuar.pack(pady=10)
        
        # Frame principal (se mostrará tras procesar el nombre)
        self.frame_principal = tk.Frame(master)
        
        # Inicia el servidor en un hilo para recibir archivos
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
        # Muestra la dirección (hash) del usuario (receptor) usando un Entry readonly
        tk.Label(self.frame_principal, text="Tu dirección para recibir archivos:", 
                 font=("Helvetica", 10, "bold")).pack(pady=5)
        self.entry_hash_local = ttk.Entry(self.frame_principal, width=70, state="readonly")
        self.entry_hash_local.pack(pady=5)
        self.entry_hash_local.configure(state="normal")
        self.entry_hash_local.delete(0, tk.END)
        self.entry_hash_local.insert(0, self.hash_direccion)
        self.entry_hash_local.configure(state="readonly")
        
        # Muestra la IP local del equipo usando un Entry readonly
        ip_local = get_local_ip()
        tk.Label(self.frame_principal, text="Tu IP para recibir archivos:", 
                 font=("Helvetica", 10, "bold"), fg="blue").pack(pady=5)
        self.entry_ip_local = ttk.Entry(self.frame_principal, width=40, state="readonly")
        self.entry_ip_local.pack(pady=5)
        self.entry_ip_local.configure(state="normal")
        self.entry_ip_local.delete(0, tk.END)
        self.entry_ip_local.insert(0, ip_local)
        self.entry_ip_local.configure(state="readonly")
        
        # Botón para seleccionar archivo a enviar
        self.btn_seleccionar = tk.Button(self.frame_principal, text="Seleccionar archivo", command=self.seleccionar_archivo)
        self.btn_seleccionar.pack(pady=5)
        
        # Campo para ingresar la IP del destinatario
        tk.Label(self.frame_principal, text="IP del destinatario:").pack(pady=5)
        self.entry_direccion_envio = tk.Entry(self.frame_principal, width=40)
        self.entry_direccion_envio.pack(pady=5)
        
        # Nuevo campo para ingresar el hash (dirección) del destinatario
        tk.Label(self.frame_principal, text="Hash (dirección) del destinatario:").pack(pady=5)
        self.entry_hash_destino = tk.Entry(self.frame_principal, width=70)
        self.entry_hash_destino.pack(pady=5)
        
        # Botón para enviar archivo
        self.btn_enviar = tk.Button(self.frame_principal, text="Enviar", command=self.enviar_archivo)
        self.btn_enviar.pack(pady=10)
        
        self.frame_principal.pack(padx=20, pady=20)

    

    def seleccionar_archivo(self):
        file_path = filedialog.askopenfilename(title="Selecciona un archivo para enviar")
        if file_path:
            self.selected_file = file_path
            messagebox.showinfo("Archivo seleccionado", f"Archivo seleccionado:\n{file_path}")

    def enviar_archivo(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Debes seleccionar un archivo")
            return
        direccion = self.entry_direccion_envio.get().strip()
        if not direccion:
            messagebox.showerror("Error", "Debes introducir la IP del destinatario")
            return
        dest_hash = self.entry_hash_destino.get().strip()
        if not dest_hash:
            messagebox.showerror("Error", "Debes introducir el hash (dirección) del destinatario")
            return

        threading.Thread(target=self.procesar_envio, args=(direccion, dest_hash), daemon=True).start()

    def procesar_envio(self, direccion, dest_hash):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((direccion, SERVER_PORT))
                
                file_size = os.path.getsize(self.selected_file)
                file_name = os.path.basename(self.selected_file)
                # Aquí usamos el hash ingresado del destinatario
                header = {
                    "dest_hash": dest_hash,
                    "filename": file_name,
                    "filesize": file_size
                }
                header_json = json.dumps(header)
                header_bytes = header_json.encode()
                header_length = len(header_bytes)
                
                # Envío del tamaño del header (4 bytes en orden de red)
                s.sendall(header_length.to_bytes(4, byteorder="big"))
                # Envío del header en JSON
                s.sendall(header_bytes)
                
                # Envío del archivo en bloques
                with open(self.selected_file, "rb") as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        s.sendall(bytes_read)
                messagebox.showinfo("Éxito", f"Archivo '{file_name}' enviado correctamente")
        except Exception as e:
            messagebox.showerror("Error al enviar", str(e))

    def start_server(self):
        """
        Función que inicia el servidor TCP para recibir archivos.
        Se ejecuta en un hilo aparte para no bloquear la interfaz.
        """
        if not os.path.exists("received_files"):
            os.makedirs("received_files")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("", SERVER_PORT))
            server_socket.listen(5)
            print(f"[Servidor] Escuchando en el puerto {SERVER_PORT}...")
            while True:
                conn, addr = server_socket.accept()
                print(f"[Servidor] Conexión desde {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        try:
            raw_header_len = self.recvall(conn, 4)
            if not raw_header_len:
                return
            header_len = int.from_bytes(raw_header_len, byteorder="big")
            header_bytes = self.recvall(conn, header_len)
            header = json.loads(header_bytes.decode())
            
            # Se valida que el hash recibido coincida con el hash local (del receptor)
            if header.get("dest_hash") != self.hash_direccion:
                print("[Servidor] Hash no coincide. Rechazando archivo.")
                conn.close()
                return
            
            filename = header.get("filename", "archivo_recibido")
            filesize = header.get("filesize", 0)
            save_path = os.path.join("received_files", filename)
            
            with open(save_path, "wb") as f:
                bytes_received = 0
                while bytes_received < filesize:
                    chunk = conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_received += len(chunk)
            print(f"[Servidor] Archivo recibido: {save_path}")
            self.master.after(0, lambda: messagebox.showinfo("Archivo recibido", f"Se ha recibido el archivo:\n{filename}"))
        except Exception as e:
            print(f"[Servidor] Error al recibir archivo: {e}")
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