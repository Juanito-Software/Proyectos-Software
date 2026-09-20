"""Tests de las heurísticas AST: sintaxis, bucles infinitos, atributos fantasma,
extracción de API y validación de tests contra la API."""
import pytest


class TestValidarSintaxis:
    def test_codigo_valido(self, gdt):
        valido, error = gdt.validar_sintaxis_ast("def foo():\n    return 1")
        assert valido is True
        assert error == ""

    def test_codigo_invalido(self, gdt):
        valido, error = gdt.validar_sintaxis_ast("def foo(:\n    return 1")
        assert valido is False
        assert "Error de sintaxis" in error


class TestDetectarBucles:
    def test_detecta_while_true(self, gdt):
        advertencias = gdt.detectar_bucles_infinitos_ast(
            "while True:\n    x = 1"
        )
        assert len(advertencias) == 1
        assert "while True" in advertencias[0]

    def test_detecta_while_1(self, gdt):
        advertencias = gdt.detectar_bucles_infinitos_ast(
            "i = 0\nwhile 1:\n    i += 1"
        )
        assert len(advertencias) == 1

    def test_no_detecta_bucle_condicional(self, gdt):
        advertencias = gdt.detectar_bucles_infinitos_ast(
            "while x < 10:\n    x += 1"
        )
        assert advertencias == []

    def test_no_detecta_for(self, gdt):
        advertencias = gdt.detectar_bucles_infinitos_ast(
            "for i in range(10):\n    pass"
        )
        assert advertencias == []


class TestDetectarAtributos:
    def test_detecta_atributo_fantasma_por_traduccion(self, gdt):
        codigo = (
            "class Tamagotchi:\n"
            "    def __init__(self):\n"
            "        self.hambre = 10\n"
            "    def jugar(self):\n"
            "        return self.hunger\n"
        )
        advertencias = gdt.detectar_atributos_no_definidos(codigo)
        assert any("self.hunger" in a for a in advertencias)

    def test_no_reporta_atributos_asignados_en_init(self, gdt):
        codigo = (
            "class Perro:\n"
            "    def __init__(self, nombre):\n"
            "        self.nombre = nombre\n"
            "        self.edad = 0\n"
            "    def cumplir_anos(self):\n"
            "        self.edad += 1\n"
            "        return self.edad\n"
        )
        assert gdt.detectar_atributos_no_definidos(codigo) == []

    def test_no_reporta_metodos_de_clase(self, gdt):
        codigo = (
            "class Gato:\n"
            "    def __init__(self):\n"
            "        self.color = 'negro'\n"
            "    def maullar(self):\n"
            "        return self.maullar()\n"
        )
        assert gdt.detectar_atributos_no_definidos(codigo) == []

    def test_codigo_invalido_devuelve_vacio_sin_crash(self, gdt):
        assert gdt.detectar_atributos_no_definidos("def foo(:") == []


class TestExtraerApiEstatica:
    def test_extrae_funciones_y_clases(self, gdt):
        codigo = (
            "def sumar(a, b):\n"
            "    return a + b\n\n"
            "class Cuenta:\n"
            "    def __init__(self, titular):\n"
            "        self.titular = titular\n"
            "        self.saldo = 0\n"
            "    def ingresar(self, cantidad):\n"
            "        self.saldo += cantidad\n"
            "    def retirar(self, cantidad):\n"
            "        pass\n"
        )
        api = gdt.extraer_api_estatica(codigo)
        assert api["functions"] == ["sumar"]
        assert "Cuenta" in api["classes"]
        info = api["classes"]["Cuenta"]
        assert info["init_args"] == ["titular"]
        assert info["methods"] == ["ingresar", "retirar"]
        assert sorted(info["attributes"]) == ["saldo", "titular"]

    def test_clase_sin__init__tiene_listas_vacias(self, gdt):
        codigo = "class Vacia:\n    def metodo(self):\n        pass"
        api = gdt.extraer_api_estatica(codigo)
        info = api["classes"]["Vacia"]
        assert info["init_args"] == []
        assert info["methods"] == ["metodo"]
        assert info["attributes"] == []

    def test_codigo_invalido_devuelve_api_vacia(self, gdt):
        assert gdt.extraer_api_estatica("def foo(:") == {"classes": {}, "functions": []}


class TestValidarTestsVsApi:
    API = {
        "classes": {
            "Cuenta": {
                "init_args": ["titular"],
                "methods": ["ingresar", "retirar"],
                "attributes": ["saldo"],
            }
        },
        "functions": ["sumar"],
    }

    def test_tests_validos_no_devuelven_errores(self, gdt):
        codigo = (
            "obj = mod.Cuenta('Ana')\n"
            "obj.ingresar(100)\n"
            "assert obj.saldo == 100\n"
            "assert mod.sumar(1, 2) == 3\n"
        )
        assert gdt.validar_tests_vs_api(codigo, self.API) == []

    def test_metodo_inventado_se_rechaza(self, gdt):
        codigo = "obj = mod.Cuenta('Ana')\nobj.retirar_todo()"
        errores = gdt.validar_tests_vs_api(codigo, self.API)
        assert any("retirar_todo" in e for e in errores)

    def test_clase_inventada_se_rechaza(self, gdt):
        codigo = "obj = mod.Mascota()"
        errores = gdt.validar_tests_vs_api(codigo, self.API)
        assert any("Mascota" in e for e in errores)

    def test_funcion_inventada_se_rechaza(self, gdt):
        codigo = "mod.multiplicar(2, 3)"
        errores = gdt.validar_tests_vs_api(codigo, self.API)
        assert any("multiplicar" in e for e in errores)

    def test_import_prohibido_se_rechaza(self, gdt):
        errores = gdt.validar_tests_vs_api("import threading", self.API)
        assert any("prohibida" in e.lower() for e in errores)

    def test_sleep_prohibido(self, gdt):
        errores = gdt.validar_tests_vs_api("import time\ntime.sleep(1)", self.API)
        assert any("sleep" in e for e in errores)

    def test_sintaxis_invalida_lanza_testsyntaxerror(self, gdt):
        with pytest.raises(gdt.TestSyntaxError):
            gdt.validar_tests_vs_api("def foo(:", self.API)

    def test_alias_de_clase_resuelve_acceso(self, gdt):
        codigo = (
            "Alias = mod.Cuenta\n"
            "obj = Alias('Ana')\n"
            "obj.ingresar(1)\n"
        )
        assert gdt.validar_tests_vs_api(codigo, self.API) == []

    def test_autotest_del_validador_pasa(self, gdt):
        # Reproduce el self-test embebido en el propio script
        gdt.verificar_validador_ast()

    def test_autotest_detecta_atributo_inventado_en_sut(self, gdt):
        codigo = "obj = mod.Cuenta('Ana')\nassert obj.campo_inventado"
        errores = gdt.validar_tests_vs_api(codigo, self.API)
        assert any("campo_inventado" in e for e in errores)


class TestGenerarAssertsEstaticos:
    def test_genera_hasattr_para_cada_simbolo(self, gdt):
        api = {
            "functions": ["sumar"],
            "classes": {
                "Cuenta": {"init_args": [], "methods": ["ingresar"],
                           "attributes": []}
            },
        }
        asserts = gdt.generar_asserts_estaticos(api)
        assert "assert hasattr(mod, 'sumar')" in asserts
        assert "assert hasattr(mod, 'Cuenta')" in asserts
        assert "'ingresar'" in asserts

    def test_no_genera_nada_sin_api(self, gdt):
        assert gdt.generar_asserts_estaticos({"classes": {}, "functions": []}) == (
            "# --- VALIDACIÓN ESTÁTICA AUTOMÁTICA DE LA API ---"
        )