"""Fixture global: añade la raíz del proyecto al sys.path para poder importar
config, core.* y tools.* desde tests/."""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _verboso_desactivado(monkeypatch):
    """Evita que los prints de main.py/planner reventen con cp1252 en CI."""
    from config import CONFIG
    monkeypatch.setattr(CONFIG.agent, "verbose", False)