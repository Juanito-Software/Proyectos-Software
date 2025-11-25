"""
Franco - Personalidad: Experto en política y actualidad
Habla de forma directa, crítica y sin filtros
"""
from modules.stt_whisper import transcribe
from modules.llm_local import generate_reply
from modules.tts_silero import speak
import os

PERSONALIDAD = """Eres Franco. Experto en política y actualidad. Simpatizante de la derecha politica y social.
Sé directo, crítico y sin filtros. Responde de forma contundente y polémica.
Mantén tus respuestas concisas (máximo 3-4 frases) y directas al grano.
No uses lenguaje formal, habla como en un debate televisivo."""

PERSONALIDAD_DEBATE = """Eres Franco. Experto en política y actualidad. Simpatizante de la derecha politica y social.
Estás en un debate. Puedes:
- Hablar sobre lo que dijo Lenin
- Darle la razón si estás de acuerdo
- Argumentar en contra si no estás de acuerdo
Sé directo, crítico y sin filtros. Responde de forma contundente y polémica.
Mantén tus respuestas concisas (máximo 3-4 frases) y directas al grano.
No uses lenguaje formal, habla como en un debate televisivo."""

def agentA_process(audio_path):
    """
    Procesa el audio del usuario y genera una respuesta de Franco
    
    Args:
        audio_path: Ruta al archivo de audio del usuario
    
    Returns:
        str: Respuesta generada por el agente
    """
    try:
        print("\n" + "="*50)
        print("FRANCO - Procesando...")
        print("="*50)
        
        # 1. Transcribir audio a texto
        text = transcribe(audio_path)
        
        if not text or not text.strip():
            print("No se pudo transcribir el audio o está vacío")
            return ""
        
        # 2. Generar prompt con personalidad
        prompt = f"{PERSONALIDAD}\n\nUsuario: {text}\n\nFranco:"
        
        # 3. Generar respuesta con LLM
        # Reducido a 250 tokens para evitar textos demasiado largos para el TTS
        response = generate_reply(prompt, max_tokens=250, temperature=0.8)
        
        if not response or not response.strip():
            print("No se pudo generar respuesta")
            return ""
        
        # 4. Convertir respuesta a voz
        print("\nFranco hablando...")
        speak(response)
        
        return response
        
    except Exception as e:
        print(f"Error en agentA_process: {e}")
        import traceback
        traceback.print_exc()
        return ""

def agentA_process_text(text, is_debate=False):
    """
    Procesa texto directamente y genera una respuesta de Franco (sin audio)
    
    Args:
        text: Texto del usuario
        is_debate: Si True, usa personalidad de debate (puede debatir con Lenin)
    
    Returns:
        str: Respuesta generada por el agente
    """
    try:
        print("\n" + "="*50)
        print("FRANCO - Procesando texto...")
        print("="*50)
        
        if not text or not text.strip():
            print("Texto vacío")
            return ""
        
        # Elegir personalidad según el modo
        personalidad = PERSONALIDAD_DEBATE if is_debate else PERSONALIDAD
        
        # Generar prompt con personalidad
        prompt = f"{personalidad}\n\nUsuario: {text}\n\nFranco:"
        
        # Generar respuesta con LLM
        # Reducido a 250 tokens para evitar textos demasiado largos para el TTS
        response = generate_reply(prompt, max_tokens=250, temperature=0.8)
        
        if not response or not response.strip():
            print("No se pudo generar respuesta")
            return ""
        
        # Convertir respuesta a voz
        print("\nFranco hablando...")
        speak(response)
        
        return response
        
    except Exception as e:
        print(f"Error en agentA_process_text: {e}")
        import traceback
        traceback.print_exc()
        return ""

