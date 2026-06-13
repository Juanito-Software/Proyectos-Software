# 🎯 FPS-AI-Toolkit — Suite de IA y Visión Artificial para Juegos FPS

**Autor:** JuanitoSoftware&Games · **Versión:** 1.0 · **Licencia:** GNU GPL v3 · **Plataforma:** Windows · **Lenguaje:** Python 3

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![YOLOv8 / YOLOv11](https://img.shields.io/badge/YOLO-Ultralytics-green.svg)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer--Vision-orange.svg)](https://opencv.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
[![CUDA Boosted](https://img.shields.io/badge/CUDA-Enabled-yellow.svg)](https://developer.nvidia.com/cuda-zone)

---

## 🧾 Descripción

Suite modular de herramientas de **visión artificial e inteligencia artificial** orientadas a juegos de disparos en primera persona (FPS). Combina captura de pantalla de ultra-baja latencia, detección de objetos en tiempo real con modelos YOLO personalizados, overlay de mira flotante personalizable y optimización nativa del ratón en Windows, todo bajo una interfaz gráfica de temática **ciberpunk (Night Mode)** con arranque retro inmersivo.

---

## 🚀 Características Principales

### 👁️ 1. Detección AI en Tiempo Real

- **Detección especializada en Counter-Strike 2**: modelo YOLO entrenado sobre dataset propio para identificar:
  - 🔴 `Cabeza` — asistencia de apuntado visual
  - 🟢 `Terrorista`
  - 🔵 `Antiterrorista`
- **Detección general de personas**: modo alternativo con YOLOv8 estándar.
- **Múltiples backends**: compatible con YOLOv8, YOLOv8 ONNX y YOLO11 según el rendimiento de tu GPU.
- **Captura de ultra-baja latencia**: librería `dxcam` y `mss` a 30+ FPS con retardo imperceptible.
- **Ajuste dinámico de confianza**: umbral adaptativo (`0.3`–`0.5`) según el número de detecciones activas para minimizar falsos positivos.

### ⊕ 2. Overlay de Mira Personalizable (FloatTrans)

- **Transparente y click-through**: ventana flotante basada en la API Win32 (`win32gui`) que permite hacer clic a través de la mira directamente en el juego.
- **Personalización en tiempo real**: deslizadores de tamaño (escala) y transparencia (alpha).
- **Biblioteca incorporada**: más de 25 diseños prediseñados en la carpeta `crosshairs/`.
- **Configurable** vía `config.ini` (posición, tamaño, estilo).

### 🖱️ 3. Optimización del Ratón para Windows

- **Control de aceleración**: activa/desactiva la aceleración del cursor mediante manipulación directa del Registro (`MouseSpeed`, `MouseThreshold1/2`).
- **Sensibilidad del sistema**: ajuste lineal de 1 a 20 con precisión sub-pixel vía API nativa (`SPI_SETMOUSESPEED`).

### 🎛️ 4. Experiencia Ciberpunk y Hotkeys Globales

- **Temática Night Mode**: interfaz Tkinter en tonos oscuros y verde lima neón.
- **Arranque inmersivo**: efecto visual `matrix_effect.exe` seguido de barra de progreso animada.
- **Atajos de teclado globales** — control total sin minimizar el juego:

| Acción | Atajo |
|---|:---:|
| Activar / Apagar Detección AI | <kbd>Ctrl</kbd> + <kbd>I</kbd> |
| Mostrar / Ocultar Mira | <kbd>Ctrl</kbd> + <kbd>O</kbd> |
| Cambiar a la Siguiente Mira | <kbd>Ctrl</kbd> + <kbd>P</kbd> |

---

## 🏗️ Arquitectura y Componentes

### Módulos principales

| Módulo | Función |
|---|---|
| `MultifuncionFPS.py` | Script principal — GUI, bucles de detección, overlays y hotkeys |
| `ExtraerFramesVideo.py` | Extracción de frames de vídeo para construir datasets YOLO |
| `FloatTrans/` | Módulo de overlay transparente click-through |
| `progress_bar_utils.py` | Utilidades estéticas para la barra de progreso en consola |

### Clases principales

- `App` — Controla interfaz, configuración, eventos y overlays
- `CrosshairOverlay` — Overlay transparente para la mira
- `MotionOverlay` — Overlay para detección de movimiento visual

---

## ⚙️ Requisitos del Sistema

- **Plataforma:** Windows exclusivamente (requiere APIs Win32, DXCam y Registro de Windows)
- **Python:** 3.10 o 3.11 (64-bit)
- **GPU NVIDIA** con soporte CUDA (altamente recomendado para inferencia YOLO a 30+ FPS)

### Dependencias de Python

```
numpy<2
opencv-python
Pillow
mss
dxcam
ultralytics
keyboard
pywin32
configparser
```

Módulos estándar utilizados: `tkinter` · `threading` · `subprocess` · `os` · `sys` · `ctypes` · `winreg`

---

## 📦 Instalación

```bash
cd FPS-AI-Toolkit

# 1. Instalar PyTorch con soporte CUDA (paso crítico)
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121

# 2. Instalar el resto de dependencias
pip install -r requirements.txt

# Comando para Build
python -m PyInstaller MultifuncionFPS.py --noconfirm --onedir --windowed --clean --noupx --hidden-import=torchaudio --hidden-import=torchaudio._extension --collect-all torch --collect-all torchvision --collect-all ultralytics --collect-all cv2 --hidden-import=keyboard --hidden-import=dxcam --hidden-import=win32gui --hidden-import=win32con --hidden-import=winreg --add-binary "matrix_effect.exe;." --add-data "crosshairs;crosshairs" --add-data "FloatTrans;FloatTrans" --add-data "runs/detect/train/weights/best.pt;runs/detect/train/weights"
```

---

## 📁 Estructura del Proyecto

```plaintext
FPS-AI-Toolkit/
├── MultifuncionFPS.py        # Script principal — GUI y bucles de detección
├── ExtraerFramesVideo.py     # Extractor de frames para datasets
├── progress_bar_utils.py     # Barra de progreso estilizada
├── requirements.txt          # Dependencias de Python
├── yolov8s.pt / yolo11n.pt   # Pesos de los modelos YOLO
├── matrix_effect.exe         # Efecto visual de arranque
├── crosshairs/               # Biblioteca de miras PNG (25+ diseños)
├── FloatTrans/               # Módulo overlay flotante
│   ├── FloatTrans.exe
│   └── config.ini
├── DatasetCS2/               # Dataset propio de CS2 (opcional)
├── datasets/                 # Estructura de datasets para entrenamiento YOLO
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso y Ejecución

### Script principal
```bash
python MultifuncionFPS.py
```

**Secuencia de arranque:**
1. Se ejecuta `matrix_effect.exe` — cierra la ventana cuando desees continuar.
2. Aparece la barra de carga estilizada en consola.
3. Se abre la interfaz en modo Cyberpunk.

### Overlay de mira flotante (standalone)
```bash
cd FloatTrans
python src/main.py
```

### Extractor de frames para datasets
```bash
python ExtraerFramesVideo.py
```

---

## 🛠️ Entrenamiento del Modelo YOLO con Dataset Propio

### Paso 1 — Extracción de frames
Coloca tus clips (`.mp4`, `.avi`, `.mov`) en la carpeta `videos/` y ejecuta:
```bash
python ExtraerFramesVideo.py
```
Extrae 1 frame cada 8 fotogramas para evitar redundancia visual. Los frames se guardan en `frames/`.

### Paso 2 — Etiquetado
Etiqueta los frames con **CVAT**, **Roboflow** o **LabelImg** usando las clases:

| ID | Clase |
|---|---|
| 0 | Antiterrorista |
| 1 | Cabeza |
| 2 | Terrorista |

### Paso 3 — Entrenamiento
```bash
yolo task=detect mode=train model=yolov8s.pt data=path/to/data.yaml epochs=100 imgsz=640 device=0
```
Copia el archivo `best.pt` resultante y actualiza su ruta en `MultifuncionFPS.py` (línea ~370).

---

## ⚠️ Aviso Legal

Este software ha sido creado con **fines académicos, experimentales y de investigación en visión artificial**. El uso de herramientas de detección y overlays en partidas multijugador online puede violar los términos de servicio de los videojuegos y resultar en suspensiones permanentes. Los desarrolladores no se responsabilizan del uso que se haga de esta herramienta. **Úsala bajo tu propio riesgo y preferiblemente en entornos locales o servidores privados.**

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
