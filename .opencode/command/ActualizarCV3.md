---
description: Actualiza el CV de Juan Bernáldez a partir de la evidencia real del repositorio Proyectos-Software, aplicando una valoración profesional multicriterio y un posicionamiento orientado a puestos junior de Backend Java / Full Stack. Prioriza Java, Spring Boot, Spring Batch y TaskHub React, selecciona los proyectos según su valor profesional, preserva las tecnologías complementarias demostrables y recompila y valida el CV en LaTeX.
agent: build
---

# /ActualizarCV3

Actualiza el CV profesional de Juan Bernáldez a partir del estado real del repositorio `Proyectos-Software`.

No es un comando del shell ni de Git: se invoca en el chat mediante `/ActualizarCV3`.

Al ejecutarlo, combina:

```text
COMPORTAMIENTO DE ANÁLISIS, COMPARACIÓN Y RECOMPILACIÓN DEL CV
+
VALORACIÓN PROFESIONAL MULTICRITERIO
+
POSICIONAMIENTO BACKEND JAVA / FULL STACK
+
PRIORIZACIÓN DE PROYECTOS SEGÚN EVIDENCIA Y VALOR PROFESIONAL
+
OPTIMIZACIÓN PARA RECLUTADORES, RESPONSABLES TÉCNICOS Y ATS
```

**No describas el proceso: ejecútalo.**

Parámetro opcional `$1`: ruta alternativa al repositorio local.

Si no se proporciona:

- Ruta local, fuente primaria: `D:\Proyectos\Proyectos-Software`
- GitHub, fuente complementaria: `https://github.com/Juanito-Software/Proyectos-Software`
- Directorio inicial para localizar el CV: `C:\Users\User\Desktop\Curriculum`

La ruta local es la fuente principal porque contiene el estado de desarrollo más reciente. Utiliza GitHub como referencia complementaria cuando sea necesario.

No presupongas que las rutas, los nombres de archivos o la estructura del repositorio siguen siendo idénticos a los de ejecuciones anteriores. Inspecciona el entorno real.

---

# PRINCIPIO FUNDAMENTAL

```text
Repositorio
    ↓
Evidencia técnica verificable
    ↓
Análisis profesional
    ↓
Posicionamiento profesional
    ↓
Priorización de proyectos y tecnologías
    ↓
Redacción selectiva del CV
    ↓
Validación del contenido y del diseño
    ↓
Recompilación
    ↓
Inspección del PDF final
```

Nunca hagas esto:

```text
README → Copiar → Pegar → CV
```

El repositorio es la fuente de evidencia técnica. El CV es una representación profesional, concisa y estratégicamente organizada del candidato.

El comando debe decidir qué información añadir, reformular, mantener, eliminar u omitir. No debe limitarse a incorporar automáticamente todas las novedades del repositorio.

El objetivo no es enumerar todos los proyectos ni todas las tecnologías utilizadas. Es conseguir que el CV comunique con rapidez una identidad profesional coherente, respalde las competencias mediante evidencias concretas y resulte competitivo para puestos junior de Backend Java y desarrollo Full Stack.

---

# POLÍTICA DE POSICIONAMIENTO PROFESIONAL

Esta política debe aplicarse permanentemente en cada ejecución de `/ActualizarCV3`.

## Identidad profesional objetivo

El CV debe posicionar al candidato como:

**Desarrollador Backend Java / Full Stack, con experiencia práctica en Java, Spring Boot y Spring Batch, y desarrollo full stack con React, TypeScript, Node.js, Express y PostgreSQL.**

Esta formulación define la orientación profesional, no un nivel de dominio ni una categoría de seniority.

El perfil debe reflejar una orientación clara hacia backend Java sin ocultar las competencias full stack que estén respaldadas por proyectos reales.

No debe presentarse al candidato como experto en todos los stacks ni sugerir que domina todas las tecnologías al mismo nivel.

## Jerarquía tecnológica

### 1. Núcleo profesional: Java y Spring

Tecnologías prioritarias:

- Java.
- Spring Boot.
- Spring Batch.

La experiencia de prácticas y el proyecto BatchProcessor deben proporcionar la principal evidencia de esta orientación.

### 2. Desarrollo Full Stack prioritario

Tecnologías:

- React.
- TypeScript.
- Node.js.
- Express.
- PostgreSQL.

TaskHub React debe ser la principal evidencia de desarrollo full stack, diseño de APIs, persistencia, seguridad, testing y despliegue.

### 3. Tecnologías full stack complementarias

Tecnologías:

- Angular.
- SSR.
- PHP y Laravel.

Deben mantenerse visibles cuando su uso esté suficientemente respaldado y su inclusión aporte valor. No necesitan ocupar el mismo espacio que Java/Spring o TaskHub React.

### 4. Backend adicional

Tecnologías:

- Python.
- FastAPI.
- Flask.
- SQLAlchemy.
- Pydantic.

Inclúyelas de acuerdo con la evidencia real y su relevancia para la candidatura. No desplaces automáticamente los proyectos principales para darles más espacio.

### 5. Tecnologías complementarias y experimentales

Pueden incluirse, según su utilidad y el espacio disponible:

- LangChain y LangGraph.
- Sistemas multiagente y LLM.
- Ollama y Transformers/Hugging Face.
- Rust.
- C# y Unity.
- OpenCV y YOLO.
- Otras tecnologías demostrables del repositorio.

Estas tecnologías deben complementar la identidad profesional principal, no competir con ella por el protagonismo del CV.

La jerarquía establece prioridades de presentación, no niveles de conocimiento.

---

# REGLA DE EQUILIBRIO ENTRE ESPECIALIZACIÓN Y AMPLITUD

No interpretes automáticamente que un CV con muchas tecnologías es poco profesional.

Tampoco interpretes que toda tecnología demostrable merece ocupar una sección destacada.

La estrategia correcta es:

```text
Identificar tecnologías demostrables
            ↓
Determinar su relevancia profesional
            ↓
Agruparlas por función
            ↓
Establecer una jerarquía clara
            ↓
Relacionar las principales con proyectos
            ↓
Condensar las complementarias
            ↓
Eliminar únicamente lo que no aporte suficiente valor
```

La especialización se consigue mediante el posicionamiento, el orden y el peso relativo de la información, no necesariamente mediante la eliminación indiscriminada de tecnologías.

No presentes Java, Spring Batch, React, Angular, FastAPI, Rust, Laravel y YOLO como si tuvieran exactamente el mismo peso profesional.

Tampoco elimines tecnologías importantes solo para conseguir un CV artificialmente especializado.

---

# OBJETIVO DE CONTRATACIÓN

Prioriza las candidaturas para las que el perfil tenga correspondencia real con:

1. Desarrollador Backend Java Junior.
2. Desarrollador Java / Spring Junior.
3. Desarrollador Full Stack Junior con orientación backend.
4. Desarrollador Full Stack con React, TypeScript, Node.js y bases de datos.
5. Otros puestos junior compatibles con la experiencia y los proyectos demostrables.

El CV debe funcionar como documento general para conseguir entrevistas, sin convertirse en una candidatura especializada en cada stack existente.

Si el entorno contiene variantes del CV para distintas candidaturas, puedes actualizarlas cuando proceda, pero no generes documentos redundantes ni cambies la finalidad de cada variante sin una razón concreta.

No ejecutes búsquedas de empleo ni procesos de candidatura dentro de este comando.

---

# POLÍTICA DE PRIORIZACIÓN DE PROYECTOS

El orden siguiente es la prioridad general para el CV orientado a Backend Java / Full Stack. Debe aplicarse teniendo en cuenta la evidencia actual, la relevancia profesional, la claridad y el espacio disponible.

## 1. BatchProcessor — Proyecto principal de Backend Java

Motor genérico de integración de datos desarrollado en Java y Spring Batch (2024–2025).

Capacidades que deben evaluarse:

- Procesamiento de datos mediante componentes `ItemReader` e `ItemWriter` parametrizados.
- Nueve combinaciones de integración entre CSV, API REST y bases de datos.
- Resolución dinámica de entidades mediante reflexión y `Class.forName`.
- Validación de cabeceras CSV.
- Gestión de estado mediante `ItemStream`.
- Endpoint REST para componer dinámicamente `Job` y `Step`.
- Pruebas de integración end-to-end con H2.
- Veinte pruebas de integración declaradas, siempre que se confirmen en el estado real del proyecto.
- Integración de las pruebas en CI, si continúa implementada.

El CV debe priorizar lo que demuestra profesionalmente: Java, Spring Batch, procesamiento de datos, parametrización, integración entre sistemas, diseño de componentes y pruebas automatizadas.

No enumeres todos los detalles de implementación si no mejoran la comprensión del proyecto.

No afirmes atomicidad distribuida, transacciones entre sistemas heterogéneos ni garantías equivalentes si no están demostradas.

**Objetivo de redacción:** que un recruiter entienda rápidamente qué hace el motor y que un responsable técnico identifique la complejidad real de su implementación.

## 2. TaskHub React — Proyecto principal Full Stack

Aplicación de gestión de tareas desarrollada con React 18, TypeScript, Vite, Node.js, Express y PostgreSQL.

Esta es la variante prioritaria de TaskHub y debe recibir más espacio que las implementaciones Angular y FastAPI.

Evalúa y prioriza, según el espacio disponible:

- Backend organizado por capas.
- Consultas SQL parametrizadas y ausencia de ORM.
- APIs y persistencia con PostgreSQL.
- Autenticación y autorización con JWT, bcrypt y roles.
- Gestión de sesiones mediante refresh tokens rotativos en cookies HttpOnly.
- Detección de reutilización de tokens y revocación de la familia de sesiones afectada.
- Política CSP estricta y otras medidas de seguridad realmente implementadas.
- Pruebas automatizadas en varias capas.
- Pruebas end-to-end con Playwright.
- CI/CD con GitHub Actions.
- Análisis de código con CodeQL.
- Despliegue en Render con PostgreSQL en Neon.
- Comprobaciones posteriores al despliegue integradas en CI.
- Auditoría OWASP publicada.
- Demo en vivo.

Las cifras conocidas que deben verificarse antes de conservarse son:

- 962 pruebas automatizadas distribuidas en cuatro capas.
- Coberturas declaradas del 99,5 % y 97 %, sujetas a los umbrales de CI.
- Nueve jobs de CI/CD.

No atribuyas los porcentajes de cobertura a herramientas o componentes concretos sin comprobarlo. Verifica las cifras en la configuración, los informes o la documentación actual.

La descripción debe seleccionar las características que mejor demuestren capacidad de desarrollo Full Stack: arquitectura backend, diseño de API, SQL, seguridad, pruebas y despliegue.

No conviertas el proyecto en una lista extensa de funcionalidades. Elige las más relevantes.

No afirmes que el sistema está completamente protegido, carece de vulnerabilidades o garantiza seguridad absoluta. Las pruebas y las medidas implementadas no demuestran la ausencia de errores.

Conserva los enlaces reales existentes a:

- Repositorio.
- Demo en vivo.
- Auditoría OWASP publicada.

Localiza los enlaces en el CV original, los archivos del proyecto y la documentación. No inventes URLs ni sustituyas los enlaces existentes por otros genéricos.

## 3. Prácticas DAM — Soincon

Las prácticas realizadas en Soincon (2024) constituyen experiencia profesional real y deben mantenerse claramente diferenciadas de los proyectos personales.

La descripción debe reflejar, cuando esté respaldado por el CV y la documentación disponible:

- Desarrollo con Java y Spring Batch.
- Participación en procesos de integración entre CSV, APIs REST y bases de datos PostgreSQL/MySQL.
- Participación en componentes de lectura y escritura y en la parametrización de procesos.
- Serialización y deserialización JSON en Python.
- Uso de Git y Linux.

Prioriza las tareas efectivamente realizadas durante las prácticas.

No presentes BatchProcessor como si se hubiera desarrollado durante las prácticas. Es un proyecto personal posterior y debe describirse por separado.

Evita duplicar la misma descripción técnica en ambos apartados. Las prácticas deben comunicar el contexto profesional y las tareas realizadas; BatchProcessor debe mostrar la evolución técnica demostrable mediante un proyecto propio.

No inventes responsabilidades, resultados de negocio ni funciones que no estén respaldados.

## 4. TaskHub Angular — Proyecto complementario

Variante desarrollada con Angular 19, SSR, Node.js, Express, Prisma y PostgreSQL.

Puede demostrar:

- Desarrollo frontend con Angular.
- Renderizado del lado del servidor.
- Backend organizado mediante controllers, services y repositories.
- Validación con Zod.
- Autenticación JWT y refresh tokens.
- Pruebas con Vitest.
- Gestión de proyectos, tareas y miembros de equipos.

Verifica las características y cifras de pruebas actuales antes de incorporar métricas.

Debe ocupar menos espacio que TaskHub React. Utiliza una descripción compacta que comunique que se trata de otra implementación de la misma aplicación con un stack distinto.

No la describas como un proyecto completamente independiente si ello provoca repetición innecesaria de funcionalidades comunes.

Conserva el enlace real al repositorio.

## 5. GPTDevTeam — Proyecto experimental de IA

Pipeline experimental de desarrollo de software multiagente en Python (2026–actualidad).

Características conocidas que deben comprobarse:

- Seis agentes especializados: Planner, Coder, Tester, Juez, Reflector y Documentador.
- Modelos locales mediante Ollama y Transformers/Hugging Face.
- Entorno de ejecución controlado con límites de CPU y memoria.
- Validación mediante AST.

Preséntalo brevemente como un proyecto experimental de IA aplicada a la automatización del desarrollo de software.

No afirmes que garantiza mejoras continuas, produce siempre código correcto o es autónomo y fiable si esas propiedades no están demostradas.

Su objetivo en el CV es complementar el perfil con iniciativa y conocimientos de IA, no desplazar los proyectos principales.

## 6. OmniForge — Framework experimental de agentes de IA

Framework experimental de agentes de inteligencia artificial desarrollado en Python sobre LangChain y LangGraph (2026–actualidad).

Características que deben comprobarse:

- Orquestación de agentes capaces de planificar tareas y utilizar herramientas.
- Herramientas de interacción con el ordenador mediante acciones como ratón, teclado y navegador, de acuerdo con las capacidades realmente implementadas.
- Compatibilidad con modelos locales mediante Ollama y proveedores externos.

Descríbelo brevemente como un proyecto experimental de agentes de IA que utilizan herramientas para interactuar con el ordenador y automatizar tareas.

No lo presentes como un sistema de control total o ilimitado del PC, ni como una solución infalible o un producto estable si no se ha verificado.

Si el CV tiene espacio limitado, GPTDevTeam y OmniForge pueden aparecer en una misma sección de proyectos de IA, con descripciones diferenciadas y concisas.

## 7. TaskHub FastAPI — Proyecto adicional

Variante desarrollada con React 18, Vite, FastAPI, SQLAlchemy y Pydantic v2.

Características conocidas:

- Autenticación JWT.
- Etiquetas con relaciones many-to-many.
- Separación de esquemas de entrada y salida.
- Inyección de dependencias mediante `Depends()`.
- Pruebas con pytest y SQLite en memoria.

Inclúyela solo si aporta valor a la candidatura y cabe sin perjudicar la claridad, la legibilidad ni el espacio de los proyectos prioritarios.

Puede aparecer como variante adicional de TaskHub, sin repetir la descripción general de la aplicación.

Conserva el enlace real al repositorio si se incluye.

## 8. Proyecto PHP/Laravel

El proyecto Laravel puede aparecer si el espacio disponible lo permite y su inclusión mejora el perfil.

Antes de incluirlo, inspecciona el estado real del repositorio y confirma qué funcionalidades, arquitectura, persistencia y pruebas están implementadas.

No inventes características ni lo incluyas únicamente para añadir más tecnologías.

## 9. Otros proyectos

Evalúa proyectos como RadioStack, MotorIndexado, servidores HTTP/FTP en Python o Rust, Forge (`.fga`), SpringlessEasyBatcher, proyectos de visión por computador y otros que existan en el repositorio.

No los añadas automáticamente.

Un proyecto puede justificar su inclusión si demuestra una capacidad relevante que los proyectos principales no cubren suficientemente, o si mejora de forma concreta la candidatura para el puesto objetivo.

Si no cabe en el CV, conserva la posibilidad de que el proyecto siga disponible en el repositorio sin necesidad de describirlo en el documento.

---

# REGLAS DE SELECCIÓN Y DISTRIBUCIÓN DEL ESPACIO

El CV debe priorizar la evidencia que más contribuya a conseguir entrevistas para el objetivo profesional.

Distribución preferente:

1. Experiencia profesional y formación, claramente visibles.
2. BatchProcessor, como proyecto principal de backend Java.
3. TaskHub React, como proyecto principal Full Stack.
4. TaskHub Angular, cuando aporte valor y haya espacio.
5. GPTDevTeam y OmniForge, de forma breve y conjunta cuando resulte conveniente.
6. TaskHub FastAPI, Laravel y otros proyectos, únicamente cuando su inclusión esté justificada.

Este orden no debe aplicarse mecánicamente si el documento actual, la evidencia o las características del puesto aconsejan una variación razonable.

## Regla de capacidad demostrada

No sacrifiques detalles técnicamente valiosos de BatchProcessor o TaskHub React para incorporar más proyectos de menor relevancia.

Es preferible explicar bien dos proyectos sólidos que enumerar muchos stacks con descripciones superficiales.

Sin embargo, no elimines automáticamente Angular, FastAPI, Laravel u otras tecnologías demostrables si pueden mantenerse mediante una descripción breve, una referencia compacta o una categoría de habilidades.

Utiliza este orden para resolver problemas de espacio:

```text
1. Eliminar redundancias
2. Condensar frases
3. Eliminar detalles secundarios
4. Agrupar variantes relacionadas
5. Reorganizar secciones
6. Reducir el espacio dedicado a proyectos complementarios
7. Omitir los elementos menos relevantes
```

No reduzcas automáticamente el tamaño de fuente o el interlineado para introducir más contenido.

El objetivo preferente es un CV de una página si puede mantenerse legible y completo en lo esencial. Si la plantilla y la cantidad de evidencia importante hacen inviable una sola página sin sacrificar legibilidad, admite dos páginas bien organizadas antes que producir un documento comprimido.

No conviertas la regla de una página en una restricción que obligue a eliminar información profesional importante.

---

# HABILIDADES TÉCNICAS

La sección de habilidades debe ser compacta, compatible con ATS y coherente con los proyectos descritos.

Evalúa una organización semejante a esta:

```text
Backend principal: Java · Spring Boot · Spring Batch

Full Stack: React · TypeScript · Node.js · Express · PostgreSQL

Frontend adicional: Angular · JavaScript · HTML · CSS

Backend adicional: Python · FastAPI · Flask · SQLAlchemy · Pydantic

Bases de datos: PostgreSQL · MySQL · otras tecnologías verificadas

Testing / CI/CD: JUnit · Vitest · Playwright · pytest · GitHub Actions ·
CodeQL · Docker · Git · Linux

IA / LLM: LangChain · LangGraph · Ollama · Transformers/Hugging Face

Complementarias: PHP/Laravel · Rust · C# · Unity · OpenCV · YOLO
```

Esta estructura es orientativa, no una lista obligatoria.

Comprueba las tecnologías que se mantienen en el CV y su relevancia profesional. No añadas herramientas únicamente porque aparecen como dependencias indirectas o porque se hayan probado de manera trivial.

Tampoco elimines tecnologías respaldadas por proyectos relevantes solo porque la lista sea extensa. Intenta primero agruparlas y condensarlas.

No asignes niveles de dominio como «básico», «intermedio», «avanzado», «senior» o «experto» sin una justificación explícita y verificable.

---

# PERFIL PROFESIONAL

El perfil debe explicar con rapidez qué tipo de desarrollador es el candidato y qué puestos busca.

La dirección de referencia es:

> Desarrollador Backend Java / Full Stack, con experiencia práctica en Java, Spring Boot y Spring Batch, y desarrollo de aplicaciones full stack con React, TypeScript, Node.js, Express y PostgreSQL. Experiencia demostrable mediante prácticas profesionales y proyectos propios que incluyen integración de datos, APIs REST, persistencia, seguridad, pruebas automatizadas y CI/CD.

No copies esta redacción de manera rígida. Adáptala al contenido real del CV y al espacio disponible.

Comprueba que las tecnologías mencionadas en el perfil estén respaldadas por la experiencia o los proyectos que aparecen en el documento.

No introduzcas afirmaciones genéricas como «experto», «altamente especializado», «arquitecto de software» o «amplia experiencia profesional» si la evidencia no las justifica.

No utilices el perfil para enumerar todos los lenguajes y frameworks. Su función es establecer la identidad profesional y las competencias principales.

---

# EXPERIENCIA PROFESIONAL Y FORMACIÓN

Mantén visibles las prácticas DAM de Soincon y la formación reglada.

Formación conocida que debe verificarse en el CV original:

- Desarrollo de Aplicaciones Multiplataforma (DAM), IES Augusto G. de Linares, Santander (2022–2024).
- Sistemas Microinformáticos y Redes (SMR), mismo centro (2018–2021).
- Formación en Seguridad Informática de Nivel 3 del SEPE, Soincon (2021), verificando la denominación exacta y la duración que figuren en la documentación original.

No cambies las fechas ni los nombres oficiales sin evidencia.

Diferencia siempre:

```text
Experiencia profesional
≠
Prácticas profesionales
≠
Formación
≠
Proyectos personales
```

Los proyectos personales pueden demostrar capacidad técnica, pero no deben convertirse automáticamente en experiencia laboral.

---

# CRITERIO DE EVIDENCIA TÉCNICA

Toda afirmación nueva debe poder justificarse mediante alguna de estas fuentes:

- Código fuente.
- Tests.
- Configuración de CI/CD.
- Dependencias y configuración del proyecto.
- Documentación técnica contrastada con la implementación.
- Despliegue verificable.
- CV original o documentación profesional fiable.

Diferencia entre:

**HECHO:** información respaldada directamente.

**INFERENCIA:** interpretación razonable, pero no demostrada de forma directa.

**CONCLUSIÓN PROFESIONAL:** valoración de la competencia que demuestra una implementación real.

El CV debe utilizar hechos y conclusiones profesionales respaldadas. No presentes inferencias como hechos.

No inventes experiencia, años, responsabilidades, clientes, métricas, resultados de negocio, tecnologías, niveles de dominio ni garantías de seguridad.

No mantengas cifras de pruebas o cobertura que ya no coincidan con el estado actual del proyecto. Si no puedes verificarlas, omítelas o informa de la limitación en el resumen final.

No confundas una prueba automatizada con una garantía de ausencia de errores.

---

# FASE 1 — LOCALIZAR EL REPOSITORIO Y EL CV

1. Verifica la ruta local del repositorio o el parámetro `$1`. Si la ruta no existe o está incompleta, utiliza GitHub como fuente complementaria y explica la limitación en el resumen final.

2. Localiza el CV inspeccionando el sistema de archivos. No presupongas nombres ni rutas. Utiliza `C:\Users\User\Desktop\Curriculum` como pista inicial, no como ubicación garantizada.

3. Identifica el CV activo a partir de los archivos fuente, las últimas compilaciones, las convenciones del proyecto y la documentación disponible.

4. Si existe un `AGENTS.md` junto al CV, léelo antes de modificarlo. Respeta sus instrucciones de edición, compilación y validación.

5. Identifica qué archivos generan el PDF entregable y qué variantes del CV existen realmente.

# FASE 2 — ANALIZAR EL REPOSITORIO

1. Lee el README principal y úsalo como índice.

2. Inspecciona selectivamente los proyectos potencialmente relevantes. Examina los README específicos, la estructura, las dependencias, el código, las pruebas, la arquitectura, la documentación, la configuración, la seguridad, el despliegue y CI/CD cuando ayuden a demostrar competencias.

3. Comprueba el estado actual de BatchProcessor y TaskHub React antes de decidir qué características deben recibir mayor peso.

4. Inspecciona Angular, FastAPI, GPTDevTeam, OmniForge, Laravel y otros proyectos según su posible contribución al CV.

5. No inspecciones indiscriminadamente todos los archivos. Busca evidencia que permita tomar decisiones profesionales concretas.

# FASE 3 — ANALIZAR EL CV ACTUAL

Determina:

- Estructura y formato.
- Contenido y orden de las secciones.
- Perfil profesional.
- Experiencia y formación.
- Selección de proyectos.
- Habilidades técnicas.
- Enlaces existentes.
- Extensión y legibilidad.
- Método de edición y compilación.

Identifica qué capacidades están bien representadas, cuáles están infrarrepresentadas y qué contenido provoca repetición o diluye el posicionamiento.

# FASE 4 — COMPARAR REPOSITORIO Y CV

Compara el estado real del repositorio con el CV.

Detecta:

- Proyectos nuevos o evolucionados.
- Tecnologías relevantes que faltan.
- Características importantes que no se reflejan.
- Información obsoleta.
- Métricas que necesitan verificarse.
- Enlaces ausentes o incorrectos.
- Descripciones redundantes.
- Afirmaciones que no están respaldadas.
- Desajustes entre el posicionamiento y la evidencia.

Detectar una novedad no significa incorporarla automáticamente.

# FASE 5 — VALORACIÓN PROFESIONAL MULTICRITERIO

Evalúa el CV desde estas perspectivas:

**Recruiter**

- Claridad del perfil.
- Correspondencia con puestos junior de Backend Java y Full Stack.
- Lectura rápida.
- Jerarquía de tecnologías.
- Legibilidad y palabras clave.

**Technical Recruiter**

- Stack principal.
- Profundidad demostrable.
- Proyectos relevantes.
- Correspondencia entre tecnologías y evidencia.
- APIs, persistencia, testing, seguridad y CI/CD.

**Engineering Manager**

- Capacidad para construir software real.
- Resolución de problemas.
- Mantenimiento y calidad.
- Comprensión del ciclo de desarrollo.
- Evidencia de autonomía y aprendizaje, sin exageraciones.

**Senior Developer / Tech Lead**

- Fundamentos de programación.
- Java y Spring.
- Diseño de software y arquitectura.
- Bases de datos y SQL.
- APIs y HTTP.
- Testing y debugging.
- Seguridad.
- Modularidad y mantenibilidad.
- Concurrencia, cuando corresponda.

**Editor profesional de CV**

Para cada elemento, decide:

```text
AÑADIR
REFORMULAR
MANTENER
ELIMINAR
OMITIR
```

La decisión debe considerar el posicionamiento objetivo, la evidencia, el espacio disponible y el valor real para una candidatura.

# FASE 6 — COMPLEJIDAD REAL Y COMPETENCIAS DEMOSTRADAS

No valores un proyecto por la cantidad de archivos o frameworks.

Analiza:

```text
Problema
   ↓
Arquitectura
   ↓
Implementación
   ↓
Calidad y pruebas
   ↓
Tecnologías relevantes
   ↓
Competencias demostradas
   ↓
Valor profesional
```

No describas toda la complejidad técnica en el CV. Selecciona los elementos que mejor comuniquen la capacidad del candidato para un puesto junior.

# FASE 7 — REDACCIÓN Y ATS

Redacta en lenguaje profesional, natural, conciso y técnicamente preciso.

Cada descripción de proyecto debe priorizar, según corresponda:

- Qué se construyó.
- Qué problema resuelve.
- Qué tecnologías son centrales.
- Qué decisiones técnicas importantes se implementaron.
- Qué competencias demuestra.

Evita:

- Copiar el README.
- Listas extensas de funcionalidades.
- Buzzwords.
- Repetición entre proyectos.
- Afirmaciones absolutas.
- Descripciones genéricas.
- Métricas sin verificar.

Comprueba las palabras clave relevantes para ATS, pero no conviertas el CV en una acumulación artificial de términos.

El perfil, las habilidades y los proyectos deben complementarse: las habilidades permiten identificar el stack; los proyectos aportan la evidencia.

# FASE 8 — PROTECCIÓN Y COHERENCIA DEL CV

Antes de modificar:

- Conserva la información válida existente.
- Mantén la estructura y el diseño cuando sean razonables.
- Evita reescrituras completas innecesarias.
- No elimines información relevante solo porque no aparezca en el README.
- No sustituyas prácticas profesionales por proyectos personales.
- No elimines tecnologías demostrables únicamente por exceso de keywords.
- No sacrifiques la evidencia de BatchProcessor o TaskHub React para añadir proyectos secundarios.
- No inventes información para completar secciones.
- Conserva los enlaces reales existentes.

Si CV, README, código o documentación se contradicen, investiga antes de modificar. Si no es posible resolver la contradicción, evita introducir la afirmación dudosa e informa de ello en el resumen final.

# FASE 9 — PRESENTACIÓN Y EXTENSIÓN

Busca un CV de una página si el contenido puede mantenerse legible y profesional. Si no es viable sin comprimir excesivamente el documento, acepta dos páginas bien organizadas.

No sacrifiques legibilidad para cumplir artificialmente un límite de páginas.

Ante un problema de espacio, aplica este orden:

1. Eliminar redundancias.
2. Condensar la redacción.
3. Retirar detalles técnicos secundarios.
4. Agrupar variantes de TaskHub.
5. Reducir el espacio de proyectos complementarios.
6. Omitir proyectos de menor relevancia.
7. Considerar cambios de maquetación únicamente si mantienen la legibilidad.

No reduzcas automáticamente el tamaño de fuente o el interlineado.

# FASE 10 — APLICAR CAMBIOS Y RECOMPILAR

1. Modifica los archivos fuente del CV, no únicamente el PDF final.

2. Conserva el formato y las convenciones documentadas.

3. Actualiza las variantes del CV cuando existan y sea necesario, sin duplicar trabajo ni cambiar documentos que no correspondan.

4. Recompila con XeLaTeX siguiendo el método documentado en `AGENTS.md` o en los scripts existentes.

5. Respeta las peculiaridades del entorno Windows, incluidas las diferencias de mayúsculas en nombres de archivos. Evita operaciones que sobrescriban el PDF final accidentalmente.

6. Si falta un paquete LaTeX, sigue el método de instalación documentado o utiliza `tlmgr` de TinyTeX cuando corresponda. No cambies la fuente declarada salvo que exista un problema real.

7. Comprueba el resultado real de la compilación. No declares que el PDF se ha generado correctamente si no lo has verificado.

# FASE 11 — VALIDACIÓN DEL PDF

Después de compilar, valida el PDF producido.

Comprueba:

- Que el PDF existe y corresponde a los archivos fuente modificados.
- Que el contenido final refleja los cambios.
- Que no hay texto cortado, superpuesto ni fuera de página.
- Que los enlaces importantes se conservan y funcionan cuando puedan verificarse.
- Que las cifras y las tecnologías coinciden con la evidencia.
- Que no hay errores de compilación relevantes.
- Que no existen avisos `Overfull` sin resolver que afecten al diseño.
- Que el perfil profesional y los proyectos cuentan una historia coherente.
- Que la tipografía y el tamaño siguen siendo legibles.

Si es posible, inspecciona visualmente el PDF, además de comprobar el log y el texto extraído.

No afirmes que el diseño es correcto basándote exclusivamente en una compilación sin errores.

# FASE 12 — VALIDACIÓN FINAL DEL POSICIONAMIENTO

Antes de terminar, comprueba expresamente:

**Identidad profesional:** ¿se entiende que el candidato se orienta a Backend Java / Full Stack?

**Núcleo:** ¿Java, Spring Boot, Spring Batch y BatchProcessor tienen suficiente visibilidad?

**Full Stack:** ¿TaskHub React demuestra React, TypeScript, Node.js, Express, PostgreSQL, API, seguridad y testing sin exceso de detalle?

**Experiencia:** ¿las prácticas de Soincon permanecen visibles y separadas de los proyectos personales?

**Tecnologías complementarias:** ¿Angular, FastAPI y otras tecnologías demostrables se conservan cuando aportan valor y pueden integrarse de forma compacta?

**Proyectos experimentales:** ¿GPTDevTeam y OmniForge aparecen con un peso proporcionado?

**ATS:** ¿las palabras clave relevantes son detectables?

**Lectura humana:** ¿un recruiter puede comprender el perfil y los proyectos principales rápidamente?

**Lectura técnica:** ¿un responsable técnico puede identificar competencias reales detrás de las tecnologías declaradas?

**Honestidad:** ¿todas las afirmaciones, cifras y responsabilidades tienen respaldo?

**Coherencia:** ¿perfil, habilidades, experiencia y proyectos describen el mismo posicionamiento?

**Diseño:** ¿el PDF final es legible, está bien maquetado y no contiene desbordamientos relevantes?

Si alguna comprobación falla, corrige el problema cuando sea posible y vuelve a validar el resultado.

# FASE 13 — RESUMEN FINAL

No describas el proceso interno completo. Entrega únicamente el resultado y un resumen de las modificaciones.

Si hubo cambios:

```text
CV actualizado correctamente.

Cambios realizados:

- ...
- ...
- ...

Criterio aplicado:

- Se ha priorizado el posicionamiento Backend Java / Full Stack.
- Se ha dado prioridad a Java/Spring Batch y BatchProcessor.
- Se ha reforzado TaskHub React como proyecto principal Full Stack.
- Se ha mantenido visible la experiencia profesional de Soincon.
- Se han organizado las tecnologías según su relevancia profesional.
- Se han conservado las tecnologías complementarias demostrables cuando aportan valor.
- Se han evitado repeticiones y afirmaciones sin respaldo.
- Se ha preservado la estructura y la legibilidad del CV.

Validación:

- Fuente modificada: ...
- Compilación XeLaTeX: ...
- PDF inspeccionado: ...
- Incidencias pendientes: ...
```

Adapta los puntos a las operaciones realizadas. No afirmes que una comprobación se ha superado si no se ha ejecutado.

Si no hay cambios relevantes:

```text
CV analizado correctamente.

No se han encontrado cambios relevantes que justifiquen modificar el CV.

No se han realizado modificaciones.
```

Si hay información ambigua o una validación incompleta:

```text
CV actualizado parcialmente.

Cambios realizados:

- ...

Revisión manual recomendada:

- ...
- ...

Validación pendiente:

- ...
```

Indica las limitaciones reales de acceso, compilación o verificación. No ocultes fallos ni presentes una ejecución parcial como un resultado completamente validado.

---

# REGLA FINAL

`/ActualizarCV3` no debe maximizar el número de tecnologías, proyectos o líneas de contenido.

Debe maximizar la claridad del posicionamiento, la calidad de la evidencia profesional, la relevancia para puestos junior de Backend Java / Full Stack y la facilidad con la que un recruiter o responsable técnico puede identificar las competencias del candidato.

**Prioriza Java/Spring Batch y TaskHub React; conserva el resto de la amplitud tecnológica cuando aporte valor, sin convertir el CV en un catálogo de proyectos.**