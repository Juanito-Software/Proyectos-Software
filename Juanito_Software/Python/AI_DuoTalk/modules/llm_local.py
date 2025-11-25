"""
Módulo de LLM local usando GPT4All
Genera respuestas usando modelos locales
"""
from gpt4all import GPT4All
import os

# Modelo global para reutilización
_model = None

def get_model():
    """Carga el modelo GPT4All de forma lazy"""
    global _model
    if _model is None:
        print("Cargando modelo GPT4All 'Meta-Llama-3-8B-Instruct.Q4_0'...")
        print("[AVISO] Si es la primera vez, el modelo se descargará automáticamente (~4.6GB)")
        print("[AVISO] Esto puede tardar varios minutos...")
        # El modelo se descargará automáticamente si no existe
        # Usamos Llama 3 que es un modelo estable y bien soportado
        _model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", allow_download=True, verbose=True)
        print("Modelo GPT4All cargado correctamente")
    return _model

def generate_reply(prompt, max_tokens=200, temperature=0.7):
    """
    Genera una respuesta usando el LLM local
    
    Args:
        prompt: Texto de entrada para el modelo
        max_tokens: Número máximo de tokens a generar
        temperature: Temperatura para la generación (0.0-1.0)
    
    Returns:
        str: Respuesta generada por el modelo
    """
    model = get_model()
    print(f"Generando respuesta con LLM (máximo {max_tokens} tokens)...")
    
    # Usar generate con contexto
    # Asegurar que se generen respuestas completas
    response = model.generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temp=temperature,
        top_k=40,
        top_p=0.9,
        repeat_penalty=1.1
    )
    
    # Limpiar la respuesta
    response = response.strip()
    
    # Verificar que la respuesta no esté cortada
    # Si la respuesta termina abruptamente, podría estar cortada
    if len(response) > 0:
        # Contar palabras aproximadas (1 token ≈ 0.75 palabras en español)
        palabras_aprox = len(response.split())
        tokens_aprox = palabras_aprox / 0.75
        print(f"Respuesta generada: {palabras_aprox} palabras (~{int(tokens_aprox)} tokens)")
        print(f"Vista previa: {response[:150]}...")
        
        # Si la respuesta es muy corta comparada con max_tokens, advertir
        if tokens_aprox < max_tokens * 0.3:
            print(f"[AVISO] La respuesta parece corta. Puede que el modelo se haya detenido antes de tiempo.")
    else:
        print("[AVISO] Respuesta vacía generada")
    
    return response

