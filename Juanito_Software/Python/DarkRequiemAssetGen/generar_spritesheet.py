"""generar_spritesheet.py — clipsheet de 57 frames para Dark Requiem.

Genera una hoja de sprites 2D estilo pixel art a partir de una imagen de
referencia, con poses OpenPose, IP-Adapter y ControlNet. El nucleo de este
modulo es determinista y no necesita GPU: normaliza, cuantiza, reduce a
64x64, controla la calidad y ensambla la hoja. La generacion con SDXL se
invoca solo desde `main()`.

La hoja tiene 12 filas desiguales (idle, walk, roll y death, cada uno en sus
tres vistas) repartidas en 6 columnas, es decir 57 celdas de 64 px: la hoja
final mide 384x768. Unity la importa como Multiple (spriteMode 2) con
`spritePixelsToUnits` 100 y un manifiesto logico `*_sheet.json` que declara
el pivote (0.5, 0.125) y, por fila, el ritmo (fps), el bucle y los indices
globales de sus frames.

La regla de oro del anclaje: la escala sale de la ALTURA del recorte (nunca
del ancho) y el personaje se apoya en el suelo por su ultima fila opaca. Asi
un brazo o una espada ensanchan el bbox sin hacer crecer el cuerpo.

Fases (panel lateral derecho):
  1. Nucleo determinista: normalizacion, QC, reintentos, ensamblado.   <- aqui
  2. Poses OpenPose BODY_25 en codigo.
  3. Prompts troceados que conservan "plain solid magenta background".
  4. Cargador SDXL + LoRA + IP-Adapter + ControlNet.
  5. Orquestacion de la tanda de 57 frames y smoke test.
  6. Manifiesto logico e importador Unity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

import generar_sprite as gs_base

# --- Constantes de la hoja ---------------------------------------------

#: Lienzo de trabajo por frame: se genera a 768 y se reduce a 64.
LIENZO = 768

#: Lado de la celda final en la hoja, el contrato de Unity.
CELDA = 64

#: Alias legacy del lado de celda: los tests y `escalar_sprite` lo usan.
GRID = CELDA

#: Filas de la hoja: idle, walk, roll y death, cada uno en sus tres vistas.
FILAS = 12

#: Columnas de la hoja: el bloque mas largo del ciclo (walk) tiene 6 frames.
COLUMNAS = 6

#: Ancho y alto finales de la hoja: 6 y 12 celdas de 64 px.
ANCHO_HOJA = COLUMNAS * CELDA   # 384
ALTO_HOJA = FILAS * CELDA       # 768

#: Pixels por unidad de Unity (coherente con celda 64 -> 0.64 unidades).
PPU = CELDA

#: Ancla vertical del personaje dentro de la celda 64 (ultima fila opaca).
CELDA_PIE = 55

#: Eje horizontal del cuerpo dentro de la celda 64.
CELDA_CENTRO = 31.5

#: Alto en celdas del cuerpo del personaje en idle y walk.
ALTO_CELDAS = 47

#: Numero de filas de la celda que ocupa la altura del personaje.
FACTOR = LIENZO // GRID  # 12

#: Factores de escala que conectan coordenadas crudas (768) con la celda (64).
RAW_ALTO_OBJETIVO = ALTO_CELDAS * FACTOR      # 564
RAW_PIE_Y = CELDA_PIE * FACTOR + FACTOR - 1   # 671
RAW_CENTRO_X = CELDA_CENTRO * FACTOR         # 378

#: Paleta de destino: 32 colores de la referencia.
MAX_COLORES = 32

#: Pasos de difusion por defecto. Son los de `generar_sprite`, que es donde se
#: calibro la referencia; `--pasos` puede subirlos para un smoke mas fino.
PASOS = gs_base.PASOS

#: Guidance por defecto: alto, pero sin lavar el estilo de la referencia.
GUIDANCE = gs_base.GUIDANCE

#: Semaforos del control de calidad.
QC_ALTO_TOL = 3
#: La cobertura se reporta siempre, pero solo se rechaza por exceso: un
#: personaje tumbado en `death` o encogido en `roll` deja menos celdas ocupadas.
QC_COBERTURA_MAX = 0.40
QC_PIE_TOL = 1
QC_CENTRO_TOL = 1.0
QC_PESO_CROMATICO = 0.70
QC_DEBRIS_MAX = 0.05
QC_IOU = (0.80, 0.96)

#: Duraciones de los clips (ms), derivadas del ritmo de cada fila.
DURACION_IDLE = 167   # 4 fps nominales de fila: 1000 / 6
DURACION_WALK = 125   # 8 fps
DURACION_ROLL = 83    # 12 fps
DURACION_DEATH = 125  # 8 fps

#: Fotogramas por clip del `frames.json` de Unity, heredados de la hoja legacy
#: de 21 frames: cada vista del idle se queda con 3 y cada vista del walking
#: con 4. La hoja nueva genera mas (4 y 6 por vista); el importador de Unity
#: ya estaba calibrado para estos conteos.
FRAMES_CLIP_UNITY = {"idle": 3, "walking": 4}

#: Rutas.
RAIZ = Path(__file__).resolve().parent
RUTA_SALIDA = RAIZ / "salida"
RUTA_REFERENCIA = RAIZ / "sprite_referencia" / "sprite_3.png"

#: Tile nativo del PNG de referencia. Es un asset fijo de 128x128, anterior al
#: grid de 64, asi que su escala al lienzo sale de SU tamano y no de `FACTOR`
#: (que ya no divide: `FACTOR` convierte celda -> lienzo, no referencia -> lienzo).
TAMANO_REFERENCIA = 128
FACTOR_REFERENCIA = LIENZO // TAMANO_REFERENCIA  # 6

#: Huella de la referencia aprobada. El QC y el IP-Adapter parten de este archivo
#: concreto: si cambia, la hoja se ha generado contra otro criterio y el QC deja
#: de significar lo que dice. Se comprueba al copiarlo al destino.
SHA_REFERENCIA = "C653FC8F1ED07EDC8FB8923CDCA0D41CB9D726A5D8AD69958A02BF193532D039"

#: Modelos (identidades de Hugging Face).
MODELO_SDXL = "stabilityai/stable-diffusion-xl-base-1.0"
LORA_PIXEL_ART = "nerijs/pixel-art-xl"
CTRLNET_OPENPOSE = "xinsir/controlnet-openpose-sdxl-1.0"
IP_ADAPTER_REPO = "h94/IP-Adapter"

#: Peso del IP-Adapter sobre el prompt: manda la referencia sin lavar el texto.
IP_ADAPTER_PESO = 0.6


# --- Estructuras --------------------------------------------------------


#: Traduccion de las tres vistas de la hoja a los nombres de carpeta legacy.
#: La hoja es logica (`down`/`up`/`side`); las carpetas y el manifiesto antiguo
#: los llamaban `frontal`/`trasera`/`lateral`.
VISTA_A_LEGACY = {"down": "frontal", "up": "trasera", "side": "lateral"}
VISTA_DESDE_LEGACY = {v: k for k, v in VISTA_A_LEGACY.items()}

#: Traduccion de los nombres de animacion legacy a los canonicos. `Frame` acepta
#: ambos, asi que quien llame con "walking" sigue funcionando; lo canonico es
#: "walk", que es el nombre de la animacion en BODY-25 y en el manifiesto.
ANIMACION_DESDE_LEGACY = {
    "walking": "walk",
    "idle": "idle",
    "roll": "roll",
    "death": "death",
}
ANIMACION_A_LEGACY = {v: k for k, v in ANIMACION_DESDE_LEGACY.items()}


def animacion_legacy_de_manifiesto(animacion: str) -> str:
    """Nombre con el que la carpeta de la hoja nombra una animacion.

    El manifiesto habla canonico ("walk") pero las carpetas que consume Unity se
    llaman como las llamo la version legacy, asi que la conversion vive aqui.
    """
    return ANIMACION_A_LEGACY.get(animacion, animacion)


def _imagen_por_defecto() -> np.ndarray:
    """Celda vacia de 64x64x4, la imagen por defecto de un `Frame` sin pixel."""
    return np.zeros((CELDA, CELDA, 4), dtype=np.uint8)


@dataclass(frozen=True)
class FilaHoja:
    """Una fila de la hoja: una animacion vista desde una direccion.

    La hoja es una rejilla irregular: cada fila declara cuantos frames tiene,
    a que ritmo se reproduce y si vuelve al inicio. De ahi salen el ancho
    (el maximo de frames de la hoja) y la duracion de cada frame.
    """

    animacion: str
    vista: str
    frames: int
    fps: int
    bucle: bool
    fila: int

    @property
    def duracion_ms(self) -> int:
        return round(1000 / self.fps)

    @property
    def frames_iniciales(self) -> int:
        """Cuantos frames de la hoja hay por encima de esta fila."""
        return sum(f.frames for f in TABLA_FILAS if f.fila < self.fila)


def _construir_tabla() -> tuple[FilaHoja, ...]:
    """Las 12 filas de la hoja, en orden de lectura."""
    filas: list[FilaHoja] = []
    for animacion, frames, fps, bucle in (
        ("idle", 4, 6, True),
        ("walk", 6, 8, True),
        ("roll", 4, 12, False),
        ("death", 5, 8, False),
    ):
        for vista in ("down", "up", "side"):
            filas.append(
                FilaHoja(
                    animacion=animacion,
                    vista=vista,
                    frames=frames,
                    fps=fps,
                    bucle=bucle,
                    fila=len(filas),
                )
            )
    return tuple(filas)


#: Las 12 filas de la hoja: 3 vistas de idle, walk, roll y death.
TABLA_FILAS: tuple[FilaHoja, ...] = _construir_tabla()

#: Indice de busqueda `(animacion, vista)` -> fila, para no recorrer la tabla.
_FILA_DE = {(f.animacion, f.vista): f for f in TABLA_FILAS}


@dataclass(frozen=True)
class GeometriaCelda:
    """Caja esperada del personaje dentro de la celda de 64 px."""

    alto: int
    ancho: int
    pie: int
    alto_tol: int


def _geometria_alto(alto: int, ancho: int, pie: int) -> GeometriaCelda:
    return GeometriaCelda(alto=alto, ancho=ancho, pie=pie, alto_tol=1)


def _construir_geometrias() -> dict[tuple[str, int], GeometriaCelda]:
    """La caja esperada de cada una de las 57 celdas.

    `idle` y `walk` comparten cuerpo erguido (47x24); `roll` es una figura
    tumbada y estrecha; `death` cae progresivamente hasta quedar tendida. La
    tolerancia de alto es 1 px porque el borde del sprite es blando.
    """
    geoms: dict[tuple[str, int], GeometriaCelda] = {}

    for indice in range(1, 5):
        geoms[("idle", indice)] = _geometria_alto(47, 24, 55)
    for indice in range(1, 7):
        geoms[("walk", indice)] = _geometria_alto(47, 24, 55)
    for indice in range(1, 5):
        geoms[("roll", indice)] = _geometria_alto(18, 22, 30)

    # La caida se queda PEGADA al suelo: el pie no sube, lo que baja es la
    # cabeza (el `alto` se encoge) y lo que crece es el `ancho` porque el
    # cuerpo se tumba de lado. Asi el personaje colapsa en vez de flotar y se
    # cumple `pie - alto + 1 >= 0` en los cinco fotogramas.
    death = {
        1: _geometria_alto(47, 24, 53),
        2: _geometria_alto(45, 24, 53),
        3: _geometria_alto(32, 20, 53),
        4: _geometria_alto(24, 26, 53),
        5: _geometria_alto(18, 30, 53),
    }
    geoms.update({("death", indice): g for indice, g in death.items()})
    return geoms


#: Caja esperada por `(animacion, indice)`: 19 geometrias distintas.
GEOMETRIA_CELDAS: dict[tuple[str, int], GeometriaCelda] = _construir_geometrias()


def geometria_de_frame(frame: Frame) -> GeometriaCelda:
    """Caja esperada de la celda de `frame`.

    Se indexa por animacion e indice, no por fila: las tres vistas de una
    animacion comparten geometria.
    """
    return GEOMETRIA_CELDAS[(frame.animacion, frame.indice)]


@dataclass(frozen=True)
class QC:
    """Veredicto del control de calidad de un frame 64x64x4."""

    ok: bool
    motivos: list[str] | tuple[str, ...]
    metricas: dict


@dataclass(frozen=True)
class Frame:
    """Una celda de la hoja: vista, animacion, indice, duracion y bucle.

    `vista` y `animacion` se guardan en su forma logica, aunque se construya
    el frame con los nombres legacy (`frontal`, `walking`): `vista_legacy` los
    traduce de vuelta para las rutas de carpetas. `fila`, `columna` y
    `global_index` salen de `TABLA_FILAS`, no se pasan.
    """

    vista: str
    animacion: str
    indice: int
    duracion_ms: int
    bucle: bool
    imagen: np.ndarray = field(default_factory=_imagen_por_defecto)

    def __post_init__(self) -> None:
        # Los nombres legacy se normalizan en el frozen dataclass: asignar por
        # atributo es error, hay que pasar por `object.__setattr__`.
        object.__setattr__(self, "vista", VISTA_DESDE_LEGACY.get(self.vista, self.vista))
        object.__setattr__(
            self, "animacion", ANIMACION_DESDE_LEGACY.get(self.animacion, self.animacion)
        )

    @property
    def clave(self) -> str:
        """Identificador estable, p. ej. ``down_idle_1``."""
        return f"{self.vista}_{self.animacion}_{self.indice}"

    @property
    def fila_hoja(self) -> FilaHoja:
        return _FILA_DE[(self.animacion, self.vista)]

    @property
    def vista_legacy(self) -> str:
        """Nombre de carpeta de la hoja antigua."""
        return VISTA_A_LEGACY[self.vista]

    @property
    def fila(self) -> int:
        return self.fila_hoja.fila

    @property
    def columna(self) -> int:
        return self.indice - 1

    @property
    def global_index(self) -> int:
        return self.fila_hoja.frames_iniciales + self.indice - 1

    @property
    def original(self) -> Frame:
        """El mismo frame con el nombre de vista que se le dio al construirlo.

        Lo usan las pruebas legacy, que comparan contra `original.imagen[:, ::-1]`
        para verificar el espejo horizontal.
        """
        return Frame(
            vista=self.vista_legacy,
            animacion=self.animacion,
            indice=self.indice,
            duracion_ms=self.duracion_ms,
            bucle=self.bucle,
            imagen=self.imagen,
        )


def _construir_matriz() -> tuple[Frame, ...]:
    """Los 57 frames de la hoja, en orden de lectura."""
    celdas: list[Frame] = []
    for fila in TABLA_FILAS:
        for indice in range(1, fila.frames + 1):
            celdas.append(
                Frame(
                    vista=fila.vista,
                    animacion=fila.animacion,
                    indice=indice,
                    duracion_ms=fila.duracion_ms,
                    bucle=fila.bucle,
                )
            )
    return tuple(celdas)


#: Las 57 celdas de la hoja, en orden de lectura.
MATRIZ: tuple[Frame, ...] = _construir_matriz()


@dataclass(frozen=True)
class ResultadoCelda:
    """Estado final de una celda tras generar y pasar (o no) el QC."""

    frame: Frame
    estado: str  # "ok" | "pendiente"
    imagen: np.ndarray | None
    intentos: int = 0
    qc: QC | None = None


# --- Paleta -------------------------------------------------------------


def paleta_rgb() -> list[tuple[int, int, int]]:
    """Paleta de 32 colores RGB de la referencia.

    `generar_sprite.PALETA` son hex de 6 digitos, no triplas: se convierten con
    su propio `hex_a_rgb` para no duplicar el parseo.
    """
    return [gs_base.hex_a_rgb(h) for h in gs_base.PALETA]


def paleta_lab() -> np.ndarray:
    """Misma paleta en OKLab como array (K,3) float, precalculado.

    `srgb_a_oklab` de `generar_sprite` mapea un array (...,3) uint8 a (...,3)
    float, asi que se le pasa un color por fila en vez de cuatro argumentos.
    """
    if not hasattr(paleta_lab, "_cache"):
        filas = np.array(paleta_rgb(), dtype=np.uint8).reshape(-1, 1, 3)
        paleta_lab._cache = gs_base.srgb_a_oklab(filas)[:, 0, :]
    return paleta_lab._cache


# --- Composicion de la pose --------------------------------------------


def componer_pose_sobre_negro(rgba: np.ndarray) -> np.ndarray:
    """Compone una pose RGBA sobre un lienzo RGB negro.

    Los pixeles con alfa 0 se vuelven negro puro, nunca conservan su RGB
    oculto: ese RGB se filtraria al conditioning de ControlNet como color.
    """
    if rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError(f"se esperaba RGBA, vino {rgba.shape}")
    alfa = rgba[..., 3:4].astype(np.float32) / 255.0
    color = rgba[..., :3].astype(np.float32)
    return np.clip(color * alfa, 0, 255).astype(np.uint8)


# --- Componentes conexas y debris --------------------------------------


def _etiquetas(mascara: np.ndarray, conectividad: int = 4) -> tuple[np.ndarray, int]:
    """Etiquetas de componentes conexas de una mascara binaria.

    Implementacion en NumPy puro: dos pasadas de propagacion de etiquetas.
    `conectividad=4` une solo lados; `8` une tambien las diagonales.
    """
    alto, ancho = mascara.shape
    etiquetas = np.zeros((alto, ancho), dtype=np.int32)
    actual = 0
    vecinos4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
    vecinos8 = vecinos4 + ((-1, -1), (-1, 1), (1, -1), (1, 1))
    vecinos = vecinos4 if conectividad == 4 else vecinos8

    for y in range(alto):
        for x in range(ancho):
            if not mascara[y, x] or etiquetas[y, x]:
                continue
            actual += 1
            etiquetas[y, x] = actual
            pila = [(y, x)]
            while pila:
                cy, cx = pila.pop()
                for dy, dx in vecinos:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < alto and 0 <= nx < ancho:
                        if mascara[ny, nx] and not etiquetas[ny, nx]:
                            etiquetas[ny, nx] = actual
                            pila.append((ny, nx))
    return etiquetas, actual


def _componentes_y_debris(
    alpha: np.ndarray, conectividad: int = 4
) -> tuple[int, float]:
    """Numero de componentes conexas y fraccion de pixeles fuera de la mayor.

    Etiqueta una sola vez la mascara: `metricas_sprite` necesita el recuento y
    `debris` el reparto, asi que calcularlo aqui evita repetir el BFS.
    """
    etiquetas, total = _etiquetas(np.asarray(alpha) > 0, conectividad)
    if total == 0:
        return 0, 1.0
    conteo = np.bincount(etiquetas.ravel(), minlength=total + 1)
    conteo = conteo[1:]
    mayor = int(np.argmax(conteo))
    return total, float(conteo.sum() - conteo[mayor]) / float(conteo.sum())


def componentes_conectados(alpha: np.ndarray, conectividad: int = 4) -> int:
    """Numero de componentes conexas de la mascara alfa."""
    return _componentes_y_debris(alpha, conectividad)[0]


def debris(alpha: np.ndarray, conectividad: int = 4) -> float:
    """Fraccion de pixeles opacos fuera del componente mayor.

    Es la fraccion de `alpha` que no pertenece al cuerpo principal: chispas,
    motas de bruit y restos de fondo. Un sprite limpio vale 0.0.
    """
    return _componentes_y_debris(alpha, conectividad)[1]


# --- Anclaje y normalizacion -------------------------------------------


# Indices de BODY_25 segun `POSE_BODY_25_BODY_PARTS` de OpenPose
# (src/openpose/pose/poseParameters.cpp). Ojo: el cuerpo va despues del rostro
# y solo al final los pies, asi que los numeros NO son agrupados por region.
# Los indices 7, 8, 15 y 16 son LWrist, MidHip, REye y LEye.

#: Articulaciones que tocan el suelo: los dos tobillos y los seis puntos de pie
#: (dedo gordo, punta secundaria y talon de cada lado).
PIES_BODY_25 = (11, 14, 19, 20, 21, 22, 23, 24)

#: Articulaciones de la pelvis: la cadera media y las dos caderas. Sus columnas
#: promediadas dan el eje horizontal del cuerpo.
CADERAS_BODY_25 = (8, 9, 12)


def ancla_de_esqueleto(joints: dict[int, tuple[float, float]]) -> tuple[float, float]:
    """Extrae el anclaje del suelo y el eje del cuerpo de una pose BODY_25.

    BODY_25 viene en coordenadas `(y, x)`, no `(x, y)`: el pie es la fila mas
    baja de los tobillos y dedos (11, 14, 19-24) y, si no hay ninguna, la
    articulacion mas baja de la pose. La pelvis (8 MidHip, 9 RHip, 12 LHip) da
    el eje y se promedia en X para que el personaje quede centrado. Devuelve
    `(eje_x, pie_y)` en pixeles crudos.
    """
    if not joints:
        return (RAW_CENTRO_X, RAW_PIE_Y)

    candidatos = [joints[i] for i in PIES_BODY_25 if i in joints]
    if candidatos:
        pie_y = float(max(y for y, _ in candidatos))
    else:
        pie_y = float(max(y for y, _ in joints.values()))

    caderas = [joints[i] for i in CADERAS_BODY_25 if i in joints]
    if caderas:
        eje_x = float(np.mean([x for _, x in caderas]))
    else:
        eje_x = float(np.mean([x for _, x in joints.values()]))
    return (eje_x, pie_y)


def _bbox_alfa(alpha: np.ndarray) -> tuple[int, int, int, int] | None:
    filas = np.nonzero(alpha.any(axis=1))[0]
    columnas = np.nonzero(alpha.any(axis=0))[0]
    if filas.size == 0 or columnas.size == 0:
        return None
    return (int(filas[0]), int(filas[-1]), int(columnas[0]), int(columnas[-1]))


def normalizar_para_reduccion(
    rgba: np.ndarray,
    eje_x: float,
    pie_y: int,
    lienzo: int = LIENZO,
    grid: int = GRID,
    alto_celdas: int = ALTO_CELDAS,
    celda_pie: int = CELDA_PIE,
    celda_centro: float = CELDA_CENTRO,
) -> np.ndarray:
    """Coloca el personaje sobre el lienzo para que al reducir cuadre el QC.

    La escala sale SOLO de la altura del recorte: `alto_objetivo / alto_recorte`.
    Si el ancho resultante no cabe, se limita la escala (y con ella el alto) en
    vez de recortar margen vertical. `pie_y` es la ultima fila opaca del sujeto
    y se ancla a la fila `celda_pie`; `eje_x` se ancla al centro de la celda.
    """
    if rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError(f"se esperaba RGBA, vino {rgba.shape}")

    if lienzo % grid != 0:
        raise ValueError("el lienzo debe ser multiplo del grid")

    alfa = rgba[..., 3] > 0
    caja = _bbox_alfa(alfa)
    if caja is None:
        return np.zeros((lienzo, lienzo, 4), dtype=np.uint8)

    f0, f1, c0, c1 = caja
    alto_recorte = f1 - f0 + 1
    ancho_recorte = c1 - c0 + 1

    # Objetivo en pixeles crudos: las celdas objetivos translates a raw.
    factor = lienzo // grid
    alto_obj = alto_celdas * factor          # 684
    pie_obj = celda_pie * factor + factor - 1  # 725
    centro_obj = celda_centro * factor        # 381

    escala = alto_obj / alto_recorte
    ancho_escalado = ancho_recorte * escala
    if ancho_escalado > lienzo:
        escala = lienzo / ancho_recorte
        alto_escalado = alto_recorte * escala

    nuevo_alto = max(int(round(alto_recorte * escala)), 1)
    nuevo_ancho = max(int(round(ancho_recorte * escala)), 1)
    nuevo_alto = min(nuevo_alto, lienzo)
    nuevo_ancho = min(nuevo_ancho, lienzo)

    recorte = rgba[f0 : f1 + 1, c0 : c1 + 1]
    escalado = _redimensionar(recorte, nuevo_alto, nuevo_ancho)

    # Anclaje: se desplaza el recorte para que la articulacion que dio la escala
    # (`pie_y`, `eje_x`, en pixeles del recorte) caiga en la celda objetivo.
    offset_x = (eje_x - c0) * nuevo_ancho / ancho_recorte
    offset_y = (pie_y - f0) * nuevo_alto / alto_recorte
    left = int(round(centro_obj - offset_x))
    top = int(round(pie_obj - offset_y))
    left = int(min(max(left, 0), lienzo - nuevo_ancho))
    top = int(min(max(top, 0), lienzo - nuevo_alto))

    lienzo_final = np.zeros((lienzo, lienzo, 4), dtype=np.uint8)
    lienzo_final[top : top + nuevo_alto, left : left + nuevo_ancho] = escalado
    return lienzo_final


def _redimensionar(rgba: np.ndarray, alto: int, ancho: int) -> np.ndarray:
    """Resize nearest-neighbour de un recorte RGBA, sin depender de OpenCV."""
    if rgba.shape[0] == alto and rgba.shape[1] == ancho:
        return rgba
    img = Image.fromarray(rgba, mode="RGBA")
    return np.array(img.resize((ancho, alto), resample=Image.NEAREST))


def escalar_sprite(sprite: np.ndarray, factor: float) -> np.ndarray:
    """Escala un sprite 128x128x4 para las pruebas de QC."""
    alto = max(int(round(sprite.shape[0] * factor)), 1)
    ancho = max(int(round(sprite.shape[1] * factor)), 1)
    return _redimensionar(sprite, alto, ancho)


def cuantizar_y_reducir(
    lienzo_rgba: np.ndarray,
    paleta: list[tuple[int, int, int]] | None = None,
    lab: np.ndarray | None = None,
    grid: int = GRID,
) -> np.ndarray:
    """Reduce un lienzo 768x768x4 a una celda 128x128x4 cuantizada.

    Tres pasos, todos con los helpers de `generar_sprite`:
      1. Cuantizar el lienzo entero a la paleta de 32 colores en OKLab
         (`color_mas_cercano` devuelve el indice, no el color).
      2. Reducir por votacion a `grid` (`reducir_por_votacion`), que ademas
         devuelve la cobertura de cada celda destino.
      3. Alfa binaria con cobertura >= 0.5 y `despeckle` para matar el ruido.
    """
    if lienzo_rgba.ndim != 3 or lienzo_rgba.shape[2] != 4:
        raise ValueError(f"se esperaba RGBA, vino {lienzo_rgba.shape}")
    if lienzo_rgba.shape[0] % grid or lienzo_rgba.shape[1] % grid:
        raise ValueError("el lienzo debe ser multiplo del grid")

    paleta = paleta if paleta is not None else paleta_rgb()
    lab = paleta_lab() if lab is None else np.asarray(lab, dtype=np.float32)

    alto, ancho = lienzo_rgba.shape[:2]
    rgb = lienzo_rgba[..., :3].reshape(-1, 1, 3)
    opaco = (lienzo_rgba[..., 3] > 0).reshape(-1)
    indices = np.zeros(alto * ancho, dtype=np.int64)
    if opaco.any():
        pixeles = gs_base.srgb_a_oklab(rgb[opaco])[:, 0, :]
        indices[opaco] = gs_base.color_mas_cercano(lab, pixeles)

    alpha01 = (lienzo_rgba[..., 3].astype(np.float32) / 255.0)
    celda_idx, cobertura = gs_base.reducir_por_votacion(
        indices.reshape(alto, ancho), alpha01, grid, len(paleta)
    )
    alfa = np.where(cobertura >= 0.5, 255, 0).astype(np.uint8)
    celda_idx, alfa = gs_base.despeckle(celda_idx, alfa)

    celda = np.zeros((grid, grid, 4), dtype=np.uint8)
    opaco_celda = alfa > 0
    tabla = np.array(paleta, dtype=np.uint8)
    celda[..., :3][opaco_celda] = tabla[celda_idx[opaco_celda]]
    celda[..., 3] = alfa
    return celda


# --- QC -----------------------------------------------------------------


def metricas_sprite(rgba: np.ndarray) -> dict:
    """Metricas de un sprite RGBA: dimensiones, cobertura, color y forma.

    Acepta cualquier tamano y devuelve las medidas en pixeles de la imagen
    recibida: la celda es de GRID (64) px, pero la referencia es de 128 y el QC
    tambien se aplica a frames escalados, p. ej. 205x205. La cobertura y el
    numero de colores se miden sobre el area real recibida, no sobre la celda.
    """
    sprite = np.asarray(rgba)
    if sprite.ndim != 3 or sprite.shape[2] != 4:
        raise ValueError(f"se esperaba RGBA, vino {sprite.shape}")
    alto_img, ancho_img = sprite.shape[:2]
    alfa = sprite[..., 3] > 0
    total = alto_img * ancho_img
    valores_alfa = np.unique(sprite[..., 3])
    if not alfa.any():
        return {
            "alto": 0, "ancho": 0, "pie": None, "centro_x": None,
            "cobertura": 0.0, "n_colores": 0, "componentes": 0,
            "debris_pct": 1.0, "alfa_binaria": True, "iou_anterior": None,
            "pesos": {},
        }
    bbox = _bbox_alfa(alfa)
    if bbox is None:
        raise ValueError("bbox inesperado: hay alfa opaco pero _bbox_alfa no lo encontro")
    f0, f1, c0, c1 = bbox
    filas, columnas = (f0, f1), (c0, c1)
    n_componentes, debris_pct = _componentes_y_debris(alfa)
    pixeles = sprite[alfa][:, :3]
    # Un solo `unique` da colores y pesos: etiquetar una vez, no recorrer pixeles.
    unicos, conteo = np.unique(pixeles, axis=0, return_counts=True)
    pesos = {
        (int(px[0]), int(px[1]), int(px[2])): int(n)
        for px, n in zip(unicos.tolist(), conteo.tolist())
    }
    return {
        "alto": int(filas[1] - filas[0] + 1),
        "ancho": int(columnas[1] - columnas[0] + 1),
        "pie": int(filas[1]),
        "centro_x": float((columnas[0] + columnas[1]) / 2.0),
        "cobertura": int(alfa.sum()) / total,
        "n_colores": int(len(unicos)),
        "componentes": n_componentes,
        "debris_pct": debris_pct,
        "alfa_binaria": bool(set(valores_alfa.tolist()) <= {0, 255}),
        "iou_anterior": None,
        "pesos": pesos,
    }


def _peso_cromatico_compartido(a: dict, b: dict) -> float:
    """Fraccion del peso cromatico de `a` que aparece en `b`."""
    if not a:
        return 1.0
    total = sum(a.values())
    comun = sum(peso for clave, peso in a.items() if clave in b)
    return comun / total if total else 1.0


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    interseccion = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(interseccion / union) if union else 1.0


def _motivos_legacy(metricas: dict) -> list[str]:
    """Motivos del QC sin `frame`: forma, color y exceso de cobertura.

    Sin `frame` no hay caja declarada que comparar, y medirla contra la
    referencia descalifica de antemano media hoja: `roll` va tumbado y
    `death` cayendo. El legacy se queda con lo que el QC siempre pudo
    afirmar por si mismo, con los textos largos que leia el log.
    """
    motivos: list[str] = []

    if metricas["pie"] is None:
        motivos.append("sprite vacio")
    if metricas["cobertura"] > QC_COBERTURA_MAX:
        motivos.append(f"cobertura {metricas['cobertura']:.3f} supera {QC_COBERTURA_MAX}")
    if metricas["n_colores"] > MAX_COLORES:
        motivos.append(f"n_colores {metricas['n_colores']} supera {MAX_COLORES}")
    if not metricas["alfa_binaria"]:
        motivos.append("alfa no es binaria")
    if metricas["componentes"] != 1:
        motivos.append(f"componentes {metricas['componentes']} != 1")
    if metricas["debris_pct"] >= QC_DEBRIS_MAX:
        motivos.append(f"debris {metricas['debris_pct']:.3f} >= {QC_DEBRIS_MAX}")
    return motivos


def _motivos_celda(metricas: dict) -> tuple[str, ...]:
    """Motivos de forma de la celda en modo `frame`, como codigos cortos."""
    codigos: list[str] = []
    if metricas["cobertura"] > QC_COBERTURA_MAX:
        codigos.append("cobertura")
    if metricas["n_colores"] > MAX_COLORES:
        codigos.append("n_colores")
    if not metricas["alfa_binaria"]:
        codigos.append("alfa")
    if metricas["componentes"] != 1:
        codigos.append("componentes")
    if metricas["debris_pct"] >= QC_DEBRIS_MAX:
        codigos.append("debris")
    return tuple(codigos)


def _motivo_geometrico(metricas: dict, geometria: GeometriaCelda) -> str | None:
    """Primer fallo de forma de celda, o `None` si la caja encaja.

    El alto esperado se recorta a `pie + 1` porque la caja declarada es la
    Teorica: en `death` 3-5 la figura esta tumbada y la celda solo puede
    mostrar la parte que cae dentro. Un motivo por vez: si el alto no encaja,
    el pie tampoco es comparable y solo se reporta el alto.
    """
    if metricas["pie"] is None:
        return "pie"
    alto_esperado = min(geometria.alto, geometria.pie + 1)
    if abs(metricas["alto"] - alto_esperado) > geometria.alto_tol:
        return "alto"
    if abs(metricas["pie"] - geometria.pie) > geometria.alto_tol:
        return "pie"
    return None


def qc_frame(rgba: np.ndarray, ref: dict, frame: Frame | None = None) -> QC:
    """Control de calidad de un frame RGBA de la celda de 64 px.

    Sin `frame` el QC solo puede afirmar lo que el sprite dice de si mismo
    (forma, color, ruido, exceso de cobertura) y devuelve los motivos como
    lista, con su texto largo. Con `frame` ademas se compara la caja con la
    geometria declarada de la animacion (`GEOMETRIA_CELDAS`) y los motivos
    son codigos cortos en tupla, para que quien decide el reintento pueda
    compararlos sin texto.

    `ref` ya no decide nada, pero se conserva como parametro y se usa para
    reportar el diagnostico de peso cromatico compartido. Devuelve un `QC`
    con `.ok`, `.motivos` y `.metricas`; nunca lanza por un sprite malo,
    solo informa.
    """
    metricas = metricas_sprite(rgba)

    if frame is None:
        motivos: list[str] | tuple[str, ...] = _motivos_legacy(metricas)
    else:
        codigo = _motivo_geometrico(metricas, geometria_de_frame(frame))
        motivos = (codigo,) if codigo else _motivos_celda(metricas)

    metricas = dict(metricas)
    metricas["peso_cromatico_compartido"] = _peso_cromatico_compartido(
        metricas["pesos"], ref.get("pesos", {})
    )
    return QC(ok=not motivos, motivos=motivos, metricas=metricas)


def _mascara_alfa(sprite: np.ndarray) -> np.ndarray:
    """Mascara booleana de los pixeles opacos de un sprite RGBA."""
    return np.asarray(sprite)[..., 3] > 0


class SecuenciaTemporal:
    """Control de calidad temporal: ademas del balanceo, el salto entre frames.

    `qc_frame` juzga cada celda por separado y no puede responder a la pregunta
    que de verdad delata una hoja muerta: si el fotograma se parece al anterior.
    Este envoltorio mide la IoU contra el ultimo sprite ACEPTADO de la misma
    secuencia `(vista, animacion)` y deja el veredicto dentro de la banda
    `QC_IOU`.

    La referencia solo avanza cuando el frame es aceptado: un rechazo no pasa a
    ser referencia, porque medir contra un fotograma malo acabaria dejando pasar
    al siguiente. Si el QC base falla, este verificador devuelve ese veredicto
    tal cual y no memoriza nada.

    La banda solo se aplica entre fotogramas de la MISMA caja canonica: si la
    caja del frame entrante difiere de la del ultimo aceptado, el cambio lo
    impone la animacion (p. ej. el colapso de la caida 47->45->32->24->18) y la
    IoU contra el fotograma anterior no delata una hoja muerta, asi que el frame
    se acepta sin medir. El balanceo de idle/walk/roll, donde la caja es
    constante, sigue sujeto a la banda.
    """

    def __init__(self, verificador):
        self._verificador = verificador
        self._ultimo_aceptado: dict[tuple[str, str], tuple[GeometriaCelda, np.ndarray]] = {}

    def verificar(self, frame: Frame, sprite: np.ndarray) -> QC:
        qc = self._verificador(sprite)
        if not qc.ok:
            qc.metricas.setdefault("iou_anterior", None)
            return qc

        clave = (frame.vista, frame.animacion)
        geometria = geometria_de_frame(frame)
        mascara = _mascara_alfa(sprite)
        metricas = dict(qc.metricas)
        anterior = self._ultimo_aceptado.get(clave)

        if anterior is None:
            metricas["iou_anterior"] = None
            self._ultimo_aceptado[clave] = (geometria, mascara)
            return QC(ok=True, motivos=[], metricas=metricas)

        geometria_anterior, mascara_anterior = anterior
        if geometria != geometria_anterior:
            metricas["iou_anterior"] = None
            self._ultimo_aceptado[clave] = (geometria, mascara)
            return QC(ok=True, motivos=[], metricas=metricas)

        iou = _iou(mascara, mascara_anterior)
        metricas["iou_anterior"] = iou
        minimo, maximo = QC_IOU
        if iou < minimo:
            return QC(ok=False, motivos=[f"iou {iou:.3f} < {minimo}"], metricas=metricas)
        if iou > maximo:
            return QC(ok=False, motivos=[f"iou {iou:.3f} > {maximo}"], metricas=metricas)

        self._ultimo_aceptado[clave] = (geometria, mascara)
        return QC(ok=True, motivos=[], metricas=metricas)


#: Metricas de la referencia_APROBADA, las que gobiernan el QC por defecto. Se
#: rellena al importar el modulo: el QC se consulta desde las pruebas y desde
#: cualquier script con `gs.REFERENCIA`, y un diccionario vacio haria que toda
#: consulta fallara por `KeyError` en vez de fallar por su motivo real.
REFERENCIA: dict = {}


def metricas_de_referencia(ruta: Path | str = RUTA_REFERENCIA) -> dict:
    """Metricas del PNG de referencia que se indique, sin cachear nada.

    Es la version sin efecto secundario de `cargar_referencia`: calcula de
    nuevo y devuelve un diccionario propio. Importa que no escriba en
    `REFERENCIA`, porque `--referencia otro.png` cambia los umbrales del QC
    durante esa tanda y al terminar la global tiene que seguir siendo el
    criterio aprobado, no el rectangulo con el que se estuvo probando.
    """
    sprite = np.array(Image.open(Path(ruta)).convert("RGBA"))
    return metricas_sprite(sprite)


def cargar_referencia() -> dict:
    """Carga la referencia aprobada y calcula sus metricas una sola vez."""
    global REFERENCIA
    if not REFERENCIA:
        REFERENCIA = metricas_de_referencia(RUTA_REFERENCIA)
    return REFERENCIA


#: Se calcula al importar para que `REFERENCIA` sea un criterio de verdad desde
#: el primer `qc_frame`, sin que cada consumidor recuerde llamar a la carga.
cargar_referencia()


# --- Semillas, reintentos y ensamblado --------------------------------


def semilla(personaje: str, vista: str, animacion: str, indice: int) -> int:
    """Seed determinista derivado de la identidad de la celda."""
    texto = f"{personaje}|{vista}|{animacion}|{indice}"
    digest = hashlib.sha256(texto.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


def generar_celda(
    frame: Frame,
    generar,
    qc,
    intentos: int = 3,
    personaje: str = "sombra_velada",
) -> ResultadoCelda:
    """Genera una celda con reintentos de semilla ascendente.

    `generar(seed) -> np.ndarray` produce un sprite 128x128x4; `qc(sprite) -> QC`
    lo evalua. Se prueban hasta `intentos` semillas `seed, seed+1, seed+2` y
    se queda con la primera que pase. Si ninguna pasa, la celda queda
    "pendiente" con su ultimo QC. `personaje` entra en la semilla: sin el, dos
    personajes compartirian el mismo ruido y solo cambiaria el prompt.
    """
    base = semilla(personaje, frame.vista, frame.animacion, frame.indice)
    mejor: QC | None = None
    imagen: np.ndarray | None = None
    for intento in range(1, intentos + 1):
        candidato = generar(base + intento - 1)
        veredicto = qc(candidato)
        if veredicto.ok:
            return ResultadoCelda(frame, "ok", candidato, intento, veredicto)
        mejor = veredicto
        imagen = candidato
    return ResultadoCelda(frame, "pendiente", imagen, intentos, mejor)


def ensamblar_spritesheet(
    celdas: list[np.ndarray] | np.ndarray,
    filas: int = FILAS,
    columnas: int = COLUMNAS,
    grid: int = GRID,
) -> np.ndarray:
    """Ensambla celdas en la hoja final `filas x columnas x grid`."""
    if isinstance(celdas, np.ndarray):
        celdas = list(celdas)
    esperado = filas * columnas
    if len(celdas) != esperado:
        raise ValueError(
            f"hacen falta {esperado} celdas para {filas}x{columnas}, "
            f"vienen {len(celdas)}"
        )
    for i, celda in enumerate(celdas):
        if celda.shape[:2] != (grid, grid):
            raise ValueError(f"celda {i} mide {celda.shape[:2]}, deberia ser {(grid, grid)}")
    hoja = np.zeros((filas * grid, columnas * grid, 4), dtype=np.uint8)
    for n, celda in enumerate(celdas):
        f, c = divmod(n, columnas)
        hoja[f * grid : (f + 1) * grid, c * grid : (c + 1) * grid] = celda
    return hoja


def armar_hoja(
    resultados: dict[str, ResultadoCelda],
    filas: int = FILAS,
    columnas: int = COLUMNAS,
    grid: int = GRID,
) -> np.ndarray:
    """Ensambla la hoja desde resultados por clave; falla si algo quedo pendiente.

    Cada celda se coloca en la posicion que dicta su `Frame` (`fila` y
    `columna`), no en el orden de las claves. La rejilla es 12x6=72 pero solo
    hay 57 frames: las filas de `idle`, `roll` y `death` dejan 2, 2 y 1 huecos
    por vista. Esos huecos se rellenan con celdas transparentes para que la
    hoja sea un rectangulo completo y Unity la recorte bien.
    """
    pendientes = [k for k, r in resultados.items() if r.estado != "ok"]
    if pendientes:
        raise ValueError(
            f"faltan {len(pendientes)} celdas pendientes: {', '.join(sorted(pendientes))}"
        )
    faltantes = [f.clave for f in MATRIZ if f.clave not in resultados]
    if faltantes:
        raise ValueError(f"faltan {len(faltantes)} celdas: {', '.join(faltantes)}")

    hueco = _imagen_por_defecto()
    if grid != CELDA:
        hueco = np.zeros((grid, grid, 4), dtype=np.uint8)
    rejilla = [[hueco] * columnas for _ in range(filas)]
    for frame in MATRIZ:
        rejilla[frame.fila][frame.columna] = resultados[frame.clave].imagen
    celdas = [celda for fila in rejilla for celda in fila]
    return ensamblar_spritesheet(celdas, filas, columnas, grid)


# --- Poses OpenPose (Fase 2) -------------------------------------------


def _esqueleto_bodies25() -> list[tuple[int, int]]:
    """Pares (a, b) de los huesos BODY_25, segun `getPosePartPairs`.

    Reproduce la lista oficial de OpenPose para `PoseModel::BODY_25`, con los
    indices de `POSE_BODY_25_BODY_PARTS`: 0 nariz, 1 cuello, 2-4 brazo derecho,
    5-7 brazo izquierdo, 8 cadera media, 9-11 pierna derecha, 12-14 pierna
    izquierda, 15-18 ojos y oidos, 19-21 pie izquierdo, 22-24 pie derecho.

    Los enlaces hombro-oido (2, 17) y (5, 18) son parte del render oficial: el
    ControlNet se entreno sobre esas imagenes, asi que se respetan.
    """
    return [
        (1, 8), (1, 2), (1, 5),                            # cuello y hombros
        (2, 3), (3, 4), (5, 6), (6, 7),                    # brazos
        (8, 9), (9, 10), (10, 11),                        # pierna derecha
        (8, 12), (12, 13), (13, 14),                      # pierna izquierda
        (14, 19), (19, 20), (14, 21),                     # pie izquierdo
        (11, 22), (22, 23), (11, 24),                     # pie derecho
        (1, 0), (0, 15), (15, 17), (0, 16), (16, 18),     # cabeza
        (2, 17), (5, 18),                                  # hombro-oido
    ]


def _escala_joints(joints, factor, canvas=1024):
    """Escala joints normalizados 0..1 a pixels de un canvas de `canvas` px.

    Los joints llegan y se devuelven en el orden `(y, x)` de BODY_25, que es el
    que espera `ancla_de_esqueleto`; aqui no se invierte nada. Tampoco se centra:
    el encuadre de la pose lo fija quien la define, y un offset inventado
    descolocaria el suelo respecto al anclaje real.
    """
    return {i: (y * factor * canvas, x * factor * canvas) for i, (y, x) in joints.items()}


def _dibujar_pose(pose_dict: dict, canvas: int = 1024, ancho_hueso: int = 16) -> np.ndarray:
    """Renderiza una pose OpenPose (diccionario de joints) a una imagen RGB.

    `pose_dict` mapea indice de joint a `(y, x)`, el orden de BODY_25. La
    transposicion a `(x, y)` ocurre aqui y solo aqui, en el borde con PIL, que
    indexa por columna y fila. Los huesos se dibujan como lineas magenta de
    OpenPose y los joints como cruces. Devuelve un array RGB
    `canvas x canvas x 3` sobre fondo negro.
    """
    from PIL import ImageDraw

    img = Image.new("RGB", (canvas, canvas), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    magenta = (255, 0, 255)
    # PIL espera (x, y): se transpone al dibujar, no antes, para que el resto
    # de la cadena siga hablando el idioma de OpenPose.
    xy = {i: (x, y) for i, (y, x) in pose_dict.items()}
    for a, b in _esqueleto_bodies25():
        if a in xy and b in xy:
            draw.line([xy[a], xy[b]], fill=magenta, width=ancho_hueso)
    for x, y in xy.values():
        r = ancho_hueso // 2
        draw.line([(x - r, y), (x + r, y)], fill=magenta, width=ancho_hueso)
        draw.line([(x, y - r), (x, y + r)], fill=magenta, width=ancho_hueso)
    return np.array(img)


# --- Poses por frame ----------------------------------------------------


#: Y normalizada de la planta del pie. El 4,5 % de abajo del lienzo queda
#: libre para que el ControlNet no pegue el personaje al borde de la celda.
POSE_SUELO_Y = 0.955

#: Separacion maxima entre las dos plantas para darlas por emparejadas. Por
#: debajo de este margen los dos pies estan en el suelo y la respuesta deja de
#: distinguir uno de otro, que es el caso de los tres idles.
POSE_SUELO_TOL = 0.02

#: Cadenas de cada pierna, de cadera a punta. Sirven para responder "que pie
#: apoya", que es lo que separa un ciclo de marcha de un balanceo en el sitio.
PIERNA_DERECHA = (9, 10, 11, 22, 23, 24)
PIERNA_IZQUIERDA = (12, 13, 14, 19, 20, 21)

#: Cada hueso del lado derecho con su gemelo del izquierdo, en el mismo orden:
#: hombro, codo, muneca, cadera, rodilla, tobillo, ojo, oido, punta y talon.
_LADO_DERECHO = (2, 3, 4, 9, 10, 11, 15, 17, 22, 23, 24)
_LADO_IZQUIERDO = (5, 6, 7, 12, 13, 14, 16, 18, 19, 20, 21)


def _pose_de_pie() -> dict[int, tuple[float, float]]:
    """BODY_25 de pie, de frente y simetrica en el eje central.

    Los joints van en el orden `(y, x)` de OpenPose, el mismo que usan
    `ancla_de_esqueleto` y `_escala_joints`. La planta se apoya en
    `POSE_SUELO_Y` y la cabeza queda por encima de la cintura, de modo que el
    anclaje y el QC midan un cuerpo de pie y no un maniqui tumbado.
    """
    return {
        0: (0.150, 0.500),   # nariz
        1: (0.200, 0.500),   # cuello
        2: (0.225, 0.455),   # hombro derecho
        3: (0.320, 0.400),   # codo derecho
        4: (0.410, 0.375),   # muneca derecha
        5: (0.225, 0.545),   # hombro izquierdo
        6: (0.320, 0.600),   # codo izquierdo
        7: (0.410, 0.625),   # mano izquierda
        8: (0.500, 0.500),   # cadera media
        9: (0.500, 0.470),   # cadera derecha
        10: (0.690, 0.470),  # rodilla derecha
        11: (0.870, 0.470),  # tobillo derecho
        12: (0.500, 0.530),  # cadera izquierda
        13: (0.690, 0.530),  # rodilla izquierda
        14: (0.870, 0.530),  # tobillo izquierdo
        15: (0.140, 0.485),  # ojo derecho
        16: (0.140, 0.515),  # ojo izquierdo
        17: (0.152, 0.465),  # oido derecho
        18: (0.152, 0.535),  # oido izquierdo
        19: (0.955, 0.515),  # punta grande del pie izquierdo
        20: (0.955, 0.555),  # punta menuda del pie izquierdo
        21: (0.955, 0.545),  # talon del pie izquierdo
        22: (0.955, 0.485),  # punta grande del pie derecho
        23: (0.955, 0.445),  # punta menuda del pie derecho
        24: (0.955, 0.455),  # talon del pie derecho
    }


def _pose_de_perfil() -> dict[int, tuple[float, float]]:
    """BODY_25 de pie visto de lado, mirando a la derecha.

    Hombros y caderas casi alineados en `x`, una articulacion delante de la
    otra, y los dos pies en la planta: la vista de perfil nace de la misma
    escala vertical que la frontal para que las tres filas de la hoja midan
    el mismo personaje.
    """
    return {
        0: (0.150, 0.525),   # nariz
        1: (0.200, 0.498),   # cuello
        2: (0.230, 0.490),   # hombro derecho (el lejano)
        3: (0.320, 0.430),   # codo derecho
        4: (0.400, 0.370),   # mano derecha
        5: (0.232, 0.508),   # hombro izquierdo (el cercano)
        6: (0.320, 0.575),   # codo izquierdo
        7: (0.400, 0.640),   # mano izquierda
        8: (0.500, 0.500),   # cadera media
        9: (0.500, 0.495),   # cadera derecha
        10: (0.690, 0.498),  # rodilla derecha
        11: (0.870, 0.500),  # tobillo derecho
        12: (0.500, 0.505),  # cadera izquierda
        13: (0.690, 0.512),  # rodilla izquierda
        14: (0.870, 0.512),  # tobillo izquierdo
        15: (0.140, 0.505),  # ojo derecho
        16: (0.140, 0.530),  # ojo izquierdo
        17: (0.152, 0.490),  # oido derecho
        18: (0.152, 0.537),  # oido izquierdo
        19: (0.955, 0.545),  # punta grande del pie izquierdo
        20: (0.955, 0.565),  # punta menuda del pie izquierdo
        21: (0.955, 0.485),  # talon del pie izquierdo
        22: (0.955, 0.525),  # punta grande del pie derecho
        23: (0.955, 0.545),  # punta menuda del pie derecho
        24: (0.955, 0.465),  # talon del pie derecho
    }


def _con_cambios(
    base: dict[int, tuple[float, float]], cambios: dict[int, tuple[float, float]]
) -> dict[int, tuple[float, float]]:
    """Copia `base` y sustituye los joints de `cambios` (joint -> `(y, x)`)."""
    pose = dict(base)
    pose.update({joint: (float(y), float(x)) for joint, (y, x) in cambios.items()})
    return pose


def _intercambia_lados(
    pose: dict[int, tuple[float, float]]
) -> dict[int, tuple[float, float]]:
    """Devuelve la pose con el papel de los lados derecho e izquierdo cambiado.

    Es la mitad opuesta del mismo ciclo: en la marcha el frame 3 pisa el pie
    contrario al del frame 1, y los brazos se intercambian con las piernas. No
    se usa un espejo en `x` porque en la vista de perfil eso daria la vuelta al
    personaje en vez de cambiarle el pie de apoyo.
    """
    intercambiada = dict(pose)
    for derecho, izquierdo in zip(_LADO_DERECHO, _LADO_IZQUIERDO):
        intercambiada[derecho] = pose[izquierdo]
        intercambiada[izquierdo] = pose[derecho]
    return intercambiada


def _espejo_horizontal(
    pose: dict[int, tuple[float, float]]
) -> dict[int, tuple[float, float]]:
    """Refleja la pose en el eje central, que es como se ve desde atras.

    La vista trasera es la frontal mirada al reves: los mismos joints quedan
    al otro lado del eje y el control de estructura sigue siendo el mismo
    personaje, no un personaje distinto.
    """
    return {joint: (y, round(1.0 - x, 4)) for joint, (y, x) in pose.items()}


# --- Idles --------------------------------------------------------------
# Las poses se guardan por vista con las claves canonicas `idle_1`.., `walk_1`..
# etc. y se prefijan al montar `POSES_BODY_25`. La clave legacy `walking_1` ya no
# existe aqui: la normalizacion a `walk` ocurre en `Frame.__init__`, que es el
# unico sitio por el que se pedia una pose.

_POSES_DOWN: dict[str, dict[int, tuple[float, float]]] = {
    # Respiracion hacia dentro: pecho y hombros suben, los brazos se abren.
    "idle_2": _con_cambios(
        _pose_de_pie(),
        {
            0: (0.138, 0.500), 1: (0.188, 0.500),
            2: (0.213, 0.462), 5: (0.213, 0.538),
            3: (0.312, 0.412), 6: (0.312, 0.588),
            4: (0.400, 0.392), 7: (0.400, 0.608),
            8: (0.495, 0.500), 9: (0.495, 0.470), 10: (0.690, 0.470),
            11: (0.870, 0.470), 12: (0.495, 0.530), 13: (0.690, 0.530),
            14: (0.870, 0.530),
            15: (0.128, 0.485), 16: (0.128, 0.515),
            17: (0.140, 0.465), 18: (0.140, 0.535),
        },
    ),
    # Respiracion hacia fuera: pecho y hombros bajan, la cabeza se incline.
    "idle_3": _con_cambios(
        _pose_de_pie(),
        {
            0: (0.162, 0.500), 1: (0.212, 0.500),
            2: (0.237, 0.450), 5: (0.237, 0.550),
            3: (0.328, 0.398), 6: (0.328, 0.602),
            4: (0.418, 0.382), 7: (0.418, 0.618),
            8: (0.508, 0.500), 9: (0.508, 0.470), 10: (0.698, 0.470),
            11: (0.876, 0.470), 12: (0.508, 0.530), 13: (0.698, 0.530),
            14: (0.876, 0.530),
            15: (0.152, 0.485), 16: (0.152, 0.515),
            17: (0.164, 0.465), 18: (0.164, 0.535),
        },
    ),
    # Cuarto respiro: el peso se asienta y la mirada cae un pelo mas.
    "idle_4": _con_cambios(
        _pose_de_pie(),
        {
            0: (0.175, 0.500), 1: (0.225, 0.500),
            2: (0.248, 0.452), 5: (0.248, 0.548),
            3: (0.340, 0.398), 6: (0.340, 0.602),
            4: (0.430, 0.380), 7: (0.430, 0.620),
            8: (0.512, 0.500), 9: (0.512, 0.472), 10: (0.700, 0.472),
            11: (0.878, 0.472), 12: (0.512, 0.528), 13: (0.700, 0.528),
            14: (0.878, 0.528),
            15: (0.165, 0.485), 16: (0.165, 0.515),
            17: (0.177, 0.465), 18: (0.177, 0.535),
        },
    ),
}
_POSES_DOWN["idle_1"] = _pose_de_pie()

# --- Marcha -------------------------------------------------------------

_POSES_DOWN["walk_1"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.145, 0.500), 1: (0.195, 0.500),
        # El brazo derecho va atras (se ensancha) y el izquierdo delante (se
        # acorta): de frente, "adelante" es acortar el brazo.
        2: (0.220, 0.455), 3: (0.320, 0.415), 4: (0.408, 0.400),
        5: (0.220, 0.545), 6: (0.318, 0.565), 7: (0.402, 0.578),
        8: (0.500, 0.496), 9: (0.500, 0.466), 10: (0.690, 0.468),
        11: (0.870, 0.466), 12: (0.500, 0.526),
        13: (0.700, 0.508), 14: (0.800, 0.500),
        # Pie izquierdo siguiendo, con la punta claramente despegada del suelo.
        19: (0.905, 0.500), 20: (0.905, 0.540), 21: (0.905, 0.530),
        22: (0.955, 0.480), 23: (0.955, 0.440), 24: (0.955, 0.450),
        15: (0.135, 0.485), 16: (0.135, 0.515),
        17: (0.147, 0.465), 18: (0.147, 0.535),
    },
)
_POSES_DOWN["walk_2"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.152, 0.500), 1: (0.202, 0.500),
        2: (0.225, 0.455), 3: (0.320, 0.420), 4: (0.402, 0.398),
        5: (0.225, 0.545), 6: (0.320, 0.572), 7: (0.400, 0.588),
        8: (0.505, 0.500), 9: (0.505, 0.470), 10: (0.690, 0.470),
        11: (0.870, 0.470), 12: (0.505, 0.530),
        13: (0.655, 0.505), 14: (0.790, 0.487),
        19: (0.845, 0.487), 20: (0.845, 0.527), 21: (0.855, 0.517),
        22: (0.955, 0.480), 23: (0.955, 0.440), 24: (0.955, 0.450),
        15: (0.142, 0.485), 16: (0.142, 0.515),
        17: (0.154, 0.465), 18: (0.154, 0.535),
    },
)
_POSES_DOWN["walk_3"] = _intercambia_lados(_POSES_DOWN["walk_1"])
_POSES_DOWN["walk_4"] = _intercambia_lados(_POSES_DOWN["walk_2"])
# Vuelta del ciclo: el pie que estaba en el aire vuelve a buscar el suelo, asi
# que el apoyo derecho se recupera sin ser un calco del primer frame.
_POSES_DOWN["walk_5"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.148, 0.500), 1: (0.198, 0.500),
        2: (0.222, 0.458), 3: (0.318, 0.420), 4: (0.404, 0.404),
        5: (0.222, 0.542), 6: (0.318, 0.562), 7: (0.400, 0.575),
        8: (0.502, 0.500), 9: (0.502, 0.468), 10: (0.692, 0.470),
        11: (0.868, 0.470), 12: (0.502, 0.528),
        13: (0.694, 0.512), 14: (0.792, 0.498),
        19: (0.900, 0.502), 20: (0.900, 0.542), 21: (0.905, 0.528),
        22: (0.955, 0.480), 23: (0.955, 0.440), 24: (0.955, 0.450),
        15: (0.138, 0.485), 16: (0.138, 0.515),
        17: (0.150, 0.465), 18: (0.150, 0.535),
    },
)
_POSES_DOWN["walk_6"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.155, 0.500), 1: (0.205, 0.500),
        2: (0.228, 0.462), 3: (0.325, 0.428), 4: (0.412, 0.412),
        5: (0.228, 0.538), 6: (0.325, 0.556), 7: (0.412, 0.572),
        8: (0.508, 0.500), 9: (0.508, 0.474), 10: (0.696, 0.472),
        11: (0.874, 0.472), 12: (0.508, 0.526),
        13: (0.696, 0.505), 14: (0.806, 0.490),
        19: (0.915, 0.500), 20: (0.915, 0.538), 21: (0.920, 0.522),
        22: (0.955, 0.482), 23: (0.955, 0.444), 24: (0.955, 0.454),
        15: (0.145, 0.485), 16: (0.145, 0.515),
        17: (0.157, 0.465), 18: (0.157, 0.535),
    },
)

# --- Voltereta ----------------------------------------------------------
# Cuerpo encogido y girando: la cadera sube por encima de los hombros y los
# pies quedan por debajo, que es lo que distingue la vuelta del salto.

_POSES_DOWN["roll_1"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.340, 0.500), 1: (0.420, 0.500),
        2: (0.450, 0.462), 5: (0.450, 0.538),
        3: (0.520, 0.430), 6: (0.520, 0.570),
        4: (0.590, 0.420), 7: (0.590, 0.580),
        8: (0.620, 0.500),
        9: (0.620, 0.470), 10: (0.740, 0.462), 11: (0.850, 0.460),
        12: (0.620, 0.530), 13: (0.740, 0.538), 14: (0.850, 0.540),
        15: (0.330, 0.485), 16: (0.330, 0.515),
        17: (0.345, 0.465), 18: (0.345, 0.535),
        19: (0.860, 0.505), 20: (0.860, 0.545), 21: (0.860, 0.535),
        22: (0.860, 0.495), 23: (0.860, 0.455), 24: (0.860, 0.465),
    },
)
_POSES_DOWN["roll_2"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.420, 0.500), 1: (0.490, 0.500),
        2: (0.520, 0.458), 5: (0.520, 0.542),
        3: (0.580, 0.435), 6: (0.580, 0.565),
        4: (0.630, 0.430), 7: (0.630, 0.570),
        8: (0.630, 0.500),
        9: (0.630, 0.472), 10: (0.700, 0.468), 11: (0.760, 0.470),
        12: (0.630, 0.528), 13: (0.700, 0.532), 14: (0.760, 0.530),
        15: (0.410, 0.485), 16: (0.410, 0.515),
        17: (0.425, 0.465), 18: (0.425, 0.535),
        19: (0.780, 0.508), 20: (0.780, 0.548), 21: (0.780, 0.538),
        22: (0.780, 0.492), 23: (0.780, 0.452), 24: (0.780, 0.462),
    },
)
_POSES_DOWN["roll_3"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.480, 0.500), 1: (0.545, 0.500),
        2: (0.575, 0.460), 5: (0.575, 0.540),
        3: (0.620, 0.442), 6: (0.620, 0.558),
        4: (0.660, 0.438), 7: (0.660, 0.562),
        8: (0.640, 0.500),
        9: (0.640, 0.475), 10: (0.680, 0.472), 11: (0.720, 0.474),
        12: (0.640, 0.525), 13: (0.680, 0.528), 14: (0.720, 0.526),
        15: (0.470, 0.485), 16: (0.470, 0.515),
        17: (0.485, 0.465), 18: (0.485, 0.535),
        19: (0.720, 0.510), 20: (0.720, 0.550), 21: (0.720, 0.540),
        22: (0.720, 0.490), 23: (0.720, 0.450), 24: (0.720, 0.460),
    },
)
_POSES_DOWN["roll_4"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.300, 0.500), 1: (0.390, 0.500),
        2: (0.420, 0.466), 5: (0.420, 0.534),
        3: (0.500, 0.430), 6: (0.500, 0.570),
        4: (0.570, 0.418), 7: (0.570, 0.582),
        8: (0.620, 0.500),
        9: (0.620, 0.470), 10: (0.760, 0.462), 11: (0.880, 0.460),
        12: (0.620, 0.530), 13: (0.760, 0.538), 14: (0.880, 0.540),
        15: (0.290, 0.485), 16: (0.290, 0.515),
        17: (0.305, 0.465), 18: (0.305, 0.535),
        19: (0.920, 0.505), 20: (0.920, 0.545), 21: (0.920, 0.535),
        22: (0.920, 0.495), 23: (0.920, 0.455), 24: (0.920, 0.465),
    },
)

# --- Caida --------------------------------------------------------------
# Cinco tiempos: el impacto, el desplome, la caida, el golpe contra el suelo y
# el descanso. El cuerpo baja, la cabeza pasa de por encima de la cadera a
# quedar casi a su altura y los pies dejan de ser el punto mas bajo.

_POSES_DOWN["death_1"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.200, 0.500), 1: (0.265, 0.500),
        2: (0.290, 0.448), 5: (0.290, 0.552),
        3: (0.400, 0.398), 6: (0.400, 0.602),
        4: (0.520, 0.400), 7: (0.520, 0.600),
        8: (0.520, 0.500),
        9: (0.520, 0.468), 10: (0.700, 0.466), 11: (0.880, 0.468),
        12: (0.520, 0.530), 13: (0.700, 0.534), 14: (0.880, 0.532),
        15: (0.192, 0.485), 16: (0.192, 0.515),
        17: (0.205, 0.465), 18: (0.205, 0.535),
        19: (0.950, 0.512), 20: (0.950, 0.552), 21: (0.950, 0.542),
        22: (0.950, 0.482), 23: (0.950, 0.442), 24: (0.950, 0.452),
    },
)
_POSES_DOWN["death_2"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.320, 0.490), 1: (0.390, 0.498),
        2: (0.410, 0.440), 5: (0.410, 0.548),
        3: (0.480, 0.382), 6: (0.480, 0.580),
        4: (0.540, 0.370), 7: (0.540, 0.596),
        8: (0.580, 0.500),
        9: (0.580, 0.464), 10: (0.760, 0.462), 11: (0.910, 0.466),
        12: (0.580, 0.534), 13: (0.760, 0.538), 14: (0.910, 0.534),
        15: (0.312, 0.478), 16: (0.312, 0.506),
        17: (0.325, 0.458), 18: (0.325, 0.526),
        19: (0.925, 0.512), 20: (0.925, 0.552), 21: (0.925, 0.542),
        22: (0.925, 0.482), 23: (0.925, 0.442), 24: (0.925, 0.452),
    },
)
_POSES_DOWN["death_3"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.480, 0.462), 1: (0.540, 0.486),
        2: (0.560, 0.430), 5: (0.560, 0.540),
        3: (0.660, 0.400), 6: (0.660, 0.572),
        4: (0.760, 0.392), 7: (0.760, 0.580),
        8: (0.680, 0.500),
        9: (0.680, 0.470), 10: (0.800, 0.470), 11: (0.910, 0.472),
        12: (0.680, 0.530), 13: (0.800, 0.532), 14: (0.910, 0.530),
        15: (0.472, 0.452), 16: (0.472, 0.482),
        17: (0.485, 0.432), 18: (0.485, 0.500),
        19: (0.920, 0.508), 20: (0.920, 0.548), 21: (0.920, 0.538),
        22: (0.920, 0.478), 23: (0.920, 0.438), 24: (0.920, 0.448),
    },
)
_POSES_DOWN["death_4"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.620, 0.430), 1: (0.640, 0.462),
        2: (0.640, 0.420), 5: (0.640, 0.500),
        3: (0.680, 0.470), 6: (0.680, 0.560),
        4: (0.700, 0.520), 7: (0.700, 0.618),
        8: (0.680, 0.512),
        9: (0.680, 0.480), 10: (0.700, 0.545), 11: (0.700, 0.610),
        12: (0.680, 0.544), 13: (0.700, 0.600), 14: (0.700, 0.650),
        15: (0.622, 0.420), 16: (0.622, 0.442),
        17: (0.630, 0.402), 18: (0.630, 0.458),
        19: (0.900, 0.600), 20: (0.900, 0.640), 21: (0.900, 0.630),
        22: (0.900, 0.560), 23: (0.900, 0.520), 24: (0.900, 0.530),
    },
)
_POSES_DOWN["death_5"] = _con_cambios(
    _pose_de_pie(),
    {
        0: (0.420, 0.452), 1: (0.480, 0.478),
        2: (0.500, 0.430), 5: (0.500, 0.522),
        3: (0.560, 0.418), 6: (0.560, 0.540),
        4: (0.600, 0.430), 7: (0.600, 0.548),
        8: (0.580, 0.478),
        9: (0.580, 0.448), 10: (0.600, 0.400), 11: (0.640, 0.378),
        12: (0.580, 0.508), 13: (0.600, 0.545), 14: (0.640, 0.560),
        15: (0.412, 0.442), 16: (0.412, 0.470),
        17: (0.425, 0.424), 18: (0.425, 0.484),
        19: (0.690, 0.545), 20: (0.690, 0.585), 21: (0.690, 0.575),
        22: (0.690, 0.462), 23: (0.690, 0.420), 24: (0.690, 0.430),
    },
)

_POSES_SIDE: dict[str, dict[int, tuple[float, float]]] = {
    "idle_2": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.138, 0.525), 1: (0.188, 0.498),
            2: (0.218, 0.490), 3: (0.312, 0.422), 4: (0.392, 0.362),
            5: (0.220, 0.508), 6: (0.312, 0.582), 7: (0.392, 0.648),
            8: (0.495, 0.500), 9: (0.495, 0.495), 10: (0.690, 0.498),
            11: (0.870, 0.500), 12: (0.495, 0.505), 13: (0.690, 0.512),
            14: (0.870, 0.512),
            15: (0.128, 0.505), 16: (0.128, 0.530),
            17: (0.140, 0.490), 18: (0.140, 0.537),
        },
    ),
    "idle_3": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.162, 0.523), 1: (0.212, 0.500),
            2: (0.242, 0.490), 3: (0.328, 0.434), 4: (0.408, 0.376),
            5: (0.244, 0.508), 6: (0.328, 0.570), 7: (0.408, 0.634),
            8: (0.508, 0.500), 9: (0.508, 0.495), 10: (0.698, 0.498),
            11: (0.876, 0.500), 12: (0.508, 0.505), 13: (0.698, 0.512),
            14: (0.876, 0.512),
            15: (0.152, 0.505), 16: (0.152, 0.530),
            17: (0.164, 0.490), 18: (0.164, 0.537),
        },
    ),
    "idle_4": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.175, 0.522), 1: (0.225, 0.498),
            2: (0.252, 0.490), 3: (0.344, 0.424), 4: (0.424, 0.368),
            5: (0.254, 0.508), 6: (0.344, 0.576), 7: (0.424, 0.640),
            8: (0.512, 0.500),
            9: (0.512, 0.495), 10: (0.700, 0.498), 11: (0.878, 0.500),
            12: (0.512, 0.505), 13: (0.700, 0.512), 14: (0.878, 0.512),
            15: (0.165, 0.505), 16: (0.165, 0.530),
            17: (0.177, 0.490), 18: (0.177, 0.537),
        },
    ),
    "walk_1": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.145, 0.528), 1: (0.195, 0.500),
            # El brazo izquierdo (el cercano) va delante y el derecho atras.
            2: (0.225, 0.492), 3: (0.325, 0.385), 4: (0.410, 0.325),
            5: (0.227, 0.510), 6: (0.320, 0.600), 7: (0.400, 0.665),
            8: (0.500, 0.497), 9: (0.500, 0.490), 10: (0.690, 0.520),
            11: (0.870, 0.545), 12: (0.500, 0.505),
            13: (0.700, 0.450), 14: (0.800, 0.412),
            # Pierna izquierda atras, con el talon alzado y la punta en el aire.
            19: (0.925, 0.360), 20: (0.925, 0.345), 21: (0.800, 0.392),
            22: (0.955, 0.590), 23: (0.955, 0.606), 24: (0.955, 0.520),
            15: (0.135, 0.505), 16: (0.135, 0.532),
            17: (0.147, 0.490), 18: (0.147, 0.539),
        },
    ),
    "walk_2": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.152, 0.527), 1: (0.202, 0.500),
            2: (0.230, 0.490), 3: (0.320, 0.415), 4: (0.400, 0.372),
            5: (0.232, 0.508), 6: (0.320, 0.588), 7: (0.398, 0.618),
            8: (0.505, 0.498), 9: (0.505, 0.492), 10: (0.690, 0.492),
            11: (0.870, 0.492), 12: (0.505, 0.508),
            13: (0.655, 0.560), 14: (0.790, 0.588),
            19: (0.845, 0.598), 20: (0.845, 0.583), 21: (0.852, 0.545),
            22: (0.955, 0.518), 23: (0.955, 0.533), 24: (0.955, 0.462),
            15: (0.142, 0.505), 16: (0.142, 0.531),
            17: (0.154, 0.490), 18: (0.154, 0.538),
        },
    ),
    "walk_5": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.148, 0.525), 1: (0.198, 0.498),
            2: (0.222, 0.490), 3: (0.322, 0.400), 4: (0.408, 0.345),
            5: (0.224, 0.510), 6: (0.320, 0.590), 7: (0.400, 0.650),
            8: (0.502, 0.497),
            9: (0.502, 0.492), 10: (0.692, 0.500), 11: (0.870, 0.505),
            12: (0.502, 0.504), 13: (0.694, 0.520), 14: (0.794, 0.500),
            19: (0.900, 0.430), 20: (0.900, 0.460), 21: (0.900, 0.470),
            22: (0.955, 0.530), 23: (0.955, 0.548), 24: (0.955, 0.468),
            15: (0.138, 0.505), 16: (0.138, 0.530),
            17: (0.150, 0.490), 18: (0.150, 0.537),
        },
    ),
    "walk_6": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.155, 0.525), 1: (0.205, 0.498),
            2: (0.230, 0.490), 3: (0.325, 0.408), 4: (0.412, 0.358),
            5: (0.232, 0.510), 6: (0.325, 0.582), 7: (0.412, 0.640),
            8: (0.508, 0.498),
            9: (0.508, 0.494), 10: (0.696, 0.498), 11: (0.874, 0.498),
            12: (0.508, 0.506), 13: (0.696, 0.512), 14: (0.808, 0.496),
            19: (0.918, 0.420), 20: (0.918, 0.450), 21: (0.918, 0.478),
            22: (0.955, 0.520), 23: (0.955, 0.536), 24: (0.955, 0.462),
            15: (0.145, 0.505), 16: (0.145, 0.530),
            17: (0.157, 0.490), 18: (0.157, 0.537),
        },
    ),
    "roll_1": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.300, 0.500), 1: (0.390, 0.498),
            2: (0.420, 0.478), 3: (0.400, 0.410), 4: (0.420, 0.350),
            5: (0.422, 0.502), 6: (0.400, 0.560), 7: (0.420, 0.618),
            8: (0.600, 0.500),
            9: (0.600, 0.495), 10: (0.720, 0.480), 11: (0.820, 0.480),
            12: (0.600, 0.505), 13: (0.720, 0.520), 14: (0.820, 0.520),
            15: (0.290, 0.492), 16: (0.290, 0.512),
            17: (0.305, 0.478), 18: (0.305, 0.525),
            19: (0.840, 0.505), 20: (0.840, 0.540), 21: (0.840, 0.520),
            22: (0.840, 0.495), 23: (0.840, 0.458), 24: (0.840, 0.472),
        },
    ),
    "roll_2": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.400, 0.500), 1: (0.485, 0.498),
            2: (0.510, 0.476), 3: (0.470, 0.412), 4: (0.470, 0.352),
            5: (0.512, 0.502), 6: (0.470, 0.566), 7: (0.470, 0.622),
            8: (0.620, 0.500),
            9: (0.620, 0.495), 10: (0.700, 0.482), 11: (0.760, 0.482),
            12: (0.620, 0.505), 13: (0.700, 0.518), 14: (0.760, 0.518),
            15: (0.390, 0.492), 16: (0.390, 0.512),
            17: (0.405, 0.478), 18: (0.405, 0.525),
            19: (0.780, 0.505), 20: (0.780, 0.540), 21: (0.780, 0.520),
            22: (0.780, 0.495), 23: (0.780, 0.458), 24: (0.780, 0.472),
        },
    ),
    "roll_3": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.520, 0.496), 1: (0.590, 0.498),
            2: (0.615, 0.478), 3: (0.570, 0.420), 4: (0.570, 0.362),
            5: (0.617, 0.502), 6: (0.570, 0.562), 7: (0.570, 0.616),
            8: (0.630, 0.500),
            9: (0.630, 0.496), 10: (0.682, 0.486), 11: (0.720, 0.486),
            12: (0.630, 0.504), 13: (0.682, 0.514), 14: (0.720, 0.514),
            15: (0.510, 0.490), 16: (0.510, 0.508),
            17: (0.525, 0.478), 18: (0.525, 0.522),
            19: (0.730, 0.504), 20: (0.730, 0.538), 21: (0.730, 0.520),
            22: (0.730, 0.496), 23: (0.730, 0.460), 24: (0.730, 0.474),
        },
    ),
    "roll_4": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.320, 0.498), 1: (0.400, 0.498),
            2: (0.430, 0.476), 3: (0.440, 0.404), 4: (0.470, 0.342),
            5: (0.432, 0.502), 6: (0.440, 0.566), 7: (0.470, 0.624),
            8: (0.640, 0.500),
            9: (0.640, 0.495), 10: (0.780, 0.478), 11: (0.900, 0.476),
            12: (0.640, 0.505), 13: (0.780, 0.522), 14: (0.900, 0.524),
            15: (0.310, 0.490), 16: (0.310, 0.510),
            17: (0.325, 0.476), 18: (0.325, 0.523),
            19: (0.930, 0.508), 20: (0.930, 0.545), 21: (0.930, 0.522),
            22: (0.930, 0.492), 23: (0.930, 0.455), 24: (0.930, 0.470),
        },
    ),
    "death_1": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.220, 0.500), 1: (0.290, 0.498),
            2: (0.315, 0.488), 3: (0.400, 0.410), 4: (0.480, 0.352),
            5: (0.317, 0.506), 6: (0.400, 0.570), 7: (0.480, 0.628),
            8: (0.520, 0.500),
            9: (0.520, 0.494), 10: (0.700, 0.492), 11: (0.880, 0.492),
            12: (0.520, 0.505), 13: (0.700, 0.512), 14: (0.880, 0.512),
            15: (0.212, 0.492), 16: (0.212, 0.512),
            17: (0.225, 0.480), 18: (0.225, 0.524),
            19: (0.938, 0.540), 20: (0.938, 0.562), 21: (0.938, 0.484),
            22: (0.938, 0.524), 23: (0.938, 0.544), 24: (0.938, 0.464),
        },
    ),
    "death_2": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.320, 0.492), 1: (0.390, 0.496),
            2: (0.410, 0.480), 3: (0.470, 0.398), 4: (0.530, 0.336),
            5: (0.412, 0.504), 6: (0.470, 0.566), 7: (0.530, 0.624),
            8: (0.580, 0.500),
            9: (0.580, 0.494), 10: (0.760, 0.492), 11: (0.910, 0.500),
            12: (0.580, 0.505), 13: (0.760, 0.508), 14: (0.910, 0.516),
            15: (0.312, 0.484), 16: (0.312, 0.504),
            17: (0.325, 0.472), 18: (0.325, 0.516),
            19: (0.928, 0.545), 20: (0.928, 0.567), 21: (0.928, 0.480),
            22: (0.928, 0.520), 23: (0.928, 0.540), 24: (0.928, 0.460),
        },
    ),
    "death_3": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.440, 0.478), 1: (0.500, 0.492),
            2: (0.520, 0.472), 3: (0.600, 0.404), 4: (0.660, 0.344),
            5: (0.522, 0.500), 6: (0.600, 0.562), 7: (0.660, 0.618),
            8: (0.640, 0.500),
            9: (0.640, 0.494), 10: (0.780, 0.496), 11: (0.905, 0.508),
            12: (0.640, 0.505), 13: (0.780, 0.500), 14: (0.905, 0.508),
            15: (0.432, 0.470), 16: (0.432, 0.490),
            17: (0.445, 0.458), 18: (0.445, 0.502),
            19: (0.918, 0.540), 20: (0.918, 0.562), 21: (0.918, 0.476),
            22: (0.918, 0.516), 23: (0.918, 0.536), 24: (0.918, 0.456),
        },
    ),
    "death_4": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.600, 0.452), 1: (0.640, 0.480),
            2: (0.645, 0.462), 3: (0.680, 0.412), 4: (0.700, 0.362),
            5: (0.647, 0.488), 6: (0.680, 0.552), 7: (0.700, 0.602),
            8: (0.660, 0.500),
            9: (0.660, 0.490), 10: (0.700, 0.548), 11: (0.700, 0.606),
            12: (0.660, 0.510), 13: (0.700, 0.560), 14: (0.700, 0.618),
            15: (0.596, 0.442), 16: (0.596, 0.464),
            17: (0.610, 0.432), 18: (0.610, 0.474),
            19: (0.918, 0.596), 20: (0.918, 0.628), 21: (0.918, 0.556),
            22: (0.918, 0.560), 23: (0.918, 0.528), 24: (0.918, 0.520),
        },
    ),
    "death_5": _con_cambios(
        _pose_de_perfil(),
        {
            0: (0.620, 0.430), 1: (0.700, 0.462),
            2: (0.710, 0.446), 3: (0.760, 0.408), 4: (0.790, 0.372),
            5: (0.712, 0.472), 6: (0.760, 0.528), 7: (0.790, 0.572),
            8: (0.780, 0.480),
            9: (0.780, 0.470), 10: (0.800, 0.520), 11: (0.800, 0.566),
            12: (0.780, 0.490), 13: (0.800, 0.536), 14: (0.800, 0.580),
            15: (0.616, 0.420), 16: (0.616, 0.442),
            17: (0.630, 0.410), 18: (0.630, 0.452),
            19: (0.900, 0.575), 20: (0.900, 0.605), 21: (0.900, 0.545),
            22: (0.900, 0.545), 23: (0.900, 0.515), 24: (0.900, 0.505),
        },
    ),
}
_POSES_SIDE["idle_1"] = _pose_de_perfil()
_POSES_SIDE["walk_3"] = _intercambia_lados(_POSES_SIDE["walk_1"])
_POSES_SIDE["walk_4"] = _intercambia_lados(_POSES_SIDE["walk_2"])

#: Vista de espaldas: el mismo esqueleto de frente reflejado en el eje central.
_POSES_UP: dict[str, dict[int, tuple[float, float]]] = {
    clave: _espejo_horizontal(pose) for clave, pose in _POSES_DOWN.items()
}

#: Pose de control de cada frame, indexada por `Frame.clave`: 19 pares por
#: vista y tres vistas. Las tres comparten escala vertical, la trasera es el
#: espejo de la frontal y la lateral nace aparte, mirando a la derecha.
POSES_BODY_25: dict[str, dict[int, tuple[float, float]]] = {
    **{f"down_{clave}": pose for clave, pose in _POSES_DOWN.items()},
    **{f"side_{clave}": pose for clave, pose in _POSES_SIDE.items()},
    **{f"up_{clave}": pose for clave, pose in _POSES_UP.items()},
}


def _planta_del_pie(pose: dict[int, tuple[float, float]], cadena) -> float:
    """Y de la parte mas baja de una pierna: punta o talon, lo que este mas abajo."""
    return max(pose[joint][0] for joint in cadena)


def pie_de_apoyo(pose: dict[int, tuple[float, float]]) -> str:
    """Lado del pie que apoya en el suelo: ``"derecha"``, ``"izquierda"``.

    El pie de apoyo es el que llega a la linea de suelo (`POSE_SUELO_Y`); el
    otro va levantada y su parte mas baja queda claramente por encima. Cuando
    los dos apoyan -los tres idles- la respuesta se fija a la derecha, para que
    sea estable y comparable entre frames en vez de depender del redondeo.

    El margen `POSE_SUELO_TOL` separa "los dos en el suelo" de "uno claramente
    en el aire"; con el margen, un pie de apoyo a tres centesimas de la planta
    se leeria como los dos a la vez.
    """
    derecha = _planta_del_pie(pose, PIERNA_DERECHA)
    izquierda = _planta_del_pie(pose, PIERNA_IZQUIERDA)
    if abs(derecha - izquierda) <= POSE_SUELO_TOL:
        return "derecha"
    return "derecha" if derecha > izquierda else "izquierda"


@dataclass(frozen=True)
class PresetFrame:
    """Todo lo que un frame necesita saber antes de llamar al modelo."""

    frame: Frame
    pose: dict[int, tuple[float, float]]
    descripcion: str


#: Como se le pide cada vista, en ingles porque es el idioma del prompt. Las
#: claves son las vistas canonicas de BODY-25, no las legacy de la matriz.
_VISTAS_EN_TEXTO = {
    "down": "seen from the front, facing the camera, both shoulders symmetric",
    "up": "seen from behind, back turned to the camera, hood and back of the shoulders visible",
    "side": "seen from the side in profile, facing right, one arm and leg in front of the other",
}

#: El movimiento de cada frame. Describen la postura, no el fotograma: sin el
#: nombre de la vista, el mismo texto pediria la misma imagen a los tres frames
#: de una fila y la hoja saldria con personajes repetidos.
_MOVIMIENTOS_EN_TEXTO = {
    ("idle", 1): "standing still, weight evenly on both feet, arms resting at the sides",
    ("idle", 2): "inhaling slowly, chest lifted, shoulders raised a little, chin tipped up",
    ("idle", 3): "exhaling slowly, chest lowered, shoulders dropped, head bowed a little",
    ("idle", 4): "shifting weight onto one foot, the other leg relaxed, arms slightly away from the body",
    ("walk", 1): "first step, the right heel planted ahead, the left foot just off the ground behind",
    ("walk", 2): "mid stride, gliding over the planted right foot, the left leg swinging through under the body",
    ("walk", 3): "the other step, the left heel planted ahead, the right foot just off the ground behind",
    ("walk", 4): "mid stride, gliding over the planted left foot, the right leg swinging through under the body",
    ("walk", 5): "last step, the right heel planted ahead again, the left foot trailing behind",
    ("walk", 6): "mid stride, gliding over the planted right foot, the left leg swinging forward under the body, the lead foot reaching out ahead to plant next",
    ("roll", 1): "tumbling backwards, the body curled into a tight ball low above the ground",
    ("roll", 2): "tumbling backwards, the body curled, shoulders and knees drawn in, lifted slightly off the ground",
    ("roll", 3): "tumbling backwards, the body nearly horizontal, tucked in and low",
    ("roll", 4): "tumbling backwards, the body tucked, rolling over the shoulder close to the ground",
    ("death", 1): "collapsing, the body crumpled on the ground, limbs folded underneath",
    ("death", 2): "dying, slumped on the ground, head and torso lowered, limbs slack",
    ("death", 3): "dying, the body lying on the ground, curled on one side",
    ("death", 4): "dying, the body settled on the ground, one arm and leg stretched out",
    ("death", 5): "dead, the body still on the ground, fully collapsed and motionless",
}


def preset_de_frame(frame: Frame) -> PresetFrame:
    """Reune la pose de control y la descripcion de un frame concreto."""
    return PresetFrame(
        frame=frame,
        pose=POSES_BODY_25[frame.clave],
        descripcion=f"{_VISTAS_EN_TEXTO[frame.vista]}, {_MOVIMIENTOS_EN_TEXTO[(frame.animacion, frame.indice)]}",
    )


# --- Prompts (Fase 3) ---------------------------------------------------

#: Los cuatro conceptos de los que habla el juego: "¿Habla de muerte, juicio,
#: penitencia o condena?". Van en ingles y en minúsculas porque se comprueban
#: dentro del prompt ya en minusculas: cada concepto tiene que poder buscarse
#: como palabra suelta, no como parte de otra.
CONCEPTOS_DIRECCION: tuple[str, ...] = ("death", "penance", "judgment", "damnation")


def construir_prompt_base(personaje: str) -> str:
    """Prompt positivo en ingles con la condicion de fondo obligatorio."""
    conceptos = ", ".join(CONCEPTOS_DIRECCION)
    return (
        f"pixel art sprite, 2D side-scrolling medieval death game, {personaje}, "
        f"solemn gothic art, iconography of {conceptos}, "
        "in the manner of medieval manuscripts and altarpieces, "
        "muted desaturated palette, dark stone, "
        "flat shading, clean pixel edges, no anti-aliasing, "
        "plain solid magenta background, centered character, full body"
    )


def construir_prompt_frame(personaje: str, frame: Frame) -> str:
    """Prompt positivo de un frame: la base mas la postura que se le pide.

    La postura va en ingles y describe el fotograma, no el nombre de la vista
    ni el del clip: con el texto solo, los siete frames de una fila saldrian
    identicos y la hoja seria una copia repetida con distinto nombre.
    """
    preset = preset_de_frame(frame)
    return (
        f"{construir_prompt_base(personaje)}, {preset.descripcion}, "
        "single figure, same costume and proportions in every frame of the sheet"
    )


def construir_prompt_negativo() -> str:
    """Prompt negativo corto (<=20 terminos) sin romper el fondo magenta."""
    return (
        "photo, 3d, cgi, blurry, jpeg, watermark, text, signature, "
        "extra limbs, deformed, gradient background, ground, shadow, outline"
    )


def codificar_prompt_negativo(pipe, texto: str) -> tuple:
    """Codifica solo el prompt negativo y devuelve `(neg_embeds, neg_pooled)`.

    Es un wrapper de `codificar_prompt` de `generar_sprite` con el prompt
    positivo vacio: asi el troceado, la medicion con los dos tokenizers y el
    encoding en CPU son exactamente los del helper, sin duplicar esa logica ni
    importar `torch` aqui.
    """
    _, neg_embeds, _, neg_pooled = gs_base.codificar_prompt(pipe, "", texto)
    return neg_embeds, neg_pooled


def codificar_prompt_positivo(pipe, texto: str) -> tuple:
    """Codifica solo el prompt positivo y devuelve `(embeds, pooled)`.

    Simetrico de `codificar_prompt_negativo`: el otro lado va vacio porque el
    negativo lo codifica `llamador_real` una vez para toda la hoja. Delegar en el
    helper de `generar_sprite` es lo que garantiza que el troceado y la medicion
    con los dos tokenizers sean los mismos que en el script de referencia.
    """
    embeds, _, pooled, _ = gs_base.codificar_prompt(pipe, texto, "")
    return embeds, pooled


# --- Control y cadena de postprocesado (Fase 4) ------------------------

#: El fondo que el prompt obliga a poner y que despues se recorta. Es el mismo
#: valor que los prompts piden literally: si el modelo pintara otro fondo, el
#: relleno por inundacion no tendria nada que borrar.
COLOR_FONDO: tuple[int, int, int] = (255, 0, 255)

#: Tolerancia del relleno. Manda la que usa `quitar_fondo`: mas alta deja halo
#: del color del fondo, mas baja deja un borde oscuro alrededor del sujeto.
TOLERANCIA_FONDO = 0.10

#: Opacidad maxima aceptable despues de recortar. Si el relleno se equivoco y
#: solo dejo una capa de fondo con un agujero, el sprite llega casi entero y
#: el QC lo cuenta como un rectangulo: mas vale quedarse sin recorte que
#: adivinar, asi que se reintenta deduciendo el color del borde.
OPACIDAD_MAXIMA_TRAS_RECORTAR = 0.99


def control_de_frame(
    frame: Frame, lienzo: int = LIENZO, ancho_hueso: int = 16
) -> dict:
    """Mapa de control OpenPose de un frame, con los joints ya escalados.

    Devuelve `{"imagen": RGB, "joints": {i: (y, x)}}`. El ControlNet solo
    entiende fondo negro y lineas de color: un control pintado sobre otro
    fondo le ensena al modelo a conservar ese fondo en vez de la pose.

    Los joints salen en pixeles del lienzo y no normalizados porque son la
    MISMA medida que usa el anclaje: `ancla_de_esqueleto` compara la Y del pie
    con la ultima fila opaca del sprite, y las dos tienen que hablar el mismo
    idioma o el recorte se descentra.
    """
    preset = preset_de_frame(frame)
    joints = _escala_joints(preset.pose, 1.0, canvas=lienzo)
    return {
        "imagen": _dibujar_pose(joints, canvas=lienzo, ancho_hueso=ancho_hueso),
        "joints": joints,
    }


def cadena_post_proceso(
    rgb: np.ndarray,
    joints: dict[int, tuple[float, float]],
    color_fondo: tuple[int, int, int] = COLOR_FONDO,
    tolerancia: float = TOLERANCIA_FONDO,
    paleta: list[tuple[int, int, int]] | None = None,
    lab: np.ndarray | None = None,
    geometria: GeometriaCelda | None = None,
) -> np.ndarray:
    """Convierte un lienzo RGB del modelo en una celda RGBA lista para el QC.

    Cuatro pasos, en este orden porque cada uno necesita el anterior:
      1. El lienzo llega opaco (RGB): se le anade alfa para que el recorte
         pueda distinguir sujeto de fondo.
      2. `quitar_fondo` borra el fondo conectado al borde, no el color en
         general: un `remove color` global se comeria el ojo de una calavera o
         la ranura de un yelmo. Si con el color conocido casi nada se borra,
         se reintenta con `referencia=None`, que deduce el fondo del borde.
      3. `normalizar_para_reduccion` reescala y coloca el sujeto con el
         anclaje del esqueleto, para que al reducir a la celda cuadre el QC.
      4. `cuantizar_y_reducir` cuantiza a la paleta y reduce por votacion.

    `geometria` es la caja esperada de la celda (`geometria_de_frame`): su
    `alto` y su `pie` mandan sobre los valores por defecto, porque la celda no
    es siempre un cuerpo erguido - `roll` va tumbado y `death` cae. Sin ella se
    conservan los valores globales de antes (47 px de alto, pie en 55), que es
    lo que necesitan las llamadas que no son de un frame concreto.
    """
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"se esperaba RGB, vino {rgb.shape}")

    rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, dtype=np.uint8)])
    recortado = gs_base.quitar_fondo(rgba, color_fondo, tolerancia)

    opaco = (recortado[..., 3] > 0).mean()
    if opaco > OPACIDAD_MAXIMA_TRAS_RECORTAR:
        # El color conocido no era el fondo: se deduce del borde y se repite.
        recortado = gs_base.quitar_fondo(rgba, None, tolerancia)

    eje_x, pie_y = ancla_de_esqueleto(joints)
    alto_celdas = ALTO_CELDAS if geometria is None else geometria.alto
    celda_pie = CELDA_PIE if geometria is None else geometria.pie

    # El anclaje vertical es la ULTIMA FILA OPACA del recorte, no la articulacion
    # del pie del esqueleto. En una pose erguida coinciden -el tobillo es lo mas
    # bajo-, pero en `roll` y `death` el cuerpo esta tumbado: el tobillo queda a
    # media altura y la silueta sigue 80-150 px por debajo. Anclar por el tobillo
    # dejaba el sprite 26-48 filas crudas mas bajo de lo pedido y el QC media el
    # `pie` de la celda 2-4 filas por debajo de la geometria declarada.
    caja = _bbox_alfa(recortado[..., 3] > 0)
    pie_recorte = int(caja[1]) if caja is not None else int(round(pie_y))

    lienzo = normalizar_para_reduccion(
        recortado,
        eje_x,
        pie_recorte,
        alto_celdas=alto_celdas,
        celda_pie=celda_pie,
    )
    return cuantizar_y_reducir(lienzo, paleta=paleta, lab=lab)


def generador_de_frame(
    frame: Frame, llamar, control: dict | None = None, guardar_cruda: Path | None = None
):
    """Cierra un frame, un modelo y un control en un `generar(seed)` de una pieza.

    `llamar(frame, seed, control)` es el modelo de verdad -en la practica el
    pipeline de SDXL, aqui cualquier cosa que devuelva un RGB del lienzo- y
    `generar(seed)` es lo que consume `generar_celda`: mismo control, misma
    cadena de postprocesado, solo cambia la semilla.

    El control se pasa tal cual, sin recalcularlo: el ControlNet recibira la
    postura de SU frame, y no la de otro, que dejaria el esqueleto cruzado
    entre celdas de la misma fila.

    `guardar_cruda` es una carpeta opcional donde volcar el lienzo 768 antes de
    reducirlo. La celda final viene recortada a 128, y cuando el QC falla no hay
    forma de distinguir si el modelo genero un palo o si lo comio el recorte.
    """

    def generar(seed: int) -> np.ndarray:
        cruda = llamar(frame, seed, control)
        if guardar_cruda is not None:
            _guardar_rgb(Path(guardar_cruda) / f"cruda_{frame.clave}.png", cruda)
        return cadena_post_proceso(
            cruda,
            control["joints"] if control else None,
            geometria=geometria_de_frame(frame),
        )

    return generar


# --- Modelo falso: ensaya la cadena entera sin GPU ----------------------

#: Amplitud del balanceo, en pixeles crudos. La idle solo respira y la
#: caminada carga el peso de una pierna, asi que la segunda es mayor.
#:
#: Las dos estan calibradas contra el QC temporal, no a ojo: el recorte se
#: recentra por bbox en `normalizar_para_reduccion`, de modo que un
#: desplazamiento UNIFORME se cancelaria solo y todos los fotogramas darian
#: IoU 1.0. Solo una deformacion graduada sobrevive al recentrado, y estos
#: valores dejan los pares consecutivos dentro de la banda 0.80..0.96 sin
#: pegarse a ninguno de los dos extremos.
BALANCEO_IDLE = 20
BALANCEO_WALK = 26
#: `roll` y `death` no son bucles: no vuelven a la pose neutra, progresan
#: mientras el cuerpo se tumba. Se quedan dentro del orden de magnitud de los
#: anteriores para no vaciar la cobertura que el QC mide.
BALANCEO_ROLL = 30
BALANCEO_DEATH = 34

#: Desplazamiento por indice de animacion, con las claves CANONICAS (no
#: `walking`) y los 57 indices de `MATRIZ`. Los indices de los extremos de un
#: bucle vuelven a la pose neutra, que es lo que hace un clip sin costura;
#: `roll` y `death` son clips abiertos y por eso solo arrancan en la neutra.
DESPLAZAMIENTOS = {
    # idle: 4 fotogramas en bucle. Los valores 1..3 son los que ya pasaban el
    # QC temporal y no se tocan; el 4º cierra el ciclo volviendo a la neutra.
    "idle": {1: 0, 2: BALANCEO_IDLE, 3: -BALANCEO_IDLE, 4: 0},
    # walk: 6 fotogramas en bucle, dos medias oscilaciones para que el peso de
    # la pierna caiga dos veces por ciclo. Cada paso mueve exactamente
    # BALANCEO_WALK: si dos fotogramas consecutivos compartieran desplazamiento,
    # el modelo de mentira los pegara identicos y el QC temporal los rechazaria
    # con IoU 1.0 (fuera de la banda 0.80..0.96), como pasaba con las viejas
    # mesetas 2/3 y 5/6.
    "walk": {
        1: 0,
        2: BALANCEO_WALK,
        3: 2 * BALANCEO_WALK,
        4: BALANCEO_WALK,
        5: 0,
        6: -BALANCEO_WALK,
    },
    "roll": {
        1: 0,
        2: BALANCEO_ROLL // 2,
        3: BALANCEO_ROLL,
        4: BALANCEO_ROLL + BALANCEO_ROLL // 2,
    },
    "death": {
        1: 0,
        2: BALANCEO_DEATH // 3,
        3: BALANCEO_DEATH // 2,
        4: BALANCEO_DEATH,
        5: BALANCEO_DEATH + BALANCEO_DEATH // 3,
    },
}


def _deformar_por_filas(sprite: np.ndarray, desplazamiento: int) -> np.ndarray:
    """Inclina el sprite de una pieza hacia `desplazamiento` pixeles crudos.

    Cada fila se mueve un poco mas que la de debajo, hasta el maximo en la
    cabeza y cero en el pie: el personaje se inclina sin despegar los pies del
    suelo. Los huecos que deja quedan transparentes, no se rellenan con el color
    del vecino: un pixel inventado aqui acabaria dentro de la paleta.
    """
    if desplazamiento == 0:
        return sprite
    alto, ancho = sprite.shape[:2]
    salida = np.zeros_like(sprite)
    for fila in range(alto):
        peso = (alto - 1 - fila) / max(alto - 1, 1)
        dx = int(round(desplazamiento * peso))
        if dx == 0:
            salida[fila] = sprite[fila]
        elif dx > 0:
            salida[fila, dx:] = sprite[fila, : ancho - dx]
        else:
            salida[fila, : ancho + dx] = sprite[fila, -dx:]
    return salida


def _pegar_sobre_fondo(sprite: np.ndarray, eje_x: float, pie_y: float) -> np.ndarray:
    """Pega el recorte con el pie sobre `pie_y` y el cuerpo centrado en `eje_x`.

    Pega solo donde el alfa es opaco y deja el resto en el color del fondo: si
    pegara tambien los pixeles transparentes, el lienzo entero llegaria opaco
    al recorte y la cadena no tendria nada que separar del personaje.
    """
    caja = _bbox_alfa(sprite[..., 3])
    if caja is None:
        return np.full((LIENZO, LIENZO, 3), COLOR_FONDO, dtype=np.uint8)

    # La deformacion puede vaciar las columnas extremas: el recorte se vuelve a
    # ceñir a la caja del alfa antes de medir, o el pegado descentraria el sujeto.
    f0, f1, c0, c1 = caja
    sprite = sprite[f0 : f1 + 1, c0 : c1 + 1]
    alto, ancho = sprite.shape[:2]
    # Un recorte mayor que el lienzo haria que el clamp de `top` saliera
    # negativo, y numpy leeria la ventana desde el FINAL del eje: la ventana
    # tendria menos filas que la mascara booleana y el pegado reventaria. Se
    # recorta por el borde que sobre para que el clamp de abajo siempre valga.
    if alto > LIENZO or ancho > LIENZO:
        top0 = max(int(round(pie_y)) - (alto - 1), 0)
        left0 = max(int(round(eje_x - (ancho - 1) / 2)), 0)
        sprite = sprite[top0 : top0 + LIENZO, left0 : left0 + LIENZO]
        alto, ancho = sprite.shape[:2]
    top = int(round(pie_y)) - (alto - 1)
    left = int(round(eje_x - (ancho - 1) / 2))
    top = int(min(max(top, 0), LIENZO - alto))
    left = int(min(max(left, 0), LIENZO - ancho))

    lienzo = np.full((LIENZO, LIENZO, 3), COLOR_FONDO, dtype=np.uint8)
    ventana = lienzo[top : top + alto, left : left + ancho]
    opaco = sprite[..., 3] > 0
    ventana[opaco] = sprite[..., :3][opaco]
    return lienzo


def llamador_falso(
    frame: Frame,
    seed: int,
    control: dict | None = None,
    referencia: Path | str | None = None,
) -> np.ndarray:
    """Modelo de mentira que cumple el CONTRATO de `llamador_real`.

    No simula SDXL: pega la referencia de arte sobre el fondo magenta que pide el
    prompt, en el sitio donde el esqueleto del control dice que va el personaje.
    La cadena de postprocesado no llega a saber que el modelo es falso, asi que
    un fallo al ensayar con el es del anclaje o de la reduccion y nunca del
    modelo: por eso la tanda entera se puede correr en CPU.

    Ignora la semilla a proposito. Su unico trabajo es dejar pasar el QC al
    primer intento, para que `generar_celda` no gaste semillas ni patience de
    reintento. Lo que si cambia entre fotogramas es el balanceo, que es lo que el
    QC temporal mide.

    La vista trasera se pega en espejo porque la referencia es de frente; la
    lateral se pega tal cual, porque el recorte no tiene de donde salir un
    perfil y forzar un estrechamiento bajaria la cobertura por debajo del QC.
    """
    ruta = Path(referencia) if referencia is not None else RUTA_REFERENCIA
    sprite = np.array(Image.open(ruta).convert("RGBA"))
    if frame.vista == "up":
        sprite = sprite[:, ::-1]

    grande = escalar_sprite(sprite, FACTOR_REFERENCIA)
    caja = _bbox_alfa(grande[..., 3])
    if caja is None:
        return np.full((LIENZO, LIENZO, 3), COLOR_FONDO, dtype=np.uint8)
    f0, f1, c0, c1 = caja
    sujeto = grande[f0 : f1 + 1, c0 : c1 + 1]
    sujeto = _deformar_por_filas(sujeto, DESPLAZAMIENTOS[frame.animacion][frame.indice])

    joints = control["joints"] if control else None
    eje_x, pie_y = ancla_de_esqueleto(joints)
    return _pegar_sobre_fondo(sujeto, eje_x, pie_y)


# --- Generacion con SDXL (Fases 4 y 5) ---------------------------------


def cargar_modelo(personaje: str = "sombra_velada"):
    """Carga SDXL + LoRA pixel-art + IP-Adapter + ControlNet OpenPose.

    Devuelve `(pipe, controlnet)`. Los pesos se piden en `float16` y se dejan
    en CPU: el offload a la GPU lo decide despues `gs_base.configurar_dispositivo`.
    Combinar offload con `.to("cuda")` duplicaria los pesos en RAM de video y
    reventaria los 8 GB de la tarjeta.
    """
    import torch
    from diffusers import (
        ControlNetModel,
        EulerAncestralDiscreteScheduler,
        StableDiffusionXLPipeline,
    )
    from diffusers.loaders import IPAdapterMixin

    controlnet = ControlNetModel.from_pretrained(
        CTRLNET_OPENPOSE, torch_dtype=torch.float16, variant="fp16"
    )
    pipe = StableDiffusionXLPipeline.from_pretrained(
        MODELO_SDXL,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        variant="fp16",
    )
    pipe.load_lora_weights(LORA_PIXEL_ART)
    pipe.fuse_lora()
    # En 0.40 el IP-Adapter se carga con `load_ip_adapter` y se ajusta con
    # `set_ip_adapter_scale`; `set_ip_adapter` ya no existe.
    IPAdapterMixin.load_ip_adapter(
        pipe,
        pretrained_model_name_or_path_or_dict=IP_ADAPTER_REPO,
        subfolder="sdxl_models",
        weight_name="ip-adapter-plus_sdxl_vit-h.safetensors",
        image_encoder_folder="models/image_encoder",
    )
    pipe.set_ip_adapter_scale([IP_ADAPTER_PESO] * len(pipe.image_encoder))
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()
    if hasattr(pipe, "enable_vae_slicing"):
        pipe.enable_vae_slicing()
    pipe.enable_vae_tiling()
    return pipe, controlnet


def llamador_real(
    pipe,
    personaje: str = "sombra_velada",
    pasos: int = PASOS,
    guidance: float = GUIDANCE,
    referencia: Path | str | None = None,
):
    """Prepara el pipeline una vez y devuelve el CONTRATO de `llamador_falso`.

    Devuelve una funcion `llamar(frame, seed, control) -> RGB 768x768x3` que ya
    no vuelve a codificar nada: el prompt de cada frame y el negativo comun se
    codifican la primera vez que se usan y se guardan. Sin ese cache, una hoja de
    21 frames gastaria casi todo su tiempo codificando texto en vez de diffuse,
    y con 8 GB de VRAM cada eco de mas es un riesgo de OOM.

    La referencia se pasa al IP-Adapter UNA vez, antes de cualquier generacion, y
    en RGB: es lo que espera `set_ip_adapter_image`, y repetirla por frame seria
    reprocesar el encoder ViT-H 21 veces. A partir de ahi `image=` es solo el
    mapa de postura del ControlNet.

    El generador de ruido va en CPU a proposito: la semilla de un frame tiene
    que dar la misma imagen este equipo que el otro, y con CUDA el generador
    tambien arrastraria memoria de video.
    """
    import torch

    ruta_ref = Path(referencia) if referencia is not None else RUTA_REFERENCIA
    if referencia is not None or hasattr(pipe, "set_ip_adapter_image"):
        # Sin IP-Adapter cargado el metodo no existe: en ese caso la referencia
        # se ignora en lugar de reventar, que es lo que haria un acceso directo.
        with Image.open(ruta_ref) as abierta:
            pipe.set_ip_adapter_image(abierta.convert("RGB"))

    neg_embeds, neg_pooled = codificar_prompt_negativo(pipe, construir_prompt_negativo())
    embeds_por_frame: dict[str, tuple] = {}

    def embeddings_de(frame: Frame) -> tuple:
        if frame.clave not in embeds_por_frame:
            embeds_por_frame[frame.clave] = codificar_prompt_positivo(
                pipe, construir_prompt_frame(personaje, frame)
            )
        return embeds_por_frame[frame.clave]

    def llamar(frame: Frame, seed: int, control: dict | None = None) -> np.ndarray:
        embeds, pooled = embeddings_de(frame)
        salida = pipe(
            prompt_embeds=embeds,
            negative_prompt_embeds=neg_embeds,
            pooled_prompt_embeds=pooled,
            negative_pooled_prompt_embeds=neg_pooled,
            image=control["imagen"] if control else None,
            height=LIENZO,
            width=LIENZO,
            num_inference_steps=pasos,
            guidance_scale=guidance,
            generator=torch.Generator(device="cpu").manual_seed(seed),
        )
        return np.array(salida.images[0].convert("RGB"), dtype=np.uint8)

    return llamar


# --- Manifiesto e importador Unity (Fase 6) ---------------------------


def construir_manifiesto(
    resultados: dict[str, ResultadoCelda], nombre: str = "wanderer"
) -> dict:
    """Construye el manifiesto logico del `spritesheet.json`.

    Describe las 12 filas de la hoja (`rows`) en lugar de los frames fisicos:
    cada fila es una animacion vista desde una direccion y declara su ritmo
    (`fps`), si vuelve al inicio (`loop`) y los indices globales de sus frames,
    que es la posicion que ocupan en la hoja al leerse por filas. La unica
    fuente es `TABLA_FILAS`; `resultados` se conserva en la firma para que las
    llamadas no dependan de la fase, aunque el manifiesto logico no la usa.
    """
    return {
        "id": f"{nombre}_wanderer_sheet",
        "frameSize": GRID,
        "ppu": PPU,
        "pivot": {"x": 0.5, "y": 0.125},
        "rows": [
            {
                "row": fila.fila,
                "anim": fila.animacion,
                "dir": fila.vista,
                "loop": fila.bucle,
                "fps": fila.fps,
                "frames": list(
                    range(fila.frames_iniciales, fila.frames_iniciales + fila.frames)
                ),
            }
            for fila in TABLA_FILAS
        ],
    }


# --- Exportacion: la carpeta que se lleva Unity --------------------------


def _guardar_png(destino: Path, imagen: np.ndarray) -> Path:
    """Crea las carpetas y escribe un PNG RGBA; devuelve la ruta."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(imagen, mode="RGBA").save(destino)
    return destino


def _guardar_rgb(destino: Path, imagen: np.ndarray) -> Path:
    """Escribe el lienzo crudo tal cual salio del modelo, sin tocar nada."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(imagen, mode="RGB").save(destino)
    return destino


def _guardar_referencia(origen: Path | str, destino_dir: Path) -> Path:
    """Copia la referencia usada a `destino_dir` conservando su nombre.

    La hoja viaja con la referencia que la produjo: quien recibe la salida tiene
    que poder repetir el QC y el IP-Adapter sin el proyecto delante. La copia
    conserva el nombre de origen para que una alternativa no se cuele en la
    carpeta disfrazada de `sprite_3.png`.

    Si el origen ES la referencia aprobada, su huella tiene que ser la de
    siempre: un archivo editado en sitio deja al QCmidiendo otra cosa sin que
    nadie lo note, y para eso esta la comprobacion. Una referencia distinta de
    la aprobada no es un error (de eso vive `--referencia`), pero se avisa: sus
    metricas pasan a ser los umbrales del QC de esa tanda.
    """
    origen = Path(origen)
    destino_dir = Path(destino_dir)
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / origen.name

    huella = hashlib.sha256(origen.read_bytes()).hexdigest().upper()
    es_aprobada = origen.resolve() == RUTA_REFERENCIA.resolve()
    if es_aprobada and huella != SHA_REFERENCIA:
        raise ValueError(
            f"{origen.name} deberia tener la huella {SHA_REFERENCIA} y tiene {huella}: "
            "la referencia aprobada cambio y el QC ya no mediria lo que dice medir"
        )
    if not es_aprobada:
        print(
            f"referencia alternativa: {origen.name} (huella {huella[:12]}), "
            "sus metricas pasan a ser los umbrales del QC de esta tanda"
        )

    shutil.copy2(origen, destino)
    huella_copia = hashlib.sha256(destino.read_bytes()).hexdigest().upper()
    if huella_copia != huella:
        raise ValueError(f"la copia de la referencia quedo corrupta: {destino}")
    return destino


def exportar_celda(frame: Frame, imagen: np.ndarray, destino: Path) -> Path:
    """Escribe una celda en `destino/<animacion>/<vista_legacy>/<clave>.png`.

    La carpeta usa el nombre legacy (`frontal`, `trasera`, `lateral`) porque es
    lo que espera el importador de Unity; `vista` es solo la forma logica.
    """
    return _guardar_png(
        destino / animacion_legacy_de_manifiesto(frame.animacion) / frame.vista_legacy / f"{frame.clave}.png",
        imagen,
    )


def exportar_previews(resultados: dict[str, ResultadoCelda], destino: Path, factor: int = 8) -> list[Path]:
    """Guarda cada celda buena ampliada `factor` veces, en `destino/previews/`.

    Una celda de 128 px no se juzga a ojo: la preview es lo que se mira antes de
    decidir si la hoja sirve. Se usa NEAREST para que los pixeles sigan
    cuadrados y no se invente un degradado que el juego no vera.

    TOLERA que falten frames: con `--limite` la tanda solo ha generado una parte
    de la matriz y la preview de lo que no existe no se puede inventar. Se
    recorre `MATRIZ` y no `resultados` para no perder el orden de salida.
    """
    rutas = []
    for frame in MATRIZ:
        resultado = resultados.get(frame.clave)
        if resultado is None or resultado.estado != "ok":
            continue
        lado = GRID * factor
        ampliada = Image.fromarray(resultado.imagen, mode="RGBA").resize((lado, lado), Image.NEAREST)
        ruta = destino / "previews" / f"{frame.clave}_x{factor}.png"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ampliada.save(ruta)
        rutas.append(ruta)
    return rutas


def exportar_hoja(hoja: np.ndarray, destino: Path) -> Path:
    """Escribe la hoja ensamblada como `spritesheet.png`."""
    return _guardar_png(destino / "spritesheet.png", hoja)


def espejar_horizontal(imagen: np.ndarray) -> np.ndarray:
    """Voltea la imagen de izquierda a derecha conservando el eje Y.

    Es la vista que mira al lado contrario de la `side`: en vez de generar
    otro frame, se reutiliza el de la `side` espejado.
    """
    return imagen[:, ::-1]


def exportar_manifiesto(
    manifiesto: dict, destino: Path, nombre: str = "spritesheet.json"
) -> Path:
    """Escribe el `spritesheet.json` con el rect fisico de cada frame.

    El manifiesto logico describe filas; aqui se materializan los frames: dentro
    de la fila `row`, el frame k ocupa la celda k de la hoja y por tanto el
    rect de ancho `grid` en `(row * grid, k * grid)`. El archivo lleva los
    `rows` del manifiesto mas estos `frames` fisicos.
    """
    destino.mkdir(parents=True, exist_ok=True)
    grid = manifiesto["frameSize"]
    frames = []
    for row in manifiesto["rows"]:
        primero = row["frames"][0]
        for columna, indice_global in enumerate(row["frames"]):
            indice = indice_global - primero + 1
            frames.append(
                {
                    "clave": f"{row['dir']}_{row['anim']}_{indice}",
                    "celda": {"fila": row["row"], "columna": columna},
                    "vista": row["dir"],
                    "animacion": row["anim"],
                    "indice": indice,
                    "rect": {
                        "x": columna * grid,
                        "y": row["row"] * grid,
                        "w": grid,
                        "h": grid,
                    },
                }
            )
    datos = dict(manifiesto)
    datos["frames"] = frames
    ruta = destino / nombre
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta


def exportar_frames_unity(manifiesto: dict, destino: Path) -> Path:
    """Escribe el `frames.json` que consume el importador de Unity.

    No es el mismo formato que `spritesheet.json`: aqui cada clip trae sus
    vistas, cada vista sus fotogramas, y el recorte se hace por indice
    (columna) en lugar de por rect, que es lo que el animador necesita.
    `celda_m` convierte los 128 px de celda a metros de mundo con el PPU.

    Los clips se recortan a `FRAMES_CLIP_UNITY`: la hoja nueva genera mas
    fotogramas que la legacy (4 de idle y 6 de walking por vista) y el
    importador ya estaba calibrado para la de 21; se quedan los primeros 3 y 4,
    que son los que mantienen el numero de fotogramas por clip.
    """
    celda_m = round(GRID / PPU, 4)
    clips = []
    for animacion in ("idle", "walking"):
        duracion = DURACION_IDLE if animacion == "idle" else DURACION_WALK
        vistas = []
        for vista in ("frontal", "trasera", "lateral"):
            frames = [
                {"indice": f.indice, "columna": f.columna}
                for f in MATRIZ
                if animacion_legacy_de_manifiesto(f.animacion) == animacion
                and f.vista_legacy == vista
            ][:FRAMES_CLIP_UNITY[animacion]]
            vistas.append({"vista": vista, "frames": frames})
        clips.append(
            {
                "nombre": animacion,
                "duracion_ms": duracion,
                "bucle": True,
                "vistas": vistas,
            }
        )
    datos = {
        "hoja": "spritesheet",
        "ppu": PPU,
        "pivot": {"x": 0.5, "y": 0.0},
        "celda_m": celda_m,
        "clips": clips,
    }
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / "frames.json"
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta


def exportar_todo(
    resultados: dict[str, ResultadoCelda], destino: Path, factor: int = 8
) -> dict[str, object]:
    """Deja la carpeta completa y devuelve las rutas de lo escrito.

    Se niega a ensamblar si queda algo pendiente: una hoja con huecos parece
    completa y hace que Unity recorte el frame equivocado, que es peor que no
    tener hoja.
    """
    pendientes = [f.clave for f in MATRIZ if resultados.get(f.clave) is None or resultados[f.clave].estado != "ok"]
    if pendientes:
        raise ValueError(
            f"faltan {len(pendientes)} celdas pendientes: {', '.join(sorted(pendientes))}"
        )
    destino = Path(destino)
    manifiesto = construir_manifiesto(resultados)
    celdas = [exportar_celda(f, resultados[f.clave].imagen, destino) for f in MATRIZ]
    previews = exportar_previews(resultados, destino, factor)
    return {
        "hoja": exportar_hoja(armar_hoja(resultados), destino),
        "manifiesto": exportar_manifiesto(manifiesto, destino, nombre="wanderer_sheet.json"),
        "celdas": celdas,
        "previews": previews,
    }


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada: genera la hoja completa o un subconjunto (smoke).

    `--falso` sustituye SDXL por el modelo de mentira: es la unica forma de
    ensayar el cierre entero -hoja, manifiestos, celdas, referencias- sin GPU
    ni pesos. Devuelve el codigo de salida en vez de llamar a `sys.exit`, para
    que las pruebas puedan invocarlo y leer el numero.
    """
    ap = argparse.ArgumentParser(description="Genera la hoja de 21 frames de Dark Requiem.")
    ap.add_argument("--personaje", default="sombra_velada")
    ap.add_argument("--pasos", type=int, default=PASOS)
    ap.add_argument("--guidance", type=float, default=GUIDANCE)
    ap.add_argument("--limite", type=int, default=None)
    ap.add_argument("--salida", default=None, help="Carpeta destino; por defecto salida/<personaje>.")
    ap.add_argument("--falso", action="store_true", help="Usa el modelo de mentira, sin GPU.")
    ap.add_argument("--referencia", default=None, help="Referencia alternativa para IP-Adapter y QC.")
    args = ap.parse_args(argv)

    destino = Path(args.salida) if args.salida else RUTA_SALIDA / args.personaje
    destino.mkdir(parents=True, exist_ok=True)
    ruta_ref = Path(args.referencia) if args.referencia else RUTA_REFERENCIA

    print(f"personaje={args.personaje} pasos={args.pasos} guidance={args.guidance} limite={args.limite}")
    print(f"modelos: {MODELO_SDXL} + {LORA_PIXEL_ART} + {CTRLNET_OPENPOSE} + {IP_ADAPTER_REPO}")

    # La referencia viaja con la hoja: el QC y el IP-Adapter parten de este
    # archivo, asi que quien recibe la salida tiene que poder repetirlos.
    copia_ref = _guardar_referencia(ruta_ref, destino / "referencias")

    if args.falso:
        llamar = lambda frame, seed, control=None: llamador_falso(frame, seed, control, ruta_ref)
    else:
        pipe, _controlnet = cargar_modelo(args.personaje)
        llamar = llamador_real(pipe, args.personaje, args.pasos, args.guidance, ruta_ref)

    frames = MATRIZ if args.limite is None else MATRIZ[: args.limite]
    ref = metricas_de_referencia(ruta_ref)

    # Una sola secuencia para toda la tanda: el QC temporal compara cada frame
    # con el ULTIMO ACEPTADO de su vista, asi que una instancia por fotograma
    # dejaria la serie sin memoria y el control de parpadeo sin sentido.
    secuencia = SecuenciaTemporal(lambda sprite: qc_frame(sprite, ref))

    # Las crudas se dejan junto al resto: si el QC falla, 768 px son lo unico
    # que dice si el modelo fallo o si lo fallo el recorte.
    dir_crudas = destino / "crudas"
    resultados: dict[str, ResultadoCelda] = {}
    for frame in frames:
        control = control_de_frame(frame)
        generar = generador_de_frame(frame, llamar, control, guardar_cruda=dir_crudas)
        resultado = generar_celda(
            frame, generar, lambda sprite: secuencia.verificar(frame, sprite), personaje=args.personaje
        )
        resultados[frame.clave] = resultado
        estado = "ok" if resultado.estado == "ok" else resultado.estado
        print(f"  {frame.clave}: {estado}")

    if args.limite is not None:
        # La hoja no se monta, pero lo generado no se tira: un `--limite 2` que
        # no deja celdas ni crudas obliga a pagar los pesos otra vez para
        # mirar lo mismo. Se exporta lo bueno a pelo, sin manifiesto, que es
        # lo que describe la hoja que aun no existe.
        buenos = [f for f in frames if resultados[f.clave].estado == "ok"]
        celdas = [exportar_celda(f, resultados[f.clave].imagen, destino) for f in buenos]
        previews = exportar_previews(resultados, destino)
        print(f"limite {args.limite} de {len(MATRIZ)}: la hoja esta incompleta, no se ensambla")
        print(f"exportado: {len(celdas)} celdas, {len(previews)} previews, crudas en {dir_crudas}")
        for ruta in celdas:
            print(f"celda: {ruta}")
        print(f"referencia: {copia_ref}")
        return 1

    try:
        rutas = exportar_todo(resultados, destino)
    except ValueError as exc:
        print(f"no se pudo exportar: {exc}")
        return 1
    print(f"hoja: {rutas['hoja']}")
    print(f"manifiesto: {rutas['manifiesto']}")
    frames = exportar_frames_unity(construir_manifiesto(resultados), destino)
    print(f"frames: {frames}")
    print(f"referencia: {copia_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
