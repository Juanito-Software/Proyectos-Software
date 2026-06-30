"""
Skill: compresión y extracción de archivos — patrón de Hermes (file utilities).
Operaciones ZIP con stdlib Python, sin dependencias externas.
"""
import os
import zipfile
from pathlib import Path
from langchain_core.tools import tool


def _resolve(path: str) -> Path:
    """Expande ~ y variables de entorno (%USERPROFILE%, $HOME, etc.)."""
    return Path(os.path.expandvars(os.path.expanduser(path)))

SKILL_METADATA = {
    "agents": ["coder"],
    "description": "Comprime carpetas/archivos en ZIP y extrae archivos ZIP",
}


@tool
def compress_to_zip(source_path: str, output_zip: str = "") -> str:
    """
    Comprime un archivo o carpeta en un ZIP.
    source_path: ruta al archivo o carpeta a comprimir.
    output_zip:  ruta del ZIP resultante. Si se omite, crea <source_path>.zip en el mismo directorio.
    """
    src = _resolve(source_path)
    if not src.exists():
        return (
            f"ERROR: '{source_path}' no existe (resuelto como '{src}'). "
            "Usa ~ para el home del usuario, p.ej. '~/Desktop/carpeta'. "
            "Evita <username> literal — usa ~ en su lugar."
        )

    dest = _resolve(output_zip) if output_zip else src.with_suffix(".zip")

    try:
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            if src.is_file():
                zf.write(src, src.name)
                n_files = 1
            else:
                n_files = 0
                for f in src.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(src.parent))
                        n_files += 1
        size_kb = dest.stat().st_size // 1024
        return f"OK: {n_files} archivo(s) comprimido(s) en '{dest}' ({size_kb} KB)"
    except Exception as e:
        return f"ERROR compress_to_zip: {e}"


@tool
def extract_archive(zip_path: str, output_dir: str = "") -> str:
    """
    Extrae un archivo ZIP en el directorio indicado.
    zip_path:   ruta al archivo .zip.
    output_dir: carpeta destino. Si se omite, extrae junto al ZIP.
    """
    zp = _resolve(zip_path)
    if not zp.exists():
        return (
            f"ERROR: '{zip_path}' no existe (resuelto como '{zp}'). "
            "Usa ~ para el home del usuario, p.ej. '~/Desktop/archivo.zip'."
        )
    if not zipfile.is_zipfile(zp):
        return f"ERROR: '{zip_path}' no es un archivo ZIP válido."

    dest = _resolve(output_dir) if output_dir else zp.parent / zp.stem
    dest.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zp, "r") as zf:
            zf.extractall(dest)
            n_files = len(zf.namelist())
        return f"OK: {n_files} archivo(s) extraído(s) en '{dest}'"
    except Exception as e:
        return f"ERROR extract_archive: {e}"