"""Fase 1 end-to-end: spec -> backend -> PixelPass -> disco, sin GPU.

Todo esto corre contra el backend `mock`. No prueba que SDXL genere buen arte
—eso no lo puede probar una assertion— pero si prueba lo unico que el codigo
puede garantizar: que la cadena no pierde informacion, que el sidecar describe
de verdad lo que se hizo, y que el mismo spec produce los mismos bytes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from drag.backends import available, catalog, get_backend  # noqa: E402
from drag.palette import Palette  # noqa: E402
from drag.pipeline import generate_asset, regenerate_from_sidecar  # noqa: E402
from drag.pixelpass import PixelPassConfig  # noqa: E402
from drag.spec import AssetSpec  # noqa: E402


@pytest.fixture(scope="session")
def palette() -> Palette:
    return Palette.load("dark_requiem_32")


@pytest.fixture
def backend():
    b = get_backend("mock")
    b.load()
    return b


@pytest.fixture
def spec() -> AssetSpec:
    return AssetSpec(
        kind="character", subject="dark medieval knight", seed=1337, variants=2, backend="mock"
    )


# ------------------------------------------------------------- registro

def test_los_tres_backends_estan_registrados():
    assert set(available()) == {"mock", "sdxl-pixelart", "flux2-klein-pixel"}


def test_el_catalogo_no_importa_torch():
    """Listar backends debe funcionar en una maquina sin CUDA ni torch.
    Si un backend importara torch a nivel de modulo, esto reventaria."""
    assert "torch" not in sys.modules
    infos = catalog()
    assert any(not implemented for _, implemented in infos), "falta el candidato descartado"
    assert "torch" not in sys.modules


def test_el_candidato_con_licencia_dudosa_sigue_declarado():
    pendientes = {i.key: i for i, impl in catalog() if not impl}
    assert "sdxl-pokemon-trainer" in pendientes
    assert pendientes["sdxl-pokemon-trainer"].commercial_ok is None


def test_backend_no_cargado_falla_claro():
    from drag.backends.sdxl import SDXLPixelArtBackend

    with pytest.raises(RuntimeError, match="no cargado"):
        SDXLPixelArtBackend().generate("x", "y", 1)


# ---------------------------------------------------------------- mock

def test_mock_es_determinista(backend):
    a = np.array(backend.generate("p", "n", 42))
    b = np.array(backend.generate("p", "n", 42))
    assert np.array_equal(a, b)


def test_mock_cambia_con_la_seed(backend):
    a = np.array(backend.generate("p", "n", 1))
    b = np.array(backend.generate("p", "n", 2))
    assert not np.array_equal(a, b)


def test_mock_simula_el_problema(backend, palette):
    """Si el mock produjera imagenes limpias, las pruebas del PixelPass
    pasarian sin demostrar nada."""
    from drag.metrics import measure

    m = measure(backend.generate("p", "n", 7).convert("RGBA"), palette)
    assert m.unique_colors > 5000
    assert m.offpalette_pct > 50


# ------------------------------------------------------------ identidad

def test_las_variantes_no_cambian_la_identidad_del_asset():
    """Pedir 6 variantes en vez de 4 no convierte al caballero en otro
    caballero: el slug y la carpeta deben ser los mismos."""
    a = AssetSpec(kind="enemy", subject="skeleton", variants=4)
    b = AssetSpec(kind="enemy", subject="skeleton", variants=6)
    assert a.fingerprint == b.fingerprint
    assert a.slug == b.slug


def test_el_backend_si_cambia_la_identidad():
    a = AssetSpec(kind="enemy", subject="skeleton", backend="mock")
    b = AssetSpec(kind="enemy", subject="skeleton", backend="sdxl-pixelart")
    assert a.fingerprint != b.fingerprint


# ------------------------------------------------------------- pipeline

def test_genera_todos_los_artefactos(tmp_path, spec, backend, palette):
    out = generate_asset(spec, backend, palette, tmp_path, keep_raw=True)
    assert len(out) == 2
    for v in out:
        assert v.sprite_path.exists() and v.sidecar_path.exists()
        assert v.raw_path is not None and v.raw_path.exists()
        assert v.preview_path is not None and v.preview_path.exists()
        assert Image.open(v.sprite_path).size == (32, 32)
        assert Image.open(v.raw_path).size == (1024, 1024)


def test_no_raw_no_escribe_raw(tmp_path, spec, backend, palette):
    out = generate_asset(spec, backend, palette, tmp_path, keep_raw=False)
    assert all(v.raw_path is None for v in out)
    assert not (tmp_path / spec.slug / "raw").exists()


def test_las_variantes_son_distintas_entre_si(tmp_path, spec, backend, palette):
    out = generate_asset(spec, backend, palette, tmp_path)
    a = np.array(Image.open(out[0].raw_path))
    b = np.array(Image.open(out[1].raw_path))
    assert not np.array_equal(a, b), "dos variantes con la misma imagen: seeds mal derivadas"


def test_dos_ejecuciones_dan_bytes_identicos(tmp_path, spec, backend, palette):
    """La promesa central del proyecto. Si esto falla, el sidecar miente."""
    a = generate_asset(spec, backend, palette, tmp_path / "a")
    b = generate_asset(spec, backend, palette, tmp_path / "b")
    for va, vb in zip(a, b):
        assert va.sprite_path.read_bytes() == vb.sprite_path.read_bytes()


def test_rejilla_incoherente_se_rechaza(tmp_path, spec, backend, palette):
    with pytest.raises(ValueError, match="no coincide"):
        generate_asset(spec, backend, palette, tmp_path, cfg=PixelPassConfig(grid=64))


# -------------------------------------------------------------- sidecar

def test_el_sidecar_describe_lo_que_se_hizo(tmp_path, spec, backend, palette):
    out = generate_asset(spec, backend, palette, tmp_path)
    data = json.loads(out[0].sidecar_path.read_text(encoding="utf-8"))

    assert data["seed"] == spec.seed_for(0)
    assert data["spec"]["subject"] == spec.subject
    assert data["backend"]["key"] == "mock"
    assert data["pixelpass"]["grid"] == 32
    assert data["palette"]["size"] == 32
    assert "pixel art sprite" in data["prompt"]
    assert "anti-aliased" in data["negative"]
    # El PixelPass tiene que haber hecho su trabajo, y el sidecar demostrarlo.
    assert data["metrics_raw"]["unique_colors"] > data["metrics_final"]["unique_colors"] * 100
    assert data["metrics_final"]["offpalette_pct"] == 0.0
    assert data["metrics_final"]["soft_alpha_pct"] == 0.0


def test_el_sidecar_marca_si_el_negativo_sirve(tmp_path, spec, backend, palette):
    """klein ignora los negativos por estar destilado de guidance. Que el
    sidecar lo diga evita concluir que 'los negativos no funcionan' cuando lo
    que pasa es que ese backend no los mira."""
    out = generate_asset(spec, backend, palette, tmp_path)
    data = json.loads(out[0].sidecar_path.read_text(encoding="utf-8"))
    assert data["negative_efectivo"] is True

    from drag.backends.flux_klein import FluxKleinPixelBackend

    assert FluxKleinPixelBackend().info.key == "flux2-klein-pixel"


def test_regenerar_desde_sidecar_da_el_mismo_pixel(tmp_path, spec, backend, palette):
    out = generate_asset(spec, backend, palette, tmp_path)
    original = np.array(Image.open(out[1].sprite_path))
    rehecho = np.array(regenerate_from_sidecar(out[1].sidecar_path, backend, palette))
    assert np.array_equal(original, rehecho)
