"""Verificacion de la fase 0. Ejecutar: PYTHONPATH=src python -m pytest -q

Lo que se comprueba no es "el codigo corre", es que el PixelPass cumple las
tres garantias que Unity necesita: tamano exacto, paleta cerrada y alpha dura.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from drag.metrics import measure  # noqa: E402
from drag.palette import Palette, extract_palette  # noqa: E402
from drag.pixelpass import PixelPassConfig, detect_pixel_scale, run_pixelpass  # noqa: E402
from drag.prompts import build_prompt  # noqa: E402
from drag.spec import AssetSpec  # noqa: E402

import make_fixtures  # noqa: E402


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("fixtures")
    make_fixtures.knight(d / "raw_knight.png")
    make_fixtures.potion(d / "raw_potion.png")
    make_fixtures.blocky_sprite(d / "raw_blocky.png", block=16)
    return d


@pytest.fixture(scope="session")
def palette() -> Palette:
    return Palette.load("dark_requiem_32")


# ------------------------------------------------------------------ spec

def test_spec_es_reproducible():
    a = AssetSpec(kind="enemy", subject="skeleton knight", seed=42)
    b = AssetSpec(kind="enemy", subject="skeleton knight", seed=42)
    assert a.fingerprint == b.fingerprint
    assert a.seed_for(0) == b.seed_for(0)
    assert a.seed_for(0) != a.seed_for(1)


def test_spec_sin_seed_sigue_siendo_determinista():
    a = AssetSpec(kind="item", subject="health potion")
    assert a.seed_for(2) == AssetSpec(kind="item", subject="health potion").seed_for(2)


def test_spec_roundtrip_json(tmp_path):
    a = AssetSpec(kind="tile", subject="cracked stone floor", tags=("mossy",))
    p = tmp_path / "s.json"
    a.to_json(p)
    assert AssetSpec.from_json(p) == a


def test_spec_rechaza_basura():
    with pytest.raises(ValueError):
        AssetSpec(kind="item", subject="   ")
    with pytest.raises(ValueError):
        AssetSpec(kind="item", subject="x", grid=4)


# --------------------------------------------------------------- prompts

def test_prompt_incluye_negativos_criticos():
    pos, neg = build_prompt(AssetSpec(kind="character", subject="dark knight", grid=32))
    assert "32x32" in pos
    for veneno in ("anti-aliased", "smooth gradient", "3d render", "drop shadow"):
        assert veneno in neg


def test_prompt_de_tile_prohibe_sujeto_central():
    _, neg = build_prompt(AssetSpec(kind="tile", subject="stone floor"))
    assert "object in center" in neg


# --------------------------------------------------------------- paleta

def test_paleta_carga_32_colores(palette):
    assert len(palette) == 32
    assert palette.colors.dtype == np.uint8


def test_mapeo_es_idempotente(palette):
    """Cuantizar dos veces no debe mover ningun pixel. Si moviera, el
    benchmark mediria ruido del propio pipeline en vez del modelo."""
    rng = np.random.default_rng(3)
    px = rng.integers(0, 256, size=(500, 3), dtype=np.uint8)
    once = palette.map_rgb(px)
    twice = palette.map_rgb(once)
    assert np.array_equal(once, twice)


def test_extraccion_devuelve_colores_reales():
    rng = np.random.default_rng(5)
    base = np.array([[10, 12, 20], [200, 40, 50], [30, 120, 60]], dtype=np.uint8)
    px = base[rng.integers(0, 3, size=4000)]
    pal = extract_palette(px, n_colors=3, name="t")
    assert len(pal) == 3
    for c in pal.colors:
        assert (base == c).all(axis=1).any(), "invento un color que no estaba"


# ------------------------------------------------------------- pixelpass

def test_detecta_rejilla_real(fixtures):
    arr = np.array(Image.open(fixtures / "raw_blocky.png").convert("RGB"))
    assert detect_pixel_scale(arr) == 16


@pytest.mark.parametrize("name", ["raw_knight", "raw_potion", "raw_blocky"])
@pytest.mark.parametrize("grid", [16, 32, 64])
def test_salida_es_exactamente_la_rejilla(fixtures, palette, name, grid):
    res = run_pixelpass(fixtures / f"{name}.png", palette, PixelPassConfig(grid=grid))
    assert res.image.size == (grid, grid)


def test_alpha_es_binaria(fixtures, palette):
    res = run_pixelpass(fixtures / "raw_knight.png", palette, PixelPassConfig(grid=32))
    a = np.array(res.image)[..., 3]
    assert set(np.unique(a)).issubset({0, 255}), "hay alpha intermedia -> flecos en Unity"


def test_todos_los_colores_estan_en_paleta(fixtures, palette):
    res = run_pixelpass(fixtures / "raw_potion.png", palette, PixelPassConfig(grid=32))
    arr = np.array(res.image)
    op = arr[..., :3][arr[..., 3] > 0]
    legal = {tuple(c) for c in palette.colors}
    assert {tuple(c) for c in op}.issubset(legal)


def test_colapsa_el_numero_de_colores(fixtures, palette):
    res = run_pixelpass(fixtures / "raw_knight.png", palette, PixelPassConfig(grid=32))
    assert res.colors_before > 1000, "la fixture no simula una salida de difusor"
    assert res.colors_after <= 16, "quedan demasiados colores para un sprite de 32px"


def test_fondo_solido_desaparece(fixtures, palette):
    res = run_pixelpass(fixtures / "raw_knight.png", palette, PixelPassConfig(grid=32))
    a = np.array(res.image)[..., 3]
    assert a[0, 0] == 0 and a[0, -1] == 0, "el fondo sigue opaco"
    assert (a > 0).mean() > 0.05, "se ha comido el sujeto entero"


def test_el_sujeto_ocupa_el_canvas(fixtures, palette):
    """Sin encuadre, un sprite con mucho aire pierde resolucion util."""
    res = run_pixelpass(fixtures / "raw_potion.png", palette, PixelPassConfig(grid=32))
    a = np.array(res.image)[..., 3]
    ys, xs = np.nonzero(a)
    alto = (ys.max() - ys.min() + 1) / 32
    assert alto > 0.7, f"el sujeto solo ocupa {alto:.0%} de la altura"


def test_es_determinista(fixtures, palette):
    cfg = PixelPassConfig(grid=32)
    a = np.array(run_pixelpass(fixtures / "raw_knight.png", palette, cfg).image)
    b = np.array(run_pixelpass(fixtures / "raw_knight.png", palette, cfg).image)
    assert np.array_equal(a, b)


# --------------------------------------------------------------- metricas

def test_metricas_separan_crudo_de_procesado(fixtures, palette, tmp_path):
    crudo = measure(fixtures / "raw_knight.png", palette)
    res = run_pixelpass(fixtures / "raw_knight.png", palette, PixelPassConfig(grid=32))
    dst = tmp_path / "clean.png"
    res.image.save(dst)
    limpio = measure(dst, palette)

    assert crudo.unique_colors > limpio.unique_colors * 100
    assert crudo.offpalette_pct > 50.0
    assert limpio.offpalette_pct == 0.0
    assert crudo.orphan_color_pct > 20.0, "la fixture deberia tener ruido de degradado"
    assert limpio.orphan_color_pct < 5.0


# ------------------------------------------------- fondo: casos que fallaron

def _escena(bg, sujeto, size=256):
    """Fondo solido + rectangulo central. Deliberadamente minimo: estas
    pruebas son de logica de flood fill, no de estetica."""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, :] = bg
    q = size // 4
    arr[q : size - q, q : size - q] = sujeto
    return Image.fromarray(arr, mode="RGB")


def test_bg_key_conserva_al_sujeto(palette):
    """Regresion. Con el fondo adivinado por la mediana del borde, un sujeto
    con tonos cercanos al fondo se comia medio sprite. Fijando la clave
    magenta —que es la que el propio prompt pide— eso no puede pasar."""
    img = _escena(bg=(255, 0, 255), sujeto=(120, 118, 130))
    res = run_pixelpass(img, palette, PixelPassConfig(grid=32, bg_key="#FF00FF"))
    a = np.array(res.image)[..., 3]
    # El techo no es 100%: trim_and_frame anade un 6% de margen por lado, asi
    # que un sujeto cuadrado que llena su recorte ocupa ~(1/1.12)^2 = 80% del
    # canvas. Por debajo de 0,7 si habria mordido al sujeto.
    assert (a > 0).mean() > 0.7, "la clave magenta se comio al sujeto"


def test_clave_equivocada_reintenta_adivinando(palette):
    """Si el modelo ignora la instruccion de fondo magenta y devuelve gris, la
    clave no encuentra nada. Debe reintentar por el borde, no entregar un
    sprite con el fondo pegado."""
    img = _escena(bg=(120, 118, 130), sujeto=(200, 40, 50))
    res = run_pixelpass(img, palette, PixelPassConfig(grid=32, bg_key="#FF00FF"))
    a = np.array(res.image)[..., 3]
    assert a[0, 0] == 0, "el fondo gris sobrevivio a la clave magenta"
    assert (a > 0).mean() > 0.5


def test_tolerancia_absurda_no_borra_el_sprite(palette):
    """Con una tolerancia disparatada el flood fill se lo lleva todo. Preferimos
    reintentar con la mitad antes que devolver un PNG vacio: un fondo pegado se
    ve y se corrige, un sprite desaparecido se descubre tres carpetas despues."""
    from drag.pixelpass import remove_background

    arr = np.dstack(
        [np.array(_escena(bg=(255, 0, 255), sujeto=(200, 40, 50))),
         np.full((256, 256), 255, dtype=np.uint8)]
    )
    out = remove_background(arr, tolerance=0.9)
    assert (out[..., 3] > 0).mean() > 0.02, "se borro la imagen entera"


def test_hueco_interior_del_color_del_fondo_sobrevive(palette):
    """El ojo de una calavera es del color del fondo pero no toca el borde.
    Un `remove color` global se lo cargaria; el flood fill no debe."""
    from drag.pixelpass import remove_background

    arr = np.array(_escena(bg=(255, 0, 255), sujeto=(200, 40, 50)))
    arr[120:136, 120:136] = (255, 0, 255)   # hueco magenta interior
    rgba = np.dstack([arr, np.full((256, 256), 255, dtype=np.uint8)])
    out = remove_background(rgba, tolerance=0.10, ref_rgb=(255, 0, 255))
    assert out[128, 128, 3] == 255, "borro un hueco interior no conectado al borde"
    assert out[0, 0, 3] == 0
