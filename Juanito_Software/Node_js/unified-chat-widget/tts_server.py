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

from flask import Flask, request
from TTS.api import TTS
import os
import time
from playsound import playsound

app = Flask(__name__)

# Cargar el modelo (elige uno en español)
tts = TTS(model_name="tts_models/es/css10/vits")

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return {"error": "Falta el texto"}, 400

    base_path = "audios"
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    file_path = os.path.join(base_path, "output.wav")

    # Intentar borrar el archivo si existe
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError:
            # Si está en uso, crear un archivo con timestamp para evitar colisiones
            timestamp = int(time.time() * 1000)
            file_path = os.path.join(base_path, f"output_{timestamp}.wav")

    print(f"🗣️ Hablando: {text}")

    try:
        # Guardar el archivo de audio
        tts.tts_to_file(text=text, file_path=file_path)
        
        # Normalizar ruta absoluta y con barras normales
        abs_path = os.path.abspath(file_path)

        # Reproducir audio
        playsound(abs_path)
    except Exception as e:
        return {"error": str(e)}, 500

    return {"status": "ok", "text": text}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
