"""Tests del entorno sandbox y de la memoria persistente (JSON)."""
import json
import os

import pytest


class TestEnvSandbox:
    def test_entorno_reducido_incluye_claves_minimas(self, gdt):
        env = gdt._env_sandbox()
        assert "PATH" in env
        assert "SYSTEMROOT" in env
        assert env["PYTHONIOENCODING"] == "utf-8"

    def test_no_hereda_todas_las_variables_del_sistema(self, gdt):
        env = gdt._env_sandbox()
        # El sandbox no debe filtrar por defecto credenciales ni variables de usuario
        for sensible in ("AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "GOOGLE_APPLICATION_CREDENTIALS"):
            assert sensible not in env

    def test_mantiene_temp_y_perfil_en_windows(self, gdt):
        if os.name != "nt":
            pytest.skip("Solo relevante en Windows")
        env = gdt._env_sandbox()
        # En Windows el entorno incluye TEMP/TMP/USERPROFILE para estabilidad
        assert "TEMP" in env or "TMP" in env
        assert "USERPROFILE" in env


class TestMemoria:
    def test_cargar_sin_archivo_devuelve_vacio(self, gdt, memoria_temporal):
        assert gdt.cargar_memoria() == []

    def test_guardar_y_recargar_incluye_campos(self, gdt, memoria_temporal):
        gdt.guardar_memoria(
            prompt="crea una calculadora",
            plan="plan",
            codigo="print('hola')",
            error="",
            solucion="",
            exito=True,
        )
        memoria = gdt.cargar_memoria()
        assert len(memoria) == 1
        assert memoria[0]["prompt"] == "crea una calculadora"
        assert memoria[0]["exito"] is True
        assert memoria[0]["timestamp"] > 0

    def test_guarda_hasta_50_entradas(self, gdt, memoria_temporal):
        for i in range(60):
            gdt.guardar_memoria(f"prompt {i}", "plan", "codigo", "", "", True)
        memoria = gdt.cargar_memoria()
        assert len(memoria) == 50
        # Conserva las más recientes
        assert memoria[0]["prompt"] == "prompt 10"
        assert memoria[-1]["prompt"] == "prompt 59"

    def test_archivo_es_json_valido(self, gdt, memoria_temporal):
        gdt.guardar_memoria("p", "pl", "c", "e", "s", False)
        with open(memoria_temporal, "r", encoding="utf-8") as f:
            datos = json.load(f)
        assert isinstance(datos, list)
        assert datos[0]["exito"] is False

    def test_cargar_json_corrupto_devuelve_vacio(self, gdt, memoria_temporal):
        memoria_temporal.write_text("{ no es json", encoding="utf-8")
        assert gdt.cargar_memoria() == []