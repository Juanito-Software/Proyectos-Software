---
description: Fotografía del estado del repositorio: rama, git status, commits, ramas, PRs abiertos, ToDo y última entrada de MAINTENANCE. Solo lectura.
agent: build
---

Analiza el estado actual del repositorio y proporciona un resumen conciso.
No realices modificaciones: el objetivo es solo dar una fotografía fiable del
estado actual del proyecto.

Comprueba como mínimo:

- rama actual,
- estado de `git status`,
- commits recientes relevantes,
- ramas locales,
- ramas remotas relevantes,
- PRs abiertos si pueden consultarse desde el entorno (`gh pr list`),
- estado del ToDo (sección superior de `MAINTENANCE.md`),
- última entrada de `MAINTENANCE.md`,
- y cualquier cambio pendiente relevante para continuar el trabajo.