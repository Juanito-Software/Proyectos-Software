# 🤖 GPTDevTeam - Equipo de Desarrollo Autónomo con IA Local

Sistema multi-agente de **generación autónoma de código** basado en modelos de lenguaje de código abierto ejecutados localmente (como **CodeLlama** con quantización GPTQ). Inspirado en el paradigma de MetaGPT, orquesta un flujo de trabajo de múltiples "agentes" IA que se encargan de diseñar, generar, revisar y mejorar código automáticamente.

---

## 🚀 Características

- **100% Local y Privado**: Los modelos de IA se ejecutan en tu propia máquina con soporte para GPU (CUDA). Ningún dato sale a internet.
- **Generación de código por turnos**: Un agente **Generador** produce el código base y un agente **Revisor** lo refactoriza y limpia automáticamente.
- **Basado en transformers cuantizados (GPTQ)**: Utiliza `auto-gptq` para cargar modelos pesados en tarjetas gráficas de gama media con poca VRAM.
- **Diagrama de flujo integrado**: El archivo `Diagrama.txt` documenta visualmente la arquitectura interna del pipeline de generación.
- **Compatible con MetaGPT**: Incluye el framework `MetaGPT` para extender las capacidades del equipo de agentes.

---

## 🛠️ Requisitos del Sistema

- **Python 3.10+**
- **GPU NVIDIA** con soporte CUDA (recomendado para inferencia rápida)
- Dependencias:
  ```
  transformers
  accelerate
  torch
  huggingface-hub
  optimum
  auto-gptq==0.4.2
  triton-windows<3.4
  ```

---

## 📦 Instalación

1. Instala PyTorch con soporte CUDA desde [https://pytorch.org](https://pytorch.org).
2. Instala el resto de dependencias:
   ```bash
   pip install -r requeriments.txt
   ```
3. Descarga el modelo de IA de tu elección desde [HuggingFace Hub](https://huggingface.co) (recomendado: `TheBloke/CodeLlama-7B-GPTQ`).

---

## 💻 Uso y Ejecución

```bash
cd GPTDevTeam
python GPTDevTeam.py
```

La aplicación solicitará un **prompt o descripción de la tarea de programación**. El equipo de agentes IA se encargará de:
1. **Generar** el código inicial a partir del prompt.
2. **Revisar** y refactorizar el código generado eliminando artefactos y docstrings innecesarios.
3. **Presentar** el código final listo para copiar y usar.

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
 Código Final Optimizado
```

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
