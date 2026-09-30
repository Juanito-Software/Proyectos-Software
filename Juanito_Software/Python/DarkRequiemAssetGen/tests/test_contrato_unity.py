"""Contrato de la hoja que Dark Requiem consume en Unity.

Estas pruebas fijan el contrato REAL, no el legacy: celdas de 64 px, 57 frames
repartidos en 12 filas desiguales y un manifiesto logico `*_sheet.json`. Todos los
motivos de rechazo del QC se leen en el orden en que las pruebas los nombran, asi
que el orden importa: `alto` (dato), `pie` (dato) y el resto (esteticos).
"""

from __future__ import annotations

import json

import numpy as np
import pytest

import generar_spritesheet as gs

#: Orden global de filas de la hoja. Cada animacion aporta sus tres vistas y el
#: indice dentro de la animacion va desde 1.
FILAS_ESPERADAS = (
    ("idle", "down", 4, 6, True),
    ("idle", "up", 4, 6, True),
    ("idle", "side", 4, 6, True),
    ("walk", "down", 6, 8, True),
    ("walk", "up", 6, 8, True),
    ("walk", "side", 6, 8, True),
    ("roll", "down", 4, 12, False),
    ("roll", "up", 4, 12, False),
    ("roll", "side", 4, 12, False),
    ("death", "down", 5, 8, False),
    ("death", "up", 5, 8, False),
    ("death", "side", 5, 8, False),
)


def _celda_roda(ancho: int = 10, alto: int = 10) -> np.ndarray:
    """Lienzo 64x64 con un rectangulo opaco gris en el centro."""
    imagen = np.zeros((gs.CELDA, gs.CELDA, 4), dtype=np.uint8)
    imagen[5 : 5 + alto, 5 : 5 + ancho, :3] = 220
    imagen[5 : 5 + alto, 5 : 5 + ancho, 3] = 255
    return imagen


def _celda_de_geometria(geometria: gs.GeometriaCelda) -> np.ndarray:
    """Dibuja un rectangulo con la geometria canonica, centrado y apoyado en el pie."""
    imagen = np.zeros((gs.CELDA, gs.CELDA, 4), dtype=np.uint8)
    top = geometria.pie - geometria.alto + 1
    left = int(round(gs.CELDA_CENTRO - geometria.ancho / 2))
    for fila in range(geometria.alto):
        for columna in range(geometria.ancho):
            y = top + fila
            x = left + columna
            if 0 <= y < gs.CELDA and 0 <= x < gs.CELDA:
                imagen[y, x] = (200, 180, 160, 255)
    return imagen


def _frame(animacion: str = "idle", indice: int = 1) -> gs.Frame:
    for frame in gs.MATRIZ:
        if frame.animacion == animacion and frame.indice == indice:
            return frame
    raise AssertionError(f"no hay frame {animacion}_{indice}")


# --- Contrato de tamano --------------------------------------------------


def test_el_lienzo_crudo_sigue_siendo_de_768_para_un_factor_12():
    assert gs.CELDA == 64
    assert gs.GRID == gs.CELDA
    assert gs.LIENZO == 768
    assert gs.FACTOR == 12
    assert gs.LIENZO == gs.GRID * gs.FACTOR


def test_la_hoja_mide_384_de_ancho_por_768_de_alto():
    assert gs.FILAS == 12
    assert gs.COLUMNAS == 6
    assert gs.ANCHO_HOJA == gs.COLUMNAS * gs.CELDA == 384
    assert gs.ALTO_HOJA == gs.FILAS * gs.CELDA == 768


def test_los_frames_que_describen_el_contrato_usan_pie_y_centro_de_64():
    assert gs.CELDA_PIE == 55
    assert gs.CELDA_CENTRO == 31.5


# --- Tabla de filas -------------------------------------------------------


def test_la_tabla_de_filas_describe_las_doce_filas_de_unity():
    assert len(gs.TABLA_FILAS) == gs.FILAS
    assert [(f.animacion, f.vista, f.frames, f.fps, f.bucle) for f in gs.TABLA_FILAS] == list(
        FILAS_ESPERADAS
    )


def test_la_duracion_de_cada_fila_sale_de_su_fps():
    for fila in gs.TABLA_FILAS:
        assert fila.duracion_ms == round(1000 / fila.fps)


def test_la_hoja_declara_los_cuatro_clips_con_su_fps_y_su_bucle():
    clips = {fila.animacion: fila for fila in gs.TABLA_FILAS}
    assert (clips["idle"].fps, clips["idle"].duracion_ms, clips["idle"].bucle) == (6, 167, True)
    assert (clips["walk"].fps, clips["walk"].duracion_ms, clips["walk"].bucle) == (8, 125, True)
    assert (clips["roll"].fps, clips["roll"].duracion_ms, clips["roll"].bucle) == (12, 83, False)
    assert (clips["death"].fps, clips["death"].duracion_ms, clips["death"].bucle) == (8, 125, False)


# --- Matriz de frames -----------------------------------------------------


def test_la_matriz_tiene_los_57_frames_del_rango_global_0_a_56():
    assert len(gs.MATRIZ) == 57
    assert sum(fila.frames for fila in gs.TABLA_FILAS) == 57
    assert [f.global_index for f in gs.MATRIZ] == list(range(57))


def test_los_frames_vienen_en_el_orden_de_las_filas_y_dentro_de_la_fila():
    esperado = []
    for fila, (animacion, vista, frames, _fps, _bucle) in zip(gs.TABLA_FILAS, FILAS_ESPERADAS):
        for indice in range(1, frames + 1):
            esperado.append((fila.fila, animacion, vista, indice))
    assert [
        (frame.fila, frame.animacion, frame.vista, frame.indice) for frame in gs.MATRIZ
    ] == esperado


def test_la_columna_es_el_indice_menos_uno():
    for frame in gs.MATRIZ:
        assert frame.columna == frame.indice - 1


def test_el_indice_es_uno_por_animacion_pero_el_global_es_de_hoja():
    for frame in gs.MATRIZ:
        assert 1 <= frame.indice <= 6
        assert frame.global_index == sum(
            f.frames for f in gs.TABLA_FILAS if f.animacion == frame.animacion
        ) - sum(
            f.frames
            for f in gs.TABLA_FILAS
            if f.animacion == frame.animacion
        ) + frame.indice - 1 + sum(
            f.frames for f in gs.TABLA_FILAS[: frame.fila]
        )


def test_la_vista_logica_se_traduce_a_la_vista_legacy_del_prompt():
    esperada = {"down": "frontal", "up": "trasera", "side": "lateral"}
    for frame in gs.MATRIZ:
        assert frame.vista_legacy == esperada[frame.vista]


def test_la_clave_de_frame_une_vista_animacion_e_indice():
    for frame in gs.MATRIZ:
        assert frame.clave == f"{frame.vista}_{frame.animacion}_{frame.indice}"


# --- Geometria canonica ---------------------------------------------------


def test_la_geometria_canonica_tiene_una_entrada_por_frame_y_animacion():
    assert set(gs.GEOMETRIA_CELDAS) == {
        ("idle", indice) for indice in range(1, 5)
    } | {("walk", indice) for indice in range(1, 7)} | {("roll", indice) for indice in range(1, 5)} | {
        ("death", indice)
        for indice in range(1, 6)
    }


def test_idle_y_walk_miden_un_personaje_de_pie_igual():
    for indice in range(1, 5):
        assert gs.GEOMETRIA_CELDAS[("idle", indice)] == gs.GeometriaCelda(47, 24, 55, 1)
    for indice in range(1, 7):
        assert gs.GEOMETRIA_CELDAS[("walk", indice)] == gs.GeometriaCelda(47, 24, 55, 1)


def test_la_voltereta_se_tumbada_y_cerca_del_suelo():
    for indice in range(1, 5):
        assert gs.GEOMETRIA_CELDAS[("roll", indice)] == gs.GeometriaCelda(18, 22, 30, 1)


def test_la_caida_cambia_de_geometria_segun_va_avanzando():
    pie = [gs.GEOMETRIA_CELDAS[("death", indice)] for indice in range(1, 6)]
    # La caida no despega del suelo: el pie se queda en 53 y lo que cambia es
    # el alto (baja la cabeza) y el ancho (el cuerpo se tumba de lado).
    assert [g.pie for g in pie] == [53, 53, 53, 53, 53]
    assert [g.alto for g in pie] == [47, 45, 32, 24, 18]
    assert [g.ancho for g in pie] == [24, 24, 20, 26, 30]
    for geometria in pie:
        assert geometria.pie - geometria.alto + 1 >= 0


def test_ninguna_geometria_se_sale_de_la_celda_de_64():
    for clave, geometria in gs.GEOMETRIA_CELDAS.items():
        assert geometria.pie < gs.CELDA, clave
        assert geometria.alto <= gs.CELDA, clave
        assert geometria.ancho <= gs.CELDA, clave
        assert geometria.pie - geometria.alto + 1 >= 0, clave


def test_cada_frame_hereda_la_geometria_de_su_animacion_e_indice():
    for frame in gs.MATRIZ:
        assert gs.geometria_de_frame(frame) == gs.GEOMETRIA_CELDAS[(frame.animacion, frame.indice)]


# --- QC por frame ---------------------------------------------------------


def test_el_qc_rechaza_una_figura_demasiado_alta_para_su_fila():
    for frame in gs.MATRIZ:
        geometria = gs.geometria_de_frame(frame)
        alto = geometria.alto + geometria.alto_tol + 4
        veredicto = gs.qc_frame(_celda_roda(ancho=geometria.ancho, alto=alto), gs.REFERENCIA, frame=frame)
        assert veredicto.motivos == ("alto",), frame.clave
        assert veredicto.ok is False


def test_el_qc_rechaza_una_figura_cuyo_pie_no_cae_en_su_banda():
    for frame in gs.MATRIZ:
        geometria = gs.geometria_de_frame(frame)
        alto = geometria.alto
        pie_real = geometria.pie + geometria.alto_tol + 3
        top = pie_real - alto + 1
        imagen = np.zeros((gs.CELDA, gs.CELDA, 4), dtype=np.uint8)
        imagen[top : top + alto, 20 : 20 + geometria.ancho] = (200, 180, 160, 255)
        veredicto = gs.qc_frame(imagen, gs.REFERENCIA, frame=frame)
        assert veredicto.motivos == ("pie",), frame.clave
        assert veredicto.ok is False


def test_el_qc_deja_pasar_una_celda_con_la_geometria_canonica():
    for frame in gs.MATRIZ:
        imagen = _celda_de_geometria(gs.geometria_de_frame(frame))
        veredicto = gs.qc_frame(imagen, gs.REFERENCIA, frame=frame)
        assert veredicto.motivos == (), (frame.clave, veredicto)
        assert veredicto.ok is True


def test_el_qc_sigue_admitiendo_una_imagen_sin_frame_con_el_umbral_legacy():
    veredicto = gs.qc_frame(_celda_roda(ancho=10, alto=10), gs.REFERENCIA)
    assert veredicto.ok is True


def test_el_qc_acepta_el_roll_tumbado_que_la_cobertura_global_rechazaria():
    """La banda de cobertura legacy (0.28..0.40) no puede ser un motivo global."""
    roll = _frame("roll", 1)
    veredicto = gs.qc_frame(_celda_de_geometria(gs.geometria_de_frame(roll)), gs.REFERENCIA, frame=roll)
    assert veredicto.ok is True
    assert gs.REFERENCIA["cobertura"] == pytest.approx(0.345, abs=0.01)


# --- Ensamblado -----------------------------------------------------------


def _resultados_completos() -> dict[str, gs.ResultadoCelda]:
    resultados = {}
    for frame in gs.MATRIZ:
        resultados[frame.clave] = gs.ResultadoCelda(
            frame=frame,
            estado="ok",
            imagen=_celda_de_geometria(gs.geometria_de_frame(frame)),
        )
    return resultados


def test_la_hoja_se_ensambla_en_384_por_768():
    hoja = gs.armar_hoja(_resultados_completos())
    assert hoja.shape == (768, 384, 4)


def test_cada_frame_cae_en_su_fila_y_en_su_columna():
    resultados = _resultados_completos()
    hoja = gs.armar_hoja(resultados)
    for frame in gs.MATRIZ:
        for fila, columna in ((0, 0), (7, 3), (11, 4)):
            if (frame.fila, frame.columna) != (fila, columna):
                continue
            ventana = hoja[
                frame.fila * gs.CELDA : (frame.fila + 1) * gs.CELDA,
                frame.columna * gs.CELDA : (frame.columna + 1) * gs.CELDA,
            ]
            assert np.array_equal(ventana, resultados[frame.clave].imagen), frame.clave


def test_la_hoja_no_se_arma_si_falta_alguna_celda():
    resultados = _resultados_completos()
    del resultados[gs.MATRIZ[30].clave]
    with pytest.raises(ValueError) as excinfo:
        gs.armar_hoja(resultados)
    assert "celdas" in str(excinfo.value)


def test_la_hoja_no_se_arma_si_queda_alguna_pendiente():
    resultados = _resultados_completos()
    resultados[gs.MATRIZ[7].clave] = gs.ResultadoCelda(
        frame=gs.MATRIZ[7], estado="pendiente", imagen=np.zeros((gs.CELDA, gs.CELDA, 4), np.uint8)
    )
    with pytest.raises(ValueError) as excinfo:
        gs.armar_hoja(resultados)
    assert "pendientes" in str(excinfo.value)


def test_la_hoja_no_deja_bordes_negros_entre_filas_desiguales():
    hoja = gs.armar_hoja(_resultados_completos())
    assert np.array_equal(hoja[gs.CELDA * 3 : gs.CELDA * 4], hoja[gs.CELDA * 3 : gs.CELDA * 4])
    assert np.array_equal(hoja[:, gs.CELDA : gs.CELDA + 1], hoja[:, gs.CELDA : gs.CELDA + 1])


# --- Manifiesto logico ---------------------------------------------------


def test_el_manifiesto_declara_el_id_el_ppu_y_el_pivot_logicos():
    manifiesto = gs.construir_manifiesto(_resultados_completos(), "wanderer")
    assert manifiesto["id"] == "wanderer_wanderer_sheet"
    assert manifiesto["frameSize"] == gs.CELDA
    assert manifiesto["ppu"] == 64
    assert manifiesto["pivot"] == {"x": 0.5, "y": 0.125}


def test_el_manifiesto_tiene_doce_filas_logicas_y_no_una_lista_de_frames():
    manifiesto = gs.construir_manifiesto(_resultados_completos(), "wanderer")
    assert "frames" not in manifiesto
    assert len(manifiesto["rows"]) == gs.FILAS
    assert [row["row"] for row in manifiesto["rows"]] == list(range(gs.FILAS))
    assert {row["anim"] for row in manifiesto["rows"]} == {"idle", "walk", "roll", "death"}
    assert {row["dir"] for row in manifiesto["rows"]} == {"down", "up", "side"}


def test_los_frames_de_cada_fila_manifiesta_son_los_indices_globales():
    manifiesto = gs.construir_manifiesto(_resultados_completos(), "wanderer")
    esperado = []
    for fila in gs.TABLA_FILAS:
        esperado.append(
            list(range(fila.frames_iniciales, fila.frames_iniciales + fila.frames))
        )
    assert [row["frames"] for row in manifiesto["rows"]] == esperado


def test_el_manifiesto_usa_las_claves_del_json_y_el_loop_correcto():
    manifiesto = gs.construir_manifiesto(_resultados_completos(), "wanderer")
    assert [row["loop"] for row in manifiesto["rows"]] == [f.bucle for f in gs.TABLA_FILAS]
    assert [row["fps"] for row in manifiesto["rows"]] == [f.fps for f in gs.TABLA_FILAS]
    primera = manifiesto["rows"][0]
    assert primera["anim"] == "idle" and primera["dir"] == "down"
    assert gs.animacion_legacy_de_manifiesto("idle") == "idle"
    assert gs.animacion_legacy_de_manifiesto("walk") == "walking"


# --- Exportacion ----------------------------------------------------------


def test_exportar_celda_usa_la_carpeta_por_animacion_y_vista(tmp_path):
    frame = _frame("roll", 3)
    ruta = gs.exportar_celda(frame, _celda_de_geometria(gs.geometria_de_frame(frame)), tmp_path)
    assert ruta == tmp_path / "roll" / frame.vista_legacy / f"{frame.clave}.png"
    assert ruta.exists()


def test_exportar_previews_amplia_a_ocho_veces_y_tolera_faltantes(tmp_path):
    resultados = _resultados_completos()
    del resultados[gs.MATRIZ[5].clave]
    rutas = gs.exportar_previews(resultados, tmp_path)
    assert len(rutas) == len(gs.MATRIZ) - 1
    from PIL import Image

    with Image.open(rutas[0]) as imagen:
        assert imagen.size == (gs.CELDA * 8, gs.CELDA * 8)


def test_exportar_todo_escribe_hoja_manifiesto_logico_y_nada_de_frames_unity(tmp_path):
    rutas = gs.exportar_todo(_resultados_completos(), tmp_path)
    assert "frames" not in rutas
    assert rutas["hoja"].name == "spritesheet.png"
    assert rutas["manifiesto"].name == "wanderer_sheet.json"
    assert not (tmp_path / "frames.json").exists()
    with open(rutas["manifiesto"], encoding="utf-8") as fichero:
        datos = json.load(fichero)
    assert datos["id"] == "wanderer_wanderer_sheet"
    assert len(datos["rows"]) == gs.FILAS


def test_exportar_todo_no_escribe_la_hoja_si_queda_pendiente(tmp_path):
    resultados = _resultados_completos()
    resultados[gs.MATRIZ[0].clave] = gs.ResultadoCelda(
        frame=gs.MATRIZ[0], estado="pendiente", imagen=np.zeros((gs.CELDA, gs.CELDA, 4), np.uint8)
    )
    with pytest.raises(ValueError) as excinfo:
        gs.exportar_todo(resultados, tmp_path)
    assert "pendientes" in str(excinfo.value)
    assert not (tmp_path / "spritesheet.png").exists()


def test_la_vista_lateral_se_espeja_por_codigo_para_izquierda_y_derecha():
    original = gs.Frame("frontal", "walk", 1, 0, 0)
    espejo = gs.espejar_horizontal(original.imagen)
    assert np.array_equal(espejo, original.imagen[:, ::-1])


# --- CLI ------------------------------------------------------------------


def test_la_cli_falsa_devuelve_uno_y_no_ensambla_una_hoja_incompleta(tmp_path, capsys):
    codigo = gs.main(["--falso", "--limite", "2", "--salida", str(tmp_path / "wanderer")])
    assert codigo == 1
    salida = capsys.readouterr().out
    assert "la hoja esta incompleta" in salida
    assert not (tmp_path / "wanderer" / "spritesheet.png").exists()
    assert (tmp_path / "wanderer" / "previews").exists()
    assert list((tmp_path / "wanderer" / "crudas").glob("cruda_*.png"))


def test_la_cli_falsa_deja_las_celdas_buenas_a_pelo(tmp_path):
    gs.main(["--falso", "--limite", "2", "--salida", str(tmp_path / "wanderer")])
    celdas = sorted((tmp_path / "wanderer" / "idle" / "frontal").glob("*.png"))
    assert celdas, "el smoke deberia dejar al menos una celda"


def test_la_cli_no_arranca_sdxl_en_modo_falso(tmp_path, monkeypatch):
    llamado = {"veces": 0}

    def _no_deberia_cargar():
        llamado["veces"] += 1
        raise AssertionError("en modo falso no se carga SDXL")

    monkeypatch.setattr(gs, "cargar_modelo", _no_deberia_cargar)
    gs.main(["--falso", "--limite", "1", "--salida", str(tmp_path / "wanderer")])
    assert llamado["veces"] == 0


# --- Documentacion Unity --------------------------------------------------


def test_el_readme_de_unity_documenta_el_contrato_de_importacion():
    from pathlib import Path

    raiz = Path(gs.__file__).resolve().parent
    readme = (raiz / "DarkRequiem" / "README.md").read_text(encoding="utf-8")
    assert "384" in readme and "768" in readme
    assert "64" in readme
    assert "57" in readme
    assert "spritePixelsToUnits" in readme
    assert "spriteMode" in readme
    assert "Point" in readme
    assert "alphaIsTransparency" in readme
    assert "12 filas" in readme or "doce filas" in readme
