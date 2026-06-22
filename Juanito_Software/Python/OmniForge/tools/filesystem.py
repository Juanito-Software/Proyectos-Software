"""
Tool: sistema de archivos.
Operaciones atómicas — read, write, list, delete.
"""
import os
from pathlib import Path
from langchain_core.tools import tool


@tool
def read_file(path: str) -> str:
    """Lee el contenido de un archivo y lo devuelve como string."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"ERROR: Archivo no encontrado: {path}"
    except PermissionError:
        return f"ERROR: Sin permisos para leer: {path}"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Escribe content en path. Crea directorios intermedios si es necesario."""
    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"OK: Archivo escrito en {path} ({len(content)} caracteres)"
    except PermissionError:
        return f"ERROR: Sin permisos para escribir: {path}"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def list_dir(path: str = ".") -> str:
    """Lista el contenido de un directorio. Devuelve nombres y tipos."""
    try:
        entries = []
        for entry in sorted(Path(path).iterdir()):
            kind = "DIR " if entry.is_dir() else "FILE"
            entries.append(f"{kind}  {entry.name}")
        return "\n".join(entries) if entries else "(directorio vacío)"
    except FileNotFoundError:
        return f"ERROR: Directorio no encontrado: {path}"
    except PermissionError:
        return f"ERROR: Sin permisos para listar: {path}"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def delete_file(path: str) -> str:
    """Elimina un archivo. No elimina directorios."""
    try:
        target = Path(path)
        if target.is_dir():
            return f"ERROR: {path} es un directorio. Usa herramientas de sistema para eliminar directorios."
        target.unlink()
        return f"OK: Archivo eliminado: {path}"
    except FileNotFoundError:
        return f"ERROR: Archivo no encontrado: {path}"
    except Exception as e:
        return f"ERROR: {e}"


FILESYSTEM_TOOLS = [read_file, write_file, list_dir, delete_file]
