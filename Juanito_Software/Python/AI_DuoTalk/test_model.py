"""
Script de prueba para verificar que el modelo GPT4All funciona
"""
import sys

def test_model():
    """Prueba la carga y uso del modelo"""
    print("="*70)
    print("  PRUEBA DE MODELO GPT4All")
    print("="*70)
    print()
    
    try:
        print("[1/3] Importando módulo LLM...")
        from modules.llm_local import generate_reply
        print("    OK - Módulo importado")
        
        print("\n[2/3] Cargando modelo (esto puede tardar la primera vez)...")
        print("    [AVISO] Si es la primera vez, se descargará ~4.6GB")
        print("    [AVISO] Esto puede tardar varios minutos...")
        
        # Probar con un prompt simple
        test_prompt = "Eres un asistente útil. Responde brevemente: ¿Qué es Python?"
        
        print("\n[3/3] Generando respuesta de prueba...")
        response = generate_reply(test_prompt, max_tokens=50, temperature=0.7)
        
        if response:
            print("\n" + "="*70)
            print("  PRUEBA EXITOSA")
            print("="*70)
            print(f"\nRespuesta del modelo: {response}")
            print("\n[OK] El modelo funciona correctamente!")
            return True
        else:
            print("\n[ERROR] El modelo no generó respuesta")
            return False
            
    except Exception as e:
        print("\n" + "="*70)
        print("  ERROR EN LA PRUEBA")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model()
    sys.exit(0 if success else 1)

