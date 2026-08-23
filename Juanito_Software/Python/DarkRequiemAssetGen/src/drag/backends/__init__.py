from .base import (
    CATALOG,
    PENDING,
    Backend,
    BackendInfo,
    available,
    catalog,
    get_backend,
    register,
)

# Los tres se registran al importar el paquete. Ninguno importa torch a nivel
# de modulo, asi que `drag backends` funciona en una maquina sin CUDA: los
# imports pesados viven dentro de load().
from . import flux_klein, mock, sdxl  # noqa: E402,F401

__all__ = [
    "Backend",
    "BackendInfo",
    "CATALOG",
    "PENDING",
    "available",
    "catalog",
    "get_backend",
    "register",
]
