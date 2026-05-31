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

import cv2
import os

# Carpeta donde tienes tus vídeos
VIDEOS_DIR = "videos"
# Carpeta donde guardarás los frames
OUTPUT_DIR = "frames"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(VIDEOS_DIR):
    if filename.endswith((".mp4", ".avi", ".mkv", ".mov")):
        video_path = os.path.join(VIDEOS_DIR, filename)
        cap = cv2.VideoCapture(video_path)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = 8  # saltar de 8 en 8 frames

        print(f"[+] Procesando {filename} ({total_frames} frames)")

        frame_idx = 0
        saved = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % step == 0:  # guardar solo cada 8 frames
                out_name = f"{os.path.splitext(filename)[0]}_frame{frame_idx}.jpg"
                out_path = os.path.join(OUTPUT_DIR, out_name)
                cv2.imwrite(out_path, frame)
                saved += 1

            frame_idx += 1

        cap.release()
        print(f"    -> {saved} frames guardados")

print("✅ Extracción completada")

