# 🎬 AIClipCreator

**AIClipCreator** es una aplicación desarrollada en **Python** que utiliza **redes neuronales y procesamiento de audio/vídeo** para detectar automáticamente los momentos más relevantes de un vídeo y generar **clips destacados** de manera inteligente.

El sistema combina un modelo de deep learning propio (**VideoAutoClipper2**) junto con un pipeline de procesamiento de audio (MFCC + scaler) y segmentación de vídeo. Además, incluye una **interfaz web** (Flask) que permite subir vídeos, configurar parámetros y obtener clips listos para usar en plataformas como **Twitch, YouTube o TikTok**.

---

## 📦 Características principales

- Subida de vídeos desde interfaz web.
- Segmentación automática en fragmentos de análisis.
- Predicción de momentos relevantes mediante el modelo **VideoAutoClipper2**.
- Generación de clips con tiempos de inicio y fin personalizados.
- Configuración avanzada mediante `config.json`:
  - Uso de GPU o CPU.
  - Duración mínima/máxima de los clips.
  - Número máximo de clips a generar.
  - Padding antes y después del clip.
  - Umbral de relevancia.
- Gestión de modelos: carga automática o bajo demanda.
- Sistema de predicciones basado en **MFCC + scaler (joblib)**.
- Guardado automático de clips en la carpeta `./static/clips`.
- Acceso rápido a la carpeta de clips directamente desde la app.
- Persistencia y actualización de configuración en tiempo real.
- Script `.bat` para automatizar activación de entorno virtual y ejecución.

---

## 🔧 Requisitos

### Python
- **Python 3.8 o superior**

### Dependencias principales
| Módulo              | Descripción |
|----------------------|-------------|
| flask               | Framework web para la interfaz y endpoints |
| werkzeug            | Manejo seguro de archivos subidos |
| joblib              | Carga del scaler de audio (MFCC) |
| json                | Configuración y persistencia de parámetros |
| subprocess          | Apertura de carpetas según SO |
| models (propio)     | Incluye `VideoAutoClipper2`, procesamiento de vídeo y predicciones |

---

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tuusuario/AIClipCreator.git
cd AIClipCreator
```

2. Crea y activa el entorno virtual:
```bash
python -m venv AIClipCreator_env
source AIClipCreator_env/bin/activate   # Linux / macOS
.\AIClipCreator_env\Scriptsctivate    # Windows
```

3. Instala las dependencias necesarias:
```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

Con el script incluido (`start.bat` en Windows):
```bash
start.bat
```

O manualmente:
```bash
python main.py
```

Una vez iniciado, accede desde tu navegador a:  
👉 [http://localhost:5000](http://localhost:5000)

---

## 📂 Estructura principal del proyecto

```
AIClipCreator/
│── main.py                # Archivo principal (Flask + lógica de clips)
│── config.json            # Configuración editable por usuario
│── models/
│   ├── model.py           # Definición del modelo VideoAutoClipper2
│   ├── processing.py      # Funciones de segmentación y predicción
│   ├── VideoAutoClipper.pt # Modelo entrenado
│   └── mfcc_scaler.joblib # Escalador de características de audio
│── static/
│   ├── uploads/           # Carpeta de vídeos subidos
│   └── clips/             # Carpeta de clips generados
│── templates/
│   └── index.html         # Interfaz web
│── start.bat              # Script para Windows
```
---

## 📃 Agradecimientos y atribuciones

Este proyecto utiliza software y librerías de terceros que requieren mención explícita de sus autores:

- **Whisper**: modelo de transcripción automática desarrollado por **OpenAI**.  
  Repositorio oficial: [https://github.com/openai/whisper](https://github.com/openai/whisper)  

- **Auto-Editor**: aplicación de edición automática de videos desarrollada por **Adam Geitgey**.  
  Repositorio oficial: [https://github.com/WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor)  

- **FFmpeg**: herramienta de procesamiento de audio y video de código abierto desarrollada por **FFmpeg Team**.  
  Página oficial: [https://ffmpeg.org](https://ffmpeg.org)  

Se reconoce y agradece a los autores por poner su trabajo a disposición como **código libre**.

---

## 📃 Licencia

Este programa es **software libre**: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU (GPL v3)** o cualquier versión posterior.

Más información: 👉 [GNU GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

## © 2025 JuanitoSoftware

📬 Contacto:  
📧 bernaldezperedaj@gmail.com
