# Juanito Software 2025

# GPTDevTeam
from transformers import AutoTokenizer
import subprocess
import threading
import requests
import torch
import os
import time
import re
import textwrap

from gptqmodel import GPTQModel
import huggingface_hub
print("huggingface_hub:", huggingface_hub.__version__)

import triton
print("triton:", triton.__version__)

print(f"CUDA disponible: {torch.cuda.is_available()}, versión: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Carga única del modelo CodeLlama GPTQ
model_id = "TheBloke/CodeLlama-7B-Python-GPTQ"
tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
model = GPTQModel.from_quantized(
    model_id,
    device="cuda:0",
    trust_remote_code=True
)

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

def codellama_generate(prompt: str, max_tokens=2048):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.1,
        top_p=0.9,
        repetition_penalty=1.1
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def build_codellama_prompt(code_snippet):
    instrucciones = (
        "Corrige y refactoriza el siguiente código Python.\n"
        "- Asegúrate de que no tenga errores de ejecución.\n"
        "- Mejora la legibilidad y mantenibilidad.\n"
        "- Devuelve solo el código Python corregido, sin comentarios ni explicación.\n"
        "\n```python\n" + code_snippet.strip() + "\n```"
    )
    return instrucciones

def ejecutar_codigo_py(path):
    try:
        proceso = subprocess.Popen(
            ["python", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout_lines = []
        stderr_lines = []
        start_time = time.time()

        def leer_salida():
            for line in proceso.stdout:
                stdout_lines.append(line)
                if "Bienvenido al Tamagochi" in line:
                    proceso.terminate()  # Simula Ctrl+C en cuanto arranca
                    break

        hilo_salida = threading.Thread(target=leer_salida)
        hilo_salida.start()

        while hilo_salida.is_alive():
            hilo_salida.join(timeout=1)
            if time.time() - start_time > 60:
                proceso.kill()
                return False, "".join(stdout_lines), "Timeout: el programa tardó más de 60 segundos en iniciar."

        stdout, stderr = proceso.communicate(timeout=5)

        return True, "".join(stdout_lines) + stdout, stderr

    except subprocess.TimeoutExpired:
        proceso.kill()
        return False, "", "Timeout: ejecución demasiado larga."

    except Exception as e:
        return False, "", f"Error durante ejecución: {e}"

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
    return ollama_generate("codegemma:7b-instruct", prompt)

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

    print("🧠 Generando código con CodeLlama...")

    prompt = (
        "Genera un script completo, limpio y funcional en Python\n"
        "IMPORTANTE: No incluyas comentarios, y si necesitas incluir alguno hazlo siempre mediante #\n"
        f"Objetivo del script:\n{entrada_prompt}"
    )

    generated_code = codellama_generate(prompt, max_tokens=2048)
    # 🧹 Limpieza inicial
    generated_code = limpiar_docstring_inicial(generated_code)
    

    prompt = build_codellama_prompt(generated_code)
    codigo_actual = generated_code
    max_intentos = 4
    intentos = 0

    while intentos < max_intentos:
        if intentos > 0 and 'stderr' in locals():
            # Reutiliza el prompt de depuración anterior
            full_prompt = prompt
        else:
            full_prompt = build_codellama_prompt(codigo_actual)

        codigo_mejorado = codellama_generate(full_prompt, max_tokens=2048)
        codigo_ejecutable = extraer_codigo_puro(codigo_mejorado)
        codigo_ejecutable = limpiar_docstring_inicial(codigo_ejecutable)

        print("📦 Código ejecutable:\n", codigo_ejecutable)

        if not codigo_ejecutable.strip():
            print("⚠️ Código generado está vacío. Reintentando...")
            intentos += 1
            continue

        with open("codigo_actual.py", "w", encoding="utf-8") as f:
            f.write(codigo_ejecutable)
        
        print(f"🧪 Intento {intentos + 1}: ejecutando código...")
        exito, stdout, stderr = ejecutar_codigo_py("codigo_actual.py")

        if exito:
            print("✅ Código ejecutado correctamente.")
            codigo_actual = codigo_ejecutable
            break
        else:
            print(f"❌ Error en ejecución:\n{stderr}")
            prompt = (
                "# --- INSTRUCCIONES PARA DEPURAR EL SIGUIENTE CÓDIGO ---\n"
                "Corrige el error para que el código funcione correctamente.\n"
                f"\n```python\n{codigo_ejecutable}\n```\n\nError:\n{stderr}"
            )
            codigo_actual = codigo_ejecutable
            intentos += 1

    print("📝 Generando documentación con CodeGemma...")
    documentacion = documentar_codigo(codigo_actual)
    documentacion = extraer_codigo_puro(documentacion)
    print("📘 Documentación generada:\n", documentacion)

    with open("CodigoFinal.py", "w", encoding="utf-8") as f:
        f.write(documentacion)
    print("📁 Código final guardado en CodigoFinal.py")

if __name__ == "__main__":
    main()
