# Copyright (C) 2025 JuanitoSoftware
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

"""
Modo Moderador Absoluto - Sistema en Tiempo Real
Los agentes escuchan SIEMPRE tu micrófono, pero solo hablan cuando tú lo ordenas
"""
from modules.live_audio import LiveAudioRecorder, record_chunk
from modules.stt_whisper import transcribe
from agents.agent_A import agentA_process_text
from agents.agent_B import agentB_process_text
import time
import random
import os
import threading
import keyboard

# Configuración
AUDIO_FILE = "live.wav"
RECORD_DURATION = 30  # Segundos de grabación por defecto
DEBATE_MODE = False
DEBATE_ACTIVE = False
DEBATE_INTERRUPT_FOR_INPUT = False  # Flag para interrumpir debate y grabar input del usuario
DEBATE_STATE = None  # Estado del debate para poder continuar después de interrupción

def show_help():
    """Muestra la ayuda de comandos"""
    print("\n" + "="*70)
    print("  MODO MODERADOR ABSOLUTO - COMANDOS DISPONIBLES")
    print("="*70)
    print("\nComandos principales:")
    print("  [A]     - Preguntar solo a Franco (político/crítico)")
    print("  [B]     - Preguntar solo a Lenin (filosófico/reflexivo)")
    print("  [AB]    - Preguntar a ambas IAs (responden en orden aleatorio)")
    print("  [DEBATE] - Iniciar debate entre IAs (se contestan entre sí)")
    print("  [Ctrl+B] - Detener debate o cualquier proceso activo (atajo de teclado)")
    print("  [Ctrl+N] - Interrumpir debate, añadir tu voz y continuar (solo en debate)")
    print("  [SALIR] - Salir del sistema")
    print("\nComandos adicionales:")
    print("  [H]     - Mostrar esta ayuda")
    print("  [D]     - Listar dispositivos de audio")
    print("  [T]     - Cambiar duración de grabación (10s, 20s, 30s, 60s)")
    print("="*70 + "\n")

def process_with_agent(agent_func, agent_name, text, check_debate_active=False, is_debate=False):
    """
    Procesa texto con un agente específico
    
    Args:
        agent_func: Función del agente a usar
        agent_name: Nombre del agente (para mostrar)
        text: Texto a procesar
        check_debate_active: Si True, verifica DEBATE_ACTIVE antes de procesar
        is_debate: Si True, el agente puede debatir (hablar sobre el otro, darle razón, argumentar)
    """
    global DEBATE_ACTIVE
    
    # Si estamos en modo debate y el debate fue detenido, no procesar
    if check_debate_active and not DEBATE_ACTIVE:
        return None
    
    if not text or not text.strip():
        print(f"[AVISO] No se detectó texto válido para {agent_name}")
        return None
    
    print(f"\n[PROCESANDO] {agent_name} está pensando...")
    print(f"[TEXTO] Usuario dijo: {text}")
    
    try:
        # Pasar is_debate al agente si la función lo acepta
        if is_debate:
            response = agent_func(text, is_debate=True)
        else:
            response = agent_func(text)
        
        # Verificar nuevamente después de procesar (por si se detuvo durante el procesamiento)
        if check_debate_active and not DEBATE_ACTIVE:
            return None
            
        if response:
            print(f"[OK] {agent_name} respondió correctamente")
            return response
        else:
            print(f"[ERROR] {agent_name} no pudo generar respuesta")
            return None
    except Exception as e:
        print(f"[ERROR] Error al procesar con {agent_name}: {e}")
        return None

def ask_agent_A(recorder, text=None):
    """Pregunta solo a Franco"""
    global DEBATE_ACTIVE
    
    if text is None:
        # Grabar audio
        audio_file = recorder.record_chunk(RECORD_DURATION, AUDIO_FILE)
        # Transcribir
        text = transcribe(audio_file)
    
    DEBATE_ACTIVE = False
    return process_with_agent(agentA_process_text, "FRANCO", text)

def ask_agent_B(recorder, text=None):
    """Pregunta solo a Lenin"""
    global DEBATE_ACTIVE
    
    if text is None:
        # Grabar audio
        audio_file = recorder.record_chunk(RECORD_DURATION, AUDIO_FILE)
        # Transcribir
        text = transcribe(audio_file)
    
    DEBATE_ACTIVE = False
    return process_with_agent(agentB_process_text, "LENIN", text)

def ask_both_agents(recorder, text=None):
    """Pregunta a ambas IAs (orden aleatorio)"""
    global DEBATE_ACTIVE
    
    if text is None:
        # Grabar audio
        audio_file = recorder.record_chunk(RECORD_DURATION, AUDIO_FILE)
        # Transcribir
        text = transcribe(audio_file)
    
    DEBATE_ACTIVE = False
    
    # Orden aleatorio
    agents = [
        (agentA_process_text, "FRANCO"),
        (agentB_process_text, "LENIN")
    ]
    random.shuffle(agents)
    
    print("\n[AMBAS] Ambas IAs van a responder en orden aleatorio...")
    
    responses = []
    for agent_func, agent_name in agents:
        response = process_with_agent(agent_func, agent_name, text)
        if response:
            responses.append((agent_name, response))
        time.sleep(1)  # Pausa entre respuestas
    
    return responses

def start_debate(recorder, initial_text=None, max_rounds=4):
    """
    Inicia un debate entre las IAs
    
    Args:
        recorder: Grabador de audio
        initial_text: Texto inicial (si None, graba audio)
        max_rounds: Número máximo de rondas (por defecto 4)
    """
    global DEBATE_MODE, DEBATE_ACTIVE, DEBATE_INTERRUPT_FOR_INPUT, RECORD_DURATION
    
    if initial_text is None:
        # Grabar audio inicial
        audio_file = recorder.record_chunk(RECORD_DURATION, AUDIO_FILE)
        # Transcribir
        initial_text = transcribe(audio_file)
    
    if not initial_text or not initial_text.strip():
        print("[ERROR] No se pudo obtener texto inicial para el debate")
        return
    
    DEBATE_MODE = True
    DEBATE_ACTIVE = True
    
    print("\n" + "="*70)
    print("  DEBATE INICIADO")
    print("="*70)
    print(f"[TEMA] {initial_text}")
    print(f"[RONDAS] Máximo {max_rounds} rondas")
    print("\n[AVISO] Las IAs debatirán entre sí.")
    print("[AVISO] El debate se detendrá automáticamente después de las rondas.")
    print("[AVISO] Presiona Ctrl+B en cualquier momento para detener el debate.")
    print("[AVISO] Presiona Ctrl+N para interrumpir, añadir tu voz y continuar el debate.")
    print("="*70 + "\n")
    
    # Primera ronda: ambas responden al tema inicial (NO es debate aún, solo responden)
    print("[Ronda 1] Respuestas iniciales...")
    
    # Verificar antes de cada procesamiento
    if not DEBATE_ACTIVE:
        return
    
    # Primera ronda: is_debate=False (solo responden al tema, no debaten)
    response_a = process_with_agent(agentA_process_text, "FRANCO", initial_text, check_debate_active=True, is_debate=False)
    
    if not DEBATE_ACTIVE:
        return
    
    time.sleep(1)
    
    if not DEBATE_ACTIVE:
        return
    
    # Primera ronda: is_debate=False (solo responden al tema, no debaten)
    response_b = process_with_agent(agentB_process_text, "LENIN", initial_text, check_debate_active=True, is_debate=False)
    
    if not DEBATE_ACTIVE:
        return
    
    # Continuar debate hasta que se pare o se alcance el máximo
    round_num = 2
    last_response_a = response_a
    last_response_b = response_b
    next_agent_is_a = True  # True = siguiente es Franco, False = siguiente es Lenin
    
    while DEBATE_ACTIVE and DEBATE_MODE and round_num <= max_rounds:
        # Verificar inmediatamente al inicio de cada iteración
        if not DEBATE_ACTIVE:
            break
        
        # Verificar si se solicitó interrupción para input del usuario
        if DEBATE_INTERRUPT_FOR_INPUT:
            DEBATE_INTERRUPT_FOR_INPUT = False  # Resetear flag
            
            print("\n" + "="*70)
            print("  [Ctrl+N] GRABANDO INPUT DEL USUARIO")
            print("="*70)
            print(f"[AVISO] Se grabarán {RECORD_DURATION} segundos de audio")
            print("[AVISO] El debate continuará con el siguiente agente después de tu input.")
            print("="*70 + "\n")
            
            # Grabar audio del usuario
            audio_file = recorder.record_chunk(RECORD_DURATION, AUDIO_FILE)
            user_input = transcribe(audio_file)
            
            if not user_input or not user_input.strip():
                print("[AVISO] No se detectó input válido. Continuando el debate...")
            else:
                print(f"[INPUT] Usuario dijo: {user_input}")
                # Continuar con el siguiente agente usando el input del usuario
                if next_agent_is_a:
                    # El siguiente es Franco, usar input del usuario como contexto
                    context = f"El usuario interrumpió y dijo: {user_input}. Lenin había dicho: {last_response_b}"
                    last_response_a = process_with_agent(
                        agentA_process_text,
                        "FRANCO",
                        context,
                        check_debate_active=True,
                        is_debate=True
                    )
                    if not DEBATE_ACTIVE:
                        break
                    next_agent_is_a = False  # Siguiente será Lenin
                else:
                    # El siguiente es Lenin, usar input del usuario como contexto
                    context = f"El usuario interrumpió y dijo: {user_input}. Franco había dicho: {last_response_a}"
                    last_response_b = process_with_agent(
                        agentB_process_text,
                        "LENIN",
                        context,
                        check_debate_active=True,
                        is_debate=True
                    )
                    if not DEBATE_ACTIVE:
                        break
                    next_agent_is_a = True  # Siguiente será Franco
                    round_num += 1  # Incrementar ronda después de B
                
                time.sleep(1)
                if not DEBATE_ACTIVE:
                    break
                continue  # Continuar el bucle sin procesar el turno normal
            
        # Si no hay interrupción pendiente, continuar con el turno normal
        if not DEBATE_INTERRUPT_FOR_INPUT:
            print(f"\n[DEBATE] Ronda {round_num}/{max_rounds}")
            
            # Franco responde a lo que dijo Lenin (MODO DEBATE: puede debatir)
            if last_response_b and DEBATE_ACTIVE and next_agent_is_a:
                # En modo debate: puede hablar sobre lo que dijo el otro, darle razón, o argumentar en contra
                context = f"Lenin dijo: {last_response_b}"
                last_response_a = process_with_agent(
                    agentA_process_text, 
                    "FRANCO", 
                    context,
                    check_debate_active=True,
                    is_debate=True  # Modo debate activado
                )
                
                # Verificar después de cada procesamiento
                if not DEBATE_ACTIVE:
                    break
                
                # Si se solicitó interrupción durante el procesamiento, se manejará en la siguiente iteración
                if not DEBATE_INTERRUPT_FOR_INPUT:
                    time.sleep(1)
                    if not DEBATE_ACTIVE:
                        break
                    next_agent_is_a = False  # Siguiente será Lenin
                # Si hay interrupción, continuar al inicio del bucle para manejarla
            
            # Lenin responde a lo que dijo Franco (MODO DEBATE: puede debatir)
            elif last_response_a and DEBATE_ACTIVE and not next_agent_is_a:
                # En modo debate: puede hablar sobre lo que dijo el otro, darle razón, o argumentar en contra
                context = f"Franco dijo: {last_response_a}"
                last_response_b = process_with_agent(
                    agentB_process_text, 
                    "LENIN", 
                    context,
                    check_debate_active=True,
                    is_debate=True  # Modo debate activado
                )
                
                # Verificar después de cada procesamiento
                if not DEBATE_ACTIVE:
                    break
                
                # Si se solicitó interrupción durante el procesamiento, se manejará en la siguiente iteración
                if not DEBATE_INTERRUPT_FOR_INPUT:
                    time.sleep(1)
                    if not DEBATE_ACTIVE:
                        break
                    next_agent_is_a = True  # Siguiente será Franco
                    round_num += 1  # Incrementar ronda después de B
                # Si hay interrupción, continuar al inicio del bucle para manejarla
    
    # Asegurar que las variables estén limpias ANTES de verificar el estado
    debate_was_stopped = not DEBATE_ACTIVE
    DEBATE_MODE = False
    DEBATE_ACTIVE = False
    
    if round_num > max_rounds:
        print(f"\n[DEBATE] Debate completado ({max_rounds} rondas)")
    elif debate_was_stopped:
        # El debate fue detenido por el usuario (Ctrl+B)
        # El mensaje ya se mostró en stop_debate()
        print("\n[OK] Debate detenido. Retornando al menú principal...")
    else:
        print("\n[DEBATE] Debate detenido por el usuario")
    
    # Retornar al bucle principal - el programa continúa normalmente
    # El bucle principal mostrará el prompt "[COMANDO] >> " automáticamente

def stop_debate():
    """Detiene el debate activo"""
    global DEBATE_MODE, DEBATE_ACTIVE
    if DEBATE_ACTIVE:
        DEBATE_MODE = False
        DEBATE_ACTIVE = False
        print("\n" + "="*70)
        print("  [Ctrl+B] DEBATE DETENIDO")
        print("="*70)
        print("[AVISO] El debate ha sido detenido.")
        print("[AVISO] Si un agente está procesando, espera a que termine.")
        print("[AVISO] Después podrás continuar usando el programa normalmente.")
        print("="*70)

def interrupt_debate_for_input():
    """Interrumpe el debate para grabar input del usuario y continuar"""
    global DEBATE_INTERRUPT_FOR_INPUT
    if DEBATE_ACTIVE:
        DEBATE_INTERRUPT_FOR_INPUT = True
        print("\n" + "="*70)
        print("  [Ctrl+N] INTERRUPCIÓN PARA INPUT DEL USUARIO")
        print("="*70)
        print("[AVISO] El debate se pausará después de que termine el agente actual.")
        print("[AVISO] Se grabará tu voz y el debate continuará con el siguiente agente.")
        print("="*70)

def setup_keyboard_listener():
    """Configura el listener de teclado para detectar Ctrl+B y Ctrl+N"""
    def on_ctrl_b():
        """Callback cuando se presiona Ctrl+B - solo detiene el debate, no cierra el programa"""
        global DEBATE_ACTIVE
        if DEBATE_ACTIVE:
            stop_debate()
        # No hacer nada más - el programa continúa normalmente
    
    def on_ctrl_n():
        """Callback cuando se presiona Ctrl+N - interrumpe para grabar input y continuar"""
        interrupt_debate_for_input()
    
    # Registrar los atajos
    keyboard.add_hotkey('ctrl+b', on_ctrl_b)
    keyboard.add_hotkey('ctrl+n', on_ctrl_n)
    print("[OK] Atajo de teclado Ctrl+B configurado para detener debates")
    print("[OK] Atajo de teclado Ctrl+N configurado para interrumpir y añadir input")
    print("[AVISO] Ctrl+B detiene el debate, Ctrl+N permite añadir tu voz y continuar")

def main():
    """Función principal del modo moderador"""
    global RECORD_DURATION
    
    print("\n" + "="*70)
    print("  MODO MODERADOR ABSOLUTO - SISTEMA EN TIEMPO REAL")
    print("="*70)
    print("\n[INICIO] Sistema iniciado. Los agentes están escuchando...")
    print("[AVISO] Usa 'H' para ver la ayuda de comandos\n")
    
    # Configurar listener de teclado para Ctrl+B
    try:
        setup_keyboard_listener()
    except Exception as e:
        print(f"[AVISO] No se pudo configurar el atajo de teclado: {e}")
        print("[AVISO] El comando 'PARAR' seguirá disponible como alternativa")
    
    # Inicializar grabador de audio
    recorder = LiveAudioRecorder()
    
    # Mostrar dispositivos disponibles
    try:
        devices = recorder.list_devices()
    except:
        pass
    
    show_help()
    
    while True:
        try:
            cmd = input("\n[COMANDO] >> ").strip().upper()
            
            if not cmd:
                continue
            
            # Comandos de control
            if cmd == "S" or cmd == "SALIR":
                if DEBATE_ACTIVE:
                    stop_debate()
                print("\n[SALIR] Saliendo del sistema...")
                break
            
            elif cmd == "H" or cmd == "AYUDA":
                show_help()
                continue
            
            elif cmd == "D" or cmd == "DISPOSITIVOS":
                recorder.list_devices()
                continue
            
            elif cmd == "T" or cmd == "TIEMPO":
                print(f"\n[Tiempo actual: {RECORD_DURATION}s]")
                new_duration = input("Nueva duración (10, 20, 30, 60): ").strip()
                try:
                    new_dur = int(new_duration)
                    if new_dur >= 5 and new_dur <= 120:
                        RECORD_DURATION = new_dur
                        print(f"[OK] Duración configurada a {RECORD_DURATION}s")
                    else:
                        print("[ERROR] Duración debe estar entre 5 y 120 segundos")
                except:
                    print("[ERROR] Duración no válida")
                continue
            
            elif cmd == "PARAR" or cmd == "STOP":
                # Mantener como alternativa al atajo de teclado
                if DEBATE_ACTIVE:
                    stop_debate()
                else:
                    print("[AVISO] No hay debate activo para detener")
                continue
            
            # Comandos de agentes
            elif cmd == "A":
                print("\n" + "="*70)
                print("  FRANCO - PREPARADO PARA ESCUCHAR")
                print("="*70)
                print(f"[AVISO] Se grabarán {RECORD_DURATION} segundos de audio")
                print("[AVISO] Empieza a hablar cuando veas el mensaje 'GRABANDO...'")
                print("="*70)
                time.sleep(1)  # Pausa para que lea el mensaje
                ask_agent_A(recorder)
            
            elif cmd == "B":
                print("\n" + "="*70)
                print("  LENIN - PREPARADO PARA ESCUCHAR")
                print("="*70)
                print(f"[AVISO] Se grabarán {RECORD_DURATION} segundos de audio")
                print("[AVISO] Empieza a hablar cuando veas el mensaje 'GRABANDO...'")
                print("="*70)
                time.sleep(1)  # Pausa para que lea el mensaje
                ask_agent_B(recorder)
            
            elif cmd == "AB" or cmd == "AMBAS":
                print("\n" + "="*70)
                print("  AMBAS IAs - PREPARADAS PARA ESCUCHAR")
                print("="*70)
                print(f"[AVISO] Se grabarán {RECORD_DURATION} segundos de audio")
                print("[AVISO] Empieza a hablar cuando veas el mensaje 'GRABANDO...'")
                print("="*70)
                time.sleep(1)  # Pausa para que lea el mensaje
                ask_both_agents(recorder)
            
            elif cmd == "DEBATE":
                print("\n" + "="*70)
                print("  DEBATE - PREPARADO PARA ESCUCHAR TEMA INICIAL")
                print("="*70)
                print(f"[AVISO] Se grabarán {RECORD_DURATION} segundos de audio")
                print("[AVISO] Empieza a hablar cuando veas el mensaje 'GRABANDO...'")
                print("="*70)
                time.sleep(1)  # Pausa para que lea el mensaje
                start_debate(recorder)
            
            else:
                print(f"\n[ERROR] Comando '{cmd}' no reconocido.")
                print("[AVISO] Usa 'H' para ver la ayuda")
        
        except KeyboardInterrupt:
            if DEBATE_ACTIVE:
                stop_debate()
            print("\n\n[AVISO] Interrupción del usuario. Saliendo...")
            break
        
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Limpiar el listener de teclado al salir
    try:
        keyboard.unhook_all()
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Asegurar limpieza del listener de teclado
        try:
            keyboard.unhook_all()
        except:
            pass

