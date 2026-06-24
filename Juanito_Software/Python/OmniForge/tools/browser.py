"""
Tool: automatización web vía Browser Use.
El agente llama estas tools estructuradamente — no invoca Browser Use directamente.
"""
import asyncio
from langchain_core.tools import tool
from config import CONFIG


def _run_async(coro):
    """
    Ejecuta una coroutine desde contexto síncrono.
    Usa get_running_loop() como predicado — no crea loops silenciosos (deprecado en 3.10+).
    """
    try:
        asyncio.get_running_loop()
        # Loop activo (FastAPI, Jupyter…) — thread propio con loop aislado
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    except RuntimeError:
        # Sin loop activo — crear y cerrar limpiamente
        return asyncio.run(coro)


async def _browser_task(task: str, url: str = None) -> str:
    """Núcleo async de Browser Use."""
    from browser_use import Agent as BrowserAgent
    from core.llm import build_llm

    llm = build_llm(CONFIG)

    agent = BrowserAgent(
        task=task if not url else f"Go to {url} and {task}",
        llm=llm,
        headless=CONFIG.tools.browser_headless,
    )
    result = await agent.run()
    return str(result)


@tool
def browse_url(url: str, task: str) -> str:
    """
    Navega a una URL y ejecuta una tarea sobre la página.
    task: descripción en lenguaje natural de lo que hacer (ej: 'extrae todos los títulos h1').
    """
    try:
        return _run_async(_browser_task(task=task, url=url))
    except ImportError:
        return "ERROR: browser_use no instalado. Ejecuta: pip install browser-use"
    except Exception as e:
        return f"ERROR browser: {e}"


@tool
def web_search(query: str) -> str:
    """
    Realiza una búsqueda web y devuelve los resultados principales.
    Usa el navegador — no requiere API key de búsqueda.
    """
    try:
        task = f"Search for '{query}' and return the top 5 results with title and URL"
        return _run_async(_browser_task(task=task, url="https://www.google.com"))
    except ImportError:
        return "ERROR: browser_use no instalado. Ejecuta: pip install browser-use"
    except Exception as e:
        return f"ERROR búsqueda: {e}"


@tool
def extract_page_content(url: str) -> str:
    """
    Extrae el contenido textual de una página web.
    Útil para scraping y análisis de contenido.
    """
    try:
        task = "Extract all the main text content from this page, structured by sections"
        return _run_async(_browser_task(task=task, url=url))
    except ImportError:
        return "ERROR: browser_use no instalado. Ejecuta: pip install browser-use"
    except Exception as e:
        return f"ERROR extracción: {e}"


BROWSER_TOOLS = [browse_url, web_search, extract_page_content]
