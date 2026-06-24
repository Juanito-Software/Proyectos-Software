"""
Tool: ejecución de código y terminal vía Open Interpreter.
Open Interpreter gestiona el contexto de ejecución y la salida.
"""
from langchain_core.tools import tool
from config import CONFIG


@tool
def run_code(code: str, language: str = "python") -> str:
    """
    Ejecuta un bloque de código usando Open Interpreter.
    language: python | shell | javascript | r
    Devuelve stdout + stderr combinados.
    """
    try:
        from interpreter import interpreter as oi

        oi.llm.model = "none"       # OI no llama a ningún LLM — solo ejecuta
        oi.auto_run = True
        oi.verbose = False
        oi.max_output = 8000

        # Open Interpreter espera un mensaje de chat natural,
        # lo envolvemos con instrucción directa para ejecución limpia
        prompt = f"Run this {language} code and return only the output:\n```{language}\n{code}\n```"
        output_chunks = []

        for chunk in oi.chat(prompt, stream=True, display=False):
            if isinstance(chunk, dict) and chunk.get("type") == "console":
                content = chunk.get("content", "")
                if content:
                    output_chunks.append(str(content))

        result = "".join(output_chunks).strip()
        return result if result else "(sin salida)"

    except ImportError:
        # Fallback a subprocess si Open Interpreter no está instalado
        return _subprocess_fallback(code, language)
    except Exception as e:
        return f"ERROR ejecución: {e}"


@tool
def run_command(command: str) -> str:
    """
    Ejecuta un comando de shell con timeout.
    Preferir run_code con language='shell' para scripts largos.
    """
    return _subprocess_fallback(command, "shell")


def _subprocess_fallback(code: str, language: str) -> str:
    """Ejecución directa sin Open Interpreter — solo para shell."""
    import subprocess
    import sys
    import os

    timeout = CONFIG.tools.terminal_timeout

    if language == "shell":
        cmd = code
        shell = True
    elif language == "python":
        cmd = [sys.executable, "-c", code]
        shell = False
    else:
        return f"ERROR: language '{language}' no soportado sin Open Interpreter"

    # Asegurar que Tesseract esté en el PATH del subproceso.
    # Deriva el directorio desde CONFIG para no hardcodear la ruta.
    env = os.environ.copy()
    tess_cmd = CONFIG.vision.tesseract_cmd
    if tess_cmd:
        tess_dir = str(os.path.dirname(tess_cmd))
        env["TESSERACT_CMD"] = tess_cmd
    else:
        tess_dir = r"C:\Program Files\Tesseract-OCR"  # fallback instalación estándar
    if tess_dir and tess_dir not in env.get("PATH", ""):
        env["PATH"] = tess_dir + os.pathsep + env.get("PATH", "")

    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output.strip() if output.strip() else "(sin salida)"
    except subprocess.TimeoutExpired:
        return f"ERROR: Comando expiró después de {timeout}s"
    except Exception as e:
        return f"ERROR: {e}"


TERMINAL_TOOLS = [run_code, run_command]
