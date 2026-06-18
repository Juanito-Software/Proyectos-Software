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

OLLAMA_MODEL = "codegemma:7b-instruct"
TIMEOUT_EJECUCION = 30
TIMEOUT_ARRANQUE = 10
SCORE_MINIMO_EXITO = 8

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

def build_refactor_prompt(code_snippet):
    instrucciones = (
        "Corrige y refactoriza el siguiente código Python.\n"
        "- Asegúrate de que no tenga errores de ejecución.\n"
        "- Mejora la legibilidad y mantenibilidad.\n"
        "- Devuelve solo el código Python corregido, sin comentarios ni explicación.\n"
        "\n```python\n" + code_snippet.strip() + "\n```"
    )
    return instrucciones

def build_debug_prompt(codigo: str, informe: str, historial_errores: list[str]) -> str:
    historial_txt = ""
    if historial_errores:
        previos = "\n---\n".join(historial_errores[-3:])
        historial_txt = f"\n\nErrores previos en intentos anteriores:\n{previos}"

    return (
        "# --- INSTRUCCIONES PARA DEPURAR EL SIGUIENTE CÓDIGO ---\n"
        "Analiza el error de ejecución.\n"
        "Devuelve una versión corregida del código.\n"
        "Mantén la estructura original.\n"
        "No introduzcas dependencias nuevas.\n"
        "Prioriza estabilidad sobre optimización.\n"
        f"\n```python\n{codigo}\n```\n\n"
        f"Informe de ejecución:\n{informe}"
        f"{historial_txt}"
    )

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
    return score

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
    temp_dir = tempfile.mkdtemp(prefix="gptdevteam_")
    proceso = None

    try:
        script_name = os.path.basename(path)
        shutil.copy2(path, os.path.join(temp_dir, script_name))

        proceso = subprocess.Popen(
            ["python", "-I", "-u", script_name],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=_env_sandbox(),
        )

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
                stderr_parcial = "".join(stderr_lines)

            if exit_code is not None:
                break

            if elapsed >= startup_timeout and not stderr_parcial.strip() and stdout_parcial.strip():
                proceso.terminate()
                try:
                    proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proceso.kill()
                exit_code = 0
                motivo = "Arranque interactivo validado (salida sin errores en stderr)."
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
        exito = exit_code == 0 and score >= SCORE_MINIMO_EXITO

        return {
            "exito": exito,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "score": score,
            "motivo": motivo,
        }

    except Exception as e:
        return {
            "exito": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Error durante ejecución: {e}",
            "score": 0,
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
        f"Motivo: {resultado.get('motivo') or 'N/A'}\n"
        f"stdout:\n{resultado['stdout'] or '(vacío)'}\n"
        f"stderr:\n{resultado['stderr'] or '(vacío)'}"
    )

def ollama_generate(model: str, prompt: str):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        print("❌ Error al llamar a Ollama:", e)
        return ""

def documentar_codigo(codigo: str):
    prompt = (
        "Añade comentarios para el siguiente código Python:\n"
        "IMPORTANTE: Utiliza siempre # para los comentarios\n"
        f"Codigo a documentar:\n"+codigo.strip()
    )
    return ollama_generate(OLLAMA_MODEL, prompt)

def limpiar_docstring_inicial(codigo: str) -> str:
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
                    # Caso docstring de una línea tipo """texto"""
                    return '\n'.join(lineas[i + 1:]).lstrip()
        elif any(q in contenido for q in triple_quotes):
            if apertura_idx is None and cierre_idx is None:
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



def main():
    entrada_prompt = (
        "Recrea las mecánicas básicas del Tamagotchi original."
        "Que tenga diferentes estados de ánimo. "
        "que puedas recargar su energia alimentandolo."
        "que funcione por comandos. "
        "Importante mostrar una guía de uso al inicio del programa."
    )

    print("🧠 Generando código con CodeGemma (Ollama)...")

    prompt = (
        "Genera un script completo, limpio y funcional en Python\n"
        "IMPORTANTE: No incluyas comentarios, y si necesitas incluir alguno hazlo siempre mediante #\n"
        f"Objetivo del script:\n{entrada_prompt}"
    )

    generated_code = ollama_generate(OLLAMA_MODEL, prompt)
    # 🧹 Limpieza inicial
    generated_code = limpiar_docstring_inicial(generated_code)
    

    codigo_actual = generated_code
    max_intentos = 4
    intentos = 0
    prompt_depuracion = None
    historial_errores: list[str] = []
    mejor_version = {"codigo": None, "score": -1}
    validar_output = None  # opcional: str o callable(stdout) -> bool

    while intentos < max_intentos:
        full_prompt = prompt_depuracion or build_refactor_prompt(codigo_actual)

        codigo_mejorado = ollama_generate(OLLAMA_MODEL, full_prompt)
        codigo_ejecutable = extraer_codigo_puro(codigo_mejorado)
        codigo_ejecutable = limpiar_docstring_inicial(codigo_ejecutable)

        print("📦 Código ejecutable:\n", codigo_ejecutable)

        if not codigo_ejecutable.strip():
            print("⚠️ Código generado está vacío. Reintentando...")
            intentos += 1
            continue

        valido_ast, error_ast = validar_sintaxis_ast(codigo_ejecutable)
        if not valido_ast:
            print(f"❌ Error de sintaxis detectado (AST):\n{error_ast}")
            historial_errores.append(error_ast)
            prompt_depuracion = build_debug_prompt(codigo_ejecutable, error_ast, historial_errores)
            codigo_actual = codigo_ejecutable
            intentos += 1
            continue

        with open("codigo_actual.py", "w", encoding="utf-8") as f:
            f.write(codigo_ejecutable)

        print(f"🧪 Intento {intentos + 1}: ejecutando en sandbox...")
        resultado = ejecutar_codigo_py("codigo_actual.py", validar_output=validar_output)
        informe = formatear_informe_ejecucion(resultado)
        print(f"📊 Score: {resultado['score']} | Exit code: {resultado['exit_code']}")

        if resultado["score"] > mejor_version["score"]:
            mejor_version = {"codigo": codigo_ejecutable, "score": resultado["score"]}

        if resultado["exito"]:
            print("✅ Código ejecutado correctamente.")
            codigo_actual = codigo_ejecutable
            break

        print(f"❌ Ejecución insuficiente:\n{informe}")
        historial_errores.append(informe)
        prompt_depuracion = build_debug_prompt(codigo_ejecutable, informe, historial_errores)
        codigo_actual = codigo_ejecutable
        intentos += 1
    else:
        if mejor_version["codigo"]:
            print(
                f"📊 Usando mejor versión acumulada "
                f"(score {mejor_version['score']}/{SCORE_MINIMO_EXITO})."
            )
            codigo_actual = mejor_version["codigo"]

    print("📝 Generando documentación con CodeGemma...")
    documentacion = documentar_codigo(codigo_actual)
    documentacion = extraer_codigo_puro(documentacion)
    print("📘 Documentación generada:\n", documentacion)

    with open("CodigoFinal.py", "w", encoding="utf-8") as f:
        f.write(documentacion)
    print("📁 Código final guardado en CodigoFinal.py")

if __name__ == "__main__":
    main()
