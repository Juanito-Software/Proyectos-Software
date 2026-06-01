# 🎮 FPS-AI-Toolkit - Kit de Herramientas IA para Juegos FPS

Suite de herramientas de **visión artificial e inteligencia artificial** orientadas a juegos de disparos en primera persona (FPS). Combina captura de pantalla ultrarrápida, detección de objetos con modelos YOLO y una mirilla flotante personalizable.

---

## 🚀 Características

### 🎯 MultifuncionFPS (Script Principal)
- **Aimbot con YOLO**: Detección de objetivos en tiempo real usando modelos **YOLOv8** y **YOLO11** con aceleración por GPU.
- **Captura ultrarrápida**: Soporte para `mss` y `dxcam` para capturas de pantalla de bajísima latencia.
- **Mirilla flotante (FloatTrans)**: Overlay transparente de mirilla personalizable sobre cualquier juego.
- **Interfaz de configuración**: Panel gráfico completo en Tkinter para ajustar sensibilidad, modelos, teclas y más.
- **Múltiples backends**: Compatible con `YOLOv8`, `YOLOv8 ONNX` y `YOLO11` según el rendimiento de tu GPU.

### 🎬 ExtraerFramesVideo
- Extrae fotogramas de vídeos automáticamente para crear datasets de entrenamiento de YOLO.
- Configurable por intervalo de frames y directorio de salida.

### 🔭 FloatTrans (Overlay)
- Ventana transparente click-through que muestra una mirilla flotante configurable sobre el juego.
- Configurable mediante `config.ini` (posición, tamaño, estilo).

---

## 🛠️ Requisitos del Sistema

- **Python 3.10+** (64-bit)
- **GPU NVIDIA** con CUDA recomendada para inferencia en tiempo real
- Dependencias principales:
  ```
  numpy<2
  opencv-python
  Pillow
  mss
  ultralytics
  keyboard
  pywin32
  dxcam
  ```
- **Torch con CUDA** (instalar manualmente):
  ```bash
  pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121
  ```

---

## 📦 Instalación

```bash
cd FPS-AI-Toolkit/FPS-AI-Toolkit

# 1. Instalar PyTorch con CUDA primero
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121

# 2. Instalar el resto de dependencias
pip install -r requirements.txt
```

---

## 💻 Uso y Ejecución

### Script principal (Aimbot + Configuración)
```bash
python MultifuncionFPS.py
```

### Extractor de fotogramas para datasets
```bash
python ExtraerFramesVideo.py
```

### Overlay de mirilla flotante
```bash
cd FloatTrans
python src/main.py
```

---

## ⚠️ Aviso Legal

Esta herramienta es de **uso educativo y de investigación** en visión artificial. Su uso en juegos multijugador puede infringir los términos de servicio del juego. El autor no se responsabiliza del uso que se haga de este software.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
