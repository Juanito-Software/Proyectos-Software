# Juanito Software 2025 - YoutubeToMp3 mixto (CSV o consola)
import re
from yt_dlp import YoutubeDL
import os
import subprocess
import sys
import csv

def run_matrix_effect():
    """Ejecuta la animación de Matrix en la misma consola."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_path, "matrix_effect.exe")

    if os.path.exists(exe_path):
        print("🎬 Iniciando animación de Matrix. Pulsa ESC o cierra la ventana para continuar...")
        try:
            subprocess.run([exe_path], check=False)
        except Exception as e:
            print(f"❌ Error ejecutando matrix_effect.exe: {e}")
    else:
        print("❌ No se encontró matrix_effect.exe, se saltará la animación.")

def limpiar_nombre(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre)

def descargar_audio_mp3(url, carpeta_salida="descargas", calidad_mp3="320"):
    """Descarga el audio en MP3 de una URL de YouTube."""
    os.makedirs(carpeta_salida, exist_ok=True)
    with YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        nombre_archivo = limpiar_nombre(info['title'])

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
        'ignoreerrors': True,
        'quiet': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print(f"✅ Descargado: {nombre_archivo}.mp3")

def descargar_desde_csv(ruta_csv="descargas.csv"):
    """Lee las URLs de un CSV y las descarga automáticamente sin input()"""
    if not os.path.exists(ruta_csv):
        print(f"❌ No se encontró el CSV: {ruta_csv}")
        return

    urls = []
    with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        if 'url' not in lector.fieldnames:
            print("❌ El CSV debe tener una columna llamada 'url'.")
            return
        for fila in lector:
            url = fila['url'].strip()
            if url:
                urls.append(url)

    if not urls:
        print("❌ No se encontraron URLs válidas en el CSV.")
        return

    print(f"▶ Iniciando descarga de {len(urls)} vídeos desde CSV...")
    for url in urls:
        try:
            descargar_audio_mp3(url)
        except Exception as e:
            print(f"❌ Error descargando {url}: {e}")

def proceso_interactivo():
    """Modo interactivo por consola, URLs una a una"""
    print("📥 Modo interactivo. Escribe 'salir' para terminar.")
    while True:
        url = input("\nIntroduce la URL de YouTube (o 'salir'):\n> ").strip()
        if url.lower() in ("salir", "n", "no"):
            print("Gracias por usar el programa. Esperamos verte pronto.👋")
            break
        try:
            descargar_audio_mp3(url)
        except Exception as e:
            print(f"❌ Error en la descarga: {e}")

if __name__ == "__main__":
    # Animación opcional
    if os.path.exists("matrix_effect.exe"):
        ver_intro = input("¿Quieres ver la animación de Matrix? (s/n): ").strip().lower()
        if ver_intro == "s":
            run_matrix_effect()

    # Preguntar modo de descarga
    modo = input("\n¿Quieres descargar automáticamente desde CSV o manualmente por consola? (csv/manual): ").strip().lower()
    if modo == "csv":
        descargar_desde_csv()
    else:
        proceso_interactivo()

    print("🎉 Todas las descargas han terminado.")
    input("\nPulsa ENTER para salir...")
