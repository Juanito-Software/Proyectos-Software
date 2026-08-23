"""SDXL 1.0 + nerijs/pixel-art-xl. La linea base del benchmark.

Notas de 8 GB, que es donde este backend se juega la vida:

- fp16 obligatorio. El UNet de SDXL en fp32 no cabe ni de lejos.
- `enable_model_cpu_offload()` mueve cada submodulo a la GPU solo mientras se
  usa. Cuesta tiempo, pero es la diferencia entre generar y no generar.
- No llamar a `.to("cuda")` si se activa el offload: son incompatibles y
  diffusers avisa (o peor, se lo come y revienta a mitad).
- `enable_vae_tiling()` importa mas de lo que parece: el pico de VRAM de SDXL
  no esta en el UNet, esta en el decode del VAE a 1024x1024.

Sobre el LoRA: no necesita palabra de activacion. Basta con que "pixel" salga
en el prompt, cosa que PromptBuilder garantiza siempre.
"""

from __future__ import annotations

from PIL import Image

from .base import Backend, BackendInfo, register

REPO = "stabilityai/stable-diffusion-xl-base-1.0"
LORA_REPO = "nerijs/pixel-art-xl"
LORA_FILE = "pixel-art-xl.safetensors"


class SDXLPixelArtBackend(Backend):
    info = BackendInfo(
        key="sdxl-pixelart",
        display_name="nerijs/pixel-art-xl (LoRA sobre SDXL 1.0)",
        base_model=REPO,
        license="creativeml-openrail-m",
        commercial_ok=True,
        min_vram_gb=8.0,
        notes="Linea base. Sin palabra de activacion. 30 pasos, guidance 7.5.",
    )

    def __init__(
        self,
        lora_scale: float = 1.0,
        steps: int = 30,
        guidance: float = 7.5,
        force_offload: bool | None = None,
    ) -> None:
        self.lora_scale = lora_scale
        self.steps = steps
        self.guidance = guidance
        self.force_offload = force_offload
        self.pipe = None

    def load(self) -> None:
        import torch
        from diffusers import EulerAncestralDiscreteScheduler, StableDiffusionXLPipeline

        from ..env import probe

        env = probe()
        if not env.has_cuda:
            raise RuntimeError(
                "SDXL sin CUDA no es viable (minutos por imagen). "
                "Usa el backend 'mock' para probar el pipeline."
            )

        pipe = StableDiffusionXLPipeline.from_pretrained(
            REPO, torch_dtype=torch.float16, variant="fp16", use_safetensors=True
        )
        # Euler Ancestral: converge antes y da bordes mas duros que DDIM, que es
        # justo lo que queremos antes de pasar por el PixelPass.
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
        pipe.load_lora_weights(LORA_REPO, weight_name=LORA_FILE)
        pipe.fuse_lora(lora_scale=self.lora_scale)
        pipe.set_progress_bar_config(disable=True)

        offload = env.needs_offload if self.force_offload is None else self.force_offload
        if offload:
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")
        pipe.enable_attention_slicing()
        # diffusers >=0.40 elimino los atajos enable_vae_tiling/enable_vae_slicing
        # de StableDiffusionMixin (verificado contra el wheel real de 0.40.0);
        # el metodo sigue vivo en el VAE (AutoencoderMixin), asi que llamamos
        # ahi directamente. El hasattr de arriba cubre versiones antiguas.
        if hasattr(pipe, "enable_vae_tiling"):
            pipe.enable_vae_tiling()
        else:
            pipe.vae.enable_tiling()
        if hasattr(pipe, "enable_vae_slicing"):
            pipe.enable_vae_slicing()
        else:
            pipe.vae.enable_slicing()

        self.pipe = pipe

    def generate(
        self,
        prompt: str,
        negative: str,
        seed: int,
        width: int = 1024,
        height: int = 1024,
    ) -> Image.Image:
        # El chequeo va ANTES del import de torch a proposito: en una maquina
        # sin torch, olvidarse de llamar a load() debe dar "backend no cargado"
        # y no un ModuleNotFoundError que manda a depurar el sitio equivocado.
        if self.pipe is None:
            raise RuntimeError("Backend no cargado: llama a load() primero")

        import torch
        # Generador en CPU a proposito: el generador de CUDA da resultados
        # distintos segun la tarjeta y rompe la promesa de reproducibilidad del
        # AssetSpec entre maquinas.
        gen = torch.Generator(device="cpu").manual_seed(int(seed))
        return self.pipe(
            prompt=prompt,
            negative_prompt=negative,
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


@register("sdxl-pixelart")
def _factory() -> Backend:
    return SDXLPixelArtBackend()
