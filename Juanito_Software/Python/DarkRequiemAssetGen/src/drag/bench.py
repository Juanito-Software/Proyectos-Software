"""Fase 2: el arnes de benchmark.

Mi opinion mas fuerte sobre este proyecto sigue siendo esta: si comparas los
modelos a ojo sobre 96 imagenes, vas a elegir mal. No por falta de criterio,
sino porque a la imagen numero cuarenta ya estas justificando la que te gusto
primero. El CSV no decide por ti, pero te obliga a mirar lo que la vista pasa
por alto.

Tres decisiones de diseno que vienen de tu restriccion de 8 GB:

- **Un load por backend, no uno por imagen.** Cargar SDXL cuesta decenas de
  segundos; hacerlo 32 veces es tirar media hora. Se carga, se generan las 32
  imagenes de ese backend, se descarga y se pasa al siguiente.
- **CSV incremental.** Cada fila se escribe en cuanto existe. Una corrida de
  SDXL en 8 GB puede pasar de una hora: que un cuelgue a mitad no borre el
  trabajo no es comodidad, es la diferencia entre ejecutarlo y no ejecutarlo.
- **Reanudable.** Al arrancar lee lo ya hecho y lo salta. Puedes parar,
  liberar la GPU para jugar, y seguir manana.

Y una decision que no viene de la VRAM: se mide el tiempo por imagen. En una
tarjeta ajustada, "el mejor modelo" que tarda cuatro veces mas no es el mejor
modelo, porque acabaras generando cuatro veces menos variantes por sprite.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from statistics import median

import numpy as np
from PIL import Image

from .backends.base import Backend, get_backend
from .metrics import measure
from .palette import Palette
from .pixelpass import PixelPassConfig, run_pixelpass
from .prompts import build_prompt
from .spec import AssetSpec

RESULTS = "results.csv"
RUBRIC = "rubrica.csv"

#: Criterios manuales. Deliberadamente incluyen el unico que importa de verdad
#: y que ninguna metrica puede calcular: cuanto trabajo te ahorra en Aseprite.
RUBRIC_CRITERIA = [
    "rejilla",          # se alinea tras el downscale
    "paleta",           # respeta las rampas de Dark Requiem
    "legibilidad_32",   # se entiende a 32px reales, sin ampliar
    "silueta",          # coherencia de silueta entre seeds
    "ahorro_aseprite",  # cuanto retoque manual te quita de encima
]


@dataclass
class BenchRow:
    backend: str
    spec_index: int
    kind: str
    subject: str
    seed: int
    seconds: float
    sprite_path: str
    raw_unique_colors: int
    raw_offpalette_pct: float
    raw_orphan_color_pct: float
    raw_grid_adherence: float
    final_unique_colors: int
    final_offpalette_pct: float
    final_soft_alpha_pct: float
    subject_coverage: float
    sospechosa: int          # 1 si el sprite salio vacio o casi

    @property
    def key(self) -> tuple[str, int, int]:
        return (self.backend, self.spec_index, self.seed)


# ------------------------------------------------------------------ matriz

def load_matrix(path: str | Path) -> tuple[list[AssetSpec], list[int], str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    seeds = [int(s) for s in data["seeds"]]
    specs = [
        AssetSpec(
            kind=s["kind"],
            subject=s["subject"],
            facing=s.get("facing", "S"),
            tags=tuple(s.get("tags", ())),
            variants=1,
        )
        for s in data["specs"]
    ]
    return specs, seeds, data.get("name", Path(path).stem)


# ----------------------------------------------------------------- corrida

def _read_done(csv_path: Path) -> set[tuple[str, int, int]]:
    if not csv_path.exists():
        return set()
    done = set()
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            done.add((r["backend"], int(r["spec_index"]), int(r["seed"])))
    return done


def _append(csv_path: Path, row: BenchRow) -> None:
    header = [f.name for f in fields(BenchRow)]
    nuevo = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        if nuevo:
            w.writeheader()
        w.writerow(asdict(row))


def run_benchmark(
    specs: list[AssetSpec],
    seeds: list[int],
    backend_keys: list[str],
    palette: Palette,
    out_dir: str | Path,
    grid: int = 32,
    render_size: int = 1024,
    keep_raw: bool = False,
    bg_key: str | None = "#FF00FF",
    on_log=print,
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / RESULTS
    done = _read_done(csv_path)
    cfg = PixelPassConfig(grid=grid, bg_key=bg_key)

    total = len(specs) * len(seeds) * len(backend_keys)
    hechas = len(done)
    if hechas:
        on_log(f"Reanudando: {hechas}/{total} ya estaban hechas.")

    for bkey in backend_keys:
        pendientes = [
            (i, s, seed)
            for i, s in enumerate(specs)
            for seed in seeds
            if (bkey, i, seed) not in done
        ]
        if not pendientes:
            on_log(f"[{bkey}] nada pendiente.")
            continue

        backend: Backend = get_backend(bkey)
        on_log(f"[{bkey}] cargando ({len(pendientes)} imagenes pendientes)...")
        backend.load()
        bdir = out / bkey
        bdir.mkdir(exist_ok=True)
        if keep_raw:
            (bdir / "raw").mkdir(exist_ok=True)

        try:
            for i, spec, seed in pendientes:
                prompt, negative = build_prompt(spec.with_(grid=grid))
                t0 = time.perf_counter()
                raw = backend.generate(prompt, negative, seed, render_size, render_size)
                seconds = time.perf_counter() - t0

                res = run_pixelpass(raw, palette, cfg)
                name = f"{i:02d}_{spec.kind}_seed{seed}"
                sprite_path = bdir / f"{name}.png"
                res.image.save(sprite_path)
                if keep_raw:
                    raw.save(bdir / "raw" / f"{name}_raw.png")

                rm = measure(raw.convert("RGBA"), palette, target_grid=grid)
                fm = measure(res.image, palette, target_grid=grid)
                alpha = np.array(res.image)[..., 3]
                coverage = float((alpha > 0).mean())

                row = BenchRow(
                    backend=bkey,
                    spec_index=i,
                    kind=spec.kind,
                    subject=spec.subject,
                    seed=seed,
                    seconds=round(seconds, 2),
                    sprite_path=str(sprite_path),
                    raw_unique_colors=rm.unique_colors,
                    raw_offpalette_pct=rm.offpalette_pct,
                    raw_orphan_color_pct=rm.orphan_color_pct,
                    raw_grid_adherence=rm.grid_adherence,
                    final_unique_colors=fm.unique_colors,
                    final_offpalette_pct=fm.offpalette_pct,
                    final_soft_alpha_pct=fm.soft_alpha_pct,
                    subject_coverage=round(coverage, 4),
                    # Un sprite que ocupa menos del 5% del canvas o que se
                    # queda en dos colores no es un resultado flojo: es un
                    # fallo. Contarlos aparte evita que la mediana los tape.
                    sospechosa=int(coverage < 0.05 or fm.unique_colors <= 2),
                )
                _append(csv_path, row)
                hechas += 1
                on_log(
                    f"  [{hechas:3d}/{total}] {bkey:18s} {name:28s} "
                    f"{seconds:6.2f}s  cols {rm.unique_colors:5d}->{fm.unique_colors:2d}"
                    + ("  SOSPECHOSA" if row.sospechosa else "")
                )
        finally:
            backend.unload()
            on_log(f"[{bkey}] descargado.")

    return csv_path


# ----------------------------------------------------------------- informe

@dataclass
class BackendSummary:
    backend: str
    imagenes: int
    seg_mediana: float
    seg_total: float
    colores_finales_mediana: float
    fuera_paleta_crudo_mediana: float
    huerfanos_crudo_mediana: float
    cobertura_mediana: float
    sospechosas: int
    tasa_fallo_pct: float


def _rows(csv_path: str | Path) -> list[dict]:
    with Path(csv_path).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def summarize(csv_path: str | Path) -> list[BackendSummary]:
    rows = _rows(csv_path)
    out: list[BackendSummary] = []
    for bkey in sorted({r["backend"] for r in rows}):
        rs = [r for r in rows if r["backend"] == bkey]
        segs = [float(r["seconds"]) for r in rs]
        fallos = sum(int(r["sospechosa"]) for r in rs)
        out.append(
            BackendSummary(
                backend=bkey,
                imagenes=len(rs),
                seg_mediana=round(median(segs), 2),
                seg_total=round(sum(segs), 1),
                colores_finales_mediana=median(float(r["final_unique_colors"]) for r in rs),
                fuera_paleta_crudo_mediana=round(
                    median(float(r["raw_offpalette_pct"]) for r in rs), 2
                ),
                huerfanos_crudo_mediana=round(
                    median(float(r["raw_orphan_color_pct"]) for r in rs), 2
                ),
                cobertura_mediana=round(median(float(r["subject_coverage"]) for r in rs), 3),
                sospechosas=fallos,
                tasa_fallo_pct=round(fallos / len(rs) * 100, 1),
            )
        )
    return out


def write_rubric_template(csv_path: str | Path, dst: str | Path) -> Path:
    """Una fila por (backend, spec): 8x3 = 24 juicios, no 96.

    Puntuar imagen a imagen es inviable y ademas equivocado: lo que quieres
    juzgar es si ese modelo entiende ese tipo de sujeto, y eso se ve mirando
    las cuatro seeds juntas, no una suelta.
    """
    rows = _rows(csv_path)
    vistos = []
    for r in rows:
        k = (r["backend"], int(r["spec_index"]))
        if k not in vistos:
            vistos.append(k)

    dst = Path(dst)
    with dst.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["backend", "spec_index", "kind", "subject", *RUBRIC_CRITERIA, "notas"])
        for bkey, idx in vistos:
            ref = next(
                r for r in rows if r["backend"] == bkey and int(r["spec_index"]) == idx
            )
            w.writerow([bkey, idx, ref["kind"], ref["subject"], *([""] * len(RUBRIC_CRITERIA)), ""])
    return dst


def merge_rubric(csv_path: str | Path, rubric_path: str | Path) -> list[dict]:
    """Cruza la rubrica rellenada a mano con las metricas automaticas."""
    auto = _rows(csv_path)
    manual = _rows(rubric_path)
    out = []
    for m in manual:
        rs = [
            r
            for r in auto
            if r["backend"] == m["backend"] and r["spec_index"] == m["spec_index"]
        ]
        if not rs:
            continue
        puntos = [float(m[c]) for c in RUBRIC_CRITERIA if m.get(c, "").strip()]
        out.append(
            {
                "backend": m["backend"],
                "spec_index": int(m["spec_index"]),
                "kind": m["kind"],
                "subject": m["subject"],
                "rubrica_total": round(sum(puntos), 1) if puntos else None,
                "rubrica_max": len(RUBRIC_CRITERIA) * 3,
                "seg_mediana": round(median(float(r["seconds"]) for r in rs), 2),
                "sospechosas": sum(int(r["sospechosa"]) for r in rs),
                "notas": m.get("notas", ""),
            }
        )
    return out
