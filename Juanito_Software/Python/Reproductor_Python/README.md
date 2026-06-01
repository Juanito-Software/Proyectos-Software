# 🎵 Reproductor Python - Reproductor MP3 con Atajos Globales

Reproductor de música MP3 de escritorio, ligero y eficiente, con soporte para **atajos de teclado globales** que funcionan en segundo plano sin necesidad de que la ventana esté en primer plano. Perfecto para controlar la música mientras juegas, programas o trabajas.

---

## 🚀 Características

- **Atajos de teclado globales**: Controla la reproducción (siguiente, anterior, pausar, subir/bajar volumen) desde cualquier aplicación, sin necesidad de cambiar de ventana.
- **HotKey Manager integrado**: Módulo `HotKeyManager.py` dedicado a la gestión de teclas multimedia del teclado (Play/Pause, Next, Prev, etc.).
- **Interfaz gráfica Tkinter**: Lista de reproducción visual con soporte para arrastrar y soltar archivos de música.
- **Soporte para listas de reproducción**: Carga y guarda listas de reproducción de tus carpetas favoritas.
- **Disponible como ejecutable**: `MP3Player.exe` compilado para sistemas sin Python.
- **Dos versiones**: `MP3Player.py` (versión completa) y una segunda versión con mejoras adicionales.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+** (Windows recomendado para los atajos globales)
- Dependencias:
  ```bash
  pip install pygame keyboard
  ```

---

## 📦 Instalación

```bash
cd Reproductor_Python/Reproductor_Python
pip install pygame keyboard
```

---

## 💻 Uso y Ejecución

### Opción A: Lanzador automático (Windows)
Haz doble clic en `MP3Player.bat` o `MP3Player2.bat`.

### Opción B: Desde la consola
```bash
cd Reproductor_Python/Reproductor_Python
python MP3Player.py
```

### Controles de la interfaz
- **Abrir carpeta**: Carga todos los MP3 de un directorio en la lista de reproducción.
- **Reproducir / Pausar**: Botón principal o atajo de teclado.
- **Siguiente / Anterior**: Navega entre canciones de la lista.
- **Volumen**: Control deslizante en la interfaz.

### Atajos de teclado globales
Los atajos funcionan globalmente (en cualquier aplicación):

| Tecla | Acción |
|---|---|
| `Media Play/Pause` | Reproducir / Pausar |
| `Media Next` | Siguiente canción |
| `Media Prev` | Canción anterior |
| `Media Stop` | Detener |

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
