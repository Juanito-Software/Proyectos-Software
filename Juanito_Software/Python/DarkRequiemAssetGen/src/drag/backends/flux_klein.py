"""FLUX.2-klein-4B + Limbicnation/pixel-art-lora.

La opcion con la licencia mas limpia del catalogo: Apache 2.0 en la base y en
el LoRA. Es el unico peso de FLUX.2 que lo esta — `dev` y `klein 9B` son no
comerciales.

Hay un detalle arquitectonico que conviene tener presente y que no es un fallo
de este codigo: **klein esta destilado de guidance, corre con
`guidance_scale=1.0`, y en ese regimen el prompt negativo no hace nada.** Todo
el trabajo que en SDXL hacen los negativos ("anti-aliased, smooth gradient,
3d render") aqui no existe. Consecuencia practica: con klein el PixelPass no es
una capa de pulido, es la unica defensa. Se acepta el `negative` en la firma
para no romper la interfaz de Backend, y se ignora explicitamente.

Memoria: aqui hay un dato que el "~13 GB" del model card esconde. Los pesos
reales del repo son:

    transformer/  7,75 GB     <- el modelo de 4B del que habla el nombre
    text_encoder/ 8,04 GB     <- en dos shards; es MAS grande que el modelo
    vae/          0,17 GB
    ------------------------
    total        ~16 GB de descarga

`enable_model_cpu_offload()` mueve los modulos **de uno en uno**, asi que el
pico de VRAM es el del modulo mas grande: 8,04 GB del text encoder. En una
tarjeta de 8 GB eso NO cabe. Por eso el modo por defecto aqui es
`sequential`, que baja a nivel de submodulo y cabe en cualquier sitio a cambio
de ser bastante mas lento.

Camino rapido si quieres velocidad en 8 GB: cuantizar el text encoder a 8 bits
(bitsandbytes) y dejar el transformer en BF16 con offload de modulo. Esta
documentado en MANUAL.md; no se automatiza aqui para no meter una dependencia
mas en un backend que quiza descartes tras el benchmark.
"""

from __future__ import annotations

import warnings

from PIL import Image

from .base import Backend, BackendInfo, register

REPO = "black-forest-labs/FLUX.2-klein-4B"
LORA_REPO = "Limbicnation/pixel-art-lora"
LORA_FILE = "pytorch_lora_weights.safetensors"


class FluxKleinPixelBackend(Backend):
    info = BackendInfo(
        key="flux2-klein-pixel",
        display_name="Limbicnation/pixel-art-lora (LoRA sobre FLUX.2-klein-4B)",
        base_model=REPO,
        license="apache-2.0",
        commercial_ok=True,
        min_vram_gb=8.0,
        notes="Apache 2.0 en base y LoRA. 4 pasos, guidance 1.0. ~16 GB de "
              "descarga; el text encoder (8,04 GB) pesa mas que el modelo y "
              "obliga a offload secuencial por debajo de 9 GB de VRAM. "
              "El prompt negativo se ignora: destilado de guidance.",
    )

    def __init__(
        self,
        steps: int = 4,
        guidance: float = 1.0,
        lora_scale: float = 1.0,
        dtype: str = "bfloat16",
        offload: str = "auto",   # auto | sequential | model | none
    ) -> None:
        self.steps = steps
        self.guidance = guidance
        self.lora_scale = lora_scale
        self.dtype = dtype
        self.offload = offload
        self.pipe = None
        self._warned = False

    def _resolve_offload(self, vram_gb: float) -> str:
        if self.offload != "auto":
            return self.offload
        # El umbral es 9 y no 8 porque el modulo mas grande (text encoder)
        # pesa 8,04 GB: en una tarjeta de 8 GB no entra ni el solo.
        if vram_gb < 9.0:
            return "sequential"
        if vram_gb < 18.0:
            return "model"
        return "none"

    def load(self) -> None:
        import torch

        from ..env import probe

        env = probe()
        if not env.has_cuda:
            raise RuntimeError(
                "FLUX.2 klein sin CUDA no es viable. Usa el backend 'mock'."
            )

        try:
            from diffusers import Flux2KleinPipeline as Pipe
        except ImportError:
            try:
                from diffusers import AutoPipelineForText2Image as Pipe  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "diffusers no expone Flux2KleinPipeline. Actualiza: "
                    "pip install -U diffusers"
                ) from exc

        torch_dtype = getattr(torch, self.dtype)
        if torch_dtype is torch.bfloat16 and not env.bf16_ok:
            warnings.warn("La GPU no soporta BF16; cayendo a fp16.", stacklevel=2)
            torch_dtype = torch.float16

        pipe = Pipe.from_pretrained(REPO, torch_dtype=torch_dtype)
        # weight_name explicito: el repo trae DOS ficheros de LoRA
        # (`pytorch_lora_weights.safetensors` y la variante `.comfyui.`), y
        # dejar que diffusers elija es pedir un fallo silencioso el dia que
        # cambien el orden.
        pipe.load_lora_weights(LORA_REPO, weight_name=LORA_FILE)
        try:
            pipe.fuse_lora(lora_scale=self.lora_scale)
        except Exception:  # algunos pipelines de FLUX no soportan fuse
            pass
        pipe.set_progress_bar_config(disable=True)

        modo = self._resolve_offload(env.vram_gb)
        if modo == "sequential":
            pipe.enable_sequential_cpu_offload()
        elif modo == "model":
            pipe.enable_model_cpu_offload()
        elif modo == "none":
            pipe.to("cuda")
        else:
            raise ValueError(f"offload desconocido: {modo}")
        self.resolved_offload = modo
        # Mismo cambio de API que en sdxl.py: diffusers >=0.40 quito el atajo
        # de la pipeline; el fallback real es pipe.vae.enable_tiling(). El
        # try/except anterior tragaba el AttributeError y se quedaba sin
        # tiling activado en silencio -- aqui si aplicamos el fallback.
        if hasattr(pipe, "enable_vae_tiling"):
            pipe.enable_vae_tiling()
        elif hasattr(pipe, "vae") and pipe.vae is not None:
            pipe.vae.enable_tiling()

        self.pipe = pipe

    def generate(
        self,
        prompt: str,
        negative: str,
        seed: int,
        width: int = 1024,
        height: int = 1024,
    ) -> Image.Image:
        if self.pipe is None:
            raise RuntimeError("Backend no cargado: llama a load() primero")

        import torch
        if negative and not self._warned:
            warnings.warn(
                "klein corre con guidance 1.0: el prompt negativo se ignora. "
                "El filtrado de antialias y degradados recae entero en el PixelPass.",
                stacklevel=2,
            )
            self._warned = True

        gen = torch.Generator(device="cpu").manual_seed(int(seed))
        return self.pipe(
            prompt=prompt,
            num_inference_steps=self.steps,
            guidance_scale=self.guidance,
            width=width,
            height=height,
            generator=gen,
        ).images[0]

    def unload(self) -> None:
        self.pipe = None
        try:
            import gc

            import torch

            gc.collect()
            torch.cuda.empty_cache()
        except ImportError:
            pass


@register("flux2-klein-pixel")
def _factory() -> Backend:
    return FluxKleinPixelBackend()
