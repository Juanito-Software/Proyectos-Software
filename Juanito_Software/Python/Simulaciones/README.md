# 🌌 Simulaciones - Colección de Simulaciones Físicas en Python

Colección de **simulaciones físicas e interactivas** desarrolladas en Python. Desde la gravedad newtoniana de sistemas orbitales hasta la vida emergente del autómata celular de Conway, cada simulación es visualmente atractiva e interactiva.

---

## 📂 Simulaciones Disponibles

### 🪐 AstroSim — Simulador Orbital de N-Cuerpos
Simulación física de sistemas gravitatorios con múltiples cuerpos celestes. Implementa la **Ley de Gravitación Universal de Newton** para calcular en tiempo real las trayectorias orbitales de planetas, estrellas y cometas.

**Modos disponibles:**
- **Órbita simple**: Un planeta orbitando alrededor de una estrella.
- **Sistema de 3 cuerpos**: El caótico problema de los 3 cuerpos (altamente sensible a las condiciones iniciales).
- **AstroSim completo**: Simulación configurable con múltiples parámetros.

### 🧫 Conway Life Simulation — El Juego de la Vida
Implementación clásica del **autómata celular de John Horton Conway**. Cada célula vive o muere según el número de vecinos vivos, produciendo patrones emergentes fascinantes como planeadores, osciladores y estructuras estables.

---

## 🚀 Características

- **Visualización en tiempo real con Pygame**: Renderizado fluido a 60 FPS con colores diferenciados por velocidad o energía.
- **Exportación de datos**: AstroSim exporta trayectorias en `astro_trajectories.csv` para análisis posterior.
- **Lanzadores rápidos**: Archivos `.bat` para iniciar cada simulación con doble clic.
- **Parámetros configurables**: Masas, velocidades iniciales, tamaño del grid, etc.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- Dependencias:
  ```bash
  pip install pygame numpy
  ```

---

## 📦 Instalación

```bash
cd Simulaciones/AstroSim
pip install -r requirements.txt
```

---

## 💻 Uso y Ejecución

### AstroSim — Lanzadores rápidos (Windows)
- Doble clic en `Ejecutar AstroSim.bat` → Simulación completa configurable.
- Doble clic en `Ejecutar orbita simple.bat` → Sistema de 2 cuerpos.
- Doble clic en `Ejecutar 3 cuerpos.bat` → Problema caótico de 3 cuerpos.

### AstroSim — Desde la consola
```bash
cd Simulaciones/AstroSim
python main.py
```

### Conway Life Simulation
```bash
cd Simulaciones/Conway_Life_Simulation
python ConwayLifeSimulation.py
```

O usa el ejecutable compilado: `ConwayLifeSimulation.exe`.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `AstroSim/README.md` para más detalles.
