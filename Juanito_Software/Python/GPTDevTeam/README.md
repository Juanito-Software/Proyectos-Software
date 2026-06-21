# 🤖 GPTDevTeam — Equipo de Desarrollo Autónomo con IA Local

**Autor:** JuanitoSoftware
**Versión:** 2.0 (incluye `GPTDevTeam_v1.3.py` como versión anterior conservada en el repo)
**Licencia:** GNU GPL v3
**Plataforma:** Windows
**Lenguaje:** Python 3

---

## 🧾 Descripción

Sistema multi-agente de **generación, validación, ejecución y documentación autónoma de código Python**, basado enteramente en modelos de lenguaje open-source ejecutados localmente a través de **[Ollama](https://ollama.com/)**. Orquesta un pipeline donde varios "agentes" (Planner, Coder, Tester, Judge, Reflector, Documenter) se reparten el diseño, la generación, la corrección iterativa, el testeo en sandbox y la documentación final del código, de forma completamente local y privada — sin enviar nada a APIs externas.

A diferencia de versiones anteriores del proyecto, **GPTDevTeam ya no carga ningún modelo directamente en proceso** (no usa `transformers`, `auto-gptq` ni GPU propia): todo el trabajo de inferencia se delega a un servidor Ollama corriendo en `localhost:11434`.

---

## 🚀 Características

- 🔒 **100% local y privado**: los modelos corren vía Ollama en tu propia máquina. Ningún prompt ni código sale a internet.
- 🧠 **Pipeline multi-agente especializado**: cada rol (planificación, codificación, testing, evaluación, corrección, documentación) usa el modelo más adecuado para su tarea.
- 🔁 **Corrección iterativa con mejora monótona**: si una corrección empeora el score global, se descarta y se retoma la mejor versión conocida para seguir corrigiendo desde ahí.
- 🧪 **Sandbox de ejecución aislado**: el código generado y sus tests se ejecutan en un proceso aparte, con límites de CPU/memoria (`resource`) y un filtro de imports peligrosos (`safe_import`).
- 🧩 **Validación estática con AST**: detecta bucles infinitos, atributos usados sin asignar, y verifica que los tests generados solo usen símbolos de la API real del código.
- 🧾 **Tests autogenerados y autocorregidos**: el Tester LLM genera tests contra una API extraída estáticamente del código, y los corrige si violan esa API.
- 🗒️ **Memoria persistente**: cada intento (éxito o fallo) se guarda en `memory.json` para trazabilidad del proceso.
- ✍️ **Documentación automática**: el rol Documenter comenta el código final antes de guardarlo.
- 📐 **Diagrama de flujo integrado**: el archivo `Diagrama.txt` documenta visualmente la arquitectura interna del pipeline.
- 🧩 **MetaGPT incluido**: el repo incluye el framework MetaGPT (carpeta `MetaGPT/`) como referencia/extensión, aunque el pipeline actual no depende de él para funcionar.

---

## 🧱 Componentes Principales

| Componente | Función |
|---|---|
| Ollama (`qwen3:8b`) | LLM usado por los roles Planner, Judge, Reflector y Documenter |
| Ollama (`qwen2.5-coder:7b`) | LLM usado por los roles Coder y Tester |
| `requests` | Cliente HTTP para hablar con la API local de Ollama |
| Sandbox (`subprocess` + `resource` + `safe_import`) | Ejecución aislada y acotada del código/tests generados |
| `ast` | Validación sintáctica, extracción de API estática y heurísticas de seguridad del código generado |
| MetaGPT | Framework de agentes incluido para extender el pipeline (opcional, no requerido) |

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.10+
- **[Ollama](https://ollama.com/)** instalado y corriendo localmente en `localhost:11434`, con los modelos:
  ```bash
  ollama pull qwen3:8b
  ollama pull qwen2.5-coder:7b
  ```
- No se requiere GPU ni CUDA para el script orquestador en sí (el consumo de GPU/CPU lo gestiona Ollama internamente según cómo lo tengas configurado).

### Dependencias de Python

```
requests
```

El resto de módulos usados (`ast`, `json`, `os`, `re`, `subprocess`, `tempfile`, `textwrap`, `threading`, `time`, `shutil`, `runpy`, `importlib.util`, `dataclasses`, `typing`) son librería estándar de Python.

---

## 📦 Instalación

1. Instala [Ollama](https://ollama.com/) y arráncalo (debe quedar escuchando en `http://localhost:11434`).
2. Descarga los modelos usados por el pipeline:
   ```bash
   ollama pull qwen3:8b
   ollama pull qwen2.5-coder:7b
   ```
3. Crea el entorno virtual e instala las dependencias de Python:
   ```bash
   setup.bat
   ```
   o manualmente:
   ```bash
   python -m venv venv
   venv\Scripts\python -m pip install -r requirements.txt
   ```

---

## 📁 Estructura del Proyecto

```plaintext
GPTDevTeam/
├── GPTDevTeam_v2.0.py     # Versión actual del orquestador (pipeline completo)
├── GPTDevTeam_v1.3.py     # Versión anterior, conservada en el repo
├── Diagrama.txt           # Arquitectura visual del pipeline
├── requirements.txt       # Dependencias de Python
├── requirements-lock.txt  # Versiones exactas verificadas
├── memory.json            # Historial persistente de generaciones (se crea/actualiza en runtime)
├── CodigoFinal.py          # Código final generado y documentado (salida, se sobreescribe en cada ejecución)
├── MetaGPT/                # Framework MetaGPT incluido (opcional, no requerido por el pipeline)
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso y Ejecución

```bash
cd GPTDevTeam
python GPTDevTeam_v2.0.py "Descripción de la tarea de programación que quieres generar"
```

Si no se pasa ningún argumento, el script usa como ejemplo de prueba un Tamagotchi por consola con estados de ánimo (hambre, energía, felicidad, salud).

También puedes lanzarlo con:
```bash
run.bat
```
(ten en cuenta que `run.bat` activa el entorno virtual y ejecuta `GPTDevTeam.py`; si usas `run.bat` actualízalo para que apunte a `GPTDevTeam_v2.0.py`, o renombra/copia el script).

---

## 📐 Arquitectura del Pipeline (v2.0)

```
Usuario (Prompt)
       │
       ▼
 Planner (qwen3:8b) — genera el plan de diseño
       │
       ▼
 Coder (qwen2.5-coder:7b) — genera el código inicial a partir del plan
       │
       ▼
 ┌─────────────────────────────────────────────┐
 │ Bucle de corrección (hasta agotar intentos)  │
 │                                               │
 │  Validación AST → API estática → Tester      │
 │  (qwen2.5-coder:7b) → Sandbox (tests + main) │
 │  → Judge (qwen3:8b) → ¿score suficiente?     │
 │       │ no                                   │
 │       ▼                                       │
 │  Reflector (qwen3:8b) corrige el código      │
 │  (se conserva la mejor versión por score)    │
 └─────────────────────────────────────────────┘
       │
       ▼
 Documenter (qwen3:8b) — comenta el código final
       │
       ▼
 CodigoFinal.py — código funcional y documentado
```

---

## 🧩 Referencia de Funciones Principales

- `main()` — Orquestador general del pipeline completo
- `ollama_generate(model, prompt)` — Llama a la API local de Ollama y devuelve la respuesta
- `planificar_diseño(prompt)` — Rol Planner: genera el plan de diseño
- `generar_codigo_de_plan(prompt, plan)` — Rol Coder: genera el código a partir del plan
- `limpiar_docstring_inicial(codigo)` — Limpia docstrings mal formateados del código generado
- `extraer_codigo_puro(texto)` — Extrae bloques de código Python de la respuesta del LLM
- `extraer_api_estatica(codigo)` — Extrae la API pública (clases/funciones) del código generado
- `generar_tests(codigo, api)` / `generar_tests_corregir(...)` — Rol Tester: genera y corrige tests contra la API
- `validar_tests_vs_api(test_code, api)` — Valida estáticamente que los tests solo usen símbolos de la API real
- `ejecutar_codigo_py(...)` — Ejecuta código/tests en el sandbox aislado
- `evaluar_semantica(codigo, prompt, resultado_tests)` — Rol Judge: evalúa semánticamente el resultado
- `reflexionar_y_corregir(...)` — Rol Reflector: corrige el código a partir de los errores detectados
- `documentar_codigo(codigo)` — Rol Documenter: comenta y documenta el código final
- `guardar_memoria(...)` / `cargar_memoria()` — Persisten y leen el historial de generaciones en `memory.json`
- `detectar_bucles_infinitos_ast(codigo)` / `detectar_atributos_no_definidos(codigo)` — Heurísticas estáticas de robustez

---

## 📦 Salidas

- `CodigoFinal.py` — Código funcional y documentado (se sobreescribe en cada ejecución)
- `memory.json` — Historial de los últimos intentos (prompt, plan, código, errores, éxito/fallo)
- Logs en consola con el estado de cada etapa del pipeline y los scores de evaluación

---

## 🚨 Notas de Seguridad

- El código generado se ejecuta en un sandbox con límites de CPU/memoria y un filtro de imports, pero **no es un aislamiento de seguridad a nivel de sistema operativo** (no sustituye a una VM o contenedor).
- **No ejecutar el código generado sin revisión manual previa en entornos sensibles.**
- El sistema puede generar código no seguro si el prompt lo induce.
- Este software es de uso experimental/educativo y no garantiza código seguro en entornos de producción.

---

## 📚 Créditos de Modelos y Librerías

- Modelos LLM servidos localmente vía [Ollama](https://ollama.com/) (`qwen3:8b`, `qwen2.5-coder:7b`, modelos de Alibaba/Qwen).
- MetaGPT incluido bajo su propia licencia ([metagpt-oss](https://github.com/geekan/MetaGPT)).

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
