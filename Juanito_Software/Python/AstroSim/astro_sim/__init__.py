"""
AstroSim — Motor de simulación astronómica interactiva.

Gravitación newtoniana N-body, visualización en tiempo real
y exportación a CSV. Preparado para extensión con ML (predicción de trayectorias).
"""

from .body import Body
from .simulation import Simulation
from .visualizer import Visualizer
from .export import export_trajectories_csv

__version__ = "0.1.0"
__all__ = ["Body", "Simulation", "Visualizer", "export_trajectories_csv"]
