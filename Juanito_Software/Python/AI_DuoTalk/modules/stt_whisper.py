"""
Módulo de Speech-to-Text usando Whisper
Transcribe audio a texto en español
"""
import whisper
import os

# Cargar modelo una vez al importar el módulo
_model = None

def get_model():
    """Carga el modelo Whisper (small) de forma lazy"""
    global _model
    if _model is None:
        print("Cargando modelo Whisper 'small'...")
        _model = whisper.load_model("small")
        print("Modelo Whisper cargado correctamente")
    return _model

def transcribe(audio_path):
    """
    Transcribe un archivo de audio a texto en español
    
    Args:
        audio_path: Ruta al archivo de audio (.wav, .mp3, etc.)
    
    Returns:
        str: Texto transcrito
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"El archivo de audio no existe: {audio_path}")
    
    model = get_model()
    print(f"Transcribiendo audio: {audio_path}")
    result = model.transcribe(audio_path, language="es")
    text = result["text"].strip()
    print(f"Texto transcrito: {text}")
    return text

