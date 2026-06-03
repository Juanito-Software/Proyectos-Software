# 🌌 AstroSim — Motor de Simulación Astronómica Interactiva

**Autor:** JuanitoSoftware
**Versión:** 1.0
**Licencia:** GNU GPL v3 
**Lenguaje:** Python 3

---

## 🧾 Descripción

Simulación **N-body** con gravitación newtoniana 2D, visualización en tiempo real con **pygame** y exportación a CSV para análisis o futuro entrenamiento de redes neuronales. Implementa la **Ley de Gravitación Universal de Newton** para calcular en tiempo real las trayectorias orbitales de múltiples cuerpos celestes (planetas, estrellas, cometas). Incluye escenarios listos para usar y controles interactivos para modificar parámetros sobre la marcha.

---

## 🚀 Características Principales

### 👁️ Visualización y Simulación
- **Gravitación newtoniana**: \(F = G \cdot m_1 \cdot m_2 / r^2\) entre múltiples cuerpos
- **Integrador Velocity-Verlet**: algoritmo de integración numérica con excelente conservación de energía
- **Visualización 2D en tiempo real**: renderizado a 60 FPS con pygame, escala automática y estelas opcionales
- **Control de parámetros**: ajusta masa, velocidad inicial, constante gravitatoria (G) y paso de tiempo (dt) en vivo

### 📊 Exportación y Análisis
- **Exportación a CSV**: registra tiempo, posiciones y velocidades de cada cuerpo para análisis posterior o entrenamiento de IA
- **Escenarios precargados**: Sol–Tierra–Luna (sistema realista), problema de los 3 cuerpos (caótico), órbita simple (2 cuerpos)

### 🎮 Interfaz Interactiva
- **Lanzadores rápidos**: archivos `.bat` para iniciar cada escenario con doble clic (Windows)
- **Controles en pantalla**: pausa, exportación, ajuste de parámetros, estelas, todo sin interrumpir la simulación
- **Línea de comandos**: flags `--scenario` y `--export` para automatización y scripting

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.9 o superior
- **Dependencias principales:**

  ```bash
  pip install pygame numpy
  ```

  Opcional (para análisis avanzado fuera del motor):
  ```bash
  pip install matplotlib scipy
  ```

---

## 📦 Instalación

```bash
cd AstroSim
pip install -r requirements.txt
```

---

## 📁 Estructura del Proyecto

```plaintext
AstroSim/
├── astro_sim/
│   ├── body.py              # Clase Cuerpo celeste (masa, posición, velocidad)
│   ├── simulation.py        # Integrador N-body (Velocity-Verlet), parámetro G
│   ├── visualizer.py        # Ventana pygame, dibujo y controles interactivos
│   └── export.py            # Exportación a CSV
├── main.py                  # Entrada principal, escenarios y bucle de simulación
├── Ejecutar AstroSim.bat    # Lanzador rápido (simulación completa)
├── Ejecutar orbita simple.bat # Lanzador rápido (2 cuerpos)
├── Ejecutar 3 cuerpos.bat   # Lanzador rápido (problema de 3 cuerpos)
├── requirements.txt
└── README.md
```

---

## 💻 Uso y Ejecución

### Desde lanzadores rápidos (Windows)
```bash
# Doble clic en cualquier .bat
Ejecutar AstroSim.bat          # Simulación completa configurable
Ejecutar orbita simple.bat     # Sistema de 2 cuerpos
Ejecutar 3 cuerpos.bat        # Problema caótico de 3 cuerpos
```

### Desde la consola (todos los sistemas)
```bash
cd AstroSim

# Escenario por defecto (Sol, Tierra, Luna)
python main.py

# Problema de los 3 cuerpos
python main.py --scenario three_body

# Órbita simple (estrella + planeta)
python main.py --scenario orbit

# Registrar y exportar trayectoria al salir
python main.py --export trayectorias.csv
```

---

## 🎮 Controles en Pantalla

| Tecla | Acción |
|---|---|
| **P** | Pausa / Reanudar simulación |
| **E** | Exportar trayectoria a CSV (si hay datos registrados) |
| **+ / −** | Aumentar / Disminuir constante gravitatoria (G) |
| **\* / /** | Aumentar / Disminuir paso de tiempo (dt) |
| **T** | Activar / Desactivar estelas de trayectoria |
| **ESC** | Salir de la simulación |

---

## 🔧 Uso como Librería

Puedes importar AstroSim en tus propios proyectos de Python:

```python
from astro_sim import Body, Simulation, Visualizer
import numpy as np

# Crear cuerpos celestes
cuerpos = [
    Body("Sol", 1.0, np.array([0., 0.]), np.array([0., 0.])),
    Body("Planeta", 0.001, np.array([1., 0.]), np.array([0., 0.8])),
]

# Crear simulación
sim = Simulation(cuerpos, G=1.0, dt=0.01)

# Opción 1: Paso a paso sin ventana visual
for _ in range(1000):
    sim.step()
    sim.record_snapshot()

# Opción 2: Con visualización interactiva
from astro_sim.visualizer import run_loop
viz = Visualizer()
run_loop(sim, viz, record_interval=5, export_path="datos.csv")
```

---

## 📊 Exportación y Análisis de Datos

El archivo CSV exportado contiene:

```csv
tiempo,cuerpo,x,y,vx,vy
0.0,Sol,0.0,0.0,0.0,0.0
0.0,Planeta,1.0,0.0,0.0,0.8
0.01,Sol,0.001,-0.001,0.1,-0.1
0.01,Planeta,1.001,0.008,-0.1,0.8
...
```

Puedes procesar estos datos con **pandas**, **matplotlib** o entrenar redes neuronales (PyTorch, TensorFlow) para predecir trayectorias futuras.

---

## 🔬 Próximos Pasos (Ideas Futuras)

- **Simulación 3D**: migración a moderngl u OpenGL para visualización en tres dimensiones
- **Análisis avanzado**: gráficas de energía, momento angular, diagramas de fase con matplotlib
- **Red neuronal**: modelo PyTorch/TensorFlow para predecir trayectorias a partir de datos históricos exportados
- **Relatividad**: incluir efectos relativistas para órbitas cercanas a agujeros negros

---

## 📌 Notas Técnicas

- El algoritmo **Velocity-Verlet** es superior al Euler simple: mejor conservación de energía, estable a pasos de tiempo mayores
- Python es ideal para prototipado científico: numpy para vectores, pygame para visualización inmediata, ecosistema completo para IA y análisis
- Los escenarios predefinidos están calibrados para visualización interesante; puedes crear los tuyos propios editando `main.py`

---

## 📦 Simulaciones Adicionales

Este proyecto es parte de una colección **Simulaciones Físicas** que también incluye:

### 🧫 Conway Life Simulation
Implementación del **autómata celular de John Horton Conway** con patrones emergentes fascinantes (planeadores, osciladores, estructuras estables). Ejecución: `python ConwayLifeSimulation.py` o `ConwayLifeSimulation.exe`.

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
