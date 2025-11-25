"""
Script de prueba para verificar que todas las importaciones funcionan correctamente
"""
import sys

def test_imports():
    """Prueba todas las importaciones necesarias"""
    print("Probando importaciones...")
    
    try:
        print("  [1/5] Probando Whisper...")
        from modules.stt_whisper import transcribe
        print("       OK - Whisper importado correctamente")
    except Exception as e:
        print(f"       ERROR - Whisper: {e}")
        return False
    
    try:
        print("  [2/5] Probando GPT4All...")
        from modules.llm_local import generate_reply
        print("       OK - GPT4All importado correctamente")
    except Exception as e:
        print(f"       ERROR - GPT4All: {e}")
        return False
    
    try:
        print("  [3/5] Probando Silero TTS...")
        from modules.tts_silero import speak
        print("       OK - Silero TTS importado correctamente")
    except Exception as e:
        print(f"       ERROR - Silero TTS: {e}")
        return False
    
    try:
        print("  [4/5] Probando Franco...")
        from agents.agent_A import agentA_process
        print("       OK - Franco importado correctamente")
    except Exception as e:
        print(f"       ERROR - Franco: {e}")
        return False
    
    try:
        print("  [5/5] Probando Lenin...")
        from agents.agent_B import agentB_process
        print("       OK - Lenin importado correctamente")
    except Exception as e:
        print(f"       ERROR - Lenin: {e}")
        return False
    
    print("\n[SUCCESS] Todas las importaciones funcionan correctamente!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

