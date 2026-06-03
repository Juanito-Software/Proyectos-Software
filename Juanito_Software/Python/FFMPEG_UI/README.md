# 🎬 FFmpeg Audio Converter GUI — Convertidor Multimedia Gráfico

**Autor:** JuanitoSoftware · **Versión:** 1.0.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3 · **Interfaz:** PyQt5

---

## 🧾 Descripción

Aplicación de escritorio con interfaz gráfica basada en **PyQt5** para convertir archivos de audio y vídeo entre múltiples formatos, aprovechando toda la potencia de **FFmpeg** bajo el capó. Permite seleccionar carpetas de origen y destino, elegir formatos de entrada/salida y visualizar un log de progreso en tiempo real, sin necesidad de usar la línea de comandos.

---

## 🚀 Características

- 🎵 **Soporte multimedia amplio**: conversión entre los formatos más populares de audio y vídeo (ver lista completa más abajo).
- 📁 **Conversión masiva**: selección de carpeta de origen y destino para procesar múltiples archivos.
- 🖥️ **Interfaz visual moderna**: diseñada con PyQt5 y archivo `.ui` de Qt Designer para una experiencia limpia y fluida.
- ⚙️ **Detección automática de FFmpeg**: usa los binarios del sistema o los embebidos en el proyecto.
- 📊 **Log interactivo**: registro de operaciones realizadas y errores en tiempo real.
- 📦 **Ejecución portátil**: el ejecutable `ConvertidorAudio.exe` permite usar la herramienta en Windows sin tener Python instalado.

---

## 🗂️ Formatos Soportados

### Audio
`aac` · `mp3` · `flac` · `wav` · `ogg` · `wma` · `alac` · `amr` · `opus` · `aiff` · `ac3` · `ra` · `tak` · `m4a` · `gsm` · `tta` · `w64` · `ape` · `atrac` · `mid` · `midi` · y muchos más.

### Vídeo
`mp4` · `mkv` · `avi` · `mov` · `webm`

> Los formatos disponibles pueden listarse dinámicamente desde FFmpeg si se desea personalizar la selección.

---

## 🔧 Tecnologías Utilizadas

| Tecnología | Descripción |
|---|---|
| Python 3 | Lenguaje principal de desarrollo |
| PyQt5 | Framework para la interfaz gráfica |
| FFmpeg | Backend para la conversión multimedia |

---

## 🛠️ Requisitos del Sistema

- **Sistema Operativo:** Windows, Linux o macOS
- **Python:** 3.6 o superior
- **Dependencias:**
  - `PyQt5`
  - `FFmpeg` (instalado en el sistema o incluido en la ruta local del proyecto)

Para usar la versión compilada (`ConvertidorAudio.exe`):
- Solo **Windows** — no requiere Python ni dependencias adicionales.

---

## 📦 Instalación

```bash
pip install PyQt5
```

Asegúrate de que la carpeta `ffmpeg/` esté en la misma ubicación que el script principal, o que FFmpeg esté instalado en el `PATH` del sistema.

---

## 📁 Estructura del Proyecto

```plaintext
FFmpegConverter/
├── main.py                  # Código fuente principal
├── converter.ui             # Diseño de la interfaz (Qt Designer)
├── ConvertidorAudio.exe     # Ejecutable compilado para Windows
├── ffmpeg/
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
├── README.md
└── LICENSE                  # Licencia GPLv3
```

---

## 💻 Uso y Ejecución

### Desde el código fuente
```bash
cd FFmpegConverter
python main.py
```

### Con el ejecutable compilado
Haz doble clic en `ConvertidorAudio.exe` en la carpeta del proyecto.

### Flujo de uso
1. Selecciona la **carpeta de origen** con los archivos a convertir.
2. Selecciona la **carpeta de destino** donde se guardarán los resultados.
3. Elige el **formato de entrada y salida** en los desplegables.
4. Pulsa **"Convertir"** y sigue el progreso en el log interactivo.

---

## 📌 Notas Adicionales

- Este software **no garantiza** la calidad de la conversión; depende de los códecs disponibles en FFmpeg.
- Si FFmpeg no está en el PATH del sistema, incluye una versión local en el directorio `ffmpeg/`.

---

## ⚖️ Licencia

Este proyecto utiliza **FFmpeg**, licenciado bajo LGPLv2.1/GPLv3. Consulta [https://ffmpeg.org/legal.html](https://ffmpeg.org/legal.html) para más detalles.

El código propio está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de dicha licencia o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
