# 🎬 ClipsAI - Ficha Técnica

**ClipsAI** es una aplicación de escritorio desarrollada en **Python** que permite transcribir un video, detectar automáticamente los momentos más relevantes y generar clips de forma autónoma y optimizada.

Su flujo combina **procesamiento de audio (ASR)**, análisis lingüístico con **NLTK**, herramientas de edición de video con **FFmpeg**, y módulos especializados de **detección de segmentos** para producir clips cortos listos para redes sociales o archivos de difusión.

Cuenta con soporte para reconversión automática de formatos de video, exportación de clips en alta calidad y redimensionamiento opcional en relación de aspecto **9:16** (ideal para TikTok, Reels y Shorts).

---

## 📦 Características principales

- Selección de video mediante interfaz gráfica **Tkinter**.  
- **Transcripción automática** del audio del video a texto.  
- Reconversión de archivos de video problemáticos a **MP4 estándar** (H.264/AAC).  
- **Detección automática de clips** relevantes a partir de la transcripción.  
- Exportación de cada clip en alta calidad con **FFmpeg**.  
- **Registro de información de clips** generado en `clips_info.txt`.  
- Redimensionamiento opcional en formato vertical **9:16** (con autenticación de Pyannote).  
- Manejo de errores con reconversión automática y reintentos en la transcripción.  
- Organización automática de resultados en carpeta `./clips_output`.  

---

## 🔧 Requisitos

### Python
- Python **3.9 o superior**  

### Dependencias principales

| Módulo / Herramienta   | Descripción |
|------------------------|-------------|
| **tkinter**            | Interfaz gráfica para selección de archivos. |
| **subprocess**         | Ejecución de procesos externos (FFmpeg). |
| **nltk**               | Procesamiento de lenguaje natural (tokenización). |
| **clipsai**            | Librería base con `Transcriber`, `ClipFinder` y `resize`. |
| **ffmpeg** (externo)   | Herramienta CLI para edición y exportación de video. |
| **os / shutil**        | Gestión de rutas y directorios. |

---

## ▶️ Ejecución

```bash
python clipsai.py
```

1. Selecciona un video desde la ventana emergente.  
2. El programa transcribirá el audio y detectará automáticamente clips relevantes.  
3. Los clips se exportarán en la carpeta `./clips_output` junto con un archivo `clips_info.txt`.  
4. (Opcional) Si cuentas con token de **Pyannote**, se redimensionarán automáticamente a formato 9:16.  
---

## 📃 Agradecimientos y atribuciones

Este proyecto utiliza software y librerías de terceros que requieren mención explícita de sus autores:

- **Whisper**: modelo de transcripción automática desarrollado por **OpenAI**.  
  Repositorio oficial: [https://github.com/openai/whisper](https://github.com/openai/whisper)  

- **FFmpeg**: herramienta de procesamiento de audio y video de código abierto desarrollada por **FFmpeg Team**.  
  Página oficial: [https://ffmpeg.org](https://ffmpeg.org)  

- **NLTK**: biblioteca de procesamiento de lenguaje natural en Python desarrollada por **Steven Bird y otros contribuyentes**.  
  Repositorio oficial: [https://www.nltk.org/](https://www.nltk.org/)  

- **Pyannote**: librería de análisis de audio y segmentación desarrollada por **Hervé Bredin y colaboradores**.  
  Repositorio oficial: [https://github.com/pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio)  

Se reconoce y agradece a los autores por poner su trabajo a disposición como **código libre**.


---

## 📃 Licencia

Este programa es **software libre**: puede redistribuirse y/o modificarse bajo los términos de la **Licencia Pública General de GNU, versión 3** o cualquier versión posterior.  

Consulta la licencia completa en: [GNU GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html)  

---

## © 2025 JuanitoSoftware  
📬 Contacto:  
📧 **bernaldezperedaj@gmail.com**
