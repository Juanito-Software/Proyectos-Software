# 🌀 Fibonacci Spiral Simulation — Visualización Animada de la Espiral Dorada

**Autor:** JuanitoSoftware · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

Simulación interactiva que visualiza la **secuencia de Fibonacci** en coordenadas polares, generando la famosa **espiral dorada** (Golden Spiral) que aparece en la naturaleza: flores, caracoles, galaxias. Los puntos se animan con rotación continua para crear un efecto visual hipnotizante.

La simulación implementa el **ángulo dorado (Golden Angle) de 137.5°**, el mismo que optimiza el empaquetamiento de semillas en los girasoles y maximiza la exposición a la luz solar.

---

## 🚀 Características

- 🌀 **Secuencia de Fibonacci**: generación dinámica de hasta N términos de la serie
- 📐 **Coordenadas polares**: visualización en espiral usando el ángulo dorado (137.5°)
- 🎬 **Animación en tiempo real**: rotación continua para efectos visuales captivantes
- 🎨 **Dos modos de visualización**:
  - **Scatter Mode**: puntos dispersos (FibonacciSimulation.py)
  - **Line Mode**: puntos conectados por líneas (FibonacciSimulation2.py)
- 🔬 **Matemáticas naturales**: demuestra cómo el número φ (phi ≈ 1.618) aparece en la naturaleza

---

## 📊 Conceptos Matemáticos

### La Secuencia de Fibonacci
Una serie donde cada número es la suma de los dos anteriores:
```
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
```

### El Ángulo Dorado
137.5° (≈ 360° / φ²) es el ángulo de divergencia óptimo observado en plantas. Distribuye elementos de forma uniforme sin solapamientos.

### La Razón Dorada (φ)
φ ≈ 1.618... emerge naturalmente: `lím(F(n+1) / F(n))` cuando n → ∞

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.7 o superior
- **Dependencias:**
  ```bash
  pip install matplotlib numpy
  ```

---

## 📦 Instalación

```bash
pip install matplotlib numpy
```

---

## 📁 Estructura del Proyecto

```plaintext
FibonacciSimulation/
├── FibonacciSimulation.py      # Versión Scatter (puntos dispersos)
├── FibonacciSimulation2.py     # Versión Line (puntos conectados)
├── requirements.txt
└── README.md
```

---

## 💻 Uso y Ejecución

### Versión Scatter (puntos dispersos)
```bash
python FibonacciSimulation.py
```
Visualiza los números de Fibonacci como **puntos verdes dispersos** que rotan alrededor del origen.

### Versión Line (puntos conectados)
```bash
python FibonacciSimulation2.py
```
Visualiza los mismos datos como una **línea continua** conectando los puntos, enfatizando la forma espiral.

### Parámetros Configurables

Edita directamente el archivo Python para ajustar:

```python
n = 20           # Número de términos de Fibonacci a generar (default: 20)
angle = np.radians(137.5)  # Ángulo dorado en radianes (no cambiar para efecto natural)
```

Aumentar `n` generará más puntos, creando una espiral más densa y detallada.

---

## 🔍 Explicación del Código

### Generación de Fibonacci
```python
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n+1):
        fib.append(fib[-1] + fib[-2])
    return np.array(fib[1:])  # Array de n elementos
```

### Transformación a Coordenadas Polares
```python
r_values = fibonacci(n)                    # Radio (valor de Fibonacci)
theta_values = np.arange(n) * angle        # Ángulo (múltiplos de 137.5°)

x = r_values * np.cos(theta_values)
y = r_values * np.sin(theta_values)
```

### Animación de Rotación
```python
for t in range(100):
    theta_values += 0.1  # Incrementar ángulo cada frame
    x = r_values * np.cos(theta_values)
    y = r_values * np.sin(theta_values)
    # Actualizar visualización
    plt.pause(0.05)  # 20 FPS
```

---

## 🎨 Comparación de Modos

| Aspecto | Scatter | Line |
|---|---|---|
| **Visualización** | Puntos dispersos | Línea continua |
| **Énfasis** | Distribución espacial | Forma de la espiral |
| **Impacto visual** | Moderno, minimalista | Clásico, orgánico |
| **Claridad** | Mejor para análisis | Mejor para comprensión |

---

## 🔬 Aplicaciones Educativas

Esta simulación ilustra:

1. **Matemáticas**:
   - Secuencias recursivas y su convergencia
   - Geometría polar y transformaciones
   - La razón dorada φ en contextos reales

2. **Biología**:
   - Filofiaxis (disposición de hojas en plantas)
   - Empaquetamiento eficiente de semillas
   - Patrones naturales emergentes

3. **Programación**:
   - Animaciones con matplotlib
   - Transformaciones de coordenadas con NumPy
   - Bucles de tiempo real

---

## 💡 Variaciones Futuras

- **Espiral 3D**: proyección tridimensional con mpl_toolkits.mplot3d
- **Parámetros dinámicos**: interfaz interactiva para ajustar N, ángulo y velocidad
- **Exportación**: guardar frames como imagen PNG o vídeo MP4
- **Comparación**: superponer múltiples ángulos para demostrar la optimalidad del 137.5°

---

## 🧬 Curiosidad: Por qué 137.5°?

En naturaleza, el ángulo dorado (137.5°) maximiza:
- **Exposición a la luz**: cada hoja no sombrea a la anterior
- **Distribución uniforme**: sin aglomeraciones o vacíos
- **Eficiencia estructural**: mínimo espacio desperdiciado

Plantas como girasoles, piñas y margaritas siguen este patrón exacto. ¡La naturaleza es matemática!

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
