# 🎙️ StreamTools - Utilidades para Streamers y Creadores de Contenido

Colección de herramientas especializadas para **streamers y creadores de contenido en vivo**, desarrolladas en Python. Incluye desde cronómetros y contadores para OBS hasta un sistema de generación automática de clips de momentos épticos con IA.

---

## 📂 Herramientas Disponibles

### ⏱️ BackCount — Cronómetro Web para OBS
Temporizador de cuenta atrás accesible como **Browser Source en OBS**. Basado en **Flask**, expone una página web local que OBS puede mostrar directamente en escena como overlay.

### 🔢 ContadorOBS — Contador de Eventos con Hotkeys
Contador manual de eventos (kills, muertes, victorias, etc.) controlable mediante **atajos de teclado globales**. El número se actualiza en tiempo real y puede mostrarse en OBS.

### 🎬 AIClipCreator_EpicHL — Generador Automático de Clips Épicos
Sistema de **IA para detectar y cortar automáticamente los mejores momentos** de tus partidas o streams en clips listos para publicar. Usa computer vision y análisis de audio para identificar picos de acción.

---

## 🚀 Características

#### BackCount
- Cuenta atrás configurable desde la interfaz web.
- Compatible como Browser Source en OBS Studio.
- Estilos CSS personalizables para que encaje con tu stream.
- API REST para controlar el timer desde streamdecks u otras apps.

#### ContadorOBS
- Teclas rápidas globales para incrementar/decrementar el contador.
- Visualización siempre visible en la barra de sistema o ventana flotante.

#### AIClipCreator_EpicHL
- Análisis de vídeo con IA para detectar momentos de alto impacto.
- Exportación automática de clips recortados en MP4.
- Configurable por umbral de acción, duración de clip, etc.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- Dependencias por herramienta:

**BackCount:**
```bash
pip install flask
```

**ContadorOBS:**
```bash
pip install keyboard pywin32
```

**AIClipCreator_EpicHL:**
```bash
pip install -r ClipsGeneration/AIClipCreator_EpicHL/requirements.txt
```

---

## 📦 Instalación

```bash
# Instalar dependencias de BackCount
cd StreamTools/BackCount
pip install -r requirements.txt

# Instalar dependencias de AIClipCreator
cd StreamTools/ClipsGeneration/AIClipCreator_EpicHL
pip install -r requirements.txt
```

---

## 💻 Uso y Ejecución

### ⏱️ BackCount (Cronómetro para OBS)

**Opción A - Lanzador (Windows):**
Doble clic en `BackCount/start.bat`.

**Opción B - Consola:**
```bash
cd StreamTools/BackCount
python app.py
```
Luego en OBS: Añadir **Browser Source** → URL: `http://localhost:5000`

### 🔢 ContadorOBS
```bash
cd StreamTools/ContadorOBS
python ContadorOBS.py
```

### 🎬 AIClipCreator_EpicHL
```bash
cd StreamTools/ClipsGeneration/AIClipCreator_EpicHL/AI-clip-creator
python main.py
```
O usa el lanzador `run-windows.bat`.

---

## ⚖️ Licencia

Las herramientas propias de este proyecto están licenciadas bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**.
