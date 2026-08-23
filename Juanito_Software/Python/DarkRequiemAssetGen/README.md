# Dark Requiem Asset Generator

Generador de sprites de pixel art para *Dark Requiem*, orientado a Unity.
Rejilla objetivo **32x32**, paleta cerrada, alpha dura, y specs reproducibles.

**Estado: fases 0-3 completas** (v0.3.4). De un spec de texto a un atlas
importable en Unity, con benchmark de modelos por el camino. El backend `mock`
ejecuta la cadena entera sin GPU; los dos backends reales estan escritos y
verificados contra hardware real (RTX 4060 Ti, 8 GB).

---

## La tesis

Los generadores no producen pixel art: producen **imagenes con estetica de
pixel**. La diferencia se paga en Unity — rejilla desalineada, bordes con
antialias que se ven sucios al escalar, y paletas que explotan a cientos de
colores donde deberia haber dieciseis.

Por eso el valor del proyecto no esta en el modelo, sino en las capas que van
**despues** del modelo. Un wrapper de `diffusers` te deja una carpeta de PNGs
bonitos e inservibles. Esto te deja assets.

```
AssetSpec  ->  PromptBuilder  ->  Backend  ->  PixelPass  ->  Packager
  spec         plantillas       modelo      downscale +    atlas +
  tipado       + negativos      local       paleta+alpha    .meta Unity
   [x]            [x]            [x]           [x]            [x]
```

## Instalacion

```bash
pip install -e .           # solo pillow + numpy
pip install -e ".[sdxl]"   # torch, diffusers, peft, accelerate
drag doctor                # que puede hacer esta maquina, y como
```

Paso a paso para Windows + NVIDIA de 8 GB, con las trampas de torch/CUDA y las
cifras reales de descarga: **[MANUAL.md](MANUAL.md)**.

El core se mantiene en dos dependencias a proposito: el PixelPass, el benchmark
y el packager tienen que poder ejecutarse en cualquier maquina, en CI incluida,
sin arrastrar 3 GB de CUDA. Ningun backend importa `torch` a nivel de modulo.

## El flujo completo

```bash
drag doctor                                       # diagnostico de GPU
drag backends                                     # catalogo: licencia y VRAM

drag generate specs/knight.json -b sdxl-pixelart -n 4    # spec -> sprites

drag bench run -b sdxl-pixelart,flux2-klein-pixel        # fase 2
drag bench report bench/out/results.csv
drag bench rubric bench/out/results.csv                  # plantilla manual
drag bench rubric bench/out/results.csv --merge          # decision final

drag pack assets/mis_sprites -o unity/atlas.png --ppu 32 # fase 3
```

Comandos sueltos: `drag pixelpass`, `drag metrics`, `drag palette extract`,
`drag prompt`.

## Fase 1 — el sidecar, y por que existe

`drag generate` deja por spec un PNG de 32x32, su preview ampliado, el
1024x1024 original y un **sidecar JSON** con el spec completo, el prompt
exacto, la seed, el backend **con su licencia**, la config del PixelPass y las
metricas antes y despues. `regenerate_from_sidecar()` rehace el pixel exacto.

Lo primero es comodidad. Lo segundo no: si *Dark Requiem* acaba en Steam, la
trazabilidad de que pesos generaron que arte es el papel que querras tener
escrito, y reconstruirlo a posteriori sobre cientos de sprites es imposible.

## El PixelPass, y en que orden

1. **Quitar fondo** — flood fill desde los bordes en OKLab.
2. **Recortar y encuadrar** — sin esto, un sprite con aire alrededor pierde la
   mitad de su resolucion util al bajar a 32.
3. **Cuantizar a paleta, a resolucion completa** — *antes* del downscale.
4. **Downscale modal** — color dominante por celda, por votacion.
5. **Alpha binaria** — 0 o 255, nunca intermedios.
6. **Despeckle** — a 32x32 un pixel suelto no es detalle, es parpadeo.

Los puntos no obvios:

- **3 antes de 4.** Si reduces primero y cuantizas despues, el promedio de la
  reduccion inventa colores intermedios que luego se mapean a tonos que no
  estaban en la imagen: aparecen halos. Cuantizando primero, el downscale solo
  vota entre colores que ya son legales.
- **Moda, no media.** Promediar bordes es literalmente fabricar antialias.
- **OKLab, no RGB.** La distancia euclidea en sRGB miente sobre todo en
  sombras, que es donde vive el 60% de una paleta de fantasia oscura.
- **`--bg-key #FF00FF`.** El prompt ya pide fondo magenta, asi que adivinarlo
  por la mediana del borde es tirar informacion que ya tenemos — y fallaba en
  cuanto el sujeto tenia tonos cercanos al fondo: el relleno entraba por ahi y
  se comia medio sprite. `generate` keyea magenta y reintenta adivinando si el
  modelo ignoro la instruccion.

## Fase 2 — el benchmark

Matriz fija en `bench/matrix.json`: 8 specs (2 personajes, 2 enemigos, 2
objetos, 2 tiles) x 4 seeds. Con los tres backends son 96 imagenes, todas por
el mismo PixelPass.

Tres decisiones vienen directamente de una tarjeta de 8 GB:

- **Un load por backend, no uno por imagen.** Cargar SDXL cuesta decenas de
  segundos; hacerlo 32 veces es tirar media hora.
- **CSV incremental.** Cada fila se escribe en cuanto existe. Que un cuelgue a
  mitad no borre una hora de trabajo no es comodidad: es la diferencia entre
  ejecutar el benchmark y no ejecutarlo.
- **Reanudable.** Al arrancar lee lo hecho y lo salta. Puedes parar, liberar la
  GPU, y seguir manana.

Y una que no viene de la VRAM: **se cronometra cada imagen**. En una tarjeta
ajustada, un modelo que gana por poco pero tarda cuatro veces mas no gana,
porque acabaras generando cuatro veces menos variantes por sprite.

`drag bench report` agrega por backend: segundos mediana y total, colores
finales, % fuera de paleta y huerfanos en crudo, cobertura del canvas, y una
**tasa de fallo** — sprites que salieron vacios o en dos colores, contados
aparte para que la mediana no los tape.

Esas cifras miden aptitud mecanica, no calidad artistica. Para decidir hace
falta `drag bench rubric`: una fila por (backend, spec) — 24 juicios, no 96 —
con cinco criterios de 0 a 3, incluido el unico que ninguna metrica puede
calcular, *cuanto retoque manual en Aseprite te ahorra*. Puntuar imagen a
imagen es inviable y ademas equivocado: lo que juzgas es si ese modelo entiende
ese tipo de sujeto, y eso se ve mirando las cuatro seeds juntas.

## Fase 3 — atlas y `.meta` de Unity

Importar 60 sprites sueltos y configurarlos a mano son 60 oportunidades de que
uno se quede en Bilinear y salga borroso en la build. El `.meta` generado fija
de una vez los cuatro ajustes que importan:

| Ajuste | Valor | Por que |
|---|---|---|
| `filterMode` | 0 (Point) | El unico responsable de que se vea nitido. |
| `textureCompression` | 0 | DXT sobre 32x32 destroza la paleta que cuantizaste. |
| `enableMipMap` | 0 | En 2D no aportan y emborronan a distancia. |
| `spriteMeshType` | 0 (FullRect) | Con Tight, Unity recorta al alfa y desalinea pivotes entre frames. |

El pivote por defecto es **(0.5, 0.0)**, centro-abajo, no el centro. Para
personajes sobre un tilemap, el pivote en los pies es lo que hace que el sprite
se apoye en el suelo y que el orden de dibujado por Y funcione sin offsets
magicos en cada prefab. Para items usa `--pivot 0.5,0.5`.

El atlas es una rejilla uniforme y no un bin-packing: con sprites del mismo
tamano el packing optimo *es* la rejilla, y ademas queda editable si abres el
atlas en Aseprite para retocar un frame.

**Aviso**: el formato del `.meta` varia entre versiones de Unity. Esta escrito
contra el esquema de 2021-2023 LTS. Verifica el primero antes de generar
sesenta. Los GUID e internalID se derivan del contenido, no de un random, para
que reimportar no rompa referencias en escenas y prefabs.

## Metricas

| Metrica | Que detecta |
|---|---|
| `unique_colors` | Un sprite sano vive bajo ~24. Un PNG de difusor pasa de 5.000. |
| `offpalette_pct` | % de pixeles lejos de tu paleta. Trabajo de cuantizacion pendiente. |
| `soft_alpha_pct` | Alpha intermedia = flecos sucios en Unity con filtro Point. |
| `orphan_color_pct` | Colores con menos del 0,1% de presencia: firma de degradado. |
| `grid_adherence` | Si el bloque real coincide con el que exige la rejilla objetivo. |

## Backends (filtro: comercial + 8 GB de VRAM)

| Clave | Base | Licencia | Comercial | Notas |
|---|---|---|---|---|
| `mock` | — | — | — | Sin modelo, determinista. Pruebas y CI. |
| `sdxl-pixelart` | SDXL 1.0 | CreativeML OpenRAIL-M | Si | 30 pasos, guidance 7.5. Linea base. |
| `flux2-klein-pixel` | FLUX.2-klein-4B | Apache 2.0 | Si | 4 pasos, guidance 1.0. |
| `sdxl-pokemon-trainer` | SDXL 1.0 | bespoke-lora-trained-license | **Verificar** | No implementado. |

- **SDXL en 8 GB**: fp16 + `enable_model_cpu_offload()` + attention slicing +
  VAE tiling. El pico de VRAM no esta en el UNet sino en el decode del VAE a
  1024x1024, asi que el tiling no es opcional.
- **klein 4B**: el "~13 GB" del model card esconde un dato incomodo. Los pesos
  reales son transformer 7,75 GB + **text encoder 8,04 GB** + vae 0,17 GB, unos
  16 GB de descarga. Como `enable_model_cpu_offload()` mueve los modulos de uno
  en uno, el pico es el del mayor: 8,04 GB, que en una tarjeta de 8 GB no cabe
  ni el solo. El backend cae a offload secuencial por debajo de 9 GB de VRAM.
  El camino rapido es cuantizar el text encoder a 8 bits; esta en el manual.
- **klein ignora el prompt negativo.** Esta destilado de guidance y corre a
  `guidance_scale=1.0`; en ese regimen el negativo no hace nada. Todo el
  trabajo que en SDXL hacen `anti-aliased, smooth gradient, 3d render` aqui no
  existe, y el PixelPass pasa de pulido a unica defensa. El sidecar lo registra
  en `negative_efectivo` para no concluir mas tarde que "los negativos no
  sirven" cuando lo que pasa es que ese backend no los mira.
- El LoRA de sWizad tiene licencia a medida de CivitAI. Mientras no se lean sus
  clausulas no entra en un juego de pago: queda declarado, sin implementar.

El generador usa `torch.Generator(device="cpu")` a proposito: el de CUDA da
resultados distintos segun la tarjeta y romperia la reproducibilidad del spec
entre maquinas.

## Verificacion

```bash
PYTHONPATH=src:tests python -m pytest tests -q     # ~4 min, 67 pruebas
```

Las fixtures son sinteticas y simulan la salida cruda de un difusor
(1024x1024, antialias, degradados, ruido, fondo magenta) — validar el PixelPass
contra pixel art ya limpio pasaria trivialmente y no probaria nada.

Lo que se afirma: tamano exacto a 16/32/64, alpha estrictamente binaria, todos
los colores en paleta, fondo eliminado sin comerse el sujeto (con regresiones
para los tres modos de fallo que aparecieron), huecos interiores conservados,
dos ejecuciones del mismo spec dando bytes identicos, el sidecar describiendo
lo que se hizo, el benchmark reanudando sin repetir trabajo, cada frame del
atlas recortando su sprite original, y el rect de Unity apuntando al sprite
correcto tras el flip vertical.

## Roadmap

- [x] **Fase 0** — PixelPass, paleta, spec, metricas. Sin modelo.
- [x] **Fase 1** — Backends (mock + SDXL + klein), pipeline, sidecar, doctor.
- [x] **Fase 2** — Benchmark reanudable, informe agregado, rubrica manual.
- [x] **Fase 3** — Atlas + `.meta` de Unity.
- [ ] **Fase 4** — Consistencia de personaje entre frames (IP-Adapter / referencia).

Sobre la fase 4: es la unica que no se puede escribir a ciegas. Mantener el
mismo personaje entre ocho frames de animacion depende de que combinacion de
IP-Adapter, ControlNet de pose y peso de referencia funcione **con el backend
que gane el benchmark**, y esa eleccion aun no esta hecha. Escribirla antes
seria escribir contra un modelo imaginario.

## Creditos

La deteccion de escala de rejilla reimplementa la idea de
[pixeldetector](https://github.com/Astropulse/pixeldetector) (Astropulse, MIT)
sobre numpy puro.
