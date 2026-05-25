# AstroSim — Motor de simulación astronómica interactiva

Simulación **N-body** con gravitación newtoniana en 2D, visualización en tiempo real con **pygame** y exportación a CSV para análisis o futuro entrenamiento de redes neuronales.

## Características

- **Gravitación newtoniana** entre múltiples cuerpos (\(F = G \, m_1 m_2 / r^2\))
- **Integrador velocity-Verlet** para buena conservación de energía
- **Visualización 2D** en tiempo real (escala automática, estelas opcionales)
- **Control de parámetros**: masa, velocidad inicial, constante G, paso de tiempo (dt)
- **Exportación a CSV** (tiempo, posiciones y velocidades de cada cuerpo)
- Escenarios listos: sistema Sol–Tierra–Luna, problema de los 3 cuerpos, órbita simple

## Requisitos

- Python 3.10+
- numpy, pygame, matplotlib (opcional para análisis fuera del motor)

## Instalación

```bash
cd AstroSim
pip install -r requirements.txt
```

## Uso

```bash
# Escenario por defecto (Sol, Tierra, Luna)
python main.py

# Problema de los 3 cuerpos
python main.py --scenario three_body

# Órbita simple (estrella + planeta)
python main.py --scenario orbit

# Registrar trayectoria y exportar al salir
python main.py --export trayectorias.csv
```

### Controles en pantalla

| Tecla | Acción |
|-------|--------|
| **P** | Pausa / reanudar |
| **E** | Exportar trayectoria a CSV (si hay datos registrados) |
| **+ / -** | Aumentar / disminuir constante G |
| **\* / /** | Aumentar / disminuir paso de tiempo (dt) |
| **T** | Activar / desactivar estelas |
| **ESC** | Salir |

## Estructura del proyecto

```
AstroSim/
├── astro_sim/
│   ├── body.py       # Cuerpo celeste (masa, posición, velocidad)
│   ├── simulation.py # Integrador N-body (Verlet), parámetro G
│   ├── visualizer.py # Ventana pygame, dibujo y controles
│   └── export.py     # Exportación a CSV
├── main.py           # Entrada, escenarios y bucle principal
├── requirements.txt
└── README.md
```

## Uso como librería

```python
from astro_sim import Body, Simulation, Visualizer
import numpy as np

cuerpos = [
    Body("Sol", 1.0, np.array([0., 0.]), np.array([0., 0.])),
    Body("Planeta", 0.001, np.array([1., 0.]), np.array([0., 0.8])),
]
sim = Simulation(cuerpos, G=1.0, dt=0.01)

# Paso a paso (sin ventana)
for _ in range(1000):
    sim.step()
    sim.record_snapshot()

# O con visualización
from astro_sim.visualizer import run_loop
viz = Visualizer()
run_loop(sim, viz, record_interval=5, export_path="datos.csv")
```

## Próximos pasos (ideas)

- **3D** con moderngl o OpenGL
- **Análisis** con matplotlib (energía, momento angular, gráficas posición/tiempo)
- **Red neuronal** (PyTorch/TensorFlow) para predecir trayectorias a partir de datos exportados

---

*Python es ideal para prototipado científico: numpy para vectores, pygame para ver resultados al instante, y todo el ecosistema para IA y análisis.*
