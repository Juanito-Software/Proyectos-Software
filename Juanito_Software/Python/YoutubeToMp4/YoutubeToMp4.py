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


def obtener_ruta_ffmpeg():
    """Obtiene la ruta de ffmpeg, buscando primero en PATH y luego en rutas específicas."""
    # Primero intentar buscar en PATH
    ruta_ffmpeg = shutil.which('ffmpeg')
    if ruta_ffmpeg:
        return ruta_ffmpeg
    
    # Si no está en PATH, buscar en rutas específicas comunes
    rutas_especificas = [
        r"D:\ffmpeg\bin\ffmpeg.exe",  # Ruta proporcionada por el usuario
        r"C:\ffmpeg\bin\ffmpeg.exe",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe"),
    ]
    
    for ruta in rutas_especificas:
        if os.path.exists(ruta):
            return ruta
    
    return None


def ffmpeg_disponible():
    """Verifica si ffmpeg está disponible."""
    return obtener_ruta_ffmpeg() is not None


# ---------------- yt-dlp implementation ----------------

def descargar_con_ytdlp(url, carpeta_salida="descargas"):
    os.makedirs(carpeta_salida, exist_ok=True)

    if not HAS_YTDLP:
        raise RuntimeError("yt-dlp no está instalado en este entorno.")

    # Configurar ffmpeg ANTES de crear cualquier objeto YoutubeDL
    ruta_ffmpeg = obtener_ruta_ffmpeg()
    ruta_ffmpeg_dir = None
    if ruta_ffmpeg:
        ruta_ffmpeg_dir = os.path.dirname(ruta_ffmpeg)
        # Configurar PATH para que yt-dlp encuentre ffmpeg desde el inicio
        ffmpeg_bin_dir = ruta_ffmpeg_dir
        if ffmpeg_bin_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ffmpeg_bin_dir + os.pathsep + os.environ.get('PATH', '')

    # obtener información para el título y resolución
    titulo = None
    resolucion = "desconocida"
    
    # Configurar opciones básicas para obtener metadatos
    opts_metadatos = {'quiet': True, 'noplaylist': True}
    if ruta_ffmpeg_dir:
        opts_metadatos['ffmpeg_location'] = ruta_ffmpeg_dir

    try:
        with YoutubeDL(opts_metadatos) as ydl:
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

    # ruta_ffmpeg y ruta_ffmpeg_dir ya están configuradas arriba

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': ruta_salida,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'ignoreerrors': False,
        'quiet': False,
        
        # Opciones para evitar errores 403
        'retries': 10,                      # Reintentos automáticos
        'fragment_retries': 10,            # Reintentos para fragmentos
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],  # Usar cliente Android primero, luego web
            }
        },
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        
        # Subtítulos
        'writesubtitles': True,             # descargar subtítulos proporcionados por el creador
        'writeautomaticsub': True,          # descargar subtítulos automáticos si no hay
        'subtitleslangs': ['en'],           # solo en inglés
        'subtitlesformat': 'srt',           # archivo srt
        'embedsubtitles': True,             # True si quieres incrustar
    }
    
    # Si tenemos la ruta de ffmpeg, configurarla explícitamente para yt-dlp
    if ruta_ffmpeg_dir:
        ydl_opts['ffmpeg_location'] = ruta_ffmpeg_dir
        print(f"✓ Usando ffmpeg desde: {ruta_ffmpeg_dir}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Verificar que el archivo realmente se descargó
        ruta_final = os.path.join(carpeta_salida, f"{titulo} [{resolucion}].mp4")
        if os.path.exists(ruta_final):
            print(f"✅ Descargado (yt-dlp): {titulo} [{resolucion}].mp4")
            print(f"📁 Ubicación: {ruta_final}")
        else:
            # Buscar el archivo con cualquier extensión que pueda haber descargado
            archivos_encontrados = [f for f in os.listdir(carpeta_salida) if titulo in f]
            if archivos_encontrados:
                archivo_real = os.path.join(carpeta_salida, archivos_encontrados[0])
                print(f"✅ Descargado (yt-dlp): {archivos_encontrados[0]}")
                print(f"📁 Ubicación: {archivo_real}")
            else:
                print(f"❌ Error: El archivo no se descargó correctamente.")
                print(f"   Verifica los mensajes de error anteriores.")
    except Exception as e:
        print(f"❌ Error durante la descarga: {e}")
        raise


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
    # NOTA: Los streams progresivos NO requieren ffmpeg
    prog = streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if prog:
        resolucion = prog.resolution or 'desconocida'
        filename_noext = f"{titulo} [{resolucion}]"
        print(f"▶ Descargando stream progresivo (video+audio): {resolucion} ...")
        try:
            ruta_descargada = prog.download(output_path=carpeta_salida, filename=filename_noext)
            # pytube puede devolver la ruta completa o relativa, normalizarla
            if os.path.isabs(ruta_descargada):
                ruta_completa = ruta_descargada
            else:
                ruta_completa = os.path.abspath(ruta_descargada)
            # Verificar que el archivo existe
            if os.path.exists(ruta_completa):
                print(f"✅ Descargado (pytube - progresivo): {os.path.basename(ruta_completa)}")
                print(f"📁 Ubicación: {ruta_completa}")
            else:
                # Si no existe en la ruta esperada, buscar en la carpeta de salida
                ruta_alternativa = os.path.join(os.path.abspath(carpeta_salida), f"{filename_noext}.mp4")
                if os.path.exists(ruta_alternativa):
                    print(f"✅ Descargado (pytube - progresivo): {os.path.basename(ruta_alternativa)}")
                    print(f"📁 Ubicación: {ruta_alternativa}")
                else:
                    print(f"✅ Descargado (pytube - progresivo): {filename_noext}.mp4")
                    print(f"📁 Ubicación: {os.path.abspath(carpeta_salida)}")
            return
        except Exception as e:
            print(f"⚠️ Error descargando stream progresivo: {e}. Intentaré método adaptativo (requiere ffmpeg).")

    # 2) Si no hay progressive con buena resolución, intentar adaptive: video-only + audio-only y mergear
    video_stream = streams.filter(adaptive=True, only_video=True).order_by('resolution').desc().first()
    audio_stream = streams.filter(only_audio=True).order_by('abr').desc().first()

    if not video_stream:
        print("❌ No se encontró ningún stream de vídeo válido con pytube.")
        return

    if not audio_stream:
        print("⚠️ No se encontró stream de audio. Se descargará solo vídeo si es posible.")

    # comprobar ffmpeg (solo necesario para streams adaptativos, no para progresivos)
    ruta_ffmpeg = obtener_ruta_ffmpeg()
    if not ruta_ffmpeg:
        print("❌ ffmpeg no está disponible.")
        print("   Los streams progresivos no requieren ffmpeg, pero para mergear video+audio adaptativos sí es necesario.")
        print("   Instalación:")
        print("   - Windows: Descarga desde https://ffmpeg.org/download.html y añádelo al PATH")
        print("   - Linux: sudo apt install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print(f"   - O coloca ffmpeg.exe en: {os.path.dirname(os.path.abspath(__file__))}")
        return
    else:
        print(f"✓ ffmpeg encontrado: {ruta_ffmpeg}")

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
            ruta_ffmpeg = obtener_ruta_ffmpeg()
            if not ruta_ffmpeg:
                print("❌ No se pudo encontrar ffmpeg.")
                return
            
            cmd_copy_audio = [
                ruta_ffmpeg, '-y', '-i', video_path, '-i', audio_path,
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', salida_final
            ]
            print("▶ Mergeando video+audio con ffmpeg (intento rápido - copia de vídeo + re-encode de audio)...")
            try:
                subprocess.run(cmd_copy_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ Descargado (pytube - adaptive): {os.path.basename(salida_final)}")
                print(f"📁 Ubicación: {os.path.abspath(salida_final)}")
                return
            except subprocess.CalledProcessError:
                print("⚠️ El merge rápido con copia falló. Intentando re-encode completo (más lento)...")
                # re-encode completo
                cmd_reencode = [
                    ruta_ffmpeg, '-y', '-i', video_path, '-i', audio_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '192k', salida_final
                ]
                try:
                    subprocess.run(cmd_reencode, check=True)
                    print(f"✅ Descargado (pytube - adaptive, re-encode): {os.path.basename(salida_final)}")
                    print(f"📁 Ubicación: {os.path.abspath(salida_final)}")
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

def descargar_video_mp4(url, carpeta_salida=None, gestor_preferido='yt-dlp'):
    # Si no se especifica carpeta, usar "descargas" en el mismo directorio del script
    if carpeta_salida is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        carpeta_salida = os.path.join(script_dir, "descargas")
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
        if not url:  # Si está vacío, continuar el bucle
            continue
        if url.lower() in ("salir", "n", "no"):
            print("Gracias por usar el programa. Esperamos verte pronto.👋")
            break
        # Validar que sea una URL válida
        if not (url.startswith("http://") or url.startswith("https://")):
            print("❌ Por favor, introduce una URL válida que comience con http:// o https://")
            continue
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
    
    # Detectar si el usuario escribió una URL por error
    if modo.startswith("http://") or modo.startswith("https://") or "youtube.com" in modo or "youtu.be" in modo:
        print("⚠️ Parece que escribiste una URL. Se usará modo manual.")
        print("   La próxima vez, escribe 'manual' o 'csv' para elegir el modo.\n")
        proceso_interactivo(gestor=gestor_elegido)
    elif modo == "csv":
        ruta_csv = input("Ruta del CSV (por defecto descargas.csv): ").strip() or "descargas.csv"
        descargar_desde_csv(ruta_csv, gestor=gestor_elegido)
    else:
        proceso_interactivo(gestor=gestor_elegido)

    print("🎉 Todas las descargas han terminado.")
    input("\nPulsa ENTER para salir...")
