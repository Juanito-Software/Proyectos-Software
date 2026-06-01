# 🖥️ PC Health Sistema - Monitor Extremo de Salud del PC

Herramienta avanzada de **monitorización y diagnóstico del hardware** del sistema, que integra la potencia de **CPU-Z** para obtener información detallada del procesador, memoria y placa base, y la presenta de forma organizada mediante un reporte estructurado en XML.

---

## 🚀 Características

- **Integración con CPU-Z**: Ejecuta `cpuz.exe` de manera silenciosa y automatizada para capturar un informe completo del hardware en formato XML.
- **Parser de reportes XML**: Procesa y muestra de forma legible los datos de CPU, memoria RAM, placa base y frecuencias de reloj.
- **Registro de ejecución**: Genera automáticamente un `log_ejecucion.txt` con marcas de tiempo de cada análisis realizado.
- **Sistema Extremo (`SistemaProExtreme.py`)**: Módulo avanzado de estadísticas del sistema en tiempo real.
- **Hook personalizado**: `hook-cpuinfo.py` para integración avanzada con PyInstaller y herramientas de diagnóstico de CPU.
- **Ejecución autónoma**: Disponible como ejecutable `.exe` compilado para sistemas sin Python.

---

## 🛠️ Requisitos del Sistema

- **Windows** (requerido por CPU-Z y las APIs Win32)
- **Python 3.9+** (para ejecutar desde código fuente)
- **CPU-Z** (`cpuz.exe`) incluido en la carpeta `Sistema/`
- Dependencias opcionales de Python para el módulo avanzado:
  ```bash
  pip install cpuinfo psutil
  ```

---

## 📦 Instalación

1. Asegúrate de que `cpuz.exe` y `cpuz.ini` están presentes en la carpeta `Sistema/`.
2. Para el módulo Python avanzado:
   ```bash
   pip install cpuinfo psutil
   ```

---

## 💻 Uso y Ejecución

### Generar reporte de hardware con CPU-Z
```bash
cd PC_Health_Sistema/Sistema
python generar_output_cpuz_xml.py
```
Esto ejecutará CPU-Z en modo silencioso, capturará el reporte XML y lo guardará en `output.xml`.

### Monitor del sistema avanzado
```bash
cd PC_Health_Sistema/Sistema
python SistemaProExtreme.py
```

### Versión ejecutable (sin Python)
Haz doble clic en `generar_output_cpuz_xml.exe` en la carpeta `Sistema/`.

---

## 📊 Ejemplo de datos recogidos

El reporte XML incluye información detallada como:
- **CPU**: Nombre, núcleos, frecuencias, caché L1/L2/L3
- **Placa base**: Fabricante, modelo, chipset
- **RAM**: Capacidad total, tipo (DDR4/DDR5), frecuencia
- **Sistema operativo**: Versión, arquitectura

---

## ⚖️ Licencia

Este proyecto utiliza **CPU-Z** (software propietario de CPUID, uso permitido gratuitamente). El código Python propio está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**.
