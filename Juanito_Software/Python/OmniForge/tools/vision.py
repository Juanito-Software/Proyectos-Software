"""
tools/vision.py — Módulo de visión por computador.

Dos capas independientes:
  OCR  (pytesseract + OpenCV): extrae texto y coordenadas sin API ni coste.
  LLM  (Ollama/Anthropic/OpenAI): comprensión visual avanzada con modelo multimodal.

Instalación mínima (OCR):
  pip install pytesseract pillow opencv-python
  + Tesseract binario: https://github.com/UB-Mannheim/tesseract/wiki  (Windows)

Instalación para Vision LLM local (Ollama):
  ollama pull llava        ← o moondream, llava-phi3, etc.
  CONFIG.vision.engine = "ollama"

Instalación para Vision LLM en la nube:
  CONFIG.vision.engine = "anthropic"  y  ANTHROPIC_API_KEY en .env
  CONFIG.vision.engine = "openai"     y  OPENAI_API_KEY en .env
"""
from __future__ import annotations

import base64
import shutil
import time
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool
from config import CONFIG


# ── Helpers internos ─────────────────────────────────────────────────────────

def _take_and_save() -> str:
    """Toma una captura y la guarda en screenshots/. Devuelve la ruta."""
    try:
        import pyautogui
        pyautogui.FAILSAFE = CONFIG.screen.failsafe
        pyautogui.PAUSE = CONFIG.screen.action_pause
    except ImportError:
        raise RuntimeError("pyautogui no instalado: pip install pyautogui pillow")

    screenshot_dir = Path(CONFIG.screen.screenshot_dir)
    screenshot_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = screenshot_dir / f"vision_{ts}.png"
    img = pyautogui.screenshot()
    img.save(path)

    limit = CONFIG.screen.max_screenshots
    if limit > 0:
        shots = sorted(screenshot_dir.glob("vision_*.png"), key=lambda p: p.stat().st_mtime)
        for old in shots[:-limit]:
            try:
                old.unlink()
            except OSError:
                pass

    return str(path)


def _encode_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _resolve_tesseract_cmd() -> str | None:
    """
    Localiza el ejecutable de Tesseract en este orden:
      1. CONFIG.vision.tesseract_cmd  (ruta explícita del usuario)
      2. shutil.which("tesseract")    (si está en el PATH del sistema)
      3. Rutas habituales de instalación en Windows
    Devuelve la ruta encontrada o None si no se localiza.
    """
    # 1. Ruta explícita configurada por el usuario
    explicit = CONFIG.vision.tesseract_cmd
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return str(p)

    # 2. En el PATH del sistema
    found = shutil.which("tesseract")
    if found:
        return found

    # 3. Rutas habituales de Windows
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
            __import__("os").environ.get("USERNAME", "")
        ),
    ]
    for c in candidates:
        if Path(c).is_file():
            return c

    return None


def _ocr_data(path: str) -> dict | None:
    """Ejecuta Tesseract sobre la imagen y devuelve el dict con texto + bounding boxes."""
    tess_cmd = _resolve_tesseract_cmd()
    if tess_cmd is None:
        return None

    try:
        from PIL import Image
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tess_cmd
        img = Image.open(path)
        return pytesseract.image_to_data(
            img,
            output_type=pytesseract.Output.DICT,
            lang="spa+eng",
        )
    except ImportError:
        return None
    except Exception:
        # Intentar sin idioma específico (por si faltan los datos de idioma)
        try:
            from PIL import Image
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tess_cmd
            img = Image.open(path)
            return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        except Exception:
            return None


def _call_vision_llm(path: str, prompt: str) -> str:
    """Llama al motor de visión configurado y devuelve la respuesta."""
    engine = CONFIG.vision.engine.lower()
    b64 = _encode_b64(path)
    api_key = CONFIG.vision.api_key or CONFIG.llm.api_key

    if engine == "ollama":
        from langchain_ollama import ChatOllama
        from langchain_core.messages import HumanMessage
        model = ChatOllama(
            model=CONFIG.vision.model,
            base_url=CONFIG.vision.base_url,
            temperature=0.0,
        )
        msg = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ])
        return model.invoke([msg]).content

    if engine == "anthropic":
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        model = ChatAnthropic(
            model=CONFIG.vision.model,
            api_key=api_key,
            temperature=0.0,
            max_tokens=1024,
        )
        msg = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image", "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": b64,
            }},
        ])
        return model.invoke([msg]).content

    if engine == "openai":
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        model = ChatOpenAI(
            model=CONFIG.vision.model,
            api_key=api_key,
            temperature=0.0,
            max_tokens=1024,
        )
        msg = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ])
        return model.invoke([msg]).content

    return (
        f"ERROR: find_element y describe_screen requieren visión LLM "
        f"(ollama/anthropic/openai), pero el motor actual es '{engine}' (solo OCR). "
        "Alternativa inmediata: usa find_text_on_screen() para localizar texto visible, "
        "o press_key('ctrl+l') para enfocar la barra de direcciones de Chrome."
    )


# ── Capa OCR (sin API, sin red) ───────────────────────────────────────────────

@tool
def read_screen_text() -> str:
    """
    Extrae todo el texto visible en la pantalla usando OCR (pytesseract).
    No requiere API ni modelo de IA — funciona completamente offline.
    Útil para saber qué texto hay en pantalla y decidir qué hacer a continuación.
    Requiere: pip install pytesseract pillow  +  Tesseract instalado en Windows.
    """
    try:
        path = _take_and_save()
        data = _ocr_data(path)
        if data is None:
            return (
                "ERROR: Tesseract no encontrado. "
                "Comprueba que está instalado en C:\\Program Files\\Tesseract-OCR\\ "
                "o ajusta CONFIG.vision.tesseract_cmd con la ruta correcta."
            )
        words = [
            w for w, conf in zip(data["text"], data["conf"])
            if str(conf).isdigit() and int(conf) > 30 and w.strip()
        ]
        text = " ".join(words)
        return f"Texto detectado en pantalla:\n{text}" if text else "(no se detectó texto legible)"
    except Exception as e:
        return f"ERROR read_screen_text: {e}"


@tool
def find_text_on_screen(text: str) -> str:
    """
    Busca un texto concreto en la pantalla mediante OCR y devuelve las coordenadas (x, y)
    del centro de ese texto para poder hacer click sobre él.
    Ejemplo: find_text_on_screen("Buscar") → "Encontrado en (640, 36) → click(640, 36)"
    No requiere API. Requiere: pip install pytesseract pillow.
    """
    try:
        path = _take_and_save()
        data = _ocr_data(path)
        if data is None:
            return "ERROR: pytesseract no disponible."

        needle = text.lower().strip()

        # Búsqueda en palabras individuales
        for i, word in enumerate(data["text"]):
            conf = data["conf"][i]
            if not (str(conf).isdigit() and int(conf) > 30 and word.strip()):
                continue
            if needle in word.lower():
                cx = data["left"][i] + data["width"][i] // 2
                cy = data["top"][i] + data["height"][i] // 2
                return f"Encontrado '{word.strip()}' en ({cx}, {cy}) → usa click({cx}, {cy})"

        # Búsqueda en frases (ventana deslizante de hasta 6 palabras)
        words_list = data["text"]
        for start in range(len(words_list)):
            for length in range(2, 7):
                end = start + length
                if end > len(words_list):
                    break
                chunk = [words_list[j] for j in range(start, end) if words_list[j].strip()]
                phrase = " ".join(chunk).lower()
                if needle in phrase:
                    # Centro del grupo de palabras
                    indices = [j for j in range(start, end) if words_list[j].strip()]
                    if not indices:
                        continue
                    x0 = data["left"][indices[0]]
                    x1 = data["left"][indices[-1]] + data["width"][indices[-1]]
                    y0 = data["top"][indices[0]]
                    y1 = y0 + data["height"][indices[0]]
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                    return f"Encontrado '{phrase.strip()}' en ({cx}, {cy}) → usa click({cx}, {cy})"

        return f"No encontrado: '{text}' no está visible en pantalla ahora mismo."
    except Exception as e:
        return f"ERROR find_text_on_screen: {e}"


# ── Capa Vision LLM (requiere modelo multimodal) ─────────────────────────────

@tool
def describe_screen(question: str = "") -> str:
    """
    Usa un modelo de visión IA para describir la pantalla actual o responder una pregunta.
    Si 'question' está vacío → descripción general de lo visible.
    Si 'question' tiene contenido → respuesta concreta sobre lo que hay en pantalla.
    Ejemplos:
      describe_screen()
      describe_screen("¿Qué URL muestra Chrome?")
      describe_screen("¿Está YouTube cargado completamente?")
    Requiere: CONFIG.vision.engine = ollama | anthropic | openai  (ver config.py).
    """
    try:
        path = _take_and_save()
        if question:
            prompt = (
                f"Look at this screenshot and answer concisely: {question}\n"
                "Be direct and specific. If you cannot determine the answer, say so."
            )
        else:
            prompt = (
                "Describe what is visible on this screenshot. Include: "
                "the application name, current page or view, any visible URL or title, "
                "key UI elements and text. Be concise and factual."
            )
        return _call_vision_llm(path, prompt)
    except Exception as e:
        return f"ERROR describe_screen: {e}"


@tool
def find_element(description: str) -> str:
    """
    Usa visión IA para localizar un elemento de UI en pantalla y devolver sus coordenadas.
    El modelo analiza la captura y devuelve (x, y) del centro del elemento para hacer click.
    Ejemplos:
      find_element("barra de direcciones de Chrome")
      find_element("botón de búsqueda de YouTube")
      find_element("campo de texto del bloc de notas")
    Requiere: CONFIG.vision.engine = ollama | anthropic | openai  (ver config.py).
    """
    try:
        import pyautogui
        w, h = pyautogui.size()
        path = _take_and_save()
        prompt = (
            f"This screenshot is {w}x{h} pixels. "
            f"Locate this UI element: '{description}'. "
            "Respond with EXACTLY this format on the first line:\n"
            "COORDINATES: (x, y)\n"
            "Then one short sentence describing what you found. "
            "If the element is not visible, respond: NOT FOUND: <reason>"
        )
        return _call_vision_llm(path, prompt)
    except Exception as e:
        return f"ERROR find_element: {e}"


# ── Export ────────────────────────────────────────────────────────────────────

VISION_TOOLS = [
    read_screen_text,
    find_text_on_screen,
    describe_screen,
    find_element,
]
