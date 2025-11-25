"""
Módulo de Text-to-Speech usando Silero
Convierte texto a voz en español
"""
import torch
import sounddevice as sd
import numpy as np
import time
import re

# Modelo global para reutilización
_model = None
_speaker = None
_sample_rate = None

def get_model():
    """Carga el modelo Silero TTS de forma lazy"""
    global _model, _speaker, _sample_rate
    
    if _model is None:
        print("Cargando modelo Silero TTS...")
        try:
            # Cargar modelo Silero TTS v3 para español
            _model, _sample_rate = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='es',
                speaker='v3_es'
            )
            # Usar el primer speaker disponible
            _speaker = 'es_0'  # Puedes cambiar esto según el speaker que prefieras
            print("Modelo Silero TTS cargado correctamente")
        except Exception as e:
            print(f"Error al cargar modelo Silero: {e}")
            print("Intentando cargar modelo alternativo...")
            # Fallback: cargar modelo básico
            _model, _sample_rate = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='es'
            )
            _speaker = 'es_0'
            print("Modelo Silero TTS cargado (modo alternativo)")
    
    return _model, _speaker, _sample_rate

def _split_text_into_chunks(text, max_chars=800):
    """
    Divide el texto en chunks razonables para evitar exceder los límites del TTS
    
    Args:
        text: Texto a dividir
        max_chars: Número máximo de caracteres por chunk
    
    Returns:
        list: Lista de chunks de texto
    """
    if not text or not text.strip():
        return []
    
    # Dividir por oraciones (manteniendo signos de puntuación)
    sentences = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Si la oración sola es más grande que max_chars, dividirla por palabras
        if len(sentence) > max_chars:
            # Si hay un chunk acumulado, guardarlo primero
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # Dividir la oración larga por palabras
            words = sentence.split()
            temp = ""
            for word in words:
                if len(temp) + len(word) + 1 <= max_chars:
                    temp = (temp + " " + word).strip()
                else:
                    if temp:
                        chunks.append(temp)
                    temp = word
            if temp:
                current_chunk = temp
        else:
            # Verificar si podemos agregar esta oración al chunk actual
            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                current_chunk = (current_chunk + " " + sentence).strip()
            else:
                # Guardar el chunk actual y empezar uno nuevo
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
    
    # Agregar el último chunk si existe
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def speak(text, speaker_id='es_0', sample_rate=48000):
    """
    Convierte texto a voz y lo reproduce
    Divide el texto en chunks si es muy largo para evitar errores del modelo TTS
    
    Args:
        text: Texto a convertir a voz
        speaker_id: ID del speaker a usar (por defecto 'es_0')
        sample_rate: Tasa de muestreo del audio (por defecto 48000)
    """
    if not text or not text.strip():
        print("Texto vacío, no se reproduce audio")
        return
    
    model, default_speaker, default_sample_rate = get_model()
    
    # Usar el speaker por defecto si no se especifica otro
    if speaker_id is None:
        speaker_id = default_speaker
    
    # Verificar si el texto es demasiado largo (más de 1000 caracteres)
    # Si es así, dividirlo en chunks
    if len(text) > 1000:
        print(f"[TTS] Texto largo detectado ({len(text)} caracteres). Dividiendo en chunks...")
        chunks = _split_text_into_chunks(text, max_chars=800)
        
        if not chunks:
            print("[TTS] No se pudieron generar chunks válidos")
            return
        
        print(f"[TTS] Texto dividido en {len(chunks)} chunks")
        
        # Generar audio para cada chunk y concatenar
        audio_list = []
        for idx, chunk in enumerate(chunks):
            try:
                print(f"[TTS] Procesando chunk {idx + 1}/{len(chunks)}: {chunk[:50]}...")
                audio_chunk = model.apply_tts(
                    text=chunk,
                    speaker=speaker_id,
                    sample_rate=sample_rate
                )
                
                # Convertir a numpy array si es necesario
                if isinstance(audio_chunk, torch.Tensor):
                    audio_chunk = audio_chunk.cpu().numpy()
                
                # Asegurar que es un array 1D
                if len(audio_chunk.shape) > 1:
                    audio_chunk = audio_chunk.flatten()
                
                audio_list.append(audio_chunk)
                
                # Pequeña pausa entre chunks para mejor fluidez
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[TTS] Error al procesar chunk {idx + 1}: {e}")
                # Intentar con un chunk más corto
                if len(chunk) > 400:
                    try:
                        short_chunk = chunk[:400].rsplit(' ', 1)[0] + '...'
                        print(f"[TTS] Intentando con chunk reducido: {short_chunk[:50]}...")
                        audio_chunk = model.apply_tts(
                            text=short_chunk,
                            speaker=speaker_id,
                            sample_rate=sample_rate
                        )
                        if isinstance(audio_chunk, torch.Tensor):
                            audio_chunk = audio_chunk.cpu().numpy()
                        if len(audio_chunk.shape) > 1:
                            audio_chunk = audio_chunk.flatten()
                        audio_list.append(audio_chunk)
                    except Exception as e2:
                        print(f"[TTS] Error incluso con chunk reducido: {e2}")
                        continue
                else:
                    continue
        
        if not audio_list:
            print("[TTS] No se pudo generar audio para ningún chunk")
            raise Exception("TTS: no se generó audio para ningún chunk")
        
        # Concatenar todos los audios
        print(f"[TTS] Concatenando {len(audio_list)} chunks de audio...")
        full_audio = np.concatenate(audio_list, axis=0)
        
        print(f"[TTS] Reproduciendo audio completo ({len(full_audio)/sample_rate:.2f} segundos)...")
        
        # Reproducir audio completo
        sd.play(full_audio, sample_rate)
        sd.wait()  # Esperar a que termine la reproducción
        
        print("[TTS] Audio reproducido correctamente")
        
    else:
        # Texto corto, procesamiento normal
        print(f"[TTS] Generando audio para: {text[:50]}...")
        
        try:
            # Generar audio usando el modelo
            audio = model.apply_tts(
                text=text,
                speaker=speaker_id,
                sample_rate=sample_rate
            )
            
            # Convertir a numpy array si es necesario
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            
            # Asegurar que es un array 1D
            if len(audio.shape) > 1:
                audio = audio.flatten()
            
            print(f"[TTS] Reproduciendo audio ({len(audio)/sample_rate:.2f} segundos)...")
            
            # Reproducir audio
            sd.play(audio, sample_rate)
            sd.wait()  # Esperar a que termine la reproducción
            
            print("[TTS] Audio reproducido correctamente")
            
        except Exception as e:
            print(f"[TTS] Error al generar o reproducir audio: {e}")
            # Si falla con texto corto, intentar dividirlo también
            if "too long" in str(e).lower() or len(text) > 500:
                print("[TTS] Intentando dividir el texto aunque sea corto...")
                chunks = _split_text_into_chunks(text, max_chars=400)
                if chunks:
                    audio_list = []
                    for chunk in chunks:
                        try:
                            audio_chunk = model.apply_tts(
                                text=chunk,
                                speaker=speaker_id,
                                sample_rate=sample_rate
                            )
                            if isinstance(audio_chunk, torch.Tensor):
                                audio_chunk = audio_chunk.cpu().numpy()
                            if len(audio_chunk.shape) > 1:
                                audio_chunk = audio_chunk.flatten()
                            audio_list.append(audio_chunk)
                            time.sleep(0.1)
                        except:
                            continue
                    if audio_list:
                        full_audio = np.concatenate(audio_list, axis=0)
                        sd.play(full_audio, sample_rate)
                        sd.wait()
                        print("[TTS] Audio reproducido correctamente (modo chunking)")
                        return
            raise

def save_audio(text, output_path, speaker_id='es_0', sample_rate=48000):
    """
    Convierte texto a voz y lo guarda en un archivo
    
    Args:
        text: Texto a convertir a voz
        output_path: Ruta donde guardar el archivo de audio
        speaker_id: ID del speaker a usar
        sample_rate: Tasa de muestreo del audio
    """
    if not text or not text.strip():
        print("Texto vacío, no se genera audio")
        return
    
    model, default_speaker, default_sample_rate = get_model()
    
    if speaker_id is None:
        speaker_id = default_speaker
    
    print(f"Generando y guardando audio para: {text[:50]}...")
    
    try:
        audio = model.apply_tts(
            text=text,
            speaker=speaker_id,
            sample_rate=sample_rate
        )
        
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()
        
        if len(audio.shape) > 1:
            audio = audio.flatten()
        
        # Guardar usando soundfile o scipy
        try:
            import soundfile as sf
            sf.write(output_path, audio, sample_rate)
            print(f"Audio guardado en: {output_path}")
        except ImportError:
            # Fallback usando scipy
            from scipy.io import wavfile
            wavfile.write(output_path, sample_rate, audio)
            print(f"Audio guardado en: {output_path}")
            
    except Exception as e:
        print(f"Error al generar o guardar audio: {e}")
        raise

