import pygame, random, math

# Configuración
W, H = 800, 600
N = 50
G = 0.5
VEL_MAX = 5
INTER_PARTICLE_FORCE = 0.05  # fuerza entre partículas muy baja

pygame.init()
screen = pygame.display.set_mode((W, H))

# Crear partículas
particles = []
for _ in range(N):
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    vx = random.uniform(-0.2, 0.2)
    vy = random.uniform(-0.2, 0.2)
    m = random.uniform(1, 3)
    particles.append([x, y, vx, vy, m])

# Sol en el centro
sol = [W/2, H/2, 0, 0, 50]

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Calcular fuerzas
    for i, p1 in enumerate(particles):
        fx = fy = 0

        # Gravedad del sol (sin suavizado)
        dx = sol[0] - p1[0]
        dy = sol[1] - p1[1]
        dist2 = dx*dx + dy*dy
        force = G * p1[4] * sol[4] / dist2
        ang = math.atan2(dy, dx)
        fx += math.cos(ang) * force
        fy += math.sin(ang) * force

        # Fuerzas entre partículas (muy pequeñas)
        for j, p2 in enumerate(particles):
            if i == j: continue
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist2 = dx*dx + dy*dy
            force = INTER_PARTICLE_FORCE * p1[4] * p2[4] / max(dist2, 0.1)
            ang = math.atan2(dy, dx)
            fx += math.cos(ang) * force
            fy += math.sin(ang) * force

        # Actualizar velocidades
        p1[2] += fx / p1[4]
        p1[3] += fy / p1[4]

        # Limitar velocidad
        speed = math.hypot(p1[2], p1[3])
        if speed > VEL_MAX:
            p1[2] *= VEL_MAX / speed
            p1[3] *= VEL_MAX / speed

    # Actualizar posiciones y manejar colisiones con el sol
    for i, p in enumerate(particles):
        p[0] += p[2]
        p[1] += p[3]

        # Rebotes suaves para no salir de la pantalla
        if p[0] < 0: p[0] = 0; p[2] *= -0.5
        if p[0] > W: p[0] = W; p[2] *= -0.5
        if p[1] < 0: p[1] = 0; p[3] *= -0.5
        if p[1] > H: p[1] = H; p[3] *= -0.5

        # Si toca el sol, "destruir" y generar en punto aleatorio
        dx = p[0] - sol[0]
        dy = p[1] - sol[1]
        if math.hypot(dx, dy) < sol[4]:
            p[0] = random.uniform(0, W)
            p[1] = random.uniform(0, H)
            p[2] = random.uniform(-0.2, 0.2)
            p[3] = random.uniform(-0.2, 0.2)
            p[4] = random.uniform(1, 3)

        pygame.draw.circle(screen, (255, 255, 255), (int(p[0]), int(p[1])), 2)

    # Dibujar sol
    pygame.draw.circle(screen, (255, 200, 0), (int(sol[0]), int(sol[1])), int(sol[4]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
