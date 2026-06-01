# 📻 Radio Python - Reproductor de Radio en Streaming

Aplicación de escritorio para **escuchar emisoras de radio online** directamente desde una interfaz gráfica en Python. Carga dinámicamente las estaciones desde un archivo CSV local y reproduce el stream de audio con un solo clic.

---

## 🚀 Características

- **Biblioteca de emisoras configurable**: Lee las estaciones de radio desde un archivo CSV (`Radios.csv`), permitiendo añadir, eliminar o modificar emisoras sin tocar el código.
- **Interfaz gráfica limpia**: Construida con **Tkinter**, con lista de emisoras, botón de reproducción y visualización del estado actual.
- **Reproducción de streams HTTP/HTTPS**: Compatible con streams de audio en formato MP3, AAC u OGG que se transmiten por internet.
- **Disponible como ejecutable**: `RadioApp_2.0.exe` permite usar la app sin tener Python instalado.
- **Gestión de conexión**: Indica visualmente cuándo se está conectando o reproduciendo una emisora.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- Dependencias:
  ```bash
  pip install pygame
  ```
  O alternativamente, si se usa `vlc` o `mpv` para la reproducción:
  ```bash
  pip install python-vlc
  ```

---

## 📦 Instalación

```bash
cd Radio_Python/Radio_Python
pip install pygame
```

---

## 💻 Uso y Ejecución

### Desde código fuente
```bash
cd Radio_Python/Radio_Python
python RadioApp.py
```

### Versión ejecutable (sin Python)
Haz doble clic en `RadioApp_2.0.exe`.

---

## 📡 Configurar las Emisoras

Edita el archivo `Radios.csv` en la carpeta `Radio_Python/` para añadir tus propias emisoras:

```csv
nombre,url
Radio Nacional de España,https://rtveliveaudio.akamaized.net/radionacinf/radio1/live.mp3
Rock FM,https://rockfm.cope.es/rockfm.mp3
Los 40,https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_SC
```

El formato es simple: **nombre de la emisora** y **URL del stream**.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
