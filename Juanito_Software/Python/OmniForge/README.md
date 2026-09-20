# OmniForge

Agente IA autónomo que controla un PC completo: ejecuta código, navega la web y maneja el ratón, teclado y pantalla.

OmniForge funciona en dos modos:
- **Planner multi-agente (por defecto)**: un orquestador descompone la tarea en pasos y los reparte entre agentes especializados (`coder`, `researcher`, `pc_controller`).
- **Agente único (`--solo`)**: un solo agente con las 29 herramientas a su disposición.

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso](#uso)
5. [Herramientas disponibles](#herramientas-disponibles)
6. [Arquitectura](#arquitectura)
7. [Skills (plugins de herramientas)](#skills-plugins-de-herramientas)
8. [Memoria persistente](#memoria-persistente)
9. [Cambiar de modelo LLM](#cambiar-de-modelo-llm)
10. [Añadir herramientas propias](#añadir-herramientas-propias)
11. [Tests](#tests)
12. [Solución de problemas](#solución-de-problemas)

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
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe   # OCR (opcional)
```

### `config.py` — ajustes globales

Todos los parámetros del agente viven en `config.py`, agrupados por sección en dataclasses. Puedes editarlo directamente o reemplazar la instancia global `CONFIG` desde tu propio script antes de llamar a `run()`.

| Sección | Campo | Por defecto | Descripción |
|---|---|---|---|
| `llm` | `provider` | `"ollama"` | Proveedor LLM: `ollama`, `anthropic`, `openai`, `google` |
| `llm` | `model` | `"qwen3:8b"` | Nombre del modelo |
| `llm` | `temperature` | `0.0` | 0 = determinista, 1 = creativo |
| `llm` | `max_tokens` | `4096` | Tokens máximos por respuesta |
| `llm` | `fallback_providers` | `[ollama qwen2.5:7b]` | Cadena de respaldo si el primario falla |
| `tools` | `terminal_timeout` | `60` | Segundos máximos por comando de terminal |
| `tools` | `browser_headless` | `True` | `False` para ver el navegador durante la ejecución |
| `screen` | `failsafe` | `True` | Mover el ratón a la esquina superior-izquierda detiene el agente |
| `screen` | `action_pause` | `0.1` | Pausa en segundos entre acciones de ratón/teclado |
| `screen` | `max_screenshots` | `50` | Rotar capturas antiguas al superar este límite |
| `agent` | `max_iterations` | `20` | Iteraciones máximas antes de parar |
| `agent` | `max_retries` | `3` | Reintentos por error de herramienta |
| `agent` | `verbose` | `True` | Muestra progreso en consola |
| `vision` | `engine` | `"ollama"` | Visión: `ocr` (solo Tesseract), `ollama`, `anthropic`, `openai` |
| `vision` | `model` | `"llava:7b"` | Modelo de visión (Ollama) |
| `evaluator` | `enabled` | `True` | Registra cada tarea en `evaluations/evaluations.jsonl` |
| `logging` | `enabled` | `True` | Escribe logs JSONL en `logs/` |
| `memory` | `enabled` | `True` | Persiste tareas, hechos y hints en `memory/memory.json` |
| `memory` | `max_entries` | `1000` | Máximo de tareas en el historial |
| `memory` | `semantic_threshold` | `500` | Usar búsqueda semántica a partir de este nº de tareas |

---

## Uso

### Modo Planner multi-agente — una sola tarea (por defecto)

```bash
python main.py "abre el bloc de notas y escribe Hola Mundo"
```

### Modo solo — agente único

```bash
python main.py --solo "busca en Google el precio del bitcoin y dímelo"
```

### Modo interactivo

```bash
python main.py            # Planner multi-agente
python main.py --solo     # agente único
```

Escribe `exit` o pulsa `Ctrl+C` para salir.

### Desde Python

```python
from config import CONFIG
from core.planner import build_planner_graph
from core.memory import MemoryStore

memory = MemoryStore(path=CONFIG.memory.path)
graph = build_planner_graph(CONFIG, memory=memory)
```

Para configuraciones simples se puede usar `_init_graph()` de `main.py`, que construye el grafo (planner o agente único) con los objetos de memoria/evaluador/logger ya resueltos:

```python
from main import _init_graph, _init_memory, _init_evaluator, _init_logger, run

memory = _init_memory()
evaluator = _init_evaluator()
logger = _init_logger()
graph = _init_graph(solo=True, memory=memory, evaluator=evaluator)

resultado = run(
    "captura una pantalla y dime qué hay en ella",
    solo=True, graph=graph, memory=memory, evaluator=evaluator, logger=logger,
)
print(resultado)
```

> Nota: `run()` no construye nada internamente — recibe `graph`, `memory`, `evaluator` y `logger` ya preparados. El flujo interactivo de `main.py` (función `interactive`) muestra cómo construirlo todo una sola vez y reutilizarlo entre tareas.

### Parada de emergencia

Con `screen.failsafe = True` (por defecto), mueve el ratón rápidamente a la **esquina superior-izquierda** de la pantalla. Pyautogui lanza una excepción y el agente para inmediatamente.

---

## Herramientas disponibles

El agente dispone de **29 herramientas** repartidas en 5 módulos. Las llama automáticamente según la tarea — no tienes que invocarlas tú.

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
| `get_current_url()` | Lee la URL real de Chrome (Ctrl+L + Ctrl+C + portapapeles) |
| `list_open_windows()` | Lista las ventanas abiertas con sus títulos (PowerShell) |
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
| `sleep_seconds(seconds)` | Espera N segundos (recortado a 0.1–30 s) |

### Visión (`tools/vision.py`)

Visión en dos capas independientes — primero OCR (locale, instantáneo, sin LLM); solo si hace falta, visión LLM:

| Herramienta | Descripción |
|---|---|
| `read_screen_text()` | Extrae todo el texto visible con OCR (Tesseract) |
| `find_text_on_screen(text)` | Localiza un texto en pantalla y devuelve sus coordenadas |
| `describe_screen(question)` | Descripción IA de lo que hay en pantalla (visión LLM) |
| `find_element(description)` | Localiza un elemento de UI (iconos, imágenes) con visión LLM |

Para OCR necesitas [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) instalado (o `CONFIG.vision.tesseract_cmd`). La visión LLM necesita `ollama pull llava` (u otro modelo multimodal).

---

## Arquitectura

```
OmniForge/
├── config.py           ← Configuración central — secciones LLM/Tools/Screen/Agent/Vision/Evaluator/Logging/Memory
├── main.py             ← Entrada CLI, modo interactivo y función run()
├── requirements.txt
├── core/
│   ├── state.py        ← AgentState y PlannerState (TypedDict) — fuente única de verdad
│   ├── llm.py          ← build_llm(config) → BaseChatModel + cadena de fallbacks
│   ├── graph.py        ← Grafo de agente: reason → tools → post_tools (+ compresión, fallbacks)
│   ├── planner.py      ← Grafo multi-agente: plan → execute_step ×N → synthesize
│   ├── agents.py       ← REGISTRO de agentes (coder, researcher, pc_controller)
│   ├── memory.py       ← MemoryStore — tareas, hechos, hints y embeddings
│   ├── evaluator.py    ← Evaluator — registra y analiza cada ejecución
│   ├── logger.py       ← OmniForgeLogger — eventos JSONL + integración LangSmith
│   └── skills.py       ← Cargador de skills (plugin loader)
├── tools/
│   ├── __init__.py     ← ALL_TOOLS = FS + Terminal + Browser + Screen + Vision (29)
│   ├── filesystem.py
│   ├── terminal.py
│   ├── browser.py
│   ├── screen.py
│   └── vision.py
└── skills/             ← skills cargadas automáticamente (ver abajo)
```

### Agente (modo `--solo`) — `core/graph.py`

```
Usuario
  │
  ▼
[reason] → LLM decide qué herramienta usar
  │
  ├─ sin tool call ──────────────► [remind] si aún no llamó action tools → [reason]
  │                                 ► [END] si ya actuó
  └─ con tool call
        │
        ▼
      [tools] → ejecuta la herramienta
        │
        ▼
    [post_tools] → detecta errores, actualiza contador
        │
        ├─ historial largo ──────► [compress] (resume medio, preserva cabeza+cola)
        │
        └──────────────────────► [reason] siguiente iteración
```

El agente usa una **cadena de fallbacks**: si el LLM primario falla (timeout, sobrecarga), prueba el siguiente `fallback_providers` en orden. `Error_count` y `max_iterations` cortan los bucles; el modo `remind` corrige al agente cuando responde con texto sin haber llamado una herramienta de acción.

### Planner multi-agente (por defecto) — `core/planner.py`

```
Usuario
  │
  ▼
[plan] → LLM descompone la tarea en pasos [{agent, subtask}]
  │
  ├─ sin pasos válidos ──────────► [synthesize]
  │
  └─ con pasos ─────────────────► [execute_step] → invoca al agente especializado del paso
                                    │
                                    └─ (repite hasta completar todos) ──► [synthesize]
                                                                              │
                                                                              ▼
                                                              respuesta final + efectos en background
```

Los agentes especializados se construyen una sola vez desde `core/agents.py` (`REGISTRY`):
- **`coder`** — ejecuta código, lee/escribe archivos, y usa las tools de OCR (`read_screen_text`, `find_text_on_screen`).
- **`researcher`** — busca en la web, navega URLs, extrae contenido.
- **`pc_controller`** — controla la pantalla (capturas, clics, teclado) y es el único con visión IA (`describe_screen`, `find_element`). Obligado a un tool por respuesta (`sequential_tools`).

---

## Skills (plugins de herramientas)

Apiádate del patrón de OpenClaw/Hermes: coloca un `.py` con funciones `@tool` en `skills/` y se carga automáticamente — sin tocar nada más.

Incluidas de serie:

| Skill | Descripción |
|---|---|
| `compress.py` | Compresión/extracción de archivos ZIP con stdlib |
| `example_notify.py` | Notificación de escritorio (Windows) — plantilla para crear skills |
| `fetch.py` | HTTP fetch ligero para APIs REST y JSON |
| `speak.py` | Texto a voz con Windows SAPI (sin dependencias) |
| `system_info.py` | Información del sistema y procesos (system awareness) |

`SKILL_METADATA` (opcional) en cada archivo restringe a qué agentes se añade: `{"agents": ["coder", "pc_controller"]}`; omitirlo = todos los agentes.

---

## Memoria persistente

`MemoryStore` guarda en `memory/memory.json`:
- **Tareas completadas** (hasta `max_entries`), con timestamp, resultado y agentes usados.
- **Hechos durables** del usuario/sistema (rutas, apps instaladas, preferencias).
- **Hints de planificación** generados por el evaluador.

La recuperación es adaptativa: con pocas tareas inyecta las `n_recent` últimas en orden cronológico; al superar `semantic_threshold` usa similitud coseno con `nomic-embed-text` (requiere `ollama pull nomic-embed-text`). Si Ollama no responde, cae a cronológico.

`core/evaluator.py` registra cada tarea en `evaluations/evaluations.jsonl` (fallo, eficiencia, agentes) y cada `analyze_every` tareas analiza los patrones para generar un hint de mejora que se inyecta en el siguiente `plan()`.

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

Hay dos vías:

**1. Tools en `tools/` (agentes que las use deben listarlas)**

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

Regístrala en `tools/__init__.py` y, si la quieres en un agente concreto, en su entrada de `core/agents.py`.

**2. Skills en `skills/` (recomendado — sin tocar nada más)**

```python
# skills/mis_tools.py
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
```

Al arrancar, `core/skills.load_skills()` la carga y la inyecta en los system prompts — el agente la usará automáticamente.

---

## Tests

La suite usa `pytest`. Instala las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Ejecuta:

```bash
pytest
```

Los tests cubren la lógica pura del núcleo (parsing de planes, evaluador, memoria, skills, providers, filesystem) **sin** tocar LLM, pantalla, navegador ni red. Actualmente la suite tiene **115 tests**.

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

### Las tools de visión dan error de Tesseract

Instala [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) o apunta `CONFIG.vision.tesseract_cmd` a su ejecutable. Sin él, `read_screen_text()` y `find_text_on_screen()` devuelven un error claro.