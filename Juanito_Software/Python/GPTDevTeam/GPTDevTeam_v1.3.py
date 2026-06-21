# Copyright (C) 2025 JuanitoSoftware
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.

# GPTDevTeam
import sys
import ast
import subprocess
import threading
import requests
import os
import time
import re
import textwrap
import tempfile
import shutil
import json

# Configurar codificación UTF-8 para evitar errores con emojis en consolas de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

TIMEOUT_EJECUCION = 30
TIMEOUT_ARRANQUE = 10
SCORE_MINIMO_EXITO = 8          # umbral de score para considerar OK una ejecución individual
UMBRAL_APROBACION_GLOBAL = 7    # umbral de score para aprobar el resultado final (exec/semántico)
MEMORY_FILE = "memory.json"

MODEL_ROLES = {
    "planner": "qwen3:8b",
    "coder": "qwen2.5-coder:7b",
    "tester": "qwen2.5-coder:7b",
    "judge": "qwen3:8b",
    "reflector": "qwen3:8b",
    "documenter": "qwen3:8b",
}


def extraer_codigo_puro(texto):
    """
    Extrae bloques de código Python de una respuesta tipo LLM.
    Soporta delimitadores Markdown (```python) y sin ellos.
    Además, limpia comillas triples mal colocadas e indentaciones accidentales.
    """
    bloques = re.findall(r"```python(.*?)```", texto, re.DOTALL)
    if bloques:
        codigo = bloques[0].strip()
    else:
        # si no hay delimitadores, intenta con heurística básica
        lineas = texto.splitlines()
        lineas = [l for l in lineas if not l.strip().startswith("#") and not l.strip().startswith("Instrucción")]
        codigo = "\n".join(lineas)

    # Elimina comillas triples que suelen confundirse con markdown
    codigo = re.sub(r'^\s*"""', '', codigo)
    codigo = re.sub(r'"""$', '', codigo)
    # Desindenta en caso de que todo el bloque esté indentado por error
    return textwrap.dedent(codigo).strip()


def validar_sintaxis_ast(codigo: str) -> tuple[bool, str]:
    try:
        ast.parse(codigo)
        return True, ""
    except SyntaxError as e:
        return False, f"Error de sintaxis (AST): {e}"


def evaluar_salida(stdout: str, stderr: str, exit_code: int | None, validar_output=None) -> int:
    score = 0
    if exit_code == 0:
        score += 5
    if len(stderr.strip()) == 0:
        score += 3
    if len(stdout.strip()) > 0:
        score += 2
    if validar_output is not None:
        cumple = (
            validar_output(stdout)
            if callable(validar_output)
            else validar_output in stdout
        )
        score += 2 if cumple else -3
    if "AssertionError" in stderr:
        score -= 5
    if "Traceback" in stderr:
        score -= 3
    return max(0, min(score, 10))


def _env_sandbox() -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "PYTHONIOENCODING": "utf-8",
    }
    if os.name == "nt":
        env["COMSPEC"] = os.environ.get("COMSPEC", "")
    return env


def ejecutar_codigo_py(
    path: str,
    timeout: int = TIMEOUT_EJECUCION,
    startup_timeout: int = TIMEOUT_ARRANQUE,
    validar_output=None,
) -> dict:
    """
    Ejecuta un script Python en una carpeta temporal aislada (sandbox) y
    devuelve un diagnóstico de la ejecución: exit_code, score, stdout, stderr,
    si fue un "éxito" (exit 0 + score suficiente) y el motivo si terminó por
    timeout o arranque interactivo.
    """
    temp_dir = tempfile.mkdtemp(prefix="gptdevteam_")
    proceso = None

    try:
        script_name = os.path.basename(path)
        shutil.copy2(path, os.path.join(temp_dir, script_name))

        # Copiar también CodigoActual.py si existe para que los tests puedan importarlo
        if os.path.exists("CodigoActual.py") and script_name != "CodigoActual.py":
            shutil.copy2("CodigoActual.py", os.path.join(temp_dir, "CodigoActual.py"))

        proceso = subprocess.Popen(
            ["python", "-u", script_name],
            cwd=temp_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=_env_sandbox(),
        )

        if proceso.stdin:
            try:
                proceso.stdin.write("salir\nexit\nquit\n5\n")
                proceso.stdin.flush()
            except Exception:
                pass

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        lock = threading.Lock()

        def leer_stream(stream, destino: list[str]):
            for line in stream:
                with lock:
                    destino.append(line)

        hilo_stdout = threading.Thread(target=leer_stream, args=(proceso.stdout, stdout_lines), daemon=True)
        hilo_stderr = threading.Thread(target=leer_stream, args=(proceso.stderr, stderr_lines), daemon=True)
        hilo_stdout.start()
        hilo_stderr.start()

        inicio = time.time()
        exit_code = None
        motivo = ""

        while True:
            elapsed = time.time() - inicio
            exit_code = proceso.poll()

            with lock:
                stdout_parcial = "".join(stdout_lines)

            if exit_code is not None:
                break

            if elapsed >= startup_timeout and stdout_parcial.count("\n") > 0:
                proceso.terminate()
                try:
                    proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proceso.kill()
                exit_code = 0
                motivo = "Arranque interactivo validado (sin errores en stderr)."
                break

            if elapsed >= timeout:
                proceso.kill()
                exit_code = -1
                motivo = f"Timeout: ejecución superó {timeout} segundos."
                break

            time.sleep(0.2)

        hilo_stdout.join(timeout=2)
        hilo_stderr.join(timeout=2)

        if proceso.poll() is not None:
            try:
                rest_out, rest_err = proceso.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                rest_out, rest_err = "", ""
            stdout = "".join(stdout_lines) + (rest_out or "")
            stderr = "".join(stderr_lines) + (rest_err or "")
        else:
            stdout = "".join(stdout_lines)
            stderr = "".join(stderr_lines)

        if motivo and not stderr.strip():
            stderr = motivo

        score = evaluar_salida(stdout, stderr if exit_code != 0 else "", exit_code, validar_output)
        exito = (exit_code == 0) and (score >= SCORE_MINIMO_EXITO)

        return {
            "exito": exito,
            "exit_code": exit_code,
            "score": score,
            "stdout": stdout,
            "stderr": stderr,
            "motivo": motivo,
        }

    except Exception as e:
        return {
            "exito": False,
            "exit_code": -1,
            "score": 0,
            "stdout": "",
            "stderr": f"Error durante ejecución: {e}",
            "motivo": str(e),
        }

    finally:
        if proceso and proceso.poll() is None:
            proceso.kill()
        shutil.rmtree(temp_dir, ignore_errors=True)


def formatear_informe_ejecucion(resultado: dict) -> str:
    return (
        f"Exit code: {resultado['exit_code']}\n"
        f"Score: {resultado['score']}/{SCORE_MINIMO_EXITO} mínimo\n"
        f"Éxito: {resultado['exito']}\n"
        f"Motivo: {resultado.get('motivo') or 'N/A'}\n"
        f"stdout:\n{resultado['stdout'] or '(vacío)'}\n"
        f"stderr:\n{resultado['stderr'] or '(vacío)'}"
    )


def ollama_generate(model: str, prompt: str):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=600
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        print("❌ Error al llamar a Ollama:", e)
        return ""


def documentar_codigo(codigo: str):
    model = MODEL_ROLES["documenter"]
    prompt = (
        "Añade comentarios para el siguiente código Python:\n"
        "IMPORTANTE: Utiliza siempre # para los comentarios, no agregues explicaciones fuera de él.\n"
        f"Codigo a documentar:\n{codigo.strip()}"
    )
    return ollama_generate(model, prompt)


def limpiar_docstring_inicial(codigo: str) -> str:
    codigo = codigo.lstrip()
    lineas = codigo.splitlines()
    triple_quotes = ('"""', "'''")

    apertura_idx = None

    for i, linea in enumerate(lineas[:50]):
        contenido = linea.strip()

        if any(contenido.startswith(q) for q in triple_quotes):
            if apertura_idx is None:
                apertura_idx = i
                if any(contenido.endswith(q) for q in triple_quotes) and len(contenido) > 6:
                    # Caso docstring de una línea tipo """texto"""
                    return '\n'.join(lineas[i + 1:]).lstrip()
        elif any(q in contenido for q in triple_quotes):
            if apertura_idx is None:
                cierre_idx = i
                # Encapsular ese texto anterior como un bloque válido
                bloque_doc = '\n'.join(lineas[:cierre_idx + 1])
                resto = '\n'.join(lineas[cierre_idx + 1:])
                return f'"""\n{bloque_doc}\n"""\n{resto.lstrip()}'

        # Si encontramos una línea válida de código, detenemos la búsqueda
        if contenido.startswith(("import", "from", "def ", "class ")):
            break

    # Si detectamos una apertura sin cierre
    if apertura_idx is not None:
        return '\n'.join(lineas[apertura_idx + 1:]).lstrip()

    return codigo


def planificar_diseño(prompt: str) -> str:
    model = MODEL_ROLES["planner"]
    prompt_planner = (
        "Actúa como un Arquitecto de Software experto.\n"
        "Diseña un plan de implementación detallado, estructurado y paso a paso en español "
        f"para el siguiente requerimiento del usuario:\n\n"
        f"Requerimiento: \"{prompt}\"\n\n"
        "Tu plan debe incluir:\n"
        "1. Clases, atributos y métodos necesarios (ej. clase Tamagotchi con hambre, energia, felicidad, etc.).\n"
        "2. Estructura de control y flujo de interacción por comandos.\n"
        "3. Casos borde y validaciones de datos.\n"
        "IMPORTANTE: No generes código Python todavía. Genera únicamente el plan textual estructurado."
    )
    print("📋 [Planner] Generando plan de diseño...")
    return ollama_generate(model, prompt_planner)


def generar_codigo_de_plan(prompt: str, plan: str) -> str:
    model = MODEL_ROLES["coder"]
    prompt_coder = (
        "Actúa como un Programador Senior de Python.\n"
        "Escribe un script de Python completo, limpio, auto-contenido y funcional que implemente el siguiente requerimiento "
        "siguiendo rigurosamente el plan de diseño proporcionado.\n\n"
        f"Requerimiento del usuario: \"{prompt}\"\n\n"
        f"Plan de Diseño:\n{plan}\n\n"
        "REGLAS CRÍTICAS:\n"
        "- Toda la salida debe ser código Python puro encerrado dentro de bloques de código markdown ```python y ```.\n"
        "- Si la aplicación es interactiva y contiene un bucle principal (como un menú o juego en consola), "
        "debes envolver el bucle principal dentro del bloque 'if __name__ == \"__main__\":'. "
        "Esto permitirá importar el script en los tests unitarios sin iniciar la interfaz interactiva.\n"
        "- No incluyas comentarios explicativos fuera del bloque de código Python.\n"
        "- Asegúrate de que las clases y métodos coincidan exactamente con la estructura planificada."
    )
    print("💻 [Coder] Generando código base a partir del plan...")
    raw_code = ollama_generate(model, prompt_coder)
    return extraer_codigo_puro(raw_code)


def detectar_bucles_infinitos_ast(codigo: str) -> list[str]:
    warnings = []
    try:
        tree = ast.parse(codigo)

        class LoopVisitor(ast.NodeVisitor):
            def visit_While(self, node):
                es_true = (
                    (isinstance(node.test, ast.Constant) and node.test.value in (True, 1))
                    or (isinstance(node.test, ast.Name) and node.test.id == "True")
                )
                if es_true:
                    warnings.append(
                        f"Bucle 'while True' detectado en línea {node.lineno}. "
                        "Revisar mecanismos de salida (break/return/exit)."
                    )
                self.generic_visit(node)

        LoopVisitor().visit(tree)
    except Exception:
        pass
    return warnings


class InitVisitor(ast.NodeVisitor):
    """Recolecta los nombres de los atributos asignados en self.X dentro de __init__."""

    def __init__(self):
        self.attributes = []

    def visit_Assign(self, node):
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Attribute)
            and isinstance(node.targets[0].value, ast.Name)
            and node.targets[0].value.id == "self"
        ):
            attr_name = node.targets[0].attr
            if attr_name not in self.attributes:
                self.attributes.append(attr_name)
        self.generic_visit(node)


def extraer_api_estatica(codigo: str) -> dict:
    """Analiza el código vía AST y devuelve qué funciones/clases/métodos/atributos expone."""
    api = {"classes": {}, "functions": []}
    try:
        tree = ast.parse(codigo)
    except Exception:
        return api

    # Anotar relación padre-hijo para distinguir clases de nivel superior de las anidadas
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            api["functions"].append(node.name)

        elif isinstance(node, ast.ClassDef) and getattr(node, "parent", None) is None:
            clase = {"init_args": [], "methods": [], "attributes": []}

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name == "__init__":
                        clase["init_args"] = [arg.arg for arg in item.args.args if arg.arg != "self"]
                        visitor = InitVisitor()
                        visitor.visit(item)
                        clase["attributes"].extend(visitor.attributes)
                    else:
                        clase["methods"].append(item.name)

            api["classes"][node.name] = clase

    return api


def validar_tests_vs_api(test_code: str, api: dict) -> list[str]:
    try:
        tree = ast.parse(test_code)
    except SyntaxError as e:
        return [f"Error de Sintaxis en Tests (AST): {e}"]

    return TestSemanticValidator(api).validate(tree)


class TestSemanticValidator(ast.NodeVisitor):
    """
    Valida que un test generado por el LLM solo use símbolos (clases, funciones,
    métodos, atributos) realmente presentes en la API estática del código bajo prueba,
    y que no use concurrencia / hacks prohibidos.
    """

    PROHIBIDOS_IMPORT = {"threading", "multiprocessing", "concurrent"}
    PROHIBIDOS_METODOS = {"sleep"}

    def __init__(self, api: dict):
        self.api = api
        self.errors = []

        self._clases_validas = set(api.get("classes", {}).keys())
        self._funciones_validas = set(api.get("functions", []))

        self.class_aliases = {}
        self.sut_vars = {}
        self.object_builtins = set(dir(object))

    def validate(self, tree: ast.AST) -> list[str]:
        self.visit(tree)
        return self.errors

    def resolve_alias(self, name: str) -> str:
        while name in self.class_aliases:
            name = self.class_aliases[name]
        return name

    # Bloque 1: imports prohibidos
    def visit_Import(self, node):
        for alias in node.names:
            base = alias.name.split(".")[0]
            if base in self.PROHIBIDOS_IMPORT:
                self.errors.append(f"Importación prohibida en tests: {alias.name}")

    def visit_ImportFrom(self, node):
        if node.module:
            base = node.module.split(".")[0]
            if base in self.PROHIBIDOS_IMPORT:
                self.errors.append(f"Importación prohibida en tests: {node.module}")

    # Bloque 2: tracking de SUT (system under test) y aliases de clase
    def visit_Assign(self, node):
        # alias de clase: Mascota = mod.Tamagotchi
        if (
            isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "mod"
        ):
            class_name = node.value.attr
            if class_name in self._clases_validas:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        self.class_aliases[t.id] = class_name

        # instanciación del SUT
        elif isinstance(node.value, ast.Call):
            func = node.value.func
            class_name = None

            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "mod":
                class_name = func.attr
            elif isinstance(func, ast.Name):
                resolved = self.resolve_alias(func.id)
                if resolved in self._clases_validas:
                    class_name = resolved

            if class_name:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        self.sut_vars[t.id] = class_name

        self.generic_visit(node)

    # Bloque 3: reglas de atributos sobre mod.X y sobre instancias del SUT
    def visit_Attribute(self, node):
        nombre = node.attr

        if nombre in self.PROHIBIDOS_METODOS:
            self.errors.append(f"Atributo prohibido: {nombre}")

        if isinstance(node.value, ast.Name) and node.value.id == "mod":
            if nombre not in self._clases_validas and nombre not in self._funciones_validas:
                self.errors.append(f"Símbolo no permitido en mod: {nombre}")

        elif isinstance(node.value, ast.Name) and node.value.id in self.sut_vars:
            class_name = self.sut_vars[node.value.id]
            info = self.api.get("classes", {}).get(class_name, {})
            allowed = (
                set(info.get("methods", []))
                | set(info.get("attributes", []))
                | set(info.get("init_args", []))
                | self.object_builtins
            )
            if nombre not in allowed:
                self.errors.append(f"'{nombre}' no existe en SUT '{class_name}'")

        self.generic_visit(node)

    # Bloque 4: llamadas prohibidas (ej. time.sleep)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
            self.errors.append("Uso prohibido: sleep() en tests")
        self.generic_visit(node)


def verificar_validador_ast():
    print("🧪 [Self-Test] Iniciando auto-test del validador AST...")

    api_demo = {
        "classes": {
            "ClaseValida": {
                "init_args": [],
                "methods": ["metodo_valido"],
                "attributes": ["atributo_valido"],
            }
        },
        "functions": ["funcion_valida"],
    }

    casos = {
        "Caso 1 (método válido)": ("obj = mod.ClaseValida()\nobj.metodo_valido()", False),
        "Caso 2 (atributo válido)": ("obj = mod.ClaseValida()\nassert obj.atributo_valido is not None", False),
        "Caso 3 (método inventado)": ("obj = mod.ClaseValida()\nobj.metodo_inventado()", "metodo_inventado"),
        "Caso 4 (atributo inventado)": ("obj = mod.ClaseValida()\nobj.campo_inventado", "campo_inventado"),
        "Caso 5 (función válida)": ("mod.funcion_valida()", False),
        "Caso 6 (función inventada)": ("mod.funcion_magica()", "funcion_magica"),
        "Caso 7 (alias de clase)": ("Alias = mod.ClaseValida\nobj = Alias()\nobj.metodo_valido()", False),
        "Caso 8 (import prohibido)": ("import threading", "Importación prohibida"),
        "Caso 9 (sleep prohibido)": ("import time\ntime.sleep(1)", "sleep"),
        "Caso 10 (tipo builtin)": ("x = []\nx.append(1)", False),
    }

    for nombre, (codigo_test, debe_contener) in casos.items():
        err = validar_tests_vs_api(codigo_test, api_demo)
        if debe_contener is False:
            assert not err, f"{nombre} falló: {err}"
        else:
            assert any(debe_contener in e for e in err), f"{nombre} no detectó el error esperado: {err}"

    print("✅ [Self-Test] Validador AST verificado correctamente.")


def generar_asserts_estaticos(api: dict) -> str:
    lineas = ["# --- VALIDACIÓN ESTÁTICA AUTOMÁTICA DE LA API ---"]

    for func in api.get("functions", []):
        lineas.append(f"assert hasattr(mod, {func!r}), 'La función global {func} no existe en el módulo'")

    for clase_name, clase_info in api.get("classes", {}).items():
        lineas.append(f"assert hasattr(mod, {clase_name!r}), 'La clase {clase_name} no existe en el módulo'")
        for metodo in clase_info.get("methods", []):
            if metodo != "__init__":
                lineas.append(
                    f"assert hasattr(getattr(mod, {clase_name!r}), {metodo!r}), "
                    f"'El método {metodo} no existe en la clase {clase_name}'"
                )

    return "\n".join(lineas)


def _reglas_y_api_para_tests(api: dict) -> tuple[str, str]:
    """Bloques de texto compartidos por la primera generación de tests y su corrección."""
    reglas = (
        "=== REGLAS CRÍTICAS (OBLIGATORIAS) ===\n"
        "1. Los tests deben ser 100% síncronos, deterministas y sin concurrencia.\n"
        "2. Está TERMINANTEMENTE PROHIBIDO el uso de: threading, Thread, time.sleep, sleep, time, "
        "StringIO, redirect_stdout, daemon, simulación de input por stdin o cualquier concurrencia/sincronización artificial.\n"
        "3. Los tests deben tratar el código como una API cerrada.\n"
        "4. Solo se permiten llamadas o accesos a símbolos descritos en la API OFICIAL.\n"
        "5. Cualquier símbolo no listado en la API se considera inexistente.\n"
        "6. No manipules __dict__ ni uses try/except para evadir errores de ejecución.\n"
        "7. No llames a __init__ de forma explícita (ej. t.__init__()); instancia la clase llamándola normalmente.\n\n"
    )
    api_oficial = (
        "=== API OFICIAL (OBLIGATORIA) ===\n"
        "Todo símbolo no listado aquí debe considerarse inexistente. Está prohibido usar clases, "
        "funciones, atributos o métodos fuera de esta API.\n\n"
        f"{json.dumps(api, indent=2, ensure_ascii=False)}\n\n"
    )
    return reglas, api_oficial


def generar_tests(codigo: str, api: dict, test_previo: str | None = None, errores: list[str] | None = None) -> str:
    """
    Genera tests basados en assert a partir de la API estática del código.
    Si se pasan test_previo/errores, en lugar de generar desde cero le pide al
    modelo que corrija el test anterior según los errores de validación AST.
    """
    model = MODEL_ROLES["tester"]
    reglas, api_oficial = _reglas_y_api_para_tests(api)
    codigo_app = f"=== CÓDIGO DE LA APLICACIÓN ===\n```python\n{codigo}\n```\n\n"

    if test_previo is None:
        template_lines = []
        for clase_name, clase_info in api.get("classes", {}).items():
            dummy_args = ", ".join(f'"test_{arg}"' for arg in clase_info.get("init_args", []))
            template_lines.append(f"# Ejemplo de test dinámico para {clase_name}:")
            template_lines.append(f"obj = mod.{clase_name}({dummy_args})")
            for attr in clase_info.get("attributes", []):
                template_lines.append(f"assert hasattr(obj, '{attr}')")
            for metodo in clase_info.get("methods", []):
                if metodo != "__init__":
                    template_lines.append(f"# obj.{metodo}()")
        template_str = "\n".join(template_lines)

        prompt = (
            "Actúa como un Ingeniero de QA experto en Python.\n"
            "Genera tests unitarios de comportamiento usando exclusivamente la palabra clave assert de Python.\n\n"
            f"{reglas}{api_oficial}"
            f"=== PLANTILLA DE REFERENCIA ===\n{template_str}\n\n"
            f"{codigo_app}"
            "Genera assertions reales de comportamiento de Python para validar la lógica. "
            "Devuelve solo el código de test limpio dentro de un bloque ```python."
        )
        print("🧪 [Test Generator] Generando assertions de prueba...")
    else:
        errores_txt = "\n".join(f"- {err}" for err in (errores or []))
        prompt = (
            "Actúa como un Ingeniero de QA experto en Python.\n"
            "El código de test que generaste previamente contiene errores de validación AST o usa "
            "símbolos inexistentes fuera de la API oficial.\n\n"
            f"=== ERRORES DE VALIDACIÓN ===\n{errores_txt}\n\n"
            f"=== CÓDIGO DE TEST ANTERIOR ===\n```python\n{test_previo}\n```\n\n"
            f"{reglas}{api_oficial}{codigo_app}"
            "Corrige el código de test anterior eliminando o corrigiendo las llamadas a símbolos no "
            "permitidos o el uso de concurrencia. Devuelve solo los assertions corregidos dentro de "
            "un bloque ```python."
        )
        print("🧪 [Test Generator] Corrigiendo assertions de prueba por errores AST...")

    raw_tests = ollama_generate(model, prompt)
    return extraer_codigo_puro(raw_tests)


def evaluar_semantica(codigo: str, prompt: str, resultado_tests: str) -> dict:
    model = MODEL_ROLES["judge"]
    prompt_evaluador = (
        "Actúa como un Evaluador y Juez de Código Senior de Python.\n"
        "Analiza si el siguiente código de Python satisface todos los requisitos funcionales del usuario, "
        "considerando también el resultado de los tests.\n\n"
        f"Requerimiento original del usuario: \"{prompt}\"\n\n"
        f"Código generado:\n```python\n{codigo}\n```\n\n"
        f"Resultado de ejecución de tests:\n{resultado_tests}\n\n"
        "Responde OBLIGATORIAMENTE en formato JSON válido con la siguiente estructura exacta. "
        "No agregues explicaciones fuera del JSON:\n"
        "{\n"
        "  \"cumple_requisitos\": true/false,\n"
        "  \"score_semantico\": 1-10,\n"
        "  \"comentarios\": \"Análisis de qué requisitos se cumplen, cuáles no y qué mejorar.\"\n"
        "}"
    )
    print("⚖️ [Semantic Judge] Evaluando cobertura y validez semántica...")
    raw_eval = ollama_generate(model, prompt_evaluador)

    try:
        match = re.search(r"\{.*?\}", raw_eval, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"⚠️ Error parseando la evaluación semántica: {e}. Respuesta cruda: {raw_eval}")

    return {
        "cumple_requisitos": True,
        "score_semantico": 7,
        "comentarios": "No se pudo parsear el resultado del juez semántico.",
    }


def reflexionar_y_corregir(codigo: str, errores: str, prompt: str, historial_errores: list[str] | None = None) -> tuple[str, str]:
    model = MODEL_ROLES["reflector"]
    historial_txt = ""
    if historial_errores:
        previos = "\n---\n".join(historial_errores[-2:])
        historial_txt = f"\n\nHistorial de errores en intentos anteriores:\n{previos}"

    prompt_debug = (
        "Actúa como un Agente de Corrección y Refactorización de Código Python.\n"
        "El código generado ha fallado en las pruebas de ejecución o validación.\n\n"
        f"Requerimiento original del usuario: \"{prompt}\"\n\n"
        f"Código actual:\n```python\n{codigo}\n```\n\n"
        f"Informe de errores y fallos de test:\n{errores}"
        f"{historial_txt}\n\n"
        "INSTRUCCIONES:\n"
        "1. En primer lugar, reflexiona brevemente sobre por qué falló el código (análisis de causa raíz en español).\n"
        "2. En segundo lugar, proporciona el código Python corregido y completo, listo para ejecutar.\n"
        "3. Devuelve toda tu respuesta en el siguiente formato:\n\n"
        "--- REFLEXIÓN ---\n"
        "[Escribe aquí tu análisis y causa raíz del fallo en español]\n"
        "--- CÓDIGO CORREGIDO ---\n"
        "```python\n"
        "[Código corregido aquí]\n"
        "```"
    )
    print("🔄 [Reflection Loop] Solicitando reflexión y corrección...")
    response = ollama_generate(model, prompt_debug)

    if "--- REFLEXIÓN ---" in response and "--- CÓDIGO CORREGIDO ---" in response:
        partes = response.split("--- CÓDIGO CORREGIDO ---")
        reflexion = partes[0].replace("--- REFLEXIÓN ---", "").strip()
        codigo_corregido = extraer_codigo_puro(partes[1])
    else:
        reflexion = "No se pudo extraer la reflexión."
        codigo_corregido = extraer_codigo_puro(response)

    return reflexion, codigo_corregido


def cargar_memoria() -> list[dict]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def guardar_memoria(prompt, plan, codigo, error, solucion, exito):
    mem = cargar_memoria()
    mem.append({
        "timestamp": time.time(),
        "prompt": prompt,
        "plan": plan,
        "codigo": codigo,
        "error": error,
        "solucion": solucion,
        "exito": exito,
    })
    mem = mem[-50:]
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ No se pudo guardar la memoria: {e}")


def main():
    verificar_validador_ast()

    if len(sys.argv) > 1:
        entrada_prompt = " ".join(sys.argv[1:])
    else:
        entrada_prompt = (
            "Recrea las mecánicas básicas del Tamagotchi original. "
            "Que tenga diferentes estados de ánimo (hambre, energia, felicidad, salud). "
            "que puedas recargar su energia y salud alimentandolo y haciendolo dormir/descansar. "
            "que puedas jugar con él para aumentar su felicidad. "
            "que funcione por comandos (comer, dormir, jugar, estado, salir). "
            "Debe usar una clase para representar al Tamagotchi. "
            "Importante mostrar una guía de uso al inicio del programa."
        )

    print("🚀 Iniciando Pipeline Nivel 5 de GPTDevTeam")

    # 1. Planificación
    plan = planificar_diseño(entrada_prompt)
    print("\n--- PLAN DE DISEÑO GENERADO ---")
    print(plan)
    print("--------------------------------\n")

    # 2. Codificación inicial
    CodigoActual = generar_codigo_de_plan(entrada_prompt, plan)
    CodigoActual = limpiar_docstring_inicial(CodigoActual)

    max_intentos = 4
    intentos = 0
    historial_errores = []
    mejor_version = {"codigo": None, "score_global": -1}

    while intentos < max_intentos:
        print(f"\n🔄 --- INTENTO {intentos + 1} DE {max_intentos} ---")

        # Validar sintaxis AST del código base
        valido_ast, error_ast = validar_sintaxis_ast(CodigoActual)
        if not valido_ast:
            print(f"❌ Error de sintaxis detectado (AST):\n{error_ast}")
            reflexion, CodigoActual = reflexionar_y_corregir(CodigoActual, error_ast, entrada_prompt, historial_errores)
            print(f"💡 Reflexión del Agente:\n{reflexion}")
            historial_errores.append(f"Error AST: {error_ast}\nReflexión: {reflexion}")
            intentos += 1
            continue

        with open("CodigoActual.py", "w", encoding="utf-8") as f:
            f.write(CodigoActual)

        # 3. Generar y validar tests unitarios basados en asserts
        api = extraer_api_estatica(CodigoActual)
        print("\n📦 API DETECTADA:\n")
        print(json.dumps(api, indent=2, ensure_ascii=False))

        asserts_estaticos = generar_asserts_estaticos(api)

        asserts = ""
        errores_validacion = []
        for intento_test in range(3):
            asserts = generar_tests(CodigoActual, api, asserts if intento_test else None, errores_validacion)
            errores_validacion = validar_tests_vs_api(asserts, api)
            if not errores_validacion:
                print("✅ Tests validados por AST correctamente.")
                break
            print(f"❌ Tests inválidos detectados por AST: {errores_validacion}")

        test_script = (
            "import sys\n"
            "import os\n"
            "import importlib.util\n\n"
            "# --- CARGA DINÁMICA DEL MÓDULO ---\n"
            "spec = importlib.util.spec_from_file_location('CodigoActual', 'CodigoActual.py')\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n\n"
            "# --- ASSERTS ESTÁTICOS ---\n"
            f"{asserts_estaticos}\n\n"
            "# --- ASSERTS DINÁMICOS ---\n"
            f"{asserts}\n"
        )
        with open("test_actual.py", "w", encoding="utf-8") as f:
            f.write(test_script)

        # 4. Análisis estático de bucles infinitos
        warnings_bucles = detectar_bucles_infinitos_ast(CodigoActual)
        for w in warnings_bucles:
            print(f"⚠️ AST Warning: {w}")

        # 5. Ejecutar tests en sandbox
        print("🧪 Ejecutando assertions de test en sandbox...")
        resultado_tests = ejecutar_codigo_py("test_actual.py")
        informe_tests = formatear_informe_ejecucion(resultado_tests)
        print(f"📊 Test Score: {resultado_tests['score']} | Exit code: {resultado_tests['exit_code']}")

        # 6. Ejecutar programa principal (prueba de humo / arranque interactivo)
        print("🧪 Ejecutando arranque del programa principal en sandbox...")
        resultado_main = ejecutar_codigo_py("CodigoActual.py")
        informe_main = formatear_informe_ejecucion(resultado_main)
        print(f"📊 Main Score: {resultado_main['score']} | Exit code: {resultado_main['exit_code']}")

        # 7. Evaluación semántica (Juez)
        eval_sem = evaluar_semantica(CodigoActual, entrada_prompt, informe_tests)
        sem_score = eval_sem.get("score_semantico", 0)
        print(f"⚖️ Juez Semántico Score: {sem_score}/10 | Cumple requisitos: {eval_sem.get('cumple_requisitos', False)}")
        print(f"💬 Comentarios del Juez: {eval_sem.get('comentarios', '')}")

        # Consolidar resultados
        tests_exito = resultado_tests["exito"]
        main_exito = resultado_main["exito"]
        sem_exito = eval_sem.get("cumple_requisitos", False) and sem_score >= UMBRAL_APROBACION_GLOBAL
        sin_warnings_bucles = len(warnings_bucles) == 0

        score_exec = (resultado_tests["score"] + resultado_main["score"]) / 2
        score_global = (resultado_tests["score"] + resultado_main["score"] + sem_score) / 3

        if score_global > mejor_version["score_global"]:
            mejor_version = {"codigo": CodigoActual, "score_global": score_global}

        exec_exito = score_exec >= UMBRAL_APROBACION_GLOBAL

        if exec_exito and sem_exito and sin_warnings_bucles:
            print("✅ ÉXITO: Código validado completamente.")
            guardar_memoria(entrada_prompt, plan, CodigoActual, "Ninguno", "Código validado con éxito", True)
            break

        # Fallback: construir informe de errores para la siguiente reflexión
        fallos = []
        if not tests_exito:
            fallos.append(f"FALLO DE TESTS:\n{informe_tests}")
        if not main_exito:
            fallos.append(f"FALLO DE MAIN:\n{informe_main}")
        if not sin_warnings_bucles:
            fallos.append("ADVERTENCIAS DE BUCLES:\n" + "\n".join(warnings_bucles))
        if not sem_exito:
            fallos.append(f"FALLO SEMÁNTICO:\nScore: {sem_score}/10\nComentarios: {eval_sem.get('comentarios', '')}")

        errores_reporte = "\n\n".join(fallos)
        print("❌ Validación insuficiente. Iniciando fase de reflexión...")

        guardar_memoria(entrada_prompt, plan, CodigoActual, errores_reporte, "Por corregir", False)

        reflexion, CodigoActual = reflexionar_y_corregir(CodigoActual, errores_reporte, entrada_prompt, historial_errores)
        print(f"💡 Reflexión del Agente:\n{reflexion}")
        historial_errores.append(f"Errores:\n{errores_reporte}\nReflexión:\n{reflexion}")

        intentos += 1

    else:
        if mejor_version["codigo"]:
            print(f"📊 Usando mejor versión con score {mejor_version['score_global']}/10")
            CodigoActual = mejor_version["codigo"]

    # 8. Documentación final
    print("📝 Generando comentarios y documentación final con Ollama...")
    documentacion = extraer_codigo_puro(documentar_codigo(CodigoActual))

    with open("CodigoFinal.py", "w", encoding="utf-8") as f:
        f.write(documentacion)
    print("📁 Código final y documentado guardado en CodigoFinal.py")


if __name__ == "__main__":
    main()
