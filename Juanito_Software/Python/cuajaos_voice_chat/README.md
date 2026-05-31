# 🎙️ cuajaos_voice_chat - Sistema de Chat de Voz RTP

Sistema completo de transmisión y recepción de chat de voz en tiempo real diseñado para redes locales, utilizando el protocolo **RTP (Real-time Transport Protocol)** sobre sockets UDP.

Este repositorio alberga dos versiones complementarias de la aplicación:
1. **CuajaosFamilyVoiceChat**: La versión multiusuario que implementa compresión de audio y control de flujo.
2. **CuajaosFamilyVoiceChat1v1**: Una versión simplificada ideal para comunicación directa de punto a punto (1 a 1).

---

## 🚀 Características

- **Compresión de Audio**: Utiliza el códec **Opus** mediante `pyogg` para un uso de ancho de banda extremadamente eficiente con una latencia mínima.
- **Protocolo RTP**: Encapsulación estándar RTP de paquetes de audio sobre UDP para asegurar la correcta secuenciación y marca de tiempo de la voz.
- **Corrección Unicast inteligente**: Sistema robusto para evitar el envío de tráfico residual a `localhost` en caso de pérdida o desconexión del host.
- **Interfaz Gráfica Intuitiva**: Construida en **Tkinter**, permitiendo iniciar la transmisión, configurar hosts y ver el estado de la conexión de un vistazo.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- Dependencias de Python necesarias:
  - `numpy`
  - `pyaudio` (para captura y reproducción de audio por hardware)
  - `pyogg` (bindings del codec de audio Opus)
  - `Pillow` (para elementos gráficos en Tkinter)

---

## 📦 Instalación

1. Asegúrate de tener instalado Python y las herramientas de compilación para tu sistema operativo (especialmente para `pyaudio` y `pyogg`).
2. Abre la consola en este directorio e instala las dependencias:
   ```bash
   pip install numpy pyaudio pyogg Pillow
   ```

---

## 💻 Uso y Ejecución

### Versión Multiusuario (CuajaosFamilyVoiceChat)
Esta versión está diseñada para múltiples clientes en la red local.
1. Dirígete a la carpeta `CuajaosFamilyVoiceChat`.
2. Inicia la aplicación ejecutando:
   ```bash
   python CuajaosFamilyVoiceChat.py
   ```

### Versión 1v1 (CuajaosFamilyVoiceChat1v1)
Esta versión está pensada para debates o llamadas de 2 personas.
1. Dirígete a la carpeta `CuajaosFamilyVoiceChat1v1`.
2. Ejecuta:
   ```bash
   python CuajaosFamilyVoiceChat.py
   ```

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta el archivo `Licencia/LICENSE.txt` para más detalles.
