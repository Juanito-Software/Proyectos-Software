# 📤 Enviar Archivos Python — Transferencia de Archivos en Red LAN

**Autor:** JuanitoSoftware · **Versión:** 1.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3.x · **Interfaz:** Tkinter GUI

---

## 🧾 Descripción

Aplicación de escritorio en Python con interfaz gráfica basada en `Tkinter` que permite la **transferencia de archivos punto a punto (P2P)** a través del protocolo **TCP/IP** en red local (LAN), sin necesidad de internet ni software de terceros.

Incorpora medidas básicas de seguridad mediante un sistema de direcciones hash personalizadas (SHA-256) basadas en el nombre del usuario, como mecanismo de autenticación del destinatario.

---

## 🚀 Características

- 🌐 **Transferencia directa por LAN**: sin pasar por internet
- 🧠 **Generación de dirección única** por usuario (hash SHA-256)
- 🔐 **Validación del receptor** mediante coincidencia de hash
- 📤 **Envío de archivos** a una IP y dirección hash específicas
- 📥 **Recepción automática** de archivos en carpeta dedicada
- 🖥️ **Interfaz gráfica intuitiva** con barra de progreso visual
- ✅ **Verificación de integridad**: hash para detectar corrupción durante la transferencia
- 🪄 **Efecto visual opcional** (`matrix_effect.exe`) al iniciar
- 📦 **Sin dependencias externas**: solo librerías estándar de Python

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- No requiere instalación de paquetes externos. Módulos utilizados (todos estándar):

  `tkinter` · `socket` · `hashlib` · `json` · `threading` · `subprocess` · `os` · `sys` · `random` · `string`

---

## 📦 Instalación

1. Asegúrate de tener **Python 3.9 o superior** instalado y accesible desde el sistema.
2. Clona o descarga este repositorio en tu equipo.
3. No es necesario instalar dependencias adicionales.

---

## 📁 Estructura de carpetas

```plaintext
Enviar_Archivos_Python/
├── EnviarArchivos.py
├── ejecutar.bat              # Lanzador para Windows
├── matrix_effect.exe         # Efecto visual (opcional)
├── received_files/           # Carpeta donde se guardan los archivos recibidos
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso y Ejecución

### Opción A: Lanzador automático (recomendado en Windows)
Haz doble clic en `ejecutar.bat` dentro de la carpeta del proyecto.

### Opción B: Desde la consola
```bash
cd Enviar_Archivos_Python
python EnviarArchivos.py
```

---

### 📥 Modo Servidor (Receptor)

1. Abre la aplicación en el equipo que **recibirá** el archivo.
2. Anota la **IP local** que aparece en la interfaz.
3. Haz clic en **"Escuchar"** para activar el modo servidor.

### 📤 Modo Cliente (Emisor)

1. Abre la aplicación en el equipo que **enviará** el archivo.
2. Introduce la **IP** y la **dirección hash** del receptor.
3. Selecciona el archivo a enviar y haz clic en **"Enviar"**.

---

## 🔒 Seguridad

- Cada usuario genera su dirección única mediante: nombre introducido → caracteres aleatorios intercalados → hash **SHA-256**.
- Solo se aceptan archivos si el hash del remitente coincide con el del receptor.
- Si el hash es incorrecto, el archivo es **rechazado silenciosamente**.
- ⚠️ El sistema **no incluye cifrado en tránsito**; se recomienda usar exclusivamente en entornos de confianza.

---

## 🧪 Detalles Técnicos

| Parámetro | Valor |
|---|---|
| Puerto | `5001` TCP |
| Tamaño de buffer | `4096 bytes` |
| Formato del header | JSON serializado con tamaño prefijado (4 bytes) |
| Transmisión | Por bloques hasta completar el archivo |

---

## ❗ Posibles Errores

- Si `matrix_effect.exe` no está disponible, se omite sin afectar la funcionalidad.
- Un hash incorrecto provoca el rechazo silencioso del archivo.
- Asegúrate de que el **puerto 5001** esté permitido por el firewall en ambos equipos.

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Consulta el archivo `Licencia/LICENSE.txt` o visita [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html) para más detalles.

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
