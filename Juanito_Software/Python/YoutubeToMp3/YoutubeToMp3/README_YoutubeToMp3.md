# 🎧 YoutubeToMp3 - Ficha Técnica

## Descripción

**YoutubeToMp3** es una herramienta desarrollada en Python que permite descargar y convertir audio de videos de YouTube directamente a formato MP3 con calidad ajustable. Incluye un efecto visual opcional tipo "Matrix" al ejecutarse de forma interactiva, y una versión automatizada basada en un archivo CSV para descargas masivas.

---

## Características Principales

- ✅ Descarga de audio desde YouTube en formato MP3
- 🔊 Calidad de audio personalizable (por defecto: 320 kbps)
- 🧾 Compatible con listas de descarga desde archivo CSV
- 🧠 Interfaz de línea de comandos e interacción directa con el usuario
- 💻 Incluye un efecto visual tipo "Matrix" al inicio (opcional)
- 📦 Empaquetable con PyInstaller para distribución como `.exe`

---

## Requisitos

### Dependencias Python

- `yt_dlp`  
- `ffmpeg` (debe estar instalado y en el `PATH`)

### Archivos Externos

- `matrix_effect.exe` (efecto visual opcional)
- `descargas.csv` (para modo automático)
- `YoutubeToMp3.exe` (versión compilada del script principal)

---

## Instalación

1. Instalar dependencias:
   ```bash
   pip install yt_dlp
   ```

2. Asegurarse de tener `ffmpeg` instalado y disponible en el sistema.

3. (Opcional) Compilar el script a `.exe` usando PyInstaller:
   ```bash
   pyinstaller --onefile --noconsole YoutubeToMp3.py
   ```

---

## Uso

### Modo Interactivo (manual)

```bash
python YoutubeToMp3.py
```

El usuario será guiado para introducir la URL del video de YouTube y el nombre del archivo de salida.

### Modo Automático con CSV

```bash
python batch_downloader.py
```

#### Estructura del archivo `descargas.csv`

| nombre         | url                                |
|----------------|------------------------------------|
| ejemplo_audio1 | https://youtube.com/watch?v=abc123 |
| ejemplo_audio2 | https://youtube.com/watch?v=xyz456 |

> ⚠️ Asegúrate de que el archivo CSV tenga encabezados: `nombre` y `url`.

---

## Estructura del Proyecto

```
📁 JuanitoSoftware/
├── YoutubeToMp3.py           # Script principal de descarga
├── batch_downloader.py       # Script automatizado con CSV
├── descargas.csv             # Archivo de entrada para múltiples descargas
├── matrix_effect.exe         # (Opcional) Efecto Matrix al inicio
├── YoutubeToMp3.exe          # Ejecutable generado con PyInstaller
└── README.md                 # Ficha técnica / documentación
```

---

## Errores Comunes

- `❌ No se encontró el ejecutable`: Verifica que el `.exe` esté en el mismo directorio.
- `❌ No se encontró el archivo CSV`: Asegúrate de que `descargas.csv` exista y esté bien formateado.
- `Error ejecutando matrix_effect.exe`: Puede deberse a un cierre inesperado de la ventana o falta del archivo.

---

## 📃 Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública General de GNU, versión 3 o cualquier versión posterior.

Consulta la licencia completa para más detalles.
Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware&Games

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
