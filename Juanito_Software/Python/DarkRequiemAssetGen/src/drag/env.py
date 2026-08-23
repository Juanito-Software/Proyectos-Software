"""Deteccion de entorno. Todo import de torch es perezoso a proposito.

El core del proyecto tiene que poder importarse en una maquina sin CUDA, sin
torch y sin 12 GB de disco libre. Si `drag pixelpass` fallara por no encontrar
una GPU, la separacion de capas seria decorativa.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GpuEnv:
    has_torch: bool
    torch_version: str | None
    has_cuda: bool
    device_name: str | None
    vram_gb: float
    free_gb: float          # lo que queda DE VERDAD, ahora mismo
    diffusers_version: str | None
    bf16_ok: bool

    @property
    def ocupada_gb(self) -> float:
        return max(0.0, round(self.vram_gb - self.free_gb, 2))

    @property
    def tier(self) -> str:
        # El perfil se calcula sobre la VRAM LIBRE, no sobre la total. Una 8 GB
        # con Unity y Chrome abiertos es funcionalmente una tarjeta de 6,5 GB, y
        # decirle "justo" cuando en realidad esta "apretado" es como se llega a
        # un CUDA out of memory a los veinte minutos de descarga.
        if not self.has_cuda:
            return "cpu"
        ref = self.free_gb if self.free_gb > 0 else self.vram_gb
        if ref >= 16:
            return "holgado"
        if ref >= 11:
            return "comodo"
        if ref >= 7:
            return "justo"
        return "apretado"

    @property
    def needs_offload(self) -> bool:
        """Por debajo de ~11 GB libres, SDXL y klein en BF16 no caben."""
        ref = self.free_gb if self.free_gb > 0 else self.vram_gb
        return self.has_cuda and ref < 11.0


def probe() -> GpuEnv:
    try:
        import torch
    except ImportError:
        return GpuEnv(False, None, False, None, 0.0, 0.0, _diffusers_version(), False)

    has_cuda = bool(torch.cuda.is_available())
    name = None
    vram = 0.0
    free = 0.0
    bf16 = False
    if has_cuda:
        props = torch.cuda.get_device_properties(0)
        name = props.name
        vram = round(props.total_memory / (1024**3), 2)
        try:
            # mem_get_info descuenta lo que ya consumen el escritorio, el
            # navegador y el editor. Es el unico numero con el que se puede
            # decidir si un modelo cabe.
            free_b, _ = torch.cuda.mem_get_info(0)
            free = round(free_b / (1024**3), 2)
        except Exception:
            free = vram
        try:
            bf16 = bool(torch.cuda.is_bf16_supported())
        except Exception:
            bf16 = False

    return GpuEnv(
        has_torch=True,
        torch_version=torch.__version__,
        has_cuda=has_cuda,
        device_name=name,
        vram_gb=vram,
        free_gb=free,
        diffusers_version=_diffusers_version(),
        bf16_ok=bf16,
    )


def _diffusers_version() -> str | None:
    try:
        import diffusers

        return diffusers.__version__
    except ImportError:
        return None


def advice(env: GpuEnv) -> list[str]:
    """Recomendaciones concretas, no genericas."""
    out: list[str] = []
    if not env.has_torch:
        out.append("Falta torch. Instala el extra: pip install -e \".[sdxl]\"")
        out.append("En Windows con NVIDIA, usa el indice de CUDA de pytorch.org, "
                   "no el paquete por defecto de PyPI.")
        return out
    if not env.has_cuda:
        out.append("torch no ve CUDA. Generar en CPU es inviable: minutos por imagen.")
        out.append("El PixelPass y las metricas si funcionan sin GPU.")
        return out
    if env.diffusers_version is None:
        out.append("Falta diffusers. pip install -e \".[sdxl]\"")

    out.append(
        f"Perfil detectado: {env.tier} — {env.free_gb:.1f} GB libres de "
        f"{env.vram_gb:.1f} GB en {env.device_name}."
    )
    if env.ocupada_gb >= 0.8:
        out.append(
            f"ATENCION: hay {env.ocupada_gb:.1f} GB de VRAM ya ocupados por otros "
            "programas. Unity, Chrome y VS Code se comen entre 1 y 2 GB entre los "
            "tres. Cierralos antes de generar: es la causa numero uno de "
            "'CUDA out of memory' en tarjetas de 8 GB."
        )
    if env.needs_offload:
        out.append("SDXL: fp16 + enable_model_cpu_offload + attention slicing + VAE "
                   "tiling. Descarga ~6,9 GB; el modulo mayor es el UNet (5,13 GB), "
                   "asi que con offload de modulo cabe. Empieza por aqui.")
        if env.vram_gb < 9.0:
            out.append("FLUX.2 klein 4B: cuidado. Descarga ~16 GB y su TEXT ENCODER "
                       "pesa 8,04 GB el solo, mas que el propio modelo (7,75 GB). "
                       "Con enable_model_cpu_offload el pico sigue siendo 8,04 GB y "
                       "NO cabe en tu tarjeta: el backend cae a offload secuencial, "
                       "que funciona pero es lento. Alternativa rapida: cuantizar el "
                       "text encoder a 8 bits (bitsandbytes). Ver MANUAL.md.")
        out.append("Genera a 1024 y baja con el PixelPass. Generar a 512 para "
                   "'ahorrar' empeora la anatomia mas de lo que ahorra.")
    else:
        out.append("Cabe todo en VRAM sin offload. Usa .to('cuda') directamente.")
    if not env.bf16_ok:
        out.append("Sin soporte BF16: para FLUX tendras que ir a fp16/fp8.")
    return out
