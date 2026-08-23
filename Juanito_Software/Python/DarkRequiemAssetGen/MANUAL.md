# Manual de puesta en marcha

Windows + NVIDIA de 8 GB. De cero a un sprite generado, y de ahi al benchmark.

Antes de nada, dos cifras para que decidas si empiezas hoy o el sabado:

| | Descarga | Espacio en disco |
|---|---|---|
| SDXL fp16 + LoRA de nerijs | ~7,1 GB | ~7,1 GB |
| FLUX.2 klein 4B + LoRA | ~16,3 GB | ~16,3 GB |
| **Ambos** | **~23,5 GB** | **~23,5 GB** |

Y un aviso que vale mas que el resto del manual: **los pesos caen por defecto
en `C:\Users\<tu>\.cache\huggingface`**. Si tu C: es un SSD pequeno, mueve la
cache a D: en el paso 4 antes de descargar nada.

---

## 1. Python

Torch en Windows soporta Python 3.10-3.14. Si vas a instalar uno nuevo, coge
**3.12**: es el punto dulce, todo el ecosistema de diffusers tiene ruedas
compiladas para el.

```powershell
python --version
```

Si no tienes o tienes 3.9 o menos, instala desde python.org marcando
"Add python.exe to PATH".

> **Nota**: 3.13 vale. Si en el paso 3 alguna rueda de torch o diffusers no
> tuviera build para tu version, la salida rapida es crear el venv con 3.12
> (`py -3.12 -m venv .venv`) en vez de pelearte con compilaciones.

## 2. Entorno virtual

No instales esto en el Python global. Vas a mezclar torch, diffusers y
transformers, que son las tres librerias que mas se pisan entre versiones.

```powershell
cd D:\Proyectos\Proyectos-Software\Juanito_Software\Python\DarkRequiemAssetGen
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
```

Si PowerShell se queja de la politica de ejecucion:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 3. Torch con CUDA

**Este es el paso donde falla mas gente.** `pip install torch` a secas te
instala la version CPU y luego `drag doctor` te dira "CUDA: no" sin explicar
por que. Hay que usar el indice de PyTorch.

Primero mira que CUDA soporta tu driver:

```powershell
nvidia-smi
```

Arriba a la derecha pone `CUDA Version: 12.x`. Ese numero es el **maximo** que
soporta tu driver, no lo que tienes instalado; no necesitas instalar el toolkit
de CUDA, las ruedas de torch lo traen dentro.

Ahora instala torch **desde el indice de CUDA**. Elige la linea segun lo que
diga tu `nvidia-smi`:

```powershell
# Driver con CUDA 13.x (lo mas comun en drivers recientes)
pip install torch --index-url https://download.pytorch.org/whl/cu130

# Driver con CUDA 12.6 - 12.9
pip install torch --index-url https://download.pytorch.org/whl/cu128
```

Son ~3 GB. Solo necesitas `torch`: este proyecto no usa `torchvision` ni
`torchaudio`.

El driver soporta hacia abajo, asi que si tu `nvidia-smi` dice 13.2 puedes usar
cu130 sin problema. Si estas linea no funcionara, el selector de
<https://pytorch.org/get-started/locally/> siempre esta al dia: Stable /
Windows / Pip / Python / tu CUDA.

Comprueba antes de seguir:

```powershell
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Si sale `False`, para aqui. Reinstalar diffusers no lo arregla.

### Cierra Unity y el navegador antes de generar

`nvidia-smi` no solo te dice la CUDA del driver: te dice **cuanta VRAM tienes
ocupada ahora mismo**, en la columna `Memory-Usage`. Con Unity Hub, el editor,
Chrome y VS Code abiertos es normal ver 1,5-2 GB comidos de los 8.

En una tarjeta de 8 GB eso no es un detalle: el UNet de SDXL pesa 5,13 GB y
necesita hueco para activaciones. Con 1,4 GB ya ocupados vas al limite, y el
`CUDA out of memory` no llega al cargar sino a mitad del decode del VAE, media
hora despues.

`drag doctor` ahora te dice la VRAM **libre**, no la total, precisamente por
esto.

## 4. El proyecto, y donde caen los pesos

```powershell
pip install -e ".[sdxl]"
```

Si ves que esto empieza a bajar **otro** torch de 3 GB, cortalo con Ctrl+C:
significa que el paso 3 no llego a instalarse y pip esta cogiendo la version
CPU de PyPI. Vuelve al paso 3, comprueba con el `python -c "import torch..."`,
y repite este.

Y ahora lo importante. Para que los ~23 GB de modelos no se te coman el C:,
fija la cache de Hugging Face en D: **antes de la primera descarga**:

```powershell
# Solo esta sesion
$env:HF_HOME = "D:\ModelosIA\hf"

# Permanente (abre una consola nueva despues)
setx HF_HOME "D:\ModelosIA\hf"
```

Si ya descargaste algo en C:, mueve la carpeta `.cache\huggingface` a esa ruta
en lugar de volver a bajarlo.

## 5. `drag doctor`

```powershell
drag doctor
```

Deberia decirte algo asi:

```
Entorno
  torch      : 2.x.x+cuXXX
  diffusers  : 0.3x.x
  CUDA       : si
  GPU        : NVIDIA GeForce RTX 4060 Ti
  VRAM       : 6.6 GB libres de 8.0 GB (1.4 GB en uso por otros programas)
  BF16       : si
  perfil     : apretado
```

Fijate en la linea `VRAM`: lo que decide si un modelo cabe es la cifra de
**libres**, no la de total. Si ves mas de 0,8 GB en uso, `drag doctor` te lo
avisa explicitamente — cierra Unity y Chrome y vuelve a mirarlo.

`perfil: apretado` no es un error: es lo correcto para 6,6 GB libres. Con
Unity cerrado deberia subir a `justo`.

## 6. La primera generacion

No lances el benchmark todavia. Una sola imagen primero, para separar "no
arranca" de "arranca pero tarda".

```powershell
drag generate specs\knight.json -b sdxl-pixelart -n 1
```

La primera vez se descarga SDXL (~6,9 GB): tardara. Las siguientes arrancan en
unos 20-40 segundos de carga. La generacion en si, en una tarjeta de 8 GB con
offload de modulo, deberia rondar los **25-45 segundos por imagen** a 1024x1024
y 30 pasos.

Mira `assets\<slug>\preview\*_x8.png`. Si el sprite esta ahi y la silueta se
entiende, funciona.

## 7. Ajustar el fondo

El sprite que probaste en el playground salia con **fondo gris**, no magenta.
Eso importa porque el PixelPass keyea magenta por defecto:

- Si el modelo respeta el `plain solid magenta background` del prompt, todo va
  solo.
- Si te lo devuelve gris, el PixelPass no encuentra magenta y **reintenta
  adivinando por el borde**. Funciona, pero es el modo que falla cuando el
  sujeto tiene tonos parecidos al fondo.

Si ves que tu modelo insiste en el gris, dale la clave real:

```powershell
drag generate specs\knight.json -b sdxl-pixelart --bg-key "#808080"
```

Y si el recorte se come parte del sprite, baja la tolerancia:

```powershell
drag pixelpass assets\<slug>\raw -o out\ --bg-key "#808080" --bg-tolerance 0.05
```

## 8. El benchmark

Con SDXL solo, para empezar:

```powershell
drag bench run -b sdxl-pixelart
drag bench report bench\out\results.csv
```

32 imagenes. A 25-45 s/imagen son **15-25 minutos**. Es reanudable: si lo
cortas con Ctrl+C, el siguiente `bench run` sigue donde estaba.

Luego la parte que no puede automatizar nadie:

```powershell
drag bench rubric bench\out\results.csv
```

Te deja `bench\out\rubrica.csv` con 8 filas. Abre las imagenes de
`bench\out\sdxl-pixelart\`, puntua de 0 a 3 cada criterio mirando las 4 seeds
de cada spec juntas, guarda, y:

```powershell
drag bench rubric bench\out\results.csv --merge
```

## 9. FLUX.2 klein: leelo antes de descargar

Aqui tengo que corregirme respecto a lo que te dije antes. Mire los ficheros
reales del repo y el "~13 GB" del model card esconde un dato incomodo:

```
transformer/   7,75 GB    <- el modelo de 4B
text_encoder/  8,04 GB    <- MAS grande que el modelo
vae/           0,17 GB
```

`enable_model_cpu_offload()` mueve los modulos de uno en uno, asi que el pico
de VRAM es el del modulo mayor: **8,04 GB**. En tu tarjeta de 8 GB no cabe ni
el text encoder solo. Ademas, el model card declara compatibilidad a partir de
RTX 3090 / 4070.

El backend detecta tu VRAM y cae automaticamente a `enable_sequential_cpu_offload()`,
que baja a nivel de submodulo y cabe en cualquier sitio, pero es **bastante mas
lento** — puede irse a minutos por imagen pese a los 4 pasos.

Tienes tres caminos:

**a) Sequential y a esperar.** No toques nada, lanza el benchmark y deja el PC
trabajando. Sabras el coste real porque el CSV lo cronometra.

```powershell
drag bench run -b flux2-klein-pixel
```

**b) Cuantizar el text encoder a 8 bits.** Lo baja a ~4 GB y te permite usar
offload de modulo, mucho mas rapido. Requiere una dependencia mas:

```powershell
pip install bitsandbytes accelerate
```

Y cargar el pipeline con el text encoder cuantizado. No lo he automatizado
porque quiza descartes klein tras el benchmark; si decides ir por aqui, dimelo
y te lo integro en el backend con su prueba.

**c) Saltartelo.** Si SDXL te da resultados que te valen, klein es una apuesta
de licencia (Apache 2.0) que quiza no necesites resolver hoy. Mi opinion: hazlo
solo si el benchmark de SDXL te deja dudas, o si la licencia OpenRAIL-M te
preocupa de cara a Steam.

## 10. A Unity

```powershell
drag pack assets\<slug> -o unity\knight_atlas.png --ppu 32 --pivot 0.5,0.0
```

Copia a `Assets\` **los dos archivos**: el `.png` y el `.png.meta`. Si copias
solo el PNG, Unity genera su propio `.meta` con los ajustes por defecto y el
sprite sale borroso.

Dentro de Unity, comprueba en el inspector de la textura:

- Filter Mode: **Point (no filter)**
- Compression: **None**
- Sprite Mode: **Multiple**
- Pixels Per Unit: **32**

Y en el proyecto, para que el pixel art no vibre al moverse: usa el
**Pixel Perfect Camera** del paquete 2D, con el mismo PPU.

Recuerda: `--pivot 0.5,0.0` (pies) para personajes, `--pivot 0.5,0.5` para
items e iconos de inventario.

## 11. Cuando algo falla

| Sintoma | Que pasa de verdad |
|---|---|
| `CUDA: no` en doctor | Instalaste torch sin el `--index-url`. Desinstala torch y repite el paso 3. |
| `CUDA out of memory` | Cierra Chrome y Unity: se comen 1-2 GB de VRAM. Si sigue, baja `--render-size 768`. |
| Descarga eterna en la primera generacion | Normal: son 6,9 GB. No la cortes; se reanuda, pero verifica el disco libre. |
| `No such file: pixel-art-xl.safetensors` | Sin conexion a Hugging Face o proxy. Prueba `huggingface-cli download nerijs/pixel-art-xl`. |
| El sprite sale con el fondo pegado | El modelo no hizo el fondo magenta. Paso 7. |
| El sprite sale medio comido | El fondo se parece al sujeto. Baja `--bg-tolerance` a 0.05. |
| Todo sale igual entre seeds | Estas usando el backend `mock`. Pon `-b sdxl-pixelart`. |
| Sprites borrosos en Unity | Falta el `.png.meta`, o lo sobreescribiste. Paso 10. |
| Frames cruzados en la animacion | Estas leyendo el atlas con coordenadas de arriba-izquierda. Unity mide desde abajo. |
| `AttributeError: ... has no attribute 'enable_vae_tiling'` | Version vieja de `drag` (<=0.3.3) contra `diffusers>=0.40`, que quito ese atajo de la pipeline y lo dejo solo en el VAE. Actualiza a `drag` 0.3.4+: ya llama a `pipe.vae.enable_tiling()` cuando el atajo no existe. Si no puedes actualizar, la alternativa es fijar `diffusers<0.40` en el venv. |

## 12. El orden que recomiendo

1. Pasos 1-5. Pegame la salida de `drag doctor`.
2. Paso 6: una imagen con SDXL. Si sale, el resto es cuesta abajo.
3. Paso 8: benchmark solo de SDXL, 20 minutos.
4. Miras las 32 imagenes y decides si el proyecto merece la pena. **Esta es la
   decision real**, y quiero que la tomes con imagenes tuyas delante, no con mi
   entusiasmo.
5. Si sigue en pie: klein, o directamente fase 4 sobre SDXL.
