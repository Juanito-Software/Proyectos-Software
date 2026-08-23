"""AssetSpec: la unidad reproducible del generador.

La idea central del proyecto: nunca se genera desde un prompt suelto. Se genera
desde un spec tipado que se serializa a JSON y viaja junto al PNG. Con el spec y
la seed, cualquier asset se puede regenerar identico meses despues.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Literal

Kind = Literal["character", "enemy", "item", "tile", "prop"]
Facing = Literal["S", "N", "E", "W", "SE", "SW", "NE", "NW"]

SPEC_VERSION = 1


@dataclass(frozen=True, slots=True)
class AssetSpec:
    """Descripcion completa y reproducible de un asset a generar."""

    kind: Kind
    subject: str
    facing: Facing = "S"
    grid: int = 32
    palette: str = "dark_requiem_32"
    seed: int | None = None
    variants: int = 4
    backend: str = "sdxl-pixelart"
    extra_prompt: str = ""
    extra_negative: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    spec_version: int = SPEC_VERSION

    def __post_init__(self) -> None:
        if self.grid < 8 or self.grid > 256:
            raise ValueError(f"grid fuera de rango razonable: {self.grid}")
        if self.grid & (self.grid - 1) != 0:
            # No es un error fatal, pero en Unity las potencias de 2 evitan
            # sorpresas con atlas y compresion.
            pass
        if self.variants < 1:
            raise ValueError("variants debe ser >= 1")
        if not self.subject.strip():
            raise ValueError("subject vacio")

    # ---------------------------------------------------------------- ids

    #: Campos que NO forman parte de la identidad del asset. `variants` es una
    #: cantidad de produccion, no una propiedad de lo que se esta generando:
    #: pedir 4 o 6 variantes del mismo caballero no lo convierte en otro
    #: caballero, y meterlo en el hash renombraria la carpeta entera cada vez
    #: que subes el numero.
    _NO_IDENTITY = ("variants", "spec_version")

    @property
    def fingerprint(self) -> str:
        """Hash estable del spec. Dos specs iguales -> mismo asset esperado."""
        d = {k: v for k, v in self.to_dict().items() if k not in self._NO_IDENTITY}
        payload = json.dumps(d, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    @property
    def slug(self) -> str:
        """Nombre de archivo legible: enemy_skeleton-knight_S_32_a1b2c3d4e5f6."""
        safe = "".join(
            c if c.isalnum() else "-" for c in self.subject.lower()
        ).strip("-")
        while "--" in safe:
            safe = safe.replace("--", "-")
        return f"{self.kind}_{safe[:40]}_{self.facing}_{self.grid}_{self.fingerprint}"

    def seed_for(self, variant: int) -> int:
        """Seed derivada y determinista por variante.

        Si el spec no trae seed, se deriva del fingerprint: sigue siendo
        reproducible sin obligar a escribir numeros a mano.
        """
        base = self.seed
        if base is None:
            base = int(self.fingerprint, 16) % (2**31)
        return (base + variant * 7919) % (2**31)

    # ------------------------------------------------------------ serial

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(self.tags)
        return d

    def to_json(self, path: str | Path | None = None) -> str:
        text = json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AssetSpec:
        d = dict(d)
        d.pop("spec_version", None)
        if "tags" in d and d["tags"] is not None:
            d["tags"] = tuple(d["tags"])
        return cls(**d)

    @classmethod
    def from_json(cls, path: str | Path) -> AssetSpec:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def with_(self, **kwargs: Any) -> AssetSpec:
        return replace(self, **kwargs)
