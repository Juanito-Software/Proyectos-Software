# 🤖 GPTDevTeam — Equipo de Desarrollo Autónomo con IA Local

**Autor:** JuanitoSoftware 
**Versión:** 1.0 
**Licencia:** GNU GPL v3
**Plataforma:** Windows
**Lenguaje:** Python 3

---

## 🧾 Descripción

Sistema multi-agente de **generación, validación, ejecución y documentación autónoma de código Python**, basado en modelos de lenguaje de código abierto ejecutados localmente (**CodeLlama-7B-GPTQ**, **CodeGemma**). Inspirado en el paradigma de MetaGPT, orquesta un flujo de trabajo donde múltiples "agentes" IA se encargan de diseñar, generar, revisar, corregir iterativamente y documentar código de forma completamente local y privada.

---

## 🚀 Características

- 🔒 **100% local y privado**: los modelos se ejecutan en tu propia máquina con soporte GPU (CUDA). Ningún dato sale a internet.
- 🔁 **Generación iterativa con autocorrección**: genera código, detecta errores y se autocorrige hasta 4 veces usando el propio mensaje de error como prompt.
- ✍️ **Documentación automática**: usa CodeGemma (vía Ollama) para comentar y documentar el código final generado.
- ⚡ **Modelos cuantizados (GPTQ)**: carga modelos pesados en GPUs de gama media con poca VRAM mediante `auto-gptq`.
- 📐 **Diagrama de flujo integrado**: el archivo `Diagrama.txt` documenta visualmente la arquitectura interna del pipeline.
- 🧩 **Compatible con MetaGPT**: incluye el framework para extender las capacidades del equipo de agentes.

---

## 🧱 Componentes Principales

| Componente | Función |
|---|---|
| CodeLlama-7B-GPTQ | Modelo LLM cuantizado para generación y revisión de código |
| CodeGemma (Ollama) | LLM para documentación automática vía API local |
| Transformers (HuggingFace) | Tokenización y manipulación del modelo |
| Triton / Torch / CUDA | Infraestructura de ejecución en GPU |
| Subprocess / threading | Control de ejecución del código generado |
| MetaGPT | Framework de agentes para extender el pipeline |

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.10+
- **GPU NVIDIA** con soporte CUDA (recomendado para inferencia rápida)
- **RAM:** 16 GB recomendado · **VRAM:** 12 GB recomendado
- **[Ollama](https://ollama.com/)** corriendo localmente en `localhost:11434` con el modelo `codegemma:7b-instruct` disponible
- Acceso a internet opcional si los modelos ya están descargados

### Dependencias de Python

```
transformers
accelerate
torch
huggingface-hub
optimum
auto-gptq==0.4.2
triton-windows<3.4
requests
textwrap
```

---

## 📦 Instalación

1. Instala PyTorch con soporte CUDA desde [https://pytorch.org](https://pytorch.org).
2. Instala el resto de dependencias:
   ```bash
   pip install -r requeriments.txt
   ```
3. Descarga el modelo desde [HuggingFace Hub](https://huggingface.co) (recomendado: `TheBloke/CodeLlama-7B-GPTQ`).
4. Asegúrate de que Ollama esté corriendo con el modelo `codegemma:7b-instruct`.

---

## 📁 Estructura del Proyecto

```plaintext
GPTDevTeam/
├── GPTDevTeam.py        # Punto de entrada principal
├── main.py              # Orquestador del flujo de trabajo
├── Diagrama.txt         # Arquitectura visual del pipeline
├── requeriments.txt     # Dependencias
├── codigo_actual.py     # Código intermedio en ejecución/test
├── CodigoFinal.py       # Código funcional y documentado
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso y Ejecución

```bash
cd GPTDevTeam
python GPTDevTeam.py
```

La aplicación solicitará un **prompt o descripción de la tarea de programación**. El equipo de agentes se encargará del resto.

---

## 📐 Arquitectura del Pipeline

```
Usuario (Prompt)
       │
       ▼
 Agente Generador (CodeLlama GPTQ)
       │
       ▼
 Limpiador de Docstrings
       │
       ▼
 Agente Revisor / Refactorizador
       │
       ▼
 Ejecución y Validación automática
  (hasta 4 intentos de autocorrección)
       │
       ▼
 Documentación automática (CodeGemma)
       │
       ▼
 CodigoFinal.py — Código funcional y documentado
```

---

## 🧩 Referencia de Funciones Principales

- `main()` — Orquestador general del flujo de trabajo
- `codellama_generate(prompt)` — Genera código a partir de una instrucción
- `build_codellama_prompt(code)` — Construye prompts de refactorización
- `ejecutar_codigo_py(path)` — Ejecuta el código generado y verifica su funcionamiento
- `extraer_codigo_puro(texto)` — Limpia la salida del LLM extrayendo solo el código
- `documentar_codigo(codigo)` — Usa CodeGemma para comentar el código
- `limpiar_docstring_inicial(codigo)` — Elimina docstrings incorrectos o mal formateados

---

## 📦 Salidas

- `codigo_actual.py` — Código intermedio a ejecutar/testear
- `CodigoFinal.py` — Código funcional y documentado
- Logs en consola con el estado de cada intento de ejecución y errores detectados

---

## 🚨 Notas de Seguridad

- **No ejecutar el código generado sin revisión manual previa en entornos sensibles.**
- **El sistema puede generar código no seguro si el prompt lo induce.**
- Este software es de uso experimental/educativo y no garantiza código seguro en entornos de producción.

---

## 📚 Créditos de Modelos y Librerías

- Modelos LLM proporcionados por [TheBloke](https://huggingface.co/TheBloke) y [Google](https://github.com/google/codegemma).
- Transformers y HuggingFace Hub bajo licencia Apache 2.0.

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
