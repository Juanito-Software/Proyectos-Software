"""
Módulo de captura de audio en tiempo real
Captura audio del micrófono en trozos configurables
"""
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time
import threading

# Configuración por defecto
DEFAULT_SAMPLE_RATE = 16000  # Whisper funciona mejor con 16kHz
DEFAULT_CHANNELS = 1  # Mono
DEFAULT_DURATION = 30  # Segundos por defecto

class LiveAudioRecorder:
    """Clase para capturar audio en tiempo real del micrófono"""
    
    def __init__(self, sample_rate=DEFAULT_SAMPLE_RATE, channels=DEFAULT_CHANNELS):
        """
        Inicializa el grabador de audio
        
        Args:
            sample_rate: Tasa de muestreo (por defecto 16000)
            channels: Número de canales (1 = mono, 2 = estéreo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_data = None
        
    def record_chunk(self, duration=DEFAULT_DURATION, filename="live.wav"):
        """
        Graba un trozo de audio del micrófono
        
        Args:
            duration: Duración de la grabación en segundos
            filename: Nombre del archivo donde guardar el audio
        
        Returns:
            str: Ruta al archivo de audio grabado
        """
        print("\n" + "="*70)
        print("  GRABANDO AUDIO...")
        print("="*70)
        print(f"[DURACION] {duration} segundos")
        print("[AVISO] Empieza a hablar AHORA")
        print("[AVISO] La grabación comenzará en 2 segundos...")
        print("="*70)
        
        # Cuenta regresiva
        for i in range(2, 0, -1):
            print(f"[{i}...]", end=" ", flush=True)
            time.sleep(1)
        
        print("\n[GRABANDO] Habla ahora...")
        print("="*70)
        
        try:
            # Grabar audio
            frames = int(duration * self.sample_rate)
            audio = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()  # Esperar a que termine la grabación
            
            # Convertir a int16 para guardar como WAV
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Guardar archivo
            write(filename, self.sample_rate, audio_int16)
            
            print(f"\n[OK] Audio guardado en {filename} ({duration}s)")
            return filename
            
        except Exception as e:
            print(f"[ERROR] Error al grabar audio: {e}")
            raise
    
    def record_until_silence(self, silence_threshold=0.01, max_duration=10, filename="live.wav"):
        """
        Graba audio hasta detectar silencio o alcanzar duración máxima
        
        Args:
            silence_threshold: Umbral de silencio (0.0-1.0)
            max_duration: Duración máxima en segundos
            filename: Nombre del archivo donde guardar
        
        Returns:
            str: Ruta al archivo de audio grabado
        """
        print(f"[GRABANDO] Escuchando hasta silencio (máx {max_duration}s)...")
        
        try:
            chunk_duration = 0.5  # Analizar cada 0.5 segundos
            chunks = []
            silence_count = 0
            silence_required = 2  # 1 segundo de silencio para parar
            
            start_time = time.time()
            
            while (time.time() - start_time) < max_duration:
                # Grabar chunk pequeño
                frames = int(chunk_duration * self.sample_rate)
                chunk = sd.rec(
                    frames,
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype='float32'
                )
                sd.wait()
                
                chunks.append(chunk)
                
                # Calcular nivel de audio
                audio_level = np.abs(chunk).mean()
                
                if audio_level < silence_threshold:
                    silence_count += 1
                    if silence_count >= silence_required:
                        print("[SILENCIO] Detectado, finalizando grabación...")
                        break
                else:
                    silence_count = 0
                    print(".", end="", flush=True)
            
            # Concatenar todos los chunks
            if chunks:
                audio = np.concatenate(chunks, axis=0)
                # Convertir a int16
                audio_int16 = (audio * 32767).astype(np.int16)
                # Guardar
                write(filename, self.sample_rate, audio_int16)
                duration = len(audio) / self.sample_rate
                print(f"\n[OK] Audio guardado ({duration:.2f}s) en {filename}")
                return filename
            else:
                raise ValueError("No se grabó ningún audio")
                
        except Exception as e:
            print(f"\n[ERROR] Error en grabación por silencio: {e}")
            raise
    
    def list_devices(self):
        """Lista todos los dispositivos de audio disponibles"""
        print("\n[DEVICES] Dispositivos de audio disponibles:")
        print(sd.query_devices())
        return sd.query_devices()
    
    def set_device(self, device_id):
        """
        Configura el dispositivo de entrada a usar
        
        Args:
            device_id: ID del dispositivo (ver list_devices())
        """
        sd.default.device = device_id
        print(f"[CONFIG] Dispositivo configurado: {device_id}")

def record_chunk(duration=DEFAULT_DURATION, filename="live.wav", sample_rate=DEFAULT_SAMPLE_RATE):
    """
    Función de conveniencia para grabar un trozo de audio
    
    Args:
        duration: Duración en segundos
        filename: Nombre del archivo
        sample_rate: Tasa de muestreo
    
    Returns:
        str: Ruta al archivo grabado
    """
    recorder = LiveAudioRecorder(sample_rate=sample_rate)
    return recorder.record_chunk(duration, filename)

