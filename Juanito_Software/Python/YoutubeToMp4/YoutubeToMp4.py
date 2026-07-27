# JuanitoSoftware 2025 - YoutubeToMP4 (CSV o consola)
# Gestor de descargas: pytube
# - pytube: intenta descargar el stream progressive más alto; si no existe, baja video-only + audio-only y los mergea con ffmpeg

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
import os
import subprocess
import sys
import csv
import tempfile
import shutil
from urllib.parse import urlparse

HAS_PYTUBE = False

# Dominios de los que se acepta descargar.
DOMINIOS_YOUTUBE = (
    "youtube.com",
    "youtu.be",
    "youtube-nocookie.com",
)


def es_url_de_youtube(url: str) -> bool:
    """
    Comprueba que la URL apunta realmente a YouTube.

    La comprobacion se hace sobre el HOST extraido con urlparse, no buscando
    subcadenas dentro de la URL entera. Escribir `"youtube.com" in url` parece
    equivalente y no lo es: esa condicion la cumple tambien
    https://youtube.com.sitio-falso.net/x, porque la cadena aparece dentro del
    dominio del atacante. La URL entera contiene demasiadas partes que un
    tercero controla (ruta, parametros, fragmento) como para buscar en ella.

    Del mismo modo, se exige que el host sea el dominio exacto o un subdominio
    suyo comparando con el punto delante (".youtube.com"). Sin ese punto,
    "mi-youtube.com" pasaria el filtro.
    """
    try:
        partes = urlparse(url)
    except ValueError:
        return False

    if partes.scheme not in ("http", "https"):
        return False

    host = (partes.hostname or "").lower()
    return any(
        host == dominio or host.endswith("." + dominio)
        for dominio in DOMINIOS_YOUTUBE
    )

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
        print("🎬 Iniciando animación de Matrix. Pulsa Espacio o cierra la ventana para continuar...")
        try:
            result = subprocess.run([exe_path], check=False)
            #print(f"[DEBUG] matrix_effect.exe terminó con código: {result.returncode}")
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
        filename_base = f"{titulo} [{resolucion}]"
        filename_mp4 = f"{filename_base}.mp4"
        print(f"▶ Descargando stream progresivo (video+audio): {resolucion} ...")
        try:
            # Forzamos que el archivo termine en .mp4
            ruta_descargada = prog.download(output_path=carpeta_salida, filename=filename_mp4)
            # pytube puede devolver la ruta completa o relativa, normalizarla
            if os.path.isabs(ruta_descargada):
                ruta_completa = ruta_descargada
            else:
                ruta_completa = os.path.abspath(ruta_descargada)
            # Si por algún motivo la ruta no tiene extensión, la añadimos
            base, ext = os.path.splitext(ruta_completa)
            if not ext:
                nueva_ruta = base + ".mp4"
                try:
                    os.rename(ruta_completa, nueva_ruta)
                    ruta_completa = nueva_ruta
                except OSError:
                    # Si no se puede renombrar, al menos informamos la carpeta
                    print("⚠️ No se pudo renombrar el archivo para añadir .mp4. Revisa la carpeta de descargas.")
            # Verificar que el archivo existe
            if os.path.exists(ruta_completa):
                print(f"✅ Descargado (pytube - progresivo): {os.path.basename(ruta_completa)}")
                print(f"📁 Ubicación: {ruta_completa}")
            else:
                # Como último recurso, mostrar la carpeta de salida y el nombre esperado
                print(f"✅ Descargado (pytube - progresivo): {filename_mp4}")
                print(f"📁 Ubicación (carpeta): {os.path.abspath(carpeta_salida)}")
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

def descargar_video_mp4(url, carpeta_salida=None):
    # La validacion se hace aqui y no en cada sitio que pide una URL, porque
    # este es el punto por el que pasan todas: el modo interactivo y el CSV.
    # Repartirla por los puntos de entrada es como se acaba olvidando en uno.
    if not es_url_de_youtube(url):
        raise ValueError(f"La URL no pertenece a YouTube: {url}")

    if carpeta_salida is None:
        if hasattr(sys, '_MEIPASS'):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        carpeta_salida = os.path.join(script_dir, "descargas")
    if not HAS_PYTUBE:
        raise RuntimeError('pytube no está instalado en este entorno.')
    return descargar_con_pytube(url, carpeta_salida)


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

    print(f"▶ Iniciando descarga de {len(urls)} vídeos desde CSV con pytube ...")
    for url in urls:
        try:
            descargar_video_mp4(url)
        except Exception as e:
            print(f"❌ Error descargando {url}: {e}")


def proceso_interactivo():
    """Modo interactivo por consola, URLs una a una"""
    print("📥 Modo interactivo. Escribe 'salir' para terminar.")
    while True:
        url = input("\nIntroduce la URL de YouTube (o 'salir'):\n> ").strip()
        if not url:  # Si está vacío, continuar el bucle
            continue
        if url.lower() in ("salir", "n", "no"):
            print("Gracias por usar el programa. Esperamos verte pronto.👋")
            break
        # Validar que sea una URL de YouTube
        if not es_url_de_youtube(url):
            print("❌ Introduce una URL de YouTube válida (youtube.com, youtu.be) con http:// o https://")
            continue
        try:
            descargar_video_mp4(url)
        except Exception as e:
            print(f"❌ Error en la descarga: {e}")


if __name__ == "__main__":
    # Animación opcional
    if hasattr(sys, '_MEIPASS'):
        _base = sys._MEIPASS
    else:
        _base = os.path.dirname(os.path.abspath(__file__))

    if os.path.exists(os.path.join(_base, "matrix_effect.exe")):
        ver_intro = input("¿Quieres ver la animación de Matrix? (s/n): ").strip().lower()
        if ver_intro == "s":
            run_matrix_effect()

    # Comprobar disponibilidad de pytube
    if not HAS_PYTUBE:
        print("⚠️ pytube no está instalado en este entorno.")
        print("Instala pytubefix con: pip install pytubefix")
        sys.exit(1)

    # Preguntar modo de descarga (csv o manual)
    modo = input("\n¿Quieres descargar automáticamente desde CSV o manualmente por consola? (csv/manual): ").strip().lower()
    
    # Detectar si el usuario escribió una URL por error.
    #
    # Esto es una comodidad, no un control de seguridad: si acierta, se pasa al
    # modo manual, que vuelve a pedir la URL y esa si se valida. Aun asi se usa
    # la misma funcion que el resto, para no dejar en el codigo un
    # `"youtube.com" in modo` que el siguiente lector pueda copiar creyendo que
    # es una comprobacion valida.
    if es_url_de_youtube(modo) or modo.startswith(("http://", "https://")):
        print("⚠️ Parece que escribiste una URL. Se usará modo manual.")
        print("   La próxima vez, escribe 'manual' o 'csv' para elegir el modo.\n")
        proceso_interactivo()
    elif modo == "csv":
        ruta_csv = input("Ruta del CSV (por defecto descargas.csv): ").strip() or "descargas.csv"
        descargar_desde_csv(ruta_csv)
    else:
        proceso_interactivo()

    print("🎉 Todas las descargas han terminado.")
    input("\nPulsa ENTER para salir...")
