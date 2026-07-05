# 📄 README — EfectoAudioEspacio (Simulación de Partículas)

# 🌀 EfectoAudioEspacio — Simulación Física Reactiva al Audio

**Autor:** JuanitoSoftware · **Versión:** 1.0 · **Licencia:** GPLv3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

EfectoAudioEspacio es una **simulación de partículas en 2D** que reacciona al audio del sistema.

El sonido modifica dinámicamente la física del sistema, creando un efecto visual emergente tipo “universo sonoro”.

---

## 🚀 Características

* 🌌 Simulación de partículas orbitales
* ☀️ “Sol” central dinámico
* 🪐 Gravedad variable según audio
* 🎧 Reacción en tiempo real al sonido del sistema
* ⚡ Renderizado eficiente con NumPy
* 🎛️ Parámetros ajustables

---

## 🧠 Modelo de simulación

El sistema combina:

* Gravitación newtoniana simplificada
* Modulación por amplitud de audio
* Suavizado temporal (interpolación)

Fórmula conceptual:

```
G_dynamic = G_base + audio_intensity * sensibilidad
```

---

## ⚙️ Requisitos

* Python 3.8+
* Audio activo en el sistema

### Dependencias

```bash
pip install numpy pygame soundcard
```

---

## 💻 Ejecución

```bash
python EfectoAudioEspacio.py
```

### Flujo

1. Ejecutas el programa
2. Reproduces audio en el sistema
3. La simulación reacciona automáticamente
4. Ajustas parámetros en el código
5. Cierras ventana para salir

---

## 🎛️ Parámetros importantes

```python
N = 30              # partículas
G = 40              # gravedad base
SENSIBILIDAD = 6.0  # reacción al audio
SUAVIZADO = 0.3     # suavidad de transición
FPS = 60            # renderizado
```

---

## 🎨 Casos de uso

* Arte generativo
* Visualización musical
* Performances en vivo
* Instalaciones interactivas
* Experimentos físicos simulados

---

## ⚠️ Problemas comunes

| Problema        | Causa             | Solución          |
| --------------- | ----------------- | ----------------- |
| No reacciona    | Sin audio activo  | Reproducir sonido |
| Lag             | Muchas partículas | Reducir N         |
| Movimiento raro | Gravedad baja     | Aumentar G        |

---

## 📄 Licencia

GPLv3 — software libre.

---

---

Si quieres, el siguiente paso lógico sería que te lo deje aún más “pro”:

* versión con **badges (PyPI, Python, GPL, etc.)**
* README estilo GitHub profesional con UI moderna
* o incluso convertirlo en **documentación tipo Sphinx**

Solo dime.
