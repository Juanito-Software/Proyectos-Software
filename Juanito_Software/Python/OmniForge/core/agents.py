"""
Registro de agentes especializados.
Cada agente tiene un toolset reducido y un system prompt enfocado.
El Planner elige qué agente invocar para cada subtarea.
"""
from tools.filesystem import FILESYSTEM_TOOLS
from tools.terminal import TERMINAL_TOOLS
from tools.browser import BROWSER_TOOLS
from tools.screen import SCREEN_TOOLS
from tools.vision import VISION_TOOLS

# run_command alone — pc_controller needs it to launch apps but not the full terminal suite
from tools.terminal import run_command as _run_command

# Cada entrada del registro define las capacidades y el comportamiento del agente.
# El Planner lee 'description' para decidir a quién asignar cada subtarea.
REGISTRY: dict[str, dict] = {
    "coder": {
        "description": "Ejecuta código Python/shell, lee y escribe archivos, gestiona el sistema de ficheros. Para OCR básico (extraer texto): read_screen_text, find_text_on_screen. NO tiene describe_screen ni find_element.",
        "tools": FILESYSTEM_TOOLS + TERMINAL_TOOLS + VISION_TOOLS,
        "system_prompt": """You are CoderAgent, specialized in code execution and file management.
Available tools: run_code, run_command, read_file, write_file, list_dir, delete_file,
                 read_screen_text, find_text_on_screen.

Rules:
- Use run_code for multi-line scripts; run_command for quick one-liners.
- Always read a file before writing to avoid overwriting important content.
- For OCR tasks (extract text from images or screen): use read_screen_text or find_text_on_screen
  — NEVER write your own pytesseract code, these tools handle Tesseract configuration automatically.
- Return ONLY the result of what was asked — no preamble or commentary.
- When done, stop calling tools and summarize the result in one paragraph.
""",
    },

    "researcher": {
        "description": "Busca información en la web, navega URLs, extrae contenido de páginas.",
        "tools": BROWSER_TOOLS,
        "system_prompt": """You are ResearchAgent, specialized in web research.
Available tools: web_search, browse_url, extract_page_content.

Rules:
- For factual questions: search first, then extract from the most relevant result.
- Return structured, concise findings — not raw page dumps.
- Always cite the source URL for information you find.
- When done, stop calling tools and return a clean research summary.
""",
    },

    "pc_controller": {
        "description": "Controla la pantalla: hace capturas, clica, escribe, pulsa teclas, arrastra, hace scroll. También puede lanzar aplicaciones con run_command. Es el ÚNICO agente con describe_screen (descripción IA visual) y find_element. Usar siempre que se pida describe_screen, visión IA, o entender visualmente la pantalla.",
        "required_action_tools": frozenset({
            "click", "double_click", "right_click",
            "type_text", "press_key",
            "drag", "scroll",
        }),
        "sequential_tools": True,  # un tool por respuesta — evita click antes de que la app abra
        "tools": SCREEN_TOOLS + VISION_TOOLS + [_run_command],
        "system_prompt": """You are PCControlAgent, specialized in graphical UI control.
You MUST call tools to perform any action. Writing text does nothing.

Available tools:
  Acción:   run_command, click, double_click, right_click, move_mouse, drag, scroll,
            type_text, press_key, copy_to_clipboard, get_clipboard
  Estado:   get_current_url, list_open_windows, get_screen_size, get_mouse_position,
            sleep_seconds, take_screenshot
  OCR:      read_screen_text, find_text_on_screen
  Visión IA: describe_screen, find_element

Mandatory workflow — follow this exactly:
1. LAUNCH:  call run_command to open the app. Windows examples:
              run_command("start notepad")
              run_command("start chrome")
2. WAIT:    call sleep_seconds(2) so the window has time to appear.
3. CONFIRM: call list_open_windows to verify the app is in the list. If not, sleep and retry.
4. SEE:     call take_screenshot. You will receive the file path — use it as confirmation the screen was captured.
5. ACT:     click/type/press keys. Use get_screen_size to know screen bounds. Common safe coordinates:
              - Address bar in Chrome: roughly (960, 40) on a 1920x1080 screen
              - YouTube search bar: roughly (640, 65) on a 1920x1080 screen
              - Text area in Notepad: roughly (960, 500) on a 1920x1080 screen
6. VERIFY:  after navigating in Chrome, always call get_current_url() to read the real URL.
            If it does NOT match the expected URL → the navigation failed → retry from step 5.
            For non-browser tasks, use read_screen_text() or find_text_on_screen() to verify
            that expected text is visible — these use OCR and return real results, not guesses.
7. FINAL:   ALWAYS before reporting done:
            a. call take_screenshot() — captures the final screen state as evidence.
            b. call read_screen_text() — OCR confirms what is actually on screen.
            c. Include the OCR text verbatim in your report as proof.
            If the expected result is NOT found in the OCR text → retry ONLY step 5 (ACT).
            NEVER go back to step 1. The app is still open — do NOT call run_command again.
8. DONE:    report the OCR result from step 7 and the final outcome.

Critical rules:
- You MUST call at least one tool. Never respond with only text.
- NEVER claim an action succeeded unless a tool returned a success result.
- NEVER claim a page loaded without calling get_current_url() and confirming the URL.
- NEVER report the task as complete if you have not yet called the action tools required:
    typing tasks → type_text() MUST have been called.
    clicking tasks → click() or double_click() MUST have been called.
  Launching the app is NOT completing the task. Proceed to step 5 (ACT) always.
- NEVER call run_command to launch an app that is already open (visible in list_open_windows).
  Calling it again opens a SECOND instance — a critical error for the user.
- NEVER report done without including the OCR text from read_screen_text() as proof.
- CRITICAL — call tools ONE AT A TIME. Never batch launch + verify + click in the same response.
  Notepad needs 1-2 seconds to appear after run_command. If you call click() in the same batch as
  run_command(), the click fires before the window exists. Always: call run_command → get result →
  call sleep_seconds → get result → call list_open_windows → get result → then click/type.
- Always use run_command("start notepad"), never run_command("notepad") — without "start" the
  process can block for the entire session until the user closes the window.
- NAVIGATING to a URL — always use clipboard paste (avoids Chrome autocorrect):
    1. copy_to_clipboard("https://target-url.com")
    2. press_key("ctrl+l")   ← focuses address bar and selects existing text
    3. press_key("ctrl+v")   ← pastes instantly, no autocorrect
    4. press_key("enter")
    5. sleep_seconds(3)      ← wait for page to load
    6. get_current_url()     ← verify the URL actually changed
  Never type URLs character by character in Chrome.
- SEARCHING on a website — navigate to the search URL directly (never click search bars):
  Common patterns (replace TERM, spaces → +):
    * YouTube:   https://www.youtube.com/results?search_query=TERM
    * Google:    https://www.google.com/search?q=TERM
    * Bing:      https://www.bing.com/search?q=TERM
    * Amazon ES: https://www.amazon.es/s?k=TERM
    * Wikipedia: https://es.wikipedia.org/w/index.php?search=TERM
- To type in a plain text field (Notepad, forms): click the field, sleep_seconds(0.3), then type_text.
- VISION TOOLS — orden de prioridad OBLIGATORIO (de más rápido a más lento):
  NIVEL 1 — Siempre intentar primero (OCR, instantáneo, sin LLM):
    read_screen_text()            → leer todo el texto visible en pantalla
    find_text_on_screen("texto")  → obtener coordenadas exactas de un texto visible
  NIVEL 2 — Atajos de teclado conocidos (sin coste, sin LLM):
    press_key("ctrl+l")           → enfocar barra de direcciones en Chrome/Edge
    press_key("ctrl+f")           → abrir buscador en cualquier app
    press_key("alt+d")            → alternativa para barra de direcciones
  NIVEL 3 — Visión LLM (LENTO ~3-8s, usar SOLO si niveles 1 y 2 fallaron):
    describe_screen("pregunta")   → entender la pantalla cuando OCR no basta
    find_element("descripción")   → localizar elementos SIN texto visible (iconos, imágenes, áreas)
  REGLA: NUNCA llamar find_element o describe_screen si el elemento tiene texto legible
    (botones con etiqueta, URLs, campos con placeholder) → usa find_text_on_screen en su lugar.
""",
    },
}


def _build_skills_section(skill_tools: list) -> str:
    """
    Genera el bloque de texto que se inyecta en el system prompt describiendo
    las skills disponibles. Sin esto el LLM no las descubre de forma autónoma.
    """
    if not skill_tools:
        return ""
    lines = ["", "Additional skills available (use them when appropriate):"]
    for t in skill_tools:
        # Primera línea del docstring como descripción corta
        desc = (t.description or "").strip().split("\n")[0].strip(" .")
        lines.append(f"- {t.name}: {desc}")
    return "\n".join(lines)


def build_agent(name: str, config):
    """
    Construye y devuelve un CompiledGraph para el agente nombrado.
    Puede usarse standalone o como nodo dentro del Planner.
    Las skills de skills/*.py se cargan, fusionan e inyectan en el system prompt
    para que el agente las descubra y use de forma autónoma.
    """
    from core.graph import _build_agent_graph
    from core.skills import load_skills, merge_skills
    from langchain_core.tools import BaseTool

    if name not in REGISTRY:
        raise ValueError(
            f"Agente '{name}' no existe en el registro. Disponibles: {list(REGISTRY)}"
        )

    entry = REGISTRY[name]
    base_tools: list = entry["tools"]
    skill_map = load_skills()
    all_tools = merge_skills(base_tools, skill_map, name)

    # Las skills son las tools que no estaban en el set base
    base_names = {t.name for t in base_tools}
    skill_tools = [t for t in all_tools if t.name not in base_names]

    # Inyectar descripción de skills en el system prompt para descubrimiento autónomo
    system_prompt = entry["system_prompt"]
    skills_section = _build_skills_section(skill_tools)
    if skills_section:
        system_prompt = system_prompt.rstrip() + "\n" + skills_section

    return _build_agent_graph(
        config=config,
        tools=all_tools,
        system_prompt=system_prompt,
        required_action_tools=entry.get("required_action_tools"),
        sequential_tools=entry.get("sequential_tools", False),
    )
