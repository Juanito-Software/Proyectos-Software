# Copyright (C) 2025 Juanito Software
#
# Script para actualizar automáticamente las variables de Rumble en .env
# antes de cada directo

import os
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

def update_rumble_env(api_url=None, channel=None):
    """
    Actualiza las variables de Rumble en el archivo .env
    
    Args:
        api_url: URL de la API de Rumble (opcional)
        channel: Nombre del canal de Rumble (opcional)
    """
    # Buscar el archivo .env
    env_path = find_dotenv()
    
    if not env_path:
        # Si no existe, crear uno en el directorio raíz del proyecto
        project_root = Path(__file__).parent.parent
        env_path = project_root / '.env'
        if not env_path.exists():
            env_path.touch()
    
    # Cargar variables existentes
    load_dotenv(env_path)
    
    updated = False
    
    # Actualizar RUMBLE_API_URL si se proporciona
    if api_url:
        set_key(env_path, 'RUMBLE_API_URL', api_url)
        print(f"✅ Actualizado RUMBLE_API_URL: {api_url}")
        updated = True
    
    # Actualizar RUMBLE_CHANNEL si se proporciona
    if channel:
        set_key(env_path, 'RUMBLE_CHANNEL', channel)
        print(f"✅ Actualizado RUMBLE_CHANNEL: {channel}")
        updated = True
    
    if not updated:
        print("ℹ️ No se proporcionaron valores para actualizar")
        print("Uso: python update_rumble_env.py --api-url <URL> --channel <CANAL>")
    else:
        print(f"✅ Archivo .env actualizado: {env_path}")
    
    return updated

def auto_detect_rumble_stream():
    """
    Intenta detectar automáticamente el stream activo de Rumble
    Nota: Esto requiere que cocorum esté instalado y configurado
    """
    try:
        from cocorum import RumbleAPI
        
        # Intentar obtener desde .env
        load_dotenv()
        api_url = os.getenv('RUMBLE_API_URL')
        
        if not api_url:
            print("⚠️ RUMBLE_API_URL no está configurado en .env")
            return None
        
        api = RumbleAPI(api_url, refresh_rate=5)
        livestream = api.latest_livestream
        
        if livestream and livestream.is_live:
            print(f"✅ Stream detectado: {livestream.title}")
            print(f"   URL: {api_url}")
            return {
                'api_url': api_url,
                'is_live': True,
                'title': livestream.title
            }
        else:
            print("⚠️ No hay stream en vivo actualmente")
            return None
            
    except ImportError:
        print("❌ cocorum no está instalado. Instala con: pip install cocorum")
        return None
    except Exception as e:
        print(f"❌ Error detectando stream: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    # Parsear argumentos de línea de comandos
    api_url = None
    channel = None
    auto_detect = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--api-url' and i + 1 < len(sys.argv):
            api_url = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--channel' and i + 1 < len(sys.argv):
            channel = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--auto-detect':
            auto_detect = True
            i += 1
        else:
            i += 1
    
    if auto_detect:
        result = auto_detect_rumble_stream()
        if result:
            update_rumble_env(api_url=result.get('api_url'))
    else:
        update_rumble_env(api_url=api_url, channel=channel)

