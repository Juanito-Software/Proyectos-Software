"""
Visualización 3D en tiempo real con pygame.
Proyección ortográfica, cámara rotable, estelas y controles por teclado.
"""

from __future__ import annotations

import pygame
import numpy as np
from typing import List, Optional, Callable

from .body import Body
from .simulation import Simulation


def _pos3(pos: np.ndarray) -> np.ndarray:
    """Asegura posición 3D (rellena con 0 si es 2D)."""
    p = np.asarray(pos, dtype=float)
    if p.shape[0] == 2:
        return np.array([p[0], p[1], 0.0])
    return p if p.shape[0] >= 3 else np.array([0.0, 0.0, 0.0])


class Visualizer:
    """
    Ventana pygame que muestra la simulación en 3D.
    Proyección ortográfica: rotación en XZ (cámara alrededor del sistema), Y = arriba.
    """

    def __init__(
        self,
        width: int = 1200,
        height: int = 800,
        bg_color: tuple[int, int, int] = (15, 15, 25),
        show_trails: bool = True,
        trail_length: int = 200,
    ):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("AstroSim — Simulación N-body 3D")
        try:
            import ctypes
            if hasattr(pygame.display, "get_wm_info"):
                info = pygame.display.get_wm_info()
                hwnd = info.get("window") or info.get("hwnd")
                if hwnd and hasattr(ctypes.windll, "user32"):
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.show_trails = show_trails
        self.trail_length = trail_length
        self.trails: List[List[tuple[int, int]]] = []
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

        self.scale = 1.0
        self.center_view = np.zeros(2)  # Centro en coordenadas de vista (2D proyectado)
        self.camera_angle = 0.0  # Radianes: rotación cámara en plano XZ (0 = mirando +Z hacia -Z)

    def _project(self, pos: np.ndarray) -> np.ndarray:
        """Proyecta posición 3D a plano de vista 2D (x_vista, y_vista)."""
        x, y, z = _pos3(pos)
        c, s = np.cos(self.camera_angle), np.sin(self.camera_angle)
        xv = x * c - z * s
        yv = y
        return np.array([xv, yv])

    def _world_to_screen(self, pos: np.ndarray) -> tuple[int, int]:
        """Convierte posición 3D mundial a coordenadas de pantalla."""
        v = self._project(pos)
        sx = self.width / 2 + (v[0] - self.center_view[0]) * self.scale
        sy = self.height / 2 - (v[1] - self.center_view[1]) * self.scale
        return int(sx), int(sy)

    def _update_scale_and_center(self, bodies: List[Body], margin: float = 0.2) -> None:
        """Ajusta escala y centro según la proyección 2D actual de todos los cuerpos."""
        if not bodies:
            return
        view_pts = np.array([self._project(b.position) for b in bodies])
        min_pt = view_pts.min(axis=0)
        max_pt = view_pts.max(axis=0)
        span = max_pt - min_pt
        span[span < 1e-10] = 1e-10
        self.center_view = (min_pt + max_pt) / 2
        scale_x = self.width / (span[0] * (1 + margin))
        scale_y = self.height / (span[1] * (1 + margin))
        self.scale = min(scale_x, scale_y, 1e6)

    def _ensure_trails(self, n: int) -> None:
        while len(self.trails) < n:
            self.trails.append([])

    def draw(
        self,
        simulation: Simulation,
        fps: int = 60,
        on_key: Optional[Callable[[pygame.event.Event], bool]] = None,
    ) -> bool:
        """
        Dibuja el estado actual de la simulación.
        on_key: callback(event) -> True para consumir el evento.
        Returns: False si se recibió pygame.QUIT (cerrar).
        """
        bodies = simulation.bodies
        self._ensure_trails(len(bodies))
        self._update_scale_and_center(bodies)

        self.screen.fill(self.bg_color)

        # Trails
        if self.show_trails:
            for i, b in enumerate(bodies):
                pt = self._world_to_screen(b.position)
                self.trails[i].append(pt)
                if len(self.trails[i]) > self.trail_length:
                    self.trails[i].pop(0)
                if len(self.trails[i]) >= 2:
                    color = tuple(max(0, c - 120) for c in b.color[:3])  # Versión más tenue para trail
                    pygame.draw.lines(
                        self.screen, color, False, self.trails[i], 1
                    )

        # Cuerpos (radio ligeramente por profundidad para sensación 3D)
        for b in bodies:
            pt = self._world_to_screen(b.position)
            p3 = _pos3(b.position)
            depth = p3[0] * np.sin(self.camera_angle) + p3[2] * np.cos(self.camera_angle)
            depth_factor = 1.0 + 0.3 * np.clip(depth / 2.0, -1, 1)  # Lejos = más pequeño
            r = max(2, int(b.radius_display * depth_factor))
            pygame.draw.circle(self.screen, b.color, pt, r)
            pygame.draw.circle(self.screen, (255, 255, 255), pt, r, 1)
            label = self.font.render(b.name, True, (200, 200, 220))
            self.screen.blit(label, (pt[0] + r + 2, pt[1] - 8))

        # Info
        info = f"3D  t = {simulation.time:.1f}  G = {simulation.G:.2e}  dt = {simulation.dt}  |  [P] pausa  [E] CSV  [+/-] G  [*//] dt  [T] estelas  [Q/D] cámara  [ESC] salir"
        surf = self.font.render(info, True, (180, 180, 200))
        self.screen.blit(surf, (10, self.height - 28))

        pygame.display.flip()
        self.clock.tick(fps)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN and on_key is not None:
                # Ignorar repetición de tecla (al mantener pulsado) para que los toggles funcionen
                if not getattr(event, "repeat", False) and on_key(event):
                    pass  # consumido

        return True

    def clear_trails(self) -> None:
        self.trails = []


def run_loop(
    simulation: Simulation,
    visualizer: Visualizer,
    steps_per_frame: int = 1,
    record_interval: int = 0,
    export_path: Optional[str] = None,
) -> None:
    """
    Bucle principal: actualiza simulación y dibuja.
    record_interval: cada cuántos pasos guardar snapshot (0 = no guardar).
    export_path: si se proporciona, al cerrar se exporta CSV ahí.
    """
    from .export import export_trajectories_csv

    running = True
    paused = False
    record_counter = 0

    def on_key(event: pygame.event.Event) -> bool:
        nonlocal running, paused, steps_per_frame, record_counter
        key = event.key
        # P: pausa
        if key == pygame.K_p:
            paused = not paused
            return True
        # E: exportar CSV
        if key == pygame.K_e:
            traj = simulation.get_trajectory()
            if traj:
                path = export_path or "astro_trajectories.csv"
                export_trajectories_csv(traj, path)
                print(f"Exportado: {path}")
            return True
        # + / - : G (tecla normal y teclado numérico)
        if key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            simulation.set_G(simulation.G * 1.2)
            return True
        if key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            simulation.set_G(simulation.G / 1.2)
            return True
        # * / : dt (tecla normal y teclado numérico)
        if key in (pygame.K_ASTERISK, pygame.K_KP_MULTIPLY):
            simulation.set_dt(simulation.dt * 1.5)
            return True
        if key in (pygame.K_SLASH, pygame.K_KP_DIVIDE):
            simulation.set_dt(simulation.dt / 1.5)
            return True
        # T: estelas (solo al desactivar se borran; al activar se vuelven a dibujar)
        if key == pygame.K_t:
            visualizer.show_trails = not visualizer.show_trails
            if not visualizer.show_trails:
                visualizer.clear_trails()
            return True
        # Q / D: rotar cámara 3D (E está reservada para exportar)
        if key == pygame.K_q:
            visualizer.camera_angle -= 0.28
            return True
        if key == pygame.K_d:
            visualizer.camera_angle += 0.28
            return True
        # Escape: salir
        if key == pygame.K_ESCAPE:
            running = False
            return True
        return False

    while running:
        if not paused:
            for _ in range(steps_per_frame):
                simulation.step()
                if record_interval > 0:
                    record_counter += 1
                    if record_counter >= record_interval:
                        simulation.record_snapshot()
                        record_counter = 0

        running = visualizer.draw(simulation, on_key=on_key)

    if export_path and simulation.get_trajectory():
        export_trajectories_csv(simulation.get_trajectory(), export_path)
        print(f"Exportado al salir: {export_path}")

    pygame.quit()
