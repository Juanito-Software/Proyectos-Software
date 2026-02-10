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
import requests
from bs4 import BeautifulSoup
import threading
import time
import os
import re
import json
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno
load_dotenv()

# Variables globales
is_running = False
chat_thread = None
latest_messages = []
messages_lock = threading.Lock()
processed_message_ids = set()

# Configurables
BITCHUTE_CHANNEL_NAME = os.getenv('BITCHUTE_CHANNEL_NAME', '')
BITCHUTE_VIDEO_ID = os.getenv('BITCHUTE_VIDEO_ID', '')
REFRESH_RATE = int(os.getenv('BITCHUTE_REFRESH_RATE', '5'))  # segundos entre actualizaciones
MAX_MESSAGES = 100  # máximo de mensajes en buffer
MAX_PROCESSED_IDS = 1000  # máximo de IDs procesados en memoria

def sanitize_message(msg):
    """Sanitiza y normaliza mensajes del chat"""
    if not msg:
        return None
    text = str(msg).strip()
    # Elimina caracteres de control problemáticos
    text = ''.join(ch for ch in text if ord(ch) >= 32 or ch in '\n\r')
    return text

def extract_chat_messages_from_html(html_content, video_id):
    """Extrae mensajes del chat desde el HTML de la página"""
    messages = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # BitChute puede tener el chat en diferentes lugares
        # Intentar múltiples métodos de extracción
        
        # Método 1: Buscar scripts que contengan datos del chat
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Buscar datos JSON en los scripts
                try:
                    # Buscar patrones como window.__INITIAL_STATE__ o similar
                    if 'chat' in script.string.lower() or 'message' in script.string.lower():
                        # Intentar extraer JSON
                        json_matches = re.findall(r'\{[^{}]*"chat"[^{}]*\}', script.string, re.IGNORECASE)
                        for json_str in json_matches:
                            try:
                                data = json.loads(json_str)
                                if 'messages' in data or 'chat' in data:
                                    chat_data = data.get('chat') or data.get('messages') or data
                                    if isinstance(chat_data, list):
                                        messages.extend(chat_data)
                                    elif isinstance(chat_data, dict) and 'messages' in chat_data:
                                        messages.extend(chat_data['messages'])
                            except:
                                pass
                except:
                    pass
        
        # Método 2: Buscar elementos HTML con clases relacionadas al chat
        chat_containers = soup.find_all(['div', 'ul', 'ol'], class_=re.compile(r'chat|message|comment', re.I))
        for container in chat_containers:
            message_elements = container.find_all(['div', 'li', 'span'], class_=re.compile(r'message|comment|chat', re.I))
            for elem in message_elements:
                # Intentar extraer autor y mensaje
                author_elem = elem.find(['span', 'div', 'strong'], class_=re.compile(r'author|user|name|username', re.I))
                content_elem = elem.find(['span', 'div', 'p'], class_=re.compile(r'content|text|message|body', re.I))
                
                if author_elem or content_elem:
                    author = author_elem.get_text(strip=True) if author_elem else 'anon'
                    content = content_elem.get_text(strip=True) if content_elem else elem.get_text(strip=True)
                    
                    if content:
                        messages.append({
                            'username': author,
                            'message': content,
                            'timestamp': int(time.time() * 1000)
                        })
        
        # Método 3: Buscar en atributos data-* que puedan contener JSON
        data_elements = soup.find_all(attrs={'data-chat': True}) + soup.find_all(attrs={'data-messages': True})
        for elem in data_elements:
            data_attr = elem.get('data-chat') or elem.get('data-messages')
            if data_attr:
                try:
                    data = json.loads(data_attr)
                    if isinstance(data, list):
                        messages.extend(data)
                    elif isinstance(data, dict) and 'messages' in data:
                        messages.extend(data['messages'])
                except:
                    pass
                    
    except Exception as e:
        print(f"⚠️ Error extrayendo mensajes del HTML: {e}")
    
    return messages

def fetch_chat_messages():
    """Hilo que obtiene mensajes del chat de BitChute mediante scraping"""
    global is_running, latest_messages, BITCHUTE_VIDEO_ID, BITCHUTE_CHANNEL_NAME, processed_message_ids
    
    while is_running:
        try:
            if not BITCHUTE_VIDEO_ID:
                print("⚠️ [BitChute] BITCHUTE_VIDEO_ID no configurado")
                time.sleep(REFRESH_RATE * 2)
                continue
            
            # Construir URL del video
            video_url = f"https://www.bitchute.com/video/{BITCHUTE_VIDEO_ID}/"
            
            try:
                # Hacer request a la página del video
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(video_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Extraer mensajes del HTML
                    new_messages = extract_chat_messages_from_html(response.text, BITCHUTE_VIDEO_ID)
                    
                    if new_messages:
                        print(f"📨 [BitChute] Encontrados {len(new_messages)} mensaje(s) potencial(es)")
                        
                        with messages_lock:
                            for msg in new_messages:
                                username = msg.get('username', 'anon')
                                message_text = sanitize_message(msg.get('message', ''))
                                timestamp = msg.get('timestamp', int(time.time() * 1000))
                                
                                if message_text:
                                    # Crear ID único para evitar duplicados
                                    message_id = f"{username}:{message_text}:{timestamp}"
                                    
                                    if message_id not in processed_message_ids:
                                        processed_message_ids.add(message_id)
                                        
                                        # Limitar tamaño del set
                                        if len(processed_message_ids) > MAX_PROCESSED_IDS:
                                            # Eliminar los más antiguos (simple: eliminar algunos aleatorios)
                                            ids_list = list(processed_message_ids)
                                            processed_message_ids = set(ids_list[-MAX_PROCESSED_IDS//2:])
                                        
                                        formatted = {
                                            'username': username,
                                            'message': message_text,
                                            'timestamp': timestamp,
                                            'id': message_id
                                        }
                                        latest_messages.append(formatted)
                                        print(f"💬 [BitChute] Mensaje capturado: {username}: {message_text[:50]}")
                                        
                                        # Mantener solo los últimos N mensajes
                                        if len(latest_messages) > MAX_MESSAGES:
                                            latest_messages.pop(0)
                                    else:
                                        print(f"⚠️ [BitChute] Mensaje duplicado ignorado: {username}: {message_text[:30]}")
                elif response.status_code == 404:
                    print(f"⚠️ [BitChute] Video no encontrado (404). Verifica que BITCHUTE_VIDEO_ID sea correcto.")
                else:
                    print(f"⚠️ [BitChute] Error HTTP {response.status_code} al acceder al video")
                    
            except requests.exceptions.Timeout:
                print(f"⚠️ [BitChute] Timeout al acceder al video")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ [BitChute] Error de conexión: {e}")
            except Exception as e:
                print(f"⚠️ [BitChute] Error obteniendo mensajes: {e}")
                import traceback
                traceback.print_exc()
            
            time.sleep(REFRESH_RATE)
            
        except Exception as e:
            print(f"⚠️ Error en hilo de chat de BitChute: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(REFRESH_RATE * 2)

@app.route("/start", methods=["POST"])
def start_chat():
    """Inicia la conexión al chat de BitChute"""
    global is_running, chat_thread, latest_messages, BITCHUTE_VIDEO_ID, BITCHUTE_CHANNEL_NAME, processed_message_ids
    
    data = request.get_json(silent=True) or {}
    video_id = data.get('video_id') or BITCHUTE_VIDEO_ID
    channel = data.get('channel') or BITCHUTE_CHANNEL_NAME
    
    if not video_id:
        return jsonify({"error": "Falta BITCHUTE_VIDEO_ID"}), 400
    
    try:
        # Detener conexión anterior si existe
        if is_running:
            print(f"🛑 Deteniendo conexión anterior de BitChute...")
            is_running = False
            if chat_thread and chat_thread.is_alive():
                chat_thread.join(timeout=3)
            with messages_lock:
                latest_messages.clear()
                processed_message_ids.clear()
            print(f"✅ Conexión anterior detenida")
        
        BITCHUTE_VIDEO_ID = video_id
        if channel:
            BITCHUTE_CHANNEL_NAME = channel
        
        # Verificar que el video existe
        video_url = f"https://www.bitchute.com/video/{video_id}/"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(video_url, headers=headers, timeout=10)
            if response.status_code == 404:
                return jsonify({
                    "error": f"Video no encontrado (404). Verifica que el VIDEO_ID '{video_id}' sea correcto.",
                    "video_url": video_url
                }), 404
        except Exception as check_error:
            print(f"⚠️ No se pudo verificar el video: {check_error}")
        
        # Iniciar hilo de chat
        is_running = True
        with messages_lock:
            latest_messages.clear()
            processed_message_ids.clear()
        
        chat_thread = threading.Thread(target=fetch_chat_messages, daemon=True)
        chat_thread.start()
        
        print(f"✅ BitChute chat iniciado para video: {video_id}")
        if channel:
            print(f"   Canal: {channel}")
        
        return jsonify({
            "status": "ok",
            "message": f"Conectado a BitChute",
            "video_id": video_id,
            "channel": channel,
            "video_url": video_url,
            "note": "BitChute usa scraping, los mensajes pueden tardar en aparecer"
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error iniciando BitChute: {error_msg}")
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
    global is_running, latest_messages, BITCHUTE_VIDEO_ID
    
    status = {
        "connected": is_running,
        "video_id": BITCHUTE_VIDEO_ID,
        "messages_in_buffer": len(latest_messages),
        "processed_ids_count": len(processed_message_ids)
    }
    
    if BITCHUTE_VIDEO_ID:
        status["video_url"] = f"https://www.bitchute.com/video/{BITCHUTE_VIDEO_ID}/"
    
    return jsonify(status), 200

@app.route("/stop", methods=["POST"])
def stop_chat():
    """Detiene la conexión al chat"""
    global is_running, chat_thread, processed_message_ids
    
    is_running = False
    if chat_thread:
        chat_thread.join(timeout=2)
    
    processed_message_ids.clear()
    
    return jsonify({"status": "stopped"}), 200

if __name__ == "__main__":
    port = int(os.getenv('BITCHUTE_SERVER_PORT', '5005'))
    print(f"🚀 Servidor BitChute iniciando en puerto {port}")
    
    # Auto-iniciar si hay configuración en .env
    if BITCHUTE_VIDEO_ID:
        try:
            print(f"🔗 Intentando auto-conectar a BitChute: {BITCHUTE_VIDEO_ID}")
            is_running = True
            with messages_lock:
                latest_messages.clear()
                processed_message_ids.clear()
            
            chat_thread = threading.Thread(target=fetch_chat_messages, daemon=True)
            chat_thread.start()
            print(f"✅ Auto-conectado a BitChute: {BITCHUTE_VIDEO_ID}")
            print(f"✅ Hilo de chat iniciado")
            print(f"🔄 Iniciando captura de mensajes del chat...")
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Error en auto-conexión: {error_msg}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️ BITCHUTE_VIDEO_ID no configurado en .env")
        print(f"   El servidor está corriendo pero no capturará mensajes hasta que se llame a /start")
    
    app.run(host="0.0.0.0", port=port, debug=False)

