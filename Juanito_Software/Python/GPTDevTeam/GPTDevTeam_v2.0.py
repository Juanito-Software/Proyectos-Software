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

# GPTDevTeam v2.0 — Pipeline de generación de código con LLMs locales (Ollama).
#
# Arquitectura del pipeline:
#   Planner -> Coder -> [bucle: Tester + Sandbox + Judge -> Reflector] -> Documenter
#
# Cada etapa invoca un modelo LLM distinto (configurados en MODEL_ROLES).
# El bucle de corrección garantiza mejora monótona: nunca descarta una versión
# con mejor score para adoptar una regresión generada por el reflector.

from dataclasses import dataclass
from typing import Literal
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
import importlib.util

# Forzar UTF-8 en stdout/stderr para evitar UnicodeEncodeError con emojis
# en terminales Windows que usan codificaciones legacy (cp1252, cp850, etc.).
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# =========================
# CONFIG
# =========================

# Tiempo máximo (segundos) para la ejecución completa de un script en sandbox.
TIMEOUT_EJECUCION = 30
# Tiempo de gracia (segundos) para detectar arranque interactivo exitoso.
TIMEOUT_ARRANQUE = 10
# Umbral mínimo de score de ejecución considerado aceptable (sobre 10).
SCORE_MINIMO_EXITO = 8
# Ruta del archivo JSON donde se persiste el historial de generaciones.
MEMORY_FILE = "memory.json"

# Modelos Ollama asignados a cada rol del pipeline.
# Separarlos permite ajustar velocidad/calidad por tarea sin tocar el código.
MODEL_ROLES = {
    "planner":    "qwen3:8b",
    "coder":      "qwen2.5-coder:7b",
    "tester":     "qwen2.5-coder:7b",
    "judge":      "qwen3:8b",
    "reflector":  "qwen3:8b",
    "documenter": "qwen3:8b",
}

# Tipo literal para la causa de terminación de un subproceso sandbox.
TerminationReason = Literal["normal", "timeout", "startup_heuristic", "crash"]


# =========================
# ESTADO CANÓNICO
# =========================

@dataclass
class ExecutionState:
    """Resultado de una única ejecución de subproceso (tests o main)."""
    exit_code: int | None          # Código de salida del proceso; None si no terminó.
    stdout: str
    stderr: str
    execution_score: float         # Puntuación heurística 0-10; solo para ranking.
    termination_reason: TerminationReason
    forced_stop: bool              # True si el proceso fue terminado externamente.
    warnings: list[str]

    @property
    def exec_success(self) -> bool:
        """True si el proceso terminó con exit_code 0."""
        return self.exit_code == 0

    @property
    def execution_quality(self) -> float:
        """Señal heurística de calidad del runtime. No define éxito; solo ranking."""
        return self.execution_score


@dataclass
class EvaluationState:
    """Agrega los resultados de tests, main y evaluación semántica de un intento."""
    test_state: ExecutionState
    main_state: ExecutionState
    semantic: dict       # Respuesta JSON del juez LLM.
    warnings: list[str]  # Avisos estáticos de AST (bucles, atributos fantasma).


@dataclass
class EvaluationMetrics:
    """Métricas numéricas derivadas de EvaluationState."""
    evaluation: EvaluationState

    @property
    def score_exec(self) -> float:
        """Media del score de ejecución de tests y del arranque del main."""
        return (
            self.evaluation.test_state.execution_score +
            self.evaluation.main_state.execution_score
        ) / 2

    @property
    def semantic_score(self) -> float:
        """Score semántico devuelto por el juez LLM (0-10)."""
        return float(self.evaluation.semantic.get("score_semantico", 0))

    @property
    def global_score(self) -> float:
        """Promedio de score de ejecución y score semántico."""
        return (self.score_exec + self.semantic_score) / 2


@dataclass
class EvaluationDecision:
    """Decisiones binarias de éxito/fallo para un intento de generación."""
    evaluation: EvaluationState
    metrics: EvaluationMetrics

    @property
    def runtime_success(self) -> bool:
        """True si tanto los tests como el main terminaron con exit_code 0."""
        return (
            self.evaluation.test_state.exit_code == 0 and
            self.evaluation.main_state.exit_code == 0
        )

    @property
    def semantic_success(self) -> bool:
        # Se comprueba tanto el score como el campo cumple_requisitos porque el
        # juez LLM puede ser incoherente: un score >= 7 no garantiza que el
        # campo booleano sea True. Ambas condiciones deben cumplirse.
        return (
            self.metrics.semantic_score >= 7
            and self.evaluation.semantic.get("cumple_requisitos", False)
        )

    @property
    def clean(self) -> bool:
        """True si no hay advertencias estáticas de AST."""
        return len(self.evaluation.warnings) == 0

    @property
    def success(self) -> bool:
        """True si el intento supera los tres criterios: runtime, semántica y limpieza."""
        return self.runtime_success and self.semantic_success and self.clean


# =========================
# CAPA LLM (OLLAMA)
# =========================

def ollama_generate(model: str, prompt: str) -> str:
    """
    Envía un prompt a Ollama y devuelve la respuesta como string.
    Devuelve cadena vacía ante cualquier error de red o de modelo.
    El timeout de 600 s es deliberadamente alto: la inferencia local puede
    ser lenta en hardware limitado y la tarea más pesada (reflexión) puede
    producir respuestas largas.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=600
        )
        result = response.json().get("response", "").strip()
        if not result:
            print(f"⚠️ Ollama devolvió respuesta vacía para el modelo '{model}'.")
        return result
    except Exception as e:
        print("❌ Error al llamar a Ollama:", e)
        return ""


def planificar_diseño(prompt: str) -> str:
    """
    Etapa 1 del pipeline: el Planner LLM genera un plan de diseño estructurado.
    El plan incluye una sección de NOMBRES CANÓNICOS que actúa como contrato
    de nomenclatura para el Coder: cualquier nombre no listado allí se considera
    inválido, previniendo traducciones o abreviaciones que causarían AttributeError.
    """
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
        "4. NOMBRES CANÓNICOS (sección obligatoria, literal): una lista final, en español y snake_case, de "
        "cada atributo y método que el código deberá usar EXACTAMENTE con ese nombre. Prohibido usar sinónimos, "
        "traducciones al inglés o abreviaturas distintas en ningún otro punto del plan ni, después, en el código. "
        "Cualquier nombre que no aparezca en esta lista se considera inválido.\n"
        "5. SEMÁNTICA DE CADA ATRIBUTO NUMÉRICO: para cada atributo de estado (ej. hambre, energía, felicidad, "
        "salud), indica explícitamente qué significa un valor alto frente a uno bajo, y qué acciones concretas lo "
        "aumentan y cuáles lo disminuyen (ej. 'hambre alta = el personaje tiene mucha hambre; comer DISMINUYE "
        "hambre; el paso del tiempo AUMENTA hambre'). Esto evita ambigüedad y contradicciones en la implementación.\n"
        "IMPORTANTE: No generes código Python todavía. Genera únicamente el plan textual estructurado."
    )
    print("📋 [Planner] Generando plan de diseño...")
    return ollama_generate(model, prompt_planner)


def generar_codigo_de_plan(prompt: str, plan: str) -> str:
    """
    Etapa 2 del pipeline: el Coder LLM implementa el plan como código Python.
    El plan se incluye como contrato de implementación: cada sección debe traducirse
    en estructuras concretas del código, y los nombres canónicos son obligatorios.
    """
    model = MODEL_ROLES["coder"]
    prompt_coder = (
        "Actúa como un Ingeniero de Software Senior especializado en diseño de sistemas en Python.\n"
        "Tu objetivo no es solo generar código funcional, sino producir una arquitectura coherente, modular y extensible.\n\n"

        f"REQUERIMIENTO DEL USUARIO:\n{prompt}\n\n"
        f"PLAN DE DISEÑO (OBLIGATORIO, CONTRATO DE IMPLEMENTACIÓN):\n{plan}\n\n"

        "REGLAS DE DISEÑO (CRÍTICAS):\n"
        "1. Debes convertir cada sección del plan en estructuras explícitas del código (clases, funciones o módulos).\n"
        "2. Cada clase debe tener una única responsabilidad clara.\n"
        "3. Evita funciones monolíticas: divide lógica en métodos coherentes.\n"
        "4. Prioriza legibilidad y separación de responsabilidades sobre optimización prematura.\n"
        "5. Si el sistema es interactivo, el flujo principal debe estar en main guard ('if __name__ == \"__main__\").\n"
        "6. No incluyas código muerto, duplicado o no usado.\n"
        "7. NOMBRES EXACTOS: usa siempre, letra por letra, los nombres de atributos y métodos de la sección "
        "'NOMBRES CANÓNICOS' del plan. PROHIBIDO traducirlos al inglés, abreviarlos o inventar variantes "
        "(ej. si el plan define 'hambre', NUNCA escribas 'hunger'; si define 'felicidad', NUNCA escribas "
        "'happiness'). Un nombre distinto al del plan para el mismo concepto es un error grave.\n"
        "8. ATRIBUTOS SIN FANTASMAS: todo atributo que se lea como self.X en cualquier método debe haber sido "
        "asignado previamente con ESE MISMO nombre exacto (normalmente en __init__). No leas un atributo "
        "que nunca definiste con ese nombre en ningún otro punto de la clase.\n"
        "9. Respeta la semántica de aumento/disminución de cada atributo tal como la describe el plan; no "
        "inviertas la lógica (ej. si el plan dice que comer disminuye el hambre, el código debe disminuirla).\n\n"

        "REGLAS DE SALIDA:\n"
        "- Devuelve únicamente código Python dentro de un bloque ```python.\n"
        "- Sin explicaciones externas.\n"
        "- El código debe ser completamente ejecutable.\n\n"

        "VALIDACIÓN INTERNA OBLIGATORIA (ANTES DE RESPONDER):\n"
        "- ¿Cada punto del plan está representado en el código?\n"
        "- ¿El código puede entenderse sin contexto externo?\n"
        "- ¿Las responsabilidades están separadas correctamente?\n"
        "- ¿Cada self.X que usas en algún método aparece asignado en __init__ con ese mismo nombre exacto?\n"
        "- ¿Usaste los nombres canónicos del plan sin traducir, abreviar ni renombrar?\n"
    )
    print("💻 [Coder] Generando código base a partir del plan...")
    raw_code = ollama_generate(model, prompt_coder)
    return extraer_codigo_puro(raw_code)


def documentar_codigo(codigo: str) -> str:
    """Pide al Documenter LLM que añada comentarios inline al código generado."""
    model = MODEL_ROLES["documenter"]
    prompt = (
        "Añade comentarios para el siguiente código Python:\n"
        "IMPORTANTE: Utiliza siempre # para los comentarios, no agregues explicaciones fuera de él.\n"
        f"Codigo a documentar:\n{codigo.strip()}"
    )
    return ollama_generate(model, prompt)


def reflexionar_y_corregir(
    codigo: str,
    errores: str,
    prompt: str,
    historial_errores: list[str] | None = None,
) -> tuple[str, str]:
    """
    Etapa de corrección: el Reflector LLM analiza el informe de errores y devuelve
    una versión corregida del código junto con un análisis de causa raíz.

    El contrato de formato de respuesta es:
        --- REFLEXIÓN ---
        [análisis]
        --- CÓDIGO CORREGIDO ---
        ```python
        [código]
        ```
    Si el modelo no respeta el formato, se intenta extraer código de la respuesta completa.
    Se incluyen los últimos 2 errores del historial para que el reflector evite
    repetir soluciones que ya fallaron en intentos anteriores.
    """
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
        "3. Si el informe de errores menciona un 'atributo fantasma' (self.X usado pero nunca asignado), NO "
        "inventes una asignación nueva con ese nombre: identifica cuál es el atributo real ya definido en "
        "__init__ (probablemente un sinónimo, traducción o typo del mismo concepto) y unifica TODOS los usos "
        "de ese concepto bajo un único nombre exacto en toda la clase.\n"
        "4. Devuelve toda tu respuesta en el siguiente formato:\n\n"
        "--- REFLEXIÓN ---\n"
        "[Escribe aquí tu análisis y causa raíz del fallo en español]\n"
        "--- CÓDIGO CORREGIDO ---\n"
        "```python\n"
        "[Código corregido aquí]\n"
        "```"
    )
    print("🔄 [Reflection Loop] Solicitando reflexión y corrección...")
    response = ollama_generate(model, prompt_debug)

    reflexion = "No se pudo extraer la reflexión."
    codigo_corregido = codigo

    if "--- REFLEXIÓN ---" in response and "--- CÓDIGO CORREGIDO ---" in response:
        partes = response.split("--- CÓDIGO CORREGIDO ---")
        reflexion = partes[0].replace("--- REFLEXIÓN ---", "").strip()
        codigo_corregido = extraer_codigo_puro(partes[1])
    else:
        codigo_corregido = extraer_codigo_puro(response)

    return reflexion, codigo_corregido


def evaluar_semantica(codigo: str, prompt: str, resultado_tests: str) -> dict:
    """
    El Judge LLM puntúa si el código satisface los requisitos del usuario.

    Devuelve un dict con las claves: cumple_requisitos, score_semantico, comentarios.
    Ante cualquier fallo de parseo devuelve un dict de fallo seguro (score=0,
    cumple=False) para evitar que código sin evaluar pase como válido.
    """
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
        datos = extract_json(raw_eval)
        if datos:
            return datos
    except Exception as e:
        print(f"⚠️ Error parseando la evaluación semántica: {e}. Respuesta cruda: {raw_eval}")

    print("⚠️ Fallo en evaluación semántica: respuesta no parseable. Tratando como NO conforme.")
    return {
        "cumple_requisitos": False,
        "score_semantico": 0,
        "comentarios": (
            "El juez semántico no devolvió un JSON válido "
            f"(respuesta cruda: {raw_eval[:300]!r}). "
            "Se trata como fallo para evitar aprobar código sin evaluación real."
        )
    }


# =========================
# UTILIDADES DE TEXTO Y PROMPTS
# =========================

def extraer_codigo_puro(texto: str) -> str:
    """
    Extrae el bloque de código Python de la respuesta de un LLM.
    Busca primero el patrón ```python ... ``` estándar de Markdown.
    Si no encuentra delimitadores, elimina líneas de comentario y prefijos
    de instrucción que algunos modelos anteponen a su respuesta.
    """
    bloques = re.findall(r"```python(.*?)```", texto, re.DOTALL)
    if bloques:
        codigo = bloques[0].strip()
    else:
        lineas = texto.splitlines()
        lineas = [l for l in lineas if not l.strip().startswith("#") and not l.strip().startswith("Instrucción")]
        codigo = "\n".join(lineas)

    codigo = re.sub(r'^\s*"""', '', codigo)
    codigo = re.sub(r'"""$', '', codigo)
    return textwrap.dedent(codigo).strip()


def limpiar_docstring_inicial(codigo: str) -> str:
    """
    Elimina un docstring o bloque de texto inicial que el LLM haya incluido
    antes del código real. Algunos modelos envuelven su respuesta en triple
    comillas incluso cuando se les pide solo código, o añaden una introducción
    en prosa antes del primer import/def/class.
    """
    codigo = codigo.lstrip()
    lineas = codigo.splitlines()
    triple_quotes = ('"""', "'''")

    apertura_idx = None
    cierre_idx = None

    for i, linea in enumerate(lineas[:50]):
        contenido = linea.strip()

        if any(contenido.startswith(q) for q in triple_quotes):
            if apertura_idx is None:
                apertura_idx = i
                if any(contenido.endswith(q) for q in triple_quotes) and len(contenido) > 6:
                    # Docstring de una sola línea tipo """texto""": se descarta la línea entera.
                    return '\n'.join(lineas[i + 1:]).lstrip()
        elif any(q in contenido for q in triple_quotes):
            if apertura_idx is None and cierre_idx is None:
                cierre_idx = i
                bloque_doc = '\n'.join(lineas[:cierre_idx + 1])
                resto = '\n'.join(lineas[cierre_idx + 1:])
                return f'"""\n{bloque_doc}\n"""\n{resto.lstrip()}'

        if contenido.startswith(("import", "from", "def ", "class ")):
            break

    if apertura_idx is not None:
        return '\n'.join(lineas[apertura_idx + 1:]).lstrip()

    return codigo


def formatear_informe_ejecucion(state: ExecutionState) -> str:
    """Convierte un ExecutionState en un string legible para el reflector LLM."""
    return (
        f"Exit code: {state.exit_code}\n"
        f"Execution score: {state.execution_score}/{SCORE_MINIMO_EXITO} mínimo\n"
        f"Exec success: {state.exec_success}\n"
        f"Forced stop: {state.forced_stop}\n"
        f"Termination reason: {state.termination_reason or 'N/A'}\n\n"
        f"stdout:\n{state.stdout or '(vacío)'}\n\n"
        f"stderr:\n{state.stderr or '(vacío)'}"
    )


def build_refactor_prompt(code_snippet: str) -> str:
    """Construye un prompt de refactorización genérico para el Coder LLM."""
    return (
        "Corrige y refactoriza el siguiente código Python.\n"
        "- Asegúrate de que no tenga errores de ejecución.\n"
        "- Mejora la legibilidad y mantenibilidad.\n"
        "- Devuelve solo el código Python corregido, sin comentarios ni explicación.\n"
        "\n```python\n" + code_snippet.strip() + "\n```"
    )


def build_debug_prompt(codigo: str, informe: str, historial_errores: list[str]) -> str:
    """Construye un prompt de depuración que incluye los últimos 3 errores del historial."""
    historial_txt = ""
    if historial_errores:
        previos = "\n---\n".join(historial_errores[-3:])
        historial_txt = f"\n\nErrores previos en intentos anteriores:\n{previos}"

    return (
        "# --- INSTRUCCIONES PARA DEPURAR EL SIGUIENTE CÓDIGO ---\n"
        "Analiza el error de ejecución.\n"
        "Devuelve una versión corregida del código.\n"
        "Mantén la estructura original.\n"
        "No introduzcas dependencias nuevas, a no ser de que sean necesarias.\n"
        "Prioriza estabilidad sobre optimización.\n"
        f"\n```python\n{codigo}\n```\n\n"
        f"Informe de ejecución:\n{informe}"
        f"{historial_txt}"
    )


def extract_json(text: str):
    """
    Escanea el texto buscando el primer objeto JSON válido.
    Necesario porque los LLMs frecuentemente anteponen prosa explicativa
    antes del JSON, incluso cuando se les pide solo el JSON.
    """
    decoder = json.JSONDecoder()
    for i in range(len(text)):
        try:
            obj, _ = decoder.raw_decode(text[i:])
            return obj
        except json.JSONDecodeError:
            continue
    return None


# =========================
# SANDBOX DE EJECUCIÓN
# =========================

def _env_sandbox() -> dict[str, str]:
    """
    Construye un entorno mínimo para el subproceso del sandbox.
    Se reducen las variables de entorno al mínimo necesario para aislar el
    proceso del sistema del usuario (credenciales, paths personales, etc.).
    En Windows se incluyen TEMP/TMP y variables de perfil porque Python las
    necesita para tempfile.gettempdir() y para cargar extensiones .pyd;
    sin ellas, incluso código correcto puede fallar con errores crípticos.
    """
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "PYTHONIOENCODING": "utf-8",
    }
    if os.name == "nt":
        env["COMSPEC"] = os.environ.get("COMSPEC", "")
        for var in ("TEMP", "TMP", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "SystemDrive", "LOCALAPPDATA"):
            val = os.environ.get(var)
            if val:
                env[var] = val
    return env


def evaluar_salida(stdout: str, stderr: str, exit_code: int | None) -> int:
    """
    Puntuación heurística de calidad de una ejecución (0-10).
    No es autoridad sobre el éxito; solo se usa para ranking y diagnóstico.
    Criterios positivos: exit_code 0, stderr limpio, stdout no vacío.
    Penalizaciones: AssertionError (test fallido) y Traceback (excepción).
    """
    score = 0
    if exit_code == 0:
        score += 5
    if not stderr.strip():
        score += 3
    if stdout.strip():
        score += 2
    if "AssertionError" in stderr:
        score -= 5
    if "Traceback" in stderr:
        score -= 3
    return max(0, min(score, 10))


def ejecutar_codigo_py(
    path: str,
    workspace_dir: str | None = None,
    timeout: int = TIMEOUT_EJECUCION,
    startup_timeout: int = TIMEOUT_ARRANQUE,
    block_imports: bool = True,
    stdin_data: str | None = "salir\nexit\nquit\nsalir\n5\n0\n",
) -> ExecutionState:
    """
    Ejecuta un script Python en un subproceso sandboxado y devuelve su estado.

    Mecanismo de aislamiento (tres capas):
      1. Directorio temporal propio: el script se copia a .sandbox/ para que
         no pueda leer archivos del directorio de trabajo del pipeline.
      2. Subproceso con -I: ignora PYTHON*, site-packages de usuario y no
         añade el directorio del script a sys.path.
      3. Wrapper de Python: bloquea imports peligrosos desde __main__,
         elimina breakpoint() de builtins y aplica resource limits (Unix).

    Manejo de programas interactivos:
      stdin_data pre-alimenta respuestas plausibles de "salir" para que los
      programas con input() no fallen inmediatamente por EOF. El stdin NO se
      cierra: si el programa pide más input del que se le dio, se bloquea en
      input() y la heurística de arranque lo rescata como éxito.

    Heurística de arranque (startup_heuristic):
      Si el proceso lleva startup_timeout segundos vivo, ya produjo salida en
      stdout y no hay errores en stderr, se interpreta como un programa
      interactivo correcto que espera más input. Se termina con SIGTERM y se
      normaliza exit_code a 0 (el código de señal no refleja éxito/fallo).
    """
    proceso = None

    if workspace_dir:
        temp_dir = os.path.join(workspace_dir, ".sandbox")
        os.makedirs(temp_dir, exist_ok=True)
    else:
        temp_dir = tempfile.mkdtemp(prefix="sandbox_")

    BLOCKED_MODULES = {
        "os", "sys", "subprocess", "threading",
        "multiprocessing", "requests", "socket",
        "ctypes", "importlib",
    } if block_imports else set()

    wrapper_path = os.path.join(temp_dir, "sandbox_wrapper.py")
    script_name = os.path.basename(path)
    sandbox_script_path = os.path.join(temp_dir, script_name)

    try:
        # Copiar el script al directorio aislado para evitar acceso al árbol original.
        if os.path.abspath(path) != os.path.abspath(sandbox_script_path):
            shutil.copy2(path, sandbox_script_path)

        # El wrapper aplica restricciones antes de ejecutar el script objetivo.
        # Diseño: solo prepara el entorno de seguridad; delega la ejecución real
        # en runpy.run_path para no reimplementar el comportamiento de __main__.
        wrapper_code = f"""
import sys
import builtins
import runpy

# El flag -I descarta PYTHON*, incluida PYTHONIOENCODING.
# Se reconfigura aquí directamente para evitar UnicodeEncodeError con emojis.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
except Exception:
    pass

# Solo se elimina breakpoint(): eval/exec/compile son necesarios internamente
# por la stdlib (p. ej. collections.namedtuple usa eval) y quitarlos rompe
# módulos como pkgutil, tokenize y runpy que se cargan antes del script.
for _peligroso in ("breakpoint",):
    try:
        delattr(builtins, _peligroso)
    except Exception:
        pass

# El filtro de imports comprueba quién hace el import: si el llamador es
# __main__ (el script generado) o desconocido, el import se bloquea.
# Si el llamador es otro módulo de la stdlib ya cargado (su __name__ no
# es "__main__"), se deja pasar para no romper dependencias internas.
BLOCKED = {BLOCKED_MODULES!r}

__orig_import__ = builtins.__import__

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root in BLOCKED:
        llamador = globals.get("__name__") if isinstance(globals, dict) else None
        if llamador is None or llamador == "__main__":
            raise ImportError(f"Import bloqueado: {{name}}")
    return __orig_import__(name, globals, locals, fromlist, level)

builtins.__import__ = safe_import

if len(sys.argv) < 2:
    raise SystemExit("sandbox_wrapper: falta la ruta del script objetivo")

runpy.run_path(sys.argv[1], run_name="__main__")
"""

        with open(wrapper_path, "w", encoding="utf-8") as f:
            f.write(wrapper_code)

        proceso = subprocess.Popen(
            [sys.executable, "-I", "-u", "sandbox_wrapper.py", sandbox_script_path],
            cwd=temp_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=_env_sandbox(),
        )

        # Alimentar stdin sin cerrarlo: si el programa pide más input del que
        # recibe, se bloquea en input() en lugar de reventar con EOFError.
        # El bloqueo es la señal que la heurística de arranque interpreta como éxito.
        if proceso.stdin and stdin_data:
            try:
                proceso.stdin.write(stdin_data)
                proceso.stdin.flush()
            except Exception:
                pass

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        lock = threading.Lock()

        def reader(stream, buffer):
            try:
                for line in stream:
                    with lock:
                        buffer.append(line)
            finally:
                try:
                    stream.close()
                except Exception:
                    pass

        t_out = threading.Thread(target=reader, args=(proceso.stdout, stdout_lines), daemon=True)
        t_err = threading.Thread(target=reader, args=(proceso.stderr, stderr_lines), daemon=True)
        t_out.start()
        t_err.start()

        termination_reason: TerminationReason = "normal"
        start = time.time()

        while proceso.poll() is None:
            elapsed = time.time() - start

            with lock:
                stdout_parcial = "".join(stdout_lines)
                stderr_parcial = "".join(stderr_lines)

            # Heurística de arranque: proceso vivo + salida producida + sin errores
            # = programa interactivo correcto esperando más input del usuario.
            if (
                elapsed >= startup_timeout
                and stdout_parcial.count("\n") > 0
                and not stderr_parcial.strip()
            ):
                proceso.terminate()
                try:
                    proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proceso.kill()
                    proceso.wait()
                termination_reason = "startup_heuristic"
                break

            if elapsed >= timeout:
                proceso.kill()
                try:
                    proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                termination_reason = "timeout"
                break

            time.sleep(0.1)

        t_out.join(timeout=2)
        t_err.join(timeout=2)

        stdout = "".join(stdout_lines)
        stderr = "".join(stderr_lines)
        exit_code = proceso.returncode

        # Tras proceso.terminate(), returncode contiene el código de señal (p. ej. -15),
        # no 0. startup_heuristic significa arranque correcto, así que se normaliza a 0
        # para que exec_success y el resto del pipeline lo lean correctamente.
        if termination_reason == "startup_heuristic":
            exit_code = 0

        execution_score = evaluar_salida(stdout, stderr, exit_code)

        return ExecutionState(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_score=execution_score,
            termination_reason=termination_reason,
            forced_stop=(termination_reason != "normal"),
            warnings=[],
        )

    except Exception as e:
        return ExecutionState(
            exit_code=-1,
            stdout="",
            stderr=f"Error durante ejecución: {e}",
            execution_score=0,
            termination_reason="crash",
            forced_stop=False,
            warnings=["runtime_exception"],
        )

    finally:
        if proceso is not None:
            try:
                if proceso.poll() is None:
                    proceso.kill()
                    proceso.wait(timeout=2)
            except Exception:
                pass
            if proceso.stdin:
                try:
                    proceso.stdin.close()
                except Exception:
                    pass
        shutil.rmtree(temp_dir, ignore_errors=True)


# =========================
# HERRAMIENTAS AST
# =========================

def validar_sintaxis_ast(codigo: str) -> tuple[bool, str]:
    """Comprueba si el código es sintácticamente válido sin ejecutarlo."""
    try:
        ast.parse(codigo)
        return True, ""
    except SyntaxError as e:
        return False, f"Error de sintaxis (AST): {e}"


def detectar_bucles_infinitos_ast(codigo: str) -> list[str]:
    """
    Detecta patrones `while True` y `while 1` en el AST del código.
    No es una prueba de terminación completa; identifica el caso más
    frecuente de bucle sin condición de salida evidente.
    """
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


class AttrUsageVisitor(ast.NodeVisitor):
    """
    Recorre los métodos de una clase y registra qué atributos de instancia
    (self.X) se asignan y cuáles se leen.

    Captura las formas de asignación más comunes:
      - self.x = ...     (Assign)
      - self.x: T = ...  (AnnAssign)
      - self.x += ...    (AugAssign — también cuenta como lectura)
      - setattr(self, 'x', ...)  (Call a setattr)
    """

    def __init__(self):
        self.asignados: set[str] = set()
        self.leidos: list[tuple[str, int]] = []

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                self.asignados.add(target.attr)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        target = node.target
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            self.asignados.add(target.attr)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        # self.x += 1 requiere que x ya exista, por tanto se registra como lectura;
        # y tras ejecutarse deja x asignado, así que también se añade a asignados.
        target = node.target
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            self.leidos.append((target.attr, node.lineno))
            self.asignados.add(target.attr)
        self.generic_visit(node)

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Name) and node.func.id == "setattr" and len(node.args) >= 2):
            obj, key = node.args[0], node.args[1]
            if (isinstance(obj, ast.Name) and obj.id == "self"
                    and isinstance(key, ast.Constant) and isinstance(key.value, str)):
                self.asignados.add(key.value)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if (isinstance(node.value, ast.Name) and node.value.id == "self"
                and isinstance(node.ctx, ast.Load)):
            self.leidos.append((node.attr, node.lineno))
        self.generic_visit(node)


def detectar_atributos_no_definidos(codigo: str) -> list[str]:
    """
    Heurística estática que detecta atributos de instancia leídos como
    self.X en algún método de una clase sin que X haya sido asignado en
    ningún método de esa misma clase.

    Conservadora por diseño: solo reporta atributos que no aparecen
    asignados en ningún sitio, no problemas de orden de inicialización.
    El patrón más frecuente que detecta es la traducción de nombres:
    el LLM define self.hambre en __init__ pero luego lee self.hunger en
    otro método, causando AttributeError en tiempo de ejecución.
    """
    warnings = []
    try:
        tree = ast.parse(codigo)
    except Exception:
        return warnings

    object_attrs = set(dir(object))

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        # Los métodos propios (def metodo(self)) son referencias válidas de self.X.
        metodos_clase = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}

        visitor = AttrUsageVisitor()
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                visitor.visit(item)

        nombres_validos = visitor.asignados | metodos_clase | object_attrs

        primera_aparicion: dict[str, int] = {}
        for nombre, lineno in visitor.leidos:
            if nombre in nombres_validos:
                continue
            primera_aparicion.setdefault(nombre, lineno)

        for nombre, lineno in primera_aparicion.items():
            warnings.append(
                f"Atributo 'self.{nombre}' usado en la clase '{node.name}' (línea {lineno}) "
                "pero nunca asignado en __init__ ni en ningún otro método de esa clase. "
                "Provocará AttributeError en tiempo de ejecución (posible typo o nombre "
                "traducido/abreviado respecto al usado en __init__)."
            )

    return warnings


class InitVisitor(ast.NodeVisitor):
    """
    Recorre un método __init__ y recolecta los atributos de instancia que asigna.
    Utilizado por extraer_api_estatica para construir la lista de atributos de cada clase.
    """

    def __init__(self):
        self.attributes: set[str] = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                self.attributes.add(target.attr)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        target = node.target
        if (isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"):
            self.attributes.add(target.attr)
        self.generic_visit(node)

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Name) and node.func.id == "setattr" and len(node.args) >= 2):
            obj, key = node.args[0], node.args[1]
            if (isinstance(obj, ast.Name) and obj.id == "self"
                    and isinstance(key, ast.Constant) and isinstance(key.value, str)):
                self.attributes.add(key.value)
        self.generic_visit(node)


def extraer_api_estatica(codigo: str) -> dict:
    """
    Extrae la API pública del código generado como diccionario estructurado.
    El resultado se usa como contrato para el generador de tests (qué símbolos
    puede usar) y para el validador de tests (qué símbolos son válidos).

    Estructura devuelta:
        {
            "classes": {
                "NombreClase": {
                    "init_args": [...],   # Parámetros de __init__ (sin self).
                    "methods":    [...],  # Nombres de métodos públicos.
                    "attributes": [...],  # Atributos asignados en __init__.
                }
            },
            "functions": [...]  # Funciones de nivel de módulo.
        }
    """
    api: dict = {"classes": {}, "functions": []}
    try:
        tree = ast.parse(codigo)
    except Exception:
        return api

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            api["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            clase: dict = {"init_args": [], "methods": [], "attributes": []}
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


# =========================
# GENERACIÓN Y VALIDACIÓN DE TESTS
# =========================

class TestSyntaxError(Exception):
    """
    Excepción separada de SyntaxError para distinguir un fallo de parseo del
    código de tests de un error semántico de validación. El bucle de reintentos
    de tests necesita saber si debe regenerar desde cero o solo corregir.
    """
    pass


def validar_tests_vs_api(test_code: str, api: dict) -> list[str]:
    """
    Valida estáticamente que el código de tests solo use símbolos definidos en la API.
    Lanza TestSyntaxError si el código de tests no es Python válido.
    Devuelve lista de errores semánticos (puede estar vacía si todo es válido).
    """
    try:
        tree = ast.parse(test_code)
    except SyntaxError as e:
        raise TestSyntaxError(f"Tests inválidos: error de sintaxis AST -> {e.msg} (línea {e.lineno})") from e

    validator = TestSemanticValidator(api)
    return validator.validate(tree)


class TestSemanticValidator(ast.NodeVisitor):
    """
    Visitador AST que recorre el código de tests y verifica que:
      - No use módulos prohibidos (threading, multiprocessing, concurrent).
      - No llame a métodos prohibidos (sleep).
      - Solo acceda a clases, funciones, métodos y atributos presentes en la API.

    Soporta alias de clase (Alias = mod.ClaseValida) y variables SUT
    (obj = mod.ClaseValida()) para validar accesos en cadena (obj.metodo()).
    """

    def __init__(self, api: dict):
        self.api = api
        self.errors: list[str] = []
        self._clases_validas = set(api.get("classes", {}).keys())
        self._funciones_validas = set(api.get("functions", []))
        self.class_aliases: dict[str, str] = {}
        self.sut_vars: dict[str, str] = {}
        self.object_builtins = set(dir(object))

        self.PROHIBIDOS_IMPORT = {"threading", "multiprocessing", "concurrent"}
        self.PROHIBIDOS_NOMBRES = {"Thread", "daemon", "redirect_stdout", "StringIO"}
        self.PROHIBIDOS_METODOS = {"sleep"}

    def validate(self, tree: ast.AST) -> list[str]:
        self.visit(tree)
        return self.errors

    def resolve_alias(self, name: str) -> str:
        """Resuelve cadenas de alias hasta el nombre de clase original."""
        while name in self.class_aliases:
            name = self.class_aliases[name]
        return name

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split(".")[0] in self.PROHIBIDOS_IMPORT:
                self.errors.append(f"Importación prohibida en tests: {alias.name}")

    def visit_ImportFrom(self, node):
        if node.module and node.module.split(".")[0] in self.PROHIBIDOS_IMPORT:
            self.errors.append(f"Importación prohibida en tests: {node.module}")

    def visit_Assign(self, node):
        # Detecta: Alias = mod.ClaseValida  (alias de clase sin instanciar)
        if (isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "mod"):
            class_name = node.value.attr
            if class_name in self._clases_validas:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        self.class_aliases[t.id] = class_name

        # Detecta: obj = mod.ClaseValida(...)  o  obj = Alias(...)
        elif isinstance(node.value, ast.Call):
            func = node.value.func
            class_name = None
            if (isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "mod"):
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
                set(info.get("methods", [])) | set(info.get("attributes", [])) |
                set(info.get("init_args", [])) | self.object_builtins
            )
            if nombre not in allowed:
                self.errors.append(f"'{nombre}' no existe en SUT '{class_name}'")

        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
            self.errors.append("Uso prohibido: sleep() en tests")
        self.generic_visit(node)


def verificar_validador_ast():
    """
    Auto-test del validador AST. Se ejecuta al inicio de cada pipeline para
    garantizar que el propio mecanismo de validación funciona correctamente
    antes de validar cualquier código generado.
    Cubre: método válido, atributo válido, método inexistente, atributo
    inexistente, función válida, función inexistente, alias de clase,
    import prohibido, sleep prohibido y builtins de lista.
    """
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

    casos = [
        # (descripción, código_test, debe_pasar, cadena_esperada_en_error)
        ("método válido",      "obj = mod.ClaseValida()\nobj.metodo_valido()",             True,  None),
        ("atributo válido",    "obj = mod.ClaseValida()\nassert obj.atributo_valido is not None", True, None),
        ("método inventado",   "obj = mod.ClaseValida()\nobj.metodo_inventado()",           False, "metodo_inventado"),
        ("atributo inventado", "obj = mod.ClaseValida()\nobj.campo_inventado",              False, "campo_inventado"),
        ("función válida",     "mod.funcion_valida()",                                      True,  None),
        ("función inventada",  "mod.funcion_magica()",                                      False, "funcion_magica"),
        ("alias de clase",     "Alias = mod.ClaseValida\nobj = Alias()\nobj.metodo_valido()", True, None),
        ("import prohibido",   "import threading",                                          False, "Importación prohibida"),
        ("sleep prohibido",    "import time\ntime.sleep(1)",                               False, "sleep"),
        ("builtin de lista",   "x = []\nx.append(1)",                                      True,  None),
    ]

    for descripcion, codigo_test, debe_pasar, cadena in casos:
        err = validar_tests_vs_api(codigo_test, api_demo)
        if debe_pasar:
            assert not err, f"Caso '{descripcion}' falló inesperadamente: {err}"
        else:
            assert any(cadena in e for e in err), (
                f"Caso '{descripcion}' no detectó el error esperado ('{cadena}'): {err}"
            )

    print("✅ [Self-Test] Validador AST verificado correctamente.")


def generar_asserts_estaticos(api: dict) -> str:
    """
    Genera assertions de existencia (hasattr) para cada clase, función y método
    de la API. Estas comprobaciones estáticas se anteponen a los tests dinámicos
    del LLM y verifican la estructura mínima del módulo antes de ejercitar la lógica.
    """
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


def generar_tests(codigo: str, api: dict) -> str:
    """
    Pide al Tester LLM que genere assertions de comportamiento para el código.
    Incluye la API oficial como contrato y una plantilla de referencia dinámica
    (construida desde la API) para guiar el formato de salida del modelo.
    """
    model = MODEL_ROLES["tester"]
    api_resumen = json.dumps(api, indent=2, ensure_ascii=False)

    template_lines = []
    for clase_name, clase_info in api.get("classes", {}).items():
        init_args = clase_info.get("init_args", [])
        dummy_args = [f'"test_{arg}"' for arg in init_args]
        args_str = ", ".join(dummy_args)
        template_lines.append(f"# Ejemplo de test dinámico para {clase_name}:")
        template_lines.append(f"obj = mod.{clase_name}({args_str})")
        for attr in clase_info.get("attributes", []):
            template_lines.append(f"assert hasattr(obj, '{attr}')")
        for method in clase_info.get("methods", []):
            if method != "__init__":
                template_lines.append(f"# obj.{method}()")
    template_str = "\n".join(template_lines)

    prompt_tests = (
        "Actúa como un Ingeniero de QA experto en Python.\n"
        "Genera tests unitarios de comportamiento usando exclusivamente la palabra clave assert de Python.\n\n"
        "=== REGLAS CRÍTICAS (OBLIGATORIAS) ===\n"
        "1. Los tests deben ser 100% síncronos, deterministas y sin concurrencia.\n"
        "2. Está TERMINANTEMENTE PROHIBIDO el uso de: threading, Thread, time.sleep, sleep, time, StringIO, redirect_stdout, daemon, simulación de input por stdin o cualquier concurrencia/sincronización artificial.\n"
        "3. Los tests deben tratar el código como una API cerrada.\n"
        "4. Solo se permiten llamadas o accesos a símbolos descritos en la API OFICIAL (OBLIGATORIA).\n"
        "5. Cualquier símbolo (clase, función, método o atributo) que no esté en la API se considera inexistente.\n"
        "6. No manipules __dict__ ni uses try/except para evadir errores de ejecución.\n"
        "7. No llames a __init__ de forma explícita (ej. t.__init__()), instancia la clase llamándola normalmente.\n\n"
        "=== API OFICIAL (OBLIGATORIA) ===\n"
        "Todo símbolo no listado aquí debe considerarse inexistente.\n"
        "Está prohibido generar tests que usen clases, funciones, atributos o métodos fuera de esta API.\n\n"
        f"{api_resumen}\n\n"
        "=== PLANTILLA DE REFERENCIA ===\n"
        f"{template_str}\n\n"
        f"=== CÓDIGO DE LA APLICACIÓN ===\n```python\n{codigo}\n```\n\n"
        "Genera assertions reales (assert) de comportamiento de Python para validar la lógica. "
        "Devuelve solo el código de test limpio dentro de un bloque ```python."
    )

    print("🧪 [Test Generator] Generando assertions de prueba...")
    raw_tests = ollama_generate(model, prompt_tests)
    return extraer_codigo_puro(raw_tests)


def generar_tests_corregir(codigo: str, api: dict, test_previo: str, errores: list[str]) -> str:
    """
    Re-genera los tests corrigiendo los errores reportados por validar_tests_vs_api.
    Incluye el test anterior y la lista de errores para que el modelo sepa
    exactamente qué símbolos eliminó o reemplazó.
    """
    model = MODEL_ROLES["tester"]
    api_resumen = json.dumps(api, indent=2, ensure_ascii=False)
    errores_txt = "\n".join(f"- {err}" for err in errores)

    prompt_tests = (
        "Actúa como un Ingeniero de QA experto en Python.\n"
        "El código de test que generaste previamente contiene errores de validación AST o usa símbolos inexistentes fuera de la API oficial.\n\n"
        "=== ERRORES DE VALIDACIÓN ===\n"
        f"{errores_txt}\n\n"
        "=== CÓDIGO DE TEST ANTERIOR ===\n"
        f"```python\n{test_previo}\n```\n\n"
        "=== REGLAS CRÍTICAS (OBLIGATORIAS) ===\n"
        "1. Los tests deben ser 100% síncronos, deterministas y sin concurrencia.\n"
        "2. Está TERMINANTEMENTE PROHIBIDO el uso de: threading, Thread, time.sleep, sleep, time, StringIO, redirect_stdout, daemon, simulación de input por stdin o cualquier concurrencia/sincronización artificial.\n"
        "3. Los tests deben tratar el código como una API cerrada y usar solo la API oficial.\n\n"
        "=== API OFICIAL (OBLIGATORIA) ===\n"
        "Todo símbolo no listado aquí debe considerarse inexistente.\n"
        "Está prohibido generar tests que usen clases, funciones, atributos o métodos fuera de esta API.\n\n"
        f"{api_resumen}\n\n"
        "=== CÓDIGO DE LA APLICACIÓN ===\n"
        f"```python\n{codigo}\n```\n\n"
        "Corrige el código de test anterior eliminando o corrigiendo las llamadas a símbolos no permitidos o el uso de concurrencia. "
        "Devuelve solo los assertions assert de Python corregidos y limpios dentro de un bloque ```python."
    )
    print("🧪 [Test Generator] Corrigiendo assertions de prueba por errores AST...")
    raw_tests = ollama_generate(model, prompt_tests)
    return extraer_codigo_puro(raw_tests)


# =========================
# MEMORIA PERSISTENTE
# =========================

def cargar_memoria() -> list[dict]:
    """Carga el historial de generaciones desde el archivo JSON. Devuelve lista vacía si no existe."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def guardar_memoria(prompt: str, plan: str, codigo: str, error: str, solucion: str, exito: bool):
    """
    Persiste una entrada en el historial de generaciones (máx. 50 entradas).
    Usa escritura atómica (tempfile + os.replace) para evitar corrupción del
    archivo si el proceso es interrumpido durante la escritura.
    """
    mem = cargar_memoria()
    mem.append({
        "timestamp": time.time(),
        "prompt": prompt,
        "plan": plan,
        "codigo": codigo,
        "error": error,
        "solucion": solucion,
        "exito": exito
    })
    mem = mem[-50:]

    directorio = os.path.dirname(os.path.abspath(MEMORY_FILE)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".memory_", suffix=".tmp", dir=directorio)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, MEMORY_FILE)
    except Exception as e:
        print(f"⚠️ No se pudo guardar la memoria: {e}")
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# =========================
# PIPELINE PRINCIPAL
# =========================

def main():
    """
    Orquesta el pipeline completo de generación de código:

      1. Auto-test del validador AST.
      2. Planner LLM: genera plan de diseño estructurado.
      3. Coder LLM: genera código Python a partir del plan.
      4. Bucle de hasta max_intentos correcciones:
         a. Validación sintáctica (AST).
         b. Extracción de API estática.
         c. Generación + validación de tests (hasta 3 reintentos).
         d. Análisis estático: bucles infinitos y atributos fantasma.
         e. Ejecución de tests en sandbox.
         f. Prueba de humo del programa principal en sandbox.
         g. Evaluación semántica (Judge LLM).
         h. Decisión de éxito (EvaluationDecision).
         i. Si falla: Reflector LLM corrige el código.
         j. Tracking de mejor versión: garantiza mejora monótona del score.
      5. Documenter LLM: añade comentarios al código final.
      6. Guardado de CodigoFinal.py.
      7. Limpieza de directorios temporales del pipeline.

    El prompt puede pasarse como argumentos de línea de comandos; si no se
    proporcionan, se usa el ejemplo del Tamagotchi como caso de prueba.
    """
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
    if not plan.strip():
        print("❌ Error crítico: el Planner devolvió un plan vacío (Ollama sin respuesta). Abortando.")
        return
    print("\n--- PLAN DE DISEÑO GENERADO ---")
    print(plan)
    print("--------------------------------\n")

    # 2. Codificación inicial
    CodigoActual = generar_codigo_de_plan(entrada_prompt, plan)
    CodigoActual = limpiar_docstring_inicial(CodigoActual)
    if not CodigoActual.strip():
        print("❌ Error crítico: el Coder devolvió código vacío (Ollama sin respuesta). Abortando.")
        return

    max_intentos = 4
    intentos = 0
    historial_errores: list[str] = []

    # mejor_version garantiza que el reflector nunca trabaje sobre una regresión:
    # si un intento obtiene peor score que el anterior, se descarta y se retoma
    # el código con mejor puntuación conocida para seguir corrigiendo desde ahí.
    mejor_version: dict = {
        "codigo": None,
        "score_global": -1,
        "execution_score": 0,
        "semantic_score": 0,
        "errores_reporte": None,
    }

    # Los directorios temporales de cada intento se acumulan aquí y se limpian
    # todos juntos al final, una vez guardado CodigoFinal.py.
    pipeline_dirs: list[str] = []

    while intentos < max_intentos:
        print(f"\n🔄 --- INTENTO {intentos + 1} DE {max_intentos} ---")

        # a. Validación sintáctica: un error de sintaxis no puede puntuarse.
        valido_ast, error_ast = validar_sintaxis_ast(CodigoActual)
        if not valido_ast:
            print(f"❌ Error de sintaxis detectado (AST):\n{error_ast}")
            if mejor_version["codigo"] is not None:
                # Se retoma la mejor versión en lugar de corregir código roto,
                # que por definición nunca llegó a ejecutarse.
                print("⏪ Se descarta el código con error de sintaxis y se retoma la mejor versión conocida.")
                CodigoActual = mejor_version["codigo"]
                historial_errores.append(f"Error AST (descartado, se retoma mejor versión): {error_ast}")
            else:
                reflexion, CodigoActual = reflexionar_y_corregir(CodigoActual, error_ast, entrada_prompt, historial_errores)
                print(f"💡 Reflexión del Agente:\n{reflexion}")
                historial_errores.append(f"Error AST: {error_ast}\nReflexión: {reflexion}")
            intentos += 1
            continue

        pipeline_dir = tempfile.mkdtemp(prefix="gptdevteam_pipeline_")
        pipeline_dirs.append(pipeline_dir)
        code_path = os.path.join(pipeline_dir, "CodigoActual.py")
        test_path = os.path.join(pipeline_dir, "test_actual.py")

        with open(code_path, "w", encoding="utf-8") as f:
            f.write(CodigoActual)

        # b. Extracción de API estática
        api = extraer_api_estatica(CodigoActual)
        api_resumen = json.dumps(api, indent=2, ensure_ascii=False)
        print("\n📦 API DETECTADA:\n")
        print(api_resumen)

        asserts_estaticos = generar_asserts_estaticos(api)

        # c. Generación y validación de tests (hasta 3 reintentos por intento)
        MAX_INTENTOS_TEST = 3
        intento_test = 0
        asserts = ""
        errores_validacion: list[str] = []

        while intento_test < MAX_INTENTOS_TEST:
            if intento_test == 0:
                asserts = generar_tests(CodigoActual, api)
            else:
                asserts = generar_tests_corregir(CodigoActual, api, asserts, errores_validacion)

            try:
                errores_validacion = validar_tests_vs_api(asserts, api)
                if not errores_validacion:
                    print("✅ Tests validados por AST correctamente.")
                    break
                print(f"❌ Tests inválidos detectados por AST: {errores_validacion}")
                intento_test += 1
            except TestSyntaxError as e:
                print(f"💥 FALLO CRÍTICO DE TESTS (AST roto): {e}")
                errores_validacion = [str(e)]
                intento_test += 1

        test_script = (
            "import sys\n"
            "import os\n"
            "import importlib.util\n\n"
            "# --- CARGA DINÁMICA DEL MÓDULO ---\n"
            f"spec = importlib.util.spec_from_file_location('CodigoActual', {code_path!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n\n"
            "# --- ASSERTS ESTÁTICOS ---\n"
            f"{asserts_estaticos}\n\n"
            "# --- ASSERTS DINÁMICOS ---\n"
            f"{asserts}\n"
        )
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_script)

        # d. Análisis estático
        warnings_bucles = detectar_bucles_infinitos_ast(CodigoActual)
        for w in warnings_bucles:
            print(f"⚠️ AST Warning: {w}")

        warnings_atributos = detectar_atributos_no_definidos(CodigoActual)
        for w in warnings_atributos:
            print(f"⚠️ AST Warning (atributo fantasma): {w}")

        warnings_estaticos = warnings_bucles + warnings_atributos

        # e. Ejecución de tests en sandbox
        print("🧪 Ejecutando assertions de test en sandbox...")
        resultado_tests = ejecutar_codigo_py(test_path, pipeline_dir, block_imports=False)
        informe_tests = formatear_informe_ejecucion(resultado_tests)
        print(f"📊 Test Score: {resultado_tests.execution_score} | Exit code: {resultado_tests.exit_code}")
        if resultado_tests.execution_score < 3:
            print("⚠️ ejecución tests muy inestable")

        # f. Prueba de humo del programa principal
        print("🧪 Ejecutando arranque del programa principal en sandbox...")
        resultado_main = ejecutar_codigo_py(code_path, pipeline_dir)
        informe_main = formatear_informe_ejecucion(resultado_main)
        print(f"📊 Main Score: {resultado_main.execution_score} | Exit code: {resultado_main.exit_code}")
        if resultado_main.execution_score < 3:
            print("⚠️ ejecución main muy inestable")

        # g. Evaluación semántica
        eval_sem = evaluar_semantica(CodigoActual, entrada_prompt, informe_tests)
        print(
            f"⚖️ Juez Semántico Score: {eval_sem.get('score_semantico', 0)}/10 | "
            f"Cumple requisitos: {eval_sem.get('cumple_requisitos', False)}"
        )
        print(f"💬 Comentarios del Juez: {eval_sem.get('comentarios', '')}")

        evaluation = EvaluationState(
            test_state=resultado_tests,
            main_state=resultado_main,
            semantic=eval_sem,
            warnings=warnings_estaticos
        )
        metrics = EvaluationMetrics(evaluation)

        # EvaluationDecision es la única fuente de verdad sobre el éxito del intento.
        decision = EvaluationDecision(evaluation=evaluation, metrics=metrics)
        runtime_ok = decision.runtime_success
        sem_ok = decision.semantic_success
        no_warnings = decision.clean

        print(
            f"📊 Exec score: {metrics.score_exec}/10 | "
            f"Semantic score: {metrics.semantic_score}/10 | "
            f"Global score: {metrics.global_score}/10"
        )

        # j. Tracking de mejor versión
        es_nueva_mejor = metrics.global_score > mejor_version["score_global"]
        if es_nueva_mejor:
            mejor_version = {
                "codigo": CodigoActual,
                "score_global": metrics.global_score,
                "execution_score": metrics.score_exec,
                "semantic_score": metrics.semantic_score,
                "errores_reporte": None,
            }

        # h. Decisión de éxito
        if runtime_ok and sem_ok and no_warnings:
            print("✅ ÉXITO: Código validado completamente.")
            guardar_memoria(entrada_prompt, plan, CodigoActual, "Ninguno", "Código validado con éxito", True)
            break

        # Construir informe de errores para el reflector.
        # errores_lista es la lista de bloques; errores_reporte es el string final.
        errores_lista: list[str] = []

        if not evaluation.test_state.exec_success:
            errores_lista.append(f"❌ FALLO DE TESTS:\n{informe_tests}")
        if not evaluation.main_state.exec_success:
            errores_lista.append(f"❌ FALLO DE MAIN:\n{informe_main}")
        if not sem_ok:
            errores_lista.append(
                f"❌ FALLO SEMÁNTICO:\n"
                f"Score: {metrics.semantic_score}/10\n"
                f"Comentarios: {eval_sem.get('comentarios', '')}"
            )
        if warnings_bucles:
            errores_lista.append("⚠️ ADVERTENCIAS DE BUCLES:\n" + "\n".join(warnings_bucles))
        if warnings_atributos:
            errores_lista.append(
                "⚠️ ATRIBUTOS FANTASMA (self.X nunca asignado en __init__/métodos):\n" +
                "\n".join(warnings_atributos)
            )

        # Señales heurísticas de observabilidad (complementan los fallos explícitos).
        heuristica_feedback: list[str] = []
        score_tests = resultado_tests.execution_score
        score_main = resultado_main.execution_score

        if score_tests < 3:
            heuristica_feedback.append("⚠️ Tests inestables (ruido, crashes o errores intermitentes)")
        if score_main < 3:
            heuristica_feedback.append("⚠️ Main inestable o con comportamiento frágil")
        if resultado_tests.stderr.strip() or resultado_main.stderr.strip():
            heuristica_feedback.append("⚠️ Presencia de stderr → posible fragilidad o excepciones ocultas")
        if not resultado_main.stdout.strip():
            heuristica_feedback.append("⚠️ Output vacío en main → posible fallo lógico o flujo no ejecutado")
        if warnings_bucles:
            heuristica_feedback.append("⚠️ Riesgo de bucles infinitos detectado por AST")
        if warnings_atributos:
            heuristica_feedback.append("⚠️ Atributos usados sin asignar (self.X fantasma) detectados por AST")

        partes_reporte = list(errores_lista)
        if heuristica_feedback:
            partes_reporte.append("\n--- HEURÍSTICA (OBSERVABILIDAD) ---\n")
            partes_reporte.extend(heuristica_feedback)
        errores_reporte = "\n\n".join(partes_reporte)

        if es_nueva_mejor:
            mejor_version["errores_reporte"] = errores_reporte

        # Si este intento empeoró el score, se retoma la mejor versión conocida
        # para que el reflector corrija desde una base sólida, no desde la regresión.
        if not es_nueva_mejor and mejor_version["codigo"] is not None and metrics.global_score < mejor_version["score_global"]:
            print(
                f"⏪ Este intento empeoró el score global "
                f"({metrics.global_score:.2f} < {mejor_version['score_global']:.2f}). "
                "Se retoma la mejor versión conocida para corregirla."
            )
            CodigoActual = mejor_version["codigo"]
            if mejor_version["errores_reporte"]:
                errores_reporte = mejor_version["errores_reporte"]

        print("❌ Validación insuficiente. Iniciando fase de reflexión...")
        guardar_memoria(entrada_prompt, plan, CodigoActual, errores_reporte, "Por corregir", False)

        reflexion, CodigoActual = reflexionar_y_corregir(
            CodigoActual, errores_reporte, entrada_prompt, historial_errores
        )
        print(f"💡 Reflexión del Agente:\n{reflexion}")
        historial_errores.append(f"Errores:\n{errores_reporte}\nReflexión:\n{reflexion}")

        intentos += 1

    else:
        # El bucle while agotó todos los intentos sin break (sin éxito completo).
        if mejor_version["codigo"] is not None:
            print(f"📊 Usando mejor versión con score {mejor_version['score_global']}/10")
            CodigoActual = mejor_version["codigo"]

    # 5. Documentación final
    print("📝 Generando comentarios y documentación final con Ollama...")
    documentacion = documentar_codigo(CodigoActual)
    documentacion = extraer_codigo_puro(documentacion)

    with open("CodigoFinal.py", "w", encoding="utf-8") as f:
        f.write(documentacion)
    print("📁 Código final y documentado guardado en CodigoFinal.py")

    # 7. Limpieza de directorios temporales del pipeline
    eliminadas = 0
    for d in pipeline_dirs:
        try:
            shutil.rmtree(d, ignore_errors=True)
            eliminadas += 1
        except Exception as e:
            print(f"⚠️ No se pudo eliminar la carpeta temporal {d}: {e}")
    print(f"🧹 Limpieza completada: {eliminadas}/{len(pipeline_dirs)} carpeta(s) temporal(es) de pipeline eliminada(s).")


if __name__ == "__main__":
    main()
