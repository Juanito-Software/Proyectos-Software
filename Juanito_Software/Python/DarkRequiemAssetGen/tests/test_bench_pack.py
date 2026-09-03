"""Fases 2 y 3: benchmark y empaquetado para Unity.

La prueba que mas me importa de todo este archivo es
`test_el_rect_de_unity_apunta_al_sprite_correcto`: el flip vertical del origen
es el fallo clasico de todo empaquetador casero, y es traicionero porque el
atlas se ve perfecto y solo te enteras dentro de Unity, cuando el frame que
sale es el simetrico del que pediste.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from drag.bench import (  # noqa: E402
    RUBRIC_CRITERIA,
    load_matrix,
    merge_rubric,
    run_benchmark,
    summarize,
    write_rubric_template,
)
from drag.packager import (  # noqa: E402
    Frame,
    export_for_unity,
    pack_sprites,
    unity_meta,
)
from drag.palette import Palette  # noqa: E402

MATRIX = Path(__file__).resolve().parents[1] / "bench" / "matrix.json"


@pytest.fixture(scope="session")
def palette() -> Palette:
    return Palette.load("dark_requiem_32")


@pytest.fixture(scope="session")
def corrida(tmp_path_factory, palette) -> Path:
    """Una corrida pequena de verdad: 2 specs x 2 seeds con el backend mock."""
    specs, seeds, _ = load_matrix(MATRIX)
    out = tmp_path_factory.mktemp("bench")
    run_benchmark(specs[:2], seeds[:2], ["mock"], palette, out, on_log=lambda *_: None)
    return out / "results.csv"


def _sprites(tmp_path, n=5, size=32):
    """Sprites distinguibles: cada uno de un color plano distinto, para poder
    afirmar que el frame k del atlas es el sprite k y no su vecino."""
    paths = []
    for i in range(n):
        arr = np.zeros((size, size, 4), dtype=np.uint8)
        arr[..., 0] = (20 + i * 31) % 256
        arr[..., 1] = (200 - i * 23) % 256
        arr[..., 2] = (60 + i * 17) % 256
        arr[..., 3] = 255
        p = tmp_path / f"s{i}.png"
        Image.fromarray(arr, mode="RGBA").save(p)
        paths.append(p)
    return paths


# ------------------------------------------------------------- matriz

def test_la_matriz_cubre_los_cuatro_kinds():
    specs, seeds, nombre = load_matrix(MATRIX)
    assert len(specs) == 8 and len(seeds) == 4
    assert {s.kind for s in specs} == {"character", "enemy", "item", "tile"}
    assert nombre == "dark_requiem_v1"


def test_la_matriz_no_trae_seeds_aleatorias():
    """Si las seeds cambiaran entre corridas, comparar backends no mediria el
    backend: mediria la loteria."""
    a, sa, _ = load_matrix(MATRIX)
    b, sb, _ = load_matrix(MATRIX)
    assert sa == sb
    assert [s.fingerprint for s in a] == [s.fingerprint for s in b]


# ---------------------------------------------------------- benchmark

def test_la_corrida_produce_una_fila_por_imagen(corrida):
    filas = list(csv.DictReader(corrida.open(encoding="utf-8")))
    assert len(filas) == 4
    assert {f["backend"] for f in filas} == {"mock"}
    assert all(float(f["seconds"]) > 0 for f in filas)


def test_las_imagenes_del_benchmark_existen_y_son_el_grid_por_defecto(corrida):
    for f in csv.DictReader(corrida.open(encoding="utf-8")):
        assert Image.open(f["sprite_path"]).size == (128, 128)


def test_reanudar_no_regenera_nada(corrida, palette):
    """Una corrida de SDXL en 8 GB puede pasar de una hora. Si reanudar
    repitiera trabajo, nadie la reanudaria."""
    specs, seeds, _ = load_matrix(MATRIX)
    antes = corrida.read_text(encoding="utf-8")
    logs: list[str] = []
    run_benchmark(specs[:2], seeds[:2], ["mock"], palette, corrida.parent,
                  on_log=lambda m: logs.append(str(m)))
    assert corrida.read_text(encoding="utf-8") == antes, "el CSV cambio al reanudar"
    assert any("nada pendiente" in m for m in logs)


def test_reanudar_completa_lo_que_falta(corrida, palette, tmp_path):
    specs, seeds, _ = load_matrix(MATRIX)
    run_benchmark(specs[:2], seeds[:2], ["mock"], palette, tmp_path, on_log=lambda *_: None)
    parcial = len(list(csv.DictReader((tmp_path / "results.csv").open(encoding="utf-8"))))
    run_benchmark(specs[:3], seeds[:2], ["mock"], palette, tmp_path, on_log=lambda *_: None)
    total = len(list(csv.DictReader((tmp_path / "results.csv").open(encoding="utf-8"))))
    assert parcial == 4 and total == 6, "no anadio solo las que faltaban"


def test_el_resumen_agrega_por_backend(corrida):
    res = summarize(corrida)
    assert len(res) == 1
    s = res[0]
    assert s.backend == "mock" and s.imagenes == 4
    assert s.seg_total >= s.seg_mediana
    assert 0.0 <= s.cobertura_mediana <= 1.0
    assert s.tasa_fallo_pct == 0.0


def test_la_rubrica_es_por_backend_y_spec_no_por_imagen(corrida, tmp_path):
    """24 juicios son revisables; 96 no se rellenan nunca."""
    dst = write_rubric_template(corrida, tmp_path / "r.csv")
    filas = list(csv.DictReader(dst.open(encoding="utf-8")))
    assert len(filas) == 2, "deberia haber una fila por (backend, spec), no por imagen"
    assert all(c in filas[0] for c in RUBRIC_CRITERIA)
    assert all(filas[0][c] == "" for c in RUBRIC_CRITERIA), "debe venir sin puntuar"


def test_fusionar_rubrica_puntuada(corrida, tmp_path):
    dst = write_rubric_template(corrida, tmp_path / "r.csv")
    filas = list(csv.DictReader(dst.open(encoding="utf-8")))
    for i, f in enumerate(filas):
        for c in RUBRIC_CRITERIA:
            f[c] = str(2 if i == 0 else 3)
    with dst.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    fus = merge_rubric(corrida, dst)
    assert len(fus) == 2
    assert fus[0]["rubrica_total"] == 10.0 and fus[0]["rubrica_max"] == 15
    assert fus[1]["rubrica_total"] == 15.0
    assert fus[0]["seg_mediana"] > 0


# --------------------------------------------------------- empaquetado

def test_atlas_en_rejilla_uniforme(tmp_path):
    sheet = pack_sprites(_sprites(tmp_path, 5), columns=3, power_of_two=False)
    assert sheet.cell == (32, 32)
    assert sheet.size == (96, 64)          # 3 columnas x 2 filas
    assert len(sheet.frames) == 5


def test_potencia_de_dos(tmp_path):
    sheet = pack_sprites(_sprites(tmp_path, 5), columns=3, power_of_two=True)
    assert sheet.size == (128, 64)


def test_tamanos_mezclados_se_rechazan(tmp_path):
    ps = _sprites(tmp_path, 2)
    Image.new("RGBA", (16, 16)).save(tmp_path / "raro.png")
    with pytest.raises(ValueError, match="tamanos distintos"):
        pack_sprites([*ps, tmp_path / "raro.png"])


def test_cada_frame_recorta_su_sprite(tmp_path):
    """El atlas debe poder deshacerse: el recorte del frame k tiene que ser
    identico al sprite k original."""
    ps = _sprites(tmp_path, 5)
    sheet = pack_sprites(ps, names=[p.stem for p in ps], columns=3, power_of_two=False)
    for p, f in zip(ps, sheet.frames):
        recorte = np.array(sheet.image.crop((f.x, f.y, f.x + f.w, f.y + f.h)))
        assert np.array_equal(recorte, np.array(Image.open(p).convert("RGBA"))), f.name


def test_el_rect_de_unity_apunta_al_sprite_correcto(tmp_path):
    """Unity mide desde abajo. Si el flip esta mal, el atlas se ve perfecto y
    dentro de Unity sale el frame simetrico. Se comprueba deshaciendo el flip
    exactamente como lo hace el motor."""
    ps = _sprites(tmp_path, 5)
    sheet = pack_sprites(ps, names=[p.stem for p in ps], columns=3, power_of_two=True)
    W, H = sheet.size
    for p, f in zip(ps, sheet.frames):
        uy = f.unity_y(H)
        # De coordenadas Unity (abajo-izquierda) de vuelta a imagen (arriba).
        top = H - (uy + f.h)
        recorte = np.array(sheet.image.crop((f.x, top, f.x + f.w, top + f.h)))
        assert np.array_equal(recorte, np.array(Image.open(p).convert("RGBA"))), f.name


def test_el_flip_no_es_la_identidad():
    """Guarda contra 'arreglar' el flip devolviendo y sin tocar."""
    f = Frame(name="x", x=0, y=0, w=32, h=32)
    assert f.unity_y(256) == 224


# --------------------------------------------------------------- .meta

def test_el_meta_fija_los_ajustes_de_pixel_art(tmp_path):
    ps = _sprites(tmp_path, 4)
    _, _, meta = export_for_unity(ps, tmp_path / "atlas.png", names=[p.stem for p in ps])
    txt = meta.read_text(encoding="utf-8")
    assert "filterMode: 0" in txt, "sin Point filter el sprite sale borroso"
    assert "enableMipMap: 0" in txt
    assert "textureCompression: 0" in txt, "DXT destroza una paleta cuantizada"
    assert "spriteMeshType: 0" in txt, "Tight desalinea pivotes entre frames"
    assert "spriteMode: 2" in txt, "el atlas necesita modo Multiple"
    assert "alphaIsTransparency: 1" in txt
    assert "spritePixelsToUnits: 128" in txt


def test_el_meta_declara_todos_los_sprites(tmp_path):
    ps = _sprites(tmp_path, 7)
    _, _, meta = export_for_unity(ps, tmp_path / "atlas.png", names=[p.stem for p in ps])
    txt = meta.read_text(encoding="utf-8")
    for p in ps:
        assert f"name: {p.stem}" in txt
    assert txt.count("serializedVersion: 2\n      name:") == 7


def test_los_ids_son_unicos_y_deterministas(tmp_path):
    """Un GUID o un internalID duplicado rompe referencias en escenas y
    prefabs, y Unity no siempre avisa."""
    ps = _sprites(tmp_path, 6)
    sheet = pack_sprites(ps, names=[p.stem for p in ps])
    a = unity_meta(sheet, "atlas.png")
    b = unity_meta(sheet, "atlas.png")
    assert a == b, "el .meta no es determinista: reimportar rompe referencias"

    ids = re.findall(r"spriteID: ([0-9a-f]{32})", a)
    internos = re.findall(r"internalID: (-?\d+)", a)
    assert len(ids) == 6 and len(set(ids)) == 6
    assert len(set(internos)) >= 6


def test_el_pivote_por_defecto_va_en_los_pies(tmp_path):
    ps = _sprites(tmp_path, 2)
    sheet = pack_sprites(ps, names=[p.stem for p in ps])
    txt = unity_meta(sheet, "atlas.png")
    assert "pivot: {x: 0.5, y: 0.0}" in txt
    assert "alignment: 9" in txt, "sin alignment Custom, Unity ignora el pivote"


def test_frames_json_documenta_el_origen(tmp_path):
    import json

    ps = _sprites(tmp_path, 3)
    _, js, _ = export_for_unity(ps, tmp_path / "atlas.png", names=[p.stem for p in ps])
    data = json.loads(js.read_text(encoding="utf-8"))
    assert data["origen"] == "arriba-izquierda", "sin esto nadie sabe si hay que voltear"
    assert len(data["frames"]) == 3
