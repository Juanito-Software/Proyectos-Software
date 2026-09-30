---

description: Actualiza el CV de Juan Bernáldez a partir del estado real del repositorio Proyectos-Software, aplicando una valoración profesional multicriterio (recruiter, technical recruiter, engineering manager, senior/tech lead y editor de CV), un posicionamiento Full Stack orientado a backend y criterios de evidencia técnica para decidir qué información merece el CV, redactarla en lenguaje profesional y recompilarla en LaTeX.
agent: build

---

Actualiza el CV profesional de Juan Bernáldez a partir del estado real del repositorio `Proyectos-Software`. No es un comando del shell ni de git: se invoca en el chat con `/ActualizarCV`.

Al ejecutarlo combina:

```text
COMPORTAMIENTO ACTUAL DE /ActualizarCV (análisis, comparación, recompilación)
+
VALORACIÓN PROFESIONAL DEL PERFIL
+
POLÍTICA DE POSICIONAMIENTO PROFESIONAL
```

No describas el proceso: ejecútalo.

Parámetro opcional `$1`: ruta alternativa al repositorio local. Si no se proporciona se usa la ruta por defecto:

* Ruta local (fuente primaria): `D:\Proyectos\Proyectos-Software`
* GitHub (fuente complementaria): `https://github.com/Juanito-Software/Proyectos-Software`

La ruta local es la fuente principal: contiene el código y los archivos en desarrollo. GitHub solo se usa como referencia complementaria cuando sea útil.

# PRINCIPIO FUNDAMENTAL

```text
Repositorio
    ↓
Evidencia técnica
    ↓
Análisis profesional
    ↓
Posicionamiento del perfil
    ↓
Filtro de relevancia
    ↓
Redacción de CV
    ↓
Validación
    ↓
Recompilación
```

Nunca esto:

```text
README → Copiar → Pegar → CV
```

El repositorio es la fuente de evidencia técnica.

El CV es una representación profesional, selectiva y estratégicamente organizada del perfil.

El comando debe decidir:

* qué información merece aparecer;
* qué información debe reformularse;
* qué información debe mantenerse;
* qué información debe eliminarse;
* qué información debe permanecer fuera;
* y cómo debe organizarse para que el perfil profesional se entienda rápidamente.

---

# POLÍTICA DE POSICIONAMIENTO PROFESIONAL

Esta política debe aplicarse permanentemente al actualizar el CV.

## Posicionamiento objetivo

El CV debe presentar a Juan Bernáldez como:

> **Desarrollador Full Stack orientado a backend, con especial fortaleza en Java/Spring y Python/FastAPI, y experiencia práctica en frontend con React y Angular.**

Este posicionamiento no significa que el candidato sea especialista exclusivo en Java o Python.

El perfil se caracteriza por haber construido proyectos reales utilizando diferentes stacks, arquitecturas y tecnologías.

La amplitud tecnológica debe presentarse como:

```text
AMPLITUD TECNOLÓGICA REAL
+
EVIDENCIA MEDIANTE PROYECTOS
+
NÚCLEO PROFESIONAL CLARO
```

No debe presentarse como una colección indiscriminada de keywords.

## Importante: amplitud no significa falta de foco

No interpretes automáticamente:

```text
muchas tecnologías
        ↓
reducir tecnologías
        ↓
perfil más profesional
```

La interpretación correcta es:

```text
muchas tecnologías
        ↓
determinar cuáles están realmente demostradas
        ↓
agruparlas por función
        ↓
establecer una jerarquía de presentación
        ↓
relacionarlas con proyectos
        ↓
mantener las relevantes sin inflar el CV
```

El objetivo no es convertir artificialmente el perfil en un "Java Developer exclusivamente".

El objetivo es que el lector entienda:

```text
Full Stack
    ↓
orientación backend
    ↓
Java/Spring + Python/FastAPI
    ↓
React + Angular
    ↓
Node/Express y otras tecnologías complementarias
```

---

# TECNOLOGÍAS DEMOSTRADAS Y TECNOLOGÍAS DECLARADAS

Diferencia siempre entre:

### Tecnología declarada

Una tecnología que aparece en la sección de habilidades.

### Tecnología demostrada

Una tecnología que además está respaldada por un proyecto, experiencia profesional o evidencia técnica suficiente.

Una tecnología demostrada mediante un proyecto relevante **no debe eliminarse simplemente porque el CV contenga muchas tecnologías**.

Por ejemplo:

```text
Angular
```

es una keyword.

Pero:

```text
TaskHub_Angular
→ Angular
→ Express
→ Prisma
→ PostgreSQL
→ SSR
→ controllers/services/repositories
→ Zod
→ 278 tests
→ CI
```

es evidencia técnica.

Lo mismo ocurre con:

```text
FastAPI
```

frente a:

```text
TaskHub FastAPI
→ FastAPI
→ SQLAlchemy
→ Pydantic
→ React
→ JWT
→ many-to-many
→ dependency injection
→ 55 tests
→ CI
```

Cuando exista este tipo de evidencia, prioriza utilizarla para respaldar la tecnología en lugar de eliminarla por exceso de keywords.

---

# JERARQUÍA DE PRESENTACIÓN TECNOLÓGICA

Esta jerarquía determina cómo organizar visualmente el perfil.

No representa niveles de seniority.

No significa que las tecnologías de una categoría inferior deban eliminarse.

## Núcleo principal

### Java / Spring

* Java
* Spring Boot
* Spring Batch

### Python / Backend

* Python
* FastAPI

## Full Stack

### Frontend

* React
* Angular
* TypeScript
* JavaScript

### Backend adicional

* Node.js
* Express.js
* SQLAlchemy
* Prisma
* Zod

## Complementarias

* Rust
* PHP/Laravel
* C# / Unity
* IA/LLM
* OpenCV
* YOLO
* Docker
* GitHub Actions
* etc.

Esta jerarquía es exclusivamente una herramienta de presentación.

No utilices etiquetas como:

* Básico
* Intermedio
* Avanzado
* Senior
* Experto

salvo que el usuario proporcione explícitamente esos niveles.

---

# REGLA DE NO ELIMINACIÓN AUTOMÁTICA

No elimines Angular, FastAPI, React, Node.js, Express, Prisma, SQLAlchemy u otras tecnologías demostrables simplemente para "hacer el CV más especializado".

Antes de eliminar una tecnología, comprueba:

1. ¿Está realmente utilizada?
2. ¿El uso es significativo?
3. ¿Existe un proyecto que la respalde?
4. ¿Ayuda a explicar el perfil?
5. ¿Puede integrarse de forma compacta?

Si las respuestas son favorables, intenta reorganizarla antes de eliminarla.

La solución a un exceso de tecnologías debe ser normalmente:

```text
organizar
+
agrupar
+
jerarquizar
+
condensar
```

y no:

```text
eliminar indiscriminadamente
```

---

# TASKHUB COMO EVIDENCIA FULL STACK

TaskHub tiene especial valor porque el mismo dominio ha sido implementado utilizando diferentes stacks.

Cuando sea relevante, conserva la existencia de:

### TaskHub React

```text
Node.js / TypeScript
Express
PostgreSQL
React
```

### TaskHub Angular

```text
Express
Prisma
PostgreSQL
Angular
SSR
Zod
```

### TaskHub FastAPI

```text
FastAPI
SQLAlchemy
Pydantic
React
```

TaskHub debe poder utilizarse para demostrar:

* desarrollo Full Stack;
* React;
* Angular;
* FastAPI;
* Node.js;
* Express;
* diferentes estrategias de persistencia;
* APIs;
* autenticación;
* testing;
* CI;
* arquitectura por capas;
* capacidad de trabajar con distintos stacks.

No reduzcas automáticamente TaskHub a una sola implementación si eso provoca que desaparezca evidencia profesional relevante de Angular, FastAPI, React o Node/Express.

La descripción debe seguir siendo compacta y adaptarse al espacio disponible.

---

# PROYECTOS CON MAYOR PRIORIDAD

Cuando el espacio del CV sea limitado, prioriza los proyectos que mejor demuestren capacidad profesional.

El siguiente orden es una guía de presentación y no una puntuación absoluta.

## 1. BatchProcessor

Debe utilizarse como evidencia especialmente relevante de:

* Java;
* Spring Batch;
* integración de datos;
* CSV;
* APIs REST;
* bases de datos;
* parametrización mediante configuración externa;
* múltiples rutas de integración;
* reflexión;
* ItemStream;
* testing;
* H2;
* CI.

Es especialmente útil porque conecta el perfil con problemas de integración y procesamiento de datos habituales en software empresarial.

## 2. RadioStack

Debe utilizarse para demostrar, cuando corresponda:

* Java;
* Spring Boot;
* arquitectura modular;
* JWT;
* HTTP;
* STOMP;
* comunicación en tiempo real;
* Flyway;
* testing;
* MockMvc;
* CI.

## 3. TaskHub

Debe utilizarse para demostrar:

* Full Stack;
* React;
* Angular;
* FastAPI;
* Node.js;
* Express;
* PostgreSQL;
* Prisma;
* SQLAlchemy;
* Pydantic;
* autenticación;
* testing;
* CI;
* arquitectura por capas.

Especialmente importante: no sacrificar sistemáticamente Angular o FastAPI solo para reducir el número de tecnologías.

## 4. MotorIndexado

Puede utilizarse como evidencia de:

* Rust;
* algoritmos;
* índice invertido;
* concurrencia;
* Rayon;
* Axum;
* Tokio.

Es un proyecto complementario que demuestra amplitud y profundidad técnica fuera del stack principal.

## 5. GPTDevTeam / OmniForge

Pueden utilizarse para demostrar:

* Python;
* LLM;
* LangChain;
* LangGraph;
* arquitectura multiagente;
* testing;
* sandbox/restricciones de ejecución.

No deben desplazar automáticamente a los proyectos principales de backend/full-stack cuando el espacio sea limitado.

## 6. gym-app

Puede utilizarse como evidencia adicional de:

* PHP;
* Laravel;
* Blade;
* autenticación/autorización;
* testing.

---

# PERFIL PROFESIONAL

El perfil debe comunicar inmediatamente qué tipo de desarrollador es el candidato.

Evita perfiles genéricos como:

> "Apasionado por la tecnología con conocimientos en múltiples lenguajes."

La dirección preferida es conceptualmente:

> **Desarrollador Full Stack orientado a backend, con experiencia práctica en Java/Spring Boot y Python/FastAPI, y desarrollo frontend con React y Angular. Experiencia construyendo APIs REST, sistemas de integración de datos, autenticación, persistencia, testing automatizado y CI/CD mediante proyectos propios y prácticas profesionales.**

La redacción puede mejorar con el tiempo si aparece nueva evidencia en el repositorio, pero debe conservar las ideas fundamentales:

* Full Stack;
* orientación backend;
* Java/Spring;
* Python/FastAPI;
* React;
* Angular;
* APIs;
* persistencia;
* testing;
* CI/CD;
* experiencia práctica.

No conviertas esta redacción en una plantilla rígida.

---

# HABILIDADES TÉCNICAS

La sección de habilidades debe ser compacta, organizada y compatible con ATS.

Como estructura de referencia:

```text
Backend: Java · Spring Boot · Spring Batch · Python · FastAPI · Node.js · Express.js · SQLAlchemy · Prisma · Zod

Frontend: React · Angular · TypeScript · JavaScript · HTML5 · CSS3

Bases de datos: PostgreSQL · MySQL · MongoDB

Testing / CI/CD: GitHub Actions · JUnit 5 · Vitest · Playwright · pytest · Flyway · Docker · Git · Linux

IA / LLM: LangChain · LangGraph · Ollama · OpenCV · YOLO

Otros: PHP/Laravel · Rust · C# · Unity
```

Esta lista es una referencia de posicionamiento actual.

No la conviertas en una lista obligatoria e inmutable.

Si el repositorio evoluciona:

* incorpora tecnologías nuevas cuando estén suficientemente demostradas;
* elimina tecnologías que dejen de ser relevantes o que ya no estén respaldadas;
* reorganiza categorías cuando sea necesario;
* no añadas tecnologías únicamente porque aparecen como dependencias secundarias.

---

# EXPERIENCIA PROFESIONAL

Las prácticas de Soincon constituyen experiencia profesional real y deben mantenerse visibles.

No las presentes como años de experiencia laboral ordinaria.

Tampoco las minimices frente a los proyectos personales.

La experiencia:

**Prácticas DAM — Desarrollador · Soincon**

debe poder demostrar, cuando corresponda:

* Spring Batch;
* APIs REST;
* bases de datos;
* CSV;
* Python;
* Git;
* Linux;
* entorno profesional.

Diferencia siempre:

```text
Experiencia profesional
≠
Prácticas
≠
Proyecto personal
≠
Proyecto académico
```

Nunca conviertas automáticamente un proyecto personal en experiencia laboral.

---

# AMPLITUD TECNOLÓGICA SIN INFLACIÓN

No presentes todas las tecnologías como si tuvieran exactamente el mismo peso.

No hagas:

```text
Java = Rust = Angular = YOLO = Laravel = Spring Batch
```

cuando el propio perfil demuestra una jerarquía natural.

Tampoco hagas lo contrario:

```text
Java/Spring
```

y elimines tecnologías importantes que forman parte real del perfil.

La solución es la jerarquización.

El CV debe comunicar:

```text
NÚCLEO
Java/Spring
Python/FastAPI

FULL STACK
React
Angular
Node/Express

COMPLEMENTARIAS
Rust
Laravel
IA/LLM
Docker
CI/CD
etc.
```

La presentación debe permitir que un recruiter identifique rápidamente el núcleo, mientras que un technical recruiter pueda comprobar la amplitud.

---

# CRITERIO PARA CONSERVAR O ELIMINAR INFORMACIÓN

Cuando debas decidir si una tecnología o proyecto permanece en el CV, utiliza:

> **¿Esta información ayuda a demostrar una capacidad profesional concreta y está respaldada por experiencia real o por un proyecto verificable?**

Si sí:

* no la elimines automáticamente;
* busca una forma compacta de integrarla;
* relaciónala con el proyecto que la demuestra cuando sea posible.

Si no:

* considera eliminarla;
* mantenerla fuera del CV;
* o dejarla únicamente en el repositorio.

La existencia de muchas tecnologías no justifica por sí misma eliminarlas.

La falta de evidencia o relevancia sí puede justificarlo.

---

# PROFUNDIDAD > CANTIDAD

La regla:

> **Profundidad > cantidad**

no significa:

> "Cuantas menos tecnologías haya, mejor."

Significa:

> **Es preferible mostrar tecnologías respaldadas por uso significativo y explicar mediante proyectos qué se hizo con ellas, antes que enumerar muchas tecnologías sin evidencia.**

Por tanto:

```text
Angular + proyecto demostrable
```

tiene más valor que:

```text
Angular
```

pero eso no significa que Angular deba desaparecer de Habilidades Técnicas.

La sección de habilidades y la sección de proyectos cumplen funciones diferentes:

* Habilidades → permiten identificar rápidamente el stack.
* Proyectos → proporcionan evidencia de que ese stack se ha utilizado.

Ambas deben complementarse.

---

# FASE 1 — LOCALIZAR REPOSITORIO Y CV

1. Verifica que existe la ruta local del repositorio (o `$1` si se pasó). Si no existe o está incompleta, usa la copia de GitHub como fuente complementaria (`gh` o el MCP github configurado) y notifícalo en el resumen final.

2. Localiza el CV inspeccionando el sistema de archivos; no asumas rutas ni nombres. Pista inicial: `C:\Users\User\Desktop\Curriculum`. Determina el formato real (LaTeX/TeX), la estructura y qué archivos fuente generan el PDF entregable.

3. El CV activo se identifica no por el nombre sino por la evidencia: última compilación, `AGENTS.md` adyacente, convención del proyecto y archivos fuente.

4. Si junto al CV existe un `AGENTS.md`, léelo antes de tocar nada.

---

# FASE 2 — ANALIZAR EL REPOSITORIO

1. Lee el README principal y úsalo como índice, no como única entrada.

2. Para los proyectos con valor potencial, inspecciona según aporte:

* README;
* estructura;
* dependencias;
* tests;
* código;
* arquitectura;
* documentación;
* infraestructura;
* CI;
* seguridad;
* configuración.

No analices todos los archivos indiscriminadamente.

3. Extrae información profesional relevante:

* proyectos nuevos;
* proyectos muy evolucionados;
* tecnologías relevantes;
* arquitecturas;
* patrones;
* funcionalidades;
* decisiones técnicas;
* cifras de tests;
* CI/CD;
* seguridad;
* despliegue;
* integración;
* persistencia.

---

# FASE 3 — ANALIZAR EL CV

Determina:

* formato;
* estructura;
* contenido;
* secciones;
* orden;
* tono;
* tecnologías;
* proyectos;
* experiencia;
* educación;
* mecanismo de compilación.

Identifica qué información ya representa los proyectos y qué capacidades están subrepresentadas.

---

# FASE 4 — COMPARAR Y DETECTAR CAMBIOS

Compara:

```text
REPOSITORIO ↔ CV
```

Detecta:

* proyectos nuevos;
* proyectos evolucionados;
* cambios importantes;
* tecnologías nuevas;
* arquitecturas;
* funcionalidades;
* conocimientos demostrables no representados;
* información obsoleta;
* duplicidades;
* incoherencias;
* tecnologías presentes en el CV pero sin evidencia suficiente.

Detectar algo no significa añadirlo automáticamente.

---

# FASE 5 — VALORACIÓN MULTICRITERIO

Evalúa desde estas perspectivas:

## Recruiter

* claridad;
* legibilidad;
* keywords;
* posicionamiento;
* rapidez de comprensión.

## Technical Recruiter

* stack;
* profundidad;
* proyectos;
* evidencia;
* GitHub;
* arquitectura;
* calidad técnica.

## Engineering Manager

* autonomía;
* aprendizaje;
* resolución de problemas;
* mantenimiento;
* ciclo de desarrollo;
* construcción de software real.

## Senior Developer / Tech Lead

Evalúa:

* fundamentos;
* OOP;
* SOLID;
* clean code;
* arquitectura;
* bases de datos;
* SQL;
* Git;
* testing;
* debugging;
* APIs/HTTP;
* Linux;
* Docker;
* seguridad;
* concurrencia;
* modularidad;
* mantenibilidad.

## Editor profesional de CV

Para cada pieza decide:

```text
AÑADIR
REFORMULAR
MANTENER
ELIMINAR
OMITIR
```

La decisión debe tener en cuenta también la política de posicionamiento profesional definida anteriormente.

---

# FASE 6 — COMPLEJIDAD APARENTE VS REAL

No evalúes proyectos por:

* cantidad de archivos;
* cantidad de tecnologías;
* cantidad de frameworks.

Diferencia:

```text
Complejidad aparente
        vs
Complejidad real
```

Para cada proyecto:

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
Valor profesional
```

---

# FASE 7 — TECNOLOGÍA ≠ COMPETENCIA

No confundas:

> "El proyecto utiliza X"

con:

> "El candidato tiene dominio profesional de X."

Que una dependencia aparezca en:

* `pom.xml`;
* `package.json`;
* `composer.json`;
* `requirements.txt`;
* etc.

no implica automáticamente que deba aparecer como competencia destacada.

Evalúa si el uso:

* es significativo;
* forma parte de la arquitectura;
* resuelve una necesidad real;
* demuestra conocimiento;
* es relevante para el perfil.

Sin embargo, cuando exista evidencia significativa, **no elimines la tecnología únicamente por reducir el número de keywords**.

---

# FASE 8 — EXPERIENCIA PROFESIONAL VS PROYECTOS

No confundas:

* años programando;
* experiencia profesional;
* prácticas;
* formación;
* proyectos personales;
* open source.

Nunca conviertas automáticamente un proyecto personal en experiencia laboral.

---

# FASE 9 — HECHO, INFERENCIA Y CONCLUSIÓN

Nunca inventes:

* experiencia;
* años;
* responsabilidades;
* logros;
* resultados;
* clientes;
* tecnologías;
* dominio.

Diferencia:

### HECHO

Respaldado directamente.

### INFERENCIA

Razonable pero no declarada.

### CONCLUSIÓN PROFESIONAL

Valoración técnica respaldada por evidencia.

El CV debe utilizar principalmente hechos y conclusiones profesionales justificadas.

---

# FASE 10 — CRITERIO PROFESIONAL

Prioriza:

* proyectos relevantes;
* arquitectura;
* tecnologías principales;
* funcionalidades;
* problemas resueltos;
* testing;
* APIs;
* persistencia;
* seguridad;
* automatización;
* CI/CD;
* diseño;
* conocimientos demostrables.

Evita:

* buzzwords;
* duplicidades;
* tecnologías triviales;
* detalles internos irrelevantes;
* exageraciones;
* afirmaciones sin respaldo.

Pero recuerda:

> **Evitar listas interminables no significa eliminar tecnologías demostrables arbitrariamente.**

---

# FASE 11 — REDACCIÓN PROFESIONAL Y ATS

No copies README.

Transforma la información en lenguaje de CV:

* conciso;
* natural;
* profesional;
* técnicamente preciso;
* orientado al valor;
* verificable.

Describe:

* qué se construyó;
* qué problema resuelve;
* tecnologías importantes;
* decisiones técnicas;
* capacidades demostradas.

ATS:

* keywords relevantes;
* estructura;
* legibilidad;
* información relevante.

Recruiter:

* debe entender rápidamente el perfil.

Hiring Manager:

* debe entender que las tecnologías están respaldadas por experiencia o proyectos.

---

# FASE 12 — PRESENTACIÓN Y REESTRUCTURACIÓN

El comando puede mejorar una descripción aunque no exista un cambio técnico nuevo si:

* mejora precisión;
* elimina ambigüedad;
* elimina buzzwords;
* mejora lectura;
* representa mejor la evidencia;
* mejora el posicionamiento.

Puede reorganizar la sección de habilidades si eso mejora la jerarquía del perfil.

Puede modificar el Perfil profesional si el posicionamiento actual no representa correctamente la evidencia del repositorio.

Puede reorganizar la selección de proyectos cuando un proyecto nuevo o evolucionado cambie significativamente qué capacidades son más representativas.

No conviertas esto en una reescritura completa innecesaria en cada ejecución.

---

# FASE 13 — PROTECCIÓN DEL CV

Antes de modificar:

* conserva información válida;
* mantén estructura y formato cuando sea razonable;
* evita cambios innecesarios;
* no elimines información solo porque no aparezca en README;
* no sustituyas experiencia profesional por proyectos;
* no inventes información;
* no elimines tecnologías demostrables únicamente por exceso de keywords;
* no sacrifiques evidencia importante de Full Stack para conseguir una falsa especialización.

Si no existen cambios relevantes:

```text
no modifiques el CV
```

---

# FASE 14 — CONTRADICCIONES

Si CV, README, código o documentación se contradicen:

* analiza el contexto;
* determina qué está respaldado;
* no inventes;
* no sobrescribas automáticamente;
* si no puede determinarse, conserva lo razonable e informa del problema.

---

# FASE 15 — APLICAR CAMBIOS Y RECOMPILAR

1. Realiza las ediciones en los archivos fuente.

2. Conserva el formato.

3. Si existen variantes del CV, actualízalas cuando corresponda.

4. Recompila con XeLaTeX siguiendo el método documentado.

Trampas típicas:

* Windows ignora mayúsculas en nombres;
* no hagas copias que se sobrescriban;
* si falta un paquete LaTeX, instálalo con `tlmgr`;
* no cambies la fuente declarada salvo necesidad real.

Valida:

* una página si el diseño exige una página;
* cero `Overfull`;
* cifras correctas;
* tecnologías correctas;
* ninguna afirmación sin respaldo;
* coherencia entre Perfil, Proyectos y Habilidades.

Si el CV desborda:

```text
1. eliminar redundancias
2. condensar redacción
3. reorganizar información
4. reducir detalles secundarios
5. solo después considerar eliminar información menos relevante
```

No sacrifiques automáticamente Angular, FastAPI, React u otras tecnologías demostrables únicamente para resolver un problema de espacio.

---

# FASE 16 — VALIDACIÓN FINAL DEL POSICIONAMIENTO

Antes de terminar, comprueba explícitamente:

### Identidad profesional

¿Se entiende rápidamente que el perfil es Full Stack orientado a backend?

### Núcleo

¿Java/Spring y Python/FastAPI tienen suficiente visibilidad?

### Frontend

¿React y Angular siguen estando representados si la evidencia los respalda?

### Amplitud

¿El CV demuestra que el candidato puede trabajar con diferentes stacks?

### Evidencia

¿Las tecnologías importantes aparecen respaldadas por proyectos o experiencia?

### Experiencia profesional

¿Las prácticas de Soincon siguen teniendo el peso correspondiente?

### Honestidad

¿No se han añadido niveles de dominio, años o responsabilidades inventadas?

### ATS

¿Las tecnologías relevantes son detectables?

### Lectura humana

¿Un recruiter puede entender el perfil rápidamente?

### Lectura técnica

¿Un technical recruiter o engineering manager puede identificar evidencia técnica real detrás de las keywords?

### Coherencia

¿El CV cuenta la misma historia que el repositorio?

---

# FASE 17 — RESUMEN FINAL

Si hubo cambios:

```text
CV actualizado correctamente.

Cambios realizados:

- ...
- ...
- ...

Criterio aplicado:

- Se ha priorizado evidencia técnica demostrable.
- Se ha mantenido el posicionamiento Full Stack orientado a backend.
- Se han conservado tecnologías relevantes respaldadas por proyectos.
- Se ha mantenido visible la experiencia con React y Angular cuando corresponde.
- Se ha mantenido visible la experiencia con FastAPI cuando corresponde.
- Se han priorizado Java/Spring y Python/FastAPI como núcleo del perfil.
- Se ha evitado convertir el CV en una lista indiscriminada de tecnologías.
- No se han añadido afirmaciones sin respaldo.
- Se ha conservado la distinción entre experiencia profesional y proyectos propios.
```

Si no hubo cambios:

```text
CV analizado correctamente.

No se han encontrado cambios relevantes que justifiquen modificar el CV.

No se han realizado modificaciones.
```

Si existe información ambigua:

```text
CV actualizado parcialmente.

Cambios realizados:

- ...

Revisión manual recomendada:

- ...
```

No describas el proceso interno completo. Ejecuta el comando y entrega únicamente el resultado y el resumen final.
