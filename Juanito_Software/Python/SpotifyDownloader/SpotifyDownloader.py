# JuanitoSoftware 2025 - Spotify CSV Downloader
# Descarga canciones desde un CSV exportado con Exportify

import re
import csv
import os
import sys
from yt_dlp import YoutubeDL


def verificar_ffmpeg():
    ruta_ffmpeg = r'D:\ffmpeg\bin'
    ffmpeg_path = os.path.join(ruta_ffmpeg, 'ffmpeg.exe')
    ffprobe_path = os.path.join(ruta_ffmpeg, 'ffprobe.exe')
    if os.path.isfile(ffmpeg_path) and os.path.isfile(ffprobe_path):
        if ruta_ffmpeg not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ruta_ffmpeg + os.pathsep + os.environ.get('PATH', '')
        return True
    return False


def limpiar_nombre(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre)


def buscar_y_descargar(track_name, artist_name, carpeta_salida="descargas", calidad_mp3="320"):
    """Busca la canción en YouTube y la descarga como MP3."""
    query = f"{track_name} {artist_name}"
    print(f"\n🔍 Buscando: {query}")

    nombre_archivo = limpiar_nombre(f"{artist_name} - {track_name}")
    ruta_mp3 = os.path.join(carpeta_salida, nombre_archivo + ".mp3")

    if os.path.exists(ruta_mp3):
        print(f"⏭️  Ya existe, se omite: {nombre_archivo}.mp3")
        return

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
        'ignoreerrors': False,
        'quiet': False,
        'default_search': 'ytsearch1',  # busca en YouTube y toma el primer resultado
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
        },
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 3,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        if os.path.exists(ruta_mp3):
            print(f"✅ Descargado: {nombre_archivo}.mp3")
        else:
            print(f"⚠️  No se generó el MP3 para: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error descargando '{query}': {e}")


def descargar_desde_spotify_csv(ruta_csv):
    """Lee el CSV de Exportify y descarga cada canción."""
    if not os.path.exists(ruta_csv):
        print(f"❌ No se encontró el archivo: {ruta_csv}")
        return

    canciones = []
    with open(ruta_csv, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            track = fila.get('Track Name', '').strip()
            artist = fila.get('Artist Name(s)', '').strip()
            # Exportify puede listar varios artistas separados por coma; tomamos el primero
            artist = artist.split(',')[0].strip()
            if track and artist:
                canciones.append((track, artist))

    if not canciones:
        print("❌ No se encontraron canciones válidas en el CSV.")
        return

    print(f"🎵 {len(canciones)} canciones encontradas en el CSV.")
    print("▶  Iniciando descarga...\n")

    ok, fallo = 0, 0
    for i, (track, artist) in enumerate(canciones, 1):
        print(f"[{i}/{len(canciones)}]", end=" ")
        try:
            buscar_y_descargar(track, artist)
            ok += 1
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            fallo += 1

    print(f"\n🎉 Proceso terminado. ✅ {ok} descargadas  ❌ {fallo} fallidas")


if __name__ == "__main__":
    if not verificar_ffmpeg():
        print("⚠️  ffmpeg no encontrado en D:\\ffmpeg\\bin")
        print("   Instálalo con: winget install ffmpeg")
        continuar = input("¿Continuar de todos modos? (s/n): ").strip().lower()
        if continuar != "s":
            sys.exit(1)

    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        ruta = input("Ruta del CSV de Exportify: ").strip().strip('"')

    descargar_desde_spotify_csv(ruta)
    input("\nPulsa ENTER para salir...")