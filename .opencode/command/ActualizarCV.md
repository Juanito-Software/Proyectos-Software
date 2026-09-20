---
description: Actualiza el CV de Juan Bernáldez a partir del estado real del repositorio Proyectos-Software, aplicando una valoración profesional multicriterio (recruiter, technical recruiter, engineering manager, senior/tech lead y editor de CV) para decidir qué información merece el CV, redactarla en lenguaje profesional y recompilarla en LaTeX.
agent: build
---

Actualiza el CV profesional de Juan Bernáldez a partir del estado real del
repositorio `Proyectos-Software`. No es un comando del shell ni de git: se
invoca en el chat con `/ActualizarCV`.

Al ejecutarlo combina:

```text
COMPORTAMIENTO ACTUAL DE /ActualizarCV (análisis, comparación, recompilación)
+
VALORACIÓN PROFESIONAL DEL PERFIL (recruiter + engineering manager + tech lead + editor)
```

No describas el proceso: ejecútalo. Parámetro opcional `$1`: ruta alternativa al
repositorio local. Si no se proporciona se usa la ruta por defecto:

- Ruta local (fuente primaria): `D:\Proyectos\Proyectos-Software`
- GitHub (fuente complementaria): `https://github.com/Juanito-Software/Proyectos-Software`

La ruta local es la fuente principal: contiene el código y los archivos en
desarrollo. GitHub solo se usa como referencia complementaria cuando sea útil.

## Principio fundamental

```text
Repositorio → Evidencia técnica → Análisis profesional → Filtro de relevancia → Redacción de CV
```

Nunca esto:

```text
README → Copiar → Pegar → CV
```

El repositorio es la fuente de evidencia técnica. El CV es una representación
profesional y selectiva del perfil: el comando decide qué información merece
aparecer, cuál debe reformularse y cuál debe permanecer fuera.

## Flujo completo

El comportamiento sigue conceptualmente este flujo:

```text
/ActualizarCV
      ↓
Ejecutar el comportamiento actual existente
      ↓
Analizar repositorio local (README principal + proyectos)
      ↓
Identificar proyectos relevantes
      ↓
Inspeccionar código/documentación cuando sea necesario
      ↓
Extraer información técnica
      ↓
Analizar CV actual
      ↓
Comparar REPOSITORIO ↔ CV
      ↓
Detectar cambios
      ↓
Evaluar relevancia profesional
      ↓
Evaluar evidencia técnica
      ↓
Detectar sobrevaloraciones y subvaloraciones
      ↓
Seleccionar información relevante
      ↓
Redactar profesionalmente
      ↓
Actualizar CV
      ↓
Validar CV
      ↓
Mostrar resumen
```

Las fases siguientes implementan este flujo en detalle.

## Alcance de `/ActualizarCV`

Los criterios de recruiter técnico aquí definidos también podrán usarse en el
futuro por otras funcionalidades (entrevistas, preguntas técnicas, coding
interviews, evaluación de respuestas, simulaciones de procesos de selección,
análisis de ofertas). **Esas funcionalidades NO se ejecutan dentro de
`/ActualizarCV`.** Dentro de este comando úsalas única y exclusivamente para
aplicar los criterios de evaluación necesarios para mejorar el CV: no mantengas
una entrevista, no hagas preguntas técnicas ni simulaciones al ejecutarlo.

## FASE 1 — Localizar repositorio y CV

1. Verifica que existe la ruta local del repositorio (o `$1` si se pasó). Si no
   existe o está incompleta, usa la copia de GitHub como fuente complementaria
   (`gh` o el MCP github configurado) y notifícalo en el resumen final.
2. Localiza el CV **inspeccionando el sistema de archivos; no asumas rutas ni
   nombres**. Pista inicial: `C:\Users\User\Desktop\Curriculum`. Determina el
   formato real (LaTeX/TeX), la estructura y qué archivos fuente generan el PDF
   entregable. El CV activo se identifica no por el nombre sino por
   la evidencia (última compilación, `AGENTS.md` adyacente, convención del
   proyecto).
3. Si junto al CV existe un `AGENTS.md`, léelo antes de tocar nada: documenta el
   proceso de compilación, las cifras fuente y las trampas conocidas. Es parte
   del mecanismo de esta tarea, no documentación ajena.

## FASE 2 — Analizar el repositorio

1. Lee el README principal y úsalo como índice, no como única entrada.
2. Para los proyectos con valor potencial, inspecciona según aporte: README del
   proyecto, estructura, dependencias declaradas, tests (cifras), código y
   arquitectura relevante, documentación técnica e infraestructura/CI que
   demuestre criterio de ingeniería. También, cuando aporte: frameworks, bases
   de datos, APIs, testing, Docker, CI/CD, seguridad, patrones
   arquitectónicos, configuración y documentación técnica. No analices todos
   los archivos indiscriminadamente: usa criterio para localizar solo lo que
   pueda tener valor en el CV.
3. Extrae información profesional relevante: proyectos nuevos o muy
   evolucionados, tecnologías con relevancia real, arquitecturas y patrones,
   funcionalidades significativas, decisiones técnicas y cifras de tests.

## FASE 3 — Analizar el CV

- Determina formato, estructura y contenido actuales: secciones, orden, tono.
- Identifica la información profesional ya existente (experiencia laboral,
  educación, habilidades) y lo que ya cubre de los proyectos.
- Identifica el mecanismo de modificación y compilación existente y las trampas
  documentadas (p. ej. en `AGENTS.md`).

## FASE 4 — Comparar y detectar cambios

Compara el estado real del repositorio (FASE 2) con el CV (FASE 3) para
detectar:

- Proyectos nuevos que deberían añadirse.
- Proyectos existentes que hayan evolucionado significativamente.
- Cambios importantes en descripciones.
- Tecnologías nuevas con sentido real.
- Arquitecturas o patrones relevantes.
- Funcionalidades técnicamente significativas.
- Conocimientos demostrables no representados.
- Información del CV obsoleta, duplicada o a reformular.
- Posibles incoherencias entre el CV y el estado real del repositorio.

**Detectar algo no significa añadirlo automáticamente.** Toda información pasa
por el filtro de relevancia profesional de las fases 5 a 12 antes de tocar el CV.

## FASE 5 — Valoración con lente multicriterio

Evalúa el material detectado desde estas cinco perspectivas, por este orden:

**Recruiter** — ¿Se entiende rápido qué tipo de desarrollador es? Claridad,
legibilidad, keywords relevantes, coherencia del perfil, presentación.

**Technical Recruiter** — Stack tecnológico, profundidad demostrable,
proyectos, GitHub, arquitectura, calidad técnica, capacidad técnica
demostrable. ¿Las tecnologías citadas están respaldadas por evidencia en el
repositorio?

**Engineering Manager** — ¿Los proyectos demuestran capacidad de aprendizaje,
autonomía, resolución de problemas, mantenimiento de código, comprensión del
ciclo de desarrollo y construcción de software real? (No vale solo el código
que «funciona»; importa cómo se sostiene.)

**Senior Developer / Tech Lead** — Inspecciona con ojo técnico: fundamentos de
programación, OOP, SOLID, clean code, arquitectura, bases de datos/SQL, Git,
testing, debugging, APIs/HTTP, Linux, Docker, seguridad, concurrencia, calidad
de código, separación de responsabilidades, modularidad y mantenibilidad.
Separa lo sólido de lo anecdótico.

**Editor profesional de CV** — Sintetiza las cuatro ópticas y decide por cada
pieza de información: AÑADIR / REFORMULAR / MANTENER / ELIMINAR / OMITIR.
Para AÑADIR o REFORMULAR, exige evidencia suficiente.

## FASE 6 — Evaluación de proyectos: complejidad aparente vs real

No evalúes los proyectos por cantidad de archivos, tecnologías o frameworks.
Diferencia:

- **Complejidad aparente** (muchas tecnologías, muchos archivos, muchos
  frameworks) de
- **Complejidad real** (problema, arquitectura, persistencia, testing,
  seguridad, concurrencia, mantenibilidad, escalabilidad, diseño, integración).

Para cada proyecto potencialmente relevante recorre este pipeline:

```text
Problema
   ↓
Arquitectura
   ↓
Implementación
   ↓
Calidad
   ↓
Tecnologías
   ↓
Dificultad
   ↓
Competencias demostradas
   ↓
Valor profesional para el CV
```

El objetivo no es describir técnicamente todo el proyecto: es identificar
**qué demuestra profesionalmente** para un perfil junior.

## FASE 7 — Tecnología ≠ competencia; sobrevaloración y subvaloración

**No confundas** «el proyecto utiliza X» con «el candidato tiene dominio
profesional de X». Que una dependencia aparezca en `pom.xml`, `package.json`,
`composer.json` o `requirements.txt` no implica que deba figurar como
competencia destacada. Determina si el uso de cada tecnología: es significativo,
forma parte importante de la arquitectura, resuelve una necesidad real,
demuestra conocimiento, o es secundario, experimental o simplemente está
presente como dependencia.

**Sobrevaloración:** si el CV afirma algo que el repositorio no respalda (p. ej.
«Experto en Java» con uso básico, o «Experto en arquitectura de software» con
solo patrones básicos), **reformula** la afirmación para que represente
fielmente la evidencia. No inventes una justificación para mantenerla.

**Subvaloración:** si el repositorio demuestra una competencia relevante para un
perfil junior que el CV no representa suficientemente (p. ej. el CV dice
«Proyecto Java» y el repo muestra API REST, persistencia, Spring Boot,
seguridad, testing y arquitectura modular), no copies todo: determina qué
elementos bastan para comunicar mejor la capacidad técnica.

## FASE 8 — Experiencia profesional vs proyectos

No confundas años programando con años trabajando profesionalmente como
desarrollador. Diferencia correctamente: experiencia profesional, experiencia
freelance, prácticas, experiencia académica, proyectos personales, open source
y formación. **Nunca** conviertas automáticamente un proyecto personal en
experiencia laboral, ni atribuyas responsabilidades profesionales que no
existen.

## FASE 9 — Hecho, inferencia y conclusión profesional

Nunca inventes: experiencia profesional; años de experiencia; responsabilidades;
logros; resultados; métricas; clientes; conocimientos; tecnologías; dominio de
herramientas; experiencia laboral.

Si algo no puede demostrarse, **NO lo inventes**. Si existe una inferencia
razonable, trátala como inferencia y no como hecho.

Diferencia siempre:

- **HECHO** — respaldado directamente por el repositorio o la información
  profesional existente (p. ej. «el proyecto usa Spring Boot», «962 tests en
  CI, incluido Playwright»).
- **INFERENCIA** — razonable a partir de la evidencia, pero no declarada
  (p. ej. «muestra autonomía»). Si la usas, redáctala como inferencia o
  suavízala; no la presentes como hecho consumado.
- **CONCLUSIÓN PROFESIONAL** — valoración técnica de lo que la evidencia
  demuestra (p. ej. «capacidad demostrable de mantener una base de código con
  tests»). Acompáñala solo cuando la evidencia la sostenga.

En el CV usa hechos y conclusiones profesionales respaldadas; las inferencias
deben marcarse como tales o omitirse si no aportan.

## FASE 10 — Criterio profesional (editor técnico, perfil junior)

No copies el README al CV. Decide como editor técnico qué merece aparecer:

**Prioriza:** proyectos técnicamente relevantes; arquitectura de software;
tecnologías principales; funcionalidades significativas; problemas resueltos;
aplicación de buenas prácticas; testing; APIs; persistencia; seguridad;
automatización; diseño de software; decisiones técnicas relevantes;
conocimientos demostrables. Información que ayude a un recruiter o técnico a
entender rápido el perfil.

**Evita:** listas interminables de tecnologías; buzzwords; tecnologías usadas de
forma trivial o secundaria; tecnologías experimentales sin suficiente
relevancia; detalles internos sin valor profesional; duplicidades; información
irrelevante; descripciones excesivamente largas; jerga innecesaria;
exageraciones; afirmaciones sin respaldo.

Regla de oro: que una dependencia aparezca en `pom.xml`, `package.json`,
`composer.json`, etc. **no implica** que deba destacarse como competencia en el
CV. La decisión se basa en el contexto y la relevancia real, no en la presencia
del paquete.

**Profundidad > cantidad.**

## FASE 11 — Redacción profesional y ATS

**No copies el README.** Transforma la información en lenguaje profesional de
CV: concisa, natural, técnicamente precisa, orientada al valor, fácil de leer,
compatible con lectura rápida de recruiters y basada en hechos.

Al redactar, describe:

- Qué se construyó.
- Qué problema resuelve.
- Qué tecnologías importantes utiliza.
- Qué decisiones técnicas relevantes existen.
- Qué capacidad demuestra.

Evita fórmulas vacías: «Proyecto innovador y revolucionario…», «Gran
experiencia utilizando…», «Apasionado por…».

**ATS:** comprueba keywords relevantes, estructura, legibilidad, secciones e
información relevante.

**Recruiter:** debe quedar claro rápido quién soy, qué puesto busco, qué
tecnologías son relevantes, qué experiencia tengo, qué proyectos importan y qué
capacidades técnicas puedo demostrar.

**Hiring Manager:** debe entenderse que las tecnologías no son una lista de
keywords suelta, sino que están respaldadas por proyectos o experiencia real.

## FASE 12 — Mejoras de presentación justificadas

El comando puede mejorar una descripción existente **aunque no haya un cambio
técnico nuevo**, si la nueva redacción:

- representa mejor el proyecto;
- elimina ambigüedad;
- elimina buzzwords;
- mejora la precisión;
- mejora la lectura;
- refleja mejor la capacidad técnica demostrada.

No conviertas `/ActualizarCV` en una reescritura completa del documento en cada
ejecución. La modificación debe estar justificada por un criterio profesional
concreto y debe comprobarse contra el resto del CV (p. ej. que un cambio no
desborde la única página o no duplique información).

## FASE 13 — Protección del CV

Antes de modificar:

- Conserva la información válida existente.
- Mantén su estructura y formato siempre que sea razonable.
- Evita modificaciones innecesarias.
- No elimines información solo porque no aparezca en el README.
- No sustituyas experiencia profesional por información del repositorio.
- No reescribas secciones completas sin necesidad.
- No inventes información para rellenar secciones ni para sostener afirmaciones
  (ver FASE 9, «Hecho, inferencia y conclusión profesional»).

Si no existen cambios relevantes, **no modifiques el CV innecesariamente**.

## FASE 14 — Contradicciones

Si CV, README principal, READMEs de proyectos, código o documentación se
contradicen:

- No inventes una solución ni sobrescribas automáticamente.
- Analiza el contexto y determina qué información está respaldada por evidencia.
- Si no puede determinarse con seguridad, conserva la información existente
  cuando sea razonable e informa del problema en el resumen final en lugar de
  asumir.

## FASE 15 — Aplicar cambios y recompilar

1. Realiza las ediciones en los archivos fuente del CV conservando el formato
   (si aplica, actualiza también las variantes del CV, no solo la principal).
2. Recompila con XeLaTeX siguiendo el método documentado (puede estar en el
   `AGENTS.md` del CV). Trampas típicas a respetar:
   - Windows ignora mayúsculas en nombres: el PDF final y el producido por
     XeTeX pueden ser el mismo archivo; no hagas copias que se sobrescriban a
     sí mismas.
   - Si falta un paquete LaTeX, instálalo con `tlmgr` de TinyTeX.
   - No cambies la fuente declarada a menos que falle de verdad; si falla,
     resuélvelo y anótalo.
3. Valida el resultado:
   - Una página si el diseño lo exige en 1 página («Output written ... (1 page)»).
   - Cero desbordamientos (sin `Overfull` en el log).
   - Las cifras nuevas figuran realmente en el texto.
   - Si el CV desborda, la salida es recortar texto, no bajar más el
     interlineado.
   - Ninguna tecnología o afirmación añadida sin respaldo suficiente.

## FASE 16 — Resumen final

Indica claramente qué se ha hecho, con uno de estos formatos. **Si hubo
cambios:**

```text
CV actualizado correctamente.

Cambios realizados:
- Añadido proyecto RadioStack.
- Actualizada la descripción de TaskHub.
- Añadida experiencia demostrable con Spring Boot.
- Actualizada la sección de tecnologías.
- Mejorada la descripción técnica de un proyecto existente.
- Eliminadas referencias obsoletas.
- No se han añadido tecnologías secundarias sin suficiente relevancia.

Criterio aplicado:
- Se han priorizado competencias demostrables.
- Se han evitado tecnologías utilizadas de forma secundaria.
- No se han añadido afirmaciones que no estén respaldadas.
- Se ha conservado la estructura profesional del CV.
```

**Si no hay cambios relevantes, no modifiques:**

```text
CV analizado correctamente.

No se han encontrado cambios relevantes que justifiquen modificar el CV.

No se han realizado modificaciones.
```

**Si hay información ambigua o contradictoria sin resolver:**

```text
CV actualizado parcialmente.

Cambios realizados:
- ...

Revisión manual recomendada:
- Se ha detectado información contradictoria sobre ...
- No se ha modificado automáticamente para evitar introducir información no
  verificada.
```