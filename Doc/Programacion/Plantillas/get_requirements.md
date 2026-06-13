# get_requirements.md

## Objetivo

Generar un `requirements.txt` fiable para un proyecto Python utilizando el entorno virtual como fuente de verdad.

---

## Método recomendado (100% fiable)

### 1. Crear entorno virtual limpio

```bash
python -m venv venv
```

### 2. Activar entorno

Windows:

```bash
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias necesarias

Ejecutar el proyecto y resolver los errores `ModuleNotFoundError` instalando únicamente los paquetes realmente utilizados.

Ejemplo:

```bash
pip install requests
pip install flask
```

### 4. Generar requirements.txt

```bash
pip freeze > requirements.txt
```

### 5. Verificar

Eliminar el entorno virtual:

```bash
rmdir /s /q venv
```

Crear uno nuevo:

```bash
setup.bat
```

Comprobar que el proyecto funciona correctamente.

---

## Método rápido para proyectos existentes

### Buscar imports

```bash
findstr /s /i "^import ^from" *.py
```

o

```bash
pip install pipreqs
pipreqs .
```

Generará un requirements aproximado basado en los imports detectados.

### Revisar resultado

Comprobar especialmente:

* módulos internos del proyecto
* dependencias opcionales
* imports dinámicos
* paquetes renombrados en PyPI

Ejemplos:

```python
import PIL
```

requiere:

```text
Pillow
```

```python
import yaml
```

requiere:

```text
PyYAML
```

---

## Método de validación final

Crear entorno limpio:

```bash
python -m venv test_env
```

Instalar:

```bash
test_env\Scripts\pip install -r requirements.txt
```

Ejecutar:

```bash
test_env\Scripts\python src\main.py
```

Si funciona sin errores de módulos, el requirements es válido.

---

## Herramientas recomendadas

### pip freeze

Fuente de verdad cuando el entorno está limpio.

```bash
pip freeze > requirements.txt
```

### pipreqs

Inferencia automática desde imports.

```bash
pip install pipreqs
pipreqs .
```

### Poetry

Gestión profesional de dependencias.

```bash
poetry add requests
poetry install
```

---

## Orden de prioridad

1. Poetry / pyproject.toml
2. pip freeze desde entorno limpio
3. pipreqs
4. Revisión manual
5. Consulta externa (ChatGPT)

```
```
