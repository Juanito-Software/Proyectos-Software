# God Loquete - Ficha Técnica

**Nombre del Proyecto:** God Loquete  
**Autor:** Juanito Software  
**Licencia:** [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)  
**Lenguaje:** Python 3  
**Interfaz Gráfica:** Tkinter  
**Dependencias:** `tkinter`, `Pillow`, `pyogg`, `pyaudio`, `numpy`, `pyrtp`, `struct`, `socket`, `threading`, `logging`, `time`, `random`  

## Descripción General

**God Loquete** es una aplicación de comunicación por voz en red, descentralizada, diseñada para gestionar llamadas grupales en una arquitectura P2P con elección dinámica de host. Incorpora audio en tiempo real con codificación Opus y transmisión mediante RTP sobre UDP.

## Características

- Comunicación de voz en tiempo real.
- Transmisión de audio comprimido usando el códec Opus.
- Encapsulación de audio en paquetes RTP.
- Detección automática de caídas del host y elección de nuevo host mediante heartbeat.
- Buffer de audio basado en `deque` para manejar jitter y pérdidas.
- Mezcla de audio de múltiples clientes y redistribución desde el host.
- Interfaz gráfica con estado de conexión.
- Servidor TCP para gestión de conexiones y descubrimiento de IPs.

## Arquitectura del Sistema

- **Cliente/Servidor:** TCP para control e intercambio de IPs.
- **Audio:** RTP sobre UDP con reenvío de paquetes y mezcla en el host.
- **Heartbeat:** UDP broadcast para detección de host caído y elección de nuevo host.
- **Interfaz de usuario:** Aplicación de escritorio con Tkinter.

## Puertos Utilizados

| Funcionalidad           | Protocolo | Puerto  |
|------------------------|-----------|---------|
| Servidor TCP           | TCP       | 12345   |
| Heartbeat / Elección   | UDP       | 12346   |
| Audio RTP              | UDP       | 12347   |

## Dependencias

Instalación recomendada de dependencias vía `pip`:

```bash
pip install pyogg pyaudio numpy Pillow pyrtp
```

## Uso

Ejecutar el script principal para abrir la interfaz:

```bash
python god_loquete.py
```

- Pulsar **Entrar** para unirse a la llamada.
- Pulsar **Salir** para desconectarse.
- El programa detecta automáticamente si debe actuar como host o cliente.

---

## 📃 Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública General de GNU, versión 3 o cualquier versión posterior.

Consulta la licencia completa para más detalles.
Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware&Games

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
