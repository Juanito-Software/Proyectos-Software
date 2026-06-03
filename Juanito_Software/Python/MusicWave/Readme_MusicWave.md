# MusicWave - Ficha Técnica

**MusicWave** es una aplicación de escritorio desarrollada en **Python** con interfaz gráfica (**Tkinter**) que permite visualizar en tiempo real la señal de audio de cualquier altavoz disponible en el sistema mediante diferentes representaciones: forma de onda, espectro FFT, onda ASCII, espectro por bandas y línea continua tipo ECG. Utiliza **SoundCard** para la captura de audio y **NumPy** para el procesamiento de las señales.

---

## 📦 Características principales

* Selección de altavoz desde la interfaz.
* Captura de audio en tiempo real usando loopback.
* Visualización de la señal de audio en múltiples formatos:

  * Forma de onda.
  * Espectro FFT.
  * Onda ASCII.
  * Espectro por bandas.
  * Línea continua tipo ECG.
* Normalización y escalado automático de la señal.
* Actualización en tiempo real con hilos y cola de datos.
* Cierre seguro de ventanas y liberación de recursos.

---

## 🔧 Requisitos

### Python

* **Python 3.8 o superior**

### Dependencias principales

| Módulo    | Descripción                                              |
| --------- | -------------------------------------------------------- |
| tkinter   | Interfaz gráfica y widgets (incluido en Python estándar) |
| soundcard | Captura de audio desde altavoces y micrófonos            |
| numpy     | Procesamiento numérico y transformadas FFT               |
| queue     | Cola para manejar datos de audio en tiempo real          |
| threading | Manejo de hilos para captura y actualización             |
| ttk       | Combobox y widgets extendidos de Tkinter                 |

---

## 🚀 Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tuusuario/MusicWave.git
cd MusicWave
```

2. Crea y activa un entorno virtual:

```bash
python -m venv MusicWave_env
source MusicWave_env/bin/activate   # Linux / macOS
.\MusicWave_env\Scripts\activate   # Windows
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

Ejecuta el programa con:

```bash
python main.py
```

* Selecciona el altavoz que deseas monitorizar.
* Presiona **Play** para iniciar la visualización.
* Se abrirá una ventana con todas las representaciones gráficas en tiempo real.

---

## 📂 Estructura principal del proyecto

```
MusicWave/
│── main.py               # Archivo principal de la aplicación
│── requirements.txt      # Dependencias del proyecto
│── README.md             # Ficha técnica y documentación
```

---

## 📃 Licencia

Este programa es **software libre**: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU (GPL v3)** o cualquier versión posterior.

Más información: [GNU GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

## 📃 Agradecimientos y atribuciones

Este proyecto utiliza software y librerías de terceros que requieren mención explícita de sus autores:

* **SoundCard**: biblioteca para captura y reproducción de audio en Python, desarrollada por **bastibe**.
  Repositorio oficial: [https://github.com/bastibe/python-soundcard](https://github.com/bastibe/python-soundcard)

* **NumPy**: biblioteca para computación científica en Python, desarrollada por la comunidad de **NumPy Developers**.
  Repositorio oficial: [https://numpy.org/](https://numpy.org/)

Se reconoce y agradece a los autores por poner su trabajo a disposición como **código libre**.

---

## © 2025 JuanitoSoftware

📬 Contacto:
📧 [bernaldezperedaj@gmail.com](mailto:bernaldezperedaj@gmail.com)