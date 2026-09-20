"""Fixture global: carga GPTDevTeam_v2.0.py como módulo (el nombre del fichero
contiene un punto, no es importable con `import` normal)."""
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_FICHA = PROJECT_ROOT / "GPTDevTeam_v2.0.py"

_spec = importlib.util.spec_from_file_location("gptdevteam_v2", _FICHA)
_gptdevteam = importlib.util.module_from_spec(_spec)
sys.modules["gptdevteam_v2"] = _gptdevteam
_spec.loader.exec_module(_gptdevteam)

import pytest


@pytest.fixture
def gdt():
    """Acceso al módulo GPTDevTeam v2.0 cargado."""
    return _gptdevteam


@pytest.fixture
def memoria_temporal(gdt, tmp_path, monkeypatch):
    """Redirige MEMORY_FILE a un archivo temporal aislado por test."""
    ruta_memoria = tmp_path / "memory.json"
    monkeypatch.setattr(gdt, "MEMORY_FILE", str(ruta_memoria))
    return ruta_memoria