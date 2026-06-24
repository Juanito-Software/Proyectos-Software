"""
Skill: HTTP fetch ligero — patrón de Hermes (herramienta de datos sin browser completo).
Para consultas de APIs REST, JSON endpoints, o páginas simples sin JavaScript.
Más rápido que browse_url: sin Playwright, sin headless Chrome.
"""
import json
import urllib.request
import urllib.error
from langchain_core.tools import tool

SKILL_METADATA = {
    "agents": ["researcher", "coder"],
    "description": "HTTP GET ligero sin navegador (ideal para APIs y JSON endpoints)",
}

_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OmniForge/1.0",
    "Accept": "application/json, text/plain, */*",
}
_MAX_BYTES = 32_000


@tool
def fetch_url(url: str, timeout: int = 10, as_json: bool = False) -> str:
    """
    Descarga el contenido de una URL vía HTTP GET sin abrir el navegador.
    Ideal para APIs REST, datos JSON o páginas HTML simples (sin JavaScript).
    url:     URL completa incluyendo https://.
    timeout: segundos máximo de espera (default: 10).
    as_json: si True, formatea la respuesta JSON con indentación.
    """
    try:
        req = urllib.request.Request(url, headers=_DEFAULT_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(_MAX_BYTES)
            content_type = resp.headers.get("Content-Type", "")
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()
            text = raw.decode(charset, errors="replace")

            if as_json or "application/json" in content_type:
                try:
                    parsed = json.loads(text)
                    text = json.dumps(parsed, ensure_ascii=False, indent=2)[:_MAX_BYTES]
                except json.JSONDecodeError:
                    pass

            status = resp.status
            truncated = len(raw) >= _MAX_BYTES
            note = " [truncado]" if truncated else ""
            return f"HTTP {status}{note}\n{text}"
    except urllib.error.HTTPError as e:
        return f"ERROR HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"ERROR URL: {e.reason}"
    except Exception as e:
        return f"ERROR fetch_url: {e}"