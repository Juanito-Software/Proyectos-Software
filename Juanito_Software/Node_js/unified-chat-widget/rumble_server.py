# Copyright (C) 2025 Juanito Software
#
# Este programa está protegido por una Licencia de Uso No Comercial.
# Puedes utilizarlo y compartirlo de forma gratuita, siempre que no se modifique
# y se incluya este aviso completo.
#
# Queda prohibido su uso con fines comerciales, así como su modificación,
# ingeniería inversa o redistribución alterada.
#
# Este software se proporciona "tal cual", sin garantía de ningún tipo, ya sea
# expresa o implícita, incluyendo, pero no limitado a, garantías de comerciabilidad
# o idoneidad para un propósito particular.
#
# Para más detalles, consulta el archivo LICENSE.txt incluido con este programa
# o contacta a bernaldezperedaj@gmail.com.

from flask import Flask, request, jsonify
from flask_cors import CORS
from cocorum import RumbleAPI
import threading
import time
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno
load_dotenv()

# Variables globales
rumble_api = None
chat_thread = None
is_running = False
latest_messages = []
messages_lock = threading.Lock()

# Configurables
RUMBLE_API_URL = os.getenv('RUMBLE_API_URL', '')
RUMBLE_CHANNEL = os.getenv('RUMBLE_CHANNEL', '')
RUMBLE_STREAM_URL = os.getenv('RUMBLE_STREAM_URL', '')  # URL opcional del stream específico
REFRESH_RATE = int(os.getenv('RUMBLE_REFRESH_RATE', '5'))  # segundos entre actualizaciones
MAX_MESSAGES = 100  # máximo de mensajes en buffer

def sanitize_message(msg):
    """Sanitiza y normaliza mensajes del chat"""
    if not msg:
        return None
    text = str(msg).strip()
    # Elimina caracteres de control problemáticos
    text = ''.join(ch for ch in text if ord(ch) >= 32 or ch in '\n\r')
    return text

def fetch_chat_messages():
    """Hilo que obtiene mensajes del chat de Rumble"""
    global rumble_api, is_running, latest_messages, RUMBLE_API_URL
    
    reconnect_attempts = 0
    max_reconnect_attempts = 10  # Intentar reconectar cada 30 segundos
    
    while is_running:
        try:
            if not rumble_api:
                # Intentar reconectar si tenemos URL configurada
                if RUMBLE_API_URL and reconnect_attempts < max_reconnect_attempts:
                    try:
                        print(f"🔄 Intentando reconectar a Rumble... (intento {reconnect_attempts + 1}/{max_reconnect_attempts})")
                        rumble_api = RumbleAPI(RUMBLE_API_URL, refresh_rate=REFRESH_RATE)
                        reconnect_attempts = 0  # Resetear contador si conecta
                        print(f"✅ Reconectado a Rumble")
                    except Exception as reconnect_error:
                        reconnect_attempts += 1
                        error_msg = str(reconnect_error)
                        if "404" not in error_msg:  # Solo loguear si no es un 404 (normal sin stream)
                            print(f"⚠️ Error al reconectar: {error_msg}")
                time.sleep(REFRESH_RATE * 6)  # Esperar más tiempo entre intentos de reconexión
                continue
            
            livestream = rumble_api.latest_livestream
            if livestream and livestream.is_live:
                # Obtener nuevos mensajes
                try:
                    new_messages = livestream.chat.new_messages
                    message_count = len(new_messages) if new_messages else 0
                    
                    if message_count > 0:
                        print(f"📨 [Rumble] Obtenidos {message_count} mensaje(s) nuevo(s)")
                    
                    # Usar un set para evitar duplicados basado en username + message + timestamp aproximado
                    processed_messages = set()
                    
                    with messages_lock:
                        for msg in new_messages:
                            username = getattr(msg, 'username', 'anon')
                            # ChatMessage tiene la propiedad 'text' según la documentación de cocorum
                            message_text = sanitize_message(
                                getattr(msg, 'text', None) or 
                                str(msg) if msg else ''
                            )
                            
                            if message_text:
                                # Crear una clave única para evitar duplicados (username + mensaje + timestamp aproximado)
                                # Usamos timestamp redondeado a segundos para agrupar mensajes del mismo segundo
                                timestamp_rounded = int(time.time())
                                message_key = f"{username}:{message_text}:{timestamp_rounded}"
                                
                                if message_key not in processed_messages:
                                    processed_messages.add(message_key)
                                    
                                    formatted = {
                                        'username': username,
                                        'message': message_text,
                                        'timestamp': int(time.time() * 1000)
                                    }
                                    latest_messages.append(formatted)
                                    print(f"💬 [Rumble] Mensaje capturado: {username}: {message_text[:50]}")
                                    
                                    # Mantener solo los últimos N mensajes
                                    if len(latest_messages) > MAX_MESSAGES:
                                        latest_messages.pop(0)
                                else:
                                    print(f"⚠️ [Rumble] Mensaje duplicado ignorado: {username}: {message_text[:30]}")
                except Exception as msg_error:
                    print(f"⚠️ Error obteniendo mensajes del chat: {msg_error}")
                    import traceback
                    traceback.print_exc()
            else:
                if not livestream:
                    print(f"⚠️ [Rumble] No se pudo obtener livestream")
                elif not livestream.is_live:
                    print(f"⚠️ [Rumble] Stream no está en vivo")
            
            time.sleep(REFRESH_RATE)
        except Exception as e:
            error_msg = str(e)
            # Solo loguear errores que no sean 404 (normal sin stream)
            if "404" not in error_msg:
                print(f"⚠️ Error obteniendo mensajes de Rumble: {error_msg}")
            # Si el error es crítico, resetear rumble_api para intentar reconectar
            if "404" not in error_msg and "connection" in error_msg.lower():
                rumble_api = None
            time.sleep(REFRESH_RATE)

@app.route("/start", methods=["POST"])
def start_chat():
    """Inicia la conexión al chat de Rumble"""
    global rumble_api, chat_thread, is_running, RUMBLE_API_URL, RUMBLE_CHANNEL
    
    data = request.get_json(silent=True) or {}
    api_url = data.get('api_url') or RUMBLE_API_URL
    channel = data.get('channel') or RUMBLE_CHANNEL
    stream_url = data.get('stream_url') or RUMBLE_STREAM_URL  # URL opcional del stream específico
    
    if not api_url:
        return jsonify({"error": "Falta RUMBLE_API_URL"}), 400
    
    try:
        # Detener conexión anterior si existe (evitar duplicación de hilos)
        if is_running:
            print(f"🛑 Deteniendo conexión anterior de Rumble para evitar duplicación...")
            is_running = False
            if chat_thread and chat_thread.is_alive():
                chat_thread.join(timeout=3)
            # Limpiar mensajes acumulados para evitar duplicados
            with messages_lock:
                latest_messages.clear()
            print(f"✅ Conexión anterior detenida")
        
        # Validar formato de URL
        if not api_url.startswith('http'):
            return jsonify({"error": f"URL inválida. Debe empezar con http:// o https://. Recibido: {api_url}"}), 400
        
        print(f"🔗 Intentando conectar a Rumble: {api_url}")
        
        # La api_url debe ser la URL de la API con la clave (ej: https://rumble.com/-livestream-api/get-data?key=...)
        # No debemos limpiar parámetros porque la clave está en los parámetros
        url_to_use = api_url
        
        # Si se proporciona una URL de stream específico, intentar usarla primero (pero normalmente usaremos api_url)
        # Nota: stream_url es opcional y normalmente no se usa si tenemos la API URL correcta
        if stream_url and stream_url != api_url:
            print(f"🔧 URL de stream específico proporcionada: {stream_url}")
            # No limpiar parámetros aquí porque puede ser necesario
        
        # Inicializar API de Rumble
        try:
            print(f"🔗 Intentando conectar con: {url_to_use}")
            rumble_api = RumbleAPI(url_to_use, refresh_rate=REFRESH_RATE)
            # Verificar si hay stream activo
            try:
                livestream = rumble_api.latest_livestream
                if livestream:
                    if livestream.is_live:
                        print(f"✅ Stream en vivo detectado: {livestream.title if hasattr(livestream, 'title') else 'Sin título'}")
                    else:
                        print(f"⚠️ No hay stream en vivo actualmente. El sistema seguirá intentando conectarse.")
                else:
                    print(f"⚠️ No se pudo obtener información del stream. Puede que no haya stream activo.")
            except Exception as stream_check_error:
                print(f"⚠️ No se pudo verificar el estado del stream: {stream_check_error}")
                # Continuamos de todas formas, el sistema intentará conectarse cuando haya stream
        except Exception as api_error:
            error_msg = str(api_error)
            print(f"❌ Error al inicializar RumbleAPI con URL: {url_to_use}")
            print(f"   Error: {error_msg}")
            
            # Si el error es de parsing JSON, puede ser que la URL no sea válida o el contenido sea Premium
            if "Expecting value" in error_msg or "JSON" in error_msg or "parse" in error_msg.lower():
                print(f"   ⚠️ Error de parsing JSON. Esto indica que cocorum está recibiendo HTML en lugar de JSON.")
                print(f"   💡 IMPORTANTE: cocorum necesita una 'API URL with key' específica, no la URL pública del canal/video.")
                print(f"   💡 Esta URL se obtiene desde tu panel de Rumble como streamer.")
                print(f"   💡 La URL debe ser algo como: https://rumble.com/api/[tu-key]")
                print(f"   💡 Verifica en tu panel de Rumble dónde se encuentra esta URL de la API.")
            
            # Si falla y tenemos stream_url diferente, intentar con stream_url
            if stream_url and url_to_use != stream_url:
                print(f"🔄 Intentando con URL de stream: {stream_url}")
                try:
                    rumble_api = RumbleAPI(stream_url, refresh_rate=REFRESH_RATE)
                    print(f"✅ Conectado usando URL de stream")
                except Exception as stream_error:
                    error_msg = str(stream_error)
                    print(f"❌ También falló con URL de stream: {error_msg}")
            
            # Si es un 404 o error de parsing, puede ser que la URL no sea correcta o no haya stream
            if "404" in error_msg or "not found" in error_msg.lower() or "Expecting value" in error_msg:
                # Intentamos continuar de todas formas - puede que no haya stream activo o sea Premium
                print(f"⚠️ No se pudo conectar. Posibles causas:")
                print(f"   - No hay stream activo en este momento")
                print(f"   - El stream es Premium Only (requiere suscripción)")
                print(f"   - La URL no es accesible públicamente")
                print(f"   El sistema seguirá intentando conectarse cuando haya un stream público activo.")
                # No retornamos error, permitimos que el sistema continúe
                # El hilo de chat intentará reconectar periódicamente
            else:
                return jsonify({"error": f"Error al conectar con Rumble: {error_msg}"}), 500
        
        # Si se proporciona canal, intentar conectarse
        if channel:
            print(f"🔗 Conectando a Rumble: {channel}")
        
        # Iniciar hilo de chat (incluso si no hay stream activo, para que intente reconectar)
        is_running = True
        with messages_lock:
            latest_messages.clear()
        
        chat_thread = threading.Thread(target=fetch_chat_messages, daemon=True)
        chat_thread.start()
        
        if rumble_api:
            print(f"✅ RumbleAPI inicializado correctamente para: {api_url}")
            return jsonify({
                "status": "ok",
                "message": f"Conectado a Rumble",
                "api_url": api_url,
                "channel": channel,
                "note": "El sistema seguirá intentando conectarse si no hay stream activo"
            }), 200
        else:
            # Si no se pudo inicializar pero no fue un error crítico (ej: 404 sin stream)
            print(f"⚠️ RumbleAPI no inicializado, pero el sistema seguirá intentando: {api_url}")
            return jsonify({
                "status": "pending",
                "message": "Sistema iniciado. Esperando stream activo o reconexión.",
                "api_url": api_url,
                "channel": channel,
                "note": "El sistema intentará conectarse automáticamente cuando haya stream activo"
            }), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error iniciando Rumble: {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route("/messages", methods=["GET"])
def get_messages():
    """Obtiene los mensajes acumulados y los limpia"""
    global latest_messages
    
    with messages_lock:
        messages = latest_messages.copy()
        latest_messages.clear()
    
    return jsonify({"messages": messages}), 200

@app.route("/status", methods=["GET"])
def get_status():
    """Obtiene el estado de la conexión"""
    global is_running, rumble_api, latest_messages
    
    status = {
        "connected": is_running,
        "api_initialized": rumble_api is not None,
        "messages_in_buffer": len(latest_messages)
    }
    
    if rumble_api:
        try:
            livestream = rumble_api.latest_livestream
            status["is_live"] = livestream.is_live if livestream else False
            if livestream:
                try:
                    # Intentar obtener información del chat
                    chat = livestream.chat
                    # Verificar si hay mensajes recientes
                    recent_msgs = getattr(chat, 'recent_messages', [])
                    status["recent_messages_count"] = len(recent_msgs) if recent_msgs else 0
                    status["chat_available"] = True
                except Exception as chat_error:
                    status["chat_error"] = str(chat_error)
                    status["chat_available"] = False
        except Exception as e:
            status["is_live"] = False
            status["error"] = str(e)
    
    return jsonify(status), 200

@app.route("/stop", methods=["POST"])
def stop_chat():
    """Detiene la conexión al chat"""
    global is_running, chat_thread
    
    is_running = False
    if chat_thread:
        chat_thread.join(timeout=2)
    
    return jsonify({"status": "stopped"}), 200

if __name__ == "__main__":
    port = int(os.getenv('RUMBLE_SERVER_PORT', '5003'))
    print(f"🚀 Servidor Rumble iniciando en puerto {port}")
    
    # Auto-iniciar si hay configuración en .env
    if RUMBLE_API_URL:
        try:
            print(f"🔗 Intentando auto-conectar a Rumble: {RUMBLE_API_URL}")
            if not RUMBLE_API_URL.startswith('http'):
                print(f"⚠️ URL inválida en .env. Debe empezar con http:// o https://")
            else:
                try:
                    rumble_api = RumbleAPI(RUMBLE_API_URL, refresh_rate=REFRESH_RATE)
                    is_running = True
                    chat_thread = threading.Thread(target=fetch_chat_messages, daemon=True)
                    chat_thread.start()
                    print(f"✅ Auto-conectado a Rumble: {RUMBLE_API_URL}")
                    print(f"✅ Hilo de chat iniciado")
                    # Verificar si hay stream activo
                    try:
                        livestream = rumble_api.latest_livestream
                        if livestream and livestream.is_live:
                            print(f"✅ Stream en vivo detectado: {livestream.title if hasattr(livestream, 'title') else 'Sin título'}")
                            print(f"🔄 Iniciando captura de mensajes del chat...")
                        else:
                            print(f"⚠️ No hay stream en vivo actualmente. El sistema seguirá intentando.")
                    except Exception as stream_check:
                        print(f"⚠️ No se pudo verificar el estado del stream: {stream_check}")
                        import traceback
                        traceback.print_exc()
                except Exception as init_error:
                    error_msg = str(init_error)
                    if "404" in error_msg:
                        print(f"⚠️ No se pudo auto-conectar (404). Esto puede ser normal si no hay stream activo.")
                        print(f"   El sistema seguirá intentando conectarse cuando inicies un stream.")
                        print(f"   URL configurada: {RUMBLE_API_URL}")
                        # Iniciamos el hilo de todas formas para que intente reconectar
                        is_running = True
                        chat_thread = threading.Thread(target=fetch_chat_messages, daemon=True)
                        chat_thread.start()
                        print(f"✅ Hilo de reconexión iniciado")
                    else:
                        print(f"⚠️ No se pudo auto-conectar: {error_msg}")
                        print(f"   URL actual: {RUMBLE_API_URL}")
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Error en auto-conexión: {error_msg}")
            import traceback
            traceback.print_exc()
    
    app.run(host="0.0.0.0", port=port, debug=False)

