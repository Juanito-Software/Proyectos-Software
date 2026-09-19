---
description: Auditoría de coherencia de la documentación (enlaces, Markdown, contradicciones, duplicidades y fuentes de verdad). Por defecto solo inspecciona e informa; aplica correcciones únicamente si el usuario lo solicita.
agent: build
---

Comprueba la coherencia de la documentación del repositorio. Sigue este flujo:

```
INSPECCIONAR
    ↓
COMPARAR
    ↓
DETECTAR HALLAZGOS
    ↓
INFORMAR
    ↓
[solo si el usuario lo solicita]
APLICAR CORRECCIONES APROBADAS
    ↓
VALIDAR
```

## 1. Inspeccionar

Revisa como mínimo los documentos raíz (hoy `README.md`, `MAINTENANCE.md` —
única fuente consolidada — y `AGENTS.md`). Audítalos **siempre**, aunque revisar
esos documentos también sea tarea de `/CierreSesion` o de `/Write`: la
auditoría se solapa con ellos sin conflicto. Comprueba:

- enlaces internos y externos relevantes,
- referencias a archivos que realmente existan,
- encabezados y estructura Markdown,
- posibles contradicciones,
- información obsoleta evidente,
- duplicidades importantes,
- convenciones de documentación existentes,
- coherencia de las «fuentes de verdad»: cifras de tests y cobertura **solo** en
  `README.md` (los `minimo` de `ci.yml` son los que las aplican) y
  `MAINTENANCE.md` como única fuente consolidada del repo (ToDo + Roadmap +
  historial).
- **cifras al día**: cada proyecto con tests documenta su cifra en su propio
  `README.md` (p. ej. BatchProcessor 20, RadioStack 166 —o 155 sin
  `RADIOSTACK_DB_TESTS`—, FastAPI TaskHub 55, gym-app 41,
  TaskHub_Angular backend 175 / frontend 103, TaskHub_React 983) y el global
  `README.md` las consolida en la tabla «Tests que se ejecutan hoy en cada
  push» y en la suma total («Suman … tests»). Comprueba que esas cifras
  coinciden con el conteo real de tests (informes de CI si hay resultados, o el
  conteo de `<testcase>` de Surefire / `vitest-report.xml` /
  `pytest-report.xml` / `phpunit-report.xml` en la última ejecución) y con los
  `minimo` declarados en `ci.yml`. Una cifra obsoleta es un hallazgo.

## 2. Comparar y detectar hallazgos

Cruza lo inspeccionado con el estado real del repositorio (código, workflows,
comandos, git…) y detecta los problemas. Identifica para cada hallazgo:

- archivos afectados,
- gravedad o importancia,
- y qué corrección resolvería el problema.

## 3. Informar

Entrega un informe claro con los problemas encontrados y las propuestas de
corrección. **La ejecución normal no modifica archivos.**

Solo si el usuario pide explícitamente aplicar los hallazgos o (p. ej. invocando
la variante `/VerificarDocs_Validado`, en la que la invocación es el permiso):

1. identifica exactamente qué hallazgos se van a aplicar,
2. modifica únicamente los archivos afectados,
3. limítate a los hallazgos aprobados: no hagas refactors documentales
   adicionales,
4. valida las modificaciones,
5. informa exactamente qué archivos modificó,
6. no realices operaciones Git automáticamente.

`/VerificarDocs` es **auditor**: revisa y toca los documentos raíz (entre ellos
`MAINTENANCE.md` y `AGENTS.md`) en cada auditoría, aunque eso se repita con el
trabajo de `/CierreSesion` — revisar es su tarea; no debe saltarse esos
documentos por miedo a solaparse. Es **no escritor**: no los usa como memoria
general. La **memoria persistente del agente** (entradas fechadas y estado
`[x]` del ToDo en `MAINTENANCE.md`, y comportamiento/conocimiento en
`AGENTS.md`) es responsabilidad directa de `/CierreSesion`, no de `/Write`:
`/Write` solo registra durante la conversación lo que `/CierreSesion` consolida
al cerrar.