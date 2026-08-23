"""PixelPass: convierte una imagen "con estetica de pixel" en pixel art real.

Esta es la capa que justifica el proyecto. Un modelo de difusion produce una
imagen de 1024x1024 con bordes antialiaseados, cientos de colores y una rejilla
que casi nunca esta alineada. Unity no quiere eso: quiere 32x32 exactos, alpha
dura, y una paleta cerrada.

Orden de operaciones (importa, y mucho):

    1. quitar fondo          -> flood fill desde el borde, tolerancia perceptual
    2. recortar y encuadrar  -> el sujeto ocupa el canvas, no flota en el centro
    3. cuantizar a paleta    -> ANTES del downscale, en OKLab
    4. downscale modal       -> color dominante por celda, no promedio
    5. alpha binaria         -> 0 o 255, nunca intermedios
    6. despeckle             -> matar pixeles huerfanos

El punto no obvio es el 3 antes del 4. Si primero reduces y luego cuantizas,
el promedio de la reduccion inventa colores intermedios que despues se mapean
a tonos que no estaban en la imagen: aparecen halos. Cuantizando primero, el
downscale solo tiene que elegir por votacion entre colores que ya son legales.

Y el 4 con moda en vez de media: promediar bordes es literalmente crear
antialias, que es exactamente lo que estamos intentando eliminar.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from .palette import Palette, hex_to_rgb, srgb_to_oklab


# ------------------------------------------------------------------ config

@dataclass(frozen=True)
class PixelPassConfig:
    grid: int = 32
    remove_background: bool = True
    bg_tolerance: float = 0.10          # distancia OKLab; ~0.10 es generosa
    bg_key: str | None = None           # "#FF00FF" para no adivinar el fondo
    margin: float = 0.06                # margen relativo tras el recorte
    alpha_threshold: float = 0.5        # cobertura minima para que la celda exista
    despeckle: bool = True
    square: bool = True
    preview_scale: int = 8


# --------------------------------------------------------------- deteccion

def detect_pixel_scale(rgb: np.ndarray, tol: int = 10, max_scale: int = 64) -> int:
    """Estima el tamano real del "pixel" de la imagen.

    Recorre filas y columnas midiendo cuantos pixeles consecutivos se mantienen
    dentro de una tolerancia de color. La mediana de esas longitudes de racha es
    el espaciado de rejilla. Es la idea de pixeldetector (Astropulse, MIT)
    reimplementada sobre numpy puro.

    Devuelve 1 cuando la imagen es continua (salida cruda de un difusor), que es
    la senal de que no hay rejilla que recuperar y hay que reducir a pelo.
    """
    arr = np.asarray(rgb)[..., :3].astype(np.int16)
    runs: list[int] = []
    for axis in (0, 1):
        a = arr if axis == 0 else arr.transpose(1, 0, 2)
        h, w, _ = a.shape
        step = max(1, h // 64)
        for y in range(0, h, step):
            row = a[y]
            diff = np.abs(np.diff(row, axis=0)).max(axis=1)
            edges = np.flatnonzero(diff > tol)
            if edges.size < 2:
                continue
            # Un borde antialiaseado produce 2-3 indices consecutivos para una
            # sola transicion. Sin colapsarlos, la mediana de rachas se va a 1 y
            # el detector declara "imagen continua" en una imagen que si tiene
            # rejilla. Se agrupan los indices separados por menos de 2 px.
            keep = [int(edges[0])]
            for e in edges[1:]:
                if e - keep[-1] > 2:
                    keep.append(int(e))
            if len(keep) < 2:
                continue
            lengths = np.diff(np.array(keep))
            runs.extend(int(v) for v in lengths if 2 <= v <= max_scale)
    if not runs:
        return 1
    scale = int(np.median(runs))
    return max(1, scale)


# ----------------------------------------------------------------- fondo

def remove_background(
    rgba: np.ndarray,
    tolerance: float = 0.10,
    ref_rgb: tuple[int, int, int] | None = None,
    min_subject: float = 0.02,
) -> np.ndarray:
    """Flood fill desde los cuatro bordes en espacio OKLab.

    Solo borra lo conectado al borde: un hueco interior del mismo color que el
    fondo (el ojo de una calavera, la ranura de un yelmo) se conserva, que es
    justo lo que un `remove color` global se cargaria.

    Dos defensas que no estaban en la primera version, ambas por el mismo
    fallo observado: si el sujeto tiene tonos cercanos al color de fondo, el
    relleno entra por la parte clara y se come medio sprite.

    - `ref_rgb`: fijar el color a eliminar en vez de deducirlo de la mediana
      del borde. Es la opcion correcta cuando controlamos el prompt, porque el
      prompt ya pide "plain solid magenta background": si sabemos que el fondo
      es magenta, adivinarlo es un riesgo gratuito.
    - `min_subject`: si tras el relleno queda menos de esta fraccion de pixeles
      opacos, se reintenta con la mitad de tolerancia. Preferimos devolver una
      imagen con fondo (visible, corregible a mano) que una que se ha comido al
      personaje (silenciosa, y descubierta tres carpetas despues).
    """
    h, w, _ = rgba.shape
    lab = srgb_to_oklab(rgba[..., :3])

    if ref_rgb is not None:
        ref = srgb_to_oklab(np.array(ref_rgb, dtype=np.uint8).reshape(1, 1, 3))[0, 0]
    else:
        border = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
        ref = np.median(border, axis=0)
    cand = np.sqrt(((lab - ref) ** 2).sum(axis=-1)) <= tolerance

    reach = np.zeros((h, w), dtype=bool)
    reach[0] |= cand[0]
    reach[-1] |= cand[-1]
    reach[:, 0] |= cand[:, 0]
    reach[:, -1] |= cand[:, -1]

    # Propagacion vectorizada en lugar de BFS pixel a pixel. Cada pasada avanza
    # una distancia arbitraria a lo largo de una fila o columna entera, asi que
    # converge en unas pocas iteraciones en vez de en un millon de pops de cola.
    cols = np.arange(w)[None, :]
    rows = np.arange(h)[:, None]

    for _ in range(64):
        before = int(reach.sum())

        blocked = np.maximum.accumulate(np.where(~cand, cols, -1), axis=1)
        seen = np.maximum.accumulate(np.where(reach, cols, -1), axis=1)
        reach |= cand & (seen > blocked)

        rc = cols.max() - cols
        blocked = np.maximum.accumulate(np.where(~cand, rc, -1)[:, ::-1], axis=1)[:, ::-1]
        seen = np.maximum.accumulate(np.where(reach, rc, -1)[:, ::-1], axis=1)[:, ::-1]
        reach |= cand & (seen > blocked)

        blocked = np.maximum.accumulate(np.where(~cand, rows, -1), axis=0)
        seen = np.maximum.accumulate(np.where(reach, rows, -1), axis=0)
        reach |= cand & (seen > blocked)

        rr = rows.max() - rows
        blocked = np.maximum.accumulate(np.where(~cand, rr, -1)[::-1], axis=0)[::-1]
        seen = np.maximum.accumulate(np.where(reach, rr, -1)[::-1], axis=0)[::-1]
        reach |= cand & (seen > blocked)

        if int(reach.sum()) == before:
            break

    superviviente = 1.0 - reach.mean()
    if superviviente < min_subject and tolerance > 0.02:
        return remove_background(rgba, tolerance / 2, ref_rgb, min_subject)

    out = rgba.copy()
    out[reach, 3] = 0
    return out


def trim_and_frame(rgba: np.ndarray, margin: float = 0.06, square: bool = True) -> np.ndarray:
    """Recorta al contenido opaco y encuadra. Sin esto, un sprite generado con
    mucho aire alrededor pierde la mitad de su resolucion util al bajar a 32."""
    alpha = rgba[..., 3]
    ys, xs = np.nonzero(alpha > 0)
    if ys.size == 0:
        return rgba
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    crop = rgba[y0:y1, x0:x1]

    h, w, _ = crop.shape
    if square:
        side = max(h, w)
        pad = int(round(side * margin))
        side += pad * 2
        canvas = np.zeros((side, side, 4), dtype=rgba.dtype)
        oy, ox = (side - h) // 2, (side - w) // 2
        canvas[oy : oy + h, ox : ox + w] = crop
        return canvas
    return crop


# -------------------------------------------------------------- downscale

def modal_downscale(
    idx_map: np.ndarray, alpha01: np.ndarray, grid: int, n_colors: int
) -> tuple[np.ndarray, np.ndarray]:
    """Reduce por votacion: cada celda destino se queda con el indice de paleta
    mas frecuente entre sus pixeles opacos. Devuelve (indices, cobertura)."""
    h, w = idx_map.shape
    row_cell = (np.arange(h) * grid // h).clip(0, grid - 1)
    col_cell = (np.arange(w) * grid // w).clip(0, grid - 1)
    cell = (row_cell[:, None] * grid + col_cell[None, :]).ravel()

    a = alpha01.ravel()
    keys = cell * n_colors + idx_map.ravel()
    votes = np.bincount(
        keys, weights=a, minlength=grid * grid * n_colors
    ).reshape(grid * grid, n_colors)

    total = np.bincount(cell, minlength=grid * grid).astype(np.float64)
    covered = np.bincount(cell, weights=a, minlength=grid * grid)
    coverage = np.divide(covered, total, out=np.zeros_like(covered), where=total > 0)

    best = votes.argmax(axis=1)
    return best.reshape(grid, grid), coverage.reshape(grid, grid)


def despeckle(idx: np.ndarray, alpha: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Elimina pixeles opacos totalmente aislados y rellena agujeros de 1px.

    A 32x32 un pixel suelto no es detalle, es ruido: en movimiento parpadea.
    """
    a = alpha.copy()
    idxo = idx.copy()
    pad = np.pad(a, 1, constant_values=0)
    neigh = sum(
        pad[1 + dy : 1 + dy + a.shape[0], 1 + dx : 1 + dx + a.shape[1]]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
    )
    a[(a > 0) & (neigh == 0)] = 0

    padi = np.pad(idxo, 1, mode="edge")
    holes = (a == 0) & (neigh == 4)
    if holes.any():
        a[holes] = 255
        ys, xs = np.nonzero(holes)
        for y, x in zip(ys, xs):
            vals = [padi[y, x + 1], padi[y + 2, x + 1], padi[y + 1, x], padi[y + 1, x + 2]]
            idxo[y, x] = max(set(vals), key=vals.count)
    return idxo, a


# ------------------------------------------------------------------ paso

@dataclass
class PixelPassResult:
    image: Image.Image           # RGBA exacto grid x grid
    preview: Image.Image         # ampliado nearest, para mirarlo sin bizquear
    detected_scale: int
    colors_before: int
    colors_after: int


def run_pixelpass(
    src: Image.Image | str | Path,
    palette: Palette,
    cfg: PixelPassConfig | None = None,
) -> PixelPassResult:
    cfg = cfg or PixelPassConfig()
    img = Image.open(src) if isinstance(src, (str, Path)) else src
    img = img.convert("RGBA")
    rgba = np.array(img)

    colors_before = int(
        np.unique(rgba[..., :3][rgba[..., 3] > 0].reshape(-1, 3), axis=0).shape[0]
    ) if (rgba[..., 3] > 0).any() else 0

    scale = detect_pixel_scale(rgba[..., :3])

    if cfg.remove_background and (rgba[..., 3] == 255).all():
        ref = hex_to_rgb(cfg.bg_key) if cfg.bg_key else None
        rgba = remove_background(rgba, cfg.bg_tolerance, ref_rgb=ref)
        # Si el modelo ignoro la instruccion de fondo magenta, la clave no
        # encuentra nada que quitar. Antes de devolver un sprite con el fondo
        # pegado, se reintenta adivinando por el borde.
        if ref is not None and (rgba[..., 3] == 255).mean() > 0.99:
            rgba = remove_background(rgba, cfg.bg_tolerance, ref_rgb=None)

    rgba = trim_and_frame(rgba, cfg.margin, cfg.square)

    # 3. cuantizar A RESOLUCION COMPLETA
    flat_idx = palette.nearest_index(rgba[..., :3].reshape(-1, 3))
    idx_map = flat_idx.reshape(rgba.shape[:2])
    alpha01 = (rgba[..., 3].astype(np.float64) / 255.0)

    # 4. downscale por moda
    idx_small, coverage = modal_downscale(idx_map, alpha01, cfg.grid, len(palette))

    # 5. alpha binaria
    alpha_small = np.where(coverage >= cfg.alpha_threshold, 255, 0).astype(np.uint8)

    # 6. despeckle
    if cfg.despeckle:
        idx_small, alpha_small = despeckle(idx_small, alpha_small)

    out = np.zeros((cfg.grid, cfg.grid, 4), dtype=np.uint8)
    out[..., :3] = palette.colors[idx_small]
    out[..., 3] = alpha_small
    out[alpha_small == 0, :3] = 0

    result_img = Image.fromarray(out, mode="RGBA")
    preview = result_img.resize(
        (cfg.grid * cfg.preview_scale, cfg.grid * cfg.preview_scale), Image.NEAREST
    )
    colors_after = int(
        np.unique(out[..., :3][out[..., 3] > 0].reshape(-1, 3), axis=0).shape[0]
    ) if (out[..., 3] > 0).any() else 0

    return PixelPassResult(
        image=result_img,
        preview=preview,
        detected_scale=scale,
        colors_before=colors_before,
        colors_after=colors_after,
    )
