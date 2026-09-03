"""Metricas objetivas para el benchmark.

Tesis de esta capa: comparar modelos "a ojo" sobre 160 imagenes es un ejercicio
de sesgo de confirmacion. Estas cinco cifras no sustituyen tu criterio artistico,
pero detectan los fallos que la vista perdona y Unity no: alpha blanda, colores
fuera de paleta, y ruido de gradiente disfrazado de detalle.

Todas se calculan sobre la imagen CRUDA del modelo, antes del PixelPass. Ahi es
donde miden lo que quieres medir: cuanto trabajo le queda al pipeline.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from .palette import Palette
from .pixelpass import detect_pixel_scale


@dataclass
class ImageMetrics:
    path: str
    width: int
    height: int
    unique_colors: int
    offpalette_pct: float
    soft_alpha_pct: float
    orphan_color_pct: float
    detected_scale: int
    grid_adherence: float

    def as_row(self) -> dict:
        return asdict(self)


def measure(
    src: Image.Image | str | Path,
    palette: Palette,
    target_grid: int = 128,
    offpalette_tol: float = 0.02,
    orphan_frac: float = 0.001,
) -> ImageMetrics:
    path = str(src) if isinstance(src, (str, Path)) else "<memoria>"
    img = (Image.open(src) if isinstance(src, (str, Path)) else src).convert("RGBA")
    arr = np.array(img)
    h, w, _ = arr.shape
    alpha = arr[..., 3]
    opaque = alpha > 0
    rgb = arr[..., :3][opaque].reshape(-1, 3)

    if rgb.shape[0] == 0:
        return ImageMetrics(path, w, h, 0, 0.0, 0.0, 0.0, 1, 0.0)

    uniq, counts = np.unique(rgb, axis=0, return_counts=True)

    # 1. Cuantos colores hay realmente. Un sprite de 32x32 sano vive por debajo
    #    de ~24; un PNG de difusor sin tratar puede pasar de 5.000.
    unique_colors = int(uniq.shape[0])

    # 2. Cuanto se sale de tu paleta. Mide el trabajo de cuantizacion pendiente.
    dist = palette.distance_to(rgb)
    offpalette_pct = float((dist > offpalette_tol).mean() * 100.0)

    # 3. Alpha intermedia = antialias en el borde. En Unity con Point filter
    #    esto se ve como flecos sucios alrededor del sprite.
    soft_alpha_pct = float(((alpha > 0) & (alpha < 255)).mean() * 100.0)

    # 4. Colores huerfanos: los que aparecen en menos del 0.1% de los pixeles.
    #    Es la firma de un degradado suave, no de una rampa de pixel art.
    threshold = max(1, int(rgb.shape[0] * orphan_frac))
    orphan_color_pct = float(counts[counts < threshold].sum() / rgb.shape[0] * 100.0)

    # 5. Adherencia a rejilla: si la imagen es NxN y el objetivo es 32, el
    #    bloque real deberia medir N/32. Cuanto se aleja, mas rota esta.
    #
    #    Guarda importante: sobre una imagen que YA esta a la rejilla objetivo,
    #    la deteccion no mide escala, mide cuanto miden las manchas de color
    #    plano. Un sprite limpio con un torso de 6 px daria "escala 6" y una
    #    adherencia de 0,17, que es exactamente lo contrario de la verdad. En
    #    ese caso la respuesta correcta es trivial: cada pixel es un pixel.
    if min(w, h) <= target_grid:
        detected, grid_adherence = 1, 1.0
    else:
        detected = detect_pixel_scale(arr[..., :3])
        expected = max(1, min(w, h) // target_grid)
        grid_adherence = float(
            min(detected, expected) / max(detected, expected) if max(detected, expected) else 0.0
        )

    return ImageMetrics(
        path=path,
        width=w,
        height=h,
        unique_colors=unique_colors,
        offpalette_pct=round(offpalette_pct, 3),
        soft_alpha_pct=round(soft_alpha_pct, 3),
        orphan_color_pct=round(orphan_color_pct, 3),
        detected_scale=detected,
        grid_adherence=round(grid_adherence, 3),
    )


def write_csv(rows: list[ImageMetrics], path: str | Path) -> None:
    path = Path(path)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].as_row().keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r.as_row())
