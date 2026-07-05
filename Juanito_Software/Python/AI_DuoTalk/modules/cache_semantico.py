"""
Sistema de caché semántico para respuestas similares
Reduce latencia al reutilizar respuestas de preguntas parecidas
"""
import hashlib
import json
import os
from typing import Optional, Dict, Tuple
import time

# Archivo de caché
CACHE_FILE = "cache_semantico.json"
CACHE_MAX_SIZE = 100  # Máximo número de entradas en caché
CACHE_EXPIRY_DAYS = 7  # Días hasta que expire una entrada

_cache_data: Optional[Dict] = None

def _load_cache():
    """Carga el caché desde el archivo"""
    global _cache_data
    if _cache_data is not None:
        return _cache_data
    
    _cache_data = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                _cache_data = json.load(f)
            # Limpiar entradas expiradas
            current_time = time.time()
            expired_keys = []
            for key, value in _cache_data.items():
                if 'timestamp' in value:
                    age_days = (current_time - value['timestamp']) / (24 * 3600)
                    if age_days > CACHE_EXPIRY_DAYS:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del _cache_data[key]
            
            if expired_keys:
                _save_cache()
        except Exception as e:
            print(f"[CACHE] Error al cargar caché: {e}")
            _cache_data = {}
    
    return _cache_data

def _save_cache():
    """Guarda el caché en el archivo"""
    global _cache_data
    if _cache_data is None:
        return
    
    try:
        # Limitar tamaño del caché
        if len(_cache_data) > CACHE_MAX_SIZE:
            # Eliminar las entradas más antiguas
            sorted_items = sorted(
                _cache_data.items(),
                key=lambda x: x[1].get('timestamp', 0)
            )
            items_to_keep = sorted_items[-CACHE_MAX_SIZE:]
            _cache_data = dict(items_to_keep)
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[CACHE] Error al guardar caché: {e}")

def _normalize_text(text: str) -> str:
    """Normaliza el texto para comparación semántica básica"""
    # Convertir a minúsculas, eliminar espacios extra, signos de puntuación
    text = text.lower().strip()
    # Eliminar signos de puntuación comunes
    import string
    text = ''.join(c for c in text if c not in string.punctuation)
    # Normalizar espacios
    text = ' '.join(text.split())
    return text

def _get_cache_key(text: str) -> str:
    """Genera una clave de caché basada en el hash del texto normalizado"""
    normalized = _normalize_text(text)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def get_cached_response(text: str) -> Optional[str]:
    """
    Busca una respuesta en caché para un texto similar
    
    Args:
        text: Texto de entrada
    
    Returns:
        Respuesta en caché si existe, None si no
    """
    cache = _load_cache()
    key = _get_cache_key(text)
    
    if key in cache:
        entry = cache[key]
        # Verificar que la entrada original sea similar (similitud básica)
        original_normalized = _normalize_text(entry.get('original_text', ''))
        current_normalized = _normalize_text(text)
        
        # Comparación simple: si los textos normalizados son muy similares
        # (más del 80% de palabras en común), usar la respuesta en caché
        original_words = set(original_normalized.split())
        current_words = set(current_normalized.split())
        
        if original_words and current_words:
            similarity = len(original_words & current_words) / len(original_words | current_words)
            if similarity > 0.7:  # 70% de similitud
                print(f"[CACHE] Respuesta encontrada en caché (similitud: {similarity:.2%})")
                return entry.get('response')
    
    return None

def save_response(text: str, response: str):
    """
    Guarda una respuesta en caché
    
    Args:
        text: Texto de entrada original
        response: Respuesta generada
    """
    cache = _load_cache()
    key = _get_cache_key(text)
    
    cache[key] = {
        'original_text': text,
        'response': response,
        'timestamp': time.time()
    }
    
    _save_cache()
    print(f"[CACHE] Respuesta guardada en caché")

def clear_cache():
    """Limpia todo el caché"""
    global _cache_data
    _cache_data = {}
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    print("[CACHE] Caché limpiado")

