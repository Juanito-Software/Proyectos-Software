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

# --- CABEZA: importa lo que ya tienes ---
import pygame
import random
import math
import numpy as np
import soundcard as sc
import threading
import queue
import time

# ==========================
# CONFIGURACIÓN PRINCIPAL
# ==========================
W, H = 1080, 720
N = 30          # menos partículas
G = 40
VEL_MAX = 5
INTER_PARTICLE_FORCE = 0.05

# ==========================
# CONFIG AUDIO
# ==========================
SAMPLERATE = 44100       # más bajo para fluidez
BLOCKSIZE = 256        # más pequeño para latencia
SENSIBILIDAD = 6.0       # ajustar a gusto
SUAVIZADO = 0.3

# ==========================
# INICIALIZA PYGAME
# ==========================
pygame.init()
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Simulación 2D - Sol reactivo al sonido")
clock = pygame.time.Clock()
# Superficie interna a resolución fija (base); la ventana se puede redimensionar
canvas = pygame.Surface((W, H))
window_w, window_h = W, H

# ==========================
# CREACIÓN DE PARTÍCULAS
# ==========================
particles = []
for _ in range(N):
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    vx = random.uniform(-0.2, 0.2)
    vy = random.uniform(-0.2, 0.2)
    m = random.uniform(1, 2)   # masa
    r = random.randint(2, 6)   # radio visual; 2 es el mínimo actual, 6 es 3x
    particles.append([x, y, vx, vy, m, r])

# Sol central
sol = [W / 2, H / 2, 0, 0, 30]   # radio más pequeño

# ==========================
# AUDIO LOOPBACK CON SOUNDCARD
# ==========================
# escoger altavoz principal (loopback) con selector
speakers = sc.all_speakers()


def seleccionar_speaker():
    """
    Muestra los dispositivos de audio disponibles y permite seleccionar uno
    por índice, de forma similar a cómo se elige en MusicWave.py.
    """
    if not speakers:
        raise RuntimeError("No se han encontrado dispositivos de salida de audio.")

    print("\nDispositivos de audio disponibles:")
    for i, spk in enumerate(speakers):
        print(f"{i}: {spk.name}")

    while True:
        seleccion = input(
            "Selecciona el índice del dispositivo de salida a usar "
            "(ENTER para usar el 0 por defecto): "
        ).strip()

        if seleccion == "":
            return speakers[0]

        try:
            idx = int(seleccion)
        except ValueError:
            print("Por favor, introduce un número válido.")
            continue

        if 0 <= idx < len(speakers):
            return speakers[idx]
        else:
            print(f"Índice fuera de rango. Debe estar entre 0 y {len(speakers) - 1}.")


speaker = seleccionar_speaker()
nivel_suavizado = 0.0

q_audio = queue.Queue(maxsize=4)

def audio_thread():
    global nivel_suavizado
    with sc.get_microphone(speaker.name, include_loopback=True).recorder(
            samplerate=SAMPLERATE, blocksize=BLOCKSIZE) as rec:
        while True:
            data = rec.record(numframes=None)
            mono = data.mean(axis=1)  # convertir a mono
            rms = np.sqrt(np.mean(mono**2))
            level = rms * SENSIBILIDAD
            level = max(0.0, min(level, 1.0))
            nivel_suavizado = SUAVIZADO * nivel_suavizado + (1 - SUAVIZADO) * level
            try:
                q_audio.put_nowait(nivel_suavizado)
            except queue.Full:
                pass

threading.Thread(target=audio_thread, daemon=True).start()

# ==========================
# BUCLE PRINCIPAL
# ==========================
running = True
frame_count = 0
audio_level = 0.0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            window_w, window_h = event.w, event.h
            screen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)

    canvas.fill((0, 0, 0))

    # Leer último audio
    try:
        while True:
            audio_level = q_audio.get_nowait()
    except queue.Empty:
        pass

    # tamaño del sol
    size_factor = 0.5 + 2.5 * nivel_suavizado  # factor de tamaño más grande
    sol[4] = 30 * size_factor

    # color según nivel
    r = int(nivel_suavizado * 255)
    g = int((1 - nivel_suavizado) * 255)
    sun_color = (r, g, 0)


    # --- física simplificada ---
    for i, p1 in enumerate(particles):
        fx = fy = 0
        dx = sol[0] - p1[0]
        dy = sol[1] - p1[1]
        dist2 = dx*dx + dy*dy
        force = G * p1[4] * sol[4] / (dist2 if dist2>0 else 0.1)
        ang = math.atan2(dy, dx)
        fx += math.cos(ang) * force
        fy += math.sin(ang) * force

        for j, p2 in enumerate(particles):
            if i == j: continue
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist2 = dx*dx + dy*dy
            force = INTER_PARTICLE_FORCE * p1[4] * p2[4] / max(dist2, 0.1)
            ang = math.atan2(dy, dx)
            fx += math.cos(ang) * force
            fy += math.sin(ang) * force

        p1[2] += fx / p1[4]
        p1[3] += fy / p1[4]
        speed = math.hypot(p1[2], p1[3])
        if speed > VEL_MAX:
            p1[2] *= VEL_MAX / speed
            p1[3] *= VEL_MAX / speed

    # actualizar posiciones y dibujar
    for p in particles:
        p[0] += p[2]; p[1] += p[3]
        if p[0] < 0: p[0] = 0; p[2] *= -0.5
        if p[0] > W: p[0] = W; p[2] *= -0.5
        if p[1] < 0: p[1] = 0; p[3] *= -0.5
        if p[1] > H: p[1] = H; p[3] *= -0.5

        dx = p[0] - sol[0]; dy = p[1] - sol[1]
        if math.hypot(dx, dy) < sol[4]:
            p[0] = random.uniform(0, W); p[1] = random.uniform(0, H)
            p[2] = random.uniform(-0.2, 0.2); p[3] = random.uniform(-0.2, 0.2)
            p[4] = random.uniform(1, 2)      # masa
            p[5] = random.randint(2, 6)      # nuevo tamaño aleatorio

        pygame.draw.circle(canvas, (255,255,255), (int(p[0]), int(p[1])), p[5])

    pygame.draw.circle(canvas, sun_color, (int(sol[0]), int(sol[1])), int(sol[4]))

    # Escalar canvas (resolución base) a la ventana actual y mostrar
    if window_w > 0 and window_h > 0:
        scaled = pygame.transform.smoothscale(canvas, (window_w, window_h))
        screen.blit(scaled, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

