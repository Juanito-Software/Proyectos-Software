---
description: Cierra la sesión: resume los cambios, añade la entrada fechada en MAINTENANCE.md y marca a [x] las tareas completadas del ToDo.
agent: build
---

Ejecuta el cierre de la sesión de trabajo siguiendo las convenciones del repo.

1. Revisa el trabajo realizado durante la sesión.
2. Resume brevemente los cambios realizados.
3. Añade una nueva entrada fechada en `MAINTENANCE.md` siguiendo el formato y las
   convenciones existentes: `## YYYY-MM-DD — Título`, subsecciones `###`, bloque
   `---` al terminar, entrada más reciente al principio de la sección de
   entradas.
4. Mueve a `[x]` las tareas completadas de la sesión en el ToDo consolidado (la
   sección superior de `MAINTENANCE.md`, `# TODO del repositorio
   (consolidado)`), dejando la referencia de la sesión (fecha y PR si lo hay).
5. No modifiques código ni archivos que no sean necesarios para registrar el
   cierre de sesión.
6. Muestra al final un resumen de lo realizado.