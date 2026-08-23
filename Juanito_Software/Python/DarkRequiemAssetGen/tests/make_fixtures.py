"""Genera entradas sinteticas que imitan la salida cruda de un difusor.

No sirve de nada validar el PixelPass contra pixel art ya limpio: pasaria
trivialmente. Lo que hay que simular es el problema real: 1024x1024, bordes
antialiaseados, degradados suaves, ruido de compresion y fondo solido.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024


def _gradient(shape, c0, c1, angle=0.0):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    t = (xx * np.cos(angle) + yy * np.sin(angle))
    t = (t - t.min()) / max(1e-6, (t.max() - t.min()))
    c0 = np.array(c0, dtype=np.float64)
    c1 = np.array(c1, dtype=np.float64)
    return (c0[None, None, :] * (1 - t[..., None]) + c1[None, None, :] * t[..., None])


def knight(path: Path) -> None:
    """Caballero: casco, torso, capa, espada. Con sombreado continuo."""
    mask = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(mask)
    cx = SIZE // 2
    d.ellipse([cx - 150, 120, cx + 150, 420], fill=255)          # casco
    d.polygon([(cx - 210, 400), (cx + 210, 400), (cx + 260, 800), (cx - 260, 800)], fill=255)
    d.polygon([(cx - 300, 420), (cx - 200, 400), (cx - 150, 880), (cx - 330, 860)], fill=255)
    d.rectangle([cx + 250, 180, cx + 300, 720], fill=255)        # espada
    d.rectangle([cx + 190, 700, cx + 360, 740], fill=255)        # guarda
    d.rectangle([cx - 190, 800, cx - 90, 940], fill=255)
    d.rectangle([cx + 90, 800, cx + 190, 940], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3.0))            # antialias

    body = _gradient((SIZE, SIZE), (18, 22, 34), (96, 122, 150), angle=0.9)
    cape = _gradient((SIZE, SIZE), (52, 10, 18), (168, 44, 52), angle=2.2)
    m = np.array(mask, dtype=np.float64) / 255.0
    capemask = np.zeros((SIZE, SIZE))
    capemask[:, : cx - 150] = 1.0
    rgb = body * (1 - capemask[..., None]) + cape * capemask[..., None]

    bg = np.array([120, 118, 130], dtype=np.float64)
    out = rgb * m[..., None] + bg[None, None, :] * (1 - m[..., None])
    out += np.random.default_rng(0).normal(0, 2.2, out.shape)     # ruido tipo jpeg
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)


def potion(path: Path) -> None:
    mask = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(mask)
    cx, cy = SIZE // 2, SIZE // 2 + 60
    d.ellipse([cx - 260, cy - 200, cx + 260, cy + 300], fill=255)
    d.rectangle([cx - 90, cy - 420, cx + 90, cy - 150], fill=255)
    d.rectangle([cx - 130, cy - 470, cx + 130, cy - 400], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(4.0))

    glass = _gradient((SIZE, SIZE), (20, 60, 34), (110, 220, 120), angle=1.4)
    m = np.array(mask, dtype=np.float64) / 255.0
    bg = np.array([200, 198, 205], dtype=np.float64)
    out = glass * m[..., None] + bg[None, None, :] * (1 - m[..., None])
    out += np.random.default_rng(1).normal(0, 1.8, out.shape)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)


def blocky_sprite(path: Path, block: int = 16) -> None:
    """Caso 2: el modelo SI produjo rejilla, pero a 64x64 dentro de 1024.
    El detector de escala deberia devolver ~16."""
    rng = np.random.default_rng(7)
    small = rng.integers(0, 6, size=(SIZE // block, SIZE // block))
    palette = np.array(
        [[11, 10, 15], [58, 51, 72], [47, 74, 143], [140, 37, 49], [217, 164, 65], [194, 188, 203]],
        dtype=np.uint8,
    )
    img = palette[small].repeat(block, 0).repeat(block, 1)
    img = Image.fromarray(img).filter(ImageFilter.GaussianBlur(0.8))  # un poco de AA
    img.save(path)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures")
    out.mkdir(parents=True, exist_ok=True)
    knight(out / "raw_knight.png")
    potion(out / "raw_potion.png")
    blocky_sprite(out / "raw_blocky.png")
    print(f"Fixtures en {out}")


if __name__ == "__main__":
    main()
