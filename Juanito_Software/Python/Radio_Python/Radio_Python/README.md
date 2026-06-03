# 📻 Radio Player — Reproductor de Radio en Streaming

**Autor:** JuanitoSoftware&Games · **Versión:** 2.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

Aplicación de escritorio desarrollada en Python con **interfaz gráfica (Tkinter)** para escuchar emisoras de radio online por streaming. Carga dinámicamente las estaciones desde un archivo CSV local, reproduce el audio mediante el motor **python-vlc** y cuenta con modo claro/noche, atajos de teclado y un efecto visual de arranque estilo Matrix.

---

## 🚀 Características

- 🎧 **Reproductor streaming** con motor **python-vlc** — compatible con streams MP3, AAC y OGG
- 📋 **Biblioteca de emisoras configurable**: lista cargada desde `Radios.csv`, sin tocar el código
- 🌓 **Modo claro / modo noche** alternables desde la interfaz
- 🖱️ **Controles múltiples**: doble clic, botones y atajos de teclado
- 🟩 **Efecto visual de arranque** `matrix_effect.exe` (opcional)
- 📊 **Indicador de estado**: muestra visualmente cuándo se está conectando o reproduciendo
- 📦 **Ejecutable disponible**: `RadioApp_2.0.exe` para usar sin Python instalado
- 🪟 **Interfaz multiplataforma** basada en `tkinter`

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.7 o superior
- **VLC Media Player** instalado en el sistema (necesario para `python-vlc`)
- **Sistema operativo:** Windows, macOS o Linux

### Dependencias de Python

```bash
pip install python-vlc
```

---

## 📦 Instalación

```bash
cd Radio_Player
pip install python-vlc
```

Asegúrate de tener **VLC Media Player** instalado antes de ejecutar.

---

## 📁 Estructura del Proyecto

```plaintext
Radio_Player/
├── radio_player.py           # Código fuente principal
├── RadioApp_2.0.exe          # Ejecutable compilado para Windows
├── Radios.csv                # Lista de emisoras (nombre, URL)
├── matrix_effect.exe         # Efecto visual de arranque (opcional)
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso y Ejecución

### Desde código fuente
```bash
python radio_player.py
```

### Versión ejecutable (sin Python)
Haz doble clic en `RadioApp_2.0.exe`.

---

## 🎛️ Controles

| Acción | Control |
|---|---|
| Reproducir emisora | Doble clic en la lista |
| Reproducir / Pausar | <kbd>Enter</kbd> o <kbd>Espacio</kbd> |
| Detener reproducción | Botón **"Detener"** |
| Alternar modo claro/noche | Botón **"🌙"** |

---

## 📡 Configurar las Emisoras

Edita `Radios.csv` para añadir, modificar o eliminar emisoras:

```csv
Nombre,URL
Radio Nacional de España,https://rtveliveaudio.akamaized.net/radionacinf/radio1/live.mp3
Rock FM,https://rockfm.cope.es/rockfm.mp3
Los 40,https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_SC
```

El formato es simple: **nombre de la emisora** y **URL del stream**.

---

## 🔨 Compilación a Ejecutable (opcional)

Para generar un `.exe` con PyInstaller:

```bash
pyinstaller --noconsole --add-data "Radios.csv;." radio_player.py
```

Incluye `matrix_effect.exe` en el mismo directorio que el `.exe` resultante si deseas el efecto de arranque.

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
