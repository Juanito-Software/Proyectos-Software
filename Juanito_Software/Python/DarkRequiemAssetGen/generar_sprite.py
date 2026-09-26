"""Genera sprites de pixel art. Un archivo, un prompt, un comando.

    pip install -r requirements.txt
    python generar_sprite.py

Edita SOLO el bloque CONFIGURACION de abajo y ejecuta. Eso es todo.

Que hace, paso a paso:

    1. Pide al modelo una imagen de 1024x1024 con el prompt que escribiste.
       Es un dibujo normal, con bordes suaves y miles de colores: todavia NO
       es pixel art.
    2. Borra el fondo. El prompt pide un color plano (COLOR_FONDO) y el
       relleno arranca desde los bordes, asi que los huecos interiores del
       mismo color (los ojos de una calavera, la ranura de un yelmo) se
       conservan.
    3. Recorta el espacio vacio y encuadra al sujeto en un cuadrado. Sin esto
       un sprite con mucho aire pierde la mitad de su resolucion util.
    4. Convierte a pixel art de verdad, y aqui esta todo el truco. En este
       orden, que no se puede alterar:
         4a. cuantizar a la paleta, con la imagen todavia a 1024x1024
         4b. bajar a GRID x GRID por votacion (el color mas frecuente de cada
             celda), no por promedio
       Cuantizar antes de reducir es lo que evita los halos: al reducir primero,
       el promedio inventa colores intermedios que luego caen en tonos que no
       estaban en la imagen. Cuantizando primero, la reduccion solo elige entre
       colores que ya son legales. Y votando en vez de promediar, porque
       promediar bordes ES crear antialias, que es justo lo que se elimina.
    5. Alpha binaria (0 o 255, nunca intermedio), mata pixeles sueltos y guarda
       el sprite mas un preview ampliado x8 para mirarlo sin bizquear.

Los 5 pasos son los unicos que hacen falta. No hay specs, ni plantillas de
prompt, ni benchmark, ni metricas, ni atlas: si algo no ayuda a que salga un
sprite, no esta aqui.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

# =============================================================================
# CONFIGURACION  <- edita esto
# =============================================================================

# Lo que quieres ver. En ingles (los modelos estan entrenados en ingles), breve
# y concreto. El fondo plano en COLOR_FONDO es obligatorio: sin el, el paso 2
# tiene que adivinarlo y a veces se come al personaje.
PROMPT = (
    "pixel art, dark medieval knight, full body, front view "
    "standing centered, tattered cape, glowing red visor, "
    "isolated on a plain solid magenta background, no shadow on the ground"
)

# Lo que NO quieres. Si el modelo insiste en algo que no has pedido, subelo
# aqui en vez de fightar con los parametros.
NEGATIVE_PROMPT = (
    "blurry, anti-aliased, 3d render, smooth gradients, photorealistic, "
    "text, watermark, signature, ui, frame, border, multiple characters, "
    "cropped, out of frame, drop shadow, gradient background, scenery, "
    "checkerboard background, jpeg artifacts, noise"
)

# Cuantas imagenes hacer de una vez. Cada una usa SEED, SEED+1, SEED+2...
# La seed es lo que hace reproducible una imagen: mismo prompt + misma seed =
# mismo sprite. Cambia la seed para probar otra variante.
CUANTAS = 4
SEED = 1337

# Modelo. SDXL base con el LoRA de pixel art de nerijs: sin palabra de
# activacion, el LoRA se aplica siempre, y 8 GB de VRAM dan abasto.
MODELO = "stabilityai/stable-diffusion-xl-base-1.0"
LORA = "nerijs/pixel-art-xl"
PESO_LORA = 1.0

# Muestreo. 30 pasos y guidance 7.5 es lo que se ve bien de forma consistente.
# Sube PASOS a 50 para mas detalle (mas lento). Baja GUIDANCE a 5 para menos
# "imaginacion" del modelo, subelo a 9-11 si ignora algo que le pides.
PASOS = 30
GUIDANCE = 7.5

# Tamano del sprite final. 128x128 es la rejilla que usa el proyecto. Cualquier
# valor vale: si no divide exacto en TAMANO, las celdas salen de 8 o 9 pixeles
# de alto, y la votacion lo resuelve igual.
GRID = 128
TAMANO = 1024

# Color de fondo a eliminar. Ponlo a "" si prefieres que lo adivine por el
# borde (funciona peor: come partes del sujeto que sean de ese mismo color).
COLOR_FONDO = "#FF00FF"

# Donde se guarda. Se crea si no existe. Cada imagen deja dos archivos:
#   <SALIDA>/sprite_0.png        el sprite, GRID x GRID, RGBA
#   <SALIDA>/sprite_0_x8.png     el preview, GRID*8, para inspeccion visual
#   <SALIDA>/cruda_0.png         la imagen original de 1024x1024
SALIDA = "salida"

# =============================================================================
# PALETA  <- los 32 colores de Dark Requiem. Anade quita lo que necesites.
# =============================================================================

PALETA = [
    "#0B0A0F", "#16141D", "#241F2E", "#3A3348", "#564D68",   # obsidiana
    "#7A7290", "#9C96AB", "#C2BCCB", "#EAE6F0",               # hueso frio
    "#1D2B3A", "#2F4A63", "#47708F", "#6F9DBA",               # acero
    "#2A0D12", "#571620", "#8C2531", "#C93F45",               # sangre
    "#1E1410", "#3A2620", "#5C3D2E", "#8A5C3D",               # cuero
    "#6B4A16", "#A9762A", "#D9A441", "#F2D489",               # laton
    "#14251A", "#24462C", "#3D7443", "#6AA85E",               # veneno
    "#2B1740", "#52286E", "#8A4BB0",                          # arcano
]

# =============================================================================
# COLOR: sRGB -> OKLab
#
# Por que OKLab y no RGB: la distancia euclidea en sRGB miente. Un azul oscuro
# y un violeta oscuro pueden estar mas "cerca" en RGB que dos grises que el ojo
# ve casi identicos. Cuantizar en RGB produce manchas del color equivocado en
# las sombras, que es donde vive la mayor parte de una paleta de fantasia
# oscura. OKLab esta disenado para que la distancia euclidea se parezca a la
# diferencia percibida, y son 20 lineas de numpy sin dependencias extra.
# =============================================================================


def srgb_a_oklab(rgb: np.ndarray) -> np.ndarray:
    """(..., 3) uint8 sRGB -> (..., 3) float OKLab."""
    c = np.asarray(rgb).astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    largo = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    medio = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    corto = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = np.cbrt(largo), np.cbrt(medio), np.cbrt(corto)
    return np.stack(
        [
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
        ],
        axis=-1,
    )


def hex_a_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def color_mas_cercano(paleta_lab: np.ndarray, pixeles: np.ndarray) -> np.ndarray:
    """Indice del color de paleta mas cercano para cada pixel. (N,3)->(N,).

    En bloques de 65536 para no reventar la RAM: comparar N pixeles contra los
    K colores de la paleta son N*K distancias, y a 1024x1024 sale a 33 M."""
    salida = np.empty(pixeles.shape[0], dtype=np.int64)
    for i in range(0, pixeles.shape[0], 65536):
        trozo = pixeles[i : i + 65536]
        d = ((trozo[:, None, :] - paleta_lab[None, :, :]) ** 2).sum(axis=-1)
        salida[i : i + 65536] = d.argmin(axis=1)
    return salida


# =============================================================================
# PASO 2: borrar el fondo
# =============================================================================


def quitar_fondo(
    rgba: np.ndarray, referencia: tuple[int, int, int] | None, tolerancia: float = 0.10
) -> np.ndarray:
    """Relleno por inundacion desde los cuatro bordes, en OKLab.

    Solo borra lo conectado al borde. Un `remove color` global se cargaria los
    huecos interiores del mismo color que el fondo (el ojo de una calavera, la
    ranura de un yelmo); el relleno no los ve.

    Si no se sabe el color exacto (referencia=None), se deduce de la mediana
    del borde. Adivinar tiene riesgo: si el sujeto tiene tonos parecidos al
    fondo, el relleno entra por la parte clara y se come medio sprite.
    """
    alto, ancho, _ = rgba.shape
    lab = srgb_a_oklab(rgba[..., :3])

    if referencia is not None:
        ref = srgb_a_oklab(np.array(referencia, dtype=np.uint8).reshape(1, 1, 3))[0, 0]
    else:
        borde = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
        ref = np.median(borde, axis=0)

    candidato = np.sqrt(((lab - ref) ** 2).sum(axis=-1)) <= tolerancia

    alcanzado = np.zeros((alto, ancho), dtype=bool)
    alcanzado[0] |= candidato[0]
    alcanzado[-1] |= candidato[-1]
    alcanzado[:, 0] |= candidato[:, 0]
    alcanzado[:, -1] |= candidato[:, -1]

    # Propagacion vectorizada en vez de BFS pixel a pixel: cada pasada avanza una
    # distancia arbitraria a lo largo de una fila o columna entera, asi que
    # converge en unas pocas iteraciones en vez de en un millon de pops de cola.
    columnas = np.arange(ancho)[None, :]
    filas = np.arange(alto)[:, None]

    for _ in range(64):
        antes = int(alcanzado.sum())

        bloqueado = np.maximum.accumulate(np.where(~candidato, columnas, -1), axis=1)
        visto = np.maximum.accumulate(np.where(alcanzado, columnas, -1), axis=1)
        alcanzado |= candidato & (visto > bloqueado)

        rc = columnas.max() - columnas
        bloqueado = np.maximum.accumulate(
            np.where(~candidato, rc, -1)[:, ::-1], axis=1
        )[:, ::-1]
        visto = np.maximum.accumulate(np.where(alcanzado, rc, -1)[:, ::-1], axis=1)[:, ::-1]
        alcanzado |= candidato & (visto > bloqueado)

        bloqueado = np.maximum.accumulate(np.where(~candidato, filas, -1), axis=0)
        visto = np.maximum.accumulate(np.where(alcanzado, filas, -1), axis=0)
        alcanzado |= candidato & (visto > bloqueado)

        rr = filas.max() - filas
        bloqueado = np.maximum.accumulate(np.where(~candidato, rr, -1)[::-1], axis=0)[::-1]
        visto = np.maximum.accumulate(np.where(alcanzado, rr, -1)[::-1], axis=0)[::-1]
        alcanzado |= candidato & (visto > bloqueado)

        if int(alcanzado.sum()) == antes:
            break

    salida = rgba.copy()
    salida[alcanzado, 3] = 0
    return salida


# =============================================================================
# PASO 3: recortar y encuadrar
# =============================================================================


def recortar_y_encuadrar(rgba: np.ndarray, margen: float = 0.06) -> np.ndarray:
    """Recorta al contenido opaco y lo centra en un cuadrado con margen."""
    ys, xs = np.nonzero(rgba[..., 3] > 0)
    if ys.size == 0:
        return rgba

    recorte = rgba[int(ys.min()) : int(ys.max()) + 1, int(xs.min()) : int(xs.max()) + 1]
    alto, ancho, _ = recorte.shape
    lado = max(alto, ancho) + int(round(max(alto, ancho) * margen)) * 2

    lienzo = np.zeros((lado, lado, 4), dtype=rgba.dtype)
    oy, ox = (lado - alto) // 2, (lado - ancho) // 2
    lienzo[oy : oy + alto, ox : ox + ancho] = recorte
    return lienzo


# =============================================================================
# PASO 4: cuantizar y reducir por votacion
# =============================================================================


def reducir_por_votacion(
    indices: np.ndarray, alpha01: np.ndarray, grid: int, n_colores: int
) -> tuple[np.ndarray, np.ndarray]:
    """Cada celda destino se queda con el indice de paleta mas frecuente entre
    sus pixeles opacos. Devuelve (indices, cobertura)."""
    alto, ancho = indices.shape
    fila_celda = (np.arange(alto) * grid // alto).clip(0, grid - 1)
    col_celda = (np.arange(ancho) * grid // ancho).clip(0, grid - 1)
    celda = (fila_celda[:, None] * grid + col_celda[None, :]).ravel()

    a = alpha01.ravel()
    votos = np.bincount(
        celda * n_colores + indices.ravel(), weights=a, minlength=grid * grid * n_colores
    ).reshape(grid * grid, n_colores)

    total = np.bincount(celda, minlength=grid * grid).astype(np.float64)
    cubiertos = np.bincount(celda, weights=a, minlength=grid * grid)
    cobertura = np.divide(cubiertos, total, out=np.zeros_like(cubiertos), where=total > 0)

    return votos.argmax(axis=1).reshape(grid, grid), cobertura.reshape(grid, grid)


def despeckle(indices: np.ndarray, alpha: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mata pixeles opacos totalmente aislados y rellena agujeros de 1 px.

    A rejilla pequena un pixel suelto no es detalle, es ruido: en movimiento
    parpadea."""
    a = alpha.copy()
    idx = indices.copy()
    borde = np.pad(a, 1, constant_values=0)
    vecinos = sum(
        borde[1 + dy : 1 + dy + a.shape[0], 1 + dx : 1 + dx + a.shape[1]]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
    )
    a[(a > 0) & (vecinos == 0)] = 0

    bordes_idx = np.pad(idx, 1, mode="edge")
    agujeros = (a == 0) & (vecinos == 4)
    if agujeros.any():
        a[agujeros] = 255
        ys, xs = np.nonzero(agujeros)
        for y, x in zip(ys, xs):
            vals = [
                bordes_idx[y, x + 1],
                bordes_idx[y + 2, x + 1],
                bordes_idx[y + 1, x],
                bordes_idx[y + 1, x + 2],
            ]
            idx[y, x] = max(set(vals), key=vals.count)
    return idx, a


# =============================================================================
# EL POSPROCESO COMPLETO
# =============================================================================


def a_pixel_art(
    imagen: Image.Image, paleta: np.ndarray, paleta_lab: np.ndarray, grid: int
) -> Image.Image:
    """Imagen cruda del modelo -> sprite RGBA de grid x grid."""
    rgba = np.array(imagen.convert("RGBA"))

    ref = hex_a_rgb(COLOR_FONDO) if COLOR_FONDO else None
    rgba = quitar_fondo(rgba, ref)
    # Si el modelo ignoro el color pedido, el relleno no encuentra nada que
    # quitar. Antes de devolver un sprite con el fondo pegado, se reintenta
    # adivinando el color por el borde.
    if ref is not None and (rgba[..., 3] == 255).mean() > 0.99:
        rgba = quitar_fondo(rgba, None)

    rgba = recortar_y_encuadrar(rgba)

    # Cuantizar A RESOLUCION COMPLETA, antes de reducir. Ver docstring del modulo.
    mapa = color_mas_cercano(
        paleta_lab, srgb_a_oklab(rgba[..., :3].reshape(-1, 3))
    ).reshape(rgba.shape[:2])
    alpha01 = rgba[..., 3].astype(np.float64) / 255.0

    indices, cobertura = reducir_por_votacion(mapa, alpha01, grid, len(paleta))

    # Alpha binaria: 0 o 255, nunca intermedio.
    alpha_chico = np.where(cobertura >= 0.5, 255, 0).astype(np.uint8)
    indices, alpha_chico = despeckle(indices, alpha_chico)

    salida = np.zeros((grid, grid, 4), dtype=np.uint8)
    salida[..., :3] = paleta[indices]
    salida[..., 3] = alpha_chico
    salida[alpha_chico == 0, :3] = 0
    return Image.fromarray(salida)


# =============================================================================
# PASO 1: el modelo
# =============================================================================


def cargar_modelo():
    """SDXL en fp16 con el LoRA de pixel art encima.

    Notas de 8 GB, que es donde esto se juega la vida:
    - fp16 obligatorio. El UNet de SDXL en fp32 no cabe ni de lejos.
    - El offload a CPU mueve cada submodulo a la GPU solo mientras se usa.
      Cuesta tiempo, pero es la diferencia entre generar y no generar.
    - El tiling del VAE importa mas de lo que parece: el pico de VRAM de SDXL
      no esta en el UNet, esta en el decode del VAE a 1024x1024.
    """
    import torch
    from diffusers import EulerAncestralDiscreteScheduler, StableDiffusionXLPipeline

    if not torch.cuda.is_available():
        raise SystemExit(
            "No hay GPU NVIDIA con CUDA. SDXL necesita una (8 GB de VRAM minimo).\n"
            "En CPU tardaria minutos por imagen."
        )

    pipe = StableDiffusionXLPipeline.from_pretrained(
        MODELO, torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    )
    # Euler Ancestral: converge antes y da bordes mas duros que DDIM, que es
    # justo lo que se quiere antes de la cuantizacion.
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.load_lora_weights(LORA, weight_name="pixel-art-xl.safetensors")
    pipe.fuse_lora(lora_scale=PESO_LORA)
    pipe.set_progress_bar_config(disable=True)

    # El offload / .to("cuda") lo decide configurar_dispositivo(), que se
    # llama despues de codificar los prompts. Ver ahi el por que del orden.
    pipe.enable_attention_slicing()
    # diffusers >=0.40 quito los atajos enable_vae_tiling/enable_vae_slicing de
    # StableDiffusionMixin; los metodos siguen vivos en el VAE, asi que se llaman
    # ahi. El pico de VRAM de SDXL no esta en el UNet, esta aqui.
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()

    return pipe, torch


def configurar_dispositivo(pipe, torch) -> None:
    """Coloca el pipeline en la GPU que toca segun la VRAM de la tarjeta.

    Va DESPUES de codificar los prompts, y ese orden es lo importante: con el
    offload activado los codificadores de texto van saltando entre CPU y GPU en
    cada llamada, y codificar trozo a trozo por ahi se vuelve fragil (las
    entradas y los pesos se acaban en dispositivos distintos). Codificando
    primero, el pipeline esta entero en CPU y no hay nada que cuadrar.
    """
    if torch.cuda.get_device_properties(0).total_memory / 1024**3 < 11:
        pipe.enable_model_cpu_offload()   # 8 GB: offload o no hay imagen
    else:
        pipe.to("cuda")


def trocear_prompt(pipe, texto: str) -> list[str]:
    """Parte un prompt en trozos que caben en el contexto de CLIP.

    CLIP admite 77 tokens por trozo (dos son BOS y EOS). Se cuentan con el
    tokenizador de verdad, no con una estimacion por palabras, y se empacan
    respetando las comas para no partir una instruccion por la mitad. Si un
    fragmento entre comas ya no cabe por si solo, se resuelve a palabras, que
    es el unico corte que queda antes de tener que mutilar el texto.
    """
    limite = 75
    if not texto.strip():
        return [""]

    def n_tokens(texto: str) -> int:
        # SDXL codifica el texto con dos CLIP distintos y cada uno tokeniza
        # distinto. Si solo se mira uno, el trozo se pasa de largo en el otro.
        # verbose=False calla el aviso de "sequence length is longer than the
        # maximum": aqui se miden candidatos largos a proposito y no se
        # cargan, asi que ese aviso solo taparia los avisos de verdad.
        return max(
            len(pipe.tokenizer(texto, verbose=False).input_ids),
            len(pipe.tokenizer_2(texto, verbose=False).input_ids),
        )

    def _partir_palabras(fragmento: str) -> list[str]:
        """Trocea un fragmento que no cabe entero ni partiendo por comas."""
        piezas, actual = [], ""
        for palabra in fragmento.split():
            candidata = f"{actual} {palabra}" if actual else palabra
            if actual and n_tokens(candidata) > limite:
                piezas.append(actual)
                actual = palabra
            else:
                actual = candidata
        if actual:
            piezas.append(actual)
        return piezas

    trozos: list[str] = []
    actual = ""
    for parte in (p.strip() for p in texto.split(",")):
        if not parte:
            continue
        if n_tokens(parte) > limite:
            # Las comas ya no bastan para partirlo: se guarda lo pendiente y
            # este fragmento se resuelve a palabras.
            if actual:
                trozos.append(actual)
                actual = ""
            trozos.extend(_partir_palabras(parte))
            continue
        candidata = f"{actual}, {parte}" if actual else parte
        if actual and n_tokens(candidata) > limite:
            trozos.append(actual)
            actual = parte
        else:
            actual = candidata
    if actual:
        trozos.append(actual)
    return trozos


def codificar_prompt(pipe, prompt: str, negativo: str):
    """Codifica el prompt troceado y pega las secuencias en una sola.

    Sin esto, un prompt de mas de 77 tokens se trunca en silencio por el final
    y se pierde la ultima instruccion, que aqui es precisamente la del color de
    fondo: la que decide despues que pixeles se borran. Codificar trozo a trozo
    y concatenarlos mantiene el texto entero.
    """
    import torch

    def _pegar(texto):
        embeds, pooled = [], []
        for trozo in trocear_prompt(pipe, texto):
            e, _, p, _ = pipe.encode_prompt(
                prompt=trozo,
                # En CPU a proposito: con el offload los codificadores migran
                # entre CPU y GPU en cada llamada, y los trozos se quedarian en
                # dispositivos distintos sin poder concatenarlos. El pipeline
                # los mueve a la GPU al invocarlo.
                device="cpu",
                num_images_per_prompt=1,
                do_classifier_free_guidance=False,
            )
            embeds.append(e)
            pooled.append(p)
        return torch.cat(embeds, dim=1), torch.stack(pooled).mean(dim=0)

    embeds, pooled = _pegar(prompt)
    neg_embeds, neg_pooled = _pegar(negativo)
    return embeds, neg_embeds, pooled, neg_pooled


def main() -> None:
    import gc

    paleta = np.array([hex_a_rgb(h) for h in PALETA], dtype=np.uint8)
    paleta_lab = srgb_a_oklab(paleta)

    destino = Path(SALIDA)
    destino.mkdir(parents=True, exist_ok=True)

    print(f"paleta   : {len(paleta)} colores")
    print(f"rejilla  : {GRID}x{GRID}")
    print(f"salida   : {destino.resolve()}")
    print(f"prompt   : {PROMPT[:70]}...")
    print("cargando modelo (la primera vez descarga varios GB)...", flush=True)

    pipe, torch = cargar_modelo()

    # Se codifica una vez, antes del bucle: el texto es el mismo para todas las
    # semillas y no cambia entre imagenes.
    embeds, neg_embeds, pooled, neg_pooled = codificar_prompt(
        pipe, PROMPT, NEGATIVE_PROMPT
    )
    n_trozos = len(trocear_prompt(pipe, PROMPT))
    if n_trozos > 1:
        print(f"prompt   : {n_trozos} trozos (el contexto de CLIP son 77 tokens)")

    # Ya con los prompts codificados: ahora si, a generar.
    configurar_dispositivo(pipe, torch)

    try:
        for i in range(CUANTAS):
            seed = SEED + i
            # Generador en CPU a proposito: el de CUDA da resultados distintos
            # segun la tarjeta y rompe la promesa de que misma seed = misma
            # imagen.
            gen = torch.Generator(device="cpu").manual_seed(seed)

            print(f"  [{i + 1}/{CUANTAS}] seed={seed} generando...", flush=True)
            cruda = pipe(
                prompt_embeds=embeds,
                negative_prompt_embeds=neg_embeds,
                pooled_prompt_embeds=pooled,
                negative_pooled_prompt_embeds=neg_pooled,
                num_inference_steps=PASOS,
                guidance_scale=GUIDANCE,
                width=TAMANO,
                height=TAMANO,
                generator=gen,
            ).images[0]
            cruda.save(destino / f"cruda_{i}.png")

            sprite = a_pixel_art(cruda, paleta, paleta_lab, GRID)
            sprite.save(destino / f"sprite_{i}.png")
            sprite.resize(
                (GRID * 8, GRID * 8), Image.NEAREST
            ).save(destino / f"sprite_{i}_x8.png")

            pixeles = np.array(sprite)
            n_colores = len(
                np.unique(pixeles[..., :3][pixeles[..., 3] > 0].reshape(-1, 3), axis=0)
            )
            print(f"        -> sprite_{i}.png  ({n_colores} colores)", flush=True)
    finally:
        del pipe
        gc.collect()
        torch.cuda.empty_cache()

    print(f"\nListo. {CUANTAS} sprites en {destino}")


if __name__ == "__main__":
    main()
