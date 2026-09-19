---
description: Variante autorizada de /VerificarDocs. Audita la documentación y aplica directamente las correcciones de los hallazgos: invocar el comando es la autorización explícita de escritura, sin necesidad de pedirlo aparte.
agent: build
---

Variante de `/VerificarDocs` con permiso de escritura **implícito en la
invocación**: al ejecutar este comando el usuario autoriza a aplicar las
correcciones, de modo que no hace falta añadir nada como «VerificarDocs y te
permito escribir los datos».

Sigue el mismo flujo de auditoría que `/VerificarDocs`:

```
INSPECCIONAR
    ↓
COMPARAR
    ↓
DETECTAR HALLAZGOS
    ↓
INFORMAR (breve)
    ↓
APLICAR CORRECCIONES AUTORIZADAS
    ↓
VALIDAR
```

## 1. Inspeccionar

Revisa como mínimo los documentos raíz (hoy `README.md`, `MAINTENANCE.md` —
única fuente consolidada — y `AGENTS.md`). Audítalos **siempre**, aunque
revisar esos documentos también sea tarea de `/CierreSesion` o de `/Write`: la
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

## 2. Comparar y detectar hallazgos

Cruza lo inspeccionado con el estado real del repositorio (código, workflows,
comandos, git…) y detecta los problemas. Identifica para cada hallazgo:

- archivos afectados,
- gravedad o importancia,
- y qué corrección resolvería el problema.

## 3. Aplicar correcciones (autorizadas)

Presenta un resumen breve de los hallazgos y, a continuación, aplica las
correcciones:

1. modifica únicamente los archivos afectados por cada hallazgo,
2. limítate a los hallazgos detectados: no hagas refactors documentales
   adicionales,
3. si un hallazgo exige una decisión de contenido (no una corrección evidente),
   pregúntalo antes de escribir,
4. valida las modificaciones,
5. informa exactamente qué archivos modificó y qué cambió en cada uno,
6. no realices operaciones Git automáticamente.

## Límites

`/VerificarDocs_Validado` es un **corrector acotado**, no un escritor general:
revisa y toca los documentos raíz (entre ellos `MAINTENANCE.md` y `AGENTS.md`)
en cada auditoría, aunque eso se repita con el trabajo de `/CierreSesion`.
Como escritor solo modifica los archivos afectados por los hallazgos; no los
usa como memoria general. La **memoria persistente del agente** (entradas
fechadas y estado `[x]` del ToDo en `MAINTENANCE.md`, y
comportamiento/conocimiento en `AGENTS.md`) es responsabilidad directa de
`/CierreSesion`, no de `/Write`: `/Write` solo registra durante la conversación
lo que `/CierreSesion` consolida al cerrar.