"""Orquestacion: AssetSpec -> N variantes en disco, con sidecar.

El sidecar es la pieza que convierte esto en una herramienta y no en un script.
Junto a cada PNG queda un JSON con el spec completo, el prompt exacto que se
uso, la seed, el backend con su licencia y la configuracion del PixelPass. Seis
meses despues, con el sidecar puedes regenerar ese sprite exacto, o justificar
de donde salio si alguien pregunta por la licencia de los assets de tu juego.

Lo segundo no es paranoia: si Dark Requiem acaba en Steam, la trazabilidad de
que pesos generaron que arte es exactamente el papel que querras tener escrito.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from .backends.base import Backend
from .metrics import measure
from .palette import Palette
from .pixelpass import PixelPassConfig, run_pixelpass
from .prompts import build_prompt
from .spec import AssetSpec


@dataclass
class Variant:
    index: int
    seed: int
    sprite_path: Path
    sidecar_path: Path
    raw_path: Path | None
    preview_path: Path | None
    colors_before: int
    colors_after: int


def _sidecar(
    spec: AssetSpec,
    backend: Backend,
    cfg: PixelPassConfig,
    palette: Palette,
    prompt: str,
    negative: str,
    seed: int,
    variant: int,
    raw_metrics: dict,
    final_metrics: dict,
) -> dict:
    from . import __version__

    info = backend.info
    return {
        "drag_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "spec": spec.to_dict(),
        "variant": variant,
        "seed": seed,
        "prompt": prompt,
        "negative": negative,
        "negative_efectivo": info.key != "flux2-klein-pixel",
        "backend": {
            "key": info.key,
            "base_model": info.base_model,
            "license": info.license,
            "commercial_ok": info.commercial_ok,
        },
        "pixelpass": {
            "grid": cfg.grid,
            "remove_background": cfg.remove_background,
            "bg_tolerance": cfg.bg_tolerance,
            "bg_key": cfg.bg_key,
            "margin": cfg.margin,
            "alpha_threshold": cfg.alpha_threshold,
            "despeckle": cfg.despeckle,
        },
        "palette": {"name": palette.name, "size": len(palette), "colors": palette.hex_list},
        "metrics_raw": raw_metrics,
        "metrics_final": final_metrics,
    }


def generate_asset(
    spec: AssetSpec,
    backend: Backend,
    palette: Palette,
    out_dir: str | Path,
    cfg: PixelPassConfig | None = None,
    keep_raw: bool = True,
    render_size: int = 1024,
    on_progress=None,
) -> list[Variant]:
    """Genera todas las variantes de un spec y las deja procesadas en disco."""
    cfg = cfg or PixelPassConfig(grid=spec.grid)
    if cfg.grid != spec.grid:
        raise ValueError(
            f"La rejilla del PixelPass ({cfg.grid}) no coincide con la del spec "
            f"({spec.grid}). Es casi siempre un error de invocacion, no una decision."
        )

    if spec.kind == "tile" and cfg.remove_background:
        # Un tile es textura de borde a borde por diseno (ver prompts.py):
        # no hay "sujeto sobre fondo" que recortar, asi que el keying de
        # magenta no tiene nada valido que buscar y termina comiendose
        # trozos de textura real al azar. dataclasses.replace porque
        # PixelPassConfig es frozen y cfg puede venir compartido entre
        # specs de un mismo run de benchmark.
        from dataclasses import replace

        cfg = replace(cfg, remove_background=False)

    prompt, negative = build_prompt(spec)
    root = Path(out_dir) / spec.slug
    root.mkdir(parents=True, exist_ok=True)
    (root / "preview").mkdir(exist_ok=True)
    if keep_raw:
        (root / "raw").mkdir(exist_ok=True)

    results: list[Variant] = []
    for i in range(spec.variants):
        seed = spec.seed_for(i)
        raw = backend.generate(prompt, negative, seed, render_size, render_size)

        raw_path = None
        if keep_raw:
            raw_path = root / "raw" / f"{spec.slug}_v{i}_raw.png"
            raw.save(raw_path)

        res = run_pixelpass(raw, palette, cfg)

        sprite_path = root / f"{spec.slug}_v{i}.png"
        res.image.save(sprite_path)

        preview_path = root / "preview" / f"{spec.slug}_v{i}_x{cfg.preview_scale}.png"
        res.preview.save(preview_path)

        # `path` se cae: en el sidecar seria siempre "<memoria>" y no informa.
        raw_m = measure(raw.convert("RGBA"), palette, target_grid=cfg.grid).as_row()
        fin_m = measure(res.image, palette, target_grid=cfg.grid).as_row()
        raw_m.pop("path", None)
        fin_m.pop("path", None)

        sidecar_path = root / f"{spec.slug}_v{i}.json"
        sidecar_path.write_text(
            json.dumps(
                _sidecar(spec, backend, cfg, palette, prompt, negative, seed, i, raw_m, fin_m),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        v = Variant(
            index=i,
            seed=seed,
            sprite_path=sprite_path,
            sidecar_path=sidecar_path,
            raw_path=raw_path,
            preview_path=preview_path,
            colors_before=res.colors_before,
            colors_after=res.colors_after,
        )
        results.append(v)
        if on_progress:
            on_progress(v)

    return results


def regenerate_from_sidecar(
    sidecar: str | Path, backend: Backend, palette: Palette | None = None
) -> Image.Image:
    """Rehace exactamente una imagen a partir de su sidecar.

    Es la prueba de fuego de la promesa de reproducibilidad: si esto no
    devuelve el mismo pixel, el sidecar es decoracion.
    """
    data = json.loads(Path(sidecar).read_text(encoding="utf-8"))
    spec = AssetSpec.from_dict(data["spec"])
    pal = palette or Palette.load(data["palette"]["name"])
    cfg = PixelPassConfig(**{**data["pixelpass"]})
    raw = backend.generate(data["prompt"], data["negative"], data["seed"], 1024, 1024)
    return run_pixelpass(raw, pal, cfg).image
