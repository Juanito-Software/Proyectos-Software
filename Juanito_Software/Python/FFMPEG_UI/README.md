# 🎬 FFMPEG UI - Convertidor Multimedia Gráfico

Interfaz gráfica de escritorio para **convertir archivos de audio y vídeo** de manera sencilla, sin necesidad de usar la línea de comandos. Desarrollada con **PyQt5**, aprovecha toda la potencia de **FFmpeg** bajo el capó con solo unos clics.

---

## 🚀 Características

- **Soporte multimedia universal**: Convierte entre los formatos más populares de audio (`mp3`, `aac`, `ogg`, `flac`, `wav`) y vídeo (`mp4`, `mkv`, `avi`, `mov`, `webm`).
- **Interfaz visual moderna**: Diseñada con PyQt5 y un archivo `.ui` de Qt Designer para una experiencia de usuario limpia y fluida.
- **Integración con FFmpeg**: Llama directamente al ejecutable de FFmpeg incluido, sin necesidad de instalarlo globalmente en el sistema.
- **Barra de progreso en tiempo real**: Muestra el progreso de la conversión directamente en la interfaz.
- **Ejecución portátil**: El ejecutable `ConvertidorAudio.exe` permite usar la herramienta sin tener Python instalado.

---

## 🛠️ Requisitos del Sistema

Para ejecutar desde el código fuente:
- **Python 3.9+**
- **PyQt5**:
  ```bash
  pip install PyQt5
  ```
- El directorio `ffmpeg/` incluido en el proyecto debe contener `ffmpeg.exe`, `ffplay.exe` y `ffprobe.exe`.

Para usar la versión compilada (`ConvertidorAudio.exe`):
- Solo **Windows** — no requiere Python ni dependencias adicionales.

---

## 📦 Instalación

```bash
# Instalar dependencias de Python
pip install PyQt5
```

Asegúrate de que la carpeta `ffmpeg/` esté en la misma ubicación que `FFmpegConverter.py` o que FFmpeg esté instalado en el `PATH` del sistema.

---

## 💻 Uso y Ejecución

### Desde el código fuente
```bash
cd FFMPEG_UI
python FFmpegConverter.py
```

### Con el ejecutable compilado
Haz doble clic en `ConvertidorAudio.exe` en la carpeta del proyecto.

### Flujo de uso
1. Haz clic en **"Seleccionar archivo"** y elige el archivo de entrada.
2. Selecciona el **formato de salida** deseado en el desplegable.
3. Pulsa **"Convertir"** y espera a que la barra de progreso complete el proceso.
4. El archivo convertido se guardará en el mismo directorio que el original.

---

## ⚖️ Licencia

Este proyecto usa **FFmpeg**, licenciado bajo LGPLv2.1/GPLv3. Consulta [https://ffmpeg.org/legal.html](https://ffmpeg.org/legal.html) para más detalles.

El código propio está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt`.
