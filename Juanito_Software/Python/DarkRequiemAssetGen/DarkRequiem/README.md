# DarkRequiem — hoja de sprites para Unity

Hoja generada por `generar_spritesheet.py` a partir de las celdas del
personaje. Una sola lamina de **384 x 768** px (6 columnas de 64 px por
**12 filas** de 64 px) con **57** celdas, cada una de 64 px, ensamblada
por posicion de frame.

## Contrato de importacion en Unity

Para que el importador recorte cada celda donde corresponde, la textura se
configura asi.

- **Import Type**: Sprite (mode **`spriteMode` = *Multiple***), recortado
  automaticamente por el rect del manifiesto (`spritesheet.json`).
- **Pixels Per Unit**: **`spritePixelsToUnits` = 64** (cada pixel de celda
  equivale a una unidad).
- **Filter Mode**: *`Point`* (sin suavizado; se conserva el pixel-art).
- **Alpha Is Transparency**: **`alphaIsTransparency`** activado (los bordes
  transparentes de la celda no ensucian el recorte).

Unity no lee `spritesheet.json`: recorta por **carpetas** y por `frames.json`.
Las celdas se guardan en los subdirectorios legacy que el importador espera,
`idle/frontal/`, `walking/trasera/`…, y `frames.json` describe ppu, pivot y
los **cuatro clips** que el juego reproduce:

| Clip | Direcciones | Frames/dir | Duración | Bucle |
|---|---|---|---|---|
| `idle` | down, up, right, left | 4 | 0.167 s | sí |
| `walking` | down, up, right, left | 6 | 0.125 s | sí |
| `roll` | down, up, right, left | 4 | 0.083 s | no |
| `death` | down, up, right, left | 5 | 0.125 s | no |

La hoja física solo tiene **tres vistas** por animación (`frontal`, `trasera`
y `lateral`). La dirección `left` se sirve desde la misma lateral que `right`
con `"espejo": true` en `frames.json`: el importador vuelve a usar la misma
textura recortada con `scale.x = -1` (equivalente a
`espejar_horizontal` de `generar_spritesheet.py`). No hace falta generar
frames dobles para izquierda y derecha.

## Salida

- `spritesheet.png` — la lamina lista para Unity.
- `wanderer_sheet.json` — manifiesto logico (hoja, celdas y rects).
- `frames.json` — formato propio de Unity (ppu, pivot, clips).
- `previews/` — vistas x8 para revisar a ojo.
- `crudas/` — celdas de 768 px para diagnosticar el control de calidad.