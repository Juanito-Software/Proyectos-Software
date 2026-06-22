# OmniForge

Agente IA autónomo que controla un PC completo: ejecuta código, navega la web y maneja el ratón, teclado y pantalla.

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso](#uso)
5. [Herramientas disponibles](#herramientas-disponibles)
6. [Arquitectura](#arquitectura)
7. [Cambiar de modelo LLM](#cambiar-de-modelo-llm)
8. [Añadir herramientas propias](#añadir-herramientas-propias)
9. [Solución de problemas](#solución-de-problemas)

---

## Requisitos

- Python 3.11 o superior
- [Ollama](https://ollama.com) instalado y corriendo (para el proveedor por defecto)
- Windows 10/11 (las herramientas de pantalla usan pyautogui, que funciona en todos los SO pero está probado en Windows)

---

## Instalación

```bash
# 1. Clonar o descargar el proyecto
cd OmniForge

# 2. Instalar dependencias
python -m pip install -r requirements.txt

# 3. Instalar los navegadores de Playwright (para el módulo browser)
python -m playwright install chromium

# 4. Descargar el modelo local (con Ollama)
ollama pull qwen3:8b
```

Si quieres usar Claude, GPT o Gemini en lugar de Ollama, ve a la sección [Cambiar de modelo LLM](#cambiar-de-modelo-llm).

---

## Configuración

### Variables de entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto. Es ignorado por git y cargado automáticamente al arrancar.

```env
# Descomenta la que uses
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=...
```

### `config.py` — ajustes globales

Todos los parámetros del agente viven en `config.py`. Puedes editarlo directamente o sobreescribir `CONFIG` en tu propio script antes de llamar a `build_graph()`.

| Sección | Campo | Por defecto | Descripción |
|---|---|---|---|
| `llm` | `provider` | `"ollama"` | Proveedor LLM: `ollama`, `anthropic`, `openai`, `google` |
| `llm` | `model` | `"qwen3:8b"` | Nombre del modelo |
| `llm` | `temperature` | `0.0` | 0 = determinista, 1 = creativo |
| `llm` | `max_tokens` | `4096` | Tokens máximos por respuesta |
| `tools` | `terminal_timeout` | `60` | Segundos máximos por comando de terminal |
| `tools` | `browser_headless` | `True` | `False` para ver el navegador durante la ejecución |
| `screen` | `failsafe` | `True` | Mover el ratón a la esquina superior-izquierda detiene el agente |
| `screen` | `action_pause` | `0.1` | Pausa en segundos entre acciones de ratón/teclado |
| `screen` | `screenshot_dir` | `"screenshots"` | Carpeta donde se guardan las capturas |
| `agent` | `max_iterations` | `20` | Iteraciones máximas antes de parar |
| `agent` | `max_retries` | `3` | Reintentos por error de herramienta |
| `agent` | `verbose` | `True` | Muestra progreso en consola |

---

## Uso

### Modo comando — una sola tarea

```bash
python main.py "abre el bloc de notas y escribe Hola Mundo"
```

```bash
python main.py "busca en Google el precio del bitcoin y dímelo"
```

```bash
python main.py "lista los archivos de mi escritorio y guárdalos en un txt"
```

### Modo interactivo — conversación continua

```bash
python main.py
```

Escribe `exit` o pulsa `Ctrl+C` para salir.

### Desde Python

```python
from config import CONFIG
from main import run

# Tarea simple
resultado = run("captura una pantalla y dime qué hay en ella")
print(resultado)
```

```python
# Cambiar modelo antes de ejecutar
from config import CONFIG
CONFIG.llm.provider = "anthropic"
CONFIG.llm.model = "claude-sonnet-4-6"
CONFIG.llm.api_key = "sk-ant-..."

from main import run
run("organiza todos los PDFs del escritorio en carpetas por año")
```

### Parada de emergencia

Con `screen.failsafe = True` (por defecto), mueve el ratón rápidamente a la **esquina superior-izquierda** de la pantalla. Pyautogui lanza una excepción y el agente para inmediatamente.

---

## Herramientas disponibles

El agente dispone de 22 herramientas repartidas en 4 módulos. Las llama automáticamente según la tarea — no tienes que invocarlas tú.

### Sistema de archivos (`tools/filesystem.py`)

| Herramienta | Descripción |
|---|---|
| `read_file(path)` | Lee el contenido de un archivo |
| `write_file(path, content)` | Escribe o sobreescribe un archivo (crea carpetas si faltan) |
| `list_dir(path)` | Lista el contenido de un directorio |
| `delete_file(path)` | Elimina un archivo (no elimina carpetas) |

### Terminal (`tools/terminal.py`)

| Herramienta | Descripción |
|---|---|
| `run_code(code, language)` | Ejecuta código Python, shell, JavaScript o R vía Open Interpreter |
| `run_command(command)` | Ejecuta un comando de shell directamente |

`language` puede ser `"python"`, `"shell"`, `"javascript"` o `"r"`. Si Open Interpreter no está instalado, usa subprocess como fallback para Python y shell.

### Navegador (`tools/browser.py`)

| Herramienta | Descripción |
|---|---|
| `browse_url(url, task)` | Navega a una URL y ejecuta una acción en lenguaje natural |
| `web_search(query)` | Busca en Google y devuelve los 5 primeros resultados |
| `extract_page_content(url)` | Extrae todo el texto de una página web |

El navegador es controlado por [Browser Use](https://github.com/browser-use/browser-use) con Playwright. Para verlo en acción pon `CONFIG.tools.browser_headless = False`.

### Control de pantalla (`tools/screen.py`)

| Herramienta | Descripción |
|---|---|
| `take_screenshot(save_path)` | Captura la pantalla. Sin argumento genera nombre automático en `screenshots/` |
| `get_screen_size()` | Resolución actual en píxeles |
| `get_mouse_position()` | Posición actual del cursor |
| `click(x, y, button)` | Clic en coordenadas absolutas. `button`: `"left"`, `"right"`, `"middle"` |
| `double_click(x, y)` | Doble clic |
| `right_click(x, y)` | Clic derecho (abre menú contextual) |
| `move_mouse(x, y)` | Mueve el cursor sin clicar |
| `drag(x1, y1, x2, y2)` | Arrastra desde un punto hasta otro |
| `scroll(x, y, clicks)` | Scroll en (x, y). Positivo = arriba, negativo = abajo |
| `type_text(text, interval)` | Escribe texto en el campo activo simulando teclado |
| `press_key(key)` | Pulsa una tecla o combinación: `"enter"`, `"ctrl+c"`, `"alt+f4"`, `"win+d"` |
| `copy_to_clipboard(text)` | Copia texto al portapapeles |
| `get_clipboard()` | Lee el portapapeles actual |

---

## Arquitectura

```
OmniForge/
├── config.py           ← Configuración central — modelo, timeouts, flags
├── main.py             ← Entrada CLI e interactivo
├── requirements.txt
├── core/
│   ├── state.py        ← AgentState (TypedDict) — fuente única de verdad
│   ├── llm.py          ← build_llm(config) → BaseChatModel (agnóstico de provider)
│   └── graph.py        ← Grafo LangGraph: reason → tools → post_tools → repeat
└── tools/
    ├── __init__.py     ← ALL_TOOLS = FS + Terminal + Browser + Screen
    ├── filesystem.py
    ├── terminal.py
    ├── browser.py
    └── screen.py
```

**Flujo de ejecución:**

```
Usuario
  │
  ▼
[reason] → LLM decide qué herramienta usar
  │
  ├─ sin tool call ──────────────────────► [END] respuesta final
  │
  └─ con tool call
        │
        ▼
      [tools] → LangGraph ejecuta la herramienta
        │
        ▼
    [post_tools] → detecta errores, actualiza contador
        │
        └──────────────────────────────► [reason] siguiente iteración
```

El `AgentState` es el único estado del sistema. LangGraph es el único que lo muta. El LLM nunca sabe qué proveedor es — solo ve un `BaseChatModel`.

---

## Cambiar de modelo LLM

### Usar Claude (Anthropic)

```python
# En config.py o antes de llamar a run()
CONFIG.llm.provider = "anthropic"
CONFIG.llm.model = "claude-sonnet-4-6"
CONFIG.llm.api_key = "sk-ant-..."   # o ponlo en .env como ANTHROPIC_API_KEY
```

Instala el paquete:
```bash
python -m pip install langchain-anthropic
```

### Usar GPT (OpenAI)

```python
CONFIG.llm.provider = "openai"
CONFIG.llm.model = "gpt-4o"
CONFIG.llm.api_key = "sk-..."   # o OPENAI_API_KEY en .env
```

```bash
python -m pip install langchain-openai
```

### Usar Gemini (Google)

```python
CONFIG.llm.provider = "google"
CONFIG.llm.model = "gemini-2.0-flash"
CONFIG.llm.api_key = "..."   # o GOOGLE_API_KEY en .env
```

```bash
python -m pip install langchain-google-genai
```

### Usar otro modelo local con Ollama

```python
CONFIG.llm.model = "llama3.2"   # cualquier modelo disponible en tu Ollama
```

```bash
ollama pull llama3.2
```

---

## Añadir herramientas propias

1. Crea tu función en `tools/` con el decorador `@tool`:

```python
# tools/mis_tools.py
from langchain_core.tools import tool

@tool
def abrir_aplicacion(nombre: str) -> str:
    """Abre una aplicación por nombre en Windows."""
    import subprocess
    try:
        subprocess.Popen(nombre)
        return f"OK: {nombre} abierto"
    except Exception as e:
        return f"ERROR: {e}"

MIS_TOOLS = [abrir_aplicacion]
```

2. Regístrala en `tools/__init__.py`:

```python
from tools.mis_tools import MIS_TOOLS

ALL_TOOLS = FILESYSTEM_TOOLS + TERMINAL_TOOLS + BROWSER_TOOLS + SCREEN_TOOLS + MIS_TOOLS
```

El agente la usará automáticamente en la siguiente ejecución. No hay que tocar el grafo ni el LLM.

---

## Solución de problemas

### `ModuleNotFoundError: No module named 'langchain_core'`

Asegúrate de instalar con el mismo Python que ejecutas el proyecto:
```bash
python -m pip install -r requirements.txt
```

### El agente mueve el ratón pero el sistema lo bloquea (Windows UAC)

Pyautogui no puede interactuar con ventanas elevadas (UAC, Task Manager) sin permisos de administrador. Ejecuta el terminal como administrador si necesitas controlar esas ventanas.

### `browser_use` no encuentra el navegador

Instala los binarios de Playwright:
```bash
python -m playwright install chromium
```

### El agente entra en bucle sin terminar

Reduce `CONFIG.agent.max_iterations` a 10 para forzar la parada antes. O activa el failsafe (ya está activo por defecto) y mueve el ratón a la esquina superior-izquierda.

### Ollama no responde

Comprueba que el servicio está corriendo:
```bash
ollama list       # lista modelos descargados
ollama serve      # arranca el servidor si no está activo
```

El endpoint por defecto es `http://localhost:11434`. Cámbialo en `CONFIG.llm.base_url` si usas otro puerto.
