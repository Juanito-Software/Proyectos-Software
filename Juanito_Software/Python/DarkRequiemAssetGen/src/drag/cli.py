"""CLI.

    drag pixelpass in.png -o out/            # una imagen o una carpeta entera
    drag metrics out/ --csv bench.csv        # metricas objetivas a CSV
    drag palette extract arte/ -n 32 -o palettes/mia.json
    drag palette show dark_requiem_32
    drag prompt spec.json                    # ver que prompt saldria del spec
    drag backends                            # catalogo con licencia y VRAM
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from .backends import catalog, get_backend
from .bench import (
    RESULTS,
    RUBRIC,
    load_matrix,
    merge_rubric,
    run_benchmark,
    summarize,
    write_rubric_template,
)
from .env import advice, probe
from .packager import export_for_unity
from .metrics import measure, write_csv
from .palette import Palette, extract_palette
from .pipeline import generate_asset
from .pixelpass import PixelPassConfig, run_pixelpass
from .prompts import build_prompt
from .spec import AssetSpec

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def _iter_images(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        p
        for p in target.rglob("*")
        if p.suffix.lower() in IMG_EXT and "preview" not in p.parts
    )


# ------------------------------------------------------------------ cmds

def cmd_pixelpass(args: argparse.Namespace) -> int:
    palette = Palette.load(args.palette)
    cfg = PixelPassConfig(
        grid=args.grid,
        remove_background=not args.keep_background,
        bg_tolerance=args.bg_tolerance,
        bg_key=args.bg_key,
        margin=args.margin,
        alpha_threshold=args.alpha_threshold,
        despeckle=not args.no_despeckle,
        preview_scale=args.preview_scale,
    )
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = _iter_images(Path(args.input))
    if not files:
        print(f"No hay imagenes en {args.input}", file=sys.stderr)
        return 1

    for f in files:
        res = run_pixelpass(f, palette, cfg)
        dst = out_dir / f"{f.stem}_{cfg.grid}.png"
        res.image.save(dst)
        if args.preview_scale > 1:
            # Los previews van a su propia carpeta: si conviven con los sprites
            # reales, `drag metrics` los mide tambien y el CSV del benchmark
            # cuenta cada asset dos veces.
            prev_dir = out_dir / "preview"
            prev_dir.mkdir(exist_ok=True)
            res.preview.save(prev_dir / f"{f.stem}_{cfg.grid}_x{args.preview_scale}.png")
        print(
            f"{f.name:40s} escala detectada={res.detected_scale:2d}  "
            f"colores {res.colors_before:5d} -> {res.colors_after:3d}  ->  {dst.name}"
        )
    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    palette = Palette.load(args.palette)
    rows = [measure(f, palette, target_grid=args.grid) for f in _iter_images(Path(args.input))]
    if not rows:
        print("Sin imagenes que medir", file=sys.stderr)
        return 1

    head = f"{'archivo':30s} {'colores':>8s} {'fuera%':>8s} {'alpha%':>8s} {'huerf%':>8s} {'rejilla':>8s}"
    print(head)
    print("-" * len(head))
    for r in rows:
        print(
            f"{Path(r.path).name[:30]:30s} {r.unique_colors:8d} {r.offpalette_pct:8.2f} "
            f"{r.soft_alpha_pct:8.2f} {r.orphan_color_pct:8.2f} {r.grid_adherence:8.2f}"
        )
    if args.csv:
        write_csv(rows, args.csv)
        print(f"\nCSV escrito en {args.csv}")
    return 0


def cmd_palette_extract(args: argparse.Namespace) -> int:
    px = []
    for f in _iter_images(Path(args.input)):
        arr = np.array(Image.open(f).convert("RGBA"))
        px.append(arr[..., :3][arr[..., 3] > 0].reshape(-1, 3))
    if not px:
        print("Sin imagenes de las que extraer", file=sys.stderr)
        return 1
    pal = extract_palette(np.concatenate(px), n_colors=args.n, name=Path(args.output).stem)
    pal.save(args.output)
    print(f"Paleta de {len(pal)} colores escrita en {args.output}")
    for h in pal.hex_list:
        print("  ", h)
    return 0


def cmd_palette_show(args: argparse.Namespace) -> int:
    pal = Palette.load(args.name)
    print(f"{pal.name}: {len(pal)} colores")
    if pal.ramps:
        for ramp, colors in pal.ramps.items():
            print(f"  {ramp:12s} {' '.join(colors)}")
    else:
        for h in pal.hex_list:
            print("  ", h)
    if args.swatch:
        side = 32
        cols = 8
        rows = (len(pal) + cols - 1) // cols
        img = Image.new("RGB", (cols * side, rows * side), (0, 0, 0))
        arr = np.array(img)
        for i, c in enumerate(pal.colors):
            y, x = divmod(i, cols)
            arr[y * side : (y + 1) * side, x * side : (x + 1) * side] = c
        Image.fromarray(arr).save(args.swatch)
        print(f"Muestrario en {args.swatch}")
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    spec = AssetSpec.from_json(args.spec)
    pos, neg = build_prompt(spec)
    print(f"slug        : {spec.slug}")
    print(f"fingerprint : {spec.fingerprint}")
    print(f"seeds       : {[spec.seed_for(i) for i in range(spec.variants)]}")
    print(f"\nPOSITIVO:\n{pos}\n\nNEGATIVO:\n{neg}")
    return 0


def cmd_backends(args: argparse.Namespace) -> int:
    print(f"{'clave':24s} {'licencia':30s} {'comercial':10s} {'VRAM':>6s}  estado")
    print("-" * 86)
    for b, implemented in catalog():
        com = {True: "si", False: "no", None: "VERIFICAR"}[b.commercial_ok]
        estado = "implementado" if implemented else "solo declarado"
        print(f"{b.key:24s} {b.license:30s} {com:10s} {b.min_vram_gb:5.1f}G  {estado}")
        print(f"    {b.display_name}")
        print(f"    {b.notes}\n")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    env = probe()
    print("Entorno")
    print(f"  torch      : {env.torch_version or 'NO INSTALADO'}")
    print(f"  diffusers  : {env.diffusers_version or 'NO INSTALADO'}")
    print(f"  CUDA       : {'si' if env.has_cuda else 'no'}")
    if env.has_cuda:
        print(f"  GPU        : {env.device_name}")
        print(f"  VRAM       : {env.free_gb:.1f} GB libres de {env.vram_gb:.1f} GB "
              f"({env.ocupada_gb:.1f} GB en uso por otros programas)")
        print(f"  BF16       : {'si' if env.bf16_ok else 'no'}")
    print(f"  perfil     : {env.tier}")
    print("\nRecomendaciones")
    for line in advice(env):
        print(f"  - {line}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    spec = AssetSpec.from_json(args.spec)
    if args.variants:
        spec = spec.with_(variants=args.variants)
    if args.seed is not None:
        spec = spec.with_(seed=args.seed)

    backend_key = args.backend or spec.backend
    backend = get_backend(backend_key)
    if args.guidance is not None and hasattr(backend, "guidance"):
        backend.guidance = args.guidance
    if args.steps is not None and hasattr(backend, "steps"):
        backend.steps = args.steps
    palette = Palette.load(args.palette or spec.palette)
    # Por defecto se keyea magenta: PromptBuilder lo pide explicitamente en
    # cada prompt, asi que adivinar el fondo aqui seria tirar informacion que
    # ya tenemos. Si el modelo lo ignora, run_pixelpass reintenta adivinando.
    cfg = PixelPassConfig(
        grid=spec.grid, preview_scale=args.preview_scale, bg_key=args.bg_key
    )

    print(f"spec     : {spec.slug}")
    print(f"backend  : {backend.info.display_name}")
    print(f"licencia : {backend.info.license} (comercial: {backend.info.commercial_ok})")
    print(f"variantes: {spec.variants}  seeds: {[spec.seed_for(i) for i in range(spec.variants)]}")
    print("cargando backend...", flush=True)
    backend.load()

    def _tick(v):
        print(
            f"  v{v.index}  seed={v.seed:<12d} colores {v.colors_before:5d} -> "
            f"{v.colors_after:3d}  {v.sprite_path.name}",
            flush=True,
        )

    try:
        generate_asset(
            spec,
            backend,
            palette,
            out_dir=args.output,
            cfg=cfg,
            keep_raw=not args.no_raw,
            render_size=args.render_size,
            on_progress=_tick,
        )
    finally:
        backend.unload()

    print(f"\nListo en {Path(args.output) / spec.slug}")
    return 0


def cmd_bench_run(args: argparse.Namespace) -> int:
    specs, seeds, nombre = load_matrix(args.matrix)
    backends = [b.strip() for b in args.backends.split(",") if b.strip()]
    palette = Palette.load(args.palette)
    total = len(specs) * len(seeds) * len(backends)
    print(f"matriz   : {nombre} ({len(specs)} specs x {len(seeds)} seeds)")
    print(f"backends : {', '.join(backends)}")
    print(f"total    : {total} imagenes\n")
    csv_path = run_benchmark(
        specs, seeds, backends, palette,
        out_dir=args.output, grid=args.grid, render_size=args.render_size,
        keep_raw=args.keep_raw, bg_key=args.bg_key,
    )
    print(f"\nCSV: {csv_path}")
    print(f"Siguiente: drag bench report {csv_path}")
    return 0


def cmd_bench_report(args: argparse.Namespace) -> int:
    filas = summarize(args.csv)
    if not filas:
        print("CSV vacio", file=sys.stderr)
        return 1
    cab = (f"{'backend':20s} {'img':>4s} {'s/img':>7s} {'total':>8s} {'cols':>6s} "
           f"{'fuera%':>8s} {'huerf%':>8s} {'cobert':>7s} {'fallos':>7s}")
    print(cab)
    print("-" * len(cab))
    for f in filas:
        print(
            f"{f.backend:20s} {f.imagenes:4d} {f.seg_mediana:7.2f} {f.seg_total:8.1f} "
            f"{f.colores_finales_mediana:6.1f} {f.fuera_paleta_crudo_mediana:8.2f} "
            f"{f.huerfanos_crudo_mediana:8.2f} {f.cobertura_mediana:7.3f} "
            f"{f.sospechosas:3d} ({f.tasa_fallo_pct:.0f}%)"
        )
    print("\nEstas cifras miden aptitud mecanica, no calidad artistica.")
    print("Para decidir hace falta la rubrica: drag bench rubric <csv>")
    if args.csv_out:
        import csv as _csv
        from dataclasses import asdict as _asdict
        with open(args.csv_out, "w", newline="", encoding="utf-8") as fh:
            w = _csv.DictWriter(fh, fieldnames=list(_asdict(filas[0]).keys()))
            w.writeheader()
            for f in filas:
                w.writerow(_asdict(f))
        print(f"\nResumen escrito en {args.csv_out}")
    return 0


def cmd_bench_rubric(args: argparse.Namespace) -> int:
    dst = Path(args.output or Path(args.csv).parent / RUBRIC)
    if args.merge:
        filas = merge_rubric(args.csv, dst)
        cab = f"{'backend':20s} {'kind':10s} {'sujeto':34s} {'rubrica':>9s} {'s/img':>7s}"
        print(cab)
        print("-" * len(cab))
        for f in sorted(filas, key=lambda r: -(r["rubrica_total"] or -1)):
            tot = "sin puntuar" if f["rubrica_total"] is None else f"{f['rubrica_total']:.0f}/{f['rubrica_max']}"
            print(f"{f['backend']:20s} {f['kind']:10s} {f['subject'][:34]:34s} {tot:>9s} {f['seg_mediana']:7.2f}")
        return 0
    write_rubric_template(args.csv, dst)
    print(f"Plantilla en {dst}")
    print("Puntua de 0 a 3 cada criterio mirando las seeds juntas, y luego:")
    print(f"  drag bench rubric {args.csv} --merge")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    files = _iter_images(Path(args.input))
    if not files:
        print(f"No hay sprites en {args.input}", file=sys.stderr)
        return 1
    pivot = tuple(float(v) for v in args.pivot.split(","))
    png, js, meta = export_for_unity(
        files,
        out_png=args.output,
        names=[f.stem for f in files],
        columns=args.columns,
        padding=args.padding,
        power_of_two=not args.no_pot,
        pixels_per_unit=args.ppu,
        pivot=pivot,
    )
    from PIL import Image as _I
    w, h = _I.open(png).size
    print(f"{len(files)} sprites -> atlas {w}x{h}")
    print(f"  {png}")
    print(f"  {js}")
    print(f"  {meta}")
    print("\nCopia el .png Y el .png.meta juntos a Assets/. Sin el .meta, Unity")
    print("importa el atlas con sus ajustes por defecto y se ve borroso.")
    return 0


# ------------------------------------------------------------------ parser

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="drag", description="Dark Requiem Asset Generator")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("pixelpass", help="Convertir imagenes en pixel art real")
    pp.add_argument("input")
    pp.add_argument("-o", "--output", default="out")
    pp.add_argument("-g", "--grid", type=int, default=128)
    pp.add_argument("-p", "--palette", default="dark_requiem_32")
    pp.add_argument("--keep-background", action="store_true")
    pp.add_argument("--bg-tolerance", type=float, default=0.10)
    pp.add_argument("--bg-key", help="Color de fondo a eliminar, p.ej. #FF00FF. "
                                     "Sin esto se adivina por el borde.")
    pp.add_argument("--margin", type=float, default=0.06)
    pp.add_argument("--alpha-threshold", type=float, default=0.5)
    pp.add_argument("--no-despeckle", action="store_true")
    pp.add_argument("--preview-scale", type=int, default=8)
    pp.set_defaults(func=cmd_pixelpass)

    m = sub.add_parser("metrics", help="Metricas objetivas + CSV")
    m.add_argument("input")
    m.add_argument("-p", "--palette", default="dark_requiem_32")
    m.add_argument("-g", "--grid", type=int, default=128)
    m.add_argument("--csv")
    m.set_defaults(func=cmd_metrics)

    pal = sub.add_parser("palette", help="Trabajar con paletas")
    psub = pal.add_subparsers(dest="palcmd", required=True)

    pe = psub.add_parser("extract", help="Derivar paleta de tu arte existente")
    pe.add_argument("input")
    pe.add_argument("-n", type=int, default=32)
    pe.add_argument("-o", "--output", default="palettes/extracted.json")
    pe.set_defaults(func=cmd_palette_extract)

    ps = psub.add_parser("show", help="Ver una paleta")
    ps.add_argument("name", nargs="?", default="dark_requiem_32")
    ps.add_argument("--swatch", help="Escribir un PNG de muestrario")
    ps.set_defaults(func=cmd_palette_show)

    pr = sub.add_parser("prompt", help="Ver el prompt que genera un spec")
    pr.add_argument("spec")
    pr.set_defaults(func=cmd_prompt)

    b = sub.add_parser("backends", help="Catalogo de modelos con licencia y VRAM")
    b.set_defaults(func=cmd_backends)

    doc = sub.add_parser("doctor", help="Que puede hacer esta maquina y como")
    doc.set_defaults(func=cmd_doctor)

    g = sub.add_parser("generate", help="spec -> sprites procesados + sidecar")
    g.add_argument("spec")
    g.add_argument("-o", "--output", default="assets")
    g.add_argument("-b", "--backend", help="Sobrescribe el backend del spec")
    g.add_argument("-p", "--palette", help="Sobrescribe la paleta del spec")
    g.add_argument("-n", "--variants", type=int, help="Sobrescribe el numero de variantes")
    g.add_argument("--seed", type=int, help="Fija la seed base")
    g.add_argument("--render-size", type=int, default=1024)
    g.add_argument("--preview-scale", type=int, default=8)
    g.add_argument("--bg-key", default="#FF00FF",
                   help="Color de fondo a eliminar. El prompt lo pide magenta.")
    g.add_argument("--no-raw", action="store_true", help="No conservar los 1024x1024")
    g.add_argument("--guidance", type=float,
                   help="Sobrescribe el guidance_scale del backend (SDXL: 7.5 por "
                        "defecto). Subirlo a 9-11 fuerza mas el negativo cuando el "
                        "modelo insiste en ignorar un rasgo pedido, p.ej. armadura "
                        "que no deberia aparecer.")
    g.add_argument("--steps", type=int, help="Sobrescribe num_inference_steps del backend")
    g.set_defaults(func=cmd_generate)

    bch = sub.add_parser("bench", help="Fase 2: benchmark de backends")
    bsub = bch.add_subparsers(dest="benchcmd", required=True)

    br = bsub.add_parser("run", help="Ejecutar la matriz (reanudable)")
    br.add_argument("-m", "--matrix", default="bench/matrix.json")
    br.add_argument("-b", "--backends", default="mock")
    br.add_argument("-o", "--output", default="bench/out")
    br.add_argument("-p", "--palette", default="dark_requiem_32")
    br.add_argument("-g", "--grid", type=int, default=128)
    br.add_argument("--render-size", type=int, default=1024)
    br.add_argument("--bg-key", default="#FF00FF")
    br.add_argument("--keep-raw", action="store_true")
    br.set_defaults(func=cmd_bench_run)

    bp = bsub.add_parser("report", help="Resumen agregado por backend")
    bp.add_argument("csv", nargs="?", default=f"bench/out/{RESULTS}")
    bp.add_argument("--csv-out")
    bp.set_defaults(func=cmd_bench_report)

    bu = bsub.add_parser("rubric", help="Plantilla de rubrica manual, o fusion")
    bu.add_argument("csv", nargs="?", default=f"bench/out/{RESULTS}")
    bu.add_argument("-o", "--output")
    bu.add_argument("--merge", action="store_true")
    bu.set_defaults(func=cmd_bench_rubric)

    pk = sub.add_parser("pack", help="Fase 3: atlas + .meta de Unity")
    pk.add_argument("input")
    pk.add_argument("-o", "--output", default="unity/atlas.png")
    pk.add_argument("-c", "--columns", type=int)
    pk.add_argument("--padding", type=int, default=0)
    pk.add_argument("--no-pot", action="store_true", help="No redondear a potencia de 2")
    pk.add_argument("--ppu", type=int, default=128, help="Pixels per unit")
    pk.add_argument("--pivot", default="0.5,0.0", help="Pivote; 0.5,0.0 = pies")
    pk.set_defaults(func=cmd_pack)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
