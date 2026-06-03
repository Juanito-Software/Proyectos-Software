# 🌍 Sistema Solar Emergente 2D — Simulación Gravitatoria Newtoniana

**Autor:** JuanitoSoftware · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

Colección de tres simulaciones de **sistemas solares emergentes** basadas en **gravitación newtoniana 2D**. Cada versión representa una evolución progresiva en complejidad y fidelidad física, desde un sistema simple hasta una simulación con rastros visuales, órbitas elípticas y parámetros altamente configurables.

Observa cómo múltiples partículas con masas variables orbitan un sol central masivo, interaccionan gravitatoriamente entre sí y generan dinámicas complejas y emergentes a partir de reglas físicas simples.

---

## 🚀 Características Generales

- ⭐ **Sol central masivo**: punto de atracción gravitatoria dominante
- 🪐 **N partículas en órbita**: con masas variables y física newtoniana
- 🎬 **Renderizado en tiempo real**: 60 FPS con pygame
- 📊 **Gravitación realista**: \(F = G \cdot m_1 \cdot m_2 / r^2\)
- 🛡️ **Suavizado (Softening)**: evita singularidades cuando las partículas están muy cerca
- 🔄 **Interacción N-body**: cada partícula interactúa con todas las demás
- 🎨 **Visualización clara**: colores diferenciados por tipo (sol dorado, partículas blancas)

---

## 📂 Las Tres Versiones

### 📍 v1: Simulacion2D.py — Sistema Básico

**Características:**
- Partículas colocadas **aleatoriamente** en la pantalla
- Velocidades iniciales **random** muy pequeñas
- Gravedad del sol sin suavizado
- Interacción entre partículas mínima (muy débil)
- Rebotes simples en bordes de pantalla

**Comportamiento esperado:**
- Caos visual inicial, partículas "cayendo" hacia el sol
- Algunas permanecen en órbita inestable; otras caen rápidamente
- Dinámica muy caótica, poco realista

**Cuándo usarla:**
- Propósito educativo básico
- Demostración de cómo funcionan los rebotes y colisiones
- Punto de partida para aprender la estructura

---

### 🌀 v2: Simulacion2D_v2.py — Órbitas Circulares Iniciales

**Mejoras respecto a v1:**
- Partículas nacen en **órbitas circulares estables** (radio y ángulo aleatorios)
- Velocidades orbitales calculadas correctamente: \(v_{circ} = \sqrt{G \cdot M_{sol} / r}\)
- **Softening** en interacciones partícula-partícula para evitar fuerzas infinitas
- Sistema más realista y predecible

**Comportamiento esperado:**
- Órbitas circulares estables alrededor del sol
- Algunas perturbaciones por interacción entre partículas
- Dinámica ordenada y visualmente satisfactoria

**Cuándo usarla:**
- Demostración de órbitas kepleríanas
- Comparación con simulaciones realistas
- Uso educativo intermedio

---

### ✨ v3: Simulacion2D_v3.py — Sistema Avanzado con Rastros y Órbitas Elípticas

**Mejoras respecto a v2:**
- **Rastros visuales (trails)**: cada partícula deja una estela que se desvanece gradualmente
- **Órbitas elípticas**: perturbaciones controladas en velocidad tangencial y radial
- **Parámetros extremadamente configurables** (ver sección más abajo)
- **Suavizado separado** para sol (`SOL_SOFTENING`) y partículas (`PART_SOFTENING`)
- Integración numérica mejorada (semi-implícita)
- **Respawn dinámico**: partículas destruidas por el sol reaparecen en anillo seguro
- Visualización mejorada con surface de rastros
- Mayor estabilidad y menor tendencia a explosiones numéricas

**Comportamiento esperado:**
- Órbitas elípticas hermosas y visuales
- Rastros que crean un patrón fractal emergente
- Sistema estable incluso con muchas interacciones

**Cuándo usarla:**
- Mejor para observación y captura de imágenes/vídeos
- Investigación de parámetros y dinámicas complejas
- Producción de arte generativo

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.7 o superior
- **Dependencias:**
  ```bash
  pip install pygame
  ```
  Módulos estándar: `random`, `math`, `collections`

---

## 📦 Instalación

```bash
pip install pygame
```

---

## 💻 Uso y Ejecución

### Versión 1 (Básica)
```bash
python Simulacion2D.py
```

### Versión 2 (Órbitas Circulares)
```bash
python Simulacion2D_v2.py
```

### Versión 3 (Avanzada con Rastros)
```bash
python Simulacion2D_v3.py
```

**Cerrar:** presiona el botón de cerrar ventana o <kbd>Alt</kbd>+<kbd>F4</kbd>

---

## 🎛️ Parámetros Configurables (v3)

Edita `Simulacion2D_v3.py` para ajustar:

```python
# Dimensiones y física
W, H = 800, 600          # Ancho x Alto de ventana
N = 50                   # Número de partículas
G = 0.5                  # Constante gravitatoria (↑ más atracción)
VEL_MAX = 8              # Límite de velocidad (evita explosiones)
DT = 1.0                 # Paso de integración (↓ más preciso pero lento)

# Fuerzas y softening
SOL_SOFTENING = 20       # Suavizado para evitar singularidades en sol
PART_SOFTENING = 5       # Suavizado en interacción entre partículas
INTER_PARTICLE_FORCE = 0.01  # Fuerza mutua entre partículas (↓ menos interacción)

# Spawn inicial
MIN_R = 120              # Radio mínimo de aparición de partículas
MAX_R = 300              # Radio máximo de aparición
SOL_RADIUS = 50          # Tamaño del sol (colisión a este radio)

# Visualización
TRAIL_LENGTH = 120       # Longitud máxima del rastro
TRAIL_FADE_ALPHA = 18    # Cuánto se desvanecen los rastros (↑ más rápido)
FPS = 60                 # Fotogramas por segundo

# Órbitas elípticas (v3)
tangential_scale = random.uniform(0.95, 1.08)  # <1 órbita más excéntrica
radial_frac = random.uniform(-0.06, 0.06)      # Componente radial
```

**Ejemplos de ajuste:**
- **Más caos**: `↑ INTER_PARTICLE_FORCE`, `↓ G`
- **Órbitas más estables**: `↑ SOL_SOFTENING`, `↓ INTER_PARTICLE_FORCE`
- **Rastros más cortos**: `↓ TRAIL_LENGTH`
- **Sistema más rápido**: `↓ DT`, `↑ FPS`

---

## 🔬 Conceptos Físicos

### Gravitación Newtoniana
```
F = G · m₁ · m₂ / r²
a = F / m
v += a · dt
x += v · dt
```

### Softening (Suavizado)
Evita singularidades (fuerzas infinitas) cuando dos objetos están muy cerca:
```
F = G · m₁ · m₂ / (r² + softening²)
```

### Órbitas Circulares
Para mantener una órbita circular:
```
v_circular = √(G·M / r)
```

### Órbitas Elípticas
Se logran con pequeñas perturbaciones en la velocidad:
- **Componente tangencial** ≠ 1.0 → excentricidad
- **Componente radial** ≠ 0 → rotación de ápside

---

## 📊 Comparación de Versiones

| Aspecto | v1 | v2 | v3 |
|---|:---:|:---:|:---:|
| Órbitas iniciales | Random | Circulares | Elípticas |
| Softening | Mínimo | Sí | Sí (mejorado) |
| Rastros visuales | No | No | Sí |
| Parámetros configurables | Pocos | Algunos | Muchos |
| Estabilidad | Baja | Media | Alta |
| Propósito | Educativo | Realista | Producción |

---

## 🎨 Sugerencias Creativas

1. **Captura de imágenes**: configura v3 con `TRAIL_LENGTH = 300` y deja correr 5 minutos
2. **Registro de vídeo**: usa software como OBS para grabar la salida
3. **Variaciones paramátricas**: experimenta con `INTER_PARTICLE_FORCE` de 0.001 a 0.1
4. **Arte generativo**: combina múltiples capturas con diferentes semillas aleatorias
5. **Análisis**: exporta posiciones y velocidades para análisis estadístico

---

## 🔮 Próximos Pasos

- **Exportación de datos**: guardar posiciones/velocidades a CSV para análisis
- **Integrador más preciso**: RK4 (Runge-Kutta de 4º orden) en lugar de semi-implícito
- **Colisiones elásticas**: cuando dos partículas se tocan, rebotan realísticamente
- **Interfaz gráfica**: ajusta parámetros en tiempo real con sliders
- **Simulación 3D**: extensión a tres dimensiones con OpenGL o moderngl
- **Análisis orbital**: calcula excentricidad, período, energía total

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
