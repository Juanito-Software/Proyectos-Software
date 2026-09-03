# Historial de mantenimiento del repositorio

Registro de operaciones estructurales sobre el repositorio (no sobre el código
de los proyectos).

---

## Estado de las alertas de seguridad

> **Actualización 2026-08-30.** TaskHub_React es el primer proyecto desplegado
> públicamente y el primero con pipeline de CI propio. Cambia el criterio de
> descarte descrito más abajo: al estar en producción, sus alertas entran en el
> supuesto 1 y ninguna puede descartarse por ser un proyecto experimental.
> Detalle en la sección del 29 y 30 de agosto.

- **Dependabot:** 2 abiertas, ambas dependencias transitivas del build de
  Angular sin arreglo disponible (las únicas "correcciones" son retrocesos de
  versión). Se dejan abiertas a propósito para que GitHub las cierre cuando
  Angular actualice.
- **Secret scanning:** 4 alertas revisadas. Una era real (clave de API de
  Google, revocada y restringida a YouTube Data API v3), dos falsos positivos y una de
  código de terceros ya retirado.
- **Code scanning (CodeQL):** 69 alertas agrupadas en nueve familias de
  problemas, más una décima descubierta después. **246 cerradas, 10 abiertas**
  en el momento de escribir esto, y las 10 corregidas en el último commit a la
  espera de que CodeQL reanalice.

  Las familias abordadas: modo debug de Flask, exposición de información (Java y
  Python), falta de límite de peticiones, path traversal, XSS, criptografía
  débil, CSRF, enlace de sockets, validación de URL y registro de secretos en
  claro.

  **Matiz importante:** las familias se cerraron por grupos de ficheros, no
  siempre por repositorio. Al revisar las 10 restantes aparecieron dos casos de
  «familia dada por cerrada» que seguían vivos en ficheros que no se habían
  mirado: límite de peticiones en `unified-chat-widget` y `JSGameChat`, y
  exposición por excepción en `TestMail.py` y `rumble_server.py`. La lección es
  que **cerrar una familia significa cerrar la lista de alertas de esa familia,
  no garantizar que el patrón no exista en otro sitio**; lo segundo requiere
  buscar el patrón, no fiarse del listado.
- **Credenciales en código:** revisadas y retiradas las de
  `LeaderBoard_Unity` y `unified-chat-widget`. Ninguna quedaba detectable por
  el escáner automático; aparecieron leyendo el código.

---

## 2026-08-29 / 2026-08-30 — TaskHub_React: producción, auditoría y CI

Primer proyecto del monorepo desplegado y accesible públicamente:
**taskhub-react.onrender.com**. Servicio web en Render y PostgreSQL gestionado
en Neon, los dos en la región de Frankfurt (`eu-central-1`) para que las
consultas no crucen el Atlántico. Ambos en plan gratuito permanente.

El detalle que decidió el reparto: **el PostgreSQL gratuito de Render caduca a
los 30 días**. Para una demo enlazada desde un currículum eso significa que
quien la abra mes y medio después se encuentra un error. Neon no caduca, así
que la base de datos vive allí y Render solo ejecuta el proceso. Supabase se
descartó por el mismo motivo: pausa los proyectos tras 7 días sin actividad.

### De ficheros JSON a PostgreSQL

`d5780ab` — El almacenamiento eran dos ficheros JSON. En Render el disco es
efímero, así que cada despliegue habría borrado los datos: desplegar obligaba a
migrar.

Se escribió SQL a mano sobre el driver `pg`, sin ORM, con todos los valores
como parámetros. El único elemento estructural dinámico —qué columnas actualiza
un `UPDATE`— se resuelve con lista blanca, que es el patrón correcto cuando la
parametrización no es aplicable.

**Un fallo que el almacenamiento en ficheros escondía:** comprobar si un título
está repetido y escribirlo son dos operaciones. Con JSON, dos peticiones
simultáneas pasaban ambas la comprobación y creaban las dos tareas. Ahora lo
impide un índice único sobre `(user_id, LOWER(TRIM(title)))`, y el servicio
traduce el error `23505` de Postgres al mismo 409 de siempre en lugar de
devolver un 500.

**Lo que no salió como estaba previsto:** se dijo que el patrón repository
aislaría el cambio y que controllers y services no se enterarían. Fue cierto a
medias: el acceso a datos quedó encapsulado, pero el repositorio pasó de
síncrono a asíncrono y eso obligó a propagar `async`/`await` hacia arriba. El
patrón aísla *cómo* se accede a los datos, no que pasen a ser asíncronos.

El aislamiento de la suite dejó de ser una carpeta temporal y pasó a ser un
esquema de Postgres creado y destruido en cada ejecución, incluso si falla a
mitad.

### Un proceso para tres cosas

`06a084b`, `ca9068d` — El mismo Express sirve el cliente React compilado en
`/`, el playground en `/playground` y la API en `/api`. Las rutas desconocidas
devuelven el `index.html` para que decida el enrutador de React, salvo las de
`/api/`, que siguen devolviendo 404 en JSON: si no, un error de escritura en
una llamada devolvería HTML y el cliente fallaría al parsearlo.

El primer despliegue falló con `vite: not found`. Causa: Render define
`NODE_ENV=production` y npm omite entonces las devDependencies, donde están
Vite, TypeScript y tsx. Se resolvió forzando `--include=dev` en la instalación.

### Rate limiting inutilizado detrás del proxy

`f9abef2` — Con Render por delante, Express veía la IP del proxy en todas las
peticiones, así que `express-rate-limit` contaba a todos los visitantes como un
único cliente: un solo usuario activo podía agotar el límite para el resto.
Aparecía en los registros como `ERR_ERL_UNEXPECTED_X_FORWARDED_FOR`.

Se confía en **exactamente un salto**, no en `true`. Confiar en todos permitiría
a cualquiera falsificar `X-Forwarded-For` y saltarse el límite con una IP
inventada distinta en cada petición.

### Rol de administrador por semilla

`6befc84` — Rol `admin` que puede listar usuarios, borrarlos —arrastrando sus
tareas por la clave foránea— y consultar un resumen global.

**Solo se concede por semilla**, desde `ADMIN_USERNAME` y `ADMIN_PASSWORD` al
arrancar. No hay ningún camino desde la API pública: el registro fuerza `user`,
el repositorio no acepta el rol como parámetro y no existe endpoint de
promoción. Un test manda `role: "admin"` en el registro y comprueba que sale un
usuario normal.

Tres decisiones registradas por si se revisan más adelante:

- **El rol se lee de la base de datos en cada petición, no del JWT.** Si viajara
  en el token, retirarle el rol a alguien no surtiría efecto hasta que caducara,
  hasta siete días después.
- **403 y no 404**, al contrario que en las tareas ajenas. Allí el 404 evita
  confirmar que un recurso existe; aquí quien pregunta ya está autenticado y la
  existencia de una zona de administración no es un secreto. Queda así resuelta
  la incoherencia aparente entre proyectos: no es criterio cambiante, es que
  cada situación pide una respuesta distinta.
- **Un administrador no puede borrarse a sí mismo ni dejar la instancia sin
  administradores.**

### Auditoría de seguridad completa

Informe en `Juanito_Software/JS/React/TaskHub_React/docs/AUDITORIA_SEGURIDAD.md`.

Lo que estaba bien: cero inyecciones SQL en 16 consultas, aislamiento entre
usuarios correcto, ningún `innerHTML` ni `dangerouslySetInnerHTML` en el
cliente React, cero vulnerabilidades en las dependencias del servidor.

Hallazgos corregidos:

| Severidad | Problema | Corrección |
|---|---|---|
| **HIGH** | `JWT_SECRET` con valor por defecto publicado en el repositorio: si faltaba la variable, la aplicación arrancaba con una clave conocida y cualquiera podía firmar tokens | En producción se niega a arrancar sin secreto propio, y rechaza el de desarrollo y los de menos de 32 caracteres |
| **HIGH** | Sin CI: los tests solo corrían si alguien se acordaba | Pipeline de 8 jobs (ver más abajo) |
| MEDIUM | CORS abierto a cualquier origen | Lista de orígenes en `ALLOWED_ORIGINS`; en producción, ninguno externo por defecto |
| MEDIUM | Sin ninguna cabecera de seguridad | `helmet` con CSP a medida, compatible con los estilos y scripts en línea del playground |
| MEDIUM | `jwt.verify` sin restringir el algoritmo | `algorithms: ['HS256']` explícito, al firmar y al verificar |
| MEDIUM | `nanoid < 3.3.18` (transitiva de Vite) | `npm audit fix`; cliente y servidor a cero |
| LOW | Contraseñas de 6 caracteres mínimos | 8 como mínimo y 72 como máximo, que es lo que bcrypt tiene en cuenta |
| LOW | Estado, prioridad e id sin escapar en el playground | Escapados; ya no depende de que el esquema no cambie |
| LOW | `taskhub: file:..`, el paquete raíz como dependencia de sus propios subpaquetes | Retirada |

**Un bug real que solo apareció al escribir el test de regresión:** el filtro de
búsqueda parametrizaba correctamente —no había inyección posible— pero no
escapaba los comodines de `LIKE`. Buscar `%` devolvía todas las tareas y buscar
`50%` no encontraba ese texto. Se añadió `escapeLikePattern` con `ESCAPE`
explícito. **El comentario que había en el código afirmando lo contrario era
falso**, lo que ilustra por qué un comentario no sustituye a un test.

### Tests: de 37 a 229

| Capa | Antes | Ahora | Herramienta |
|---|---|---|---|
| End-to-end de API | 37 | **62** | Script propio contra Postgres real |
| Unitarios del servidor | 0 | **86** | Vitest |
| Componentes y servicios del cliente | 0 | **61** | Vitest + Testing Library |
| End-to-end de navegador | 0 | **20** | Playwright + Chromium |
| Cobertura | No medida | Umbrales que fallan el build | v8 |

Lo añadido cubre lo que la auditoría señaló como huecos: manipulación de tokens
(firma inválida, caducado, `alg: none`, sin `sub`, usuario inexistente,
formato inválido), regresión de inyección SQL con cargas reales, validadores,
escapado de comodines y campo calculado `completed`.

Con esto, TaskHub_React deja de ser el único de los tres TaskHub sin batería de
ataques a JWT — la tenía el de FastAPI y faltaba aquí.

**Los E2E de navegador destaparon un desajuste entre cliente y servidor que
ninguna otra capa podía ver:** el campo de contraseña del formulario tenía
`minLength={6}` mientras el servidor, tras subir el mínimo a 8 en esta misma
auditoría, rechazaba las de 7 caracteres. El formulario dejaba enviar y el
error llegaba después, sin que el usuario pudiera preverlo. Es exactamente el
tipo de fallo que solo aparece cuando algo prueba las dos mitades a la vez.

**Lecciones de la puesta a punto de Playwright**, por si sirven para los
próximos proyectos:

- Playwright **falla ante un selector ambiguo** en lugar de elegir el primero.
  Es lo correcto, pero obliga a acotar: "Alta", "Pendiente" o "En progreso"
  aparecen a la vez como distintivo de una tarjeta y como `<option>` de los
  desplegables de filtro. La solución es buscar dentro de un contenedor —el
  formulario, el `<li>` de la tarea— y localizar los distintivos por clase CSS
  en lugar de por texto.
- **Un checkbox controlado por React no cambia de estado hasta que responde la
  API**, así que `check()` falla siempre: comprueba el cambio justo después del
  clic. Con `click()` más una espera al distintivo se verifica además el viaje
  completo, que es una aserción más fuerte.
- **Dos pestañas del mismo contexto comparten `localStorage`**: para simular
  dos usuarios distintos hace falta un contexto de navegador independiente, no
  una pestaña nueva.
- Se sustituyeron las esperas por tiempo fijo (`waitForTimeout`) por esperas a
  que un elemento aparezca. Los tiempos fijos son la causa más común de tests
  que fallan de forma intermitente en CI, donde la máquina va más lenta.

Los umbrales de cobertura se fijaron **por debajo** de la medición real (35% de
sentencias, 40% de ramas). No son un objetivo, son un suelo: impiden que baje
sin que nadie se entere. Un umbral inalcanzable acaba desactivándose.

### Pipeline de CI

`.github/workflows/taskhub-react-ci.yml`, ocho jobs con filtro de rutas para
que solo se dispare cuando cambia este proyecto:

`static` (ESLint y TypeScript) · `server-unit` · `client-tests` con cobertura ·
`api-tests` contra un servicio de PostgreSQL 17 real · `e2e` con Chromium ·
`build` con `NODE_ENV=production`, que comprueba que el artefacto contiene
servidor, playground y cliente · `security` con `npm audit` · `ci-ok`, un job
único del que colgar la protección de rama sin tener que enumerar los demás.

**Política de auditoría:** solo bloquean las vulnerabilidades altas y críticas.
Con `--audit-level=moderate` el pipeline estaría en rojo permanente por
dependencias transitivas de herramientas de desarrollo, y un CI siempre en rojo
deja de mirarse. Las moderadas y bajas quedan para Dependabot.

Se añadió ESLint, que no existía en ningún paquete: TypeScript en el servidor,
reglas de hooks en el cliente. El criterio es señalar errores reales, no
cuestiones de formato.

### Política de contraseñas según NIST SP 800-63B Rev 4

Último cambio funcional de la tanda. Se revisó la política de contraseñas y se
añadió confirmación en el registro.

**Lo que exige la norma** (Revisión 4, julio de 2025):

- **15 caracteres mínimo** cuando la contraseña es el único factor de
  autenticación. El mínimo de 8 solo vale con MFA, que TaskHub no tiene, así
  que se subió de 8 a 15.
- **Prohibido exigir composición.** La Rev 4 pasó de desaconsejar a prohibir
  los requisitos de mayúsculas, números y símbolos. El motivo es que producen
  contraseñas predecibles: obligado a poner una mayúscula, casi todo el mundo
  la pone la primera; obligado a un número, casi todo el mundo pone un `1` o el
  año al final. `Password1!` está en las primeras posiciones de cualquier
  diccionario de ataque; `café con leche y dos tostadas` no está en ninguno.
- **Aceptar todos los caracteres**, espacios incluidos.
- **Comprobar contra contraseñas comprometidas o predecibles.**

**Decisiones propias de TaskHub, que no son requisitos de NIST:**

- El **máximo de 72** es el límite técnico de bcrypt, que solo lee los primeros
  72 bytes. Se rechaza lo que pase de ahí en lugar de recortarlo en silencio,
  que sí es lo que exige la norma.
- La **lista de bloqueo va embebida en el código** en lugar de consultar un
  servicio de credenciales filtradas. Una llamada de red por registro añadiría
  latencia y un punto de fallo desproporcionados para este proyecto. Conectar
  una fuente real queda como mejora futura.
- El **umbral de 4 caracteres** para comparar la contraseña con el nombre de
  usuario. Con 3 aparecían falsos positivos: un usuario "ana" no habría podido
  usar frases con "semana" o "mañana".

**Confirmación de contraseña.** El registro pide escribirla dos veces, pero es
asunto exclusivo del formulario: se compara en el cliente, no viaja a la API y
no se persiste. El contrato de `POST /api/auth/register` sigue siendo
`username` y `password`. Hay un test que manda `passwordConfirmation` con un
valor distinto y comprueba que el servidor lo ignora.

**Compatibilidad.** La política se aplica **solo al registro**. El validador
del inicio de sesión no comprueba longitud ni lista de bloqueo, así que las
cuentas creadas con el mínimo anterior de 8 caracteres siguen entrando. Un test
lo fija insertando un usuario con contraseña de 7 caracteres y verificando que
puede iniciar sesión. Aplicar la política al login habría invalidado cuentas
existentes y, además, daría respuestas distintas según el caso, revelando
información sobre la cuenta antes de comprobar las credenciales.

**Tres cosas que aparecieron al implementarlo:**

1. El **administrador tenía su propia regla de 12 caracteres**, independiente
   de la general. En cuanto la política subiera a 15, la cuenta con más
   permisos habría quedado con un mínimo más laxo que un usuario normal. Ahora
   `seed-admin` usa la misma función de validación.
2. La comprobación de longitud del manejador del formulario resultó
   **inalcanzable desde la interfaz**: el `minLength` del campo bloquea el
   envío antes. Se mantiene como segunda barrera —por si el atributo se pierde
   o el navegador autocompleta— y el test se ajustó para comprobar lo que de
   verdad ocurre.
3. `getByPlaceholder` de Playwright busca **por subcadena**, así que
   `'Contraseña'` casaba también con `'Repite la contraseña'` y catorce tests
   fallaron a la vez por ambigüedad. Ahora usan `{ exact: true }`.

**Tests: de 162 a 229.** Los nuevos incluyen varios cuya única función es
impedir que alguien reintroduzca reglas de composición más adelante: afirman
que `caballo correcto grapa pila` es una contraseña válida y que el campo del
formulario **no** lleva atributo `pattern`.

> **Nota posterior (3 de septiembre de 2026).** Esa decisión se revirtió: la
> política pasó a exigir mayúscula, número y símbolo. Los tests citados en el
> párrafo anterior cumplieron su función —fallaron y obligaron a tomar la
> decisión de forma consciente— y se sustituyeron por sus inversos. Ver la
> entrada siguiente.

### Composición obligatoria: una decisión más estricta que NIST

Fecha: 3 de septiembre de 2026.

Se revirtió la ausencia de reglas de composición. La política pasa a exigir, en
el registro y además de los 15 caracteres, **al menos una mayúscula, un número y
un símbolo**.

**Esto no es una lectura distinta de NIST: es apartarse de NIST.** La Revisión 4
dice que los verificadores **no deben** imponer reglas de composición. La
documentación del proyecto no debe presentarlas como requisito de la norma, y se
reescribió el README y la sección anterior para dejarlo separado:

| Alineado con NIST | Decisión propia de TaskHub |
|---|---|
| Mínimo de 15 caracteres | Mayúscula obligatoria |
| Admitir contraseñas largas | Número obligatorio |
| No truncar en silencio | Símbolo obligatorio |
| Aceptar cualquier carácter, espacios incluidos | Contenido de la lista de bloqueo |
| Comprobar contra una lista de bloqueo | Máximo de 72 bytes (límite de bcrypt) |
| Almacenamiento con hash | Umbral de 4 caracteres del nombre de usuario |

**El efecto secundario se asume y se compensa.** Obligar a mezclar tipos de
carácter empuja a `Password123!`, `Verano2026!` o `P@ssw0rd`, que cumplen los
cuatro requisitos y están en la primera página de cualquier diccionario de
ataque. Aplicar la regla sin más habría dejado la aplicación **peor** que antes.
Por eso se añadió `esPatronPredecible`: rechaza una palabra común rodeada de
dígitos y símbolos aunque cumpla la composición.

**Un fallo encontrado escribiendo esa comprobación.** La primera versión quitaba
todo lo que no fuera letra y comparaba el resto contra la lista de palabras
comunes. Con `P@ssword2026!!!` quedaba `pssword`, que no está en la lista, y se
colaba. Lo detectó un test propio. La corrección deshace las sustituciones de
estilo *leet* antes de comparar y prueba cuatro normalizaciones distintas,
porque el relleno (`2026!!!`) y la sustitución (`@` por `a`) se estorban entre
sí: aplicar solo una de las dos operaciones no llega a `password` por ninguno de
los dos caminos.

**El máximo pasó de caracteres a bytes.** bcrypt cuenta bytes. Una contraseña de
72 caracteres con acentos o eñes son más de 72 bytes en UTF-8, y bcrypt
descartaba el sobrante sin avisar — justo el truncamiento silencioso que la
norma prohíbe. La comprobación anterior, con `.length`, dejaba ese caso pasar.
Es un fallo que estaba desde el principio y que solo salió al revisar el límite.

**La suite de API se estrangulaba a sí misma.** Al añadir las comprobaciones de
las tres reglas, `verify.ts` pasó a hacer una decena de registros que deben ser
rechazados, y cada rechazo cuenta como intento fallido de autenticación. El
limitador cortaba a partir del décimo y todo lo posterior fallaba con 429 en vez
de por lo que se estaba probando. Se resolvió con `AUTH_RATE_LIMIT`, que **se
ignora cuando `NODE_ENV` es `production`**: un límite de fuerza bruta que se
puede aflojar desde el entorno no protege de nada, bastaría con colar la
variable en el panel de despliegue. Tres tests nuevos fijan ese comportamiento.

**Interfaz.** El formulario muestra los cuatro requisitos y los marca según se
escribe, en vez de soltarlos todos al enviar. Con cuatro reglas, descubrirlas de
una en una a base de rechazos es precisamente lo que acaba en `Password123!`. El
estado no se transmite solo con el color: cada línea lleva `✓` o `·` y un texto
para lectores de pantalla.

**Compatibilidad.** Sin cambios respecto a lo anterior: la política se aplica
solo al registro. Se añadió un test que inserta directamente el hash de
`caballo correcto grapa pila` y comprueba que esa cuenta sigue pudiendo entrar.

**Tests: de 229 a 344.** La auditoría individual de los 229 anteriores está en
`docs/AUDITORIA_TESTS_229.md`: 150 quedaron intactos, 63 necesitaron actualizar
fixture o aserción y 10 eran incompatibles con la política nueva y se
sustituyeron por sus inversos. Ninguno se borró ni se desactivó.

### `.gitattributes` estaba truncado y nunca normalizó nada

Fecha: 3 de septiembre de 2026. Afecta a **todo el monorepo**, no solo a TaskHub.

Al revisar el estado del repositorio aparecían como modificados una docena de
archivos de TaskHub_React que nadie había tocado —`App.jsx`, `main.jsx`,
`db.ts`, `schema.ts`, `index.html`…—. El diff era CRLF contra LF: contenido
idéntico, final de línea distinto.

La causa era que **`.gitattributes` estaba cortado a media frase**. Tenía cuatro
líneas, todas de comentario, y terminaba en `#  ` sin salto de línea final. Las
reglas nunca llegaron a escribirse, y así estaba también en el commit: no era un
archivo mal editado en local, era un archivo mal commiteado en su día. Sin
ninguna regla activa, git no normalizaba, y cada editor que guardara con CRLF
dejaba el archivo marcado como modificado para siempre.

El alcance real era mucho mayor de lo que parecía: **`git status` listaba unos
920 archivos modificados en todo el monorepo** —el vault de Obsidian, los
proyectos de Java, los de PHP— y prácticamente todos eran ruido de finales de
línea. Con el archivo reparado, la cifra baja a 44, que son cambios de contenido
de verdad.

La regla que se ha puesto es `* text=auto eol=lf`, con dos matices:

- Se fija `eol=lf` explícitamente en lugar de dejarlo a `core.autocrlf`, que es
  configuración de cada máquina. Así el resultado es el mismo en Windows, en
  Linux y en el runner del CI, sin depender de cómo tenga cada uno su git.
- **Excepción para `*.bat` y `*.cmd`, que van con CRLF.** El intérprete de
  Windows puede fallar al leer un archivo por lotes con LF, sobre todo en las
  etiquetas de `goto`. Hay 79 `.bat` en el repositorio, así que la excepción no
  es teórica. Los `.sh` llevan la marca contraria, LF obligatorio.

Para los archivos de código no hizo falta `git add --renormalize`: el índice ya
guardaba LF y era el árbol de trabajo el que tenía CRLF, así que en cuanto hubo
reglas git dejó de ver diferencia.

**Para los scripts sí hizo falta, y ahí apareció un fallo de verdad.** Los 79
`.bat`, el `mvnw.cmd` y los `.sh` estaban guardados **en el repositorio** con
CRLF, no solo en disco: nunca hubo normalización que lo impidiera. Al declararlos
como texto, git pasó a querer almacenarlos con LF y los marcó todos como
modificados, lo que obligó a renormalizarlos:

```
git add --renormalize "*.bat" "*.cmd" "*.sh"
```

En los `.bat` el efecto es puramente interno —siguen saliendo con CRLF al disco
por la excepción `eol=crlf`, así que en Windows no cambia nada—, pero en los
`.sh` era un error real: `install-linux.sh` e `install-macos.sh` tenían
`#!/bin/bash\r` en la primera línea. En Linux eso falla con `bad interpreter:
/bin/bash^M`, porque el `\r` forma parte de la ruta del intérprete. Los scripts
llevaban rotos desde que se subieron y solo salió a la luz al mirar los finales
de línea.

El renormalizado se acotó con esas tres extensiones en lugar de usar `.`, que
habría arrastrado al índice el trabajo en curso de otros proyectos.

**De paso, dos temporales que llevaban meses versionados.** `server/csp-temp.ts`
y `server/sch-temp.ts` eran scripts de diagnóstico de un solo uso —uno imprimía
la CSP para localizar el `script-src-attr 'none'` que rompió el playground, el
otro contaba esquemas `verify_` huérfanos—. Se borraron.

### Sesiones revocables: access token corto y refresh rotativo

Fecha: 3 de septiembre de 2026.

Era el hueco de seguridad más real que quedaba, y estaba anotado como pendiente
desde la auditoría: **tokens de siete días sin forma de revocarlos**. Un token
robado servía una semana, y el logout solo vaciaba el navegador — quien tuviera
una copia seguía dentro.

**Lo que hay ahora.** Dos credenciales en vez de una. Un JWT de acceso de quince
minutos, que es lo que viaja en `Authorization`, y un token de refresco de siete
días guardado en la tabla `refresh_sessions`. Solo el segundo se puede revocar,
y por eso el primero dura tan poco: un JWT firmado vale hasta que caduca, y la
alternativa —una lista negra consultada en cada petición— cuesta una consulta
por llamada para resolver un problema que se resuelve acortando la ventana.

**El refresco no es un JWT, y eso es lo que hace segura la separación.** Son 32
bytes aleatorios. Si los dos fueran JWT, distinguirlos dependería de comprobar
un claim `typ` en cada sitio, y olvidarlo una sola vez bastaría para que un
refresco valiera como token de acceso. Siendo opaco, el middleware intentaría
verificar una firma inexistente y falla solo. El claim está igualmente, como
segunda barrera.

**Rotación con detección de reutilización.** Cada renovación gasta el token y
entrega otro con el mismo `family_id`. Si reaparece uno ya gastado, no basta con
rechazarlo: quien pudo copiarlo tiene también el siguiente de la cadena, así que
se revoca la familia entera.

Con una excepción que hubo que añadir: dos pestañas del mismo usuario pueden
renovar a la vez con la misma cookie, y eso no es un ataque. Dentro de una
ventana de diez segundos la perdedora se rechaza sin matar la familia. Es un
compromiso explícito —estrecha la detección durante esos segundos— pero la
alternativa era cerrar la sesión a quien tuviera dos pestañas abiertas.

**El refresco va en cookie HttpOnly**, no en localStorage. Es la credencial que
importa: sirve para emitir tokens de acceso durante días. Meter una cookie
obligaba a mirar CSRF, que la documentación anterior citaba como ausente
precisamente porque no había cookies. Queda cerrado con `SameSite=Strict`, que
impide que el navegador la mande en peticiones nacidas de otro sitio, más el
hecho de que la cookie no autoriza ninguna ruta de datos y va limitada a
`Path=/api/auth`. CORS se queda con `credentials: false`: todo es mismo origen
en producción, y en desarrollo Vite hace de proxy.

**Dos cosas que aparecieron al implementarlo:**

1. **Dos renovaciones seguidas devolvían el mismo token de acceso.** El único
   campo variable de un JWT es `iat`, con resolución de segundos, así que dos
   emisiones dentro del mismo segundo salían byte a byte idénticas —con la misma
   caducidad—. Se añadió `jti` con un UUID.
2. **Un test de concurrencia que pasaba por el motivo equivocado.** Lanzaba dos
   renovaciones en paralelo y comprobaba que solo una respondiera 200. Pasaba,
   pero porque el driver del entorno de desarrollo solo admite una conexión y
   tumbaba la segunda, no porque el guardián de la rotación funcionara. Se
   sustituyó por una comprobación determinista: dos llamadas seguidas a
   `marcarRotado`, de las que la segunda tiene que devolver `null`.

**Migración de los tokens antiguos: se invalidaron todos.** No llevan el claim
`typ`, así que dejaron de valer en el primer despliegue y todo el mundo tuvo que
volver a entrar. Fue deliberado: mantenerlos por comodidad habría dejado abierta
una semana justo la puerta que el cambio venía a cerrar.

**Tests: de 344 a 453.** La revisión individual de los 344 anteriores está en
`docs/AUDITORIA_TESTS_344.md`. Cobertura del cliente: del 54,93 % al 72,34 %,
con `AuthContext.jsx` pasando de 0 % a 100 %.

### Experiencia de uso y cobertura del cliente

Fecha: 3 de septiembre de 2026.

Los dos fallos de experiencia de uso que estaban anotados como pendientes, más
la parte del cliente que seguía sin cubrir.

**El checkbox de completada esperaba a la respuesta del servidor** antes de
cambiar de aspecto. Con la base de datos en la misma región son 40-80 ms y
apenas se nota, pero desde una conexión lenta la casilla se quedaba quieta lo
suficiente para que pareciera que el clic no había funcionado, y la gente vuelve
a pulsar. Ahora se pinta el cambio de inmediato y se revierte con un aviso si la
petición falla, que es la contrapartida obligatoria: enseñar un cambio que no
llegó a guardarse sería peor que tardar en enseñarlo.

Un detalle que había que resolver: `completed` es un campo calculado a partir de
`status`, así que el estado optimista tiene que traducir los dos. Cambiar solo
`completed` dejaba la tarjeta incoherente durante el instante en que se pinta,
con la casilla marcada y el distintivo diciendo «Pendiente». La regla —marcar
lleva a `completed`, desmarcar vuelve a `pending`— queda duplicada entre cliente
y servidor, y el test de navegador que marca una tarea y comprueba el distintivo
es lo que detectaría que las dos se separen.

También hubo que distinguir las actualizaciones silenciosas: el ciclo optimista
llama a `onUpdate` dos o tres veces por clic, y el aviso «Tarea actualizada»
salía repetido. El checkbox no avisa —él mismo es la confirmación visual—; la
edición sí, porque el formulario se cierra y sin el mensaje no queda claro que
se haya guardado.

**Al salir, el formulario conservaba el modo** en el que estuviera. Quien acababa
de registrarse y pulsaba Salir se encontraba otra vez «Crear cuenta», con su
campo de confirmación y sus cuatro requisitos de contraseña, cuando lo que casi
siempre quiere es volver a entrar. Ahora vuelve a modo «iniciar sesión» al
perder la sesión, sea por Salir o porque caducara. El reinicio va atado al cambio
de `isAuthenticated` y no a cada render, para no estorbar a quien pulsa
«Regístrate» estando ya fuera.

Los dos tests de navegador que **rodeaban** este comportamiento en lugar de
arreglarlo se han enderezado: uno comprobaba el campo de usuario en vez del
botón porque «podía decir Entrar o Registrarse», y el otro tenía que pulsar
«Inicia sesión» antes de buscar el botón «Entrar».

**Cobertura del cliente: del 72% al 96,95%.** `TaskList.jsx` eran 163 líneas sin
un solo test siendo el componente central de la aplicación, y `App.jsx` otras 51
con el enrutado. Los dos están ahora al 100%, y de paso los tests de `TaskList`
son los que fijan que **los filtros los resuelve la API**: si alguien los
reimplementara en el navegador, la lista seguiría pareciendo correcta con pocas
tareas y dejaría de escalar sin que nada avisara.

**Un `vi.mock` que podía romper otro archivo.** `TaskItem.test.jsx` sustituía el
módulo de servicios entero, y esa sustitución vive en el registro de módulos,
que se comparte entre archivos cuando la suite corre sin aislamiento. Según el
orden de ejecución, dejaba a `api.refresh.test.js` sin el módulo de verdad.
Se cambió por espías, que se instalan y se retiran dentro de su propio archivo.

**Tests: de 453 a 501.** Umbrales de cobertura subidos a 95/94/93/96, siempre
justo por debajo de lo real para que actúen como trinquete.

### CD: despliegue automático, no encadenado al CI

Render publica en cada commit a `main` mediante Auto-Deploy. **El CI y el
despliegue van en paralelo**: Render no espera al pipeline, así que un commit
con los tests en rojo llega igualmente a producción. Ocurrió con `9bca722`, que
falló el CI y se desplegó, dejando la aplicación rota por el fallo de CORS.

Se mantiene así a propósito mientras el proyecto está en desarrollo: poder
desplegar un commit con tests fallando permite depurar contra el entorno real.
Encadenarlos —desactivar el auto-deploy y llamar a un Deploy Hook desde un job
que dependa de `ci-ok`— queda para cuando la aplicación se estabilice.

### Pendiente

- **Encadenar el despliegue al CI**, según lo anterior.
- **Protección de rama sin configurar.** Al ser un repositorio de una sola
  persona, lo razonable es exigir que `ci-ok` pase antes de fusionar, sin exigir
  revisión humana: no hay nadie que pueda aprobarla.
- **`PUT` y `PATCH` comparten controlador** y hacen los dos actualización
  parcial. Un `PUT` estricto debería reemplazar el recurso completo. No rompe
  nada, pero es una desviación de la semántica HTTP.
- ~~**Tokens de 7 días sin revocación.**~~ Resuelto: access token de 15 minutos
  y refresh rotativo con tabla de sesiones.
- ~~**Cobertura del cliente al 72%.**~~ Resuelto: 96,95%, con `TaskList.jsx` y
  `App.jsx` al 100%.
- ~~**El checkbox de completada espera a la respuesta del servidor.**~~
  Resuelto: actualización optimista con reversión y aviso si falla.
- **Los E2E comparten la base de datos de desarrollo** y dejan usuarios
  `e2e-*` detrás de cada ejecución. En CI da igual porque el contenedor se
  destruye, pero en local conviene limpiarlos de vez en cuando o darles su
  propia base de datos.

---

## 2026-07-26 / 2026-07-27 — Saneamiento de dependencias y seguridad

Revisión completa de las alertas de seguridad del repositorio, con el criterio
de **corregir en lugar de silenciar**: solo se descarta lo que no tiene arreglo
posible, y siempre con el motivo registrado.

### Credenciales expuestas

Un archivo de notas de `unified-chat-widget` contenía una copia literal de un
`.env` con credenciales reales de varios servicios de terceros. El escáner de
GitHub solo había detectado una de ellas, por ser la única con un formato
reconocible; el resto pasaba inadvertido.

Se sustituyeron todos los valores por marcadores de posición y se rotaron o
restringieron las credenciales afectadas. El `.env` real nunca estuvo
versionado: la fuga se produjo al copiar su contenido a un archivo que sí lo
estaba.

Se revisaron además las otras alertas del escáner de secretos, de las que dos
resultaron ser falsos positivos (marcadores de posición y un nombre de clase
que coincide con un patrón de clave) y una pertenece a código de terceros
retirado del repositorio.

### Código de terceros vendorizado

`unified-chat-widget` incluía una copia completa del código fuente de
`@retconned/kick-js` en `libs/`. Ahora se instala desde npm como cualquier otra
dependencia. Además de eliminar 347 paquetes y la duplicación de alertas (el
mismo aviso aparecía hasta cuatro veces por tener la librería sus propios
manifiestos), corrige un fallo latente: el código importaba `libs/kick-js/dist`,
que estaba en `.gitignore`, por lo que un clon limpio no podía arrancar.

### Actualizaciones de dependencias

- **gym-app (PHP):** Laravel 10 → 12.64. Las ramas 10 y 11 están fuera de
  soporte y Composer se negaba a instalar cualquier versión de ambas por
  avisos de seguridad sin parche. Se actualizaron en bloque Sanctum 4,
  Breeze 2, PHPUnit 11, Collision 8 y los componentes de Symfony 7.
  `composer audit` pasó de 29 avisos en 13 paquetes a ninguno.
- **gym-app (npm):** Vite y `laravel-vite-plugin` a sus versiones mayores
  actuales. Nota: Laravel declara `axios` y `alpinejs` como dependencias de
  desarrollo, pero ambas se empaquetan para el navegador, así que se tratan
  como de producción a efectos de seguridad.
- **Angular/TaskHub/backend:** `bcrypt` v5 → v6, lo que elimina la cadena
  `node-pre-gyp` / `node-gyp` / `tar` (48 paquetes menos) que arrastraba las
  vulnerabilidades críticas. Compatibilidad de hashes verificada con el flujo
  de login real. También `vitest` 4 y `eslint` 10.
- **Angular/TaskHub/frontend:** Angular 19 → 21 mediante `ng update`, en dos
  saltos mayores verificados por separado, con `@angular/material` y
  `@angular/cdk` alineados. Migrado al paquete `@angular/build`.
- **React/TaskHub/client y FastApi/TaskHub/frontend:** Vite 8 y
  `@vitejs/plugin-react`, con la compilación verificada en ambos.
- **unified-chat-widget:** retirado el soporte de BitChute, DLive, Odysee y
  Trovo. La carpeta `messages/` deja de versionarse por ser estado de
  ejecución.
- Cerradas las pull requests de Dependabot que apuntaban a rutas eliminadas en
  la reestructuración de julio.

### Fallos latentes que salieron a la luz

La actualización de Laravel obligó a ejecutar la batería de tests de gym-app,
probablemente por primera vez, y destapó tres problemas anteriores a esta
sesión:

- `phpunit.xml` tenía comentadas las líneas que redirigen los tests a SQLite en
  memoria. Como los tests usan `RefreshDatabase` (que ejecuta `migrate:fresh`),
  **destruían la base de datos de desarrollo** al ejecutarse. Corregido y
  documentado en el propio archivo.
- `UserFactory` no generaba `phone_number`, campo que la migración declara
  `NOT NULL`, por lo que todos los tests basados en factorías fallaban.
- Los tests de registro y perfil, heredados del scaffolding de Breeze, no
  enviaban los campos que la aplicación añadió después (`phone_number`, `role`)
  ni cumplían su política de contraseñas.
- `Angular/TaskHub/backend` declaraba un script `lint` sin tener ninguna
  configuración de ESLint: nunca había llegado a ejecutarse. Añadido
  `eslint.config.mjs` en formato flat config.

### Recuperación de la base de datos de gym-app

Los respaldos existentes (`docs/sql/*.sql`) eran volcados de MySQL y dejaron de
ser restaurables cuando el proyecto migró a PostgreSQL. Se añadió
`docs/sql/gym_app_postgres.sql`, un script de **solo datos** — el esquema es
responsabilidad de las migraciones — con las secuencias sincronizadas mediante
`setval`, paso imprescindible al migrar de MySQL a PostgreSQL.

### Análisis estático (CodeQL)

Las 69 alertas de CodeQL se agruparon en nueve familias de problemas: lo que
parecían decenas de fallos distintos era el mismo puñado de patrones repetidos
en varios archivos. Se han abordado dos de esas familias.

**Modo debug de Flask (4 alertas, resuelta).** Desactivado en las cuatro
aplicaciones que lo tenían activo. El depurador de Werkzeug permite ejecutar
código Python arbitrario desde el navegador; en dos de ellas se combinaba con
`host='0.0.0.0'`, lo que lo exponía a toda la red local. En `BackCount` se
mantiene el `0.0.0.0` de forma deliberada: OBS necesita alcanzar el servidor
desde otro equipo de la red, y esa es precisamente la razón por la que el
depurador debía apagarse.

**Exposición de información en mensajes de error (parte Java, resuelta).**
El patrón `catch (Exception e) { ... .body("..." + e.getMessage()) }` devuelve
al cliente el detalle interno del fallo, que puede incluir rutas del sistema,
consultas SQL o nombres de clases. Corregido en trece controladores: el detalle
pasa a registrarse con `log.error` y la respuesta HTTP lleva un mensaje
genérico. Donde había `e.printStackTrace()` se sustituyó por el mismo registro.

Dos casos se dejaron intactos a propósito, por estar dentro de bloques de
código comentado y no en rutas activas. Y en `HanoiController2`, que no exponía
nada pero se tragaba la excepción sin dejar rastro, se añadió el registro: un
error silencioso es un problema distinto, pero también es un problema.

La mayoría de esos trece archivos son variantes del mismo ejercicio de Spring
Batch guardadas como carpetas paralelas, por lo que cada aviso aparecía
multiplicado por el número de copias. Se valoró excluir esas carpetas del
análisis y se descartó: son código propio y corregirlo cuesta poco más que
justificar por qué no se corrige.

**Exposición de información (parte Python, resuelta).** Mismo patrón en Flask:
`return jsonify({'error': str(e)}), 500` devuelve la excepción al cliente.
Corregidos 21 casos en la API de puntuaciones de LeaderBoard, en
`flask_api_personas.py` y en el servidor TTS del widget de chat. El detalle
pasa a `app.logger.exception` y la respuesta lleva un mensaje genérico.

**Falta de límite de peticiones (resuelta).** Las rutas de autenticación de los
dos TaskHub con backend Express admitían intentos ilimitados: sin límite, probar
contraseñas por fuerza bruta solo depende del ancho de banda del atacante.

Añadido `express-rate-limit` con dos políticas: una estricta para autenticación
(10 intentos cada 15 minutos por IP) y otra general para el resto de la API
(300). La estricta usa `skipSuccessfulRequests`, de forma que los accesos
correctos no consumen cuota y solo se penaliza a quien falla repetidamente —
que es justo el patrón de un ataque, no el de un usuario despistado.

Verificado en los dos sentidos contra el servidor en marcha: diez intentos
fallidos devuelven 401 y a partir del undécimo 429; doce accesos correctos
seguidos no producen ningún bloqueo. Ambas mitades importan — un límite que
frenara también a los usuarios legítimos sería una defensa convertida en avería.

Limitación conocida: el contador es por IP y vive en memoria, así que se
reinicia con el servidor y no cubre a un atacante distribuido. Suficiente para
el uso de estos proyectos; en un despliegue real habría que respaldarlo en
Redis y bloquear también por cuenta, no solo por origen.

Conviene subrayar dónde vive esta protección: en el **backend** de ambos
proyectos, que en los dos casos es Express. El framework de la interfaz
(Angular o React) no interviene ni puede hacerlo, porque un atacante no usa la
interfaz — lanza peticiones directas contra la API. Toda validación de
seguridad tiene que estar en el servidor; la del cliente es comodidad para el
usuario, no defensa.

**Path traversal (resuelta).** Tres servicios construían rutas de fichero a
partir de datos que controla quien hace la petición: dos servicios de lectura y
escritura de CSV en los ejercicios de Spring Batch —cuya ruta llega por un
parámetro HTTP— y el servidor de juegos, que aceptaba por socket una orden
`DESCARGAR <nombre>` y servía el fichero sin comprobar nada. Este último era el
más grave: bastaba pedir `DESCARGAR ../../..` seguido de cualquier ruta para
que el servidor enviase cualquier fichero de la máquina.

En los tres casos se aplica el mismo patrón, y el orden de los pasos es lo que
lo hace correcto: resolver la ruta contra un directorio base, **normalizarla**
para colapsar los `..`, y solo entonces comprobar que sigue estando dentro de
la base. Comprobar antes de normalizar es el error habitual al implementar esta
defensa, y deja la puerta igual de abierta. En el servicio de escritura se
sanea además el nombre derivado de una columna del CSV, sustituyendo cualquier
carácter que no sea alfanumérico, punto, guion o guion bajo.

Cambio de comportamiento a tener en cuenta: esos servicios aceptaban antes
rutas absolutas cualesquiera y ahora solo rutas dentro del directorio base, que
por defecto es el de trabajo y se puede cambiar con `-Dbatch.files.dir=...`.

### Wrappers de Maven incompletos

Al intentar compilar para verificar los cambios anteriores apareció otro
defecto de fondo: **doce proyectos tenían el script `mvnw` versionado pero sin
los ficheros del wrapper**, así que ninguno era construible desde un clon
limpio — incluido `Java/BatchProcessor`, que figura en el catálogo como
proyecto mantenido. Restaurados los doce.

Es el mismo patrón que el script de lint sin configuración de ESLint y que los
tests que nunca llegaban a ejecutarse: **herramientas declaradas pero jamás
ejercitadas**. Tres hallazgos con la misma causa y la misma solución, que es
integración continua: un pipeline que compile y ejecute lo que el repositorio
dice tener habría detectado los tres el primer día.

**XSS y sanitización incompleta (resuelta).** Cuatro avisos con tres causas
distintas, y cada uno pedía una solución diferente:

En el controlador de pseudocifrado, la respuesta contiene texto del usuario y
podía servirse con un tipo de contenido que el navegador interpretara como
HTML. Aquí **escapar no era una opción** — alteraría el resultado del cifrado —,
así que la defensa es declarar `produces = TEXT_PLAIN`: el navegador muestra la
respuesta literalmente en lugar de interpretarla.

En la consola de depuración de TaskHubPro se construía el contenido con
`innerHTML` a partir de la URL (que incluye los filtros que teclea el usuario)
y de la respuesta del servidor. Sustituido por construcción del DOM con
`textContent`. La diferencia es de fondo: `innerHTML` interpreta lo que recibe,
`textContent` lo inserta tal cual.

Y en el saneado de texto para el sintetizador de voz del widget había el error
más instructivo de los tres. La línea original quitaba etiquetas con una única
pasada de `replace(/<[^>]*>/g, '')`. Parece correcta, pero con una entrada como
`<<span>script>` el filtro elimina el `<span>` central y **produce** `<script>`,
una etiqueta recién creada que ya nadie vuelve a revisar. Ahora se repite hasta
que el texto deja de cambiar y se eliminan los signos sueltos. La lección
general: un filtro de una sola pasada puede construir aquello que pretende
eliminar.

### Más herramientas declaradas pero nunca ejercitadas

Intentar compilar para verificar los cambios anteriores destapó dos defectos
más, ninguno relacionado con esta sesión:

- El `pom.xml` de `ApiService` **se declaraba como dependencia de sí mismo**, lo
  que impedía a Maven ni siquiera leer el proyecto. Tenía además un
  `spring-boot-starter` duplicado y Lombok fijado a `RELEASE`, un valor obsoleto
  que hacía que la compilación pudiera cambiar de un día para otro sin tocar
  nada. Ese proyecto no había compilado nunca.
- Siete `application.properties` estaban guardados en ISO-8859 en lugar de
  UTF-8, por haberse escrito con un editor de Windows en español. Maven y Spring
  Boot leen los recursos como UTF-8, así que la compilación fallaba en cuanto
  aparecía una vocal acentuada en un comentario. Convertidos los siete.

Con estos, van seis hallazgos de la misma naturaleza: script de lint sin
configuración de ESLint, tests que destruían la base de datos y nunca se
ejecutaban, doce wrappers de Maven incompletos, un `pom.xml` ilegible y unos
recursos mal codificados. Todos son **cosas declaradas que nadie llegó a
ejecutar**, y todos los habría detectado un pipeline de integración continua en
su primer día. Es, con diferencia, la conclusión más útil de esta revisión.

(Más adelante aparecieron cinco más, hasta once: el `IvParameterSpec` y la
generación de claves RSA de HashTools, el SSR de TaskHub Angular, el
`permitAll()` con token de demostración de RadioStack, y unos `@types/node`
fijados a la versión 18 en un proyecto que se ejecuta sobre Node 22. Todos
documentados en sus respectivas secciones.)

### Criptografía débil en HashTools

Cuatro alertas en `Java/HashTools`, un ejercicio del ciclo formativo que cifra
ficheros con AES y con RSA. Las alertas señalaban los modos de operación: AES en
CBC y RSA con relleno PKCS#1 v1.5. Ambos son corregibles con un cambio de una
línea, pero al revisar el código apareció algo más importante que las propias
alertas.

**El vector de inicialización nunca fue aleatorio.** El código creaba el
`IvParameterSpec` a partir de un array vacío y *después* llamaba a
`SecureRandom.nextBytes()` sobre ese array. `IvParameterSpec` copia el array que
recibe en el constructor, así que rellenarlo más tarde no tiene ningún efecto:
el IV han sido siempre dieciséis bytes a cero. La intención era correcta y el
código lo aparenta, pero la aleatoriedad nunca llegó a aplicarse.

Lo relevante es que **el programa funcionaba gracias a ese fallo**. El IV no se
guardaba en ninguna parte, así que si de verdad hubiera sido aleatorio, el
descifrado no habría tenido forma de reconstruirlo y habría fallado siempre. Un
error tapaba al otro. Es el mismo patrón que los seis hallazgos de la sección
anterior: código escrito, nunca comprobado de verdad.

La corrección:

- **AES pasa a GCM** (`AES/GCM/NoPadding`) con un nonce de 12 bytes generado en
  cada cifrado y escrito al principio del fichero de salida, que es de donde lo
  lee el descifrado. GCM además es cifrado autenticado: si el fichero se
  manipula, el descifrado lanza una excepción en lugar de devolver datos
  corruptos en silencio, cosa que CBC no detecta.
- **RSA pasa a OAEP** con SHA-256 en el hash y en MGF1, declarados de forma
  explícita porque el valor por defecto de Java combina SHA-256 con MGF1-SHA1 y
  esa incoherencia provoca fallos de interoperabilidad difíciles de localizar.

Al cambiar a OAEP hubo que tocar el tamaño de bloque, y eso destapó un tercer
defecto. OAEP consume 66 bytes de relleno frente a los 11 de PKCS#1, así que el
bloque de 117 bytes fijado a mano dejaba de valer; ahora se calcula a partir del
módulo de la clave. Pero además el descifrado RSA leía el fichero **entero** y
lo pasaba a un único `doFinal`, cosa que solo funciona si el original cabía en
un bloque: cualquier fichero mayor que el bloque fallaba al descifrarse. Ahora
se descifra bloque a bloque.

**Aviso de compatibilidad:** cambia el formato del fichero cifrado. Los ficheros
generados con la versión anterior del programa ya no pueden descifrarse con
ésta. Dado que se trata de un ejercicio y no hay datos que conservar, se asume.

#### Generación de claves RSA

Mismo patrón que el IV, en el mismo proyecto. `generarClaves(String pass, int
tamaño)` no usaba ninguno de sus dos parámetros: nunca llamaba a
`kpg.initialize(...)`, así que Java generaba una clave de 2048 bits con su
generador por defecto e ignoraba tanto el tamaño como el `SecureRandom`
sembrado con la contraseña.

Lo interesante es que **los dos parámetros muertos eran trampas** para quien
intentara "arreglarlos" sin mirar:

- El único sitio que llamaba al método pasaba `256`, un valor copiado de la
  generación de claves AES, donde 256 bits es lo normal. Para RSA es un error de
  categoría: `initialize(256)` habría lanzado `InvalidParameterException`.
- Conectar el `SecureRandom` habría sido peor. `setSeed` sobre SHA1PRNG
  sustituye la semilla y vuelve **determinista** la generación: cualquiera que
  conociese la contraseña podría reproducir la misma clave privada. Y
  `PasswordValidator` acepta contraseñas de 8 a 20 caracteres, al alcance de un
  ataque por fuerza bruta.

Corregido llamando a `initialize(2048)` con el generador aleatorio del sistema,
rechazando cualquier tamaño inferior a 2048, y eliminando el `SecureRandom`
sembrado en lugar de conectarlo. Se retiró el parámetro `pass`, que ya no
interviene.

**El comportamiento observable no cambia**: antes se generaban claves de 2048
bits con el generador por defecto, y es lo que se sigue haciendo. Las claves ya
guardadas siguen siendo válidas. Lo que cambia es que el código ahora dice lo
que hace.

### Protección CSRF desactivada

Dos alertas, en dos proyectos, que pese a la etiqueta común **no son el mismo
problema**. La distinción que decide ambos casos es si existe *autoridad
ambiental*: credenciales que el navegador adjunta por su cuenta a una petición
provocada desde otro sitio web. Sin eso, no hay CSRF posible, porque la petición
forjada llega sin identidad.

**RadioStack — falso positivo.** La API es `STATELESS` y no crea sesión ni emite
ninguna cookie; no hay `HttpSession`, `Cookie`, `formLogin` ni `httpBasic` en
todo el proyecto. Desactivar CSRF ahí es la configuración correcta. CodeQL ve
`csrf.disable()` y avisa sin poder determinar si hay autoridad ambiental.
Documentado en el propio `SecurityConfig`, con la condición que obligaría a
revertirlo: si algún día se añade autenticación por sesión o por cookie.

**TaskHub Angular — real, aunque de impacto bajo.** El access token viaja en la
cabecera `Authorization`, que el navegador no añade solo y por tanto es inmune.
Pero el refresh token va en cookie, y `POST /api/auth/refresh` y
`POST /api/auth/logout` se autentican **únicamente** con ella. Eso sí es
autoridad ambiental.

El impacto conviene medirlo con precisión en lugar de asumir el peor caso: el
CORS está restringido a un solo origen, así que un atacante no puede leer la
respuesta y no roba ningún token. Lo máximo que consigue es forzar un cierre de
sesión o una rotación del refresh token. Molestia, no robo de credenciales.

Corregido subiendo la cookie de `sameSite: 'lax'` a `'strict'`. Es un cambio que
no puede romper nada: la SPA y la API son *same-site*, que es la razón de que ya
funcionase con `lax`; `strict` solo restringe el caso cruzado, que aquí no
existe. Se descartó montar un token CSRF con librería (patrón double-submit):
para dos rutas cuyo peor desenlace es un logout forzado, es más infraestructura
de la que el problema justifica.

También se descartó **quitar la cookie** y devolver el refresh token en el
cuerpo de la respuesta. Eliminaría la clase de vulnerabilidad entera, pero esa
cookie es `httpOnly` precisamente para que un XSS no pueda leer el refresh
token: sería cambiar un CSRF de impacto bajo por un XSS con robo de sesión.

**La alerta de TaskHub se descarta a mano.** La consulta
`js/missing-token-validation` es sintáctica — busca `cookie-parser` sin
middleware CSRF y no evalúa los atributos de la cookie, así que no hay forma de
que la corrección aplicada la cierre sola. Es la única excepción al criterio de
*corregir en lugar de silenciar* seguido en el resto de la revisión, y la
diferencia respecto a un descarte de conveniencia es que aquí sí hay un arreglo
real de por medio: lo que se descarta es una comprobación que no sabe mirar
dónde está puesta la defensa.

La corrección se verificó ejecutándola, no por deducción: con la cookie ya en
`Strict`, `POST /api/auth/refresh` devuelve 200 con usuario y token nuevos, y
`POST /api/auth/logout` devuelve 204. Las dos rutas que dependen de la cookie
siguen funcionando.

**Hallazgo aparte:** `SecurityConfig` de RadioStack declaraba
`anyRequest().permitAll()`, es decir, la API entera accesible sin autenticación.
Se anotó aquí como *"puede ser deliberado si es de solo lectura"*; al revisarlo
resultó que no lo era. Resuelto en la sección «Autenticación real en RadioStack».

### Bug de sesión con SSR en TaskHub Angular

Descubierto al verificar lo anterior, y no relacionado con ello: **al pulsar F5
estando dentro, la aplicación expulsaba al usuario al login**.

Lo primero fue descartar que lo hubiera provocado el cambio de la cookie. Tres
medidas lo dejaron claro:

- `localStorage` conservaba la sesión intacta después del F5. Si la causa
  hubiera sido la cookie, el único camino hasta la pantalla de login pasa por
  `clearSession()`, que la habría borrado.
- No se registró **ninguna** petición a `/api/auth/refresh`. La expulsión ocurría
  sin consultar al backend.
- Pedir `/` directamente devolvía un **redirect HTTP** (respuesta 3xx), es decir,
  la decisión venía del servidor, antes de ejecutarse una línea de JavaScript en
  el navegador.

La cadena causal: `ng serve` renderiza en servidor; allí se construye
`AuthService`, cuyo `readUser()` devuelve `null` porque en el servidor no existe
`localStorage`; `isAuthenticated()` da `false`; el `authGuard` que protege la
ruta raíz responde `createUrlTree(['/login'])`; y Angular SSR traduce eso a un
redirect. **En el servidor la aplicación estaba siempre deslogueada.** Solo se
manifestaba al refrescar, que es la única ocasión en que interviene el servidor.

Había además un agravante: `app.routes.server.ts` declaraba
`{ path: '**', renderMode: RenderMode.Prerender }`. Prerenderizar es generar
HTML en tiempo de compilación, así que una ruta protegida por un guard quedaba
congelada en un fichero estático con el resultado de evaluar la sesión de un
usuario inexistente.

**Corregido** marcando las rutas protegidas como `RenderMode.Client`, de modo
que el guard se evalúa solo en el navegador, que es donde vive la sesión. Login
y registro siguen prerenderizándose: son públicas y no dependen de quién sea el
usuario. La regla que ordena ahora ese fichero está escrita en él, junto con la
condición que permitiría revertirlo (deducir la sesión de la cookie `httpOnly`,
que el servidor sí puede leer).

Es el octavo caso del patrón dominante de esta revisión: el SSR estaba
configurado, compilaba y arrancaba, pero el estado de sesión se había diseñado
como si solo existiera el navegador. **Nadie había pulsado F5 estando dentro.**

### Sockets enlazados a todas las interfaces

Once alertas de la misma regla (`py/bind-socket-all-network-interfaces`), en
cuatro programas de Python. Tratarlas en bloque habría sido el error: la regla
detecta `bind("")` o `bind("0.0.0.0")`, pero la pregunta que decide cada caso no
es *¿escucha en todas las interfaces?* sino **¿tiene sentido que este programa
reciba conexiones de la red?**. Salieron tres respuestas distintas.

**Intencionadas — chat de voz, 8 alertas (#63 a #70).** Aplicación de voz entre
equipos de una red doméstica, con descubrimiento por broadcast
(`BROADCAST_IP = "192.168.1.255"`). Recibir conexiones de otros equipos es su
función; enlazar a `127.0.0.1` la dejaría sin hacer nada. Documentadas en la
cabecera de ambos ficheros y descartadas.

El riesgo real de estos programas no es el enlace sino que **no autentican**:
cualquiera en la misma red puede unirse o inyectar audio. Se asume por ser una
red doméstica, y así queda escrito en el código, con la advertencia de no
usarlos en redes ajenas.

**Intencionada — `EnviarArchivos.py`, 1 alerta (#224).** Mismo caso, con un
matiz a favor: sí comprueba un `dest_hash` (SHA-256 derivado del nombre que se
comparte con el emisor) y rechaza lo que no lo traiga. Documentada y descartada.

**Descuido real — `servidor_ftp.py`, 2 alertas (#72, #73).** Aquí el problema
era más grave que la alerta, y solo se ve leyendo el código:

```python
elif cmd == "PASS":
    if last_user is not None:
        logged_in = True          # cualquier usuario, cualquier contraseña
```

**No había autenticación.** Con `USER` y `PASS` arbitrarios se obtenía lectura y
escritura sobre el directorio del script. Enlazado a `0.0.0.0`, eso significaba
un servidor de ficheros abierto a toda la red local.

Y era además incoherente con su propio diseño: el modo pasivo anuncia al cliente
la dirección `127.0.0.1` como destino del canal de datos, con el comentario
*"cliente suele conectar a la misma máquina"*. Es decir, **el código ya asumía
uso local**, pero abría el puerto de control a la red entera.

Corregido:

- `HOST = "127.0.0.1"`, coherente con lo que el modo pasivo ya daba por hecho.
  El socket pasivo se enlaza también a `HOST` en lugar de a `0.0.0.0`: el canal
  de datos no debe estar más expuesto que aquel por el que uno se autentica.
- Credenciales reales, leídas de `FTP_USUARIO` y `FTP_CLAVE`. Si faltan, **el
  servidor no arranca**: arrancar sin credenciales equivaldría a aceptar a
  cualquiera, que es justo lo que hacía antes. Mismo criterio de fallo ruidoso
  que se aplicó en `LeaderBoard_Unity`.
- Comparación con `hmac.compare_digest` en lugar de `==`. Un `==` corta en el
  primer carácter distinto, y ese tiempo desigual permite adivinar la clave
  carácter a carácter midiendo la respuesta.
- Mismo mensaje de error para usuario inexistente y clave incorrecta, para no
  revelar qué usuarios existen.

**Un tercer defecto encontrado de camino**, en el mismo fichero: las cuatro
comprobaciones de que una ruta no se sale de la raíz usaban
`str(ruta).startswith(str(root))`. Comparar rutas como cadenas es un error
clásico: si la raíz es `/datos/FTP`, la ruta `/datos/FTP_privado` empieza por esa
cadena y pasaba el filtro pese a estar fuera. Sustituidas por
`Path.is_relative_to`, que compara por componentes.

### Path traversal en EnviarArchivos.py

No lo detectó CodeQL; apareció al revisar el código de la familia anterior.

```python
save_path = os.path.join("received_files", filename)   # filename lo elige el emisor
```

El nombre del fichero viene en la cabecera que envía el remitente, sin sanear.
Con `../../algo.txt` se escribía fuera del directorio de destino. Requiere
conocer el `dest_hash`, así que no era explotable por cualquiera, pero es la
misma clase de fallo que ya se corrigió en los proyectos Java.

Corregido con `os.path.basename` para quedarse solo con el último componente, y
una verificación posterior con `os.path.commonpath` que confirma que la ruta
final resuelta cuelga realmente del directorio de destino. Se sanea primero y se
comprueba después, en ese orden: el saneo por sí solo es fácil de dar por bueno
sin serlo, y la comprobación es lo que lo respalda.

### Autenticación real en RadioStack

Salió del descarte de la alerta de CSRF. Al documentar por qué desactivar CSRF
era correcto allí quedó anotado un cabo suelto: `anyRequest().permitAll()`. Se
dejó dicho que *"puede ser deliberado si es de solo lectura"*. **No lo era.**

La API tiene `POST`, `PUT`, `PATCH` y `DELETE` sobre programas, locutores,
emisiones, comentarios y chat. Cualquiera podía crear o borrar programas de
radio sin identificarse. Y debajo había algo peor:

```java
res.setToken("Bearer-demo-" + u.getId());
...
Long id = Long.parseLong(auth.replace("Bearer-demo-", ""));
```

El token era el texto `Bearer-demo-` seguido del identificador del usuario. Sin
firma, sin secreto y sin caducidad: enviando la cabecera
`Authorization: Bearer-demo-1` se suplantaba al usuario 1. No había nada que
falsificar, bastaba con teclearlo.

**Lo relevante no es que faltase autenticación, sino que el código aparentaba
tenerla.** Había un `AuthController`, un `/login`, un `PasswordEncoder` con
BCrypt comparando hashes correctamente y un `/me` que devolvía 401. Todo el
andamiaje estaba bien construido, y solo el token era un marcador de posición.
Un sistema sin autenticación se reconoce a simple vista; uno que la simula
induce a error a quien lo lea después.

Sustituido por JWT firmado:

- `JwtService` firma con HMAC-SHA256. La clave se lee de
  `RADIOSTACK_JWT_SECRET` y **no tiene valor por defecto**: uno escrito en el
  repositorio sería una clave pública con la que cualquiera podría emitir
  tokens válidos. Se rechaza al arrancar cualquier clave de menos de 256 bits.
- El token lleva identificador, email y rol. Nada secreto: un JWT viaja en
  Base64, no cifrado, y su contenido es legible por cualquiera. Lo que no se
  puede es alterarlo sin invalidar la firma.
- `JwtAuthenticationFilter` deja la identidad en el contexto de seguridad pero
  **nunca rechaza una petición**. Si no hay token, continúa con el contexto
  vacío. Decidir quién pasa es competencia de `SecurityConfig`, y así las reglas
  de acceso viven en un único sitio en lugar de repartidas en dos.
- `SecurityConfig` sustituye el `permitAll()` global: login abierto, `GET`
  abierto (la parrilla de una radio es información para los oyentes) y todo lo
  que modifica datos exige token. Se añadió un `authenticationEntryPoint` para
  responder **401** en lugar de 403: la diferencia importa, porque no es que
  falte permiso, es que no se ha dicho quién eres.
- `/me` vuelve a consultar la base de datos para comprobar que la cuenta sigue
  activa. **Un JWT no se puede revocar**: al desactivar un usuario, su token
  sigue siendo criptográficamente válido hasta que caduque. La caducidad (una
  hora por defecto) es el único límite real, y por eso es configurable.

**Cambio de compatibilidad:** el cliente JavaFX enviaba `Authorization: <token>`
sin el prefijo `Bearer`, porque el prefijo venía incrustado en la cadena
`Bearer-demo-<id>`. Funcionaba por coincidencia. Corregido en `ApiClient`, que
ahora añade el esquema donde corresponde —forma parte del protocolo HTTP, no del
token—. **El módulo admin hay que recompilarlo.**

Es el noveno caso del patrón dominante: `permitAll()` y el token de demostración
eran marcadores de posición que nadie retiró.

#### Autenticación del WebSocket del chat

Quedó abierta en un primer momento y se cerró después. El filtro JWT de HTTP no
sirve para el chat: una conexión WebSocket se abre con un único handshake y
luego las tramas viajan por un canal ya establecido, fuera del ciclo
petición-respuesta donde actúan los filtros de servlet. Y el handshake tampoco
puede llevar cabecera `Authorization`, porque la API de WebSocket de los
navegadores no permite añadirlas.

La solución es autenticar **una trama más tarde**, en el `CONNECT` de STOMP, que
es la primera que el cliente envía y sí admite cabeceras propias. Lo hace
`StompAuthChannelInterceptor`, y el usuario resultante queda asociado a la
sesión, de modo que las tramas posteriores lo heredan.

El criterio de acceso es **el mismo que en HTTP**, a propósito, para no tener dos
políticas distintas según el transporte:

- `SUBSCRIBE` a `/topic` (leer el chat) es público, como los `GET`.
- `SEND` a `/app` exige token válido, como los `POST`.

Un `CONNECT` sin token se admite como anónimo. Uno con token inválido se
rechaza en lugar de degradarse a anónimo: un token caducado o manipulado indica
que algo va mal, y conviene que el cliente lo sepa.

**Un segundo fallo encontrado al hacerlo:** el alias del mensaje venía en el
cuerpo (`payload.getOrDefault("alias", "Anónimo")`), así que cualquiera podía
firmar con el nombre de otro. Ahora se toma del email del token, que es la única
identidad que el servidor puede verificar. El cliente ha dejado de enviarlo.

En el cliente de escritorio, `StompClient` envía el token en el `CONNECT` y pasa
a interpretar las tramas `ERROR`, que antes descartaba en silencio: sin eso, un
envío rechazado por falta de permisos simplemente no aparecía y el usuario no
recibía explicación alguna.

**Pendiente en la interfaz:** el campo "Tu alias" de `chat.fxml` ya no tiene
efecto. Se deja señalado en lugar de retirarlo, pero es un control muerto.

### Validación incompleta de URL en YoutubeToMp4

Una sola alerta, en la línea que detectaba si el usuario había escrito una URL
en lugar de `csv` o `manual`:

```python
if modo.startswith("http://") or ... or "youtube.com" in modo or "youtu.be" in modo:
```

Buscar `"youtube.com"` dentro de la URL entera parece equivalente a comprobar el
dominio y no lo es. La URL completa contiene partes que controla quien la
escribe —ruta, parámetros, fragmento—, así que
`https://youtube.com.sitio-falso.net/x` y `https://malo.net/?ref=youtube.com`
pasan el filtro sin ser de YouTube.

Ahora bien, **esa línea concreta no era un control de seguridad**: si acierta,
pasa al modo manual, que vuelve a pedir la URL. El fallo real estaba en otro
sitio y CodeQL no lo señalaba: **ni el modo interactivo ni el CSV comprobaban el
destino**. El interactivo solo exigía que empezara por `http://` o `https://`, y
el CSV no comprobaba nada.

Corregido con `es_url_de_youtube()`, que analiza la URL con `urlparse` y compara
el **host**, no la cadena completa. Dos detalles que hacen que funcione:

- Se exige que el esquema sea `http` o `https`, lo que descarta `file://` y
  `javascript:`.
- La coincidencia por subdominio compara con el punto delante
  (`host.endswith(".youtube.com")`). Sin ese punto, `mi-youtube.com` pasaría.

La validación se colocó dentro de `descargar_video_mp4()`, que es el punto por
el que pasan los dos modos, en lugar de repetirla en cada punto de entrada:
repartirla es como se acaba olvidando en uno de ellos.

Verificado con 14 casos, incluidos los cuatro que el filtro anterior aceptaba
indebidamente. Los 14 pasan.

Con esto quedan cerradas las nueve familias **de la lista inicial**. Ver más
abajo: al revisar el listado después aparecieron diez alertas más, dos de ellas
de familias que se creían cerradas.

### Migración de Karma a Vitest en TaskHub Angular

No viene de una alerta de CodeQL sino de Dependabot: la cadena vulnerable de
`brace-expansion` entraba por Karma, el ejecutor de tests. Angular 21 usa Vitest
por defecto y ofrece guía de migración, así que en vez de perseguir la
dependencia se retiró la rama entera.

- El builder pasa de `@angular/build:karma` a `@angular/build:unit-test`. Vitest
  no lanza un navegador: ejecuta en Node y simula el DOM con jsdom.
- El builder nuevo no admite opciones de compilación en el target de test
  (`polyfills`, `assets`, `styles`), que ya estaban en el de `build`. La única
  que no estaba, `zone.js/testing`, no hace falta: el único test no usa
  `fakeAsync` ni `waitForAsync`. Si algún día se usan, hay que añadir
  `zone.js/plugins/vitest-patch`.
- Como el proyecto tiene SSR, se añadió una configuración de build `testing` que
  desactiva `ssr` y `outputMode: server`. Sin ella, el builder habría usado
  `development`, que arrastra el servidor a los tests.
- `tsconfig.spec.json` pasa de tipos `jasmine` a `vitest/globals`.

El fichero de test no se tocó: usa `describe`, `it`, `expect`, `toBeTruthy` y
`not.toBeNull`, todo compatible. Existe un schematic oficial
(`refactor-jasmine-vitest`) para convertir espías y matchers de Jasmine, pero
aquí no había nada que convertir.

**Resultado:** los 2 tests pasan en Vitest y las vulnerabilidades de npm en ese
proyecto **bajan de 12 a 3**, desapareciendo las seis de severidad alta. El
árbol de dependencias pasa de 668 a 519 paquetes.

Desinstalar Karma no bastó por sí solo. Tras hacerlo, `npm audit` seguía
señalando la cadena `brace-expansion → minimatch → glob → karma →
@angular/build`. La causa se vio en el `package.json` de `@angular/build`:

```json
"peerDependencies":     { "karma": "^6.4.0", "vitest": "^4.0.8" },
"peerDependenciesMeta": { "karma": { "optional": true }, "vitest": { "optional": true } }
```

Angular declara **ambos runners como peers opcionales**, para que cada proyecto
instale solo el que use. npm no instala los peers opcionales, así que ese Karma
no lo necesitaba nadie: era un resto que sobrevivía en el `package-lock.json` de
cuando sí era dependencia directa. `npm uninstall` retira la declaración pero no
purga el árbol. Se resolvió regenerando `node_modules` y el `package-lock.json`
desde cero.

La lección, que vale para cualquier proyecto de npm: **desinstalar un paquete no
garantiza que salga del árbol**. Mientras siga en el bloqueo, sus dependencias
transitivas siguen instaladas y siguen contando en la auditoría.

**Queda abierta a propósito** la cadena
`@angular/cli → @modelcontextprotocol/sdk → @hono/node-server` (3 moderadas). El
único arreglo que ofrece npm es retroceder `@angular/cli` a la 21.0.4. Mismo
criterio que las otras alertas bloqueadas aguas arriba: no se descarta, se deja
abierta para que se cierre sola cuando Angular actualice.

**No se ejecutó `npm audit fix --force` en ningún momento.** Proponía instalar
`@angular/build@19.1.9` y `@angular/cli@21.0.4`, es decir, deshacer la
actualización a Angular 21 que costó dos rondas de `ng update`. Retroceder de
versión no es corregir una vulnerabilidad.

**Un hallazgo de camino.** La instalación falló primero con `ERESOLVE`: Vitest 4
exige `@types/node` 20, 22 o 24 en adelante, y el proyecto declaraba `^18.18.0`
mientras el Node realmente instalado es el **22.16.0**. Llevaba tiempo
compilándose con los tipos de una versión de Node que no se usa, y que además ya
está fuera de soporte. Se alineó a `^22`, la que coincide con el runtime: unos
tipos más modernos que el intérprete permitirían usar APIs inexistentes en la
máquina, y el fallo aparecería en ejecución en lugar de al compilar.

Se resolvió subiendo la dependencia, **no** con `--force` ni
`--legacy-peer-deps`: el conflicto era real, no un aviso espurio.

**Nota:** la propia documentación de Angular marca como *experimental* la
migración de un proyecto existente a Vitest.

### python-jose sustituido por PyJWT en TaskHub (FastAPI)

Primera de las alertas de Dependabot abordadas una a una. `python-jose 3.3.0`
acumulaba una alerta **crítica** —confusión de algoritmos con claves OpenSSH
ECDSA, que permite forjar tokens— y una moderada de denegación de servicio.

**La crítica no era explotable aquí, y conviene dejarlo escrito.** Ese ataque
necesita que el servidor verifique con una clave ECDSA y que el atacante firme
con HS256 usando esa clave pública como secreto HMAC. Este proyecto usa un
secreto simétrico y, sobre todo, fija la lista de algoritmos en el descifrado:

```python
jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

Ese `algorithms=` es precisamente la defensa contra la familia de ataques de
confusión de algoritmos: impide que el servidor use el `alg` que venga en la
cabecera del token. Estaba bien hecho desde el principio.

Aun así se corrigió, porque bastaría con cambiar `ALGORITHM` en el `.env` para
que dejara de ser teórico.

**Se eligió migrar a PyJWT en lugar de subir a `python-jose 3.5.0`**, que habría
sido una línea. El motivo no es la vulnerabilidad concreta sino el historial:
python-jose pasó **cuatro años sin publicar versión** —3.3.0 en 2021, 3.4.0 en
2025— y en ese hueco arrastró la confusión de algoritmos sin corregir. Subir de
versión arregla el fallo de hoy pero no el riesgo de cadena de suministro. La
documentación oficial de FastAPI dejó de recomendarlo por lo mismo.

Y unifica: `LeaderBoard_Unity` ya usaba PyJWT, así que ahora hay **una sola
librería de JWT** en el repositorio en lugar de dos que hacen lo mismo.

El cambio son tres líneas: el import, el tipo de excepción capturada y la
dependencia. Las llamadas a `encode` y `decode` tienen firma idéntica en ambas
librerías. Se retiró el extra `[cryptography]`, innecesario con HS256, lo que
elimina también `ecdsa`, `rsa` y `pyasn1` del árbol.

**Verificado con cinco pruebas contra el servidor en marcha**, no solo con el
caso feliz:

| Prueba | Resultado |
|---|---|
| Token válido | 200 |
| Sin cabecera `Authorization` | 401 |
| Cadena que no es un token | 401 |
| Firma alterada en un byte | 401 |
| **`sub` cambiado de `prueba1` a `admin`, firma original intacta** | **401** |

La última es la que de verdad importa: comprueba la propiedad que hace útil un
JWT, que el contenido no se puede modificar sin invalidar la firma. Debería
estar en el CI.

**Un error metodológico digno de recordar.** El primer intento de alterar la
firma cambió su último carácter, de `...Erno` a `...Ernp`, y el servidor
respondió 200. Parecía que la autenticación estaba rota. No lo estaba: una firma
HMAC-SHA256 son 32 bytes, que en base64url ocupan 43 caracteres, y el último
grupo de 3 caracteres codifica solo 2 bytes. **Los 2 bits sobrantes se
descartan**, y `o` y `p` se diferencian justo en uno de ellos. Ambas cadenas
decodifican a los mismos 32 bytes: el token era auténtico y el servidor hizo lo
correcto.

Es el tercer caso en dos días en que la herramienta o la prueba dicen algo que
no es —tras las clases duplicadas de CodeQL y las alertas fantasma de
Dependabot—. Sin comprobar los bytes, se habría "arreglado" código que
funcionaba.

**Anotado y no corregido:** `datetime.utcnow()` está obsoleto desde Python 3.12.
Funciona correctamente con PyJWT, que interpreta el datetime ingenuo como UTC,
así que no es un fallo. Se deja para cuando toque.

#### python-multipart y python-dotenv en el mismo proyecto

`python-multipart` 0.0.12 → 0.0.32 y `python-dotenv` 1.0.1 → 1.2.2.

`python-multipart` acumulaba cuatro alertas altas, y conviene separar cuál
importaba. La de **escritura arbitraria de ficheros indica en su propio título
«via Non-Default Configuration»**: requiere una configuración que FastAPI no
usa, así que no aplicaba. Las otras tres son denegación de servicio al parsear
formularios —cabeceras de parte sin límite, frontera malformada, parseo
cuadrático de la cadena de consulta— y esas **sí** eran alcanzables.

El motivo es dónde interviene el paquete: FastAPI lo usa para leer formularios,
y aquí eso ocurre en `OAuth2PasswordRequestForm`, en `routers/auth.py`. Es
decir, en el **login**, que es una ruta pública y sin autenticar. Cualquiera
podía enviarle un formulario deformado sin tener cuenta.

El salto de versión es grande, así que antes de aplicarlo se comprobó en un
entorno aparte que `OAuth2PasswordRequestForm` sigue funcionando con FastAPI
0.115.0 y `python-multipart` 0.0.32, en `application/x-www-form-urlencoded` y en
`multipart/form-data`, y que sigue devolviendo 422 cuando falta un campo.

Verificado después contra el servidor real: `POST /auth/token` con credenciales
incorrectas devuelve 401 y con las correctas devuelve el token. El 401 también
cuenta como prueba: significa que el formulario se parseó bien y la comparación
se hizo; si el parseo hubiera fallado, el error habría sido otro.

### Jackson al día en radiostack-admin

`jackson-databind` 2.15.2 → 2.22.0, con dos altas: saltos del validador de tipos
polimórficos que permiten instanciar clases arbitrarias.

**Lo interesante fue cómo hacerlo, no la versión.** El pom padre importa el BOM
de Spring Boot, que fija las versiones de Jackson para **todos** los módulos.
Subir aquí solo `jackson-databind` habría dejado su `jackson-core` transitivo en
la versión que marca Spring Boot, y esa mezcla de versiones distintas entre
artefactos del mismo grupo es exactamente la que producía las alertas separadas
de `jackson-core` en los proyectos que se retiraron.

Peor aún: **ese desajuste no rompe la compilación**. Las clases se encuentran y
el build pasa; falla en tiempo de ejecución, al deserializar.

Se resolvió importando el **BOM de Jackson en el propio módulo**, que mantiene
`databind`, `core` y `annotations` en bloque y solo afecta a este módulo.

No se subió Jackson en todo el proyecto a propósito: `radiostack-api` es una
aplicación Spring Boot y debe usar el Jackson que Spring espera. `radiostack-admin`
es un cliente JavaFX independiente que solo usa `ObjectMapper` para leer el JSON
de la API, así que ahí el salto está aislado. **Es el mismo criterio aplicado a
PyTorch: actualizar hasta donde el cambio está contenido, y no más allá.**

Verificado con `dependency:tree`, que es lo que compilar no demuestra:

```
jackson-databind:jar:2.22.0
+- jackson-annotations:jar:2.22
\- jackson-core:jar:2.22.0
```

(El `2.22` de `annotations` no es un desajuste: Jackson publica ese artefacto con
versión de dos componentes en las entregas `.0`.)

#### El bug que la prueba destapó: el cliente nunca pudo iniciar sesión

Al arrancar la API y el cliente JavaFX juntos para probar el parseo, el login
falló:

```
Unrecognized field "activo" (class com.radiostack.admin.client...LoginResponse$UserInfo)
```

**No lo causó la actualización.** El historial lo confirma: el `UsuarioDTO` del
servidor devuelve el campo `activo` desde el commit original del proyecto
(`7076f35`), y la clase `UserInfo` del cliente nunca lo declaró. El
`ObjectMapper` del cliente estaba sin configurar, y su comportamiento por
defecto es fallar ante campos desconocidos. Es decir: **el cliente de RadioStack
no ha podido iniciar sesión desde el primer día.** Nadie lo notó porque nadie
había arrancado los dos módulos a la vez.

Que apareciera *ahora* es, irónicamente, la prueba de que Jackson 2.22 funciona:
el error solo puede producirse después de recibir y empezar a leer el JSON.

Corregido en el sitio correcto —el `ObjectMapper` del cliente, no la clase
`UserInfo`— con `FAIL_ON_UNKNOWN_PROPERTIES = false`. Añadir el campo a mano
habría dejado el mismo fallo latente para el próximo campo que el servidor
añadiese. Un cliente HTTP debe tolerar que el servidor incorpore campos: es la
forma normal de evolucionar una API sin romper a quien la consume.

Verificado de extremo a extremo: la API arranca (Tomcat en 8080, Flyway valida,
PostgreSQL conecta), el cliente hace login con `admin@radiostack.local` y entra
al panel de administración.

Es el duodécimo caso del patrón de esta revisión —algo que compila pero que
nunca se ejercitó— y el mejor argumento para el CI pendiente: **arrancar los dos
módulos juntos una sola vez** habría detectado que el cliente no podía loguearse.

### Conector de MySQL: cambio de artefacto, no de versión

`Java/BatchProcessor` declaraba `mysql:mysql-connector-java:8.0.33`, con una alta
(*MySQL Connectors takeover*). Este no se arregla subiendo la versión: **ese
artefacto está descatalogado**. Oracle movió el conector a
`com.mysql:mysql-connector-j` en 2022 y dejó de publicar el anterior, que se
quedó congelado en la 8.0.33 con la vulnerabilidad sin parchear. Subir el número
no habría servido de nada, porque no hay versiones nuevas de las coordenadas
viejas.

Cambiadas las coordenadas a `com.mysql:mysql-connector-j` y retirada la
`<version>`: el proyecto hereda de `spring-boot-starter-parent`, que gestiona
ese artefacto y lo mantiene al día.

**El cambio es transparente** porque el nombre de la clase del driver no cambia
en la práctica: `application.properties` ya usaba `com.mysql.cj.jdbc.Driver`, que
es la clase del artefacto nuevo. No hubo que tocar ninguna configuración.

### Apache POI en XlsxToCsvConverter

`poi-ooxml` 5.3.0 → 5.5.1 (una moderada de validación de entrada al parsear
OOXML). `poi` y `poi-ooxml` se subieron en bloque mediante una propiedad
`poi.version` compartida: `poi-ooxml` depende de `poi`, y versiones distintas del
mismo grupo dan errores de enlace en ejecución. Salto dentro de la serie 5.x y el
código solo usa `XSSFWorkbook` y `ss.usermodel`, así que no hubo cambios de
código.

**Un hallazgo de camino, el decimotercero del patrón:** al compilar falló con
`invalid target release: 23`. El pom declaraba `maven.compiler.target=23`, una
versión de Java que el JDK instalado (21) no puede generar. Es decir, **este
proyecto no compilaba en la máquina donde vive**, y nadie lo había notado porque
nadie lo había compilado. Bajado a 21, que es el JDK real y le sobra a POI, que
solo requiere Java 8.

### JasperReportExecutor: reescritura del pom y compilación al vuelo

Cinco alertas concentradas en un proyecto del portfolio (el TFG): iText 2.1.7 de
2009 (XXE), dos de `jasperreports`, POI y el driver de PostgreSQL. Como el
proyecto **se ejecuta de verdad** —genera informes contra PostgreSQL y exporta a
PDF—, no bastaba con que compilara: tenía que seguir produciendo los informes.

**El pom estaba roto, no solo desactualizado.** Declaraba a mano iText, POI,
groovy y commons, y **dos versiones distintas de `jasperreports`** (6.18.1 y
5.6.0) más `poi`/`poi-ooxml` repetidos tres veces. Maven se queda con la primera
versión de cada uno e ignora el resto, así que medio pom no hacía nada.

El código solo usa `net.sf.jasperreports` y JDBC; iText y POI los emplea
JasperReports por debajo. Así que se reescribió el pom a **dos dependencias**:
`jasperreports 6.21.5` (última de la serie 6.x, que conserva la API de
exportadores del código) y `postgresql 42.7.7`. Lo demás viene transitivo y
parcheado. El dato que hizo esto viable: **JasperReports 6.21.5 ya no usa iText,
usa OpenPDF** (`com.github.librepdf:openpdf`, el fork libre que corrige los fallos
de aquella iText 2.1.7), y trae POI 5.4.1 y Jackson 2.17 dentro. Verificado con
`dependency:tree`: `com.lowagie:itext` **desaparece del árbol**.

**Dos problemas destapados al ejecutarlo, ninguno de la actualización en sí:**

Las plantillas declaraban `language="groovy"`, y al arrancar fallaban con
`CompilationFailedException`: el pom viejo traía `groovy-all:2.5.14` para eso, y
JasperReports 6.21.5 declara Groovy como opcional (no se arrastra). Las
expresiones de los informes son Java válido —`$F{campo}`, `new java.util.Date()`,
`$V{REPORT_COUNT}%2 == 0`—, sin nada de Groovy, así que se pasaron las dos
plantillas a `language="java"`. JasperReports compila Java con su propio `ecj`
incluido, sin dependencia extra.

Y el programa cargaba ficheros **`.jasper` precompilados**, que llevan grabada
dentro la versión con la que se compilaron (y su Groovy). Eran el origen del
acoplamiento: al cambiar la librería, dejaban de cargarse. Se reescribió para
**compilar los `.jrxml` al vuelo con `JasperCompileManager`** en cada arranque,
de modo que la plantilla siempre se compila con la versión que corre. Se
retiraron los `.jasper` obsoletos.

De paso se corrigió un fallo latente en la carga: usaba
`getResource().getPath()`, que devuelve rutas inválidas en Windows (prefijo
`/C:/`, `%20` en los espacios). Cambiado a `getResourceAsStream`, que habría dado
problemas en cuanto la ruta del proyecto tuviera un espacio.

**Verificado ejecutándolo:** conecta a PostgreSQL, compila las dos plantillas y
genera `informePuntuaciones.pdf` e `informeJugadores.pdf`. De 200 líneas de pom a
60, de cinco vulnerabilidades a cero, y el proyecto queda **menos acoplado que
antes** —ya no depende de ficheros precompilados con una versión concreta—.

### PyTorch en AI_DuoTalk

`torch` 2.7.1 → 2.13.0. La 2.7.1 arrastraba varias alertas moderadas y bajas de
corrupción de memoria. Conviene aclarar que **aquí no estaba la crítica**: el
`torch.load` con RCE (`weights_only`) es de FPS-AI-Toolkit con torch 2.1.0, no de
este proyecto.

Antes de tocar la versión se comprobó qué la ataba: **nada la fijaba**. El código
no importa `torch` directamente —lo usan Whisper (transcripción) y Silero (voz)
por debajo—, `openai-whisper` pide `torch` sin rango de versión, y `gpt4all` ni
siquiera depende de torch. Así que subir a la última estable (2.13.0) era seguro
por el lado de las dependencias.

**Es la única actualización de esta ronda que no se pudo verificar en el
sandbox:** torch pesa cientos de MB y necesita la máquina real. Se probó
ejecutando AI_DuoTalk de extremo a extremo —Whisper transcribe y Silero
sintetiza voz—, que es lo que ejercita torch de verdad; que `pip install`
termine no habría demostrado nada, porque el modelo de Silero se carga vía
`torch.hub` en tiempo de ejecución.

**Queda `torch` de FPS-AI-Toolkit sin tocar** (entrada aparte): allí es
`torch==2.1.0+cu121`, una compilación CUDA que no viene de PyPI, y actualizarla
exige conocer la GPU y mover torch, torchvision y torchaudio en bloque. Sigue
excluida en `dependabot.yml`.

### FPS-AI-Toolkit: PyTorch CUDA y Pillow

El proyecto con más alertas de toda la revisión: **24** (Pillow 13, torch 11),
más de la mitad de las 46 que quedaban. Es una herramienta de visión por
ordenador del portfolio, y usa GPU, así que la actualización dependía del
hardware real de la máquina.

**Pillow** 12.2.0 → 12.3.0. Las 13 alertas eran de vulnerabilidades publicadas
después de la 12.2.0 —escrituras fuera de límites, bombas de descompresión,
inyección de comandos en `WindowsViewer`—, todas corregidas en la 12.3.0.

**El stack de PyTorch** pasó de `torch/torchvision/torchaudio 2.1.0/0.16.0/2.1.0
+cu121` a `torch/torchvision 2.6.0/0.21.0 +cu124`. Tres decisiones:

- **De cu121 a cu124.** Aunque el toolkit CUDA instalado (`nvcc`) es 12.1, el
  driver de NVIDIA es retrocompatible: torch trae sus propias librerías CUDA y
  solo necesita un driver suficientemente moderno. Verificado en la máquina:
  `torch.cuda.is_available()` da `True` sobre la RTX 4060 Ti (sm_89). La 2.6.0 es
  además la versión que arregla por defecto el `torch.load` con RCE
  (`weights_only`), que era la alerta crítica de este proyecto.

- **Se retiró `torchaudio`.** Estaba en el `requirements.txt` (2.1.0+cu121) pero
  el código no usa audio: es un proyecto de visión, y `torchaudio` no llegó a
  instalarse siquiera. Lo requiere `ultralytics` (YOLO) a través de torch y
  torchvision, nunca torchaudio. Fuera ~100 MB de dependencia muerta.

- **Los tres —ahora dos— artefactos se fijan emparejados** (torch 2.6.0 ↔
  torchvision 0.21.0). Mezclar versiones del stack de torch da errores en
  ejecución, no al instalar. Documentado en el propio `requirements.txt`, con la
  orden de instalación desde el índice de PyTorch (no PyPI) porque las builds
  `+cuXXX` no están en PyPI.

`torch` sigue **excluido en `dependabot.yml`** a propósito, y esto explica por
qué: Dependabot no entiende el sufijo `+cu124` ni el índice alternativo de
PyTorch, así que propondría la build de CPU de PyPI y rompería la GPU.
Actualizarlo requiere hacerlo a mano, como aquí.

**Verificado ejecutándolo:** las versiones quedan emparejadas con CUDA activa, y
el toolkit arranca con YOLO detectando en GPU.

### FPS-AI-Toolkit: el stack de PyTorch con CUDA

La mayor concentración de la revisión: 24 alertas (13 de Pillow, 11 de torch),
más de la mitad de todo lo que quedaba. Un toolkit de visión con YOLO que se
ejecuta en la GPU, así que compilar no bastaba: tenía que seguir detectando.

**PyTorch.** Estaba en `torch==2.1.0+cu121` con `torchvision` y `torchaudio`
emparejados, con una crítica (`torch.load` con RCE) y varias altas de corrupción
de memoria. Nada del proyecto fija la versión —la usa `ultralytics` por debajo, y
solo pide `torch>=1.8.0`—, así que se pudo subir.

El dato que lo decidió: la máquina ya tenía **torch 2.6.0+cu124** instalado y
funcionando. El driver de NVIDIA es retrocompatible, así que la build cu124 corre
sobre una RTX 4060 Ti aunque el toolkit `nvcc` sea 12.1: torch trae sus propias
librerías CUDA y solo necesita un driver moderno. Se alineó el `requirements.txt`
a esa versión real (2.6.0+cu124 / torchvision 0.21.0+cu124), que además es donde
se corrige por defecto el `torch.load` con RCE. Verificado:
`torch.cuda.is_available()` es `True` y ve la GPU.

**Pillow** 12.2.0 → 12.3.0. Aquí sí había parche: las 13 alertas eran de
vulnerabilidades publicadas después de la 12.2.0, y la 12.3.0 las cierra.

**Tres defectos destapados al ejecutarlo, todos del patrón dominante:**

- `torchaudio` estaba en el `requirements.txt` pero **el único uso era un import
  muerto** (`from torchaudio.models.wav2vec2 import wav2vec2_base`), sobrante de
  una prueba antigua: se importaba y no se usaba en ninguna parte. Es un proyecto
  de visión, no de audio. Se borró el import y se retiró torchaudio del
  `requirements`, ~100 MB de dependencia inútil menos.
- `dxcam` (captura de pantalla rápida) **se importaba pero faltaba en el
  `requirements.txt`**, así que una instalación limpia no arrancaba. Añadido.
- Ambos fallos solo aparecieron **ejecutando** el programa, uno tras otro: el
  import de torchaudio tumbaba el arranque en la línea 34, y una vez quitado,
  faltaba dxcam en la 39.

Son los hallazgos trece y catorce del tipo «declarado pero nunca ejercitado», y
el argumento más claro para el CI pendiente: **un CI que solo importara el módulo
principal** habría cazado los dos sin necesidad de GPU ni de nada más.

**Queda `torch` de AI_DuoTalk ya resuelto aparte; este era el último proyecto
con el stack CUDA.** Verificado ejecutando `MultifuncionFPS.py`: arranca y YOLO
detecta.

### flask-cors 5.0.0 a 6.0.5 en LeaderBoard_Unity

La última entrada de la lista real, y la única de salto de versión mayor, por eso
se dejó para el final. Tres alertas moderadas: coincidencia de rutas
inconsistente y sensibilidad a mayúsculas al casar orígenes.

El salto 5 → 6 endurece precisamente cómo flask-cors casa los patrones de
origen, que es lo que corrige las tres alertas. Podría haber roto una
configuración que dependiera de la laxitud anterior, pero aquí no aplica: el uso
es una sola llamada `CORS(app, methods=[...], origins=Config.CORS_ALLOWED_ORIGINS)`
con la **lista de orígenes vacía**. Sin orígenes que casar, el cambio de
comportamiento no tiene nada que romper. La API de la librería (`CORS(...)`) es
idéntica entre la 5 y la 6.

Verificado: instala limpio y la API arranca. Con esto quedan cerradas las 19
entradas de la lista real de vulnerabilidades, salvo las tres dejadas abiertas a
propósito (sección siguiente).

### Limpieza de validación en gym-app

Tres arreglos en `RegisteredUserController::store`, ninguno de seguridad: código
de validación redundante que se había ido acumulando.

- **`phone_number` se validaba dos veces**: la regla `size:9` y, justo después,
  una comprobación manual con `strlen`. Eliminada la manual; la regla ya lo hace.
- **`sport` era obligatorio para coach mediante un `if` con `filled()`** tras el
  `validate()`. Movido a la propia regla como `required_if:role,coach`, que es lo
  que Laravel ofrece para esto.
- **`Password::uncompromised()` corría también en los tests.** Esa regla consulta
  la API de HaveIBeenPwned por HTTP, así que metía una llamada de red externa en
  la suite: la hacía lenta y dependiente de que el servicio respondiera. Ahora se
  añade solo fuera del entorno `testing`; en producción sigue rechazando
  contraseñas filtradas.

Verificado con `php artisan test`: **25 tests, 61 assertions, todo verde**,
incluido `new users can register`, que ejercita justo esta validación. Los tests
usan SQLite en memoria (por el `phpunit.xml` corregido en su día), así que no
tocan la base de datos de desarrollo.

Los dumps MySQL obsoletos (`gym_app.sql`, `gym_app_v1.0.sql`) que figuraban como
pendientes ya no existen en `docs/sql/`; solo queda el script de PostgreSQL.

**Nota no corregida:** `size:9` valida la longitud, no que sean dígitos —
`"abcdefghi"` pasaría—. El código anterior tenía el mismo comportamiento, así que
no se cambió. Para exigir dígitos sería `digits:9`.

### Acabado: chat.fxml y el README de YoutubeToMp3

**Campo alias muerto retirado.** Tras autenticar el WebSocket de RadioStack, el
servidor firma cada mensaje con el usuario del token, así que el campo "Tu alias"
de `chat.fxml` ya no servía para nada — se dejó en su día señalado como pendiente.
Eliminados el `<TextField fx:id="aliasField">` del fxml y el
`@FXML private TextField aliasField` del controlador. El layout no se resiente:
el campo de mensaje ya tenía `HBox.hgrow="ALWAYS"` y ocupa el hueco. Ojo: el
`alias` que aparece en los mensajes **recibidos** es distinto —es el de quien
envía, que llega del servidor— y se conserva.

**README de YoutubeToMp3 corregido.** Documentaba un `batch_downloader.py` que no
existe, tanto en el árbol de ficheros como en un comando de ejecución. La
descarga masiva por CSV **sí existe**, pero está integrada en `YoutubeToMp3.py`
(función `descargar_desde_csv`), no en un script aparte. Corregidas las dos
referencias para apuntar al script real. Es documentación que mandaba a ejecutar
un fichero inexistente.

**Sobre los READMEs en general:** la tarea preveía escribir READMEs mínimos por
proyecto, pero al revisarlo la mayoría ya los tenía, y bastante completos —los
cuatro TaskHub, casi todos los de Python—. No hacía falta la ronda masiva; solo
la corrección puntual del fantasma de YoutubeToMp3.

### Angular: dependencia muerta retirada, salto a 22 aplazado

La tarea pendiente hablaba de "actualizar Node y las deprecaciones de Angular".
Al revisarlo, ninguna de las dos deprecaciones que se creían pendientes aplicaba:

- **`@angular/platform-browser-dynamic`** figuraba en el `package.json` pero **no
  se importa en ningún sitio**: la aplicación arranca con `bootstrapApplication`
  desde `@angular/platform-browser`, la forma moderna. Era dependencia muerta.
  Retirada.
- **`@angular/animations`** sí se usa, pero mediante `provideAnimations()`, que es
  la API actual y correcta (la usa Angular Material por debajo). La deprecación
  real —las animaciones basadas en `trigger()`/`transition()`, sustituidas por
  `animate.enter`/`animate.leave`— no aparece en el código. Nada que cambiar.

**El salto a Angular 22 se deja aplazado a propósito.** El proyecto está en
Angular 21, que se fijó en su día porque Angular 22 exige Node ≥ 22.22.3 y la
máquina tiene 22.16.0. Pero 21 no es una versión atascada: el `@angular/cli` 21
declara `node: ^20.19.0 || ^22.12.0 || >=24.0.0`, y el 22.16.0 instalado cumple.
Es decir, **Angular 21 funciona con el Node actual**; el requisito de 22.22.3 solo
entra en juego si se salta a 22.

Saltar a 22 obligaría a: subir Node primero, luego `ng update` (un major cada
vez), y volver a probar SSR, Vitest y el flujo de sesión, todo lo cual está
verificado sobre 21. Es una migración mayor sin nada que hoy la empuje —21 es
reciente y está soportado—, así que queda como decisión futura y no como deuda.

**Cuando se aborde:** actualizar Node a ≥ 22.22.3, `ng update @angular/core@22
@angular/cli@22` (con material y cdk en el mismo comando, que deben moverse en
bloque), y re-probar arranque, F5 con sesión y `npm test`.

### Bug de ritmo en unified-chat-widget: mensajes en tanda

Reportado por Juan: antes los mensajes del overlay aparecían de uno en uno, en
orden de llegada; en algún refactor pasaron a mostrarse **todos de golpe**.

La causa es una asimetría entre conectores que quedó al descubierto al retirar la
pool antigua:

- **Twitch y Kick** entregan por evento (`on("ChatMessage")`): un mensaje, una
  llamada, en tiempo real. Gotean solos.
- **YouTube y Rumble** entregan por **sondeo**: cada ciclo (YouTube cada 60 s)
  hacen `messages.forEach(onMessage)` y sueltan de golpe todo lo acumulado.

El diseño original amortiguaba esto con la pool de `utils/globalMessages.js`: los
mensajes se guardaban y el cliente los iba leyendo en orden. Esa pool quedó
comentada al migrar al WebSocket, y `handleMessage` pasó a llamar
`saveAndBroadcastMessage` directamente, sin nada que espaciara las tandas. Con
solo Twitch/Kick no se notaba; al volver a usar Rumble, cada sondeo inundaba el
overlay.

**Corregido** reponiendo el amortiguador del lado del servidor: una cola FIFO
(`broadcastQueue`) en la que `handleMessage` encola, y un temporizador que la
drena **de uno en uno, en orden de recepción**, cada `BROADCAST_INTERVAL_MS`
(1 s, en una sola constante para poder ajustarlo). Es el mismo efecto que daba la
pool, ahora sobre el WebSocket. Los mensajes de sistema (avisos de conexión) se
dejan inmediatos a propósito, por ser esporádicos.

Verificado por Juan con Rumble conectado: los mensajes vuelven a aparecer uno a
uno en orden.

**Limitación conocida:** con un ritmo de entrada sostenido superior a uno por
segundo, la cola acumula retraso respecto al directo. Es el mismo comportamiento
que la pool original (también era una cola); si llega a molestar, se puede
acelerar el drenado cuando la cola supere un umbral.

### Segunda tanda de alertas (avisos nuevos tras la primera limpieza)

Semanas después aparecieron alertas nuevas —unas de avisos publicados esos días,
otras que la reescritura del pom de Jasper no llegó a cubrir—. Clasificadas:

**pgjdbc 42.7.7 → 42.7.12 (corregido).** Dos altas: downgrade silencioso de
channel-binding (CVE-2026-54291) y el PBKDF2 sin límite anterior. La 42.7.7 que
se había puesto seguía afectada (rango `>= 42.7.4, < 42.7.12`). Subida a 42.7.12,
que es donde pgJDBC refuerza la comprobación en su propio código.

**Angular 21.2.18 → 21.2.19 (corregido).** Cuatro altas del propio framework, de
publicación reciente: dos XSS por atributos de manejador de evento en el pipeline
i18n (`@angular/core`, `@angular/compiler`), envenenamiento de caché en
`HttpTransferCache` (`@angular/common`) y XSS de SSR (`@angular/platform-server`).
**El parche es la 21.2.19, dentro de la rama 21** —no obliga a saltar a Angular 22
ni a subir Node—. El `package.json` ya pedía `^21.2.18`, así que el fallo estaba
solo en la versión clavada en el `package-lock.json`; se subió el suelo de todos
los `@angular/*` a `^21.2.19` y se regeneró el lock. Confirma, de paso, que valió
la pena quedarse en 21: la rama sigue recibiendo parches de seguridad.

**JasperReports (abierta a propósito, documentada).** Dos altas de deserialización
con RCE (CVE-2026-6009 y relacionada). **El parche es jasperreports 7.0.7**, y la
6.21.5 que se puso sigue afectada (`< 7.0.7`). No se sube a 7.x porque es un cambio
mayor —nueva estructura de módulos y API— que obligaría a rehacer el pom y
reprobar la generación de informes, que ya dio guerra con Groovy.

La decisión de dejarla abierta se apoya en que **el vector no existe en este
proyecto**: la RCE por deserialización necesita datos serializados no confiables
—típicamente un `.jasper` de origen externo—, y el ejecutor solo compila
plantillas `.jrxml` propias desde `resources`, no carga `.jasper` ajenos ni
deserializa entrada de usuario, y se ejecuta en local contra la base de datos del
propio autor. Es un TFG de escritorio, no un servicio que reciba informes de
terceros.

**Se deja abierta, no se descarta en GitHub.** Y con una advertencia honesta: un
aviso High de RCE abierto lo ve cualquiera que mire la pestaña de seguridad,
aunque en este uso no sea explotable. Si el proyecto llegara a exponerse como
servicio, la migración a 7.0.7 pasa a ser obligatoria.

### Pipeline de CI (GitHub Actions)

La conclusión que más se repitió en toda la revisión: **catorce fallos del tipo
"declarado pero nunca ejercitado"** —imports rotos, `requirements.txt`
incompletos, poms que no compilaban, un `.env` con valores de ejemplo, un cliente
que nunca podía loguearse—, todos encontrados a mano al ejecutar cada proyecto, y
todos los habría cazado un CI el primer día. `.github/workflows/ci.yml` es ese
CI.

**Alcance: ligero y universal, no "construir todo".** El monorepo tiene ~50
unidades construibles de cuatro ecosistemas, muchas experimentales; un CI que las
compilara y testeara todas estaría en rojo permanente (la mitad no construyen
limpias, y las que sí necesitan base de datos y secretos). En vez de eso, el
pipeline hace comprobaciones baratas que atrapan justo la clase de fallo que se
coló:

- **`python-syntax`** — `py_compile` de los 128 `.py` propios (excluye venvs y
  código vendorizado). Verificado a cero antes de crear el workflow.
- **`js-syntax`** — `node --check` de los 32 `.js` propios. Habría cazado el
  import muerto de `torchaudio`... el equivalente JS: el import roto de
  unified-chat-widget.
- **`config-lint`** — JSON y YAML bien formados. **Excluye a propósito los
  `tsconfig*.json` de Angular**, que son JSONC (con comentarios) y darían falso
  positivo con un validador de JSON estricto.
- **`regression-guard`** — falla si reaparecen dos patrones ya corregidos:
  `str(e)` en respuestas HTTP (fuga de información) y `console.log` de
  `process.env` (fuga de secretos). Hoy ambos a cero.
- **`maven-compile`** — `mvn -DskipTests compile` (sin BD ni secretos) de los
  cinco proyectos Java mantenidos, con JDK 21. Habría cazado el `target 23`
  imposible de XlsxToCsvConverter o el pom ilegible de ApiService.

Todos los jobs se verificaron en verde **antes** de crear el workflow: 128 `.py`
y 32 `.js` sin errores de sintaxis, JSON válidos (salvo los tsconfig excluidos),
y los dos patrones peligrosos a cero. El CI nace verde y a partir de ahí protege
contra regresiones.

Lo que **no** cubre, a propósito: tests con base de datos y arranque de
servicios. Eso son jobs por proyecto, con contenedores y secretos, y se añadirán
aparte si algún proyecto vitrina lo justifica.

### Flask 3.0.3 → 3.1.3 en LeaderBoard_Unity

Un aviso Low: la sesión no añade la cabecera `Vary: Cookie` en ciertos accesos,
lo que puede provocar que una caché sirva una respuesta con sesión a otro
usuario. Corregido en Flask 3.1.0; subido a 3.1.3.

Comprobada la compatibilidad con la Werkzeug 3.1.8 ya instalada (van acopladas)
en un entorno aparte antes de aplicarlo: arranca, la sesión funciona y **la
respuesta ya incluye `Vary: Cookie`**, que es justo lo que faltaba.

### PyTorch: 8 avisos abiertos a propósito (parche fuera de alcance CUDA)

Ocho avisos en `torch` (FPS-AI-Toolkit), Moderate y Low: corrupción de memoria en
funciones concretas (`unpack_sequence`, `lstm_cell`, `jit.script`,
`pad_packed_sequence`...) y un DoS local. El parche es **torch 2.9.1**.

Se dejan abiertas por dos razones que se refuerzan:

1. **El parche no existe para la CUDA de esta máquina.** El proyecto usa builds
   `+cu124` (RTX 4060 Ti), y la rama cu124 de PyTorch se quedó en la 2.6.0 —no
   hay 2.7/2.8/2.9 en cu124, cu126 ni cu128 para Windows—. Subir a 2.9.1
   obligaría a cambiar de rama CUDA y reprobar todo el stack GPU + ultralytics.
2. **Son todas de vector Local.** Requieren que el atacante ya tenga acceso a la
   máquina y consiga pasar tensores manipulados a esas funciones internas. En una
   herramienta de escritorio que ejecuta su propio autor con sus propios datos,
   el riesgo práctico es nulo: quien pudiera explotarlo ya estaría dentro.

Coste de "arreglar" (cambio de CUDA + reprueba completa de GPU) desproporcionado
frente a un riesgo local inexistente. Además, PyTorch publica avisos de esta
clase de forma continua, así que subir de versión solo cambiaría unos números por
otros. **No se descartan en GitHub; se dejan abiertas y documentadas.**

### undici forzada a 7.29.0 en TaskHub Angular (overrides)

Cinco avisos en `undici` (uno High, cuatro Moderate): filtración cross-user por
directivas de caché, inyección CRLF, inyección de atributos de cookie,
desincronización de respuestas. Todas **transitivas y de scope Development**:
undici entra por `@angular/build` (servidor de desarrollo), por `jsdom` (tests) y
por `node-gyp` (vía el CLI). **No llega al bundle de producción.**

El parche es undici 7.29.0, pero `@angular/build` **clava la 7.28.0 exacta**
(`"undici": "7.28.0"`, sin rango), así que Dependabot no podía actualizarla:
bloqueada aguas arriba como `@hono`.

A diferencia de `@hono`, aquí sí cabía forzarla con un **`overrides`** en el
`package.json` (`"undici": "7.29.0"`). Es seguro porque es un salto de parche
—un único arreglo en `lib/util/cache.js`— sobre herramientas que no se despliegan.
Verificado: `npm ls undici` muestra las tres rutas en 7.29.0 (`overridden` /
`deduped`), el build compila y `npm audit` baja de 5 a 3 (las 3 restantes son las
moderadas de `@hono`/tooling, bloqueadas aguas arriba).

Anotado en el propio `package.json`: si un futuro `@angular/build` ya trae
undici ≥ 7.29, este override sobra y debe retirarse.

### Guzzle 7.15.1 → 7.15.2 en gym-app

Dos avisos recientes en `guzzlehttp/guzzle`, dependencia **directa** del proyecto
(`composer.json: ^7.8`): host no canónico que burla comprobaciones basadas en
host (CVE-2026-69246, High) y dominio de cookie que conserva alcance de
subdominio (Moderate). Es el primer arreglo del ecosistema **Composer/PHP** en
toda la revisión.

El parche es la 7.15.2, dentro de `^7.8`, así que **no hizo falta tocar el
`composer.json`**: solo actualizar el `composer.lock` con
`composer update guzzlehttp/guzzle --with-all-dependencies`.

**Alcance real bajo:** el propio aviso dice que solo afecta a aplicaciones que
construyen la URI de la petición a partir de entrada no confiable. gym-app usa
Guzzle por debajo del cliente HTTP de Laravel, no fabrica URLs con datos de
usuario. Aun así el arreglo es un salto de parche de coste y riesgo nulos, así
que se aplica sin más.

**Obstáculo de entorno, no del proyecto:** `composer update` fallaba con
`curl error 60 (unable to get local issuer certificate)`. No era un bundle de CA
ausente —apuntar `curl.cainfo`/`openssl.cafile` al `cacert.pem` de Laragon no lo
resolvió—, sino el **antivirus interceptando HTTPS**: presenta un certificado
firmado por su propia raíz, que está en el almacén de Windows (por eso el
navegador confía) pero no en el `cacert.pem` que usa el OpenSSL de PHP. Es el
mismo problema que ya apareció con Avast semanas atrás. Se resolvió desactivando
el escaneo HTTPS del antivirus durante la actualización. Queda anotado que el
`php.ini` de Laragon no tiene `curl.cainfo` configurado.

### Alertas dejadas abiertas a propósito (bloqueadas aguas arriba)

Tres alertas no se corrigen porque el fallo está en una dependencia transitiva
de un paquete de terceros, varios niveles por debajo de lo que el repositorio
controla. En ninguna de las tres hay un fichero propio donde documentarlo —el
código vulnerable vive en `node_modules`, que no se versiona—, así que la
decisión queda registrada solo aquí. **No se descartan en GitHub: se dejan
abiertas para que se cierren solas cuando el mantenedor de aguas arriba
actualice.** Es el criterio de *corregir en lugar de silenciar* llevado a su
consecuencia lógica: si no hay corrección posible, tampoco se silencia.

- **`brace-expansion` en `unified-chat-widget`** (alta, DoS). Entra por una
  cadena de siete niveles: `@retconned/kick-js` → `puppeteer-extra-plugin-stealth`
  → … → `rimraf@3` → `glob@7` → `minimatch@3` → `brace-expansion@1.1.16`.
  `npm audit fix` responde literalmente *"No fix available"*: `kick-js` fija
  versiones antiguas de puppeteer, y estas fijan el resto de la cadena. Es una
  dependencia **de desarrollo** —puppeteer automatiza el navegador para leer el
  chat de Kick, no llega a producción— y el DoS solo se dispara con patrones de
  llaves construidos por un atacante, cosa que aquí no ocurre. Forzarla con
  `overrides` inyectaría una versión no probada siete niveles por encima; se
  descartó.

- **`@hono/node-server` en `TaskHub` Angular** (moderada). Cadena
  `@angular/cli` → `@modelcontextprotocol/sdk` → `@hono/node-server`. El único
  arreglo que ofrece npm es retroceder `@angular/cli` a la 21.0.4, deshaciendo la
  actualización a Angular 21.

- **Dos dependencias del build de Angular** ya documentadas en la cabecera de
  este archivo: sus únicas "correcciones" son retrocesos de versión.

El patrón común: **la única corrección disponible es peor que el problema**
—retroceder una versión mayor, o inyectar un paquete no probado en una cadena
ajena—. Todas se resolverán solas cuando el proyecto de aguas arriba publique.

### El listado de Dependabot se sincronizó

Las alertas fantasma descritas más abajo desaparecieron por sí solas: **de 202 a
46**, y las 46 corresponden a ficheros que existen. Ya no aparece
`Java/Spring/SpringBatch/`, `Java/Spring/SpringBoot/`, `Python/TaskHub/` ni los
paquetes no declarados de `GPTDevTeam`.

El reparto de lo que queda es más útil que el total:

| Proyecto | Alertas |
|---|---|
| `FPS-AI-Toolkit` (Pillow 13 + torch 11) | **24** |
| `JasperReportExecutor` (itext, jasperreports ×2, pgjdbc, poi) | 5 |
| `radiostack-admin` (jackson, ya corregidas) | 5 |
| `AI_DuoTalk` (torch) | 4 |
| `LeaderBoard_Unity` (flask-cors ×3, flask) | 4 |
| Sueltas (mysql-connector, poi, brace-expansion, @hono) | 4 |

**Tres proyectos concentran 33 de las 46.** Y en los tres la actualización no es
viable por motivos distintos: Pillow ya está en la última versión publicada,
torch está excluido por el asunto de la compilación CUDA, e iText 2.1.7 lleva
abandonado desde 2009 y migrar significa reescribir con iText 7 u OpenPDF.

Es decir: **el techo de lo alcanzable actualizando dependencias está en unas 13
alertas.** Bajar de ahí exige decidir si esos proyectos siguen siendo necesarios,
que es una decisión de alcance del repositorio, no de mantenimiento.

### BackCount y FFMPEG_UI

Dos proyectos pequeños, resueltos de una vez.

**`StreamTools/BackCount`** — `Flask` 3.0.0 → 3.1.3 y `Werkzeug` 3.0.1 → 3.1.8.

La alerta que figuraba como alta era *"Werkzeug debugger vulnerable to remote
execution"*, y **no era explotable**: el depurador de Werkzeug solo permite
ejecutar código si el modo debug está encendido, y `app.py` tiene `debug=False`.
Con el comentario que se dejó al arreglarlo en su momento:

```python
# host='0.0.0.0' es intencionado: OBS necesita alcanzar el servidor desde
# la red local. Por eso mismo debug debe estar desactivado: el depurador
```

Es un caso que merece señalarse: **una corrección de una sesión anterior
neutralizó una alerta que apareció después**, y el comentario evitó tener que
reconstruir el razonamiento al volver. La actualización se aplicó igualmente,
porque la 3.0.1 sí arrastra los fallos de `safe_join` en Windows.

Comprobado antes de aplicarlo que Flask 3.1.3 funciona con Werkzeug 3.1.8 en los
tres patrones que usa el proyecto —plantillas, respuestas JSON y sesión—, por
estar los dos paquetes acoplados.

**`FFMPEG_UI`** — `python-dotenv` 1.1.1 → 1.2.2. Salto menor en un proyecto de
escritorio con PyQt; no requiere verificación funcional.

### Dependencias de LeaderBoard_Unity al día

Cuatro entradas de la lista real viven en el mismo `requirements.txt`, así que se
trataron juntas.

| Paquete | Antes | Ahora | Motivo |
|---|---|---|---|
| `PyJWT` | 2.10.1 | 2.13.0 | 4 avisos, **3 no aplicables** |
| `Werkzeug` | 3.0.4 | 3.1.8 | `safe_join` inseguro en Windows, agotamiento de recursos |
| `requests` | 2.31.0 | 2.34.2 | fuga de `.netrc`, `verify=False` persistente |
| `python-dotenv` | 1.0.1 | 1.2.2 | `set_key` sigue enlaces simbólicos |

**De los cuatro avisos de PyJWT, tres no afectaban a este proyecto**: los de
clave pública JWK aceptada como secreto HMAC, SSRF en `PyJWKClient` y peticiones
JWKS ilimitadas requieren `PyJWK` o `PyJWKClient`, que no se usan en ninguna
parte. Los dos que sí aplicaban son denegación de servicio.

El proyecto ya estaba bien escrito en lo que importa: **las cinco llamadas a
`jwt.decode` fijan `algorithms=['HS256']`**, sin excepción, y el `SECRET_KEY`
mide 64 bytes. Las alertas graves no aplicaban por cómo está hecho el código, no
por casualidad.

Sin cambios de código: `encode`, `decode`, `ExpiredSignatureError` e
`InvalidTokenError` son idénticos entre 2.10 y 2.13. Se comprobó también que
Flask 3.0.3 funciona con Werkzeug 3.1.8 antes de subirlo, por estar acoplados.

**Verificado extremo a extremo**: registro 201, login 200 con los dos tokens,
perfil con token válido 200, y —la que importa— **perfil con el `id` del token
cambiado de 8 a 1 conservando la firma original: 403**. Esa API identifica al
usuario por el `id` que viaja dentro del token, así que si la firma no se
comprobara bien, bastaría cambiar un número para leer el perfil de otro.

#### Dos cabos sueltos que salieron al probarlo

**El `.env` era idéntico al `.env.example`.** Al mover las credenciales de
código a variables de entorno en una sesión anterior, el `.env` se quedó con los
valores de muestra: el rol `usuario`, que no existe en PostgreSQL. La API llevaba
desde entonces sin poder conectar a su base de datos, y nadie lo había notado
porque nadie la había arrancado. Es la undécima aparición del patrón de esta
revisión, y esta vez el descuido fue propio.

**La contraseña real contenía `@` y `?`.** En una URL de conexión el `@` separa
las credenciales del host, así que `psycopg2` partía la cadena por el sitio
equivocado. Corregido codificando (`%40`, `%3F`) y **documentado en el
`.env.example`** con la tabla de equivalencias, porque le va a ocurrir a
cualquiera que clone el proyecto.

#### Anotados y no corregidos

En `authenticate_token` (`app.py`, línea 41):

```python
if auth_header:
    token = auth_header.split(" ")[1]
if not token:
```

Si la petición llega sin cabecera `Authorization`, `token` nunca se asigna y el
`if not token` lanza `UnboundLocalError` → **500 en lugar de 403**. Si llega con
la cabecera pero sin espacio, el `split(" ")[1]` lanza `IndexError` → otro 500.
Rechaza igual, así que no es un fallo de seguridad, pero un 500 en el camino de
autenticación revela que algo revienta por dentro.

Y `app.run(host='0.0.0.0')` en la línea 1335 escucha en todas las interfaces.
Puede ser deliberado, porque el cliente es un juego de Unity que quizá corra en
otra máquina.

### El punto ciego de CodeQL en Java

Descubierto al abrir por fin el aviso amarillo *"CodeQL is reporting warnings"*
que llevaba semanas en la cabecera de la pestaña de seguridad y que nunca se
había mirado. Decía:

> **166 duplicate classes filtered out.** 166 files defined a class that clashes
> with the fully-qualified name of another scanned class. This means that only
> one of each clashing pair will be scanned.

La causa: nueve copias del ejercicio de Spring Batch conviviendo como variantes,
todas con el mismo paquete y los mismos nombres de clase. Para CodeQL,
`com.example.BatchProcessor.BatchProcessorApplication` era una sola clase
repetida nueve veces, así que analizaba una y descartaba ocho.

**Consecuencia:** el «0 alertas abiertas» de la sección anterior era cierto
sobre lo analizado, no sobre todo el código Java del repositorio.

Y el punto ciego escondía defectos reales. Un `grep` de dos minutos por las
copias no analizadas encontró **el mismo path traversal** que CodeQL sí había
reportado en `FalsosBatch` —un `@RequestParam` de HTTP entrando directo en una
ruta del sistema de ficheros— en **cuatro controladores más** que nunca
aparecieron en ninguna lista de alertas.

No era una sospecha teórica: ya se sabía que las copias divergían, porque al
corregir `FileReaderService` se dio por hecho que eran idénticas, se sobrescribió
una y falló la compilación. Copias distintas, fallos distintos.

Lo mismo ocurría con `api/ApiExtractData` y `api/api2/ApiExtractData`: dos
versiones que difieren en casi todos los ficheros pero comparten los 25 nombres
de clase, de modo que una de las dos jamás se analizó.

**Resuelto retirando del repositorio** `Java/Spring/SpringBatch` y
`Java/Spring/SpringBoot`, en lugar de renombrar paquetes o excluir rutas. Se
elimina la causa en vez de rodearla. El aviso bajó de 166 a 28 al sacar Spring
Batch, y las 28 restantes eran exactamente las dos parejas de `SpringBoot`.

Con esos proyectos se van también varias correcciones documentadas más arriba
—el `produces = TEXT_PLAIN` de `PseudoCifradoController`, los
`resolverDentroDeBase` de `FileReaderService` y `FileWritterService`— y buena
parte de las alertas de Maven, que vivían en esos `pom.xml`
(`mysql-connector-java`, `log4j-core`, `jackson-databind`, `jackson-core`). El
registro de aquellas intervenciones se mantiene aquí porque describe decisiones
válidas, aunque el código ya no esté en el repositorio.

**La lección, que es la misma que la de la sección siguiente:** el aviso de
estado de una herramienta importa tanto como su lista de resultados. Un análisis
que informa de 0 problemas y de 166 ficheros no analizados no está diciendo que
el código esté limpio.

### Las diez alertas que quedaban

Revisado el listado de code scanning tras dar por cerradas las nueve familias,
quedaban 10 alertas abiertas (frente a 246 cerradas). Ocho de ellas no eran
nuevas: pertenecían a familias ya tratadas, en ficheros que no se habían mirado.

**Registro de secretos en claro (4).** Familia que no estaba en la lista inicial,
y donde estaba el único hallazgo serio de los diez:

```js
// test-twitch.js:6
console.log("TOKEN:", process.env.TWITCH_OAUTH_TOKEN);
```

Imprimía el token de OAuth de Twitch completo por consola. Ese token da control
sobre la cuenta, y una vez escrito en la salida queda en el historial del
terminal y en el log de cualquier sistema que ejecute el script. `debug-env.js`
lo truncaba a 12 caracteres, que es menos, pero sigue siendo material secreto.

Corregido en los dos ficheros informando de si cada variable **está definida y
cuánto mide**, nunca de su valor. Los scripts existen para comprobar que el
`.env` carga, y para eso el valor no aporta nada.

**Falta de límite de peticiones (2).** `unified-chat-widget/index.js` y
`JSGameChat/server/index.js`. Añadido `express-rate-limit` con límites holgados
(600 y 300 por minuto): estos servidores los consume la fuente de navegador de
OBS, que sondea con frecuencia. El objetivo no es frenar un ataque sino que una
pestaña recargando en bucle no sature un proceso de un solo hilo que además
atiende websockets.

**Exposición de información por excepción (4).** `TestMail.py` y
`rumble_server.py`, con el mismo `str(e)` en la respuesta HTTP que se corrigió en
`app.py`. En el caso de Rumble el detalle importa: el mensaje de error de su API
puede incluir la URL completa con la clave de acceso.

`TestMail.py` merece mención aparte: **es un fichero que ya se había editado** en
la familia 1 para desactivar el modo debug de Flask, y su `str(e)` se pasó por
alto en la familia 2. La alerta apareció como nueva porque esa misma edición
provocó el reanálisis del fichero. No se escapó del listado: se dejó a medias.

### Credenciales en el código de LeaderBoard_Unity

Al revisar los mensajes de error de esa API aparecieron cuatro credenciales
reales escritas directamente en el código y versionadas. Ninguna la había
detectado el escáner de secretos de GitHub: no tienen un formato reconocible,
así que no hay patrón que buscar. Es el mismo tipo de fuga que la del archivo
de notas del widget, y refuerza la misma conclusión — **las herramientas
automáticas encuentran los secretos con formato conocido; el resto solo
aparece leyendo el código**.

Afectaba a la contraseña de aplicación del correo de notificaciones, a la clave
de firma de los JWT y a las contraseñas de dos usuarios de PostgreSQL, estas
últimas repetidas además en el README del proyecto, en dos scripts SQL, en un
archivo de notas, en la configuración de PostgreSQL y en el ejecutor de
informes de Jasper.

De las cuatro, la más grave era la clave de firma de los JWT: con ella se
pueden fabricar tokens válidos para cualquier usuario, incluido el rol de
administrador, sin necesidad de credenciales. Las cuatro han sido rotadas o
revocadas.

**Cambios aplicados:** todas las credenciales pasan a leerse de variables de
entorno, con un `.env.example` documentado y `python-dotenv` añadido a las
dependencias. La configuración **aborta el arranque con un mensaje explícito**
si falta alguna variable, en lugar de recurrir a un valor por defecto: una
clave de respaldo silenciosa acabaría en producción sin que nadie lo notara, y
eso es peor que la fuga original.

**Resultado:** alertas de Dependabot de **590 a 2**. Las dos restantes son
dependencias transitivas del sistema de compilación de Angular, cuyas únicas
"correcciones" disponibles son retrocesos de versión; se dejan abiertas a la
espera de que el framework las actualice.

### Tercera tanda: league/commonmark (gym-app) y js-yaml (unified-chat-widget)

Dos grupos nuevos que ilustran los dos extremos del criterio *corregir en lugar
de silenciar*: uno tiene arreglo limpio y se aplica; el otro no tiene arreglo
aplicable y se deja abierto y documentado.

- **`league/commonmark` 2.8.3 → 2.9.1 en gym-app** (seis alertas de golpe).
  Es transitiva: la arrastra `laravel/framework`, que la declara como
  `^2.8.1` (no está en el `composer.json` propio). Las seis son avisos
  acumulados contra la serie 2.x:
    - DoS por complejidad cuadrática al parsear Markdown malicioso
      (GHSA-c2pc-g5qf-rfrf y CVE-2026-71488).
    - Bypass del allowlist de la extensión Embed —`youtube.com.evil` cuela
      cuando se permite `youtube.com`, con riesgo de SSRF/XSS
      (CVE-2026-33347, parcheado en 2.8.2).
    - XSS en `AttributesExtension` vía `javascript:` con bytes de control que
      el navegador descarta antes de leer el esquema (CVE-2026-71478 y
      CVE-2025-46734, parcheado en 2.9.0).

  Todas las versiones de parche (2.6.0, 2.8.2, 2.9.0) son ≤ 2.9.1, la última
  de la serie 2.x, y 2.9.1 cae dentro del `^2.8.1` que exige Laravel
  (`>=2.8.1 <3.0.0`). Por eso basta con
  `composer update league/commonmark --with-dependencies`: cierra las seis sin
  tocar el `composer.json` ni romper la restricción de Laravel. No se sube a
  la 3.x porque quedaría fuera del rango que Laravel admite.

- **`js-yaml` 4.3.0 en unified-chat-widget** (una alerta, se deja abierta).
  Transitiva por la misma cadena que `brace-expansion`:
  `@retconned/kick-js` → `puppeteer` → `cosmiconfig@9` → `js-yaml`. La alerta
  es CVE-2026-59870 (consumo cuadrático de CPU al resolver `!!omap`). **El fix
  solo existe en la línea 5.x —desde 5.2.1— y no se retroportó a las ramas 3.x
  ni 4.x**; el propio aviso lo dice. `cosmiconfig@9` fija `js-yaml@^4`, así que
  forzar la 5.x con `overrides` rompería cosmiconfig (la API cambió entre 4.x y
  5.x). Además el vector no aplica: aquí js-yaml lo usa cosmiconfig para leer el
  fichero de configuración propio en arranque, no para parsear YAML de fuentes
  no confiables. Sin corrección posible en la rama 4.x y bloqueada aguas
  arriba, se deja **abierta y sin descartar en GitHub**, igual que
  `brace-expansion`.

---

## 2026-07-05 — Limpieza de historia (git filter-repo)

Se reescribió la historia completa del repositorio para eliminar contenido
que no debía estar bajo control de versiones: artefactos de build, entornos
virtuales, dependencias de terceros vendorizadas, binarios pesados y archivos
de configuración local. Como parte de la operación se rotaron preventivamente
credenciales de desarrollo.

**Resultado:** el repositorio pasó de 2,06 GiB a 48,84 MiB (−97,7%).

**Consecuencias operativas:**

- Todos los hashes de commit anteriores al 2026-07-05 cambiaron.
- Los clones y forks previos a esa fecha son incompatibles con la historia
  actual: es necesario clonar de nuevo. No hacer pull ni push desde un clon
  antiguo, y nunca forzarlos (--force / --allow-unrelated-histories):
  restauraría la historia purgada.
- La operación se realizó sobre un clon espejo con `git filter-repo`,
  validando el resultado antes de sustituir el repositorio y publicar.

---

## Política de dependencias y alertas de seguridad

Este repositorio es un monorepo de proyectos personales y experimentales: la
mayoría no se despliega en ningún servidor y varios están archivados. Las
alertas de Dependabot se tratan, por tanto, con el siguiente criterio:

1. **Se corrigen** las vulnerabilidades que afectan a dependencias de
   *producción* de proyectos mantenidos (las que acabarían ejecutándose en un
   despliegue real).
2. **Se descartan**, indicando el motivo en la propia alerta, las que afectan
   únicamente a *dependencias de desarrollo* — linters, empaquetadores,
   servidores de desarrollo, frameworks de test — porque no forman parte de
   ningún artefacto distribuible.
3. **Se descartan** igualmente las de proyectos archivados o experimentales
   que no se ejecutan.

El descarte es una decisión explícita y registrada, no un descuido. Si alguno
de estos proyectos pasara a desplegarse, sus alertas deberían revisarse de
nuevo bajo el criterio 1.

**No se descartan** las alertas que sí tienen intención de arreglarse pero
cuya corrección depende de terceros — por ejemplo, dependencias transitivas
del sistema de compilación de Angular, que solo se resuelven cuando el
framework actualiza las suyas. Esas se dejan abiertas a propósito: son el
recordatorio de una tarea pendiente, y GitHub las cerrará automáticamente
cuando la actualización llegue. Descartarlas las ocultaría sin resolverlas.

---

## 2026-07-03 / 2026-07-05 — Reestructuración del monorepo

- Política de fin de línea unificada en `.gitattributes` (`* text=auto`,
  CRLF para scripts de Windows, LF para shell) y renormalización completa.
- Anidamientos de carpetas redundantes aplanados.
- Reorganización por ecosistema: `NodeJS/{JavaScript,TypeScript}` → `JS/`,
  `Laravel/` → `PHP/`, TaskHub de Python bajo `Python/FastApi/`.
- Artefactos de runtime fuera del control de versiones; `.gitignore`
  ampliado con reglas acotadas por ruta.
- README raíz convertido en catálogo de proyectos; hoja de ruta en
  `ROADMAP.md`; notas sueltas reubicadas en `docs/` por proyecto.
