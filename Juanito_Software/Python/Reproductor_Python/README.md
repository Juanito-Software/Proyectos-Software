# 🎵 Reproductor de Audio - Ficha Técnica

**Versión:** 1.0  
**Autor:** JuanitoSoftware  
**Licencia:** [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)  
**Lenguaje:** Python 3  
**GUI:** Tkinter  
**Motor de audio:** VLC (via `python-vlc`)  
**Plataforma:** Windows (compatibilidad multiplataforma posible con ajustes menores)  

---

## 📦 Descripción

Este reproductor de audio es una aplicación gráfica desarrollada en Python que permite explorar carpetas, buscar archivos de audio, y reproducirlos con diversas opciones como reproducción aleatoria, en bucle o en orden. Además, incorpora soporte de atajos de teclado globales y un **modo noche**, así como integración opcional con un efecto visual inspirado en *The Matrix* (`matrix_effect.exe`).

---

## 🧩 Características

- 🎧 Reproducción de archivos `.mp3`, `.wav`, `.flac`, `.ogg`, `.aac`.
- 🌙 Modo noche para reducir fatiga visual.
- 🔁 Soporte para:
  - Reproducción en orden.
  - Reproducción aleatoria sin repeticiones.
  - Reproducción en bucle.
- 🧠 Búsqueda de archivos por nombre.
- 🔐 Licencia libre (GPLv3).
- ⌨️ Atajos globales de teclado (Ctrl + teclas de dirección, espacio, etc.).
- ⏳ Barra de progreso interactiva con tiempo transcurrido y total.
- 📁 Explorador de carpetas integrado.
- 🎬 Integración opcional con `matrix_effect.exe`.

---

## 🛠️ Requisitos

### Python (mínimo recomendado: 3.8)

### Dependencias (instalación recomendada vía `pip`):

```bash
pip install python-vlc pynput
```

### Librerías estándar utilizadas

- `tkinter`
- `threading`
- `os`, `sys`, `subprocess`, `random`

---

## ▶️ Uso

Ejecuta el programa con:

```bash
python MP3Player.py
```

o

```bash
python MP3Player_matrix.py
```


## 🎬 Efecto Matrix (Opcional)

Si el archivo `matrix_effect.exe` está presente en el mismo directorio, se ejecutará automáticamente al inicio como efecto visual siempre que ejecutes la version MP3Player_matrix.py. Puedes omitirlo con la tecla "Space" sin afectar el funcionamiento principal del reproductor.

---

## ⌨️ Atajos de Teclado

| Combinación | Acción                         |
|-------------|--------------------------------|
| `Ctrl + Espacio` | Reproducir/Pausar           |
| `Ctrl + →`       | Siguiente canción           |
| `Ctrl + ←`       | Canción anterior            |
| `Ctrl + ↑`       | Subir volumen               |
| `Ctrl + ↓`       | Bajar volumen               |
| `Ctrl + S`       | Detener reproducción        |
| `Ctrl + L`       | Activar/Desactivar bucle    |
| `Ctrl + R`       | Activar/Desactivar aleatoria|
| `Ctrl + T`       | Activar/Desactivar orden     |

---

## 📁 Estructura del Proyecto

```
📁 proyecto/
├── reproductor.py
├── matrix_effect.exe         # Opcional
└── README.md
```

---

## 🔧 Compilación a Ejecutable .exe  (opcional)

Si quieres distribuir sin requerir Python:

```bash
pip install pyinstaller

# Build (opcional)

pyinstaller --onefile --windowed --noconsole MP3Player.py

##with matrix_effect

pyinstaller --onefile --windowed --noconsole --add-binary "matrix_effect.exe;." MP3Player_matrix.py 

```

El ejecutable se generará en la carpeta `dist/`.

---

---

## 🧪 Funcionalidades técnicas destacadas

- Gestión del árbol de archivos con `ttk.Treeview`.
- Interacción con el motor VLC usando `python-vlc`.
- Modo oscuro aplicado dinámicamente a widgets Tkinter.
- Control de reproducción con eventos y polling del progreso.
- Atajos de teclado globales implementados con `pynput`.
- Manejo de errores y recuperación segura del entorno gráfico.

---

## 🧱 Limitaciones conocidas

- No soporta listas de reproducción (`.m3u`).
- La integración `matrix_effect.exe` solo funciona en Windows.
- No incluye ecualizador ni gestión de metadatos ID3.
- No guarda configuraciones persistentes entre sesiones.

---

## 🧑‍💻 Contribución

Este proyecto está abierto a mejoras y colaboraciones. Puedes:

- Crear un fork del repositorio.
- Añadir nuevas funciones (por ejemplo: reproducción desde URL, visualizaciones, ecualizador, etc.).
- Mejorar compatibilidad multiplataforma (Linux/macOS).
- Enviar pull requests o sugerencias.

---

## 🌐 Futuras mejoras (roadmap)

- [ ] Soporte para listas de reproducción.
- [ ] Persistencia de configuración entre sesiones.
- [ ] Ecualizador integrado.
- [ ] Minimizado a bandeja del sistema.
- [ ] Reproductor embebido en barra flotante.
- [ ] Control remoto vía red.

---

## 📃 Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública General de GNU, versión 3 o cualquier versión posterior.

Consulta la licencia completa para más detalles.
Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
