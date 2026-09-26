# Dark Requiem AssetGen

Genera sprites de pixel art para Dark Requiem a partir de un prompt escrito a
mano. Un solo archivo, un solo comando.

## Qué necesitas

- Python 3.11 o superior
- Una GPU NVIDIA con CUDA. **8 GB de VRAM** es el mínimo realista; con menos,
  SDXL no carga. El pipeline completo, con el offload por CPU, se ha probado
  en una RTX 4060 Ti de 8 GB contra un modelo de prueba reducido, no todavía
  contra SDXL entero.
- La primera ejecución descarga el modelo (~7 GB) y tarda.

## Instalar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> **Ojo con Torch.** `requirements.txt` pide `torch`, y por defecto pip instala
> la build de **CPU**, que no sirve aquí. El índice va según tu CUDA:
>
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu130  # CUDA 13
> pip install torch --index-url https://download.pytorch.org/whl/cu124  # CUDA 12.x
> ```
>
> El que está verificado aquí es `torch 2.13.0+cu130` sobre CUDA 13.0.

## Generar

Edita el bloque `CONFIGURACION` de `generar_sprite.py` — sobre todo `PROMPT` —
y ejecuta:

```bash
python generar_sprite.py
```

Se guardan en `salida/`:

| Archivo | Qué es |
|---|---|
| `cruda_0.png` | La imagen original del modelo, 1024x1024 |
| `sprite_0.png` | El sprite final, 128x128 RGBA, alfa binaria |
| `sprite_0_x8.png` | El mismo sprite ampliado x8, para inspeccionarlo |

`CUANTAS` imágenes por ejecución, con seeds `SEED`, `SEED+1`, … Mismo prompt y
misma seed = mismo sprite.

## Cómo se procesa la imagen

Cinco pasos, en este orden, y el orden importa:

1. **Generar** con SDXL base + el LoRA de pixel art.
2. **Borrar el fondo** con relleno por inundación desde los bordes. Se pide un
   color plano en el prompt (`COLOR_FONDO`); como solo se borra lo conectado al
   borde, los huecos interiores de ese mismo color —los ojos de una calavera, la
   ranura de un yelmo— se conservan.
3. **Recortar y encuadrar** en un cuadrado, para que el sujeto no pierda
   resolución en el aire sobrante.
4. **Cuantizar a la paleta y reducir por votación.** Cuantizar *antes* de
   reducir es lo que evita los halos: si se redujera primero, el promedio
   inventaría colores intermedios que no están en la paleta. Y se reduce por
   **votación**, no por promedio, porque promediar bordes es crear antialias.
5. **Alfa binaria** (0 o 255, nunca intermedio) y limpieza de píxeles sueltos.

## Las paletas

- `PALETA` en el script: los 32 colores de Dark Requiem. Añade o quita.
- `COLOR_FONDO`: el color que se borra en el paso 2. Pon `""` para adivinarlo
  por el borde (funciona peor: se come partes del sujeto).

## Si algo falla

**`No hay GPU NVIDIA con CUDA`** — no hay nada que hacer, SDXL necesita GPU.

**La primera imagen tarda mucho o se corta** — normal, está descargando. Las
siguientes van mucho más rápido.

**Se come parte del personaje** — el modelo no dio el color de fondo exacto, o
el sujeto tiene un tono parecido. Prueba otro `COLOR_FONDO` o quítale ese color
al sujeto en el prompt.

**Muy pocos colores / manchas raras** — la imagen original no tiene suficiente
contraste. Sube `PASOS` a 50 o ajusta el prompt.

## Documentación

- `dark-requiem-chuleta-artistica.md` — dirección artística del juego
  (referencias, paleta, bestiario). Útil para decidir **qué** pedir en el
  prompt.
