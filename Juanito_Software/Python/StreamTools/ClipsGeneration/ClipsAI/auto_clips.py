# Copyright (C) 2025 Juanito Software
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

import os
import subprocess
from clipsai.clip.clipfinder import ClipFinder
from clipsai import Transcriber, resize
from tkinter import Tk, filedialog
import nltk
nltk.download('punkt')      # Tokenizador general
nltk.download('punkt_tab')  # Variante requerida por algunas funciones de NLTK

# ===========================
# SELECCIÓN DINÁMICA DE VIDEO
# ===========================
print("Seleccione un video para transcribir y generar clips a partir de él...")
root = Tk()
root.withdraw()                    # Oculta la ventana principal
root.attributes("-topmost", True) # Asegura que el diálogo quede encima
VIDEO_PATH = filedialog.askopenfilename(
    title="Seleccione un video",
    filetypes=[("Archivos de video", "*.mp4 *.mov *.mkv *.avi"), ("Todos los archivos", "*.*")]
    ,
    parent=root                    # Usa root como ventana padre
)
root.destroy()                     # Cierra la ventana raíz después

if not VIDEO_PATH:
    print("No se seleccionó ningún video. Saliendo del programa.")
    exit()


# ===========================
# FUNCIONES AUXILIARES
# ===========================
def reconvertir_video(input_path):
    """Reconviertir el video a MP4 estándar con FFmpeg"""
    output_path = os.path.splitext(input_path)[0] + "_reconverted.mp4"
    print(f"[INFO] Reconvirtiendo video a MP4 estándar: {output_path}")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", output_path],
            check=True
        )
        return output_path
    except subprocess.CalledProcessError:
        print("[ERROR] No se pudo reconvertir el video.")
        exit()
        
# ===========================
# CONFIGURACIÓN
# ===========================
OUTPUT_DIR = "./clips_output"
PYANNOTE_TOKEN = os.getenv("HF_TOKEN")
RESIZE_ASPECT_RATIO = (9, 16)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===========================
# TRANSCRIPCIÓN DEL VIDEO
# ===========================
print("[INFO] Transcribiendo video...")
transcriber = Transcriber()

try:
    transcription = transcriber.transcribe(audio_file_path=VIDEO_PATH)
except Exception as e:
    print(f"[WARN] Error al transcribir el video: {e}")
    VIDEO_PATH = reconvertir_video(VIDEO_PATH)
    transcription = transcriber.transcribe(audio_file_path=VIDEO_PATH)

print("[INFO] Transcripción completada.")

# ===========================
# GENERAR CLIPS AUTOMÁTICOS
# ===========================
print("[INFO] Generando clips a partir de la transcripción...")
clipfinder = ClipFinder()
clips = clipfinder.find_clips(transcription=transcription)

clips_info_path = os.path.join(OUTPUT_DIR, "clips_info.txt")
with open(clips_info_path, "w") as f:
    for i, clip in enumerate(clips):
        f.write(f"Clip {i+1} | Start: {clip.start_time} | End: {clip.end_time}\n")

print(f"[INFO] {len(clips)} clips encontrados. Información guardada en {clips_info_path}")

# ===========================
# EXPORTAR CLIPS DE VIDEO
# ===========================
for i, clip in enumerate(clips):
    output_clip_path = os.path.join(OUTPUT_DIR, f"clip_{i+1}.mp4")
    start = str(clip.start_time)
    end = str(clip.end_time)

    print(f"[INFO] Exportando clip {i+1}: {start} - {end} -> {output_clip_path}")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", VIDEO_PATH,
                "-ss", start, "-to", end,
                "-c:v", "libx264",
                "-preset", "slow",
                "-profile:v", "high",
                "-crf", "18",
                "-coder", "1",
                "-pix_fmt", "yuv420p",
                "-g", "30",
                "-bf", "2",
                "-c:a", "aac",
                "-b:a", "384k",
                "-ac", "2",
                "-movflags", "+faststart",
                output_clip_path
            ], check=True
        )
    except subprocess.CalledProcessError:
        print(f"[ERROR] No se pudo exportar el clip {i+1}")

# ===========================
# OPCIONAL: REDIMENSIONAR VIDEO
# ===========================
if PYANNOTE_TOKEN:
    print("[INFO] Redimensionando video...")
    crops = resize(
        video_file_path=VIDEO_PATH,
        pyannote_auth_token=PYANNOTE_TOKEN,
        aspect_ratio=RESIZE_ASPECT_RATIO
    )
    for i, segment in enumerate(crops.segments):
        print(f"Corte {i+1}: {segment.start} - {segment.end}")
    print("[INFO] Redimensionamiento completado.")

print("[INFO] Proceso completado. Clips listos en:", OUTPUT_DIR)
