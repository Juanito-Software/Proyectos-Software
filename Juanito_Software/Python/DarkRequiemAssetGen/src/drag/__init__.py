"""Dark Requiem Asset Generator.

Pipeline: AssetSpec -> PromptBuilder -> Backend -> PixelPass -> Packager.
Fase 0 (esto) cubre spec, prompts, paleta, PixelPass y metricas: todo lo que
funciona sin GPU y sin modelo.
"""

from .spec import AssetSpec
from .palette import Palette, extract_palette
from .pixelpass import PixelPassConfig, run_pixelpass, detect_pixel_scale
from .metrics import measure, write_csv
from .prompts import build_prompt
from .pipeline import generate_asset, regenerate_from_sidecar
from .backends import available, catalog, get_backend
from .env import probe
from .bench import load_matrix, run_benchmark, summarize
from .packager import Frame, Sheet, export_for_unity, pack_sprites, unity_meta

__version__ = "0.3.4"

__all__ = [
    "AssetSpec",
    "Palette",
    "extract_palette",
    "PixelPassConfig",
    "run_pixelpass",
    "detect_pixel_scale",
    "measure",
    "write_csv",
    "build_prompt",
    "generate_asset",
    "regenerate_from_sidecar",
    "available",
    "catalog",
    "get_backend",
    "probe",
    "load_matrix",
    "run_benchmark",
    "summarize",
    "Frame",
    "Sheet",
    "pack_sprites",
    "unity_meta",
    "export_for_unity",
]
