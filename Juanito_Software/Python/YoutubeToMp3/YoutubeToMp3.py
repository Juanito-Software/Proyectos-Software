# Juanito Software 2025

# YoutubeToMp3
from yt_dlp import YoutubeDL
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

def descargar_audio_mp3(url, carpeta_salida="descargas", nombre_archivo="audio", calidad_mp3="320"):
    # Nos aseguramos de que la carpeta exista
    os.makedirs(carpeta_salida, exist_ok=True)

    ruta_salida = os.path.join(carpeta_salida, nombre_archivo + ".%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': ruta_salida,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': calidad_mp3,
        }],
        'noplaylist': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"✅ Descargado: {info['nombre_archivo']}.mp3")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        url = sys.argv[1]
        nombre = sys.argv[2]
        descargar_audio_mp3(url, nombre_archivo=nombre)
    else:
        try:
            run_matrix_effect()
        except subprocess.CalledProcessError as e:
            print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
        except Exception as e:
            print(f"Error inesperado ejecutando matrix_effect.exe: {e}")
        finally:
            url = input("📥 Introduce la URL del video de YouTube:\n> ").strip()
            nombre = input("📁 Nombre de archivo MP3 (sin .mp3):\n> ").strip()
            descargar_audio_mp3(url, nombre_archivo=nombre)
