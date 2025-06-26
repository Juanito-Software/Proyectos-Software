# Copyright (C) 2025 Juanito Software
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from pyogg import OpusBufferedEncoder, OpusDecoder
from collections import deque
import socket, threading, time, random, pyaudio
from threading import Event
import numpy as np
import logging
import pyrtp
import struct

# =================== CONFIGURACIONES GLOBALES ===================

SERVER_PORT = 12345       # Puerto para control y mensajes TCP (opcional para control)
HEARTBEAT_PORT = 12346    # Puerto para los mensajes de heartbeat y elección
AUDIO_PORT = 12347        # Puerto para transmisión de audio vía UDP

BROADCAST_IP = "192.168.1.255"  # Ajusta según tu red

HEARTBEAT_INTERVAL = 4   # Intervalo entre heartbeats (segundos)
HEARTBEAT_TIMEOUT = 5    # Tiempo de espera para detectar fallo del heartbeat

# Variable global adicional
host_establecido = False

# Variables globales para la elección de host
is_host = False
last_heartbeat = time.time()  # Último tiempo en que se recibió heartbeat

join_timestamp = time.time()  # Marca de tiempo del cliente al iniciar
host_info = None  # Información del host actual: (ip, join_timestamp)

# Objeto para señalizar el cese de hilos (audio, heartbeat, etc.)
stop_event = threading.Event()

# Lock para proteger variables compartidas, manejar las condiciones de carrera en host_info e is_host asi como el bloqueo de la escirtura en el bufffer de audio
lock = threading.RLock()
audio_lock = threading.Lock()
externalBufferLock = threading.Lock()

# Roles
current_role = None
role_changed = Event()

# =================== CONFIGURACIÓN DE AUDIO ===================

CHUNK = 960
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

# Configuración de PyAudio
p = pyaudio.PyAudio()

# Configuración de Opus
encoder = OpusBufferedEncoder()
decoder = OpusDecoder()


# Establecer la aplicación y los parámetros de audio
# frame_duration_ms = 20
max_bytes = 4000  # Ajusta según tu necesidad
encoder.set_application("audio")
encoder.set_channels(CHANNELS)
encoder.set_sampling_frequency(RATE)
encoder.frame_size = 960  # tamaño de frame típico para audio a 48kHz
encoder.set_frame_size(20)
encoder.set_max_bytes_per_frame(max_bytes)

decoder.set_channels(CHANNELS)
decoder.set_sampling_frequency(RATE)

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# =================== CONFIGURACION RTP ===================

seq_num = 0
timestamp = 0
ssrc_id = random.randint(100000, 999999)

def generate_rtp_packet(packet_vars):
    """
    Genera un paquete RTP concatenando un encabezado RTP dinámico y la carga útil.
    packet_vars es un diccionario con:
      - version: 2 bits (usualmente 2)
      - padding: 1 bit (0 o 1)
      - extension: 1 bit (0 o 1)
      - csi_count: 4 bits (generalmente 0)
      - marker: 1 bit (0 o 1)
      - payload_type: 7 bits (por ejemplo 111 para Opus)
      - sequence_number: 16 bits
      - timestamp: 32 bits
      - ssrc: 32 bits
      - payload: bytes con la carga útil
    """
    # Primer byte: version (2 bits), padding (1 bit), extension (1 bit), csrc count (4 bits)
    byte0 = (packet_vars['version'] << 6) | (packet_vars['padding'] << 5) | (packet_vars['extension'] << 4) | (packet_vars['csi_count'] & 0x0F)
    # Segundo byte: marker (1 bit) y payload type (7 bits)
    byte1 = (packet_vars['marker'] << 7) | (packet_vars['payload_type'] & 0x7F)
    # Empaqueta el encabezado RTP: 2 bytes, 2 bytes para sequence number, 4 para timestamp y 4 para ssrc
    header = struct.pack('!BBHII', byte0, byte1, packet_vars['sequence_number'], packet_vars['timestamp'], packet_vars['ssrc'])
    # Retorna el encabezado concatenado con la carga útil
    return header + packet_vars['payload']


def parse_rtp_packet(packet):
    """
    Decodifica un paquete RTP simple.
    Retorna un diccionario con información del encabezado y el payload.
    """
    if len(packet) < 12:
        raise ValueError("Paquete RTP demasiado corto.")

    header = struct.unpack('!BBHII', packet[:12])

    version = header[0] >> 6 & 0x03
    padding = (packet[0] >> 5) & 0x01
    extension = (packet[0] >> 4) & 0x01
    csi_count = packet[0] & 0x0F

    marker = (packet[1] >> 7) & 0x01
    payload_type = header[1] & 0x7F

    sequence_number = header[2]
    timestamp = header[3]
    ssrc = header[4]

    header_length = 12 + (csi_count * 4)
    if len(packet) < header_length:
        raise ValueError("Encabezado RTP con CSRC incompleto.")
    payload = packet[header_length:]

    return {
        "version": version,
        "padding": padding,
        "extension": extension,
        "csi_count": csi_count,
        "marker": marker,
        "payload_type": payload_type,
        "sequence_number": sequence_number,
        "timestamp": timestamp,
        "ssrc": ssrc,
        "payload": payload
    }

# =================== CLASE PARA EL BUFFER ===================

class AudioBuffer:
    def __init__(self, max_size=100):
        self.buffer = deque()  # Usamos una deque (cola doble) para almacenar los paquetes
        self.max_size = max_size
        self.lock = threading.Lock()  # Lock para asegurar acceso seguro desde múltiples hilos

    def add_packet(self, packet):
        """Agrega un paquete al buffer. Si el buffer está lleno, se descarta el más antiguo."""
        with self.lock:
            if len(self.buffer) >= self.max_size:
                self.buffer.popleft()  # Elimina el paquete más antiguo si se ha alcanzado el límite
            self.buffer.append(packet)

    def get_packet(self):
        """Obtiene el siguiente paquete del buffer (FIFO)."""
        with self.lock:
            if self.buffer:
                return self.buffer.popleft()
            return None

    def is_empty(self):
        """Verifica si el buffer está vacío."""
        with self.lock:
            return len(self.buffer) == 0

    def get_all_packets(self):
        """Obtiene todos los paquetes del buffer sin eliminarlos (útil para retransmitir)."""
        with self.lock:
            return list(self.buffer)

    def clear(self):
        """Vacía el buffer."""
        with self.lock:
            self.buffer.clear()

# =================== BUFFER AUDIO ===================

audio_buffer = AudioBuffer()  # Instancia del buffer

# =================== OBTENCIÓN DE LA IP REAL ===================

def get_ip():
    """
    Obtiene la IP local del nodo, útil para comparaciones.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception as e:
        logging.error("Error obteniendo la IP local: %s", e)
        return '127.0.0.1'
    finally:
        s.close()
    return ip

# =================== ACTUALIZACION DE HOST ===================

def update_host_info(new_host_ip, timestamp, new_is_host):
    """Actualiza la información del host de manera segura."""
    global host_info, is_host, host_establecido
    with lock:
        host_info = (new_host_ip, timestamp)
        is_host = new_is_host
        host_establecido = True
        logging.info("Nuevo host establecido: %s con timestamp %s", new_host_ip, timestamp)

def get_host_info():
    with lock:
        return host_info if host_establecido else None  

# =================== SERVIDOR DE AUDIO ===================

def start_server_for_audio(port):
    """
    Levanta el servidor UDP para gestionar las conexiones de audio y retransmitir a otros clientes.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.bind(("", port))
        logging.info(f"Servidor UDP de audio iniciado y escuchando en el puerto {AUDIO_PORT}")

        while not stop_event.is_set():
            try:
                data, addr = server_socket.recvfrom(4096)
                logging.debug(f"Paquete de audio recibido de {addr}. Tamaño: {len(data)} bytes")

                # Aquí guardamos el paquete recibido
                with audio_lock:
                    audio_buffer.add_packet(data)  # Agregar el paquete recibido al buffer de audio

                # Retransmitir el paquete a todos los clientes
                redistribute_audio(data, addr)
            except socket.timeout:
                continue
    except Exception as e:
        logging.error(f"Error al iniciar el servidor de audio: {e}")
    finally:
        server_socket.close()

# =================== FUNCIONES SERVIDOR DE AUDIO ===================

def redistribute_audio(data, sender_ip):
    """
    Redistribuye el paquete de audio recibido a todos los demás clientes conectados.
    """
    global connected_clients
    for client, ip in connected_clients:
        if ip != sender_ip:  # No enviar el paquete al cliente que lo envió
            try:
                # Enviar el paquete de audio a todos los demás clientes
                client.sendto(data, (ip, AUDIO_PORT))
                logging.debug(f"Redistribuyendo paquete a {ip}. Tamaño: {len(data)} bytes")
            except Exception as e:
                logging.warning(f"Error al redistribuir audio a {ip}: {e}")


def mix_audio(data_list):
    """
    Mezcla múltiples flujos de audio. Cada flujo es una secuencia de bytes.
    """
    # Supón que cada flujo de audio es un arreglo de NumPy de tipo int16
    mixed_audio = np.zeros_like(data_list[0], dtype=np.int16)

    for data in data_list:
        audio_array = np.frombuffer(data, dtype=np.int16)
        mixed_audio += audio_array

    # Para evitar desbordamientos, limita los valores a [-32768, 32767] (rango de int16)
    mixed_audio = np.clip(mixed_audio, -32768, 32767)
    return mixed_audio.tobytes()


def start_audio_mixing_and_forwarding():
    """
    Realiza la mezcla de audio y retransmite el audio mezclado a los clientes.
    """
    audio_data_list = []
    while not stop_event.is_set():
        # Recoge los paquetes de audio de todos los clientes
        with audio_lock:
            if not audio_buffer.is_empty():
                audio_data_list.append(audio_buffer.get_packet())
            
            if len(audio_data_list) > 0:
                # Mezcla todos los paquetes de audio recogidos
                mixed_audio = mix_audio(audio_data_list)

                # Codifica el audio mezclado
                mixed_audio_opus = encoder.encode(bytearray(mixed_audio))

                # Empaqueta los datos mezclados en un paquete RTP
                packet_vars = {
                    'version': 2,
                    'padding': 0,
                    'extension': 0,
                    'csi_count': 0,
                    'marker': 0,
                    'payload_type': 111,
                    'sequence_number': seq_num,
                    'timestamp': timestamp,
                    'ssrc': ssrc_id,
                    'payload': mixed_audio_opus
                }

                packet_bytes = generate_rtp_packet(packet_vars)

                # Redistribuir el paquete mezclado a todos los clientes
                redistribute_audio(packet_bytes, sender_ip=None)  # Aquí no es necesario enviar el sender_ip

                # Limpiar la lista de datos de audio después de la mezcla
                audio_data_list = []

            time.sleep(0.02)

# =================== FUNCIONES DE AUDIO ===================

def start_audio_capture():
    """
    Captura el audio del micrófono, lo codifica con Opus y lo añade al buffer.
    """
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    
    while not stop_event.is_set():
        try:
            with audio_lock:  # Se asegura de que solo un hilo acceda a esta sección a la vez
                # Lee datos del stream
                data = stream.read(CHUNK)
                logging.debug(f"Datos de audio capturados: {data[:50]}")

                # Convierte a un array de NumPy de tipo int16
                # audio_data = np.frombuffer(data, dtype=np.int16)

                # Codifica los datos de audio con Opus
                opus_payload = encoder.encode(bytearray(data))
                # Añadir el paquete codificado al buffer
                logging.debug(f"Agregando opus_payload al buffer: {opus_payload.hex()}")

                audio_buffer.add_packet(opus_payload)  # Almacena en el buffer
                logging.debug(f"Capturado y añadido paquete de audio. Tamaño: {len(opus_payload)} bytes")
        except Exception as e:
            logging.error("Error capturando audio: %s", e)
            break
    # Detener y cerrar el stream de audio
    try:
        stream.stop_stream()
        stream.close()
    except Exception as e:
        logging.error("Error al cerrar el stream de audio: %s", e)

def start_audio_unicast():
    """
    Toma los paquetes del buffer les añade encabezados RTP y los envía vía unicast (o broadcast, si prefieres) 
    utilizando un socket UDP y en orden de llegada.
    """  
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while not stop_event.is_set():
        try:
            # Esperar hasta que el host esté establecido
            while True:
                info = get_host_info()
                if info is not None: # cuando se establece el host rompemos el bucle
                    break
                # El bucle sigue esperando si el host no está establecido
                logging.warning("El host no está establecido. Esperando...")
                time.sleep(1) # Espera antes de intentar nuevamente


            # Una vez el host está establecido, se continúa
            with externalBufferLock:  # Protege el acceso al buffer
                if not audio_buffer.is_empty():
                    opus_payload = audio_buffer.get_packet()  # Obtiene el siguiente paquete en orden
                    
                    # Empaquetado RTP
                    packet_vars = {
                        'version': 2,
                        'padding': 0,
                        'extension': 0,
                        'csi_count': 0,
                        'marker': 0,
                        'payload_type': 111,
                        'sequence_number': seq_num,
                        'timestamp': timestamp,
                        'ssrc': ssrc_id,
                        'payload': opus_payload
                    }

                    # Genera el paquete RTP
                    packet_bytes = generate_rtp_packet(packet_vars)
                    logging.debug(f"Paquete RTP (Unicast) generado: {packet_bytes.hex()}")
                    
                    
                    # Dirección del destino (host_info[0] si está definido)
                    info = get_host_info()
                    if info:
                        destination_ip = info[0]
                        logging.debug(f"Dirección del destino: {info[0]}")
                    else:
                        logging.error("No se pudo obtener la información del host.")
                    # Envía el paquete RTP por UDP
                    sock.sendto(packet_bytes, (destination_ip, AUDIO_PORT))
                    logging.debug(f"Enviado paquete RTP a {destination_ip} con (seq={seq_num}, ts={timestamp}, tamaño={len(packet_bytes)} bytes)")
            
                    # Actualiza para el siguiente paquete
                    seq_num = (seq_num + 1) % 65536
                    timestamp += CHUNK  # Sumar tamaño del paquete (por ejemplo 960 para Opus 20ms)
            time.sleep(0.02)  # Ajusta el tiempo de espera entre paquetes
        except Exception as e:
            logging.error("Error enviando paquete de audio: %s", e)
            break
    sock.close()

def start_audio_playback():
    """
    Recibe paquetes RTP con audio Opus vía UDP y los reproduce usando PyAudio.
    """
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    output=True, frames_per_buffer=CHUNK)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind(("", AUDIO_PORT))
        logging.info(f"Escuchando en puerto {AUDIO_PORT} para paquetes de audio.")
    except Exception as e:
        logging.error("Error al enlazar el socket de audio: %s", e)
        return
    
    while not stop_event.is_set():
        try:
            # Recibe los datos por UDP
            data, addr = sock.recvfrom(4096)
            logging.debug(f"Paquete de audio recibido de {addr}. Tamaño: {len(data)} bytes")

            # Parsear RTP
            rtp_info = parse_rtp_packet(data)
            if not rtp_info.get("payload"):
                logging.error("Paquete RTP no contiene datos de audio.")
                continue  # Si no hay payload, pasamos al siguiente paquete
            audio_data = rtp_info["payload"]
            logging.debug(f"Payload extraído del paquete: {audio_data.hex()}")


            # Decodificar Opus a PCM
            decoded_data = decoder.decode(bytearray(audio_data)) # Decodificación Opus
            logging.debug(f"Datos decodificados: {bytes(decoded_data)}")

            # Convertir memoryview a bytes antes de escribir en el stream
            if isinstance(decoded_data, memoryview):
                decoded_data = decoded_data.tobytes()

            logging.debug(f"Recibido paquete de audio de {addr}. Tamaño: {len(decoded_data)} bytes")

            # Verifica si el stream está abierto antes de escribir en él
            if stream.is_active():
                stream.write(decoded_data)
            else:
                logging.warning("Stream de audio no está activo, no se puede reproducir.")
        except Exception as e:
            logging.error("Error reproduciendo audio: %s", e)
            break
    # Detener y cerrar el stream y el socket
    try:
        stream.stop_stream()
        stream.close()
        sock.close()
    except Exception as e:
        logging.error("Error al cerrar el stream o el socket: %s", e)

# =================== MÓDULO HEARTBEAT Y ELECCIÓN ===================

""""
def broadcast_host_change(new_host_ip,timestamp):

    # Envía un mensaje a todos los clientes notificando el cambio de host.

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mensaje = f"HOST_CHANGE|{new_host_ip}|{timestamp}"
        sock.sendto(mensaje.encode(), (BROADCAST_IP, HEARTBEAT_PORT))
        sock.close()
"""

def heartbeat_sender():
    """
    Si este cliente es host, envía mensajes de heartbeat a intervalos regulares.
    """
    global is_host
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while is_host and not stop_event.is_set():
            mensaje = f"HEARTBEAT|{join_timestamp}"
            sock.sendto(mensaje.encode(), (BROADCAST_IP, HEARTBEAT_PORT))
            logging.debug("Enviado HEARTBEAT desde %s", join_timestamp)
            time.sleep(HEARTBEAT_INTERVAL)
        sock.close()

def heartbeat_listener():
    """
    Escucha mensajes de heartbeat y mensajes de elección.
    """
    global last_heartbeat, host_info, is_host, current_role, server_thread
    local_ip = get_ip()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.bind(("", HEARTBEAT_PORT))
        except Exception as e:
            logging.error("Error enlazando heartbeat_listener: %s", e)
            return
        
        while not stop_event.is_set():
            try:
                data, addr = sock.recvfrom(1024)
                mensaje = data.decode()
                partes = mensaje.split("|")
                tipo_mensaje = partes[0]

                logging.debug("Intentando adquirir lock en heartbeat_listener")
                with lock:  # Bloquea antes de modificar variables compartidas
                    logging.debug("Lock adquirido en heartbeat_listener")
                    if tipo_mensaje == "HEARTBEAT":
                        last_heartbeat = time.time()
                        logging.debug("HEARTBEAT recibido desde la IP %s y puerto %s con timestamp %s y tipo de mensaje %s", addr[0], addr[1], partes[1], partes[0])

                    elif tipo_mensaje == "ELECTION":
                        candidato_ts = float(partes[1])
                        if host_info is None or candidato_ts < host_info[1]:
                            # Actualiza el host_info usando update_host_info, sin marcar a este cliente como host
                            update_host_info(addr[0], candidato_ts, False)
                            logging.debug("Actualizado host_info por elección a %s", host_info)
                    """"
                    elif tipo_mensaje == "HOST_CHANGE":
                        nuevo_host_ip = partes[1]
                        timeStamp = float(partes[2])
                        update_host_info(nuevo_host_ip, timeStamp, False)
                        logging.debug("Actualizado host_info por cambio de host a %s", host_info)
                    """
                logging.debug("Liberando lock en heartbeat_listener")

                # COMPROBACIÓN DE CAMBIO DE ROL (fuera del lock para no bloquear innecesariamente)
                new_host_ip = host_info[0] if host_info else None

                # Si el nodo pasa de cliente a host
                if not is_host and (time.time() - last_heartbeat > HEARTBEAT_TIMEOUT):
                    print("No heartbeat detected. Becoming host...")
                    is_host = True
                    current_role = "Host"
                    role_changed.set()  # Indicar que el rol ha cambiado

                    # reinicia servidor
                    server_thread = threading.Thread(target=start_TCP_server, args=(None, SERVER_PORT), daemon=True)
                    server_thread.start()

                # Si se detecta un nuevo host y el nodo actual es host
                elif is_host and new_host_ip != local_ip:
                    print(f"New host detected: {new_host_ip}. Reverting to client mode...")
                    is_host = False
                    current_role = "Cliente"
                    role_changed.set()

            except Exception as e:
                logging.error("Error en heartbeat_listener: %s", e)
                break
        sock.close()

def check_heartbeat(gui_update_callback):
    """
    Verifica de forma periódica si se están recibiendo heartbeats.
    Si no se detectan, se inicia la elección de host.
    """
    global host_info
    global is_host
    global host_establecido

    missed_heartbeats = 0  # Contador de ciclos sin heartbeat

    while not stop_event.is_set():
        with lock:
            if time.time() - last_heartbeat > HEARTBEAT_TIMEOUT:
                missed_heartbeats += 1
                if missed_heartbeats >= 2:  # Espera 2 ciclos antes de resetear host_info
                    # Solo resetear si no hay host establecido
                    if not is_host and host_info is not None and not host_establecido:
                        is_host = False
                        host_info = None  # Restablecer a un valor predeterminado
                        host_establecido = False  # Indicar que no hay host válido
                    missed_heartbeats = 0  # Reiniciar contador
                    logging.warning("Heartbeat perdido. Iniciando elección de host...")
                    initiate_election(gui_update_callback)
            else:
                missed_heartbeats = 0  # Reiniciar si se recibe un heartbeat
                logging.debug("Comprobando heartbeat. Último heartbeat: %s", last_heartbeat)
        stop_event.wait(HEARTBEAT_INTERVAL)

def initiate_election(gui_update_callback):
    """
    Envía un mensaje de elección y, tras un breve retraso aleatorio,
    decide si este cliente debe convertirse en host en función de su join_timestamp.
    """
    global is_host, host_info, join_timestamp, host_establecido
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mensaje = f"ELECTION|{join_timestamp}"
        sock.sendto(mensaje.encode(), (BROADCAST_IP, HEARTBEAT_PORT))
        logging.debug("Iniciando elección con join_timestamp: %s", join_timestamp)
        
        delay = random.uniform(0, 1)
        time.sleep(delay)

        logging.debug("Intentando adquirir lock en initiate_election")
        with lock:  # Protege el acceso a host_info
            logging.debug("Lock adquirido en initiate_election")
            # Si aún no se ha establecido un host, este cliente se convierte en host.
            if host_info is None:
                update_host_info(get_ip(), join_timestamp, True)
                logging.info("Este cliente se convierte en el nuevo host.")
                
                # Iniciar el servidor y enviar heartbeats
                threading.Thread(target=start_TCP_server, args=(None, SERVER_PORT), daemon=True).start()
                threading.Thread(target=heartbeat_sender, daemon=True).start()
                gui_update_callback("Conectado (Host)")
                # broadcast_host_change(get_ip(), join_timestamp)  # Notifica a los demás clientes
            else:
                logging.info("Otro cliente se ha convertido en host.")
                gui_update_callback("Conectado (Cliente)")
        sock.close()
        logging.debug("Lock liberado en initiate_election")

# =================== SERVIDOR PARA GESTIONAR CONEXIONES ===================

connected_clients = []


def start_TCP_server(_host_ip, port):
    """
    Levanta el servidor TCP para gestionar conexiones de clientes y reenviar mensajes de control.
    """
    global connected_clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(("", port))
        server_socket.listen(5)
        logging.info("Servidor TCP iniciado y escuchando en el puerto %d", SERVER_PORT)
        
        while not stop_event.is_set():
            try:
                server_socket.settimeout(1.0)
                client_socket, addr = server_socket.accept()
                logging.info("Cliente conectado desde: %s", addr[0])

                with lock:
                    connected_clients.append((client_socket, addr[0]))

                # Informar a todos los demás clientes de esta nueva IP
                notify_new_connection(addr[0])

                # Puedes notificar al otro extremo si lo necesitas
                threading.Thread(target=handle_client, args=(client_socket, addr[0]), daemon=True).start()
            except socket.timeout:
                continue
    except Exception as e:
        logging.error("Error al iniciar el servidor TCP: %s", e)
    finally:
        server_socket.close()

def handle_client(client_socket, addr):
    """
    Maneja la comunicación con los clientes conectados en el modelo 1vsN.
    """
    global host_info, is_host
    try:
        ip = addr[0]
        logging.info(f"[TCP] Cliente manejado: {ip}")

        # Si no hay host aún, este será el primero y lo usamos como host
        with lock:
            if not host_info:
                timestamp = time.time()
                update_host_info(ip, timestamp, True)  # Aquí lo marcas como no host si es un cliente, o True si decides que sea host
                logging.info(f"[HOST] Asignado host inicial: {ip}")

        while not stop_event.is_set():
            data = client_socket.recv(1024)
            if not data:
                logging.info(f"[TCP] Cliente {ip} cerró la conexión.")
                break
            logging.debug("Datos recibidos de %s: %s", ip, data.decode())

    except Exception as e:
        logging.error("Error en el manejo de cliente %s: %s", addr, e)
    finally:
        with lock:
            connected_clients[:] = [(c, i) for c, i in connected_clients if c != client_socket]
        client_socket.close()
        logging.info("Conexión con %s cerrada", addr)


def notify_new_connection(new_ip):
    """
    Envía la IP del nuevo cliente a todos los demás clientes.
    """
    global connected_clients
    for client, ip in connected_clients:
        try:
            message = f"NEW_CLIENT:{new_ip}".encode()
            client.sendall(message)
        except Exception as e:
            logging.warning("Error al notificar a un cliente: %s", e)



# =================== INTERFAZ GRÁFICA CON TKINTER ===================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("God Loquete")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Ruta de la imagen
        ruta_imagen = r"god_loquete.png"
        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize((400, 300), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(imagen)
        
        self.image_label = tk.Label(self, image=self.photo)
        self.image_label.pack(pady=10)
        
        # Título
        self.title_label = tk.Label(self, text="God Loquete", font=("Arial", 24))
        self.title_label.pack(pady=10)
        
        # Campo de estado de conexión
        self.status_label = tk.Label(self, text="Desconectado", font=("Arial", 14))
        self.status_label.pack(pady=5)
        
        # Botones para Entrar y Salir
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        self.entrar_btn = tk.Button(button_frame, text="Entrar", command=self.connect)
        self.entrar_btn.pack(side="left", padx=10)
        self.salir_btn = tk.Button(button_frame, text="Salir", command=self.disconnect)
        self.salir_btn.pack(side="right", padx=10)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.running = True

        # Inicia la comprobación periódica de cambio de rol
        self.check_role_change()

    def check_role_change(self):
        """Actualiza la etiqueta de estado si el rol cambia (cliente/host)."""
        global current_role, role_changed
        if role_changed.is_set():
            if current_role:
                self.status_label.config(text=f"Conectado ({current_role})")
            role_changed.clear()
        self.after(1000, self.check_role_change)  # Llama de nuevo cada segundo

    def update_status(self, estado):
        """Permite actualizar el estado desde otras funciones."""
        self.status_label.config(text=estado)
        
    def connect(self):
        """Se ejecuta al pulsar 'Entrar': inicia los hilos para audio, heartbeat y conexión."""
        global stop_event, host_info, join_timestamp
        print("Conectando a la llamada de voz...")
        self.update_status("Conectando...")
        stop_event.clear()
        host_info = None  # Restablecer a un valor predeterminado
        join_timestamp = time.time()  # Actualizamos el timestamp de unión al conectarse
        
        threading.Thread(target=start_audio_playback, daemon=True).start()# Inicia reproducción de audio (recepción)
        threading.Thread(target=heartbeat_listener, daemon=True).start()# Inicia escucha de heartbeats
        threading.Thread(target=check_heartbeat, args=(self.update_status,), daemon=True).start()# Inicia verificación de heartbeats y elección de host
        threading.Thread(target=start_server_for_audio, daemon=True).start()  # Inicia el servidor para audio

        time.sleep(1)

        with lock:
            if host_info is not None:
                server_ip = host_info[0]
            else:
                server_ip = get_ip()

        # Inicia captura y transmisión de audio
        threading.Thread(target=start_audio_capture, daemon=True).start()
        threading.Thread(target=start_audio_unicast, daemon=True).start()
        self.update_status("Conectado (Cliente)")

    def disconnect(self):
        """Se ejecuta al pulsar 'Salir': detiene hilos y actualiza la interfaz."""
        global is_host, host_info, last_heartbeat
        print("Desconectando de la llamada de voz...")
        is_host = False
        host_info = None  # Restablecer a un valor predeterminado
        with lock:
            last_heartbeat = time.time()
        self.update_status("Desconectado")
        stop_event.set()

    def on_close(self):
        """Maneja el cierre de la aplicación."""
        self.disconnect()
        self.running = False
        self.destroy()


# =================== EJECUCIÓN PRINCIPAL ===================

if __name__ == "__main__":
    app = App()
    app.mainloop()
