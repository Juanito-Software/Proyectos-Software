# 🌱 pyseed

> Genera proyectos Python limpios y modernos en segundos.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build: Hatchling](https://img.shields.io/badge/build-hatchling-blueviolet)](https://hatch.pypa.io)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-none-green.svg)]()

`pyseed` es una herramienta de línea de comandos que genera la estructura de un proyecto Python moderno: `src/` layout, `pyproject.toml` con PEP 621, licencias, tests, Git y más. Sin dependencias externas. Funciona con cualquier Python 3.8+.

---

## ✨ Características

| Característica | Descripción |
|---|---|
| 📁 **`src/` layout** | Previene importaciones accidentales del código fuente local |
| 📦 **`pyproject.toml`** | Configuración unificada bajo PEP 621, sin `setup.py` |
| 🔑 **Licencias** | MIT, Apache 2.0, GPLv3, BSD 3-Clause generadas automáticamente |
| 🧪 **Tests** | Estructura `tests/` con `pytest` o `unittest` lista para usar |
| 🖥️ **CLI opcional** | Entrypoint ejecutable con `argparse` y `__main__.py` |
| 🐙 **Git** | `git init`, `.gitignore` y `.gitattributes` optimizados para Python |
| 🐍 **`.venv`** | Creación opcional de entorno virtual en el mismo paso |
| 📜 **Poetry** | Modo Poetry: `pyproject.toml` declarativo + `scripts/` con `.bat` listos |
| 🎨 **Terminal** | Colores ANSI, iconos Unicode, spinner animado y árbol de archivos final |
| ⚡ **Cero dependencias** | Solo la biblioteca estándar de Python 3.8+ |

---

## 📦 Instalación

```bash
git clone <url-del-repositorio>
cd pyseed
pip install -e .
```

Verifica que funciona:

```bash
pyseed --version-cli
```

---

## 🚀 Uso

### Modo interactivo (recomendado)

```bash
pyseed
```

El asistente te pregunta paso a paso: nombre, descripción, autor, licencia, CLI, tests, Git, Poetry y entorno virtual. Detecta tu nombre y email desde la configuración de Git automáticamente.

### Modo directo

```bash
# Proyecto básico
pyseed mi-proyecto

# Con todas las opciones
# Windows:
pyseed mi-api --description "Una API REST moderna" --license "Apache 2.0" --author "Juan García" --email "juan@example.com" --cli --framework pytest --venv --no-git --output-dir C:\Users\User\Desktop

# Linux:
pyseed mi-api \
  --description "Una API REST moderna" \
  --license "Apache 2.0" \
  --author "Juan García" \
  --email "juan@example.com" \
  --cli \
  --framework pytest \
  --venv \
  --no-git \
  --output-dir ~/proyectos

# Con Poetry como gestor de dependencias
pyseed mi-proyecto --poetry --cli

# Sin Git ni tests
pyseed mi-script --no-git --no-tests --license "BSD 3-Clause"
```

### Como módulo Python (si no está en el PATH del sistema)

```bash
python -m pyseed mi-proyecto --cli
```

---

## 📋 Opciones

```
pyseed [project_name] [opciones]

Argumentos posicionales:
  project_name          Nombre del proyecto. Omitir para modo interactivo.

Opciones:
  -o, --output-dir DIR  Directorio destino (default: directorio actual)
  -d, --description     Descripción del proyecto
  -v, --version VER     Versión inicial (default: 0.1.0)
  -a, --author NAME     Nombre del autor
  -e, --email EMAIL     Email del autor
  -l, --license LIC     MIT | Apache 2.0 | GPLv3 | BSD 3-Clause | None
      --python VER      Versión mínima de Python (default: >=3.8)
      --cli             Generar entrypoint CLI ejecutable
      --no-tests        Omitir estructura de tests
      --framework FW    pytest | unittest (default: pytest)
      --no-git          No inicializar Git
      --venv            Crear entorno virtual .venv
      --poetry          Usar Poetry como gestor de dependencias (incompatible con --venv)
      --defaults        Usar valores por defecto sin preguntar
      --version-cli     Muestra la versión de pyseed
```

---

## 📂 Estructura generada

### Modo estándar (Hatchling)

```
mi-proyecto/
├── pyproject.toml          # Metadatos y configuración (PEP 621, Hatchling)
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── src/
│   └── mi_proyecto/
│       ├── __init__.py
│       ├── core.py
│       ├── cli.py          # Solo con --cli
│       └── __main__.py     # Solo con --cli
└── tests/
    ├── __init__.py
    └── test_mi_proyecto.py
```

### Modo Poetry (`--poetry`)

```
mi-proyecto/
├── pyproject.toml          # Backend Poetry con [tool.poetry] y lockfile
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── scripts/
│   ├── setup.bat           # poetry install
│   ├── run.bat             # poetry run ...
│   └── build.bat           # PyInstaller vía Poetry (solo con --cli)
├── src/
│   └── mi_proyecto/
│       ├── __init__.py
│       ├── core.py
│       ├── cli.py          # Solo con --cli
│       └── __main__.py     # Solo con --cli
└── tests/
    ├── __init__.py
    └── test_mi_proyecto.py
```

---

## 📜 Modo Poetry

Al usar `--poetry`, pyseed genera un `pyproject.toml` declarativo para [Poetry](https://python-poetry.org/) en lugar del backend Hatchling estándar:

```toml
[tool.poetry]
name = "mi-proyecto"
version = "0.1.0"
description = "..."
authors = ["Juan <juan@example.com>"]
packages = [{include = "mi_proyecto", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

También genera `scripts/` con tres `.bat` listos para usar en Windows:

| Script | Comando equivalente |
|---|---|
| `scripts/setup.bat` | `poetry install` |
| `scripts/run.bat` | `poetry run python -m mi_proyecto` |
| `scripts/build.bat` | `poetry run pyinstaller ...` (solo con `--cli`) |

> **Nota:** `--poetry` es incompatible con `--venv`. Poetry gestiona su propio entorno virtual.

---

## ⚡ Ejemplo de sesión

```
$ pyseed
┌────────────────────────────────────────────────────────┐
│  🌱  pyseed v0.1.0 — Python Project Generator          │
│  Genera estructuras limpias e impecables de inmediato  │
└────────────────────────────────────────────────────────┘

? Nombre del proyecto: super-api
? Descripción breve: Una API REST moderna
? Versión inicial (default: 0.1.0):
? Nombre del autor (default: Juan García):
? Email (default: juan@example.com):
? Versión de Python compatible (default: >=3.8):
? Licencia: MIT
? ¿CLI ejecutable? [y/N]: y
? ¿Tests? [Y/n]:
? Framework: pytest
? ¿Inicializar Git? [Y/n]:
? ¿Usar Poetry como gestor de dependencias? [y/N]: y

⠙ Sembrando proyecto...
✔ ¡Proyecto creado con éxito! 🎉

📁 super-api
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── scripts/
│   ├── build.bat
│   ├── run.bat
│   └── setup.bat
├── src/
│   └── super_api/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── core.py
└── tests/
    ├── __init__.py
    └── test_super_api.py

Siguientes pasos:
  1. cd super-api
  2. poetry install
  3. poetry run super-api  o  poetry run python -m super_api
     O usar los scripts: scripts\setup.bat / scripts\run.bat
```

---

## 🛠️ Desarrollo

Para contribuir o modificar `pyseed`:

```bash
git clone <url>
cd pyseed
pip install -e .
python -m unittest discover -s tests
```

---

## 📝 Licencia

MIT. Ver [LICENSE](LICENSE) para más detalles.
