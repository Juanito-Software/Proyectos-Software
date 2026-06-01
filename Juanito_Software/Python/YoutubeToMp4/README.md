# 🎬 YoutubeToMp4 - Descargador de Vídeos de YouTube en Alta Calidad

Herramienta para **descargar vídeos de YouTube en la máxima resolución disponible** (hasta 4K) en formato MP4. Gestiona automáticamente el merge de streams de vídeo y audio cuando YouTube los separa en diferentes flujos, usando **FFmpeg** como motor de procesamiento.

---

## 🚀 Características

- **Descarga en máxima resolución**: Obtiene el stream de vídeo en la calidad más alta disponible (1080p, 1440p, 4K).
- **Merge automático**: Cuando YouTube separa el vídeo (sin audio) y el audio en streams distintos, los descarga por separado y los combina automáticamente con FFmpeg.
- **Soporte para CSV**: Descarga múltiples vídeos en lote leyendo una lista de URLs desde un archivo CSV.
- **Modo consola interactivo**: Solicita la URL directamente por consola y gestiona todo el proceso de forma transparente.
- **Lanzador automático**: Incluye `YoutubeToMp4.bat` para iniciar la descarga rápidamente con doble clic.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- **FFmpeg** instalado y accesible en el `PATH` del sistema
  - Descarga FFmpeg en: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  - En Windows, puedes instalarlo con winget: `winget install Gyan.FFmpeg`
- Dependencias Python:
  ```bash
  pip install pytubefix
  ```

---

## 📦 Instalación

```bash
cd YoutubeToMp4

# 1. Instalar pytubefix
pip install pytubefix

# 2. Verificar que FFmpeg está disponible
ffmpeg -version
```

---

## 💻 Uso y Ejecución

### Opción A: Lanzador automático (Windows)
Haz doble clic en `YoutubeToMp4.bat`.

### Opción B: Desde la consola
```bash
cd YoutubeToMp4
python YoutubeToMp4.py
```

La aplicación te pedirá la URL del vídeo. Introduce la URL de YouTube y el proceso se encargará de:
1. Analizar el vídeo y encontrar la mejor calidad disponible.
2. Descargar el stream de vídeo de mayor resolución.
3. Descargar el stream de audio de mayor calidad.
4. Combinar ambos con FFmpeg en un único archivo `.mp4`.
5. Eliminar los archivos temporales intermedios.

### Descarga en lote (CSV)
Crea un archivo CSV con las URLs a descargar y pásaselo al script.

---

## 📂 Estructura de carpetas

```
YoutubeToMp4/
├── YoutubeToMp4.py
├── YoutubeToMp4.bat
└── descargas/              ← vídeos descargados
    ├── Video1.mp4
    └── Video2.mp4
```

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.

> **Aviso legal**: Descarga únicamente contenido del que tengas los derechos o que esté disponible bajo licencias que lo permitan. El autor no se responsabiliza del uso indebido de esta herramienta.
