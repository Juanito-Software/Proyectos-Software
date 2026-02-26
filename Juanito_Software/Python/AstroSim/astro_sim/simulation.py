"""
Simulación N-body: gravitación newtoniana.
Integrador Verlet (velocity-Verlet) para buena conservación de energía.
"""

from __future__ import annotations

import numpy as np
from typing import List

from .body import Body


class Simulation:
    """
    Simulación gravitatoria entre N cuerpos.
    F = G * m1*m2 / r^2  (vector fuerza dirigido de 1 hacia 2).
    """

    def __init__(
        self,
        bodies: List[Body],
        G: float = 6.674e-11,
        dt: float = 1.0,
        softening: float = 1e-6,
    ):
        """
        Args:
            bodies: Lista de cuerpos (se copian para no modificar los originales).
            G: Constante gravitatoria (SI: 6.674e-11; unidades arbitrarias: ej. 1.0).
            dt: Paso de tiempo (segundos o unidades de tiempo).
            softening: Suavizado para evitar r=0 (evita explosión numérica).
        """
        self.bodies = [b.copy() for b in bodies]
        self.G = G
        self.dt = dt
        self.softening_sq = softening**2
        self.time = 0.0
        self._trajectory: List[dict] = []  # Para exportar a CSV

    def _acceleration(self, i: int) -> np.ndarray:
        """Aceleración gravitatoria sobre el cuerpo i por el resto."""
        pos_i = self.bodies[i].position
        m_i = self.bodies[i].mass
        acc = np.zeros_like(pos_i)

        for j, other in enumerate(self.bodies):
            if i == j:
                continue
            r_vec = other.position - pos_i
            r_sq = max(np.dot(r_vec, r_vec) + self.softening_sq, self.softening_sq)
            r_norm = np.sqrt(r_sq)
            # F = G * m_j * m_i / r^2  ->  a_i = G * m_j / r^2 * (r_vec/r)
            acc += self.G * other.mass * r_vec / (r_sq * r_norm)

        return acc

    def step(self) -> None:
        """Un paso con velocity-Verlet (simétrico en tiempo, buena conservación)."""
        n = len(self.bodies)
        acc = [self._acceleration(i) for i in range(n)]

        for i in range(n):
            self.bodies[i].velocity += 0.5 * self.dt * acc[i]
            self.bodies[i].position += self.dt * self.bodies[i].velocity

        acc_new = [self._acceleration(i) for i in range(n)]
        for i in range(n):
            self.bodies[i].velocity += 0.5 * self.dt * acc_new[i]

        self.time += self.dt

    def step_euler(self) -> None:
        """Un paso con Euler explícito (más simple, menos estable)."""
        acc = [self._acceleration(i) for i in range(len(self.bodies))]
        for i, b in enumerate(self.bodies):
            b.velocity += self.dt * acc[i]
            b.position += self.dt * b.velocity
        self.time += self.dt

    def record_snapshot(self) -> None:
        """Guarda estado actual para exportación CSV."""
        snap = {"time": self.time}
        for b in self.bodies:
            prefix = b.name.replace(" ", "_")
            for d, letter in enumerate("xy" if b.ndim == 2 else "xyz"):
                snap[f"{prefix}_pos_{letter}"] = b.position[d]
                snap[f"{prefix}_vel_{letter}"] = b.velocity[d]
        self._trajectory.append(snap)

    def get_trajectory(self) -> List[dict]:
        """Devuelve la lista de snapshots registrados."""
        return self._trajectory.copy()

    def set_G(self, G: float) -> None:
        self.G = G

    def set_dt(self, dt: float) -> None:
        self.dt = dt
