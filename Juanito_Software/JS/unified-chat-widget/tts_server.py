# Copyright (C) 2025 Juanito Software
#
# Este programa está protegido por una Licencia de Uso No Comercial.
# Puedes utilizarlo y compartirlo de forma gratuita, siempre que no se modifique
# y se incluya este aviso completo.
#
# Queda prohibido su uso con fines comerciales, así como su modificación,
# ingeniería inversa o redistribución alterada.
#
# Este software se proporciona “tal cual”, sin garantía de ningún tipo, ya sea
# expresa o implícita, incluyendo, pero no limitado a, garantías de comerciabilidad
# o idoneidad para un propósito particular.
#
# Para más detalles, consulta el archivo LICENSE.txt incluido con este programa
# o contacta a bernaldezperedaj@gmail.com.

from flask import Flask, request, jsonify
from TTS.api import TTS
import os
import time
import simpleaudio as sa
import torch

app = Flask(__name__)

# XTTS v2 soporta clonación de voz a partir de un audio de referencia (speaker_wav).
# Aceptar la licencia CPML de forma no interactiva (requerido por Coqui al cargar XTTS).
os.environ.setdefault("COQUI_TOS_AGREED", "1")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())

# Configurables
BASE_AUDIO_DIR = "audios"
MAX_TEXT_LEN = 500  # seguridad: tamaño máximo aceptado
VOICE_LANGUAGE = "es"
# Carpeta con el audio de referencia de la voz a clonar: se usa el primer
# archivo de audio que haya dentro, sea cual sea su nombre.
VOICES_SELECTED_DIR = os.environ.get("VOICES_SELECTED_DIR", "voices/selected")
AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}

def get_selected_voice_path():
    if not os.path.isdir(VOICES_SELECTED_DIR):
        raise FileNotFoundError(
            f"No existe la carpeta '{VOICES_SELECTED_DIR}'. "
            "Créala y coloca dentro el audio de referencia de la voz a clonar."
        )
    candidates = sorted(
        f for f in os.listdir(VOICES_SELECTED_DIR)
        if os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS
    )
    if not candidates:
        raise FileNotFoundError(
            f"No hay ningún audio de referencia dentro de '{VOICES_SELECTED_DIR}'. "
            f"Coloca ahí un archivo de audio ({', '.join(sorted(AUDIO_EXTENSIONS))})."
        )
    if len(candidates) > 1:
        print(f"⚠️ Hay {len(candidates)} audios en '{VOICES_SELECTED_DIR}'; usando '{candidates[0]}'.")
    return os.path.join(VOICES_SELECTED_DIR, candidates[0])

# Validación temprana: falla al arrancar si aún no hay ningún audio disponible.
get_selected_voice_path()

if not os.path.exists(BASE_AUDIO_DIR):
    os.makedirs(BASE_AUDIO_DIR, exist_ok=True)

def sanitize_input(text):
    if not text:
        return ''
    # Normaliza y elimina control chars problemáticos
    t = str(text).strip()
    t = t.replace('\r', ' ').replace('\n', ' ')
    # elimina etiquetas HTML
    t = ''.join(ch for ch in t if ord(ch) >= 32)  # elimina control chars < 32
    if len(t) > MAX_TEXT_LEN:
        t = t[:MAX_TEXT_LEN] + '...'
    return t

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(silent=True) or {}
    text = sanitize_input(data.get("text", ""))
    if not text:
        return jsonify({"error": "Falta el texto o texto no válido"}), 400

    # Nombre de archivo único para evitar colisiones
    timestamp = int(time.time() * 1000)
    filename = f"output_{timestamp}.wav"
    file_path = os.path.join(BASE_AUDIO_DIR, filename)

    try:
        print(f"🗣️ Hablando: {text}")
        # Guardar wav clonando la voz de referencia seleccionada
        tts.tts_to_file(
            text=text,
            file_path=file_path,
            speaker_wav=get_selected_voice_path(),
            language=VOICE_LANGUAGE,
        )

        # Reproducir con simpleaudio (bloqueante hasta terminar)
        wave_obj = sa.WaveObject.from_wave_file(os.path.abspath(file_path))
        play_obj = wave_obj.play()
        play_obj.wait_done()

        # Intentamos eliminar el archivo (cleanup)
        try:
            os.remove(file_path)
        except Exception:
            # no fatal: sólo log
            print("⚠️ No se pudo borrar el archivo de audio:", file_path)
    except Exception as e:
        print("ERROR TTS:", e)
        # Intenta borrar si existe
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        return jsonify({"error": 'Error interno del servidor'}), 500

    return jsonify({"status": "ok", "text": text}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
