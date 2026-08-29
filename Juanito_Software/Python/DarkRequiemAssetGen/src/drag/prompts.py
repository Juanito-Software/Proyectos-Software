"""PromptBuilder: plantillas por tipo de asset, no un prompt generico.

Los negativos hacen aqui mas trabajo que los positivos. Sin ellos, cualquier
LoRA de pixel art deriva hacia semirrealismo en cuanto el sujeto se complica:
aparecen sombras suaves, profundidad de campo y bordes difuminados que el
PixelPass tendra que destruir despues, perdiendo detalle util por el camino.
"""

from __future__ import annotations

from .spec import AssetSpec

FACING_WORDS = {
    "S": "front view, facing the viewer",
    "N": "back view, seen from behind",
    "E": "side view, facing right",
    "W": "side view, facing left",
    "SE": "three-quarter front view, turned right",
    "SW": "three-quarter front view, turned left",
    "NE": "three-quarter back view, turned right",
    "NW": "three-quarter back view, turned left",
}

BASE_STYLE = (
    "pixel art sprite, {grid}x{grid} pixel grid, limited palette, "
    "hard edges, no anti-aliasing, flat shading, dark fantasy, "
    "grim medieval, high contrast readable silhouette"
)

KIND_TEMPLATES = {
    "character": "full body character sprite of {subject}, {facing}, centered, standing idle pose",
    "enemy": "full body enemy sprite of {subject}, {facing}, centered, menacing idle pose",
    "item": "single inventory item icon of {subject}, centered, isolated object, no character",
    "tile": "seamless terrain tile of {subject}, top-down, tileable, no border",
    "prop": "single environment prop of {subject}, {facing}, centered, isolated object",
}

BASE_NEGATIVE = (
    "blurry, anti-aliased, smooth gradient, soft shading, depth of field, "
    "3d render, photorealistic, realistic, painterly, oil painting, "
    "watermark, signature, text, ui, frame, border, drop shadow, "
    "multiple characters, cropped, out of frame, jpeg artifacts, noise"
)

KIND_NEGATIVE = {
    "character": "extra limbs, deformed hands, blurred face",
    "enemy": "extra limbs, deformed anatomy",
    "item": "hands holding it, character, background scenery",
    "tile": "object in center, character, isolated subject, vignette",
    "prop": "character, hands, crowd",
}

BACKGROUND_HINT = "plain solid magenta background, isolated on flat background"


def build_prompt(spec: AssetSpec) -> tuple[str, str]:
    """Devuelve (positivo, negativo) para un spec dado."""
    template = KIND_TEMPLATES[spec.kind]
    facing = FACING_WORDS.get(spec.facing, FACING_WORDS["S"])
    body = template.format(subject=spec.subject, facing=facing)
    style = BASE_STYLE.format(grid=spec.grid)

    parts = [body, style]
    # BACKGROUND_HINT pide "isolated on flat background": tiene sentido para
    # un sujeto recortable (character/enemy/item/prop), pero contradice
    # directamente la plantilla de "tile" ("seamless ... no border") y su
    # propio negativo ("isolated subject, vignette"). Meter las dos cosas en
    # el mismo prompt es lo que produce texturas de tile inconsistentes: a
    # veces el modelo obedece el hint de fondo magenta aislado y deja solo un
    # parche minusculo de textura real.
    if spec.kind != "tile":
        parts.append(BACKGROUND_HINT)
    if spec.tags:
        parts.append(", ".join(spec.tags))
    if spec.extra_prompt:
        parts.append(spec.extra_prompt)
    positive = ", ".join(p for p in parts if p)

    neg_parts = [BASE_NEGATIVE, KIND_NEGATIVE.get(spec.kind, "")]
    if spec.extra_negative:
        neg_parts.append(spec.extra_negative)
    negative = ", ".join(p for p in neg_parts if p)

    return positive, negative
