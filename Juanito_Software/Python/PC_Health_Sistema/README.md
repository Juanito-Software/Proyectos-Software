# 🖥️ PC Health Sistema — Monitor Avanzado de Salud del PC

**Autor:** JuanitoSoftware
**Versión:** 1.0
**Licencia:** GNU GPL v3
**Plataforma:** Windows
**Lenguaje:** Python 3

---

## 🧾 Descripción

Aplicación de escritorio desarrollada en Python con **interfaz gráfica (Tkinter)** que permite visualizar en tiempo real información avanzada del hardware y sistema operativo: procesador, memoria RAM, tarjeta gráfica, almacenamiento y placa base. Combina múltiples fuentes de datos (WMI, CPU-Z, psutil, GPUtil) y presenta la información de forma organizada e interactiva, incluyendo **gráficos en tiempo real** de uso y temperatura de CPU y GPU.

---

## 🚀 Características

- 🖥️ **Sistema operativo**: versión, build y arquitectura
- ⚙️ **Procesador**: nombre, núcleos, subprocesos, frecuencias, caché L1/L2/L3 y temperatura (WMI)
- 🎮 **GPU**: detección de tarjetas gráficas con estadísticas de carga y temperatura
- 🧠 **Memoria RAM**: capacidad total, tipo (DDR4/DDR5), frecuencia y uso en tiempo real
- 💾 **Almacenamiento**: espacio total, usado y libre
- 🔌 **Placa base**: fabricante, modelo y chipset (vía XML de CPU-Z y WMI)
- 📊 **Gráficos en tiempo real**: uso y temperatura de CPU y GPU con `matplotlib`
- 🔄 **Integración con CPU-Z**: ejecuta `cpuz.exe` en modo silencioso y procesa el reporte XML automáticamente
- 📋 **Registro de ejecución**: genera `log_ejecucion.txt` con marcas de tiempo de cada análisis
- ⚡ **Multihilo**: gestión con `ThreadPoolExecutor` para no bloquear la interfaz
- 🛡️ **Cierre seguro**: control de señales del sistema (`SIGINT`, `SIGTERM`)
- 📦 **Ejecución autónoma**: disponible como `.exe` compilado para sistemas sin Python

---

## 🔧 Dependencias

| Módulo | Descripción |
|---|---|
| `tkinter` | Interfaz gráfica |
| `psutil` | Estadísticas de CPU, RAM y procesos |
| `wmi` | Consulta avanzada del sistema (solo Windows) |
| `GPUtil` | Información de la GPU |
| `matplotlib` | Gráficos de uso y temperatura |
| `cpuinfo` | Información detallada del procesador |
| `tabulate` | Formato de salida tabular en consola |
| `xml.etree.ElementTree` | Lectura de reportes XML de CPU-Z |
| `concurrent.futures` | Manejo de tareas en segundo plano |
| `logging` | Registro de actividad del sistema |
| `progress_bar_utils` | Barra de progreso animada de carga inicial |

Módulos estándar: `tkinter` · `os` · `sys` · `threading` · `signal`

---

## ⚙️ Requisitos del Sistema

- **Plataforma:** Windows (requerido por CPU-Z y las APIs WMI/Win32)
- **Python:** 3.8 o superior
- **CPU-Z** (`cpuz.exe` y `cpuz.ini`) incluido en la carpeta `Sistema/`

---

## 📦 Instalación

```bash
pip install -r requirements.txt
```

Asegúrate de que `cpuz.exe` y `cpuz.ini` están presentes en la carpeta `Sistema/`.

---

## 📁 Estructura del Proyecto

```plaintext
PC_Health_Sistema/
├── main.py                        # Punto de entrada — GUI principal
├── Sistema/
│   ├── generar_output_cpuz_xml.py # Genera el reporte XML con CPU-Z
│   ├── generar_output_cpuz_xml.exe# Versión compilada (sin Python)
│   ├── SistemaProExtreme.py       # Módulo avanzado de estadísticas en tiempo real
│   ├── cpuz.exe                   # Binario de CPU-Z
│   ├── cpuz.ini                   # Configuración de CPU-Z
│   └── output.xml                 # Reporte XML generado
├── progress_bar_utils.py          # Barra de progreso animada
├── hook-cpuinfo.py                # Hook para PyInstaller
├── log_ejecucion.txt              # Registro de ejecuciones
├── requirements.txt
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso y Ejecución

### Aplicación principal con GUI
```bash
python main.py
```

### Generar reporte de hardware con CPU-Z
```bash
cd Sistema
python generar_output_cpuz_xml.py
```
Ejecuta CPU-Z en modo silencioso, captura el reporte y lo guarda como `output.xml`.

### Monitor avanzado en consola
```bash
cd Sistema
python SistemaProExtreme.py
```

### Versión ejecutable (sin Python)
Haz doble clic en `generar_output_cpuz_xml.exe` dentro de la carpeta `Sistema/`.

---

## 📊 Ejemplo de datos recogidos

El reporte XML de CPU-Z incluye:

| Categoría | Datos |
|---|---|
| CPU | Nombre, núcleos, frecuencias, caché L1/L2/L3 |
| Placa base | Fabricante, modelo, chipset |
| RAM | Capacidad total, tipo, frecuencia |
| Sistema operativo | Versión, build, arquitectura |

---

## ⚖️ Licencia

Este proyecto utiliza **CPU-Z** (software propietario de CPUID, uso gratuito permitido). El código Python propio está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
