# 📤 Enviar Archivos Python - Transferencia de Archivos en Red LAN

Herramienta de escritorio para **compartir y transferir archivos rápidamente** entre equipos en la misma red local (LAN) mediante sockets TCP. Con una interfaz gráfica sencilla basada en **Tkinter**, no necesitas ninguna configuración compleja ni software de terceros.

---

## 🚀 Características

- **Transferencia directa por LAN**: Envía cualquier tipo de archivo a otro equipo en la misma red sin pasar por internet.
- **Interfaz gráfica intuitiva**: Selección de archivos mediante explorador de archivos y barra de progreso visual.
- **Sin dependencias externas**: Basado únicamente en librerías estándar de Python (`socket`, `threading`, `tkinter`).
- **Verificación de integridad**: Hash de verificación para asegurar que los archivos no se corrompan durante la transferencia.
- **Lanzamiento fácil**: Incluye `ejecutar.bat` para iniciar la aplicación con doble clic.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- No requiere instalación de paquetes externos — todo está incluido en la librería estándar de Python.

---

## 📦 Instalación

1. Asegúrate de tener **Python 3.9 o superior** instalado y accesible desde el sistema.
2. Clona o descarga este repositorio en tu equipo.
3. No es necesario instalar dependencias adicionales.

---

## 💻 Uso y Ejecución

### Opción A: Lanzador automático (recomendado en Windows)
Haz doble clic en el archivo `ejecutar.bat` dentro de la carpeta `Enviar_Archivos_Python`.

### Opción B: Desde la consola
```bash
cd Enviar_Archivos_Python
python EnviarArchivos.py
```

### Modo Servidor (Receptor)
1. Abre la aplicación en el equipo que **recibirá** el archivo.
2. Anota la **IP local** de ese equipo (visible en la interfaz).
3. Haz clic en **"Escuchar"** para ponerte en modo servidor.

### Modo Cliente (Emisor)
1. Abre la aplicación en el equipo que **enviará** el archivo.
2. Introduce la IP del receptor en el campo correspondiente.
3. Selecciona el archivo a enviar y haz clic en **"Enviar"**.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta el archivo `Licencia/LICENSE.txt` para más detalles.
