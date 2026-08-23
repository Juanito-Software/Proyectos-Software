"""Backend simulado. No descarga nada, no necesita GPU, y es determinista.

Por que existe un backend falso en un proyecto cuyo objetivo es generar arte:
porque todo lo que rodea al modelo — el spec, los prompts, el PixelPass, el
sidecar, el nombrado de archivos, el CLI — tiene que poder probarse sin cargar
12 GB de pesos. Sin esto, cada cambio en el pipeline exige una GPU libre y tres
minutos de espera, y las pruebas dejan de ejecutarse.

Ademas simula el problema, no la solucion: produce 1024x1024 con degradados
continuos, bordes antialiaseados y fondo solido. Es decir, produce exactamente
la clase de imagen que el PixelPass tiene que arreglar.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .base import Backend, BackendInfo, register

# Magenta: el mismo color que PromptBuilder pide en BACKGROUND_HINT. Simular
# un fondo gris seria simular un problema que nuestro propio prompt evita.
_BG = (255, 0, 255)


class MockBackend(Backend):
    info = BackendInfo(
        key="mock",
        display_name="Mock (sin modelo, determinista)",
        base_model="-",
        license="-",
        commercial_ok=True,
        min_vram_gb=0.0,
        notes="Simula la salida cruda de un difusor: 1024x1024, antialias, "
              "degradados y fondo solido. Para pruebas y CI.",
    )

    def load(self) -> None:
        return None

    def generate(
        self,
        prompt: str,
        negative: str,
        seed: int,
        width: int = 1024,
        height: int = 1024,
    ) -> Image.Image:
        rng = np.random.default_rng(seed)

        mask = Image.new("L", (width, height), 0)
        d = ImageDraw.Draw(mask)
        cx, cy = width // 2, height // 2

        # Una silueta compuesta: cabeza, torso y un par de apendices. Las
        # proporciones dependen de la seed, asi que dos seeds distintas dan
        # siluetas distintas y la misma seed da siempre la misma.
        head_r = int(rng.integers(width // 10, width // 6))
        d.ellipse([cx - head_r, cy - head_r * 3, cx + head_r, cy - head_r], fill=255)
        tw = int(rng.integers(width // 6, width // 3))
        d.polygon(
            [
                (cx - tw, cy - head_r),
                (cx + tw, cy - head_r),
                (cx + tw + rng.integers(0, 60), cy + height // 4),
                (cx - tw - rng.integers(0, 60), cy + height // 4),
            ],
            fill=255,
        )
        for side in (-1, 1):
            lx = cx + side * int(tw * 0.5)
            d.rectangle(
                [lx - 45, cy + height // 4, lx + 45, cy + int(height * 0.36)], fill=255
            )
        if rng.random() > 0.4:  # arma
            sx = cx + tw + 40
            d.rectangle([sx, cy - height // 3, sx + 40, cy + height // 8], fill=255)

        mask = mask.filter(ImageFilter.GaussianBlur(3.0))

        # Relleno con degradado continuo: el enemigo natural del pixel art.
        c0 = rng.integers(10, 70, size=3).astype(np.float64)
        c1 = rng.integers(120, 235, size=3).astype(np.float64)
        yy, xx = np.mgrid[0:height, 0:width]
        ang = float(rng.uniform(0, np.pi))
        t = xx * np.cos(ang) + yy * np.sin(ang)
        t = (t - t.min()) / max(1e-6, t.max() - t.min())
        rgb = c0[None, None, :] * (1 - t[..., None]) + c1[None, None, :] * t[..., None]

        m = np.asarray(mask, dtype=np.float64) / 255.0
        bg = np.array(_BG, dtype=np.float64)
        out = rgb * m[..., None] + bg[None, None, :] * (1 - m[..., None])
        out = out + rng.normal(0, 2.0, out.shape)  # ruido tipo compresion
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGB")


@register("mock")
def _factory() -> Backend:
    return MockBackend()
