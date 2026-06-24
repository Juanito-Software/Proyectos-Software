"""
Tool: control de pantalla, ratón y teclado.
El agente puede ver la pantalla (screenshot) y actuar sobre ella (click, type, keys).
Requiere: pip install pyautogui pillow
"""
from pathlib import Path
from datetime import datetime
from langchain_core.tools import tool
from config import CONFIG


def _require_pyautogui():
    """Importa pyautogui o lanza un mensaje de error claro."""
    try:
        import pyautogui
        pyautogui.FAILSAFE = CONFIG.screen.failsafe
        pyautogui.PAUSE = CONFIG.screen.action_pause
        return pyautogui
    except ImportError:
        return None


# ── Visión ──────────────────────────────────────────────────────────────────

@tool
def take_screenshot(save_path: str = "") -> str:
    """
    Captura la pantalla completa y guarda la imagen.
    Si save_path está vacío, genera un nombre con timestamp en la carpeta screenshots/.
    Devuelve la ruta del archivo guardado y la resolución.
    """
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado. Ejecuta: pip install pyautogui pillow"
    try:
        screenshot_dir = Path(CONFIG.screen.screenshot_dir)
        screenshot_dir.mkdir(exist_ok=True)
        filename = Path(save_path).name if save_path else ""
        if not filename or not Path(filename).suffix:
            # save_path vacío o es un directorio ('screenshots/') sin nombre → auto-nombre
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = screenshot_dir / f"screenshot_{ts}.png"
        else:
            # Always keep screenshots inside the configured directory
            final_path = screenshot_dir / filename
        img = pag.screenshot()
        img.save(final_path)
        w, h = img.size

        # Rotar capturas antiguas para evitar acumulación ilimitada en disco
        limit = CONFIG.screen.max_screenshots
        if limit > 0:
            shots = sorted(screenshot_dir.glob("*.png"), key=lambda p: p.stat().st_mtime)
            for old in shots[:-limit]:
                try:
                    old.unlink()
                except OSError:
                    pass

        return f"OK: Captura guardada en {final_path} ({w}x{h}px)"
    except Exception as e:
        return f"ERROR captura: {e}"


@tool
def get_screen_size() -> str:
    """Devuelve la resolución actual de la pantalla en píxeles."""
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        w, h = pag.size()
        return f"Resolución: {w}x{h} píxeles"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def get_mouse_position() -> str:
    """Devuelve la posición actual del cursor en coordenadas de pantalla."""
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        x, y = pag.position()
        return f"Cursor en ({x}, {y})"
    except Exception as e:
        return f"ERROR: {e}"


# ── Ratón ────────────────────────────────────────────────────────────────────

@tool
def click(x: int, y: int, button: str = "left") -> str:
    """
    Clic del ratón en coordenadas absolutas de pantalla.
    button: 'left' | 'right' | 'middle'
    """
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.click(x, y, button=button)
        return f"OK: Clic {button} en ({x}, {y})"
    except Exception as e:
        return f"ERROR clic: {e}"


@tool
def double_click(x: int, y: int) -> str:
    """Doble clic en coordenadas absolutas de pantalla."""
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.doubleClick(x, y)
        return f"OK: Doble clic en ({x}, {y})"
    except Exception as e:
        return f"ERROR doble clic: {e}"


@tool
def right_click(x: int, y: int) -> str:
    """Clic derecho en coordenadas absolutas — abre menú contextual."""
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.rightClick(x, y)
        return f"OK: Clic derecho en ({x}, {y})"
    except Exception as e:
        return f"ERROR clic derecho: {e}"


@tool
def move_mouse(x: int, y: int) -> str:
    """Mueve el cursor a coordenadas absolutas sin hacer clic."""
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.moveTo(x, y, duration=0.2)
        return f"OK: Cursor movido a ({x}, {y})"
    except Exception as e:
        return f"ERROR movimiento: {e}"


@tool
def drag(x1: int, y1: int, x2: int, y2: int) -> str:
    """
    Arrastra desde (x1, y1) hasta (x2, y2) con botón izquierdo pulsado.
    Útil para seleccionar texto, mover ventanas o usar sliders.
    """
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.moveTo(x1, y1, duration=0.1)
        pag.dragTo(x2, y2, duration=0.4, button="left")
        return f"OK: Arrastre de ({x1},{y1}) a ({x2},{y2})"
    except Exception as e:
        return f"ERROR arrastre: {e}"


@tool
def scroll(x: int, y: int, clicks: int) -> str:
    """
    Scroll en la posición (x, y).
    clicks positivo = arriba, negativo = abajo.
    """
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.scroll(clicks, x=x, y=y)
        direction = "arriba" if clicks > 0 else "abajo"
        return f"OK: Scroll {direction} ({abs(clicks)} clics) en ({x}, {y})"
    except Exception as e:
        return f"ERROR scroll: {e}"


# ── Teclado ──────────────────────────────────────────────────────────────────

@tool
def type_text(text: str, interval: float = 0.04) -> str:
    """
    Escribe texto en el foco actual simulando pulsaciones de teclado.
    interval: segundos entre teclas (por defecto 0.04 — natural y fiable).
    No use este tool para contraseñas visibles en pantalla.
    IMPORTANTE: asegúrate de que el campo está enfocado ANTES de llamar a esta función.
    En YouTube, usa press_key('/') para enfocar la barra de búsqueda en lugar de hacer clic.
    """
    import time
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        time.sleep(0.4)  # Pausa para que el foco se estabilice antes del primer carácter
        pag.write(text, interval=interval)
        return f"OK: Texto escrito ({len(text)} caracteres): '{text}'"
    except Exception as e:
        return f"ERROR escritura: {e}"


@tool
def press_key(key: str) -> str:
    """
    Pulsa una tecla simple o combinación.
    Teclas simples: 'enter', 'escape', 'tab', 'space', 'backspace', 'delete',
                    'up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown',
                    'f1'..'f12', 'win', 'printscreen'.
    Combinaciones (separar con '+'): 'ctrl+c', 'ctrl+v', 'alt+f4', 'ctrl+shift+esc',
                                      'ctrl+alt+del', 'win+d'.
    """
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        keys = [k.strip().lower() for k in key.split("+")]
        if len(keys) == 1:
            pag.press(keys[0])
        else:
            pag.hotkey(*keys)
        return f"OK: Tecla(s) pulsada(s): {key}"
    except Exception as e:
        return f"ERROR tecla: {e}"


@tool
def copy_to_clipboard(text: str) -> str:
    """Copia texto al portapapeles del sistema."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return f"OK: Texto copiado al portapapeles ({len(text)} caracteres)"
    except ImportError:
        return "ERROR: pyperclip no instalado. Ejecuta: pip install pyperclip"
    except Exception as e:
        return f"ERROR portapapeles: {e}"


@tool
def get_clipboard() -> str:
    """Lee el contenido actual del portapapeles del sistema."""
    try:
        import pyperclip
        content = pyperclip.paste()
        return f"Portapapeles: {content}" if content else "(portapapeles vacío)"
    except ImportError:
        return "ERROR: pyperclip no instalado. Ejecuta: pip install pyperclip"
    except Exception as e:
        return f"ERROR lectura portapapeles: {e}"


@tool
def get_current_url() -> str:
    """
    Lee la URL que Chrome tiene actualmente en la barra de direcciones.
    Usa Ctrl+L para enfocar la barra, Ctrl+C para copiar, luego lee el portapapeles.
    Llama a esta herramienta después de cada navegación para verificar que la página cargó.
    Devuelve la URL real o un error.
    """
    import time
    import pyperclip
    pag = _require_pyautogui()
    if pag is None:
        return "ERROR: pyautogui no instalado"
    try:
        pag.hotkey("ctrl", "l")   # Enfoca la barra y selecciona todo el texto
        time.sleep(0.4)
        pag.hotkey("ctrl", "c")   # Copia la URL seleccionada
        time.sleep(0.3)
        url = pyperclip.paste()
        pag.press("escape")        # Cierra el desplegable sin navegar
        return f"URL actual en Chrome: {url}"
    except ImportError:
        return "ERROR: pyperclip no instalado. Ejecuta: pip install pyperclip"
    except Exception as e:
        return f"ERROR leyendo URL: {e}"


@tool
def list_open_windows() -> str:
    """
    Lista todas las ventanas visibles abiertas en Windows con sus títulos.
    Usar para saber qué aplicaciones están abiertas y confirmar que un programa se lanzó.
    No requiere librerías externas — usa PowerShell.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process | Where-Object { $_.MainWindowTitle -ne '' } "
             "| Select-Object Name, MainWindowTitle "
             "| Format-Table -AutoSize | Out-String"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()
        return output if output else "(no hay ventanas visibles)"
    except Exception as e:
        return f"ERROR listando ventanas: {e}"


@tool
def sleep_seconds(seconds: float) -> str:
    """
    Espera N segundos antes de continuar.
    Usar después de lanzar una aplicación para darle tiempo a abrirse (recomendado: 2-3 segundos).
    """
    import time
    seconds = max(0.1, min(seconds, 30.0))
    time.sleep(seconds)
    return f"OK: Esperados {seconds:.1f} segundos"


SCREEN_TOOLS = [
    get_current_url,
    list_open_windows,
    take_screenshot,
    get_screen_size,
    get_mouse_position,
    click,
    double_click,
    right_click,
    move_mouse,
    drag,
    scroll,
    type_text,
    press_key,
    copy_to_clipboard,
    get_clipboard,
    sleep_seconds,
]
