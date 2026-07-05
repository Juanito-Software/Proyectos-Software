# JuanitoSoftware 2025 - YoutubeToMp3 mixto (CSV o consola)

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

import re
from yt_dlp import YoutubeDL
import os
import subprocess
import sys
import csv
import shutil

def run_matrix_effect():
    """Ejecuta la animación de Matrix en la misma consola."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_path, "matrix_effect.exe")

    if os.path.exists(exe_path):
        print("🎬 Iniciando animación de Matrix. Pulsa Espacio o cierra la ventana para continuar...")
        try:
            result = subprocess.run([exe_path], check=False)
            #print(f"[DEBUG] matrix_effect.exe terminó con código: {result.returncode}")
        except Exception as e:
            print(f"❌ Error ejecutando matrix_effect.exe: {e}")
    else:
        print("❌ No se encontró matrix_effect.exe, se saltará la animación.")
        

def verificar_ffmpeg():
    """Verifica si ffmpeg está instalado y disponible en D:\ffmpeg\bin."""
    # Ruta fija de ffmpeg en la raíz de D:
    ruta_ffmpeg = r'D:\ffmpeg\bin'
    
    ffmpeg_path = os.path.join(ruta_ffmpeg, 'ffmpeg.exe')
    ffprobe_path = os.path.join(ruta_ffmpeg, 'ffprobe.exe')
    
    # Verificar que ambos archivos existen
    if os.path.isfile(ffmpeg_path) and os.path.isfile(ffprobe_path):
        # Añadir al PATH del proceso actual para que yt-dlp lo encuentre
        if ruta_ffmpeg not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ruta_ffmpeg + os.pathsep + os.environ.get('PATH', '')
        return True
    
    return False

def limpiar_nombre(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre)

def descargar_audio_mp3(url, carpeta_salida="descargas", calidad_mp3="320"):
    """Descarga el audio en MP3 de una URL de YouTube."""
    # Verificar ffmpeg antes de intentar descargar
    if not verificar_ffmpeg():
        print("❌ ERROR: ffmpeg no está instalado o no está en el PATH.")
        print("   Para convertir a MP3, necesitas instalar ffmpeg.")
        print("   Descarga desde: https://ffmpeg.org/download.html")
        print("   O instala con: winget install ffmpeg")
        print("   O con chocolatey: choco install ffmpeg")
        raise Exception("ffmpeg no está disponible")
    
    os.makedirs(carpeta_salida, exist_ok=True)
    # Opciones básicas para obtener información del video
    info_opts = {
        'quiet': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }
    with YoutubeDL(info_opts) as ydl:
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
        'ignoreerrors': False,
        'quiet': False,
        # Opciones para evitar error 403
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        },
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 3,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Verificar que el archivo MP3 se creó correctamente
        ruta_mp3 = os.path.join(carpeta_salida, nombre_archivo + ".mp3")
        if os.path.exists(ruta_mp3):
            print(f"✅ Descargado: {nombre_archivo}.mp3")
        else:
            print(f"⚠️  Advertencia: El archivo MP3 no se creó correctamente.")
            print(f"   Se descargó el video pero no se pudo convertir a MP3.")
            raise Exception("Error en la conversión a MP3")
    except Exception as e:
        if "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower():
            print("❌ ERROR: Problema con ffmpeg durante la conversión.")
            print("   Verifica que ffmpeg esté correctamente instalado.")
        raise

def descargar_desde_csv(ruta_csv="descargas.csv"):
    """Lee las URLs de un CSV y las descarga automáticamente sin input()"""
    if not os.path.exists(ruta_csv):
        print(f"❌ No se encontró el CSV: {ruta_csv}")
        return

    urls = []
    with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        if not lector.fieldnames or 'url' not in lector.fieldnames:
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
    # Verificar ffmpeg al inicio
    if not verificar_ffmpeg():
        print("⚠️  ADVERTENCIA: ffmpeg no está instalado o no está en el PATH.")
        print("   El programa necesita ffmpeg para convertir videos a MP3.")
        print("   Opciones para instalar:")
        print("   1. Con winget: winget install ffmpeg")
        print("   2. Con chocolatey: choco install ffmpeg")
        print("   3. Descarga manual: https://ffmpeg.org/download.html")
        print("   4. Añade ffmpeg al PATH después de instalarlo")
        continuar = input("\n¿Deseas continuar de todos modos? (s/n): ").strip().lower()
        if continuar != "s":
            print("Saliendo del programa...")
            sys.exit(1)
        print()

    # Animación opcional
    if hasattr(sys, '_MEIPASS'):
        _base = sys._MEIPASS
    else:
        _base = os.path.dirname(os.path.abspath(__file__))

    if os.path.exists(os.path.join(_base, "matrix_effect.exe")):
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
