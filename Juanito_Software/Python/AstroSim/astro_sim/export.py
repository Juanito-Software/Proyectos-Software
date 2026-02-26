"""
Exportación de trayectorias a CSV para análisis o entrenamiento de modelos.
"""

from __future__ import annotations

import csv
from typing import List, Dict, Any


def export_trajectories_csv(trajectory: List[Dict[str, Any]], path: str) -> None:
    """
    Escribe los snapshots de la simulación en un CSV.
    Columnas: time, nombre_pos_x, nombre_pos_y, nombre_vel_x, nombre_vel_y, ...
    Ideal para análisis con pandas/matplotlib o para datasets de ML.
    """
    if not trajectory:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=trajectory[0].keys())
        writer.writeheader()
        writer.writerows(trajectory)
