# Juanito Software 2025 - YoutubeToMP4 mixto (CSV o consola)
# Soporta dos 'gestores' de descarga: yt-dlp y pytube
# - yt-dlp: usa 'bestvideo+bestaudio/best' y merge automático (requiere ffmpeg para mergear ciertos casos)
# - pytube: intenta descargar el stream progressive más alto; si no existe, baja video-only + audio-only y los mergea con ffmpeg

import re
import os
import subprocess
import sys
import csv
import uuid
import tempfile
import shutil

# intentos de import
HAS_YTDLP = False
HAS_PYTUBE = False

try:
    from yt_dlp import YoutubeDL
    HAS_YTDLP = True
except Exception:
    HAS_YTDLP = False

try:
    from pytubefix import YouTube
    HAS_PYTUBE = True
except Exception:
    HAS_PYTUBE = False


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
    """Elimina caracteres no válidos para nombres de archivos."""
    return re.sub(r'[\\/*?:"<>|]', "", nombre)


def ffmpeg_disponible():
    return shutil.which('ffmpeg') is not None


# ---------------- yt-dlp implementation ----------------

def descargar_con_ytdlp(url, carpeta_salida="descargas"):
    os.makedirs(carpeta_salida, exist_ok=True)

    # obtener información para el título y resolución
    titulo = None
    resolucion = "desconocida"
    if not HAS_YTDLP:
        raise RuntimeError("yt-dlp no está instalado en este entorno.")

    try:
        with YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            titulo = limpiar_nombre(info.get('title', 'video'))
            # intentar obtener la altura (height) preferentemente
            height = info.get('height')
            if not height:
                # buscar en formatos
                heights = [f.get('height') for f in info.get('formats', []) if f.get('height')]
                if heights:
                    height = max(heights)
            if height:
                resolucion = f"{height}p"
    except Exception as e:
        print(f"⚠️ Error obteniendo metadatos con yt-dlp: {e}")
        titulo = titulo or "video"

    ruta_salida = os.path.join(carpeta_salida, f"{titulo} [{resolucion}].%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': ruta_salida,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'ignoreerrors': True,
        'quiet': False,

        # Subtítulos
        'writesubtitles': True,             # descargar subtítulos proporcionados por el creador
        'writeautomaticsub': True,          # descargar subtítulos automáticos si no hay
        'subtitleslangs': ['en'],           # solo en inglés
        'subtitlesformat': 'srt',           # archivo srt
        'embedsubtitles': True              # True si quieres incrustar
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"✅ Descargado (yt-dlp): {titulo} [{resolucion}].mp4")


# ---------------- pytube implementation ----------------

def descargar_con_pytube(url, carpeta_salida="descargas"):
    os.makedirs(carpeta_salida, exist_ok=True)

    if not HAS_PYTUBE:
        raise RuntimeError("pytube no está instalado en este entorno.")

    try:
        yt = YouTube(url)
    except Exception as e:
        print(f"❌ Error inicializando pytube para la URL: {e}")
        return

    titulo = limpiar_nombre(yt.title or "video")
    streams = yt.streams

    # 1) Intentar progressive (video+audio en un solo archivo) - es lo más sencillo
    prog = streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if prog:
        resolucion = prog.resolution or 'desconocida'
        filename_noext = f"{titulo} [{resolucion}]"
        print(f"▶ Descargando stream progresivo (video+audio): {resolucion} ...")
        try:
            prog.download(output_path=carpeta_salida, filename=filename_noext)
            print(f"✅ Descargado (pytube - progresivo): {filename_noext}.mp4")
            return
        except Exception as e:
            print(f"⚠️ Error descargando stream progresivo: {e}. Intentaré método adaptativo.")

    # 2) Si no hay progressive con buena resolución, intentar adaptive: video-only + audio-only y mergear
    video_stream = streams.filter(adaptive=True, only_video=True).order_by('resolution').desc().first()
    audio_stream = streams.filter(only_audio=True).order_by('abr').desc().first()

    if not video_stream:
        print("❌ No se encontró ningún stream de vídeo válido con pytube.")
        return

    if not audio_stream:
        print("⚠️ No se encontró stream de audio. Se descargará solo vídeo si es posible.")

    # comprobar ffmpeg
    if not ffmpeg_disponible():
        print("❌ ffmpeg no está disponible en PATH. Para mergear video+audio con pytube necesitas ffmpeg instalado.")
        print("   Puedes instalarlo en Linux: sudo apt install ffmpeg  (o usar el instalador de tu SO).")
        return

    tmp_dir = tempfile.mkdtemp(prefix='ytmp_')

    try:
        print("▶ Descargando video (solo video, adaptive)...")
        video_path = video_stream.download(output_path=tmp_dir)
        print(f"   -> video temporal: {video_path}")

        if audio_stream:
            print("▶ Descargando audio (solo audio)...")
            audio_path = audio_stream.download(output_path=tmp_dir)
            print(f"   -> audio temporal: {audio_path}")
        else:
            audio_path = None

        resolucion = getattr(video_stream, 'resolution', None) or 'desconocida'
        salida_final = os.path.join(carpeta_salida, f"{titulo} [{resolucion}].mp4")

        # Intentar merge con ffmpeg: copiar vídeo y reconvertir audio a aac
        if audio_path:
            cmd_copy_audio = [
                'ffmpeg', '-y', '-i', video_path, '-i', audio_path,
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', salida_final
            ]
            print("▶ Mergeando video+audio con ffmpeg (intento rápido - copia de vídeo + re-encode de audio)...")
            try:
                subprocess.run(cmd_copy_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ Descargado (pytube - adaptive): {os.path.basename(salida_final)}")
                return
            except subprocess.CalledProcessError:
                print("⚠️ El merge rápido con copia falló. Intentando re-encode completo (más lento)...")
                # re-encode completo
                cmd_reencode = [
                    'ffmpeg', '-y', '-i', video_path, '-i', audio_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '192k', salida_final
                ]
                try:
                    subprocess.run(cmd_reencode, check=True)
                    print(f"✅ Descargado (pytube - adaptive, re-encode): {os.path.basename(salida_final)}")
                    return
                except subprocess.CalledProcessError as e:
                    print(f"❌ Falló el merge/re-encode con ffmpeg: {e}")
                    return
        else:
            # No hay audio: simplemente mover/renombrar el video descargado a la carpeta de salida
            # pero advertir que no tiene audio
            destino = salida_final
            shutil.move(video_path, destino)
            print(f"⚠️ Descargado solo vídeo (sin audio): {os.path.basename(destino)}")
            return

    finally:
        # limpiar temporales
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass


# ---------------- wrapper y flujo principal ----------------

def descargar_video_mp4(url, carpeta_salida="C:\\Users\\User\\Desktop\\Proyectos\\Juanito_Software\\Python\\YoutubeToMp4\\descargas", gestor_preferido='yt-dlp'):
    gestor = gestor_preferido.lower()
    if gestor in ('yt-dlp', 'ytdlp', 'yt'):
        if not HAS_YTDLP:
            raise RuntimeError('Has elegido yt-dlp pero no está instalado en el entorno.')
        return descargar_con_ytdlp(url, carpeta_salida)
    elif gestor in ('pytube', 'py'):
        if not HAS_PYTUBE:
            raise RuntimeError('Has elegido pytube pero no está instalado en el entorno.')
        return descargar_con_pytube(url, carpeta_salida)
    else:
        raise ValueError('Gestor desconocido: ' + str(gestor_preferido))


def descargar_desde_csv(ruta_csv="descargas.csv", gestor='yt-dlp'):
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

    print(f"▶ Iniciando descarga de {len(urls)} vídeos desde CSV con gestor: {gestor} ...")
    for url in urls:
        try:
            descargar_video_mp4(url, gestor_preferido=gestor)
        except Exception as e:
            print(f"❌ Error descargando {url}: {e}")


def proceso_interactivo(gestor='yt-dlp'):
    """Modo interactivo por consola, URLs una a una"""
    print("📥 Modo interactivo. Escribe 'salir' para terminar.")
    while True:
        url = input("\nIntroduce la URL de YouTube (o 'salir'):\n> ").strip()
        if url.lower() in ("salir", "n", "no"):
            print("Gracias por usar el programa. Esperamos verte pronto.👋")
            break
        try:
            descargar_video_mp4(url, gestor_preferido=gestor)
        except Exception as e:
            print(f"❌ Error en la descarga: {e}")


if __name__ == "__main__":
    # Animación opcional
    if os.path.exists("matrix_effect.exe"):
        ver_intro = input("¿Quieres ver la animación de Matrix? (s/n): ").strip().lower()
        if ver_intro == "s":
            run_matrix_effect()

    # Preguntar gestor de descargas primero
    print("\n¿Qué gestor de descargas quieres usar?")
    print("  1) yt-dlp (recomendado: maneja mejor calidades y merges automáticos)")
    print("  2) pytube  (útil si prefieres una dependencia ligera en Python)")
    gestor = input("Elige 1 o 2 (por defecto 1): ").strip()
    if gestor in ('2', 'pytube', 'py'):
        gestor_elegido = 'pytube'
    else:
        gestor_elegido = 'yt-dlp'

    # Comprobar disponibilidad y avisar / fallback
    if gestor_elegido == 'yt-dlp' and not HAS_YTDLP:
        print("⚠️ yt-dlp no está instalado en este entorno.")
        if HAS_PYTUBE:
            print("Se usará pytube como alternativa.")
            gestor_elegido = 'pytube'
        else:
            print("Instala yt-dlp (pip install yt-dlp) o pytube (pip install pytube) y vuelve a intentarlo.")
            sys.exit(1)
    if gestor_elegido == 'pytube' and not HAS_PYTUBE:
        print("⚠️ pytube no está instalado en este entorno.")
        if HAS_YTDLP:
            print("Se usará yt-dlp como alternativa.")
            gestor_elegido = 'yt-dlp'
        else:
            print("Instala pytube (pip install pytube) o yt-dlp (pip install yt-dlp) y vuelve a intentarlo.")
            sys.exit(1)

    # Preguntar modo de descarga
    modo = input("\n¿Quieres descargar automáticamente desde CSV o manualmente por consola? (csv/manual): ").strip().lower()
    if modo == "csv":
        ruta_csv = input("Ruta del CSV (por defecto descargas.csv): ").strip() or "descargas.csv"
        descargar_desde_csv(ruta_csv, gestor=gestor_elegido)
    else:
        proceso_interactivo(gestor=gestor_elegido)

    print("🎉 Todas las descargas han terminado.")
    input("\nPulsa ENTER para salir...")
