# FPS-AI-Toolkit 🎯🤖

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![YOLOv8 / YOLOv11](https://img.shields.io/badge/YOLO-Ultralytics-green.svg)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer--Vision-orange.svg)](https://opencv.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
[![CUDA Boosted](https://img.shields.io/badge/CUDA-Enabled-yellow.svg)](https://developer.nvidia.com/cuda-zone)

**FPS-AI-Toolkit** es una herramienta avanzada de asistencia para videojuegos en primera persona (FPS) y procesamiento de visión artificial en tiempo real. Utiliza el framework **YOLO** (Ultralytics) con modelos personalizados entrenados sobre conjuntos de datos propios (dataset auto-creado) y captura de pantalla de ultra-baja latencia para sobreimprimir un overlay (HUD) dinámico de detección.

El toolkit incluye, además, utilidades para optimizar la respuesta física del ratón en Windows y sobreimprimir miras telescópicas personalizables (Crosshairs) interactivas sin interferir en los controles del juego. Todo empaquetado bajo una interfaz gráfica de temática ciberpunk (*Night Mode*) y con un espectacular arranque retro.

---

## ✨ Características Principales

### 👁️ 1. Detección AI en Tiempo Real (CS2 & Personas)
* **Detección Especializada en Counter-Strike 2**: Identificación y etiquetado instantáneo de enemigos mediante un modelo YOLO personalizado y entrenado específicamente para reconocer:
  * 🔴 **Cabezas** (`Cabeza`) para asistencia de apuntado visual.
  * 🟢 **Terroristas** (`Terrorista`).
  * 🔵 **Antiterroristas** (`Antiterrorista`).
* **Detección General de Personas**: Modo alternativo basado en YOLOv8 estándar para rastreo de personas en tiempo real.
* **Captura de Ultra-Baja Latencia (DXCam)**: Uso de la librería `dxcam` para capturar la pantalla principal a una tasa objetivo de **30+ FPS**, ofreciendo un retardo de milisegundos imperceptible.
* **Ajuste Dinámico de Umbral (Confidence)**: Modificación inteligente del umbral de confianza en tiempo real (`0.3` a `0.5`) según el número de detecciones activas en pantalla para minimizar falsos positivos y optimizar el rendimiento de inferencia.

### ⊕ 2. Superposición de Miras Personalizadas (Crosshairs)
* **Overlay Transparente Click-through**: Capa de dibujo basada en ventanas transparentes aceleradas con la API de Windows (`win32gui`), lo que permite hacer clics a través de la mira directamente en el juego sin ninguna interrupción.
* **Personalización en Tiempo Real**: Deslizadores para configurar el **Tamaño (Escala)** y la **Transparencia (Alpha)** de la mira.
* **Biblioteca Incorporada**: Rotación rápida entre más de 25 diseños de miras prediseñados ubicados en la carpeta `crosshairs/`.

### 🖱️ 3. Optimización del Ratón para Windows
* **Control de Aceleración del Sistema**: Activa o desactiva de forma directa y nativa la aceleración del cursor de Windows mediante manipulación del Registro (`MouseSpeed`, `MouseThreshold1/2`).
* **Sensibilidad del Sistema**: Ajuste lineal de la velocidad de entrada del mouse mediante API nativa (`SPI_SETMOUSESPEED`), permitiendo configurar la escala de 1 a 20 con precisión sub-pixel.

### 🎛️ 4. Experiencia Ciberpunk y Hotkeys Globales
* **Temática "Night Mode"**: Interfaz Tkinter en tonos oscuros puros y verde lima neón.
* **Arranque Inmersivo**: Ejecución inicial del módulo visual `matrix_effect.exe` seguido de una elegante barra de progreso animada en la terminal.
* **Atajos de Teclado Globales (Hotkeys)**: Control total del toolkit dentro del juego sin necesidad de minimizarlo:

| Acción | Atajo de Teclado |
|:---|:---:|
| **Activar / Apagar Detección AI (CS2)** | <kbd>Ctrl</kbd> + <kbd>I</kbd> |
| **Mostrar / Ocultar Mira en Pantalla** | <kbd>Ctrl</kbd> + <kbd>O</kbd> |
| **Cambiar a la Siguiente Mira** | <kbd>Ctrl</kbd> + <kbd>P</kbd> |

---

## 📂 Estructura del Proyecto

```text
FPS-AI-Toolkit/
├── crosshairs/               # Biblioteca de imágenes PNG para las miras
├── DatasetCS2/               # Carpeta opcional con tu conjunto de datos de CS2
├── datasets/                 # Estructura de datasets para entrenamiento YOLO
├── FloatTrans/               # Módulo helper para transparencia avanzada
├── Licencia/                 # Información de términos de uso y licencia
├── ExtraerFramesVideo.py     # Script helper para generar el dataset desde videos
├── MultifuncionFPS.py        # Script principal que contiene la GUI y los bucles de detección
├── progress_bar_utils.py     # Utilidades estéticas para barra de progreso en consola
├── requirements.txt          # Dependencias de Python necesarias
├── yolov8s.pt / yolo11n.pt   # Pesos de los modelos YOLO
└── matrix_effect.exe         # Efecto visual inmersivo al arrancar
```

---

## ⚡ Requisitos y Configuración

El proyecto está optimizado y diseñado exclusivamente para sistemas **Windows** debido al uso de llamadas de sistema del registro, APIs Win32 y aceleración gráfica DXCam.

### 1. Requisitos de Hardware
* **GPU NVIDIA con soporte CUDA** (Altamente recomendado para inferencia YOLO fluida a 30 FPS).
* Pantalla a resolución estándar compatible con DXCam.

### 2. Instalación de Dependencias

1. Asegúrate de tener instalado **Python 3.10** o **Python 3.11**.
2. Instala las dependencias principales usando `pip`:
   ```bash
   pip install -r requirements.txt
   ```
3. **Instalación de PyTorch con soporte CUDA** (Paso crítico para rendimiento óptimo con GPU):
   ```bash
   pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121
   ```

---

## 🚀 Guía de Uso

### Iniciar la Aplicación
Ejecuta el script principal desde tu terminal:
```bash
python MultifuncionFPS.py
```
* **Qué sucede al arrancar:**
  1. Se ejecutará el Easter Egg visual `matrix_effect.exe` en una ventana separada. Cierra la ventana cuando desees continuar.
  2. Verás una barra de carga dinámica estilizada en la consola completándose del 0% al 100%.
  3. Se abrirá la interfaz de usuario en modo Cyberpunk.

---

## 🛠️ Entrenamiento del Modelo YOLO con Dataset Propio

Para replicar o mejorar el modelo de detección del toolkit utilizando tus propios clips de juego:

### Paso 1: Extracción Automatizada de Frames
Coloca tus clips grabados (`.mp4`, `.avi`, `.mov`) dentro de la carpeta `videos/` y ejecuta:
```bash
python ExtraerFramesVideo.py
```
Este script leerá secuencialmente los videos y extraerá 1 frame cada 8 fotogramas (evitando la saturación y redundancia visual) guardándolos en la carpeta `frames/`.

### Paso 2: Etiquetado de Datos
Utiliza herramientas como **CVAT**, **Roboflow** o **LabelImg** para etiquetar los objetos de interés con las clases:
* `0`: Antiterrorista
* `1`: Cabeza
* `2`: Terrorista

### Paso 3: Entrenamiento
Configura tu estructura de dataset YOLO y entrena el modelo usando la CLI de `ultralytics`:
```bash
yolo task=detect mode=train model=yolov8s.pt data=path/to/data.yaml epochs=100 imgsz=640 device=0
```
Una vez completado el entrenamiento, copia el archivo `best.pt` obtenido y sustituye la ruta en `MultifuncionFPS.py` (Línea `370` aproximadamente) para empezar a usar tu red entrenada en tiempo real.

---

## ⚠️ Descargo de Responsabilidad

Este software ha sido creado con **fines académicos, experimentales y de investigación en visión artificial aplicada**.
* **El uso de herramientas de detección y overlays en partidas multijugador online puede violar los términos de servicio (ToS) de los respectivos videojuegos y resultar en suspensiones permanentes (Baneos).**
* Los desarrolladores no nos hacemos responsables por el mal uso que se le pueda dar a esta herramienta. Úsala bajo tu propio riesgo y preferiblemente en entornos locales de prueba o servidores privados.

---

## 📝 Licencia

Este proyecto está bajo los términos especificados en la carpeta [Licencia](file:///d:/Proyectos/Proyectos-Software/Juanito_Software/Python/FPS-AI-Toolkit/FPS-AI-Toolkit/Licencia). Consulta el archivo `LICENSE.txt` para obtener más detalles.
