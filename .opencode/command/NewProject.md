---
description: Prepara una nueva tarea: recopila contexto y requisitos, entrega los comandos del usuario para crear y subir la rama, y espera confirmación antes de programar.
agent: build
---

Inicia el protocolo de preparación de una nueva tarea con la rama `$1`.

## FASE 1 — Preparación

1. Interpreta `$1` como el nombre solicitado para la nueva rama.
2. Comprueba el estado actual del repositorio.
3. Comprueba que no haya cambios sin guardar o sin confirmar que puedan perderse.
4. Lee `MAINTENANCE.md` para conocer el contexto actual del proyecto.
5. Revisa el ToDo (sección superior de `MAINTENANCE.md`) y la documentación
   necesaria para comprender el estado actual.
6. **La creación de la rama NO la hace el agente**: siempre la hace el usuario
   con su flujo (`git nueva $1`). No ejecutes `git switch`, `git checkout -b` ni
   nada equivalente.
7. Indica claramente qué rama (`$1`) se va a usar para la tarea.

## FASE 2 — Instrucción para crear y subir la rama

Después de la preparación, entrega exactamente los comandos que debe ejecutar el
usuario, en este orden:

```text
git nueva $1
git subir $1
```

`git nueva` es el alias del usuario que prepara la rama (actualiza `main`, poda
las ramas ya integradas y crea la rama). `git subir` sube la rama, abre o
reutiliza el PR y programa el auto-merge en squash. No sustituyas ninguno por
otros comandos salvo que el usuario lo pida.

## FASE 3 — Recopilar requisitos

Pregunta qué cambios quiere realizar en esta nueva tarea: objetivo,
comportamiento esperado, archivos afectados, restricciones, requisitos
funcionales y técnicos, criterios de aceptación, etc. Si el usuario ya ha dado
información suficiente, no hagas preguntas innecesarias.

## FASE 4 — BLOQUEO OBLIGATORIO

Una vez recopilada la información, DETENTE. NO debes:

- escribir código,
- modificar archivos,
- ejecutar migraciones,
- ejecutar refactorizaciones,
- crear commits,
- implementar la tarea,
- ni realizar ningún cambio relacionado con el desarrollo.

Debes esperar a que el usuario confirme explícitamente que ya ejecutó
`git subir $1` y que la rama está subida (p. ej. «rama subida», «ya está
subida»). Hasta esa confirmación, la tarea queda en estado:

**ESPERANDO CONFIRMACIÓN DE RAMA**

El agente no crea ni sube la rama: eso lo hace el usuario. No asumas que la rama
está subida aunque el usuario haya preparado la tarea. No continúes
automáticamente tras mostrar los comandos.

## FASE 5 — Inicio del desarrollo

Solo después de la confirmación de que la rama ya está subida:

1. Revisa de nuevo el estado de la rama.
2. Revisa el contexto de `MAINTENANCE.md` y el ToDo.
3. Comprueba que la rama actual sea la rama de la tarea.
4. Resume brevemente qué vas a implementar.
5. Comienza el desarrollo siguiendo las instrucciones del usuario.

## REGLA GENERAL DE SEGURIDAD

`NewProject` significa:

RECOPILAR REQUISITOS → ENTREGAR `git nueva $1` y `git subir $1` → ESPERAR
CONFIRMACIÓN → COMENZAR DESARROLLO.

El agente nunca crea la rama: la crea y sube el usuario. La confirmación de que
la rama ha sido subida es obligatoria antes de cualquier modificación
relacionada con la nueva tarea.