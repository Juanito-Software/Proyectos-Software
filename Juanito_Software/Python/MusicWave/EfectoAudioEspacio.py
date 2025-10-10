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
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Simulación 2D - Sol reactivo al sonido")
clock = pygame.time.Clock()

# ==========================
# CREACIÓN DE PARTÍCULAS
# ==========================
particles = []
for _ in range(N):
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    vx = random.uniform(-0.2, 0.2)
    vy = random.uniform(-0.2, 0.2)
    m = random.uniform(1, 2)   # más pequeñas
    particles.append([x, y, vx, vy, m])

# Sol central
sol = [W / 2, H / 2, 0, 0, 30]   # radio más pequeño

# ==========================
# AUDIO LOOPBACK CON SOUNDCARD
# ==========================
# escoger altavoz principal (loopback)
speakers = sc.all_speakers()
# Puedes cambiar a cualquier altavoz de la lista
speaker = speakers[2]  
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
for i, spk in enumerate(sc.all_speakers()):
    print(i, spk.name)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

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
            p[4] = random.uniform(1, 2)

        pygame.draw.circle(screen, (255,255,255), (int(p[0]), int(p[1])), 2)

    pygame.draw.circle(screen, sun_color, (int(sol[0]), int(sol[1])), int(sol[4]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

