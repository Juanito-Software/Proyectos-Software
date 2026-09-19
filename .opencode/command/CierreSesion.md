---
description: Cierra la sesión: resume los cambios, añade la entrada fechada en MAINTENANCE.md (sin duplicar si ya existe la de hoy), marca a [x] las tareas completadas del ToDo y registra en AGENTS.md el comportamiento/conocimiento relevante.
agent: build
---

Ejecuta el cierre de la sesión de trabajo siguiendo las convenciones del repo.

1. Revisa el trabajo realizado durante la sesión.
2. Resume brevemente los cambios realizados.
3. Registra la sesión en `MAINTENANCE.md`. Primero **inspecciona** el documento
   y comprueba si ya existe una entrada con la fecha de hoy (`## YYYY-MM-DD`):
   - si **no** existe: crea la nueva entrada con el formato y las convenciones
     existentes — `## YYYY-MM-DD — Título`, subsecciones `###`, bloque `---` al
     terminar, entrada más reciente al principio de la sección de entradas;
   - si **ya** existe: **no** crees una segunda entrada idéntica. Amplía la
     entrada existente únicamente si la nueva información aporta algo distinto
     (cambios realizados después de esa entrada, decisiones nuevas). Si todo lo
     relevante ya está registrado, no la toques: el cierre no debe duplicar.
4. Mueve a `[x]` las tareas completadas de la sesión en el ToDo consolidado (la
   sección superior de `MAINTENANCE.md`, `# TODO del repositorio
   (consolidado)`), dejando la referencia de la sesión (fecha y PR si lo hay).
   Si una tarea ya está en `[x]`, no la repitas.
5. No modifiques código ni archivos que no sean necesarios para registrar el
   cierre de sesión. `MAINTENANCE.md` y `AGENTS.md` son la **memoria
   persistente del agente** y son tu documento: registra aquí el cierre, sin
   inventar comportamiento ni conocimiento especulativo (eso lo registra
   `/Write` durante la conversación; tú consolidas).
6. Muestra al final un resumen de lo realizado.