---
description: Auditoría de coherencia de la documentación (enlaces, Markdown, contradicciones, duplicidades y fuentes de verdad). Informe sin cambios automáticos.
agent: build
---

Comprueba la coherencia de la documentación del repositorio. Revisa como mínimo
los documentos de la raíz que existan (hoy `README.md` y `MAINTENANCE.md`, única
fuente consolidada).

Comprueba:

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

No hagas cambios automáticamente salvo que el usuario lo indique expresamente.
Mantén actualizados el **ToDo** (su sección consolidada en `MAINTENANCE.md`), el
**Maintenance** (`MAINTENANCE.md`) y el **AGENTS.md** con los hallazgos de la
auditoría: entradas fechadas, tareas nuevas o resueltas y referencias.

Al finalizar, proporciona un informe claro con:

- problemas encontrados,
- archivos afectados,
- gravedad o importancia de cada problema,
- y posibles acciones para corregirlos.