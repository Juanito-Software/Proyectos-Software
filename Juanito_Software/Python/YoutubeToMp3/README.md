# 🎵 YoutubeToMp3 - Descargador de Audio de YouTube

Herramienta de escritorio para **descargar el audio de vídeos de YouTube** en formato MP3 de alta calidad. Compatible con URLs individuales y descarga masiva en lote a través de un archivo CSV.

---

## 🚀 Características

- **Descarga de audio de alta calidad**: Extrae el stream de audio en la mayor calidad disponible y lo convierte a MP3 usando FFmpeg.
- **Soporte para descargas en lote**: Carga una lista de URLs desde un archivo `descargas.csv` para descargar múltiples pistas de una sola vez.
- **Compatible con YouTube**: Usa `pytubefix`, un fork actualizado de `pytube` que soluciona los problemas de compatibilidad con los cambios frecuentes de la API de YouTube.
- **Interfaz de usuario**: Disponible tanto en modo consola como con interfaz gráfica Tkinter.
- **Registro de descargas**: Guarda un historial de las pistas descargadas en `descargas.csv`.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- **FFmpeg** instalado en el sistema y accesible desde el `PATH`
  - Descarga FFmpeg desde: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Dependencias Python:
  ```bash
  pip install pytubefix
  ```

---

## 📦 Instalación

```bash
cd YoutubeToMp3/YoutubeToMp3

# Instalar pytubefix
pip install pytubefix

# Asegúrate de tener FFmpeg en tu PATH
ffmpeg -version
```

---

## 💻 Uso y Ejecución

```bash
cd YoutubeToMp3/YoutubeToMp3
python YoutubeToMp3.py
```

### Descarga individual
1. Introduce la URL del vídeo de YouTube cuando la aplicación lo solicite.
2. El audio se descargará y convertirá a MP3 automáticamente en el directorio actual.

### Descarga en lote (CSV)
Edita el archivo `descargas.csv` con las URLs que quieras descargar:

```csv
url
https://www.youtube.com/watch?v=XXXXXXXXXXX
https://www.youtube.com/watch?v=YYYYYYYYYYY
```

Luego ejecuta la aplicación y selecciona el modo de descarga por CSV.

---

## 📂 Estructura de salida

Los archivos MP3 descargados se guardan en la carpeta configurada en el script (por defecto, el directorio de ejecución):

```
YoutubeToMp3/
└── YoutubeToMp3/
    ├── YoutubeToMp3.py
    ├── descargas.csv
    └── [Título del vídeo].mp3   ← archivos descargados
```

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.

> **Aviso legal**: Descarga únicamente contenido del que tengas los derechos o que esté disponible bajo licencias que lo permitan. El autor no se responsabiliza del uso indebido de esta herramienta.
