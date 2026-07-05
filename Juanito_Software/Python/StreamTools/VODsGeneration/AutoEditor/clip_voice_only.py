import sys
if getattr(sys, 'frozen', False):
    import os
    dll_path = os.path.join(sys._MEIPASS, 'libsndfile_x64.dll')
    os.environ['PATH'] = os.pathsep.join([dll_path, os.environ.get('PATH', '')])
import subprocess
import torch
import whisper
import soundfile as sf
import json
import subprocess
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import soundfile as sf

import ffmpeg

# ---------- CONFIG ----------
WHISPER_MODEL = "medium"
WHISPER_FP16 = False
WHISPER_SR = 16000
PAD_SECONDS = 0.15
MERGE_GAP = 0.3
TEMP_AUDIO_NAME = "temp_audio.wav"
OUTPUT_JSON = "voice_segments.json"
OUTPUT_VIDEO = "output.mp4"
MAX_SEGMENTS_PER_CHUNK = 50  # puedes ajustar según tu número de segmentos
AUDIO_BITRATE = "640k"
# ----------------------------

def seleccionar_video():
    root = tk.Tk()
    root.withdraw()          # Oculta la ventana principal
    root.update()            # Actualiza la GUI para que Windows reconozca la ventana oculta
    archivo = filedialog.askopenfilename(
        title="Selecciona un archivo de vídeo",
        filetypes=[("Archivos de vídeo", "*.mp4;*.avi;*.mov;*.mkv")]
    )
    root.destroy()           # Destruye la ventana principal al finalizar
    return archivo


def merge_and_pad_segments(raw_segments, audio_duration, pad=PAD_SECONDS, merge_gap=MERGE_GAP):
    if not raw_segments:
        return []
    segs = sorted([(float(s), float(e)) for s, e in raw_segments], key=lambda x: x[0])
    merged = []
    cur_s, cur_e = segs[0]
    for s, e in segs[1:]:
        if s - cur_e <= merge_gap:
            cur_e = max(cur_e, e)
        else:
            merged.append((max(0.0, cur_s - pad), min(audio_duration, cur_e + pad)))
            cur_s, cur_e = s, e
    merged.append((max(0.0, cur_s - pad), min(audio_duration, cur_e + pad)))
    return merged

def obtener_segmentos_whisper(audio_path, model_name=WHISPER_MODEL, fp16=WHISPER_FP16):
    use_cuda = torch.cuda.is_available()
    if not use_cuda and fp16:
        fp16 = False

    print(f"🔎 Cargando Whisper '{model_name}' (gpu={use_cuda}, fp16={fp16})...")
    model = whisper.load_model(model_name)

    print("🗣️ Transcribiendo y detectando voz con Whisper...")
    result = model.transcribe(audio_path, language="es", fp16=fp16, verbose=False)
    raw_segments = [(seg["start"], seg["end"]) for seg in result.get("segments", [])]

    try:
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe["format"]["duration"])
    except Exception:
        audio_duration = 1e9

    return merge_and_pad_segments(raw_segments, audio_duration)

def check_auto_editor():
    return shutil.which("auto-editor") is not None

def run_auto_editor_keep_list(input_video, segments, output_video):
    if not segments:
        return

    # Filtrar segmentos muy cortos
    segments = [(s, e) for s, e in segments if e - s > 0.5]

    tmp_dir = tempfile.mkdtemp(prefix="ae_chunks_")
    chunk_outputs = []

    for idx in range(0, len(segments), MAX_SEGMENTS_PER_CHUNK):
        chunk = segments[idx:idx + MAX_SEGMENTS_PER_CHUNK]
        chunk_output = os.path.join(tmp_dir, f"chunk_{idx//MAX_SEGMENTS_PER_CHUNK:03d}.mp4")
        cmd = ["auto-editor", input_video, "--cut-out"]

        for start, end in chunk:
            cmd.extend(["--time-range", f"{start:.3f}-{end:.3f}"])

        cmd.extend([
            "--output", chunk_output,
            "--video_codec", "libx264",
            "--audio_codec", "aac",
            "--audio_bitrate", AUDIO_BITRATE,
            "--audio_sample_rate", "48000",
            "--no-open"
        ])

        subprocess.run(cmd, check=True)
        chunk_outputs.append(chunk_output)

    if len(chunk_outputs) > 1:
        list_path = os.path.join(tmp_dir, "concat_list.txt")
        with open(list_path, "w", encoding="utf-8") as f:
            for p in chunk_outputs:
                safe_p = p.replace("\\", "/")
                f.write(f"file '{safe_p}'\n")
        (
            ffmpeg
            .input(list_path, format="concat", safe=0)
            .output(
                output_video,
                vcodec="libx264",
                acodec="aac",
                audio_bitrate=AUDIO_BITRATE,
                ar="48000",
                ac=2,
                pix_fmt="yuv420p",
                movflags="+faststart"
            )
            .overwrite_output()
            .run(quiet=True)
        )
    else:
        shutil.move(chunk_outputs[0], output_video)

    shutil.rmtree(tmp_dir)

def ffmpeg_concat_segments(input_video, segments, output_video, tmp_dir):
    seg_files = []
    for i, (start, end) in enumerate(segments):
        seg_path = os.path.join(tmp_dir, f"seg_{i:04d}.mp4")
        (
            ffmpeg
            .input(input_video, ss=start, to=end)
            .output(
                seg_path,
                vcodec="libx264",
                acodec="aac",
                audio_bitrate=AUDIO_BITRATE,
                ar="48000",
                ac=2,
                pix_fmt="yuv420p",
                preset="fast",
                movflags="+faststart",
                format="mp4"
            )
            .overwrite_output()
            .run(quiet=True)
        )
        seg_files.append(seg_path)

    list_path = os.path.join(tmp_dir, "concat_list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for p in seg_files:
            safe_p = p.replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    (
        ffmpeg
        .input(list_path, format="concat", safe=0)
        .output(
            output_video,
            vcodec="libx264",
            acodec="aac",
            audio_bitrate=AUDIO_BITRATE,
            ar="48000",
            ac=2,
            pix_fmt="yuv420p",
            movflags="+faststart"
        )
        .overwrite_output()
        .run(quiet=True)
    )

def main():
    print("Seleccione un video para recortar las partes con voz")
    INPUT_VIDEO = seleccionar_video()
    if not INPUT_VIDEO:
        messagebox.showerror("Error", "No se seleccionó ningún archivo de vídeo.")
        return

    tmp_dir = tempfile.mkdtemp(prefix="clipvo_")
    AUDIO_WAV = os.path.join(tmp_dir, TEMP_AUDIO_NAME)
    output_json = os.path.join(os.getcwd(), OUTPUT_JSON)
    OUTPUT_VIDEO_PATH = os.path.join(os.getcwd(), OUTPUT_VIDEO)

    try:
        print("🎧 Extrayendo audio temporal (mono, 16 kHz) para ASR...")
        (
            ffmpeg
            .input(INPUT_VIDEO)
            .output(AUDIO_WAV, ac=1, ar=WHISPER_SR)
            .overwrite_output()
            .run(quiet=True)
        )

        print("🗣️ Detectando voz con Whisper...")
        segments = obtener_segmentos_whisper(AUDIO_WAV)
        if not segments:
            messagebox.showwarning("Advertencia", "No se detectó voz en el audio.")
            return

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)

        print("✂️ Generando video final listo para YouTube (estéreo 48 kHz)...")
        if check_auto_editor():
            run_auto_editor_keep_list(INPUT_VIDEO, segments, OUTPUT_VIDEO_PATH)
        else:
            print("⚠️ auto-editor no está instalado: usando fallback con ffmpeg (más lento).")
            ffmpeg_concat_segments(INPUT_VIDEO, segments, OUTPUT_VIDEO_PATH, tmp_dir)

        messagebox.showinfo("Listo", f"✅ Video generado: {OUTPUT_VIDEO_PATH}\nSegmentos guardados en: {output_json}")
        print(f"✅ Video generado: {OUTPUT_VIDEO_PATH}")

    finally:
        try:
            if os.path.exists(AUDIO_WAV):
                os.remove(AUDIO_WAV)
            shutil.rmtree(tmp_dir)
        except Exception:
            pass

if __name__ == "__main__":
    main()
