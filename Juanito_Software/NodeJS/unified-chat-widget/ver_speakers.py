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

from TTS.api import TTS

model_name = "tts_models/es/css10/vits"

# Carga el modelo
tts = TTS(model_name=model_name)

# Intenta acceder a los altavoces de forma segura
try:
    # En xtts, los altavoces están en tts.speaker_manager.speakers (diccionario)
    speakers = getattr(tts, "speaker_manager", None)
    if speakers is not None:
        speaker_dict = speakers.speakers  # es un diccionario {id: embedding}
        print("Altavoces disponibles (ids):")
        for speaker_id in speaker_dict.keys():
            print(f" - {speaker_id}")
    else:
        print("No se encontró el gestor de altavoces en el modelo.")
except Exception as e:
    print(f"Error accediendo a altavoces: {e}")
