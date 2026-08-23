"""Interfaz de backend. Fase 2 del roadmap.

Todo lo que hay debajo de esta interfaz es intercambiable: SDXL + LoRA,
FLUX.2 klein, una API de pago. Todo lo que hay encima (spec, prompts,
PixelPass, metricas, packager) no cambia. Esa separacion es lo que hace
posible el benchmark sin reescribir el programa cinco veces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from PIL import Image


@dataclass(frozen=True)
class BackendInfo:
    key: str
    display_name: str
    base_model: str
    license: str
    commercial_ok: bool | None       # None = requiere leer la licencia a mano
    min_vram_gb: float
    notes: str = ""


class Backend(ABC):
    """Contrato minimo. Una imagen cruda a partir de un prompt y una seed."""

    info: BackendInfo

    @abstractmethod
    def load(self) -> None:
        """Carga pesos. Separado de __init__ para poder listar backends sin GPU."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        negative: str,
        seed: int,
        width: int = 1024,
        height: int = 1024,
    ) -> Image.Image:
        ...

    def unload(self) -> None:
        """Libera VRAM. Critico en 8 GB cuando el benchmark encadena backends."""


_REGISTRY: dict[str, Callable[[], Backend]] = {}


def register(key: str) -> Callable[[Callable[[], Backend]], Callable[[], Backend]]:
    def deco(factory: Callable[[], Backend]) -> Callable[[], Backend]:
        _REGISTRY[key] = factory
        return factory

    return deco


def get_backend(key: str) -> Backend:
    if key not in _REGISTRY:
        raise KeyError(f"Backend '{key}' no registrado. Disponibles: {sorted(_REGISTRY)}")
    return _REGISTRY[key]()


def available() -> list[str]:
    return sorted(_REGISTRY)


# Candidatos evaluados pero NO implementados. Se mantienen declarados porque el
# filtro de licencia y VRAM es una decision de proyecto que hay que poder
# consultar, no un detalle que desaparece al no escribir la clase.
PENDING: list[BackendInfo] = [
    BackendInfo(
        key="sdxl-pokemon-trainer",
        display_name="sWizad/pokemon-trainer-sprite-pixelart (LoRA sobre SDXL)",
        base_model="stabilityai/stable-diffusion-xl-base-1.0",
        license="bespoke-lora-trained-license",
        commercial_ok=None,
        min_vram_gb=8.0,
        notes="NO IMPLEMENTADO. Riesgo de licencia para uso comercial: licencia a "
              "medida de CivitAI, hay que leer sus clausulas antes de meterlo en "
              "un juego de pago. Solo como referencia visual.",
    ),
]


def catalog() -> list[tuple[BackendInfo, bool]]:
    """Devuelve (info, implementado) para todo el catalogo."""
    out = [(_REGISTRY[k]().info, True) for k in sorted(_REGISTRY)]
    known = {i.key for i, _ in out}
    out += [(i, False) for i in PENDING if i.key not in known]
    return out


# Alias historico
CATALOG = PENDING
