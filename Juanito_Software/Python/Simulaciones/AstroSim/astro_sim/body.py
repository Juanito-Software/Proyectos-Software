"""
Cuerpo celeste: masa, posición y velocidad.
Vectores con numpy para cálculo eficiente.
"""

from __future__ import annotations

import numpy as np
from typing import Optional


class Body:
    """Un cuerpo puntual con masa, posición y velocidad (2D o 3D)."""

    def __init__(
        self,
        name: str,
        mass: float,
        position: np.ndarray,
        velocity: np.ndarray,
        color: Optional[tuple[int, int, int]] = None,
        radius_display: float = 5.0,
    ):
        """
        Args:
            name: Identificador del cuerpo (ej. "Sol", "Tierra").
            mass: Masa en kg (o unidades arbitrarias).
            position: Vector posición (x, y) o (x, y, z).
            velocity: Vector velocidad (vx, vy) o (vx, vy, vz).
            color: RGB para visualización (0-255). Si es None, se asigna por defecto.
            radius_display: Radio en píxeles para dibujar el cuerpo.
        """
        self.name = name
        self.mass = float(mass)
        self.position = np.asarray(position, dtype=float)
        self.velocity = np.asarray(velocity, dtype=float)
        self.color = color or (255, 255, 200)
        self.radius_display = radius_display

        if self.position.shape != self.velocity.shape:
            raise ValueError("position y velocity deben tener la misma dimensión")

    @property
    def ndim(self) -> int:
        """Dimensión del espacio (2 o 3)."""
        return self.position.shape[0]

    def copy(self) -> Body:
        """Copia independiente del cuerpo."""
        return Body(
            name=self.name,
            mass=self.mass,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            color=self.color,
            radius_display=self.radius_display,
        )

    def __repr__(self) -> str:
        return f"Body({self.name!r}, m={self.mass}, pos={self.position}, v={self.velocity})"
