"""Fase 3: atlas + `.meta` de Unity.

Aqui es donde el proyecto deja de ser "un generador de PNGs" y se convierte en
algo que ahorra tiempo de verdad. Importar 60 sprites sueltos a Unity y
configurarlos a mano —Point filter, sin compresion, sin mipmaps, pivote,
pixels per unit— son 60 oportunidades de que uno se quede en Bilinear y salga
borroso en la build.

Los cuatro ajustes que de verdad importan para pixel art, y que este `.meta`
fija de una vez:

- `filterMode: 0` (Point). El unico responsable de que tu sprite se vea nitido.
- `textureCompression: 0` (sin comprimir). DXT sobre pixel art de paleta cerrada
  destroza justo los colores que te has molestado en cuantizar.
- `enableMipMap: 0`. Los mipmaps en 2D no aportan y emborronan a distancia.
- `spriteMeshType: 0` (FullRect). Con Tight, Unity recorta el mesh al alfa y
  te desalinea el pivote entre frames de una animacion.

**Aviso honesto**: el formato del `.meta` varia entre versiones de Unity. Este
esta escrito contra el esquema de Unity 2021-2023 LTS y deberia importar bien,
pero verifica el primero antes de generar sesenta. Si tu version reordena
campos, Unity los reescribe sola al reimportar; lo que no perdona es un GUID
duplicado, y por eso aqui el GUID se deriva del contenido.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class Frame:
    name: str
    x: int          # origen ARRIBA-izquierda, como la imagen
    y: int
    w: int
    h: int

    def unity_y(self, sheet_height: int) -> int:
        """Unity mide el rect desde ABAJO. Este flip es el bug clasico de todo
        empaquetador casero: el atlas se ve bien y los sprites salen del frame
        equivocado, casi siempre el simetrico vertical."""
        return sheet_height - (self.y + self.h)


@dataclass
class Sheet:
    image: Image.Image
    frames: list[Frame]
    cell: tuple[int, int]
    padding: int

    @property
    def size(self) -> tuple[int, int]:
        return self.image.size


# ------------------------------------------------------------------ packing

def _next_pot(n: int) -> int:
    return 1 << (n - 1).bit_length()


def pack_sprites(
    sources: list[str | Path | Image.Image],
    names: list[str] | None = None,
    columns: int | None = None,
    padding: int = 0,
    power_of_two: bool = True,
) -> Sheet:
    """Atlas en rejilla uniforme.

    Rejilla y no bin-packing a proposito: con sprites del mismo tamano el
    packing optimo ES la rejilla, y ademas mantiene el atlas legible cuando lo
    abres en Aseprite para retocar un frame a mano. Un atlas apretado por un
    algoritmo es imposible de editar.
    """
    imgs: list[Image.Image] = []
    for s in sources:
        imgs.append(s.convert("RGBA") if isinstance(s, Image.Image) else Image.open(s).convert("RGBA"))
    if not imgs:
        raise ValueError("No hay sprites que empaquetar")

    anchos = {im.size for im in imgs}
    if len(anchos) > 1:
        raise ValueError(
            f"Los sprites tienen tamanos distintos: {sorted(anchos)}. "
            "El atlas en rejilla exige uniformidad; pasa todo por el mismo "
            "PixelPass antes de empaquetar."
        )

    cw, ch = imgs[0].size
    n = len(imgs)
    cols = columns or math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    step_x, step_y = cw + padding, ch + padding
    w = cols * step_x - (padding if padding else 0)
    h = rows * step_y - (padding if padding else 0)
    if power_of_two:
        w, h = _next_pot(w), _next_pot(h)

    sheet = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    frames: list[Frame] = []
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        x, y = c * step_x, r * step_y
        sheet.paste(im, (x, y))
        nombre = names[i] if names else f"sprite_{i:03d}"
        frames.append(Frame(name=nombre, x=x, y=y, w=cw, h=ch))

    return Sheet(image=sheet, frames=frames, cell=(cw, ch), padding=padding)


def write_frames_json(sheet: Sheet, path: str | Path) -> Path:
    """Formato propio, legible. Sirve para cualquier motor que no sea Unity y
    para depurar el atlas sin abrir Unity."""
    path = Path(path)
    payload = {
        "size": {"w": sheet.size[0], "h": sheet.size[1]},
        "cell": {"w": sheet.cell[0], "h": sheet.cell[1]},
        "padding": sheet.padding,
        "origen": "arriba-izquierda",
        "frames": [asdict(f) for f in sheet.frames],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# -------------------------------------------------------------- unity .meta

def _guid(seed: str) -> str:
    """GUID determinista de 32 hex. Derivarlo del contenido —y no de un
    random— significa que reimportar el mismo atlas no rompe las referencias
    que ya tengas en escenas y prefabs."""
    return hashlib.md5(seed.encode("utf-8")).hexdigest()


def _internal_id(seed: str) -> int:
    """int64 con signo, estable. Unity los usa para referenciar cada subsprite
    dentro del asset; si cambian, las referencias existentes se rompen."""
    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16], 16)
    return h - (1 << 63) if h >= (1 << 63) else h


def unity_meta(
    sheet: Sheet,
    texture_name: str,
    pixels_per_unit: int = 128,
    pivot: tuple[float, float] = (0.5, 0.0),
    max_texture_size: int = 2048,
) -> str:
    """Genera el contenido del `.meta`.

    El pivote por defecto es (0.5, 0.0) —centro abajo— y no (0.5, 0.5). Para
    personajes sobre un tilemap, el pivote en los pies es lo que hace que el
    sprite se apoye en el suelo y que el orden de dibujado por Y funcione sin
    offsets magicos en cada prefab. Para items e iconos querras (0.5, 0.5).
    """
    w, h = sheet.size
    tex_guid = _guid(f"{texture_name}:{w}x{h}:{len(sheet.frames)}")
    px, py = pivot
    # alignment 9 = Custom. Cualquier otro valor ignora el pivote de abajo.
    alignment = 9

    id_table = []
    sprites = []
    for f in sheet.frames:
        sid = _guid(f"{texture_name}:{f.name}")
        iid = _internal_id(f"{texture_name}:{f.name}")
        id_table.append(f"  - first:\n      213: {iid}\n    second: {f.name}")
        sprites.append(
            "\n".join(
                [
                    "    - serializedVersion: 2",
                    f"      name: {f.name}",
                    "      rect:",
                    "        serializedVersion: 2",
                    f"        x: {f.x}",
                    f"        y: {f.unity_y(h)}",
                    f"        width: {f.w}",
                    f"        height: {f.h}",
                    f"      alignment: {alignment}",
                    f"      pivot: {{x: {px}, y: {py}}}",
                    "      border: {x: 0, y: 0, z: 0, w: 0}",
                    "      outline: []",
                    "      physicsShape: []",
                    "      tessellationDetail: 0",
                    "      bones: []",
                    f"      spriteID: {sid}",
                    f"      internalID: {iid}",
                    "      vertices: []",
                    "      indices: ",
                    "      edges: []",
                    "      weights: []",
                ]
            )
        )

    tabla = "\n".join(id_table) if id_table else " {}"
    cuerpo = "\n".join(sprites)

    return f"""fileFormatVersion: 2
guid: {tex_guid}
TextureImporter:
  internalIDToNameTable:
{tabla}
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMasterTextureLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: {max_texture_size}
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 2
  spriteExtrude: 1
  spriteMeshType: 0
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: {pixels_per_unit}
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: {max_texture_size}
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites:
{cuerpo}
    outline: []
    physicsShape: []
    bones: []
    spriteID:
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  spritePackingTag:
  pSDRemoveMatte: 0
  pSDShowRemoveMatteOption: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def export_for_unity(
    sources: list[str | Path | Image.Image],
    out_png: str | Path,
    names: list[str] | None = None,
    columns: int | None = None,
    padding: int = 0,
    power_of_two: bool = True,
    pixels_per_unit: int = 128,
    pivot: tuple[float, float] = (0.5, 0.0),
) -> tuple[Path, Path, Path]:
    """Atlas + frames.json + .meta. Devuelve las tres rutas."""
    sheet = pack_sprites(sources, names, columns, padding, power_of_two)
    png = Path(out_png)
    png.parent.mkdir(parents=True, exist_ok=True)
    sheet.image.save(png)

    js = write_frames_json(sheet, png.with_suffix(".frames.json"))
    meta = png.with_suffix(png.suffix + ".meta")
    meta.write_text(
        unity_meta(sheet, png.name, pixels_per_unit=pixels_per_unit, pivot=pivot),
        encoding="utf-8",
    )
    return png, js, meta
