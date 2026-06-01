# 🌊 MusicWave - Visualizador de Música Reactivo al Sonido

Simulación física en 2D de un **sistema solar de partículas que reaccionan en tiempo real al audio** del sistema. Las partículas orbitan alrededor de un "sol" central cuya energía y atracción gravitatoria fluctúan con la intensidad y frecuencia del sonido que reproduce tu ordenador.

---

## 🚀 Características

- **Visualización reactiva al audio en tiempo real**: Captura el audio de salida del sistema (lo que suena por los altavoces) usando `soundcard`, sin necesidad de micrófono.
- **Física de partículas**: Simulación de gravitación orbital 2D con `N` partículas que se atraen entre sí y al sol central.
- **Ventana redimensionable**: La simulación se adapta automáticamente al tamaño de ventana que elijas.
- **Parámetros configurables**: Número de partículas (`N`), gravedad (`G`), velocidad máxima, sensibilidad al audio y suavizado de reacción, todo configurable en la cabecera del script.
- **Ultra fluido**: Optimizado con `NumPy` para cálculos vectorizados y `threading` para captura de audio sin bloquear el render.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- Dependencias:
  ```
  pygame
  numpy
  soundcard
  ```

---

## 📦 Instalación

```bash
cd MusicWave
pip install pygame numpy soundcard
```

> **Nota para Windows**: `soundcard` puede requerir los SDK de audio de Windows. Si tienes problemas de instalación, prueba con:
> ```bash
> pip install soundcard --no-binary soundcard
> ```

---

## 💻 Uso y Ejecución

### Opción A: Lanzador automático (Windows)
Haz doble clic en `EjecutarEfectoAudioEspacio.bat`.

### Opción B: Desde la consola
```bash
cd MusicWave
python EfectoAudioEspacio.py
```

También hay una versión alternativa disponible:
```bash
python MusicWave.py
```

### Parámetros de configuración (en el script)
Edita las siguientes variables al inicio de `EfectoAudioEspacio.py` para personalizar la experiencia:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `N` | Número de partículas | `30` |
| `G` | Constante de gravedad | `40` |
| `VEL_MAX` | Velocidad máxima de partículas | `5` |
| `SENSIBILIDAD` | Reacción al volumen del audio | `6.0` |
| `SUAVIZADO` | Suavizado de la reacción | `0.3` |
| `SAMPLERATE` | Frecuencia de muestreo de audio | `44100` |

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
