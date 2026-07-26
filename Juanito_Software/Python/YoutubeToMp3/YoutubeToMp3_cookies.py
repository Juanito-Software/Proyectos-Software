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
        

def verificar_runtime_js():
    """Verifica los runtimes JS disponibles para yt-dlp EJS.
    Retorna (deno_ok, node_version_o_None).
    yt-dlp EJS requiere Deno >= 2.3.0 (recomendado) o Node.js >= 22.0.0.
    """
    deno_ok = shutil.which('deno') is not None

    node_version = None
    if shutil.which('node'):
        try:
            out = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            # salida: "v22.1.0"
            major = int(out.stdout.strip().lstrip('v').split('.')[0])
            node_version = major
        except Exception:
            node_version = 0

    return deno_ok, node_version


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

def obtener_opciones_cookies():
    """Retorna las opciones de cookies de Firefox para yt-dlp."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ruta_cookies = os.path.join(base_path, 'cookies.txt')

    if os.path.exists(ruta_cookies):
        print("🍪 Usando cookies desde archivo: cookies.txt")
        return {'cookiefile': ruta_cookies}

    print("🦊 Usando cookies de Firefox para autenticarse en YouTube.")
    return {'cookiesfrombrowser': ('firefox',)}


def _tipo_error_cookies(err_str):
    """Retorna el tipo de error de cookies o None si no es uno."""
    err = err_str.lower()
    if 'dpapi' in err or ('decrypt' in err and 'cookie' in err):
        return 'dpapi'
    if 'cookie' in err and ('database' in err or 'could not copy' in err):
        return 'locked'
    return None


def _es_error_formato(err_str):
    """Detecta el error de 'no hay formatos disponibles' causado por fallo del challenge JS."""
    return 'requested format is not available' in err_str.lower()


def _es_error_bot(err_str):
    """Detecta el bloqueo de YouTube por detección de bot."""
    err = err_str.lower()
    return 'sign in to confirm' in err or 'not a bot' in err


def _mostrar_ayuda_formato():
    print("\n❌ YouTube no devolvió formatos de audio/vídeo descargables.")
    print("   Causa: yt-dlp no pudo resolver el challenge de JavaScript de YouTube (EJS).")
    print("   Solución definitiva: instala Node.js desde https://nodejs.org")
    print("   Node.js proporciona el runtime JS que yt-dlp necesita para los challenges.")


def limpiar_nombre(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre)

def descargar_audio_mp3(url, carpeta_salida="descargas", calidad_mp3="320", cookies_opts=None):
    """Descarga el audio en MP3 de una URL de YouTube."""
    if cookies_opts is None:
        cookies_opts = {}

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
    # tv_embedded usa un JS más compacto que a veces jsinterp puede resolver sin Node.js.
    # web_embedded y web como fallbacks con cookies.
    # Sin cookies: android evita bot-detection sin necesitar EJS.
    player_clients = ['tv_embedded', 'web_embedded', 'web'] if cookies_opts else ['android', 'web']

    info_opts = {
        'quiet': True,
        'noplaylist': True,
        'js_runtimes': {'deno': {}, 'node': {}},  # prueba Deno; si no está, usa Node.js
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': player_clients,
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        **cookies_opts,
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
        'js_runtimes': {'deno': {}, 'node': {}},  # prueba Deno; si no está, usa Node.js
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': player_clients,
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
        **cookies_opts,
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

def descargar_desde_csv(ruta_csv="descargas.csv", cookies_opts=None):
    """Lee las URLs de un CSV y las descarga automáticamente sin input()"""
    if cookies_opts is None:
        cookies_opts = {}

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
            descargar_audio_mp3(url, cookies_opts=cookies_opts)
        except Exception as e:
            err = str(e)
            tipo = _tipo_error_cookies(err)
            if tipo:
                _manejar_error_cookies(tipo)
            elif _es_error_formato(err):
                _mostrar_ayuda_formato()
                if cookies_opts:
                    print("   Reintentando sin cookies con cliente android...")
                    try:
                        descargar_audio_mp3(url, cookies_opts={})
                    except Exception as e2:
                        if _es_error_bot(str(e2)):
                            print("   ❌ Ambos métodos fallan sin Node.js. Instala Node.js desde https://nodejs.org")
                        else:
                            print(f"❌ Error sin cookies para {url}: {e2}")
            elif _es_error_bot(err):
                print(f"❌ YouTube bloqueó {url} como bot. Usa cookies de navegador.")
            else:
                print(f"❌ Error descargando {url}: {e}")

def _manejar_error_cookies(tipo):
    """Muestra ayuda según el tipo de error de cookies de Firefox."""
    if tipo == 'locked':
        print("\n❌ Firefox tiene la base de datos de cookies bloqueada.")
        print("   Cierra Firefox completamente y vuelve a intentarlo.")
    else:
        print("\n❌ Error al leer las cookies de Firefox.")
        print("   Asegúrate de que Firefox esté instalado y hayas iniciado sesión en YouTube.")


def proceso_interactivo(cookies_opts=None):
    """Modo interactivo por consola, URLs una a una"""
    if cookies_opts is None:
        cookies_opts = {}

    print("📥 Modo interactivo. Escribe 'salir' para terminar.")
    while True:
        url = input("\nIntroduce la URL de YouTube (o 'salir'):\n> ").strip()
        if url.lower() in ("salir", "n", "no"):
            print("Gracias por usar el programa. Esperamos verte pronto.👋")
            break
        try:
            descargar_audio_mp3(url, cookies_opts=cookies_opts)
        except Exception as e:
            err = str(e)
            tipo = _tipo_error_cookies(err)
            if tipo:
                _manejar_error_cookies(tipo)
            elif _es_error_formato(err):
                _mostrar_ayuda_formato()
                if cookies_opts:
                    op = input("   ¿Intentar sin cookies con cliente android (vídeos públicos)? (s/n): ").strip().lower()
                    if op == 's':
                        try:
                            descargar_audio_mp3(url, cookies_opts={})
                        except Exception as e2:
                            if _es_error_bot(str(e2)):
                                print("\n❌ Ambos métodos fallan sin Node.js:")
                                print("   · Con cookies (web): necesita Node.js para el challenge JS")
                                print("   · Sin cookies (android): YouTube bloquea como bot")
                                print("   → Instala Node.js desde https://nodejs.org y vuelve a intentarlo.")
                            else:
                                print(f"❌ Error sin cookies: {e2}")
            elif _es_error_bot(err):
                print("\n❌ YouTube ha bloqueado el acceso como bot.")
                print("   Vuelve al inicio y selecciona un navegador para usar sus cookies.")
            else:
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

    # Verificar runtime JS para yt-dlp EJS (necesario para challenges de YouTube)
    deno_ok, node_version = verificar_runtime_js()
    if not deno_ok and node_version is None:
        print("⚠️  IMPORTANTE: No se detectó Deno ni Node.js.")
        print("   yt-dlp los necesita para resolver los challenges JS de YouTube.")
        print("   · Instala Deno (recomendado): https://deno.com")
        print("   · O instala Node.js >= 22:    https://nodejs.org")
        print("   Además ejecuta: pip install -U \"yt-dlp[default]\"")
        print()
    elif not deno_ok and node_version is not None and node_version < 22:
        print(f"⚠️  Node.js v{node_version} detectado, pero yt-dlp requiere v22 o superior.")
        print("   · Actualiza Node.js a v22+: https://nodejs.org")
        print("   · O instala Deno (más fácil): https://deno.com")
        print("   Además ejecuta: pip install -U \"yt-dlp[default]\"")
        print()
    elif node_version is not None and node_version >= 22:
        print(f"ℹ️  Node.js v{node_version} detectado — se usará para resolver los challenges JS de YouTube.")
        print()

    # Autenticación con YouTube via cookies
    cookies_opts = obtener_opciones_cookies()

    # Preguntar modo de descarga
    modo = input("\n¿Quieres descargar automáticamente desde CSV o manualmente por consola? (csv/manual): ").strip().lower()
    if modo == "csv":
        descargar_desde_csv(cookies_opts=cookies_opts)
    else:
        proceso_interactivo(cookies_opts=cookies_opts)

    print("🎉 Todas las descargas han terminado.")
    input("\nPulsa ENTER para salir...")
