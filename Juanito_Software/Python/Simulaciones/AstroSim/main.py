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


#!/usr/bin/env python3
"""
AstroSim — Punto de entrada.
Simulación N-body con gravitación newtoniana y visualización en tiempo real.

Uso:
    python main.py              # Escenario por defecto (Sol Tierra Luna simplificado)
    python main.py --scenario three_body   # Problema de los 3 cuerpos
"""

import argparse
import numpy as np

from astro_sim import Body, Simulation, Visualizer
from astro_sim.visualizer import run_loop


def scenario_solar_system_3d():
    """Sol, Tierra y Luna en 3D (órbitas en plano XY, vista desde ángulo)."""
    G = 1.0
    dt = 0.002
    sun = Body(
        "Sol",
        mass=1.0,
        position=np.array([0.0, 0.0, 0.0]),
        velocity=np.array([0.0, 0.0, 0.0]),
        color=(255, 220, 100),
        radius_display=18,
    )
    earth = Body(
        "Tierra",
        mass=3e-6,
        position=np.array([1.0, 0.0, 0.0]),
        velocity=np.array([0.0, 2 * np.pi * 0.9, 0.0]),
        color=(100, 180, 255),
        radius_display=8,
    )
    moon = Body(
        "Luna",
        mass=1e-7,
        position=np.array([1.01, 0.0, 0.0]),
        velocity=np.array([0.0, 2 * np.pi * 0.9 + 0.5, 0.0]),
        color=(200, 200, 220),
        radius_display=4,
    )
    return [sun, earth, moon], G, dt


def scenario_three_body():
    """Problema clásico de los 3 cuerpos en 3D."""
    G = 1.0
    dt = 0.0005
    bodies = [
        Body("A", 1.0, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]), (255, 100, 100), 12),
        Body("B", 1.0, np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.2, 0.0]), (100, 255, 100), 12),
        Body("C", 1.0, np.array([-0.5, 0.866, 0.0]), np.array([-1.0, -0.5, 0.0]), (100, 100, 255), 12),
    ]
    return bodies, G, dt


def scenario_simple_orbit():
    """Un planeta orbitando una estrella en 3D (ritmo lento para ver bien el paso)."""
    G = 1.0
    dt = 0.0004
    star = Body("Estrella", 1.0, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]), (255, 200, 80), 14)
    planet = Body(
        "Planeta",
        0.001,
        np.array([1.5, 0.0, 0.0]),
        np.array([0.0, 0.8, 0.0]),
        (80, 200, 255),
        6,
    )
    return [star, planet], G, dt


SCENARIOS = {
    "solar": scenario_solar_system_3d,
    "three_body": scenario_three_body,
    "orbit": scenario_simple_orbit,
}


def main():
    parser = argparse.ArgumentParser(description="AstroSim — Simulación N-body interactiva")
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS),
        default="solar",
        help="Escenario inicial (solar, three_body, orbit)",
    )
    parser.add_argument("--no-record", action="store_true", help="No registrar trayectoria para CSV")
    parser.add_argument("--record-every", type=int, default=10, help="Cada cuántos pasos guardar snapshot")
    parser.add_argument("--export", type=str, default="", help="Ruta CSV para exportar al salir")
    args = parser.parse_args()

    bodies, G, dt = SCENARIOS[args.scenario]()
    sim = Simulation(bodies, G=G, dt=dt)
    viz = Visualizer(width=1200, height=800, show_trails=True, trail_length=300)

    record_interval = 0 if args.no_record else args.record_every
    export_path = args.export or None

    # Pasos por frame: solar más rápido, órbita simple más lenta para ver el cruce
    steps_per_frame = 8 if args.scenario == "solar" else (1 if args.scenario == "orbit" else 3)

    print("Controles: [P] pausa  [E] CSV  [+/-] G  [*//] dt  [T] estelas  [Q/D] rotar cámara  [ESC] salir")
    run_loop(
        sim,
        viz,
        steps_per_frame=steps_per_frame,
        record_interval=record_interval,
        export_path=export_path,
    )


if __name__ == "__main__":
    main()
