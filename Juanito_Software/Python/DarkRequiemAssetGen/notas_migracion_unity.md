# Notas de migración a Unity (57 frames, 64 px)

Bitácora de trabajo de la migración de `generar_spritesheet.py` al contrato de
importación en Unity. `tests/test_contrato_unity.py` es la fuente de verdad.

Este archivo es material de trabajo: no se versiona. Al cerrar la sesión, sus
datos deben volcarse a `MAINTENANCE.md` y lo que se decida conservar, al README
del proyecto.

## Decisiones

- **Cuadrícula nueva, no reescala.** 64 px por celda, 12 filas por 6 columnas.
  Rehacer estilo, paleta, anclaje y QC a 64 px; no escalar mecánicamente 128→64.
- **Opción B para `--referencia`.** La referencia elegida gobierna el
  IP-Adapter y el QC. Las restricciones categóricas del proyecto no se
  relativizan por usar otra referencia.
- **QC de dos niveles.** Con `Frame` el QC es geométrico y frame-aware; sin
  `Frame` se conserva el criterio estético legacy.
- **`armar_hoja` en modo dual.** Firma nueva `armar_hoja(resultados)` sobre la
  matriz de 12×6, conservando la firma legacy
  `armar_hoja(celdas, filas=3, columnas=7, grid=GRID)`.
- **Pivote del manifiesto ≠ pivote del rectángulo.** El manifiesto declara
  `pivot y = 0.125` (lógica de la hoja) y el importador de Unity fija el pivote
  por rectángulo en `0.5, 0.5`. Son dos cosas distintas y se documentan así.

## 2026-09-29

### Inspección y diseño

- Leídos `tests/test_contrato_unity.py` (fuente de verdad),
  `tests/test_generar_spritesheet.py` (suite legacy) y la implementación actual.
- Inspeccionados los PNG, JSON y `.meta` reales de referencia. Confirmado que
  el padding de alfa de 1 px por lado es intencionado
  (`offset = (-1, -1)`, `size = (ancho + 2, alto + 2)`) y que lo escribe Unity,
  no Python.
- Confirmado que no existían importadores de Unity ni documentación de
  `*_sheet.json`: hay que escribir ambos.
- Localizadas aserciones legacy que contradicen el contrato nuevo, entre ellas
  las de "personaje demasiado grande", que espera un motivo `alto` cuando la
  geometría ya no se valida en el QC legacy.
- Baseline medido **antes** de editar: contrato `37 failed, 4 passed`; suite
  completa `38 failed, 114 passed`. Son la referencia de partida, no el estado
  actual.

### Cambio 1: constante y estructura de la hoja

- `CELDA = 64`, `GRID = CELDA`, `FILAS = 12`, `COLUMNAS = 6`, `PPU = 64`.
- Anclajes a 64 px: `CELDA_PIE = 55`, `CELDA_CENTRO = 31.5`,
  `ALTO_CELDAS = 47`.
- `ANCHO_HOJA = 384`, `ALTO_HOJA = 768`.
- `QC_COBERTURA_MAX = 0.40` sustituye a la banda `QC_COBERTURA`. Motivo: la
  banda `0.28..0.40` era una media de la referencia de pie y rechazaba en falso
  las filas tumbadas de `roll` y `death`. Ahora solo se rechaza por exceso y la
  banda se conserva como dato informativo.
- Añadidos `FilaHoja`, `TABLA_FILAS` (12 filas), `GeometriaCelda`,
  `GEOMETRIA_CELDAS` (19 entradas) y `geometria_de_frame()`.
- `Frame` normalizado a vistas lógicas `down/up/side` y animaciones
  `idle/walk/roll/death`, con `imagen` RGBA por defecto, `fila`, `columna`,
  `global_index` y `clave`.
- `_construir_matriz()` genera los 57 frames.
- Docstring principal actualizado a 57 frames, 64×64, 384×768, 12 filas y
  6 columnas.

Verificado por importación: `len(MATRIZ) == 57`, `len(TABLA_FILAS) == 12`,
`len(GEOMETRIA_CELDAS) == 19`, `ANCHO_HOJA == 384`, `ALTO_HOJA == 768`, y
`Frame("frontal", "walk", 1, 0, 0)` normaliza a `down walk down_walk_1` con
fila 3, columna 0, índice global 12 y vista legacy `frontal`.

### Cambio 2: prueba de QC contractuales

- `tests/test_contrato_unity.py:34`: `_celda_roja` → `_celda_roda` (usada con ese
  nombre en las líneas 213 y 240) y docstring corregido a «rectángulo opaco
  gris».

### Cambio 3: `qc_frame` con geometría frame-aware

Firma nueva: `qc_frame(imagen, ref, frame=None)`.

- Con `frame`: primero `alto` contra `geometria.alto ± alto_tol`; si falla,
  `QC(ok=False, motivos=("alto",))` y nada más. Después `pie` contra
  `geometria.pie ± alto_tol`; si falla, `("pie",)`. Solo si la geometría pasa
  se evalúa la estética: binaria de alfa, `n_colores <= MAX_COLORES`, un solo
  componente, debris bajo el umbral y cobertura solo si supera
  `QC_COBERTURA_MAX`. Motivos como tupla ordenada.
- Sin `frame`: criterio legacy. Alfa binaria, paleta, peso cromático,
  conectividad y debris. Sin geometría, sin centro y sin banda de cobertura,
  para no heredar umbrales de rejilla de 128 px.
- Descartado: validar `pie` con `QC_PIE_TOL` (1) en el camino frame-aware. Con
  la geometría canónica el pie puede caer un píxel fuera sin ser un fallo, y
  además la forma tumbada hace poco informativo ese margen.

### Cambio 4: `normalizar_para_reduccion` y `metricas_sprite`

- `normalizar_para_reduccion` ya usaba `ALTO_CELDAS = 47`, `CELDA_PIE = 55`,
  `CELDA_CENTRO = 31.5` y `grid = 64`; la adaptación funcional estaba hecha.
  Solo se limpiaron los comentarios que seguían describiendo 128 px
  (`684/725/381`).
- `metricas_sprite` no asume 128 px: calcula dimensiones, bbox, componentes,
  debris, colores y pesos sobre el RGBA recibido.
- Sin cambios de comportamiento en este punto.

### Hallazgo sobre la paleta de la referencia

Medida con `metricas_sprite` sobre la referencia real: `alto = 114`,
`ancho = 66`, `pie = 120`, `centro_x = 63.5`, `cobertura = 0.3451`,
23 colores. El gris `(220, 220, 220)` de `_celda_roda` **no** está en la paleta
de la referencia (los más cercanos son `(234, 230, 240)` y `(194, 188, 203)`),
así que su peso cromático compartido es `0.0`.

Consecuencia: el test `test_el_qc_sigue_admitiendo_una_imagen_sin_frame_con_el_umbral_legacy`
(10×10) obliga a que la comprobación de peso cromático **no** actúe como puerta
en el QC legacy. Se conserva la métrica en `.metricas` y la función
`_peso_cromatico_compartido`, pero no decide `ok`.

### Pendiente

- Devolver `motivos` como lista en el camino legacy y como tupla en el
  frame-aware: las pruebas legacy comparan con `== []` y las contractuales con
  `== ("alto",)`.
- `espejar_horizontal()` y `animacion_legacy_de_manifiesto()`.
- `Frame.original` y la duración `0` de los frames legacy.
- 36 poses de `POSES_BODY_25`.
- `preset_de_frame`, prompts lógicos, `_VISTAS_EN_TEXTO`, `_MOVIMIENTOS_EN_TEXTO`
  y `control_de_frame`.
- `armar_hoja`, `exportar_celda`, `exportar_previews`, `exportar_todo`,
  `construir_manifiesto`, crudas, `.meta`, `main()`, `--falso`, `--limite`.
- Importador de Unity y documentación de importación.
- Reejecutar `python -m pytest tests/test_contrato_unity.py -q`.
