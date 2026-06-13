# 🌊 MusicWave — Visualizador Reactivo de Audio en Tiempo Real

**Autor:** JuanitoSoftware · **Versión:** 1.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

Suite de visualizadores de audio en tiempo real que capturan el sonido que reproduce tu ordenador y lo transforman en **representaciones visuales reactivas**. Dos enfoques complementarios:

1. **Analizador de Espectro Multiformato** (`main.py`): análisis profesional con múltiples vistas simultáneas
2. **Simulación de Partículas Reactiva** (`EfectoAudioEspacio.py`): simulación física emergente basada en física orbital

Ambas usan **captura de audio del sistema** mediante `soundcard`, sin necesidad de micrófono.

---

## 🚀 Características Generales

- 🎵 **Captura de audio en tiempo real**: acceso directo al stream de audio de salida del sistema (loopback)
- 📊 **Procesamiento con NumPy**: cálculos vectorizados eficientes para FFT y transformadas
- 🔄 **Actualización fluida**: threading para captura de audio sin bloquear renderizado
- 🎨 **Visualización adaptativa**: interfaz responsiva que se adapta a diferentes tamaños de ventana
- 📡 **Sin micrófono requerido**: captura directamente lo que suena por los altavoces
- ⚙️ **Parámetros configurables**: ajusta sensibilidad, suavizado, número de partículas, etc.

---

## 📂 Las Dos Versiones

### 📊 v1: Analizador de Espectro Multiformato

**Archivo:** `main.py`

Visualizador **profesional de audio** con múltiples representaciones simultáneas de la misma señal de audio:

#### Vistas disponibles:
- **Forma de onda**: representación clásica de amplitud vs tiempo
- **Espectro FFT**: análisis de frecuencias mediante Transformada Rápida de Fourier
- **Onda ASCII**: visualización en texto puro (retro/nostalgia)
- **Espectro por bandas**: división en bandas de frecuencia (bajos, medios, agudos)
- **Línea ECG**: representación continua tipo electrocardiograma

#### Características:
- Selección dinámica de altavoz desde la GUI
- Normalización automática de señal
- Actualización en tiempo real (60 FPS)
- Botón Play/Stop
- Cierre seguro de recursos

#### Mejor para:
- Análisis de audio profesional
- Educación (FFT, procesamiento digital)
- Debugging y monitoreo de audio
- Visualización clara y múltiple perspectiva

---

### 🌀 v2: Simulación de Partículas Reactiva al Audio

**Archivo:** `EfectoAudioEspacio.py` o `MusicWave.py`

**Simulación física emergente** donde un sistema solar de partículas **reacciona dinámicamente al audio** que reproduces:

#### Conceptos:
- **Sol central**: cuya gravedad y energía fluctúan con la intensidad del audio
- **N partículas**: orbitan alrededor del sol, interactuando entre sí gravitatoriamente
- **Reactividad**: las frecuencias altas aceleran las órbitas, los bajos cambian la gravedad
- **Suavizado de transición**: evita cambios bruscos, crea flujo visual

#### Características:
- Física orbital 2D completa (gravitación newtoniana)
- Sensibilidad al audio personalizable
- Número de partículas configurable (5-100+)
- Ventana redimensionable (simulación se adapta)
- Parámetros ajustables en cabecera del script
- Ultra eficiente con operaciones vectorizadas NumPy

#### Mejor para:
- Arte generativo / visualización creativa
- Experiencia inmersiva / live performances
- Demostración de física emergente
- Entretenimiento visual

---

## 🔄 Comparación Rápida

| Aspecto | v1 (Espectro) | v2 (Partículas) |
|---|---|---|
| **Propósito** | Análisis técnico | Arte generativo |
| **Visualización** | Multiformato/exacta | Emergente/intuitiva |
| **Uso principal** | Profesional/educativo | Entretenimiento/live |
| **Formato datos** | Forma de onda + FFT | Trayectorias de partículas |
| **Parámetros** | Altavoz, normalización | N, G, sensibilidad, suavizado |
| **Curva de aprendizaje** | Baja | Media |

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.8 o superior
- **Audio hardware:** altavoces o auriculares
- **Dependencias comunes:**

  ```bash
  pip install numpy soundcard pygame tkinter
  ```

### Detalles por versión:

**v1 (Espectro):** `tkinter`, `soundcard`, `numpy`, `queue`, `threading`

**v2 (Partículas):** `pygame`, `numpy`, `soundcard`, `threading`

---

## 📦 Instalación

```bash
cd MusicWave

# Instalar todas las dependencias
pip install numpy soundcard pygame

# En Linux, puede requerir librerías del sistema:
# sudo apt install python3-tk python3-dev
```

> **Nota Windows**: `soundcard` puede requerir los SDK de audio. Si tienes problemas:
> ```bash
> pip install soundcard --no-binary soundcard
> ```

---

## 💻 Uso y Ejecución

### 📊 Versión 1: Analizador de Espectro

```bash
python main.py
```

**Flujo:**
1. Se abre una ventana con lista de altavoces disponibles
2. Selecciona el altavoz que quieres monitorizar
3. Presiona **Play**
4. Se abre una ventana con 5 visualizaciones simultáneas del audio
5. Las vistas se actualizan en tiempo real
6. Presiona **Stop** o cierra la ventana para terminar

---

### 🌀 Versión 2: Simulación de Partículas

```bash
python EfectoAudioEspacio.py
```

O en Windows con lanzador automático:
```bash
Doble clic en EjecutarEfectoAudioEspacio.bat
```

**Flujo:**
1. Se abre una ventana con la simulación
2. Reproduce música/audio en tu ordenador
3. Las partículas reaccionan automáticamente al audio
4. Ajusta los parámetros en tiempo real (edita el script si quieres cambios permanentes)
5. Cierra la ventana para terminar

---

## 🎛️ Parámetros Configurables (v2)

Edita `EfectoAudioEspacio.py` al inicio para personalizar:

```python
# Física de partículas
N = 30                   # Número de partículas (5-100)
G = 40                   # Gravedad (mayor = órbitas más estables)
VEL_MAX = 5              # Velocidad máxima (mayor = movimiento más rápido)

# Reactividad al audio
SENSIBILIDAD = 6.0       # Cuánto cambia la gravedad con el audio
SUAVIZADO = 0.3          # Smoothing de transiciones (0.0-1.0)
SAMPLERATE = 44100       # Frecuencia de muestreo en Hz

# Visualización
ANCHO, ALTO = 1280, 720  # Resolución de ventana
FPS = 60                 # Fotogramas por segundo
COLOR_FONDO = (10, 10, 20)     # Color RGB de fondo
COLOR_PARTICULAS = (100, 200, 255)  # Color RGB de partículas
COLOR_SOL = (255, 200, 0)      # Color RGB del sol
```

**Ejemplos de ajuste:**
- **Más caos**: `↑ SENSIBILIDAD`, `↓ G`
- **Órbitas estables**: `↓ SENSIBILIDAD`, `↑ G`
- **Más visual**: `↑ N` (más partículas, pero más lento)
- **Más reactivo**: `↓ SUAVIZADO` (cambios instantáneos)

---

## 🔬 Conceptos Técnicos

### Análisis FFT (v1)

La **Transformada Rápida de Fourier** descompone el audio en sus componentes de frecuencia:
```
Audio(t) [tiempo] → FFT → Magnitud(f) [frecuencia]
```

Esto permite visualizar **qué frecuencias están presentes** (bajos, medios, agudos).

### Gravitación Orbital (v2)

Simulación de la **Ley de Gravitación Universal de Newton**:
```
F = G · m₁ · m₂ / r²
```

Las partículas orbitan el sol central; la gravedad fluctúa con el audio:
```
G_dinámica = G_base + SENSIBILIDAD · audio_actual
```

Esto crea un efecto **emergente** donde la música literalmente cambia la gravedad.

---

## 🎨 Casos de Uso

| Caso | Versión | Razón |
|---|---|---|
| DJ monitoring en vivo | v1 | Análisis técnico preciso |
| Visualización para livestream | v2 | Impactante y reactiva |
| Enseñanza de procesamiento digital | v1 | Múltiples perspectivas |
| Instalación de arte sonoro | v2 | Emergencia y belleza |
| Debugging de flujo de audio | v1 | Claridad técnica |
| Fondo reactivo para presentaciones | v2 | Llamativo y fluido |

---

## 🔧 Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| `No se encuentra soundcard` | Librería no instalada | `pip install soundcard` |
| `Error: No audio devices found` | No hay altavoz disponible | Conecta altavoces o auriculares |
| `Audio muy bajo/alto` | Normalización incorrecta | Ajusta volumen del sistema |
| `FPS bajo / lag` | CPU saturada | Reduce `N` (v2) o cierra aplicaciones |
| `Partículas se salen de pantalla` | Gravedad muy baja | Aumenta `G` |
| `Reacción al audio no visible` | Sensibilidad muy baja | Aumenta `SENSIBILIDAD` (v2) |

---

## 🔮 Próximos Pasos

- 3D rendering para v2 (con moderngl u OpenGL)
- Grabación de video de la visualización
- Exportación de datos de audio/posiciones a CSV
- Soporte para múltiples fuentes de audio
- Interfaz GUI para cambiar parámetros en tiempo real (sin editar código)
- Presets guardables

---

## 📚 Créditos y Atribuciones

- **SoundCard** (bastibe): captura de audio en Python — [github.com/bastibe/python-soundcard](https://github.com/bastibe/python-soundcard)
- **NumPy**: computación científica y FFT — [numpy.org](https://numpy.org/)
- **PyGame**: renderizado 2D — [pygame.org](https://www.pygame.org/)

Se reconoce y agradece a los autores por mantener estas librerías como software libre.

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
