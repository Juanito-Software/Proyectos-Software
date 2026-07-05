Te lo separo correctamente en **dos README independientes**, manteniendo estructura, pero haciendo que cada programa tenga su contexto limpio y sin mezclar conceptos.

---

# 📄 README — MusicWave (Analizador de Espectro)

# 🌊 MusicWave — Analizador de Espectro de Audio en Tiempo Real

**Autor:** JuanitoSoftware · **Versión:** 1.0 · **Licencia:** GPLv3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

MusicWave es un **analizador de audio en tiempo real** que captura el sonido del sistema y lo transforma en múltiples representaciones visuales simultáneas.

Está orientado a **análisis técnico del audio**, visualización de frecuencias y comprensión de señales digitales.

No requiere micrófono: usa captura directa del sistema.

---

## 🚀 Características

* 🎧 Captura de audio en tiempo real (loopback)
* 📊 Análisis FFT (frecuencias)
* 📈 Forma de onda (tiempo)
* 🧠 Visualización por bandas (bajos / medios / agudos)
* 🧾 Vista ASCII (representación textual)
* 📡 ECG-style waveform (continuo)
* ⚡ Actualización ~60 FPS
* 🔄 Multihilo para captura sin bloquear UI

---

## 📂 Funcionamiento

El programa toma la señal de audio y la transforma mediante:

* Dominio temporal → forma de onda
* Dominio frecuencial → FFT
* Segmentación → bandas de frecuencia

---

## ⚙️ Requisitos

* Python 3.8+
* Sistema con salida de audio activa

### Dependencias

```bash
pip install numpy soundcard tkinter
```

---

## 💻 Ejecución

```bash
python MusicWave.py
```

### Flujo

1. Seleccionas dispositivo de audio
2. Inicias captura
3. Se muestran múltiples vistas simultáneas
4. Puedes detener o cerrar ventana

---

## 🔬 Conceptos

* FFT (Transformada de Fourier)
* Muestreo de audio en tiempo real
* Normalización de señal
* Buffering concurrente

---

## 🎯 Uso recomendado

* Educación en DSP
* Análisis de audio
* Debugging de señales
* Visualización técnica

---

## ⚠️ Problemas comunes

| Problema          | Solución                      |
| ----------------- | ----------------------------- |
| No detecta audio  | Revisar dispositivo de salida |
| Latencia alta     | Reducir buffer                |
| Sin visualización | Verificar FFT activa          |

---

## 📄 Licencia

GPLv3 — libre uso, modificación y redistribución.