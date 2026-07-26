# 🎵 YoutubeToMp3 — Descargador de Audio de YouTube a MP3

**Autor:** JuanitoSoftware&Games · **Versión:** 1.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

Herramienta de escritorio para **descargar audio de vídeos de YouTube** en formato MP3 de alta calidad (hasta 320 kbps). Soporta descarga individual mediante URL o descarga masiva en lote desde un archivo CSV. Incluye interfaz de línea de comandos y opcional **efecto visual Matrix** de arranque para una experiencia inmersiva.

Construida sobre **yt_dlp**, un mantenedor activo y más confiable que pytube, garantiza compatibilidad continua con los cambios de API de YouTube.

---

## 🚀 Características

-  **Descarga de audio de alta calidad**: extrae el stream de audio en la máxima calidad disponible (típicamente 320 kbps) y convierte automáticamente a MP3 usando FFmpeg
-  **Descarga masiva por CSV**: carga una lista de URLs desde `descargas.csv` para descargar múltiples pistas de una sola vez
-  **Librería confiable**: usa `yt_dlp`, un fork activamente mantenido de youtube-dl con mejor compatibilidad
-  **Interfaz flexible**: modo consola interactivo para uso manual y modo automático para procesamiento de lotes
-  **Efecto visual opcional**: efecto "Matrix" al inicio (matriz_effect.exe) para experiencia visual atractiva
-  **Registro automático**: guarda historial de descargas y metadatos en `descargas.csv`
-  **Empaquetable**: compilable a `.exe` con PyInstaller para distribución sin dependencias de Python

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.9 o superior
- **FFmpeg:** instalado en el sistema y accesible desde el `PATH`
  - Descarga desde: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  - Verifica con: `ffmpeg -version`

### Dependencias Python

```bash
pip install yt_dlp
```

Alternativa (menos recomendada, para compatibilidad legacy):
```bash
pip install pytubefix
```

---

## 📦 Instalación

```bash
cd YoutubeToMp3

# Instalar yt_dlp (recomendado)
pip install yt_dlp

# Opcional: instalar matrix_effect.exe para efecto visual
# (descárgalo o cópialo en la misma carpeta)
```

Verifica que FFmpeg esté disponible:
```bash
ffmpeg -version
```

---

## 📁 Estructura del Proyecto

```plaintext
YoutubeToMp3/
├── YoutubeToMp3.py           # Script principal — descarga individual
├── YoutubeToMp3_cookies.py   # Variante con soporte de cookies (ver más abajo)
├── batch_downloader.py       # Script automatizado — descarga masiva desde CSV
├── descargas.csv             # Archivo de entrada/salida (nombre, url)
├── matriz_effect.exe         # Efecto visual (opcional)
├── YoutubeToMp3.exe          # Ejecutable compilado (Windows)
├── requirements.txt
└── README.md
```

---

## 💻 Uso y Ejecución

### 🎯 Modo Individual (Descarga Manual)

```bash
python YoutubeToMp3.py
```

**Flujo:**
1. Introduce la URL del vídeo de YouTube cuando se solicite
2. (Opcional) Introduce el nombre del archivo MP3 de salida
3. El audio se descarga en la máxima calidad y se convierte a MP3 automáticamente
4. El archivo se guarda en el directorio actual

**Ejemplo:**
```
Introduce la URL de YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Nombre del archivo (opcional): mi_cancion.mp3
Descargando...
✓ Conversión completada: mi_cancion.mp3
```

---

### 📋 Modo Masivo (Descarga por CSV)

Para descargar múltiples pistas de una sola vez:

#### Paso 1: Preparar el archivo CSV

Edita `descargas.csv` con las URLs a descargar:

```csv
nombre,url
tema_1,https://www.youtube.com/watch?v=XXXXXXXXXXX
tema_2,https://www.youtube.com/watch?v=YYYYYYYYYYY
cancion_favorita,https://www.youtube.com/watch?v=ZZZZZZZZZZZ
```

**Columnas requeridas:**
- **nombre**: nombre del archivo MP3 (sin extensión)
- **url**: dirección completa del vídeo de YouTube

#### Paso 2: Ejecutar el descargador masivo

```bash
python batch_downloader.py
```

O con el ejecutable compilado:
```bash
Doble clic en YoutubeToMp3.exe
```

**Flujo:**
1. Lee todas las URLs del archivo CSV
2. Descarga cada una secuencialmente
3. Convierte a MP3 con FFmpeg
4. Registra el estado en la consola
5. Guarda un log de ejecución

---

## 🍪 Variante con cookies (`YoutubeToMp3_cookies.py`)

YouTube ha exigido sesión iniciada para ver vídeos en distintos momentos. Cuando
eso ocurre, el script principal falla con errores del tipo *"Sign in to confirm
you're not a bot"*.

Para esos periodos existe **`YoutubeToMp3_cookies.py`**, una variante del script
principal que añade:

- Uso de cookies del navegador para autenticar las peticiones de `yt_dlp`.
- Verificación de runtimes JS (Deno / Node.js), requeridos por `yt-dlp` EJS.
- Detección y clasificación de errores de bot, formato y cookies, con mensajes
  de ayuda específicos.

**Cuál usar:** por defecto, `YoutubeToMp3.py` — es más simple y funciona mientras
YouTube permita el acceso anónimo. Si empiezan los errores de "confirma que no
eres un bot", cambia a `YoutubeToMp3_cookies.py`.

> Nota de mantenimiento: ambos scripts comparten la mayor parte del código. Si
> corriges un fallo en uno, revisa si aplica también al otro.

---

## 🎛️ Parámetros Configurables

Edita el script Python para ajustar:

```python
# Calidad de descarga (en kbps)
QUALITY = "320"              # 320, 256, 192, 128 (según disponibilidad)

# Formato de salida
OUTPUT_FORMAT = "mp3"        # Formato de FFmpeg

# Directorio de salida
OUTPUT_DIR = "./"            # Carpeta donde guardar los MP3

# Mostrar efecto Matrix
SHOW_MATRIX_EFFECT = True    # True o False
MATRIX_EFFECT_PATH = "matrix_effect.exe"

# Timeout de descarga (segundos)
DOWNLOAD_TIMEOUT = 300       # Aumentar si descargas muy lentas

# Número de reintentos
MAX_RETRIES = 3              # Reintentos si falla la descarga
```

---

## 📊 Formato del Archivo CSV

**Estructura mínima:**
```csv
nombre,url
```

**Ejemplo completo:**
```csv
nombre,url,duracion_esperada,notas
cancion_1,https://youtube.com/watch?v=abc123,3:45,Pop
podcast_2,https://youtube.com/watch?v=def456,25:30,Educativo
musica_3,https://youtube.com/watch?v=ghi789,4:12,Rock
```

Las columnas adicionales (duración, notas) son informativas y se ignoran.

---

## ✅ Validación y Errores Comunes

| Error | Causa | Solución |
|---|---|---|
| `FFmpeg no encontrado` | FFmpeg no está en el PATH | Instala FFmpeg y añádelo al PATH del sistema |
| `URL inválida` | URL de YouTube incorrecta | Verifica que sea una URL completa válida (youtube.com/watch?v=...) |
| `No se puede descargar` | Vídeo privado o eliminado | Verifica que el vídeo sea público y accesible |
| `Fallo de conversión a MP3` | FFmpeg no puede procesar el audio | Prueba con otro vídeo o actualiza FFmpeg |
| `Archivo CSV no encontrado` | descargas.csv no existe | Crea el archivo con al menos una URL válida |
| `Permisos insuficientes` | No puedes escribir en el directorio | Ejecuta como administrador o cambia OUTPUT_DIR |

---

## 🎬 Efecto Matrix (Opcional)

Si incluyes `matrix_effect.exe` en el directorio, se mostrará un efecto visual estilo Matrix al inicio:

```python
SHOW_MATRIX_EFFECT = True
```

Presiona <kbd>Espace</kbd> en la ventana Matrix para continuar con la descarga.

---

## 🔧 Compilación a Ejecutable .exe  (opcional)

Si quieres distribuir sin requerir Python:

```bash
pip install pyinstaller

# Build (opcional)
pyinstaller --onefile --console --add-binary "matrix_effect.exe;." YoutubeToMp3.py 
```

El ejecutable se generará en la carpeta `dist/`.

---

## 📌 Notas Técnicas

- **yt_dlp vs pytube**: yt_dlp es más moderno y mantenido activamente. pytube/pytubefix funciona pero puede quedarse obsoleto rápidamente.
- **Calidad de audio**: YouTube generalmente proporciona audio de 128-256 kbps. Si especificas 320 kbps, FFmpeg aumentará la tasa de bits mediante interpolación.
- **Tiempo de descarga**: depende de la duración del vídeo, tu conexión a internet y la carga de YouTube.
- **Límites de velocidad**: YouTube puede ralentizar descargas muy rápidas. Usa delays entre descargas masivas si es necesario.

---

## ⚠️ Aviso Legal

**Este software se proporciona únicamente con fines educativos y personales.**

- ✅ Se permite descargar contenido que tengas derecho a usar (películas propias, música con licencia, contenido público disponible bajo Creative Commons, etc.)
- 🚫 **NO está permitido**: descargar contenido protegido por derechos de autor sin permiso
- 🚫 **NO está permitido**: violar los términos de servicio de YouTube
- 🚫 **NO está permitido**: distribuir o revender contenido descargado sin autorización

**El autor no se responsabiliza del uso indebido de esta herramienta.** Descarga únicamente contenido del que tengas los derechos o que esté disponible bajo licencias permisivas.

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
