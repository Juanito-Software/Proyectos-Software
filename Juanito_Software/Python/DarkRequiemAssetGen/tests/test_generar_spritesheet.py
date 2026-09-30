"""Tests de generar_spritesheet.py.

Aqui vive la logica que decide si un frame sirve: el anclaje del personaje a
pies y al eje central, la reduccion a 128x128, el control de calidad y el
ensamblado. Todo se prueba con imagenes sinteticas y con la referencia real,
sin cargar SDXL: si un test necesita la GPU, no es un test, es una tanda.

La referencia se usa como criterio de verdad: si el QC acepta el sprite
aprobado y rechaza lo demas, el QC esta midiendo lo que dice medir.
"""

import hashlib
import sys
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image, ImageDraw

import generar_sprite
import generar_spritesheet as gs

LIENZO = gs.LIENZO
GRID = gs.GRID
FACTOR = LIENZO // GRID

ALTO_CELDAS = gs.ALTO_CELDAS
CELDA_PIE = gs.CELDA_PIE
CELDA_CENTRO = gs.CELDA_CENTRO


# --- ayudas de sintesis -------------------------------------------------


def _personaje(alto_px, ancho_px, fila, columna, color=(198, 58, 46, 255)):
    """Rectangulo opaco sobre lienzo transparente: un personaje sin detalle."""
    lienzo = np.zeros((LIENZO, LIENZO, 4), dtype=np.uint8)
    fin = min(fila + alto_px, LIENZO)
    lienzo[fila:fin, columna : columna + ancho_px] = color
    return lienzo


def _ancla(subject, ancho_px, fila, columna):
    """eje_x y pie_y del rectangulo, como los daria el esqueleto."""
    return {
        "eje_x": columna + ancho_px // 2,
        "pie_y": fila + 684 - 1,
    }


def _reduccion(subject, **kwargs):
    salida = gs.normalizar_para_reduccion(subject, **kwargs)
    return gs.cuantizar_y_reducir(salida, gs.paleta_rgb(), gs.paleta_lab())


def _bbox(alpha):
    filas = np.nonzero(alpha.any(axis=1))[0]
    columnas = np.nonzero(alpha.any(axis=0))[0]
    return filas, columnas


# --- anclaje ------------------------------------------------------------


def test_el_personaje_queda_anclado_a_pies_y_al_eje_central():
    # 684 px de alto se encogen a las 47 celdas del presupuesto. Pegado al pie
    # en la celda 55 y centrado en la 31.5, el rectangulo tiene que acabar
    # exactamente en la fila 671 (la ultima de la celda 55) y empezar en la 108
    # (la primera de la celda 9).
    sujeto = _personaje(684, 132, 40, 300)
    salida = gs.normalizar_para_reduccion(sujeto, **_ancla(sujeto, 132, 40, 300))

    filas, columnas = _bbox(salida[..., 3] > 0)
    assert filas[-1] == CELDA_PIE * FACTOR + FACTOR - 1
    assert filas[0] == (CELDA_PIE - ALTO_CELDAS + 1) * FACTOR
    assert len(filas) == ALTO_CELDAS * FACTOR
    assert columnas.mean() == pytest.approx(CELDA_CENTRO * FACTOR, abs=1)


def test_el_pie_marca_la_ultima_fila_opaca_y_no_el_borde_del_lienzo():
    # El pie se lee del sujeto, no del lienzo: si el recorte llega al borde de
    # abajo, el anclaje tiene que seguir siendo el del sujeto.
    sujeto = _personaje(684, 132, 84, 300)
    salida = gs.normalizar_para_reduccion(sujeto, **_ancla(sujeto, 132, 84, 300))
    filas, _ = _bbox(salida[..., 3] > 0)
    assert filas[-1] == CELDA_PIE * FACTOR + FACTOR - 1


@pytest.mark.parametrize("ancho_px", [132, 300, 456])
def test_la_escala_no_depende_del_ancho_del_bbox(ancho_px):
    # Este es el fallo que motivo el modulo: un brazo o una espada ensanchan el
    # bbox y, si la escala sale del lado mayor, el cuerpo crece o se recorta.
    # La escala sale de la altura, y la altura tiene que dar lo mismo siempre.
    sujeto = _personaje(684, ancho_px, 40, 20)
    salida = gs.normalizar_para_reduccion(sujeto, **_ancla(sujeto, ancho_px, 40, 20))
    filas, _ = _bbox(salida[..., 3] > 0)
    assert len(filas) == ALTO_CELDAS * FACTOR
    assert filas[-1] == CELDA_PIE * FACTOR + FACTOR - 1


def test_un_personaje_ancho_que_no_cabe_se_ajusta_en_vez_de_ganar_pixels():
    # Si el recorte es mas ancho que el lienzo hay que encogerlo. Encogerlo
    # recorta margen del ancho, no de la altura: el pie y el alto se respetan.
    sujeto = _personaje(684, 700, 40, 60)
    salida = gs.normalizar_para_reduccion(sujeto, **_ancla(sujeto, 700, 40, 60))
    filas, columnas = _bbox(salida[..., 3] > 0)
    assert len(filas) == ALTO_CELDAS * FACTOR
    assert filas[-1] == CELDA_PIE * FACTOR + FACTOR - 1
    assert columnas[0] >= 0 and columnas[-1] < LIENZO


def test_el_sprite_reducido_mide_47_y_apoya_el_pie_en_la_fila_55():
    sujeto = _personaje(684, 132, 40, 300)
    sprite = np.array(_reduccion(sujeto, **_ancla(sujeto, 132, 40, 300)))

    assert sprite.shape == (GRID, GRID, 4)
    filas, columnas = _bbox(sprite[..., 3] > 0)
    assert filas[0] == CELDA_PIE - ALTO_CELDAS + 1
    assert filas[-1] == CELDA_PIE
    assert len(filas) == ALTO_CELDAS
    assert columnas.mean() == pytest.approx(CELDA_CENTRO, abs=1)


# --- esqueleto ----------------------------------------------------------


def test_el_mapa_bodies25_usa_los_indices_oficiales_de_openpose():
    # BODY_25 no agrupa los indices por region: el rostro va antes que las
    # piernas y los pies van al final. Estos numeros estan tomados de
    # `POSE_BODY_25_BODY_PARTS` en src/openpose/pose/poseParameters.cpp.
    # Confundirlos rompe el anclaje en silencio, asi que se fijan aqui.
    assert gs.PIES_BODY_25 == (11, 14, 19, 20, 21, 22, 23, 24)
    assert gs.CADERAS_BODY_25 == (8, 9, 12)


def test_el_esqueleto_dibujado_solo_usa_indices_validos_y_sin_repetir():
    # 25 articulaciones, 26 con el canal de fondo: cualquier indice por encima
    # de 24 no existe y PIL se comeria un KeyError silencioso en produccion.
    huesos = gs._esqueleto_bodies25()
    for a, b in huesos:
        assert 0 <= a <= 24
        assert 0 <= b <= 24
    assert len(huesos) == len({tuple(sorted(h)) for h in huesos})


def test_el_ancla_se_saca_de_la_articulacion_mas_baja_y_del_eje_del_cuerpo():
    # El esqueleto es la fuente de verdad del anclaje: los joints de los pies
    # dan la fila del suelo y la pelvis da el eje horizontal del cuerpo.
    joints = {
        0: (100.0, 300.0),   # Nose
        8: (120.0, 370.0),   # MidHip
        9: (120.0, 400.0),   # RHip
        12: (120.0, 340.0),  # LHip
        11: (700.0, 410.0),  # RAnkle
        14: (700.0, 330.0),  # LAnkle
    }
    eje_x, pie_y = gs.ancla_de_esqueleto(joints)
    assert eje_x == pytest.approx(370.0, abs=1)
    assert pie_y == pytest.approx(700.0, abs=1)


def test_un_esqueleto_sin_pies_cae_al_bajo_del_eje():
    joints = {0: (10.0, 10.0), 8: (20.0, 50.0), 9: (20.0, 40.0), 12: (20.0, 60.0)}
    eje_x, pie_y = gs.ancla_de_esqueleto(joints)
    assert eje_x == pytest.approx(50.0, abs=1)
    assert pie_y == pytest.approx(20.0, abs=1)


# --- composicion de la pose --------------------------------------------


# --- render de la pose ---------------------------------------------------


def test_los_joints_se_escalan_en_orden_y_x_de_openpose():
    # BODY_25 entrega (y, x): la fila primero. `_escala_joints` no invierte.
    joints = {0: (0.25, 0.75), 7: (0.5, 0.4), 8: (0.5, 0.6)}
    escalados = gs._escala_joints(joints, 1.0, canvas=1000)

    assert escalados[0] == pytest.approx((250.0, 750.0))
    assert escalados[7] == pytest.approx((500.0, 400.0))


def test_el_ancla_lee_los_joints_escalados_sin_invertir_ejes():
    joints = {0: (0.1, 0.5), 8: (0.5, 0.45), 12: (0.5, 0.55), 14: (0.8, 0.45)}
    escalados = gs._escala_joints(joints, 1.0, canvas=1000)
    eje_x, pie_y = gs.ancla_de_esqueleto(escalados)

    assert eje_x == pytest.approx(500.0, abs=1)
    assert pie_y == pytest.approx(800.0, abs=1)


def test_la_pose_se_dibuja_transponiendo_para_pil():
    # Una (y, x) = (100, 700) tiene que pintar en la fila 100, columna 700.
    lienzo = gs._dibujar_pose({0: (100.0, 700.0)}, canvas=1024, ancho_hueso=16)

    assert lienzo.shape == (1024, 1024, 3)
    assert tuple(lienzo[100, 700]) == (255, 0, 255)
    # En (x, y) -> (700, 100) no hay nada: la transposicion no es un no-op.
    assert tuple(lienzo[700, 100]) == (0, 0, 0)


# --- composicion de la pose ---------------------------------------------


def test_la_pose_se_compone_sobre_negro_y_no_deja_rgb_fantasma():
    pose = np.zeros((LIENZO, LIENZO, 4), dtype=np.uint8)
    pose[100:120, 100:120] = (255, 0, 255, 0)  # magenta totalmente invisible
    compuesta = gs.componer_pose_sobre_negro(pose)

    assert compuesta.shape == (LIENZO, LIENZO, 3)
    assert compuesta.dtype == np.uint8
    assert tuple(compuesta[110, 110]) == (0, 0, 0)
    assert tuple(compuesta[10, 10]) == (0, 0, 0)


# --- connectivity / debris ---------------------------------------------


def test_los_componentes_conectados_cuentan_cuerpos_y_no_pixels_sueltos():
    alpha = np.zeros((16, 16), dtype=np.uint8)
    alpha[1:5, 1:5] = 255      # cuerpo
    alpha[10:14, 10:14] = 255   # otra cosa
    assert gs.componentes_conectados(alpha) == 2


def test_la_conectividad_por_cuatro_no_une_diagonales():
    alpha = np.zeros((8, 8), dtype=np.uint8)
    alpha[2, 2] = 255
    alpha[3, 3] = 255
    assert gs.componentes_conectados(alpha, 4) == 2
    assert gs.componentes_conectados(alpha, 8) == 1


def test_el_debris_mide_los_pixels_fuera_del_cuerpo():
    alpha = np.zeros((16, 16), dtype=np.uint8)
    alpha[4:12, 4:12] = 255
    assert gs.debris(alpha) == pytest.approx(0.0, abs=0.001)

    alpha[0, 0] = 255
    assert gs.debris(alpha) > 0.0


# --- metricas y QC ------------------------------------------------------


def test_las_metricas_de_la_referencia_son_las_esperadas():
    # La referencia es un PNG de 128 px, asi que sus metricas estan en pixeles
    # de ese lienzo: 114 de alto por 66 de ancho, con el pie en la fila 120 y el
    # eje en la 63.5. El presupuesto de 47 celdas se comprueba despues, ya
    # reducida a la celda de 64.
    ref = np.array(Image.open(gs.RUTA_REFERENCIA).convert("RGBA"))
    m = gs.metricas_sprite(ref)

    assert m["alto"] == 114
    assert m["ancho"] == 66
    assert m["pie"] == 120
    assert m["centro_x"] == pytest.approx(63.5, abs=1)
    assert m["n_colores"] <= 32
    assert m["componentes"] == 1


def test_la_referencia_reducida_cabe_en_el_presupuesto_de_la_celda():
    ref = np.array(Image.open(gs.RUTA_REFERENCIA).convert("RGBA"))
    m = gs.metricas_sprite(ref)
    sprite = np.array(
        _reduccion(ref, eje_x=m["centro_x"], pie_y=m["pie"]),
    )

    assert sprite.shape == (GRID, GRID, 4)
    filas, columnas = _bbox(sprite[..., 3] > 0)
    assert len(filas) == ALTO_CELDAS
    assert filas[-1] == CELDA_PIE
    assert filas[0] == CELDA_PIE - ALTO_CELDAS + 1
    assert columnas.mean() == pytest.approx(CELDA_CENTRO, abs=1)


def test_la_referencia_aprueba_el_control_de_calidad():
    ref = np.array(Image.open(gs.RUTA_REFERENCIA).convert("RGBA"))
    qc = gs.qc_frame(ref, gs.REFERENCIA)
    assert qc.ok, f"la referencia deberia pasar: {qc.motivos}"
    assert qc.motivos == []


def test_el_qc_rechaza_ruido_aleatorio():
    rng = np.random.default_rng(0)
    sprite = np.zeros((GRID, GRID, 4), dtype=np.uint8)
    sprite[..., 3] = 255
    sprite[..., :3] = rng.integers(0, 255, (GRID, GRID, 3), dtype=np.uint8)

    qc = gs.qc_frame(sprite, gs.REFERENCIA)
    assert not qc.ok
    assert qc.motivos


def test_el_qc_rechaza_un_personaje_demasiado_grande():
    # El alto se juzga contra la caja declarada del frame, no contra la
    # referencia: un sprite fuera de su banda se nombra con un codigo corto.
    sujeto = _personaje(684, 132, 40, 300)
    sprite = np.array(_reduccion(sujeto, **_ancla(sujeto, 132, 40, 300)))
    grande = gs.escalar_sprite(sprite, 1.6)
    frame = gs.MATRIZ[0]

    qc = gs.qc_frame(grande, gs.REFERENCIA, frame=frame)
    assert not qc.ok
    assert qc.motivos == ("alto",)


def test_el_qc_rechaza_la_cobertura_descontrolada():
    ref = np.array(Image.open(gs.RUTA_REFERENCIA).convert("RGBA"))
    # Relleno la caja del personaje: la cobertura se dispara y las dimensiones
    # siguen siendo las correctas, asi que el QC tiene que notar el area.
    relleno = ref.copy()
    filas, columnas = _bbox(relleno[..., 3] > 0)
    relleno[filas[0] : filas[-1] + 1, columnas[0] : columnas[-1] + 1] = (200, 30, 30, 255)

    qc = gs.qc_frame(relleno, gs.REFERENCIA)
    assert not qc.ok
    assert any("cobertura" in motivo for motivo in qc.motivos)


# --- ensamblado ---------------------------------------------------------


def test_la_matriz_tiene_los_57_frames_de_las_cuatro_animaciones():
    # 4 + 6 + 4 + 5 frames por animacion, repetidos en las tres vistas.
    assert len(gs.TABLA_FILAS) == 12
    assert len(gs.MATRIZ) == 57
    assert {f.vista for f in gs.MATRIZ} == {"down", "up", "side"}
    for fila in gs.TABLA_FILAS:
        indices = [
            f.indice
            for f in gs.MATRIZ
            if f.vista == fila.vista and f.animacion == fila.animacion
        ]
        assert indices == list(range(1, fila.frames + 1))
        assert all(f.fila == fila.fila for f in gs.MATRIZ if f.vista == fila.vista
                   and f.animacion == fila.animacion)
    assert [f.clave for f in gs.MATRIZ][:3] == [
        "down_idle_1",
        "down_idle_2",
        "down_idle_3",
    ]


def test_la_hoja_ensambla_21_celdas_en_896x384():
    celda = np.zeros((GRID, GRID, 4), dtype=np.uint8)
    celda[60:100, 60:70] = (10, 20, 30, 255)
    marco = gs.ensamblar_spritesheet([celda] * 21, filas=3, columnas=7, grid=GRID)

    assert marco.shape == (3 * GRID, 7 * GRID, 4)
    # La celda de la fila 1, columna 5 cae en este rectangulo de la hoja.
    assert np.array_equal(marco[GRID : 2 * GRID, 5 * GRID : 6 * GRID], celda)


def test_la_hoja_no_se_arma_si_falta_alguna_celda():
    celda = np.zeros((GRID, GRID, 4), dtype=np.uint8)
    with pytest.raises(ValueError, match="celdas"):
        gs.ensamblar_spritesheet([celda] * 20, filas=3, columnas=7, grid=GRID)


# --- semillas y reintentos ---------------------------------------------


def test_la_semilla_es_reproducible_y_cambia_con_cada_frame():
    base = gs.semilla("sombra_velada", "frontal", "idle", 1)
    assert base == gs.semilla("sombra_velada", "frontal", "idle", 1)
    assert base != gs.semilla("sombra_velada", "frontal", "idle", 2)
    assert base != gs.semilla("sombra_velada", "trasera", "idle", 1)
    assert 0 <= base < 2**32


def test_la_semilla_de_la_celda_depende_del_personaje():
    # Si la semilla ignorara el personaje, dos personajes compartiriamos el
    # mismo ruido y solo cambiaria el prompt.
    llamadas = []
    buena = np.array(Image.open(gs.RUTA_REFERENCIA).convert("RGBA"))

    def generar(seed):
        llamadas.append(seed)
        return buena

    for personaje in ("sombra_velada", "monje_cicatriz"):
        gs.generar_celda(
            gs.MATRIZ[0],
            generar=generar,
            qc=lambda sprite: gs.qc_frame(sprite, gs.REFERENCIA),
            intentos=1,
            personaje=personaje,
        )

    assert llamadas[0] == gs.semilla("sombra_velada", "down", "idle", 1)
    assert llamadas[1] == gs.semilla("monje_cicatriz", "down", "idle", 1)
    assert llamadas[0] != llamadas[1]


def test_reintenta_con_semillas_siguientes_hasta_pasar_el_qc():
    llamado = []
    buena = np.array(Image.open(gs.RUTA_REFERENCIA).convert("RGBA"))

    def generar(seed):
        llamado.append(seed)
        return buena if len(llamado) >= 3 else np.zeros((GRID, GRID, 4), np.uint8)

    resultado = gs.generar_celda(
        gs.MATRIZ[0],
        generar=generar,
        qc=lambda sprite: gs.qc_frame(sprite, gs.REFERENCIA),
        intentos=3,
    )

    assert resultado.estado == "ok"
    assert resultado.intentos == 3
    assert len(llamado) == 3
    assert llamado[1] == llamado[0] + 1
    assert llamado[2] == llamado[0] + 2


def test_la_celda_queda_pendiente_si_agota_los_intentos():
    resultado = gs.generar_celda(
        gs.MATRIZ[0],
        generar=lambda seed: np.zeros((GRID, GRID, 4), np.uint8),
        qc=lambda sprite: gs.qc_frame(sprite, gs.REFERENCIA),
        intentos=3,
    )

    assert resultado.estado == "pendiente"
    assert resultado.intentos == 3
    assert resultado.qc is not None
    assert resultado.qc.motivos


def test_una_celda_pendiente_impide_ensamblar_la_hoja():
    celda = np.zeros((GRID, GRID, 4), dtype=np.uint8)
    resultados = {f.clave: gs.ResultadoCelda(frame=f, estado="ok", imagen=celda) for f in gs.MATRIZ}
    resultados[gs.MATRIZ[5].clave] = gs.ResultadoCelda(
        frame=gs.MATRIZ[5], estado="pendiente", imagen=None
    )

    with pytest.raises(ValueError, match="pendiente"):
        gs.armar_hoja(resultados, filas=3, columnas=7, grid=GRID)


def test_la_hoja_coloca_cada_frame_en_su_slot_aunque_lleguen_desordenadas():
    # Orden alfabetico de claves: down < side < up, pero las filas canonicas
    # son down (0-3), up (4-7) y side (8-11), asi que ordenar por clave
    # intercambia `up` y `side`. Cada celda lleva un color que identifica su
    # slot, de modo que cualquier colocacion por orden de clave se ve.
    resultados = {}
    for frame in gs.MATRIZ:
        celda = np.zeros((GRID, GRID, 4), dtype=np.uint8)
        celda[10:20, 10:20] = (frame.fila + 1, frame.columna + 1, 7, 255)
        resultados[frame.clave] = gs.ResultadoCelda(frame=frame, estado="ok", imagen=celda)
    desordenado = dict(sorted(resultados.items()))

    hoja = gs.armar_hoja(desordenado)

    assert hoja.shape == (gs.FILAS * GRID, gs.COLUMNAS * GRID, 4)
    for frame in gs.MATRIZ:
        recorte = hoja[
            frame.fila * GRID : (frame.fila + 1) * GRID,
            frame.columna * GRID : (frame.columna + 1) * GRID,
        ]
        esperado = np.full((10, 10, 4), (frame.fila + 1, frame.columna + 1, 7, 255), dtype=np.uint8)
        assert np.array_equal(recorte[10:20, 10:20], esperado), frame.clave


def test_los_huecos_de_la_rejilla_quedan_transparentes():
    # `idle` deja 2 huecos, `roll` 2 y `death` 1 por vista: 15 celdas
    # transparentes en total sobre 72 slots.
    celda = np.zeros((GRID, GRID, 4), dtype=np.uint8)
    celda[10:20, 10:20] = (9, 9, 9, 255)
    resultados = {f.clave: gs.ResultadoCelda(frame=f, estado="ok", imagen=celda) for f in gs.MATRIZ}

    hoja = gs.armar_hoja(resultados)

    for fila in gs.TABLA_FILAS:
        for columna in range(fila.frames, gs.COLUMNAS):
            recorte = hoja[
                fila.fila * GRID : (fila.fila + 1) * GRID,
                columna * GRID : (columna + 1) * GRID,
            ]
            assert np.array_equal(recorte, np.zeros((GRID, GRID, 4), dtype=np.uint8)), (
                f"la celda ({fila.vista}/{fila.animacion}, col {columna}) deberia estar vacia"
            )


# --- prompts ------------------------------------------------------------


class _PipeFalso:
    """Tokenizer que cuenta palabras como si fueran tokens."""

    def __call__(self, texto, verbose=False):
        return SimpleNamespace(input_ids=[0] * len(texto.split()))


def _pipe_falso():
    tok = _PipeFalso()
    return SimpleNamespace(tokenizer=tok, tokenizer_2=tok)


def test_el_prompt_largo_se_trocea_sin_perder_una_sola_palabra():
    texto = ", ".join(f"instruccion {i} con relleno de palabras" for i in range(14))
    trozos = generar_sprite.trocear_prompt(_pipe_falso(), texto)

    assert len(trozos) > 1
    assert all(len(t.split()) <= 75 for t in trozos)
    original = [p.strip() for p in texto.split(",")]
    juntado = [p.strip() for t in trozos for p in t.split(",")]
    assert juntado == original


def test_un_prompt_corto_no_se_trocea():
    texto = "pixel art sprite de un monje, plain solid magenta background"
    assert generar_sprite.trocear_prompt(_pipe_falso(), texto) == [texto]


# --- poses por frame ----------------------------------------------------

VISTAS = ("down", "up", "side")


def test_el_alias_legacy_normaliza_la_vista_y_la_animacion():
    # La tabla de poses se indexa por clave canonica, pero el contrato Unity
    # sigue hablando en `frontal/trasera/lateral` y `walking`. El alias existe
    # para no romper ese contrato; esta es la unica prueba que lo fija.
    marco = gs.Frame("frontal", "walking", 1, gs.DURACION_WALK, True)

    assert marco.clave == "down_walk_1"
    assert gs.VISTA_A_LEGACY["down"] == "frontal"
    assert gs.VISTA_DESDE_LEGACY["trasera"] == "up"
    assert gs.ANIMACION_DESDE_LEGACY["walking"] == "walk"
    assert gs.animacion_legacy_de_manifiesto("walk") == "walking"
    assert gs.animacion_legacy_de_manifiesto("nueva") == "nueva"


def test_hay_una_pose_para_cada_frame_de_la_matriz():
    # Si falta una pose, ese frame se generaria sin control de estructura y el
    # modelo inventaria una postura: la hoja saldria con un personaje que cambia
    # de esqueleto entre celdas.
    assert set(gs.POSES_BODY_25) == {f.clave for f in gs.MATRIZ}


def test_cada_pose_tiene_los_25_joints_del_esqueleto_bodies25():
    for clave, pose in gs.POSES_BODY_25.items():
        assert set(pose) == set(range(25)), clave


def test_las_poses_dentro_del_lienzo_normalizado():
    for clave, pose in gs.POSES_BODY_25.items():
        for joint, (y, x) in pose.items():
            assert 0.0 <= y <= 1.0, (clave, joint)
            assert 0.0 <= x <= 1.0, (clave, joint)


def test_en_todas_las_poses_la_cabeza_queda_arriba_y_los_pies_abajo():
    for clave, pose in gs.POSES_BODY_25.items():
        assert pose[0][0] < pose[8][0] < max(y for y, _ in pose.values()), clave


def test_toda_pose_apoya_al_menos_un_pie_en_el_suelo():
    # Un personaje flotando rompe el anclaje: la hoja lo dejaria colgando y la
    # altura de la celda deja de ser la del cuerpo.
    for clave, pose in gs.POSES_BODY_25.items():
        assert gs.pie_de_apoyo(pose) in {"derecha", "izquierda"}, clave


@pytest.mark.parametrize("vista", VISTAS)
def test_el_ciclo_de_caminar_alterna_el_pie_de_apoyo(vista):
    # El ciclo son 6 fotogramas: 1 y 2 apoyan la derecha, 3 y 4 la izquierda y
    # 5 y 6 vuelven a la derecha para cerrar el paso. Sin esa alternancia el
    # ciclo se lee como un balanceo en el sitio, no como una marcha.
    for indice, esperado in (
        (1, "derecha"),
        (2, "derecha"),
        (3, "izquierda"),
        (4, "izquierda"),
        (5, "derecha"),
        (6, "derecha"),
    ):
        pose = gs.POSES_BODY_25[f"{vista}_walk_{indice}"]
        assert gs.pie_de_apoyo(pose) == esperado, (vista, indice)


@pytest.mark.parametrize("vista", VISTAS)
def test_los_dos_frames_de_contacto_tienen_el_pie_adelantado_al_otro_lado(vista):
    uno = gs.POSES_BODY_25[f"{vista}_walk_1"]
    tres = gs.POSES_BODY_25[f"{vista}_walk_3"]
    assert uno[11][1] != tres[11][1], "tobillo derecho"
    assert uno[14][1] != tres[14][1], "tobillo izquierdo"


@pytest.mark.parametrize("vista", VISTAS)
def test_las_poses_de_una_vista_no_se_repiten(vista):
    claves = (
        [f"{vista}_idle_{i}" for i in (1, 2, 3, 4)]
        + [f"{vista}_walk_{i}" for i in (1, 2, 3, 4, 5, 6)]
        + [f"{vista}_roll_{i}" for i in (1, 2, 3, 4)]
        + [f"{vista}_death_{i}" for i in (1, 2, 3, 4, 5)]
    )
    poses = [gs.POSES_BODY_25[clave] for clave in claves]
    assert len({tuple(sorted(p.items())) for p in poses}) == len(poses)


def test_la_pose_se_dibuja_centrada_con_la_cabeza_arriba():
    # BODY-25 habla (y, x). Si el dibujo invirtiera el par, el ControlNet
    # recibiria un personaje tumbado y aprenderia de las fotos tumbadas.
    # Los joints se escalan a pixeles antes de dibujar, que es la convencion de
    # toda la cadena: `_escala_joints` alimenta al dibujo y al anclaje.
    joints = gs._escala_joints(gs.POSES_BODY_25["down_idle_1"], 1.0, canvas=256)
    imagen = gs._dibujar_pose(joints, canvas=256, ancho_hueso=4)
    assert imagen.shape == (256, 256, 3)

    mask = (imagen == (255, 0, 255)).any(axis=2)
    filas = np.nonzero(mask.any(axis=1))[0]
    columnas = np.nonzero(mask.any(axis=0))[0]
    assert (imagen[0, 0] == 0).all(), "el fondo del control debe ser negro"
    assert filas[0] < filas[-1] / 2
    assert columnas.mean() == pytest.approx(128, abs=4)


# --- prompts por frame --------------------------------------------------


def test_el_preset_de_frame_trae_pose_y_descripcion():
    frame = gs.MATRIZ[0]
    preset = gs.preset_de_frame(frame)
    assert preset.frame is frame
    assert preset.pose == gs.POSES_BODY_25[frame.clave]
    assert preset.descripcion


def test_el_prompt_base_mantiene_el_fondo_magenta():
    # El fondo magenta es lo que despues separa al personaje; si el modelo lo
    # deja de recibir, la cuadricula con loso 21 frames se pierde.
    assert "plain solid magenta background" in gs.construir_prompt_base("sombra_velada")


def test_el_prompt_base_nombra_al_menos_dos_conceptos_de_direccion():
    base = gs.construir_prompt_base("sombra_velada").lower()
    encontrados = [c for c in gs.CONCEPTOS_DIRECCION if c in base]
    assert len(encontrados) >= 2, encontrados


def test_cada_frame_le_pide_al_modelo_una_imagen_distinta():
    # El llamador real cachea por prompt: si dos frames piden el mismo texto,
    # el segundo hereda la imagen del primero y la animacion se repite.
    prompts = [gs.construir_prompt_frame("sombra_velada", f) for f in gs.MATRIZ]
    assert len(prompts) == 57
    assert len(set(prompts)) == 57
    assert all("plain solid magenta background" in p for p in prompts)


def test_los_frames_que_comparten_apoyo_no_comparten_texto():
    # walk 1/2/5/6 apoyan el pie derecho y walk 3/4 el izquierdo; los de
    # apoyo pueden ser bodily iguales en partes, pero el prompt los distingue.
    derecha = [gs.construir_prompt_frame("sombra_velada", f)
               for f in gs.MATRIZ if f.animacion == "walk"
               and gs.pie_de_apoyo(gs.POSES_BODY_25[f.clave]) == "derecha"]
    assert len(set(derecha)) == len(derecha)


def test_el_prompt_negativo_no_toca_el_fondo_magenta():
    negativo = gs.construir_prompt_negativo().lower()
    assert "magenta" not in negativo
    assert len(negativo.split(",")) <= 20


# --- Pipeline inyectable: control, postprocesado y modelo falso ---------

#: El fondo que el prompt obliga a poner y que despues se recorta. Va aqui y
#: no en el modulo porque es una constante del TEST: si el modulo la cambias,
#: el fake dejaria de estar pegado a lo que el prompt pide.
MAGENTA = (255, 0, 255)


def _caja_de(alfa: np.ndarray) -> tuple[int, int, int, int]:
    """`(fila_ini, fila_fin, col_ini, col_fin)` de la mascara opaca."""
    filas = np.nonzero(alfa.any(axis=1))[0]
    columnas = np.nonzero(alfa.any(axis=0))[0]
    return int(filas[0]), int(filas[-1]), int(columnas[0]), int(columnas[-1])


def _caja_visible(rgb: np.ndarray) -> tuple[int, int, int, int]:
    """La caja del sujeto sobre el lienzo del fake: todo lo que no sea el fondo
    magenta es el recorte pegado, y su ultima fila dice donde quedo el pie."""
    return _caja_de((rgb != np.array(MAGENTA, dtype=np.uint8)).any(axis=2))


def _llamar_falso(frame, seed, control):
    """Modelo de mentira: la referencia pegada donde el esqueleto dice que va.

    Delega en `gs.llamador_falso` (el fake vive ya en el modulo para que `main`
    y el test compartan un unico contrato). No simula a SDXL, simula SU
    CONTRATO: recibe el frame, la semilla y el control, y devuelve un lienzo RGB
    del tamano del lienzo de trabajo. Con este fake la cadena completa llega a una
    celda que pasa el QC, cualquier fallo es de anclaje o de postprocesado, nunca
    del modelo: por eso el test se puede     ejecutar sin GPU.
    """
    return gs.llamador_falso(frame, seed, control=control)


def test_el_control_dibuja_la_pose_del_frame_en_negro_y_magenta():
    # El ControlNet OpenPose solo entiende negro de fondo y lineas de color:
    # un control sobre otro fondo le ensena al modelo a conservar ese fondo.
    control = gs.control_de_frame(gs.MATRIZ[0])
    assert control["imagen"].shape == (gs.LIENZO, gs.LIENZO, 3)
    assert (control["imagen"][0, 0] == 0).all(), "el fondo del control debe ser negro"
    assert (control["imagen"] == MAGENTA).any(axis=2).any(), "debe haber huesos"


def test_el_control_escala_los_joints_al_lienzo():
    # Los joints viajan en pixeles del lienzo, no normalizados: el anclaje
    # compara la Y del pie con la ultima fila opaca y las dos tienen que hablar
    # el mismo idioma.
    frame = gs.MATRIZ[0]
    control = gs.control_de_frame(frame)
    esperados = gs._escala_joints(gs.POSES_BODY_25[frame.clave], 1.0, canvas=gs.LIENZO)
    assert control["joints"] == esperados


@pytest.mark.parametrize("frame", gs.MATRIZ)
def test_todo_frame_tiene_control_dibujable(frame):
    # 21 poses y 21 controles: si uno se cae, ese frame sale sin estructura y el
    # modelo inventa una postura que no casa con las demas celdas de su fila.
    control = gs.control_de_frame(frame)
    assert control["imagen"].shape == (gs.LIENZO, gs.LIENZO, 3)
    assert set(control["joints"]) == set(range(25))


def test_la_cadena_deja_una_celda_de_128_con_cuatro_canales():
    frame = gs.MATRIZ[0]
    control = gs.control_de_frame(frame)
    rgb = _llamar_falso(frame, 1234, control)
    celda = gs.cadena_post_proceso(rgb, control["joints"])
    assert celda.shape == (gs.GRID, gs.GRID, 4)
    assert celda[..., 3].max() == 255, "la celda debe traer algo opaco"


def test_un_fake_de_referencia_pasa_el_qc_de_la_cadena_real():
    # La prueba de fuego: la referencia ampliada entra por la MISMA cadena que
    # usara SDXL y sale con el veredicto del QC de verdad. Si aqui falla, el
    # anclaje o el recorte estan rotos y cualquier tanda de GPU lo pagaria.
    frame = gs.MATRIZ[0]
    control = gs.control_de_frame(frame)
    ref = gs.cargar_referencia()
    generar = gs.generador_de_frame(frame, _llamar_falso, control)
    veredicto = gs.qc_frame(generar(99), ref)
    assert veredicto.ok, veredicto.motivos


def test_el_generador_acepta_no_recibir_control():
    # Sin control la cadena sigue viva (el modelo puede no necesitarlo): lo que
    # no puede pasar es que `generar` deje de existir.
    generar = gs.generador_de_frame(gs.MATRIZ[0], _llamar_falso, control=None)
    assert generar(1).shape == (gs.GRID, gs.GRID, 4)


def test_el_generador_pasa_el_control_de_su_propio_frame_al_llamable():
    # El llamable real no sabe que frame es: recibe el control ya escalado. Si
    # `generador_de_frame` calculara otro, el ControlNet recibiria otra postura
    # y la hoja saldria con el esqueleto cruzado entre celdas.
    visto = {}

    def llamar(frame, seed, control):
        visto["frame"] = frame
        visto["control"] = control
        return _llamar_falso(frame, seed, control)

    frame = gs.MATRIZ[5]
    control = gs.control_de_frame(frame)
    gs.generador_de_frame(frame, llamar, control)(3)
    assert visto["frame"] is frame
    assert visto["control"] is control


def test_una_celda_generada_con_el_fake_aprueba_el_qc_sin_tocar_la_gpu():
    # Es el enlace que usara `main()`: generar_celda -> generador_de_frame ->
    # cadena -> QC. Con el fake, una tanda entera se ensaya sin descargar ni un
    # peso de SDXL.
    frame = gs.MATRIZ[3]
    control = gs.control_de_frame(frame)
    ref = gs.cargar_referencia()
    generar = gs.generador_de_frame(frame, _llamar_falso, control)
    resultado = gs.generar_celda(frame, generar, lambda s: gs.qc_frame(s, ref))
    assert resultado.estado == "ok", resultado.qc.motivos
    assert resultado.intentos == 1, "el fake pasa a la primera: no debe gastar semillas"


def test_la_cruda_se_guarda_a_768_para_ver_donde_se_rompio(tmp_path):
    # La celda final es 128 y ya viene recortada: cuando el QC falla no hay
    # forma de saber si el modelo genero un palo o si el recorte se lo comio.
    # Guardar la cruda a 768 deja el diagnostico.
    frame = gs.MATRIZ[3]
    generar = gs.generador_de_frame(
        frame, _llamar_falso, gs.control_de_frame(frame), guardar_cruda=tmp_path
    )
    generar(3)
    cruda = tmp_path / f"cruda_{frame.clave}.png"
    assert cruda.is_file()
    with Image.open(cruda) as imagen:
        assert imagen.size == (LIENZO, LIENZO)
        assert imagen.mode == "RGB"


def test_sin_carpeta_de_crudas_no_se_escribe_nada(tmp_path):
    # Por defecto no se guarda nada: 21 crudas de 768 son ~30 MB de ruido en
    # una tanda normal. Quien las quiera, las pide.
    frame = gs.MATRIZ[3]
    generar = gs.generador_de_frame(frame, _llamar_falso, gs.control_de_frame(frame))
    sprite = generar(3)
    assert sprite.shape == (GRID, GRID, 4)
    assert list(tmp_path.iterdir()) == []


# --- CLI: el contrato con quien lo lanza a mano --------------------------


def test_la_cli_falsa_no_carga_sdxl_y_devuelve_hoja(tmp_path, monkeypatch):
    # `--falso` es la unica forma de ensayar el cierre sin GPU ni pesos: si
    # tocara `cargar_modelo`, la prueba tardaria minutos y bajaria 7 GB.
    def _no_deberia_cargar(*args, **kwargs):
        raise AssertionError("--falso no puede cargar SDXL")

    monkeypatch.setattr(gs, "cargar_modelo", _no_deberia_cargar)
    codigo = gs.main(["--falso", "--salida", str(tmp_path)])
    assert codigo == 0
    assert (tmp_path / "spritesheet.png").is_file()
    assert (tmp_path / "frames.json").is_file()
    assert (tmp_path / "idle" / "frontal").is_dir()


def test_la_cli_con_limite_avisa_de_lo_pendiente_y_falla(tmp_path, monkeypatch):
    # Con `--limite 2` no se puede montar la hoja completa. El codigo de salida
    # tiene que delatarlo: si devolviera 0, un script creeria que esta todo.
    monkeypatch.setattr(gs, "cargar_modelo", lambda *a, **k: None)
    codigo = gs.main(["--falso", "--limite", "2", "--salida", str(tmp_path)])
    assert codigo != 0
    assert not (tmp_path / "spritesheet.png").exists()


def test_la_cli_copia_la_referencia_al_destino(tmp_path, monkeypatch):
    # El IP-Adapter y el QC leen de la misma referencia que se llevo el
    # proyecto: si la hoja queda generada contra un sprite y se compara contra
    # otro, el QC no significa nada.
    monkeypatch.setattr(gs, "cargar_modelo", lambda *a, **k: None)
    gs.main(["--falso", "--salida", str(tmp_path)])
    copia = tmp_path / "referencias" / "sprite_3.png"
    assert copia.is_file()
    assert hashlib.sha256(copia.read_bytes()).hexdigest().upper() == gs.SHA_REFERENCIA


def test_la_cli_acepta_una_referencia_alternativa(tmp_path, monkeypatch):
    # `--referencia` existe para probar con otro personaje sin tocar el codigo.
    # La silueta es un personaje con transparencia; un rectangulo opaco que
    # llenara la celda no es una referencia valida y el QC lo rechaza a proposito.
    alternativa = tmp_path / "otro.png"
    lienzo = Image.new("RGBA", (96, 128), (0, 0, 0, 0))
    brocha = ImageDraw.Draw(lienzo)
    brocha.ellipse([36, 6, 60, 30], fill=(30, 150, 120, 255))      # cabeza
    brocha.rectangle([40, 28, 56, 74], fill=(30, 150, 120, 255))   # torso
    brocha.rectangle([28, 32, 39, 72], fill=(30, 150, 120, 255))   # brazo izq
    brocha.rectangle([57, 32, 68, 72], fill=(30, 150, 120, 255))   # brazo der
    brocha.rectangle([40, 72, 47, 122], fill=(30, 150, 120, 255))  # pierna izq
    brocha.rectangle([49, 72, 56, 122], fill=(30, 150, 120, 255))  # pierna der
    lienzo.save(alternativa)
    monkeypatch.setattr(gs, "cargar_modelo", lambda *a, **k: None)
    codigo = gs.main(["--falso", "--referencia", str(alternativa), "--salida", str(tmp_path / "sal")])
    assert codigo == 0
    assert (tmp_path / "sal" / "referencias" / "otro.png").is_file()


# --- Prompt positivo y llamador real -------------------------------------
#
# El llamador real es la unica pieza que habla con la GPU. No se prueba con
# pesos: se prueba con un tubo de mentira que deja ver LO QUE SE MANDA, que es
# justo donde esta el contrato (que imagen, que tamano, cuantos pasos, que
# generador y que se codifica una sola vez lo que se puede).


class _TuboFalso:
    """Pipeline de mentira: guarda cada llamada y devuelve un lienzo RGB.

    No codifica ni desenovera nada; solo anota los argumentos con los que le
    llamaron y devuelve una imagen del tamano del lienzo de trabajo.
    """

    def __init__(self):
        self.llamadas = []
        self.ip_images = []

    def set_ip_adapter_image(self, imagen):
        self.ip_images.append(imagen)

    def __call__(self, **kwargs):
        self.llamadas.append(kwargs)
        return SimpleNamespace(
            images=[Image.new("RGB", (gs.LIENZO, gs.LIENZO), (8, 8, 12))]
        )


class _GeneradorFalso:
    """`torch.Generator` de mentira: apunta el device y las semillas."""

    def __init__(self, device=None):
        self.device = device
        self.semillas = []

    def manual_seed(self, seed):
        self.semillas.append(seed)
        return self


class _TorchFalso:
    Generator = _GeneradorFalso


def _parchea_codificadores(monkeypatch):
    """Cambia los dos codificadores por marcadores que cuentan y se nombran.

    Devuelve el registro `{positivos: [...], negativos: n}` para poder
    comprobar cuantas veces se codifico cada texto. El troceado de verdad ya
    tiene sus pruebas en `generar_sprite.py`; aqui importa el CUENTO.
    """
    registro = {"positivos": [], "negativos": 0}

    def positivo(pipe, texto):
        registro["positivos"].append(texto)
        return f"embeds:{texto}", f"pooled:{texto}"

    def negativo(pipe, texto):
        registro["negativos"] += 1
        return f"neg_embeds:{texto}", f"neg_pooled:{texto}"

    monkeypatch.setattr(gs, "codificar_prompt_positivo", positivo)
    monkeypatch.setattr(gs, "codificar_prompt_negativo", negativo)
    return registro


def _llamador_real_en_cpu(monkeypatch, pipe, **kwargs):
    """`llamador_real` con `torch` de mentira: sin GPU, sin pesos.

    Devuelve `(llamar, registro)` para poder inspeccionar las codificaciones.
    """
    registro = _parchea_codificadores(monkeypatch)
    monkeypatch.setitem(sys.modules, "torch", _TorchFalso)
    return gs.llamador_real(pipe, **kwargs), registro


def test_los_pasos_y_la_guia_por_defecto_son_los_del_script_de_referencia():
    # Son los valores con los que se calibro la referencia; `--pasos` puede
    # subirlos en un smoke, pero el valor por defecto es el que ya se sabe que
    # aguanta el QC. Si un dia cambian, el motivo esta en el commit.
    assert gs.PASOS == 30
    assert gs.GUIDANCE == 7.5


def test_codificar_prompt_positivo_pide_el_negativo_vacio(monkeypatch):
    # Delega en el helper de `generar_sprite` con el otro lado VACIO: codificar
    # tambien el negativo aqui seria tirar GPU en algo que el llamador real
    # hace una sola vez para los 21 frames.
    vistos = {}

    def codificar(pipe, prompt, negativo):
        vistos["args"] = (pipe, prompt, negativo)
        return ("embeds", "neg_embeds", "pooled", "neg_pooled")

    monkeypatch.setattr(gs.gs_base, "codificar_prompt", codificar)
    embeds, pooled = gs.codificar_prompt_positivo("PIPE", "un texto de prueba")
    assert (embeds, pooled) == ("embeds", "pooled")
    assert vistos["args"] == ("PIPE", "un texto de prueba", "")


def test_el_llamador_real_encoda_el_prompt_de_su_frame_y_el_negativo_compartido(monkeypatch):
    # Al pipeline de verdad no se le pasa texto: se le pasan embeddings. Hay que
    # comprobar que lo que entra es el prompt de ESE frame y el negativo comun.
    pipe = _TuboFalso()
    llamar, _ = _llamador_real_en_cpu(monkeypatch, pipe)
    frame = gs.MATRIZ[0]
    llamar(frame, 1, gs.control_de_frame(frame))
    llamada = pipe.llamadas[0]
    esperado = gs.construir_prompt_frame("sombra_velada", frame)
    assert llamada["prompt_embeds"] == f"embeds:{esperado}"
    assert llamada["negative_prompt_embeds"] == f"neg_embeds:{gs.construir_prompt_negativo()}"


def test_el_llamador_real_manda_el_control_el_lienzo_los_pasos_y_el_generador(monkeypatch):
    pipe = _TuboFalso()
    llamar, _ = _llamador_real_en_cpu(monkeypatch, pipe)
    frame = gs.MATRIZ[0]
    control = gs.control_de_frame(frame)
    llamar(frame, 7, control)
    llamada = pipe.llamadas[0]
    # El ControlNet recibe el mapa de postura tal cual, no una copia.
    assert llamada["image"] is control["imagen"]
    assert llamada["height"] == llamada["width"] == gs.LIENZO
    assert llamada["num_inference_steps"] == gs.PASOS
    assert llamada["guidance_scale"] == gs.GUIDANCE
    # Generador en CPU y con la semilla del frame: mismo frame, misma imagen.
    generador = llamada["generator"]
    assert generador.device == "cpu"
    assert generador.semillas == [7]


def test_el_llamador_real_devuelve_un_rgb_del_lienzo(monkeypatch):
    pipe = _TuboFalso()
    llamar, _ = _llamador_real_en_cpu(monkeypatch, pipe)
    frame = gs.MATRIZ[0]
    rgb = llamar(frame, 1, gs.control_de_frame(frame))
    assert rgb.shape == (gs.LIENZO, gs.LIENZO, 3)
    assert rgb.dtype == np.uint8


def test_el_llamador_real_reutiliza_el_prompt_y_el_negativo_entre_frames(monkeypatch):
    # El prompt de un frame es el mismo en cada reintento con otra semilla, y el
    # negativo es el mismo para los 21: codificarlos por fotograma es lo que
    # hace que una tanda de GPU tarde minutos de mas.
    pipe = _TuboFalso()
    llamar, registro = _llamador_real_en_cpu(monkeypatch, pipe)
    primero, segundo = gs.MATRIZ[0], gs.MATRIZ[1]
    llamar(primero, 1, gs.control_de_frame(primero))
    llamar(primero, 2, gs.control_de_frame(primero))
    assert len(registro["positivos"]) == 1, "el mismo frame no se recodifica"
    llamar(segundo, 3, gs.control_de_frame(segundo))
    assert len(registro["positivos"]) == 2
    assert registro["negativos"] == 1, "el negativo es uno para toda la hoja"


def test_el_llamador_real_acepta_pasos_y_guia_propios(monkeypatch):
    # Lo que llega por `--pasos` y `--guidance` tiene que llegar al pipeline.
    pipe = _TuboFalso()
    llamar, _ = _llamador_real_en_cpu(monkeypatch, pipe, pasos=7, guidance=3.5)
    frame = gs.MATRIZ[0]
    llamar(frame, 1, gs.control_de_frame(frame))
    llamada = pipe.llamadas[0]
    assert llamada["num_inference_steps"] == 7
    assert llamada["guidance_scale"] == 3.5


def test_el_llamador_real_pasa_la_referencia_en_rgb_una_sola_vez_al_ip_adapter(monkeypatch):
    # El IP-Adapter procesa la referencia: pasarle una imagen por frame es
    # repetir ese trabajo 21 veces, y con alfa en vez de RGB
    # `set_ip_adapter_image` se queja.
    pipe = _TuboFalso()
    llamar, _ = _llamador_real_en_cpu(monkeypatch, pipe)
    for frame in gs.MATRIZ[:2]:
        llamar(frame, 1, gs.control_de_frame(frame))
    assert len(pipe.ip_images) == 1
    assert pipe.ip_images[0].mode == "RGB"


# --- QC temporal: el balanceo tiene que verse en la hoja, no solo en la celda


def _sprite_desplazado(dx: int, lado: int = 100, y0: int = 14, x0: int = 5) -> np.ndarray:
    """Sprite sintetico: un rectangulo opaco de `lado` px corrido `dx`.

    Sirve para medir IoU exacto: con `lado=100`, un desplazamiento de 5 px deja
    95/105 = 0.905 y uno de 20 px deja 80/120 = 0.667, que es justo el corte del
    QC temporal. Asi la prueba no depende de que el sprite "parezca" moverse.
    `x0=5` deja holgura para que hasta un salto de 20 px quepa entero en la celda
    de 128: un recorte en el borde falsearia la IoU.
    """
    rgba = np.zeros((gs.GRID, gs.GRID, 4), dtype=np.uint8)
    rgba[y0 : y0 + lado, x0 + dx : x0 + dx + lado] = (255, 255, 255, 255)
    return rgba


def _qc_siempre_ok(sprite) -> gs.QC:
    return gs.QC(ok=True, motivos=[], metricas={})


def test_el_primer_frame_de_una_secuencia_no_tiene_nada_que_comparar():
    # El primer fotograma de cada secuencia no tiene vecino: el unico estado
    # inicial valido es "no hay con quien medir el balanceo".
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    qc = secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    assert qc.ok
    assert qc.motivos == []
    assert qc.metricas["iou_anterior"] is None


def test_un_qc_base_que_falla_llega_intacto_y_no_deja_memoria():
    # El QC temporal se apoya en el base, no lo reemplaza: si el base dice que
    # no, el temporal devuelve ese veredicto tal cual (mismo objeto), y sobre
    # todo no memoriza un sprite que jamas se acepto.
    base = gs.QC(ok=False, motivos=["alto 3 fuera de 114±3"], metricas={"alto": 3})
    secuencia = gs.SecuenciaTemporal(lambda sprite: base)
    qc = secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    assert qc is base
    siguiente = secuencia.verificar(gs.MATRIZ[1], _sprite_desplazado(5))
    assert siguiente.metricas["iou_anterior"] is None


def test_un_salto_pequeno_pasa_tras_el_primer_frame():
    # 5 px de balanceo dan IoU 0.905: es movimiento real y dentro de la banda.
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    qc = secuencia.verificar(gs.MATRIZ[1], _sprite_desplazado(5))
    assert qc.ok
    assert qc.motivos == []
    assert 0.89 < qc.metricas["iou_anterior"] < 0.92


def test_un_salto_grande_se_rechaza_por_iou():
    # 20 px de salto es un teletransporte o un corte de animacion, no balanceo.
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    qc = secuencia.verificar(gs.MATRIZ[1], _sprite_desplazado(20))
    assert not qc.ok
    assert any("iou" in motivo for motivo in qc.motivos)
    assert qc.metricas["iou_anterior"] < gs.QC_IOU[0]


def test_un_frame_identico_se_rechaza_por_iou():
    # El techo de 0.96 es lo que evita una hoja "correcta" pero muerta: dos
    # fotogramas identicos tienen IoU 1.0 y delatan que el animador no se movio.
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    qc = secuencia.verificar(gs.MATRIZ[1], _sprite_desplazado(0))
    assert not qc.ok
    assert any("iou" in motivo for motivo in qc.motivos)
    assert qc.metricas["iou_anterior"] == 1.0


def test_el_rechazado_no_sustituye_al_aceptado():
    # Si el sprite rechazado se memorizara, el siguiente frame se mediria
    # contra el: aqui se mide contra el ultimo ACEPTADO y por eso pasa.
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    assert not secuencia.verificar(gs.MATRIZ[1], _sprite_desplazado(20)).ok
    qc = secuencia.verificar(gs.MATRIZ[2], _sprite_desplazado(5))
    assert qc.ok
    assert 0.89 < qc.metricas["iou_anterior"] < 0.92


def test_el_ultimo_aceptado_es_siempre_la_referencia_siguiente():
    # 0 -> 5 -> 15: el ultimo salto son 10 px, que dan 90/110 = 0.818 contra el
    # frame de 5. Si la referencia se quedara en el primero de 0 px, daria
    # 85/115 = 0.739, por debajo del corte, y el frame caeria.
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    secuencia.verificar(gs.MATRIZ[0], _sprite_desplazado(0))
    assert secuencia.verificar(gs.MATRIZ[1], _sprite_desplazado(5)).ok
    qc = secuencia.verificar(gs.MATRIZ[2], _sprite_desplazado(15))
    assert qc.ok
    assert 0.81 < qc.metricas["iou_anterior"] < 0.83


def test_cada_vista_animacion_compara_contra_la_sua():
    # Frontal idle y frontal walking son secuencias distintas: la referencia del
    # idle no puede decidir si el primer paso de marcha esta bien.
    idle = gs.Frame("frontal", "idle", 1, gs.DURACION_IDLE, True)
    marcha = gs.Frame("frontal", "walking", 1, gs.DURACION_WALK, True)
    secuencia = gs.SecuenciaTemporal(_qc_siempre_ok)
    secuencia.verificar(idle, _sprite_desplazado(0))
    assert secuencia.verificar(marcha, _sprite_desplazado(20)).ok
    assert not secuencia.verificar(idle, _sprite_desplazado(20)).ok


# --- Exportacion: lo que Unity y el revisor van a leer de verdad ----------


def _celda_de_prueba(tinte=0):
    """RGBA de 128 sintetico, distinto por celda para poder distinguirlas."""
    celda = np.zeros((gs.GRID, gs.GRID, 4), dtype=np.uint8)
    celda[10:100, 20:60] = (198, 58, 46, 255)
    celda[0, 0] = (tinte, tinte, tinte, 255)
    return celda


def _resultado(frame, estado="ok", tinte=0):
    return gs.ResultadoCelda(
        frame=frame,
        estado=estado,
        imagen=_celda_de_prueba(tinte) if estado == "ok" else None,
        intentos=1,
        qc=_qc_siempre_ok(_celda_de_prueba(tinte)),
    )


def _resultados_completos():
    """Un `ok` por cada frame de la `MATRIZ`, con tinte propio por posicion."""
    return {
        f.clave: _resultado(f, tinte=n)
        for n, f in enumerate(gs.MATRIZ)
    }


def test_cada_celda_se_escribe_en_su_animacion_y_su_vista(tmp_path):
    # Unity recorta por carpeta, no por el manifiesto: el archivo tiene que
    # quedar donde el importador lo espera, `idle/frontal/`, no en un plano.
    # Las carpetas usan los nombres legacy, no los logicos del manifiesto:
    # `vista_legacy` traduce "down" a "frontal" y `animacion_legacy_de_manifiesto`
    # deja "idle" como "idle".
    frame = gs.MATRIZ[0]
    ruta = gs.exportar_celda(frame, _celda_de_prueba(), tmp_path)
    esperado = tmp_path / gs.animacion_legacy_de_manifiesto(frame.animacion) / frame.vista_legacy / f"{frame.clave}.png"
    assert ruta == esperado
    assert ruta.is_file()
    assert np.array_equal(np.array(Image.open(ruta)), _celda_de_prueba())


def test_las_previews_se_guardan_x8_para_revisar_a_ojo(tmp_path):
    # La celda de 128 es pequena para juzgarla: la preview x8 (1024) es la que
    # se mira a ojo. Una por celda y solo de las que salieron bien.
    resultados = _resultados_completos()
    clave = gs.MATRIZ[0].clave
    resultados[clave] = _resultado(gs.MATRIZ[0], estado="pendiente")
    rutas = gs.exportar_previews(resultados, tmp_path, factor=8)
    assert len(rutas) == len(gs.MATRIZ) - 1
    assert gs.MATRIZ[1].clave + "_x8.png" in [r.name for r in rutas]
    with Image.open(rutas[0]) as imagen:
        assert imagen.size == (gs.GRID * 8, gs.GRID * 8)


def test_la_hoja_se_escribe_ensamblada_por_posicion_de_frame(tmp_path):
    # `armar_hoja` coloca por fila/columna del frame, no por orden de claves:
    # si la hoja se guardara reordenada, las celdas cruzarian de fila.
    resultados = _resultados_completos()
    ruta = gs.exportar_hoja(gs.armar_hoja(resultados), tmp_path)
    assert ruta == tmp_path / "spritesheet.png"
    with Image.open(ruta) as imagen:
        assert imagen.size == (gs.COLUMNAS * gs.GRID, gs.FILAS * gs.GRID)
        assert imagen.convert("RGBA").getpixel((0, 0))[0] == 0  # tinte del frame 0


def test_el_manifiesto_json_lleva_la_misma_hoja_que_la_imagen(tmp_path):
    # El rect del manifiesto es lo que Unity recorta: si no coincide con el
    # pixel de la hoja, el juego muestra el trozo de otro frame.
    resultados = _resultados_completos()
    manifiesto = gs.construir_manifiesto(resultados)
    ruta = gs.exportar_manifiesto(manifiesto, tmp_path)
    assert ruta == tmp_path / "spritesheet.json"
    import json

    assert json.loads(ruta.read_text(encoding="utf-8"))["frames"][0]["rect"]["w"] == gs.GRID


def test_frames_unity_describe_ppu_pivot_y_los_dos_clips(tmp_path):
    # Unity no lee `spritesheet.json`: lee `frames.json` con su propio formato
    # (ppu, pivot y clips). Sin esto el importador no tiene nada que cortar.
    resultados = _resultados_completos()
    ruta = gs.exportar_frames_unity(gs.construir_manifiesto(resultados), tmp_path)
    import json

    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert ruta.name == "frames.json"
    assert datos["ppu"] == gs.PPU
    assert datos["pivot"] == {"x": 0.5, "y": 0.0}
    assert datos["hoja"] == "spritesheet"
    clips = {c["nombre"]: c for c in datos["clips"]}
    assert set(clips) == {"idle", "walking"}
    for nombre, clip in clips.items():
        assert clip["bucle"] is True
        assert clip["duracion_ms"] == (gs.DURACION_IDLE if nombre == "idle" else gs.DURACION_WALK)
        # Tres vistas (frontal, trasera, lateral) y 9 y 12 fotogramas.
        assert len(clip["vistas"]) == 3
        assert sum(len(v["frames"]) for v in clip["vistas"]) == (9 if nombre == "idle" else 12)


def test_exportar_todo_deja_la_carpeta_lista_para_unity(tmp_path):
    # Un solo comando debe dejar hoja, manifiesto y celdas sueltas: si falta
    # algo, hay que montarlo a mano 21 veces. El `frames.json` de Unity se
    # exporta aparte con `exportar_frames_unity`.
    resultados = _resultados_completos()
    rutas = gs.exportar_todo(resultados, tmp_path)
    assert rutas["hoja"].is_file()
    assert rutas["manifiesto"].is_file()
    assert len(rutas["celdas"]) == len(gs.MATRIZ)
    assert (tmp_path / "idle" / "frontal").is_dir()
    assert (tmp_path / "walking" / "lateral").is_dir()


def test_exportar_todo_se_niega_a_hoja_parcial_si_queda_pendiente(tmp_path):
    # Con `--limite 2` solo hay 2 celdas: ensamblar una hoja con huecos produce
    # una imagen que parece completa y recorta frames equivocados. Mejor error.
    resultados = _resultados_completos()
    resultados.pop(gs.MATRIZ[5].clave)
    with pytest.raises(ValueError, match="pendientes"):
        gs.exportar_todo(resultados, tmp_path)
    assert not (tmp_path / "spritesheet.png").exists()
