---

description: Prepara una nueva tarea: recopila contexto y requisitos, entrega los comandos del usuario para crear la rama y espera confirmación antes de programar; al terminar entrega git subir.

agent: build

---

Inicia el protocolo de preparación de una nueva tarea con la rama `$1`.

**## FASE 1 — Preparación**

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

**## FASE 2 — Instrucción para crear la rama**

Después de la preparación, entrega exactamente el comando que debe ejecutar el
usuario:

```text
git nueva $1
```

`git nueva` es el alias del usuario que prepara la rama (actualiza `main`, poda
las ramas ya integradas y crea la rama). No lo sustituyas por otros comandos
salvo que el usuario lo pida.

**## FASE 3 — Recopilar requisitos**

Pregunta qué cambios quiere realizar en esta nueva tarea: objetivo,
comportamiento esperado, archivos afectados, restricciones, requisitos
funcionales y técnicos, criterios de aceptación, etc. Si el usuario ya ha dado
información suficiente, no hagas preguntas innecesarias.

**## FASE 4 — BLOQUEO OBLIGATORIO**

Una vez recopilada la información, DETENTE. NO debes:

* escribir código,
* modificar archivos,
* ejecutar migraciones,
* ejecutar refactorizaciones,
* crear commits,
* implementar la tarea,
* ni realizar ningún cambio relacionado con el desarrollo.

Debes esperar a que el usuario confirme explícitamente que ya ejecutó
`git nueva $1` y que la rama está creada (p. ej. «rama creada», «ya está
creada»). Hasta esa confirmación, la tarea queda en estado:

**ESPERANDO CONFIRMACIÓN DE RAMA**

El agente no crea la rama: eso lo hace el usuario. No asumas que la rama está
creada aunque el usuario haya preparado la tarea. No continúes automáticamente
tras mostrar el comando.

**## FASE 5 — Inicio del desarrollo**

Solo después de la confirmación de que la rama ya está creada:

1. Revisa de nuevo el estado de la rama.

2. Revisa el contexto de `MAINTENANCE.md` y el ToDo.

3. Comprueba que la rama actual sea la rama de la tarea.

4. Resume brevemente qué vas a implementar.

5. Comienza el desarrollo siguiendo las instrucciones del usuario.

**## FASE 6 — Final del desarrollo**

Cuando termines el desarrollo, actualiza la documentación pertinente entrega los comandos necesarios que debe ejecutar el usuario

para subir la rama, abrir o reutilizar el PR y programar el auto-merge en

squash:

```text
git add ""
git commit ""
git subir
```

**## REGLA GENERAL DE SEGURIDAD**

`NewTask` significa:

RECOPILAR REQUISITOS → ENTREGAR `git nueva $1` → ESPERAR CONFIRMACIÓN →

COMENZAR DESARROLLO → AL TERMINAR, DOCUMENTAR, ENTREGAR `git add "",  
git commit "" y git subir`.

El agente nunca crea la rama: la crea el usuario. La confirmación de que la
rama ha sido creada es obligatoria antes de cualquier modificación relacionada
con la nueva tarea.
