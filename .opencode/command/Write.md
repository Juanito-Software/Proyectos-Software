---
description: Comando real de opencode. Registra en AGENTS.md el comportamiento/conocimiento del agente que se quiera conservar entre sesiones; variantes por argumento message, chat o ninguna.
agent: build
---

Comando de opencode para gestionar el comportamiento/conocimiento persistente
del agente en `AGENTS.md`. Se invoca por su nombre en el chat, `/Write`, con un
argumento opcional:

- `/Write` — almacena la información más relevante de la conversación actual;
  queda a tu criterio qué guardar si no se especifica.
- `/Write message` — agenda solo lo que viene en el mismo mensaje que el
  comando.
- `/Write chat` — agenda el conjunto de la conversación.

Registra durante la conversación el comportamiento/conocimiento del agente en
`AGENTS.md`; la **memoria persistente** (consolidación al cierre de esa
información y las entradas fechadas de `MAINTENANCE.md`) es competencia de
`/CierreSesion`. Antes de escribir:

1. Analiza la información y comprueba si ya existe en `AGENTS.md`; no dupliques.
2. No registres información especulativa ni no confirmada.
3. Distingue entre REQUERIDO, NECESARIO, OPCIONAL y FUERA DE ALCANCE.
4. No modifiques documentos solo porque "podrían mejorarse".

No uses `MAINTENANCE.md` como memoria genérica: la escritura persistente es
competencia de `/CierreSesion` (entradas fechadas, estado de tareas y
consolidación en `AGENTS.md`) y de `/VerificarDocs` solo cuando el usuario
aplique la corrección de un hallazgo.

Confirma tras guardar con: ✅ INFO updated