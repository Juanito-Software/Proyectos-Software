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

import pygame, random, math, collections

# ---------------- Configuración ----------------
W, H = 800, 600
N = 50
G = 0.5                     # gravedad del sol (ajustable)
VEL_MAX = 8                 # límite suave de velocidad
INTER_PARTICLE_FORCE = 0.01 # fuerza mutua entre partículas (muy pequeña)
SOL_SOFTENING = 20          # suavizado para fuerza del sol (evita picos enormes)
PART_SOFTENING = 5          # suavizado para interacción partícula-partícula

MIN_R = 120    # radio mínimo desde el sol en spawn inicial (evita "tragarse" muchas)
MAX_R = 300    # radio máximo de spawn
SOL_RADIUS = 50

TRAIL_LENGTH = 120     # longitud máxima de rastro por partícula
TRAIL_FADE_ALPHA = 18  # cuanto se desvanecen los rastros cada frame (0-255)

FPS = 60
DT = 1.0  # paso de integración (puedes usar 1.0 / FPS si quieres)

# ---------------- Inicialización pygame ----------------
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Sistema solar emergente")
clock = pygame.time.Clock()

# Surface para pistas / trails (con alpha)
trail_surf = pygame.Surface((W, H), pygame.SRCALPHA)

# Sol en el centro, con masa grande
sol = [W/2, H/2, 0.0, 0.0, 200.0]  # x, y, vx, vy, masa (masa del Sol aumentada para estabilidad)

# ---------------- Crear partículas ----------------
# cada partícula: [x, y, vx, vy, m, trail_deque]
particles = []
for _ in range(N):
    phi = random.uniform(0, 2*math.pi)
    r = random.uniform(MIN_R, MAX_R)
    x = sol[0] + r * math.cos(phi)
    y = sol[1] + r * math.sin(phi)
    m = random.uniform(0.6, 2.8)

    # velocidad orbital circular básica
    v_circ = math.sqrt(G * sol[4] / r)
    # perturbación para órbitas elípticas: escala tangencial + pequeña componente radial
    tangential_scale = random.uniform(0.95, 1.08)   # modifica a <1 o >1 para elipticidad
    radial_frac = random.uniform(-0.06, 0.06)       # componente radial para excentricidad

    vx = -v_circ * tangential_scale * math.sin(phi) + radial_frac * math.cos(phi) * v_circ
    vy =  v_circ * tangential_scale * math.cos(phi) + radial_frac * math.sin(phi) * v_circ

    trail = collections.deque(maxlen=TRAIL_LENGTH)
    trail.append((int(x), int(y)))
    particles.append([x, y, vx, vy, m, trail])

# Colores
COLOR_BG = (0, 0, 0)
COLOR_PART = (255, 255, 255)
COLOR_SOL = (255, 200, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # FONDO y desvanecer trails suavemente
    screen.fill(COLOR_BG)
    # rellenar la superficie de trails con un alpha pequeño para que se vayan desvaneciendo
    fade = (0, 0, 0, TRAIL_FADE_ALPHA)
    trail_surf.fill(fade, special_flags=pygame.BLEND_RGBA_SUB)

    # ---------- Cálculo de fuerzas ----------
    # Usamos integración semi-implícita: v += a*dt; x += v*dt
    for i, p1 in enumerate(particles):
        fx = 0.0
        fy = 0.0

        # Fuerza del Sol (atractiva), con suavizado
        dx = sol[0] - p1[0]
        dy = sol[1] - p1[1]
        dist2 = dx*dx + dy*dy + SOL_SOFTENING**2
        dist = math.sqrt(dist2)
        # fuerza = G * m1 * m2 / dist2
        f = G * p1[4] * sol[4] / dist2
        if dist > 0:
            fx += f * (dx / dist)
            fy += f * (dy / dist)

        # Interacciones partícula-partícula (atractivas, muy débiles)
        for j, p2 in enumerate(particles):
            if i == j:
                continue
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist2p = dx*dx + dy*dy + PART_SOFTENING**2
            distp = math.sqrt(dist2p)
            # fuerza proporcional a m1*m2/(r^2 + soft^2) escalada por INTER_PARTICLE_FORCE
            f2 = INTER_PARTICLE_FORCE * p1[4] * p2[4] / dist2p
            if distp > 0:
                fx += f2 * (dx / distp)
                fy += f2 * (dy / distp)

        # actualizar velocidades con aceleración = F/m
        ax = fx / p1[4]
        ay = fy / p1[4]
        p1[2] += ax * DT
        p1[3] += ay * DT

        # limitar velocidad para estabilidad visual
        speed = math.hypot(p1[2], p1[3])
        if speed > VEL_MAX:
            scale = VEL_MAX / speed
            p1[2] *= scale
            p1[3] *= scale

    # ---------- Actualizar posiciones y dibujar ----------
    for i, p in enumerate(particles):
        p[0] += p[2] * DT
        p[1] += p[3] * DT

        # Si toca (entra) en el Sol -> "destruir" y respawnear en radio seguro
        dx = p[0] - sol[0]
        dy = p[1] - sol[1]
        dist = math.hypot(dx, dy)
        if dist < SOL_RADIUS:
            # respawnear en anillo seguro con nueva velocidad orbital (ligera perturbación)
            phi = random.uniform(0, 2*math.pi)
            r = random.uniform(MIN_R, MAX_R)
            p[0] = sol[0] + r * math.cos(phi)
            p[1] = sol[1] + r * math.sin(phi)
            p[4] = random.uniform(0.6, 2.8)
            v_circ = math.sqrt(G * sol[4] / r)
            tangential_scale = random.uniform(0.97, 1.06)
            radial_frac = random.uniform(-0.04, 0.04)
            p[2] = -v_circ * tangential_scale * math.sin(phi) + radial_frac * math.cos(phi) * v_circ
            p[3] =  v_circ * tangential_scale * math.cos(phi) + radial_frac * math.sin(phi) * v_circ
            p[5].clear()
            p[5].append((int(p[0]), int(p[1])))

        # Añadir punto al rastro
        p[5].append((int(p[0]), int(p[1])))

        # Dibujar rastro en trail_surf (línea entre puntos consecutivos)
        if len(p[5]) > 1:
            pts = list(p[5])
            # color con alpha alto para que sobresalga en trail_surf
            pygame.draw.lines(trail_surf, (200, 200, 255, 190), False, pts, 1)

        # Dibujar partícula
        pygame.draw.circle(screen, COLOR_PART, (int(p[0]), int(p[1])), 2)

    # Dibujar Sol (encima de rastros y partículas)
    pygame.draw.circle(screen, COLOR_SOL, (int(sol[0]), int(sol[1])), SOL_RADIUS)

    # Blit del trail_surf (contiene las trayectorias)
    screen.blit(trail_surf, (0, 0))

    # Flip pantalla
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
