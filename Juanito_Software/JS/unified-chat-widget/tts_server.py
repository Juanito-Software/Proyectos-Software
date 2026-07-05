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

app = Flask(__name__)

# Cargar el modelo (elige uno en español)
tts = TTS(model_name="tts_models/es/css10/vits")

# Configurables
BASE_AUDIO_DIR = "audios"
MAX_TEXT_LEN = 500  # seguridad: tamaño máximo aceptado

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
        # Guardar wav
        tts.tts_to_file(text=text, file_path=file_path)

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
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok", "text": text}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
