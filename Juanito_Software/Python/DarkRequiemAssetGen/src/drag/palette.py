"""Paletas fijas y conversion de color perceptual (OKLab).

Por que OKLab y no RGB: la distancia euclidea en sRGB miente. Un azul oscuro y
un violeta oscuro pueden estar mas "cerca" en RGB que dos grises que el ojo ve
casi identicos. Cuantizar en RGB produce manchas de color equivocado en las
zonas de sombra, que es justo donde vive el 60% de una paleta de fantasia
oscura. OKLab esta disenado para que la distancia euclidea se parezca a la
diferencia percibida, y son 20 lineas de numpy sin dependencias extra.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PALETTE_DIR = Path(__file__).resolve().parents[2] / "palettes"


# --------------------------------------------------------------- color math

def _srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = c.astype(np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb_to_oklab(rgb: np.ndarray) -> np.ndarray:
    """(..., 3) uint8/float sRGB -> (..., 3) float OKLab."""
    lin = _srgb_to_linear(np.asarray(rgb))
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.stack(
        [
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
        ],
        axis=-1,
    )


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(rgb) -> str:
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


# ------------------------------------------------------------------ palette

@dataclass(frozen=True)
class Palette:
    name: str
    colors: np.ndarray  # (N, 3) uint8
    ramps: dict[str, list[str]] | None = None

    def __len__(self) -> int:
        return int(self.colors.shape[0])

    @property
    def oklab(self) -> np.ndarray:
        return srgb_to_oklab(self.colors)

    @property
    def hex_list(self) -> list[str]:
        return [rgb_to_hex(c) for c in self.colors]

    # ------------------------------------------------------------ loading

    @classmethod
    def load(cls, name_or_path: str | Path) -> Palette:
        p = Path(name_or_path)
        if not p.exists():
            p = PALETTE_DIR / f"{name_or_path}.json"
        if not p.exists():
            raise FileNotFoundError(
                f"No encuentro la paleta '{name_or_path}'. "
                f"Buscadas: {name_or_path} y {PALETTE_DIR / f'{name_or_path}.json'}"
            )
        data = json.loads(p.read_text(encoding="utf-8"))
        if "ramps" in data:
            ramps = data["ramps"]
            hexes = [h for ramp in ramps.values() for h in ramp]
        else:
            ramps = None
            hexes = data["colors"]
        colors = np.array([hex_to_rgb(h) for h in hexes], dtype=np.uint8)
        return cls(name=data.get("name", p.stem), colors=colors, ramps=ramps)

    def save(self, path: str | Path) -> None:
        payload = {"name": self.name, "colors": self.hex_list}
        if self.ramps:
            payload = {"name": self.name, "ramps": self.ramps}
        Path(path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # -------------------------------------------------------------- mapping

    def map_rgb(self, rgb: np.ndarray) -> np.ndarray:
        """Mapea cada pixel al color mas cercano de la paleta, en OKLab."""
        flat = np.asarray(rgb).reshape(-1, 3)
        idx = self.nearest_index(flat)
        return self.colors[idx].reshape(np.asarray(rgb).shape)

    def nearest_index(self, rgb: np.ndarray) -> np.ndarray:
        """Indice del color de paleta mas cercano para cada pixel (N,3)->(N,)."""
        src = srgb_to_oklab(np.asarray(rgb).reshape(-1, 3))
        dst = self.oklab
        # (N, 1, 3) - (1, K, 3) -> (N, K). Por bloques para no reventar RAM.
        out = np.empty(src.shape[0], dtype=np.int64)
        block = 65536
        for i in range(0, src.shape[0], block):
            chunk = src[i : i + block]
            d = ((chunk[:, None, :] - dst[None, :, :]) ** 2).sum(axis=-1)
            out[i : i + block] = d.argmin(axis=1)
        return out

    def distance_to(self, rgb: np.ndarray) -> np.ndarray:
        """Distancia OKLab al color de paleta mas cercano, por pixel."""
        src = srgb_to_oklab(np.asarray(rgb).reshape(-1, 3))
        dst = self.oklab
        out = np.empty(src.shape[0], dtype=np.float64)
        block = 65536
        for i in range(0, src.shape[0], block):
            chunk = src[i : i + block]
            d = ((chunk[:, None, :] - dst[None, :, :]) ** 2).sum(axis=-1)
            out[i : i + block] = np.sqrt(d.min(axis=1))
        return out


# --------------------------------------------------------------- extraction

def extract_palette(
    pixels: np.ndarray,
    n_colors: int = 32,
    name: str = "extracted",
    iters: int = 40,
    seed: int = 0,
) -> Palette:
    """k-means en OKLab sobre pixeles opacos. Para derivar tu paleta del arte
    que ya tienes en lugar de inventarla."""
    px = np.asarray(pixels).reshape(-1, 3)
    if px.shape[0] == 0:
        raise ValueError("No hay pixeles opacos de los que extraer paleta")
    uniq = np.unique(px, axis=0)
    if uniq.shape[0] <= n_colors:
        return Palette(name=name, colors=uniq.astype(np.uint8))

    lab = srgb_to_oklab(px)
    rng = np.random.default_rng(seed)

    # k-means++ ligero: primer centro aleatorio, resto por distancia^2.
    centers = [lab[rng.integers(lab.shape[0])]]
    d2 = ((lab - centers[0]) ** 2).sum(axis=1)
    for _ in range(n_colors - 1):
        total = d2.sum()
        probs = d2 / total if total > 0 else None
        centers.append(lab[rng.choice(lab.shape[0], p=probs)])
        d2 = np.minimum(d2, ((lab - centers[-1]) ** 2).sum(axis=1))
    C = np.stack(centers)

    for _ in range(iters):
        assign = np.empty(lab.shape[0], dtype=np.int64)
        block = 65536
        for i in range(0, lab.shape[0], block):
            chunk = lab[i : i + block]
            assign[i : i + block] = (
                ((chunk[:, None, :] - C[None, :, :]) ** 2).sum(-1).argmin(1)
            )
        newC = C.copy()
        for k in range(C.shape[0]):
            sel = lab[assign == k]
            if sel.shape[0]:
                newC[k] = sel.mean(axis=0)
        if np.allclose(newC, C, atol=1e-6):
            C = newC
            break
        C = newC

    # Representante real: el pixel sRGB mas cercano a cada centro, para no
    # inventar colores que no existen en el arte original.
    out = []
    for k in range(C.shape[0]):
        sel_mask = None
        block = 65536
        best = None
        best_d = np.inf
        for i in range(0, lab.shape[0], block):
            chunk = lab[i : i + block]
            d = ((chunk - C[k]) ** 2).sum(axis=1)
            j = int(d.argmin())
            if d[j] < best_d:
                best_d = float(d[j])
                best = px[i + j]
        out.append(best)
        del sel_mask
    colors = np.unique(np.stack(out).astype(np.uint8), axis=0)
    return Palette(name=name, colors=colors)
