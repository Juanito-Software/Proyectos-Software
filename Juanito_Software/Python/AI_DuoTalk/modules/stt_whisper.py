"""
Módulo de Speech-to-Text usando Whisper
Transcribe audio a texto en español
"""
import whisper
import os
import numpy as np

# Intentar importar librosa primero, si no está disponible usar soundfile
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    try:
        import soundfile as sf
        HAS_SOUNDFILE = True
    except ImportError:
        HAS_SOUNDFILE = False

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

def _load_audio_without_ffmpeg(audio_path):
    """
    Carga audio usando librosa o soundfile para evitar depender de FFmpeg
    
    Args:
        audio_path: Ruta al archivo de audio
    
    Returns:
        numpy.ndarray: Audio cargado como array numpy (16kHz, mono)
    """
    if HAS_LIBROSA:
        # librosa carga audio y lo convierte automáticamente a 16kHz mono
        print(f"[AUDIO] Cargando audio con librosa: {audio_path}")
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        return audio
    elif HAS_SOUNDFILE:
        # soundfile carga el audio, pero necesitamos convertir a 16kHz mono
        print(f"[AUDIO] Cargando audio con soundfile: {audio_path}")
        audio, sr = sf.read(audio_path)
        
        # Convertir a mono si es estéreo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Resamplear a 16kHz si es necesario
        if sr != 16000:
            import scipy.signal
            num_samples = int(len(audio) * 16000 / sr)
            audio = scipy.signal.resample(audio, num_samples)
        
        return audio.astype(np.float32)
    else:
        raise ImportError(
            "Se requiere librosa o soundfile para cargar audio sin FFmpeg. "
            "Instala uno de ellos: pip install librosa o pip install soundfile"
        )

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
    
    # Intentar cargar audio sin FFmpeg primero
    try:
        audio = _load_audio_without_ffmpeg(audio_path)
        # Pasar el audio directamente a Whisper en lugar de la ruta del archivo
        result = model.transcribe(audio, language="es")
    except Exception as e:
        # Si falla, intentar con el método original (requiere FFmpeg)
        print(f"[AVISO] No se pudo cargar audio sin FFmpeg: {e}")
        print("[AVISO] Intentando con método original (requiere FFmpeg)...")
        try:
            result = model.transcribe(audio_path, language="es")
        except FileNotFoundError as ffmpeg_error:
            raise FileNotFoundError(
                f"FFmpeg no está instalado o no está en el PATH. "
                f"Instala FFmpeg desde https://ffmpeg.org/ o instala librosa: pip install librosa"
            ) from ffmpeg_error
    
    text = result["text"].strip()
    print(f"Texto transcrito: {text}")
    return text

