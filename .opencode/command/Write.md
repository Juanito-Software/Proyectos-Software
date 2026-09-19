---
description: (Sinónimo `write`) Marca información relevante de la conversación para guardarla en memoria persistente. Uso en el chat: /Activate.Command(write.message|chat).
agent: build
---

Sinónimo para gestionar la memoria persistente del proyecto. No es un comando
del shell ni de git: se invoca en el chat con cualquiera de estas sintaxis,
equivalentes:

- `/write` (o `/Activate.Command(write)`)
- `/write.message` (o `/Activate.Command(write.message)`)
- `/write.chat` (o `/Activate.Command(write.chat)`)

Cuando el usuario emita uno de estos, actúa según la variante:

- `/Activate.Command(write)` — almacena en memoria persistente la información
  más relevante de la conversación actual; queda a tu criterio qué guardar si
  no se especifica.
- `/Activate.Command(write.message)` — agenda solo lo que viene en el mismo
  mensaje que el comando.
- `/Activate.Command(write.chat)` — agenda el conjunto de la conversación.

La memoria persistente del repo son `AGENTS.md` (la guía del agente) y
`MAINTENANCE.md` (ToDo consolidado + historial). Tras guardar, confirma con:

✅ INFO updated