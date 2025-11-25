"""
Lenin - Personalidad: Intelectual calmado y filosófico
Reflexiona y analiza ideas profundamente
"""
from modules.stt_whisper import transcribe
from modules.llm_local import generate_reply
from modules.tts_silero import speak
import os

PERSONALIDAD = """Eres Lenin. Intelectual calmado y filosófico. Simpatizante de la izquierda politica y social.
Reflexiona, analiza ideas profundamente. Mantén un tono sereno y pensativo.
Responde de forma más elaborada y reflexiva que Franco.
Mantén tus respuestas concisas (máximo 3-4 frases) pero con profundidad.
Usa un lenguaje más elevado y analítico."""

PERSONALIDAD_DEBATE = """Eres Lenin. Intelectual calmado y filosófico. Simpatizante de la izquierda politica y social.
Estás en un debate. Puedes:
- Hablar sobre lo que dijo Franco
- Darle la razón si estás de acuerdo
- Argumentar en contra si no estás de acuerdo
Reflexiona, analiza ideas profundamente. Mantén un tono sereno y pensativo.
Responde de forma más elaborada y reflexiva que Franco.
Mantén tus respuestas concisas (máximo 3-4 frases) pero con profundidad.
Usa un lenguaje más elevado y analítico."""

def agentB_process(audio_path):
    """
    Procesa el audio del usuario y genera una respuesta de Lenin
    
    Args:
        audio_path: Ruta al archivo de audio del usuario
    
    Returns:
        str: Respuesta generada por el agente
    """
    try:
        print("\n" + "="*50)
        print("LENIN - Procesando...")
        print("="*50)
        
        # 1. Transcribir audio a texto
        text = transcribe(audio_path)
        
        if not text or not text.strip():
            print("No se pudo transcribir el audio o está vacío")
            return ""
        
        # 2. Generar prompt con personalidad
        prompt = f"{PERSONALIDAD}\n\nUsuario: {text}\n\nLenin:"
        
        # 3. Generar respuesta con LLM
        # Reducido a 250 tokens para evitar textos demasiado largos para el TTS
        response = generate_reply(prompt, max_tokens=250, temperature=0.7)
        
        if not response or not response.strip():
            print("No se pudo generar respuesta")
            return ""
        
        # 4. Convertir respuesta a voz
        print("\nLenin hablando...")
        speak(response)
        
        return response
        
    except Exception as e:
        print(f"Error en agentB_process: {e}")
        import traceback
        traceback.print_exc()
        return ""

def agentB_process_text(text, is_debate=False):
    """
    Procesa texto directamente y genera una respuesta de Lenin (sin audio)
    
    Args:
        text: Texto del usuario
        is_debate: Si True, usa personalidad de debate (puede debatir con Franco)
    
    Returns:
        str: Respuesta generada por el agente
    """
    try:
        print("\n" + "="*50)
        print("LENIN - Procesando texto...")
        print("="*50)
        
        if not text or not text.strip():
            print("Texto vacío")
            return ""
        
        # Elegir personalidad según el modo
        personalidad = PERSONALIDAD_DEBATE if is_debate else PERSONALIDAD
        
        # Generar prompt con personalidad
        prompt = f"{personalidad}\n\nUsuario: {text}\n\nLenin:"
        
        # Generar respuesta con LLM
        # Reducido a 250 tokens para evitar textos demasiado largos para el TTS
        response = generate_reply(prompt, max_tokens=250, temperature=0.7)
        
        if not response or not response.strip():
            print("No se pudo generar respuesta")
            return ""
        
        # Convertir respuesta a voz
        print("\nLenin hablando...")
        speak(response)
        
        return response
        
    except Exception as e:
        print(f"Error en agentB_process_text: {e}")
        import traceback
        traceback.print_exc()
        return ""

