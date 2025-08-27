# 🎬 AutoEditor  

**AutoEditor** es una aplicación de escritorio desarrollada en **Python** con interfaz gráfica (**Tkinter**) que procesa videos automáticamente para **recortar las partes con voz**, eliminando silencios y pausas largas.  

Está diseñada para **creadores de contenido** que quieran optimizar el tiempo de edición y preparar videos listos para **YouTube** y otras plataformas.  

---

## 📦 Características principales
- Selección de video mediante cuadro de diálogo (Tkinter).  
- Extracción automática del audio con **FFmpeg**.  
- Detección de voz con el modelo **Whisper (OpenAI)**.  
- Exportación de segmentos en formato **JSON**.  
- Recorte inteligente con padding configurable.  
- Generación de un nuevo video con:  
  - **Auto-Editor** (rápido y optimizado).  
  - **FFmpeg** (fallback en caso de no tener Auto-Editor).  
- Salida final lista para YouTube: **MP4 H.264 + AAC estéreo 48 kHz**.  

---

## 🔧 Requisitos

### Python
- **Python 3.8 o superior**  

### Dependencias principales
- torch  
- openai-whisper  
- soundfile  
- ffmpeg-python  
- tkinter (incluido en Python estándar)  

### Dependencias externas
- **FFmpeg** → [Descargar aquí](https://ffmpeg.org/download.html)  
- **Auto-Editor** (opcional, recomendado):  
```bash
pip install auto-editor
```

---

## 🚀 Instalación

1. Clona el repositorio:  
```bash
git clone https://github.com/tuusuario/AutoEditor.git
cd AutoEditor
```

2. Instala las dependencias:  
```bash
pip install -r requirements.txt
```

3. Asegúrate de tener **FFmpeg** instalado y accesible desde la terminal.  

---

## ▶️ Ejecución

Ejecuta el programa con:  
```bash
python main.py
```

- Selecciona el video desde la ventana emergente.  
- Se generarán:  
  - `voice_segments.json` → Segmentos de voz detectados.  
  - `output.mp4` → Video final editado.  
---

## 📃 Agradecimientos y atribuciones

Este proyecto utiliza software de terceros que requiere mención explícita de sus autores:

- **Whisper**: modelo de transcripción automática desarrollado por **OpenAI**.  
  Repositorio oficial: [https://github.com/openai/whisper](https://github.com/openai/whisper)  

- **Auto-Editor**: aplicación de edición automática de video desarrollada por **Wesley Chatham**.  
  Repositorio oficial: [https://github.com/WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor)  

Se reconoce y agradece a los autores por poner su trabajo a disposición como **código libre**.

---

## 📃 Licencia

Este programa es **software libre** bajo la licencia **GNU GPL v3**.  
Consulta los detalles completos en: [Licencia GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)  

---

## 📬 Contacto
📧 bernaldezperedaj@gmail.com  
