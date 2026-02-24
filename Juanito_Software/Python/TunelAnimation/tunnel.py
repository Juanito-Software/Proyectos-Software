"""
Túnel psicodélico infinito - Motor de renderizado en tiempo real.
Optimizado y preparado para reacción a audio (beat, FFT, amplitud).
"""
from __future__ import annotations

import math
import sys
from typing import Tuple

import numpy as np
import pygame

# --- Configuración por defecto (ajustable para audio más adelante) ---
WIDTH = 1280
HEIGHT = 720
FPS = 60
RINGS = 48
SEGMENTS = 80
TUNNEL_SPEED = 0.8
ROTATION_SPEED = 0.12
HUE_SPEED = 0.5
# Gancho para audio: valores 0.0–1.0 (conectar a FFT/beat más adelante).
# Puedes asignar desde otro módulo: tunnel.AUDIO_ENERGY = valor
AUDIO_ENERGY = 0.0
AUDIO_BASS = 0.0
AUDIO_BEAT = 0.0


def set_audio(energy: float = None, bass: float = None, beat: float = None) -> None:
    """Actualiza los valores de audio para reacción en tiempo real."""
    global AUDIO_ENERGY, AUDIO_BASS, AUDIO_BEAT
    if energy is not None:
        AUDIO_ENERGY = max(0.0, min(1.0, float(energy)))
    if bass is not None:
        AUDIO_BASS = max(0.0, min(1.0, float(bass)))
    if beat is not None:
        AUDIO_BEAT = max(0.0, min(1.0, float(beat)))


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convierte HSV (h 0–360, s/v 0–1) a RGB 0–255."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


class TunnelEngine:
    """
    Motor del túnel: anillos en perspectiva, colores HSV y rotación.
    Usa numpy y geometría precalculada para máximo rendimiento.
    """

    def __init__(
        self,
        width: int = WIDTH,
        height: int = HEIGHT,
        rings: int = RINGS,
        segments: int = SEGMENTS,
    ):
        self.width = width
        self.height = height
        self.center = (width / 2, height / 2)
        self.rings = rings
        self.segments = segments
        # Profundidades de cada anillo (z); se actualizan cada frame
        self.depths = np.linspace(0.4, 4.0, rings, dtype=np.float64)
        self.max_depth = 4.0
        self.min_depth = 0.15
        # Ángulos para cada segmento del anillo (precalculado)
        self.angles = np.linspace(0, 2 * np.pi, segments, dtype=np.float64, endpoint=False)
        self.cos_a = np.cos(self.angles)
        self.sin_a = np.sin(self.angles)
        # Tiempo interno para animación
        self.time = 0.0
        # Factor de perspectiva (FOV): radio aparente = scale / z
        self.scale = min(width, height) * 0.45
        # Grosor de línea y brillo base (modulables por audio)
        self.line_thickness = 2
        self.glow = 1.0

    def get_audio_factors(self) -> Tuple[float, float, float]:
        """Devuelve factores actuales de audio (módulo global o inyectado)."""
        return (AUDIO_ENERGY, AUDIO_BASS, AUDIO_BEAT)

    def update(self, dt: float) -> None:
        """Avanza la simulación y mueve el túnel."""
        energy, bass, beat = self.get_audio_factors()
        # Reacción muy visible: velocidad desde 0.4 hasta 2.2
        speed = 0.4 + 1.8 * (0.4 * energy + 0.6 * bass + 0.2)
        self.depths -= dt * speed
        self.time += dt
        # Recolocar anillos que salen por delante (túnel infinito)
        step = (self.max_depth - self.min_depth) / self.rings
        behind = self.depths < self.min_depth
        n_behind = np.sum(behind)
        if n_behind > 0:
            back_z = self.depths[~behind].max() if np.any(~behind) else self.max_depth
            self.depths[behind] = back_z + step * np.arange(1, n_behind + 1, dtype=np.float64)

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el túnel en la superficie (de atrás hacia delante)."""
        energy, bass, beat = self.get_audio_factors()
        # Ordenar por profundidad (dibujar los lejanos primero)
        order = np.argsort(self.depths)[::-1]
        time = self.time
        rot = time * ROTATION_SPEED + 1.2 * beat
        hue_offset = time * HUE_SPEED * 60 + 30 * energy  # grados

        for i in order:
            z = self.depths[i]
            if z < self.min_depth:
                continue
            # Radio proyectado
            r = self.scale / z
            if r < 1:
                continue
            if r > max(self.width, self.height) * 0.8:
                continue
            # Rotación del anillo
            cos_r = math.cos(rot + z * 0.5)
            sin_r = math.sin(rot + z * 0.5)
            xs = self.center[0] + r * (self.cos_a * cos_r - self.sin_a * sin_r)
            ys = self.center[1] + r * (self.cos_a * sin_r + self.sin_a * cos_r)
            # Color HSV: hue avanza con profundidad y tiempo
            hue = (hue_offset + z * 80 + i * 6) % 360
            sat = 0.85 + 0.15 * math.sin(time * 2 + z)
            # Brillo muy ligado al audio: sin audio ~0.7, con audio hasta 1.0
            val = 0.65 + 0.35 * (0.5 * energy + 0.5 * bass) + 0.08 * math.sin(time * 1.5 + i * 0.3)
            val = min(1.0, val)
            color = hsv_to_rgb(hue, sat, val)
            # Grosor muy variable con los graves: 1 a 5
            thick = max(1, min(5, int(1 + 4 * bass)))
            pts = list(zip(xs.astype(int), ys.astype(int)))
            if len(pts) > 1:
                pygame.draw.aalines(surface, color, True, pts)
                pygame.draw.lines(surface, color, True, pts, thick)

        # Núcleo central que pulsa con el beat
        pulse = 0.4 + 0.4 * math.sin(time * 3) + 0.5 * beat + 0.2 * energy
        r_core = int(6 + 14 * pulse)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.center[0]), int(self.center[1])), r_core)

        # Indicador de nivel de audio (esquina inferior) para ver si llega señal
        self._draw_audio_levels(surface, energy, bass, beat)

    def _draw_audio_levels(self, surface: pygame.Surface, energy: float, bass: float, beat: float) -> None:
        """Dibuja barras E/B/Beat en la esquina para comprobar que llega audio."""
        try:
            font = pygame.font.Font(None, 28)
            x0, y0 = 20, self.height - 70
            w_bar, h_bar = 120, 12
            for i, (label, val) in enumerate([("E", energy), ("B", bass), ("Beat", beat)]):
                y = y0 + i * 22
                text = font.render("%s %.2f" % (label, val), True, (200, 200, 200))
                surface.blit(text, (x0, y - 2))
                pygame.draw.rect(surface, (60, 60, 60), (x0 + 55, y, w_bar, h_bar))
                pygame.draw.rect(surface, (100, 200, 100), (x0 + 55, y, int(w_bar * val), h_bar))
        except Exception:
            pass


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Túnel psicodélico infinito")
    parser.add_argument("--demo-audio", action="store_true", help="Simula audio (sin micrófono)")
    parser.add_argument("--device", type=int, default=None, help="Índice del dispositivo de entrada (ver lista al ejecutar)")
    args = parser.parse_args()

    fake_gen = None
    audio_capture_started = False

    if args.demo_audio:
        from audio_stub import fake_audio_generator
        fake_gen = fake_audio_generator()
    else:
        try:
            from audio_capture import start as start_audio_capture
            audio_capture_started = start_audio_capture(device_index=args.device)
        except Exception:
            audio_capture_started = False
        if not audio_capture_started:
            from audio_stub import fake_audio_generator
            fake_gen = fake_audio_generator()

    pygame.init()
    pygame.display.set_caption("Túnel psicodélico infinito — Audio en tiempo real" if audio_capture_started else "Túnel psicodélico infinito — Demo audio")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    engine = TunnelEngine(width=WIDTH, height=HEIGHT, rings=RINGS, segments=SEGMENTS)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if fake_gen is not None:
            e, b, beat = next(fake_gen)
            set_audio(energy=e, bass=b, beat=beat)
        engine.update(dt)
        screen.fill((0, 0, 0))
        engine.draw(screen)
        pygame.display.flip()

    if audio_capture_started:
        try:
            from audio_capture import stop as stop_audio_capture
            stop_audio_capture()
        except Exception:
            pass
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
