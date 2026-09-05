# Auditoría de TaskHub_React

Fecha: 4 de septiembre de 2026 · Estado del proyecto tras cerrar el bloque de
seguridad, sesiones y cobertura.

Este documento consolida cuatro auditorías previas —una de seguridad y CI/CD, una
integral, y dos revisiones test a test— en un único informe del **estado actual**.
Los cuatro documentos originales se retiraron del repositorio: contenían
coordenadas de defectos ya corregidos, y publicar dónde estuvo cada fallo es
dibujar un mapa hacia los commits anteriores al arreglo. Aquí se conserva **el
razonamiento**, que es lo que tiene valor, sin las coordenadas.

> **Sobre qué se publica y qué no.** Este repositorio es público. La auditoría
> describe con detalle lo que está **corregido**, porque explicar por qué se
> tomó cada decisión es justamente el interés de un proyecto de portfolio. Lo
> que sigue **pendiente** se enuncia como trabajo por hacer, sin detalle de
> explotación: un informe público no debe funcionar como guía de ataque contra
> el despliegue vivo. Ningún apartado incluye credenciales, valores de variables
> de entorno, identificadores reales de la base de datos ni rutas concretas de
> defectos históricos.

---

## 1. Resumen

TaskHub es una aplicación de gestión de tareas con autenticación, roles y panel
de administración. Está **por encima de la media de un proyecto de portfolio** y
por debajo de lo que se despliega con usuarios reales y guardias de veinticuatro
horas.

El recorrido de las últimas semanas ha sido, en orden: cerrar los agujeros de
configuración (cabeceras, CORS, secreto de firma), sustituir la sesión de siete
días por una arquitectura de tokens revocable, endurecer la política de
contraseñas, y por último **cerrar la brecha entre «el código es correcto» y
«algo vigila que siga siéndolo»**, que era el verdadero hallazgo de la auditoría
integral.

**Valoración global: 8,9 / 10.** El desglose, en la sección 9.

### Lo que ha cambiado desde la primera auditoría

| | 30 de agosto | Hoy |
|---|---|---|
| Sesión | JWT único de 7 días, sin revocación | Access de 15 min + refresh rotativo revocable |
| Contraseñas | Mínimo 6 caracteres | 15 caracteres, lista de bloqueo y composición |
| Cabeceras HTTP | Ninguna | `helmet` con CSP a medida y HSTS |
| CORS | Abierto a cualquier origen | Delegado de mismo origen |
| Tests | 37 comprobaciones de API | **962** en cuatro capas |
| Cobertura del servidor | No medida | **99,6 %** de la lógica pura, con umbral en el CI |
| Cobertura del cliente | No medida | **96,9 %**, con umbral |
| Interfaz | Estilos por defecto, sin tokens | Sistema de tokens, modo oscuro y foco de teclado visible |
| CI | No existía | 9 jobs con puerta `ci-ok` |
| Vulnerabilidades | 1 alta (cliente) | **0** |
| Eventos de seguridad | Ninguno | Registro estructurado en los puntos clave |
| Cambio de contraseña | No existía | Con revocación global y sesión nueva para el dispositivo actual |
| Límite de intentos | Solo por IP | Tres capas: IP, retrasos progresivos por cuenta y tope duro lejano |

---

## 2. Arquitectura

| Capa | Tecnología | Notas |
|---|---|---|
| Frontend | React 18 + Vite | 6 componentes, 1 contexto, 2 servicios |
| Backend | Express 4 + TypeScript | `router → controller → service → repository` |
| Base de datos | PostgreSQL vía `pg` | SQL a mano, sin ORM, todo parametrizado |
| Esquema | DDL idempotente en TypeScript | 3 tablas: `users`, `tasks`, `refresh_sessions` |
| Sesión | JWT HS256 + cookie HttpOnly | Access 15 min, refresh 7 días rotativo |
| Despliegue | Render + Neon | Proceso único: cliente, playground y API |
| CI | GitHub Actions, 9 jobs | `ci-ok` como puerta final; el despliegue depende de ella |

**Endpoints:** 5 de autenticación, 7 de tareas, 3 de administración, 2 públicos.

El aislamiento entre usuarios no se resuelve con comprobaciones posteriores sino
metiendo `user_id` en el `WHERE` de todas las consultas. Es la diferencia entre
«se comprueba que el recurso es tuyo» y «un recurso ajeno no existe para ti»: la
segunda no se puede olvidar en una rama concreta.

---

## 3. Diseño de la sesión

Es la parte más trabajada del proyecto y merece su apartado.

**El problema del diseño anterior.** Un JWT de siete días guardado en
`localStorage` no se puede revocar. Cerrar sesión borraba el token del navegador,
pero el token seguía siendo válido: quien tuviera una copia entraba durante los
días restantes. No había ningún mecanismo para echar a nadie.

**Lo que hay ahora.** Dos credenciales con papeles distintos:

- **Access token**, JWT de quince minutos, con `typ: 'access'` e identificador
  único. Viaja en la cabecera `Authorization`. El cliente lo necesita en
  JavaScript, así que se asume que es legible desde la página; dura poco
  justamente por eso.
- **Refresh token**, 32 bytes opacos, siete días, en cookie `HttpOnly` con
  `SameSite=Strict` y limitada a la ruta de autenticación. En la base de datos
  solo se guarda su hash SHA-256: una copia de la tabla no sirve para entrar.

**Rotación con detección de reutilización.** Cada renovación invalida el token
usado y emite uno nuevo dentro de la misma *familia*. Si aparece un token ya
rotado, hay dos explicaciones posibles y el servidor las distingue:

- Dentro de una **ventana de gracia de diez segundos**, es una carrera entre dos
  pestañas del mismo usuario renovando a la vez. Se rechaza la petición y no se
  toca nada más.
- Fuera de esa ventana, es una reutilización: alguien tiene una copia. Se revoca
  **la familia entera**, lo que echa tanto al atacante como al usuario legítimo.

La comparación en el borde exacto es `<=`, es decir, en la duda se protege al
usuario legítimo. Echar a alguien de su sesión es un problema real; que un
atacante acierte el milisegundo exacto es una hipótesis.

**CSRF.** Introducir una cookie abre la puerta al CSRF, y se cierra por tres vías
independientes: `SameSite=Strict` impide que el navegador la mande desde otro
sitio, la cookie está limitada a la ruta de autenticación, y ninguna ruta de
datos la mira —todas exigen la cabecera `Authorization`, que una petición
cross-site no puede fijar—.

**Cambio de contraseña.** Cierra el hueco más raro que tenía el proyecto: se
había construido rotación, detección de reutilización y revocación por familias,
y un usuario que sospechara que le habían robado la contraseña no podía hacer
absolutamente nada.

Se pide la contraseña **actual** aunque ya haya sesión, y no es burocracia: sin
ese requisito, un token de acceso robado permitiría quedarse con la cuenta para
siempre. Con él, el robo dura quince minutos.

Al cambiarla se revocan **todas** las sesiones —marcadas con el motivo
`password-changed`, distinto de un cierre normal— y acto seguido se abre una
nueva para el dispositivo actual. Revocar sin más habría expulsado al usuario
justo después de hacer lo correcto, y una medida de seguridad incómoda es una
medida que la gente evita. El orden importa y está fijado por un test: primero
revocar, después crear; al revés se revocaría la sesión recién abierta.

Un detalle del esquema que casi pasa desapercibido: la columna `revoked_reason`
tenía una restricción `CHECK` con la lista cerrada de motivos anteriores. En una
base de datos recién creada —como la de los tests— el motivo nuevo habría pasado
sin problema; en una que ya existe, `CREATE TABLE IF NOT EXISTS` no toca la
restricción vieja y el primer cambio de contraseña habría fallado **solo en
producción**. Se añadió una migración explícita que la rehace, y se verificó
contra PostgreSQL real.

**Limitación de intentos: el rodeo que mereció la pena.** La primera versión fue
un contador por cuenta con bloqueo duro a los veinte intentos. Resolvía el
problema que tenía —el limitador por IP no frena a quien reparte el ataque entre
mil direcciones, porque ninguna agota su cuota— e introducía otro: si bloquear
es posible, cualquiera que sepa un nombre de usuario puede provocarlo aposta.

Se documentó como compromiso asumido. Pero el compromiso no hacía falta: el
problema no era el umbral sino el mecanismo. Un bloqueo es un binario, y
cualquier binario que un atacante pueda forzar acaba siendo un arma; subir el
número solo desplaza dónde está el borde.

La versión definitiva **retrasa en lugar de denegar**, con la curva creciendo
desde el cuarto fallo hasta un techo de treinta segundos. Quien conoce su
contraseña no nota nada; quien prueba a ciegas pasa de miles de intentos por
minuto a menos de ciento veinte por hora. Y nadie queda bloqueado, porque ya no
existe el estado que provocar. El tope duro se conserva a doscientos como red de
seguridad, tan lejos que alcanzarlo exige más de una hora de martilleo.

La curva se fija con tests unitarios sobre la función pura que la calcula —que
sea monótona, que respete el techo, que la fuerza bruta quede por debajo de
cierto ritmo—. Medir esperas reales habría dado un test lento y frágil sin
comprobar nada más.

Un apunte de proceso: al extraer esa función, el umbral de cobertura **detectó
que la lambda original quedaba sin probar** y puso el CI en rojo. Estaba escrita
dentro de la configuración del middleware, donde solo la ejecuta la librería en
tiempo de petición. Se extrajo con nombre y se cubrió. Es justo el trabajo para
el que está puesto el trinquete.

**Lo que esto cuesta.** El middleware de autenticación no consulta la base de
datos: valida la firma y sigue. Eso hace que cada petición sea barata, a cambio
de una ventana de hasta quince minutos entre que se revoca una cuenta y deja de
funcionar su access token. Es una decisión consciente, y el borrado de un usuario
revoca sus sesiones explícitamente para acortarla.

---

## 4. Política de contraseñas

Mínimo **15 caracteres**, lista de bloqueo de contraseñas comunes, rechazo de
caracteres repetidos, secuencias y patrones previsibles, comparación contra el
nombre de usuario, y **reglas de composición** (mayúscula, dígito y símbolo).

**Sobre la alineación con NIST.** El mínimo de 15 caracteres y la lista de
bloqueo siguen la recomendación de NIST SP 800-63B. Las reglas de composición
**no**: esa guía las desaconseja expresamente, porque empujan a la gente hacia
`Password1!` y variantes. Son una **decisión propia de este proyecto**, tomada a
sabiendas de que se aparta de la recomendación, y compensada con la lista de
bloqueo, que cubre justamente los patrones que las reglas de composición
fomentan. Se documenta así para que nadie lea el código y concluya que NIST exige
algo que no exige.

Un detalle que salió de los tests: la comprobación de patrones previsibles
quitaba los caracteres no alfabéticos antes de comparar, de modo que una
sustitución de estilo *leet* podía colar una palabra común disfrazada. Se
corrigió deshaciendo las sustituciones y probando varias normalizaciones, porque
el relleno y la sustitución se estorban entre sí. Lo detectó un test escrito para
ese caso, no una revisión a ojo.

---

## 5. OWASP Top 10 — estado actual

| Categoría | Estado | Detalle |
|---|---|---|
| **A01 Broken Access Control** | ✅ | `user_id` en el `WHERE` de todas las consultas. El rol se lee de la base de datos en cada petición, nunca del JWT, para que retirar un permiso tenga efecto inmediato. Cubierto por comprobaciones cruzadas de escritura que verifican la fila en base de datos, no solo el código de estado |
| **A02 Cryptographic Failures** | ✅ | bcrypt con 12 rondas. SHA-256 sin sal para el refresco, correcto por ser una credencial de alta entropía. HS256 declarado explícitamente al firmar **y al verificar**. Secreto de firma obligatorio y validado en producción |
| **A03 Injection** | ✅ | Todo parametrizado. El único elemento dinámico del SQL es una lista blanca de nombres de columna, que es el patrón correcto cuando lo dinámico es estructural. Comodines de `LIKE` escapados con `ESCAPE` explícito. Cargas de inyección probadas en la suite de API |
| **A04 Insecure Design** | ⚠️ | Ya hay **cambio de contraseña** con revocación global. Siguen sin existir recuperación por correo ni verificación, porque el modelo de datos no guarda direcciones: es una ausencia conocida y acotada, no un defecto |
| **A05 Security Misconfiguration** | ✅ | `helmet` con CSP a medida, HSTS en producción, `trust proxy` acotado, CORS de mismo origen, cuerpo limitado. `script-src` es `'self'` y `script-src-attr` es `'none'`: la política ya no admite código en línea, que es la concesión que la dejaba sin defender de la inyección de scripts |
| **A06 Vulnerable Components** | ✅ | **0 vulnerabilidades** en cliente y servidor |
| **A07 Identification & Auth Failures** | ✅ | Rotación con detección de reutilización, revocación en servidor, política de contraseñas descrita arriba, y **tres capas de limitación**: por IP, retrasos progresivos por cuenta y tope duro. Cierra el ataque repartido entre muchas direcciones sin abrir un bloqueo malicioso |
| **A08 Software & Data Integrity** | ⚠️ | Las acciones del CI están fijadas a etiqueta mayor, no a SHA. Son acciones oficiales; el riesgo es bajo pero una etiqueta se puede mover |
| **A09 Logging & Monitoring** | ⚠️ | Era el punto más flojo y ha mejorado mucho: hoy se registran los eventos de seguridad relevantes en formato estructurado, con redacción automática de cualquier campo que parezca una credencial. Falta la capa de agregación y alertas, que ya no es código de aplicación |
| **A10 SSRF** | ✅ | No aplica: el servidor no hace peticiones salientes |

**XSS.** React escapa por defecto y no hay ni un `dangerouslySetInnerHTML`. El
playground, que es HTML plano sin escapado automático, construye la consola con
nodos de texto y pasa por una función de escapado todo lo que va a `innerHTML`.
Sin hallazgos.

**Secretos.** No hay ningún `.env` versionado; el de ejemplo solo tiene
marcadores. Ningún secreto en el workflow de CI. Sin hallazgos.

---

## 6. Interfaz y accesibilidad

Era el punto ciego del proyecto: ninguna de las cuatro auditorías anteriores
había mirado ni la interfaz ni la accesibilidad, pese a ser una aplicación React
llena de formularios. Y es lo primero que ve cualquiera que abra el enlace de la
demo, antes de leer una línea de este documento.

**El diagnóstico.** El CSS funcionaba y estaba escrito a mano, pero tenía unos
cuarenta valores hexadecimales sueltos repetidos por la hoja, ni una media
query, y ningún estilo de foco propio. La pantalla de acceso eran dos campos sin
marca ni contexto: quien llegaba desde un enlace no sabía qué era esto ni por
qué debería crearse una cuenta.

**Lo que se hizo.**

- **Tokens de color en `index.css`.** Todo el color sale de variables. El modo
  oscuro es lo que obliga a ello: cada valor existe en dos versiones, y la única
  forma de que no se desincronicen es que el componente no sepa cuál está
  usando. No hay una sola regla duplicada entre temas.
- **Acento gris, no azul de marca.** En un gestor de tareas el color tiene que
  quedar disponible para decir algo —qué está pendiente, qué es urgente—. Una
  interfaz ya coloreada de serie apaga esas señales. El azul se reserva para el
  anillo de foco, donde sí hace falta que destaque.
- **El tema distingue tres estados, no dos:** claro, oscuro y «no ha elegido».
  Sin esa distinción, quien tiene el sistema en oscuro recibe un fogonazo blanco
  al abrir. Mientras no haya elección explícita manda `prefers-color-scheme`.

**Accesibilidad.** El foco de teclado era un **defecto real**, no una cuestión
de gusto: los botones llevan fondo propio y sobre él se pierde el anillo por
defecto del navegador, así que quien navega con teclado no sabía dónde estaba.
Se resolvió con `:focus-visible` —que sale al tabular pero no al hacer clic, que
es cuando estorba y lleva a quitarlo con `outline: none`—. Además: ningún estado
depende solo del color, los botones sin texto tienen nombre accesible que
describe la acción y no el estado, y se respeta `prefers-reduced-motion`.

**Lo que NO se ha hecho, y conviene no dar por hecho.** No se ha pasado ningún
validador automático de accesibilidad, ni se ha probado con un lector de
pantalla real, ni se han medido los contrastes con una herramienta. Lo anterior
es lo que se cuidó al escribir el código; no es un certificado de conformidad
con las WCAG, y este documento no va a insinuar que lo sea.

---

## 7. Tests

**962 comprobaciones** en cuatro capas que prueban cosas distintas:

| Suite | Cuántas | Cobertura | Umbral | Necesita |
|---|---:|---|---|---|
| Unitarios de servidor | 548 | **99,5 %** stmts · 99,0 % ramas | 99/98/98/99 | Nada |
| Unitarios de cliente | 224 | **96,5 %** stmts · 96,6 % ramas | 95/94/93/96 | Nada |
| API contra PostgreSQL | 154 | — | — | PostgreSQL |
| Navegador (Playwright) | 36 | — | — | PostgreSQL y build |

**Qué mide el 99,5 % y qué no.** Solo la lógica que corre sin base de datos. Los
repositorios, los routers y el cableado de Express están excluidos a propósito
porque quien los ejercita es la suite de API contra PostgreSQL real. Un 99,5 %
ahí no significa que el servidor entero esté probado al 99,5 %, y el documento no
lo va a insinuar.

**Por qué los umbrales importan más que los porcentajes.** El hallazgo de la
auditoría integral no fue que la cobertura del servidor fuera baja: fue que **no
se medía en ninguna parte**. El cliente tenía trinquete y el servidor no, así que
una rama nueva sin cubrir entraba sin que nada avisara. Hoy los dos lo tienen, y
los umbrales están justo por debajo de la cifra real para que bajar la cobertura
ponga el CI en rojo.

**El 100 % no es el objetivo**, y está escrito en la configuración para que nadie
lo intente. Llegar al último punto obliga a escribir tests que existen para mover
el contador y no para detectar fallos, y esos son peores que la línea sin cubrir
que sustituyen. Lo que queda fuera son ramas defensivas que no se alcanzan sin
retorcer los dobles hasta que el test deje de significar nada.

### Lo que una cabecera correcta no demuestra

El endurecimiento de la CSP dejó un aviso que merece quedar escrito, porque no
se arregla con más tests sino con tests de otro tipo.

Al retirar `'unsafe-inline'` se añadieron comprobaciones de la política: que
`script-src` fuera `'self'`, que `script-src-attr` fuera `'none'`, que el
marcado no llevara ningún atributo `on*`, que el HTML cargara su lógica de un
fichero. Las cinco pasaron. Y las cinco pasaban sobre una página cuyo
JavaScript el navegador **no llegaba a ejecutar**: el `<script>` tenía una ruta
relativa, la página se sirve en `/playground` sin barra final, y el navegador
pedía `/app.js`, donde no hay nada. El playground se pintaba entero y no
respondía a un solo clic.

Ninguna de esas cinco comprobaciones podía detectarlo, porque todas miran
cabeceras y marcado —lo que el servidor dice— y ninguna mira comportamiento —lo
que el navegador hace—. Lo detectaron los cinco tests de Playwright, que son los
únicos que abren un navegador de verdad. Una comprobación que solo lee la
respuesta del servidor confirma que la configuración es la que se escribió, no
que la página funcione bajo ella.

De ahí salieron tres comprobaciones más, que son las que cierran el hueco sin
depender de que un e2e pulse el botón concreto que se rompa: la URL del script
se **resuelve** contra la dirección de la página como haría el navegador en vez
de escribirse a mano; toda acción del marcado tiene manejador en la tabla de
delegación y ningún manejador sobra; y los cinco oyentes que se enganchan por
`id` encuentran su elemento, porque si uno falta el `TypeError` corta el
arranque en silencio.

### Tests que se revisaron uno a uno

Las dos auditorías test a test —una tras el cambio de política de contraseñas,
otra tras la migración de sesión— revisaron las 229 y las 344 comprobaciones de
entonces individualmente, no mirando el resultado de la suite. Encontraron cosas
que un `npm test` en verde nunca habría delatado:

- **Un test que se quedó en verde midiendo otra cosa.** Firmaba un JWT a mano
  para comprobar que un identificador inexistente no devolvía datos ajenos. Al
  añadirse un claim nuevo al diseño de tokens, el middleware empezó a cortar ese
  JWT antes de llegar a la consulta. El test seguía pasando —recibía un 401— pero
  la petición ya no llegaba a lo que decía probar.
- **Un falso positivo en un test de concurrencia.** Lanzaba dos renovaciones en
  paralelo y comprobaba que solo una respondiera correctamente. Pasaba, pero
  pasaba porque el motor de base de datos del entorno de desarrollo solo admite
  una conexión y tumbaba la segunda petición, no porque el guardián de la
  rotación funcionara. Se sustituyó por una comprobación determinista.
- **Un test intermitente en el borde de la ventana de gracia.** Calculaba la
  marca de tiempo al preparar el doble y el servicio hacía la resta unos
  milisegundos después, así que caía del lado equivocado salvo que las dos
  lecturas del reloj coincidieran en el mismo milisegundo. Tardó tres
  ejecuciones en delatarse. Ahora congela el reloj.
- **Ocho tests que afirmaban lo contrario de la política nueva.** Existían para
  impedir que alguien añadiera reglas de composición sin pensarlo. Cumplieron su
  función: al cambiar la política fallaron y obligaron a tomar la decisión de
  forma consciente. Se sustituyeron por sus equivalentes inversos, no se
  borraron.

Ese es el argumento a favor de revisar los tests uno a uno de vez en cuando: la
suite en verde no distingue entre un test que protege algo y un test que ya no
mide nada.

---

## 8. Defectos corregidos

Los que encontró la auditoría integral, con lo que se hizo. Se describen por su
efecto, no por su ubicación.

| Defecto | Efecto | Solución |
|---|---|---|
| Identificadores sin validar | Un identificador mal formado acababa en error 500 en cinco rutas, en vez de en un 400 limpio. Ruido en métricas y alertas falsas | Validador de formato en el router, con sus tests |
| Sesión incoherente al borrar una cuenta | Una operación posterior podía fallar por una violación de integridad en vez de responder 401 | Traducción del error a 401, y revocación explícita de sesiones al borrar |
| Tabla de sesiones sin limpiar | La función de limpieza estaba escrita, documentada y probada… y no la llamaba nadie. Crecimiento indefinido | Tarea diaria al arrancar, con sus tests |
| CSP con `'unsafe-inline'` en `script-src` | La política estaba puesta, se veía en las cabeceras y no defendía de la inyección de scripts, que es lo único que se le pide. La concesión existía porque el playground llevaba toda su lógica en un `<script>` y sus manejadores en atributos `onclick` | Lógica extraída a `public/app.js`, 21 manejadores convertidos en `addEventListener` y los 2 que se generan al pintar cada tarea resueltos por delegación. `script-src 'self'` y `script-src-attr 'none'` |
| Sin límites de longitud | Descripción y búsqueda sin techo explícito. El de la búsqueda importaba más: va a una consulta que no puede usar índice | Límites explícitos en los validadores |
| Comentario desactualizado | Describía la configuración anterior a la migración de sesión. El tipo de comentario que alguien lee y da por cierto | Corregido |
| El hash de contraseña viajaba sin necesidad | No salía en la respuesta, pero llegaba desde la base de datos a memoria sin motivo | Se dejó de seleccionar en la consulta |
| Promesa rechazada sin capturar | Tumbaba el proceso sin cerrar el pool de conexiones | Manejadores de `unhandledRejection` y `uncaughtException` |
| Vulnerabilidades de dependencias | Tres moderadas en una cadena transitiva | Resueltas fijando la versión parcheada. **Rectificación:** en la auditoría integral escribí que solo Express 5 las cerraba; era incorrecto |
| bcrypt con 10 rondas | Era el estándar de 2015 | Subido a 12. Los hashes anteriores siguen validando |
| Sin tests de escritura cruzada | El aislamiento funcionaba, pero nada lo vigilaba: un refactor podía romperlo con el CI en verde | Comprobaciones cruzadas que verifican la fila en base de datos |
| Sin eventos de seguridad | Un ataque de fuerza bruta era invisible | Registro estructurado con redacción automática de credenciales |

Sobre el último punto, un detalle que ilustra por qué los filtros de redacción
necesitan sus propios tests: el primer filtro censuraba por nombre de campo, y
acabó tachando un **contador** de sesiones revocadas porque su nombre contenía
una palabra de la lista. Se corrigió censurando solo valores de texto —una
credencial siempre es una cadena, un recuento nunca—. Lo detectó su propio test.

---

## 9. Puntuación

| Área | Nota | Justificación |
|---|---:|---|
| Arquitectura | 8/10 | Capas limpias y coherentes. Penalizan la semántica de `PUT` y la falta de paginación |
| Backend | 9/10 | Sólido y comentado explicando el porqué. Los defectos de la auditoría están cerrados |
| Frontend | 9/10 | 96,9 % de cobertura, renovación transparente, actualización optimista con reversión, sistema de tokens con modo oscuro y foco de teclado visible |
| Base de datos | 9/10 | Índices correctos, unicidad por índice, cascadas bien puestas, SQL parametrizado |
| Autenticación | 9,5/10 | Lo mejor del proyecto. Rotación, detección de reutilización, revocación, cambio de contraseña con revocación global, CSRF cerrado por tres vías |
| Autorización | 9/10 | El código era correcto desde el principio; ahora además está vigilado en escritura |
| Seguridad | 9/10 | Sin vulnerabilidad explotable encontrada, 0 dependencias vulnerables, registro de eventos, y límite de intentos por IP y por cuenta. Falta la capa de alertas |
| Testing | 9/10 | 962 comprobaciones, cobertura medida y con umbral en las dos suites unitarias, y tests revisados uno a uno |
| E2E | 8,5/10 | 36 pruebas del ciclo completo, incluidas renovación y revocación |
| CI/CD | 9/10 | Nueve jobs, permisos mínimos, sin exposición a forks, cobertura de las dos suites, despliegue encadenado a `ci-ok`, y el job espera al estado final del despliegue y comprueba que la aplicación responde. Falta fijar las acciones a SHA y exigir que las ramas estén al día antes de fusionar |
| DevOps | 6,5/10 | Despliegue automático que funciona, pero sin entornos separados ni rollback documentado |
| Mantenibilidad | 9,5/10 | Los comentarios explican **por qué**, no qué. Las decisiones se entienden sin arqueología en el historial |
| Documentación | 9/10 | README exhaustivo y este informe. Por encima de lo habitual |

### **TaskHub: 8,9 / 10**

Media ponderada dando más peso a seguridad, testing y autorización.

**No es un 10 porque** el despliegue no está encadenado al CI, no hay entornos
separados ni rollback documentado, falta la capa de observabilidad por encima del
registro, y no existen pruebas de resiliencia ante una caída de la base de datos.

**No es un 7 porque** la autenticación está a nivel profesional, no se ha
encontrado ninguna vulnerabilidad explotable, la cobertura está medida y
defendida con umbrales en las dos suites unitarias, y los tests han demostrado
—en cuatro ocasiones documentadas— que detectan fallos reales en lugar de
acompañar al código.

---

## 10. Pendiente

Enunciado como trabajo por hacer. Sin detalle de explotación, por lo dicho al
principio.

### Alto

1. ~~**Confirmar el despliegue, no solo pedirlo.**~~ Resuelto: el job lanza el
   despliegue por la API de Render —que devuelve su identificador—, espera al
   estado final aceptando solo `live`, y después comprueba que `/api/health`
   responde en la URL pública. Un fallo de compilación dentro de Render deja
   ahora el CI en rojo, cosa que antes no pasaba.
2. **Configuración fuera del repositorio.** Queda comprobar dos de los tres
   pasos, porque no viven en el código: que Auto-Deploy siga desactivado en
   Render y que `RENDER_API_KEY` y `RENDER_SERVICE_ID` estén guardados como
   secretos. El tercero —exigir `ci-ok` en la rama principal— **está hecho**,
   mediante el *ruleset* 22286987 del repositorio. Conviene anotar que el
   endpoint de protección de rama clásica responde «Branch not protected»
   aunque las reglas existan, porque induce a pensar que falta.
3. **Las ramas pueden fusionarse desactualizadas.** El ruleset tiene
   `strict_required_status_checks_policy` en `false`, así que una PR puede
   entrar en verde sin estar al día con `main`. Sus comprobaciones pasaron
   contra un estado anterior, de modo que `main` puede romperse por un
   conflicto semántico que nadie vio en rojo. Es la misma familia de problema
   que el resto de esta lista: un verde que no significa lo que parece.

### Medio

4. **Recuperación de contraseña por correo.** El modelo de datos no guarda
   direcciones —las columnas de `users` son `id`, `username`, `password_hash`,
   `role` y `created_at`—, así que exige añadir el campo, decidir qué pasa con
   las cuentas existentes y contratar un proveedor de envío con dominio
   verificado. Es más infraestructura que código.
5. Fijar las acciones del CI a SHA en lugar de a etiqueta mayor. De paso,
   conviven dos versiones distintas entre workflows —`actions/checkout@v4` y
   `@v5`, `actions/setup-node@v4` y `@v5`—, que se pueden unificar al fijarlas.
6. Registrar el mensaje y el código del error en vez del objeto completo.
   Comprobado: `error.middleware.ts` hace `console.error('[unhandled]', err)`,
   que vuelca el objeto entero.
7. Revisar qué se escribe del contenido de las peticiones en el registro de
   acceso. Comprobado, y más acotado de lo que decía esta lista: solo se
   registran método, URL, código y duración. Lo que queda por decidir es que la
   URL arrastra la cadena de consulta, así que los términos de búsqueda del
   usuario acaban en el registro.

### Bajo

8. `PUT` con semántica correcta —reemplazo completo— o retirarlo, con sus tests.
   Comprobado: `tasks.router.ts` enruta `put` y `patch` al mismo
   `tasksController.update`.
9. Paginación en el listado de tareas. Comprobado: no hay `LIMIT` ni `OFFSET`
   en el repositorio de tareas.
10. ~~**Cambio de contraseña, con revocación de todas las sesiones.**~~
    Resuelto hace varias revisiones: está implementado, descrito en A04 y
    cubierto por una docena de comprobaciones de `verify`. Seguía en esta lista
    por inercia.
11. ~~**`taskhub: file:..` reaparecía en el entorno de desarrollo.**~~ Resuelto:
    la contaminación estaba en el `node_modules` local, no en lo commiteado.
    Borrados los enlaces y reinstalado con `npm ci` —que no escribe en
    `package.json` ni en el lock—, el árbol queda limpio. La causa de fondo, por
    qué `npm install` lo declaraba en Windows, no llegó a identificarse.
    Detalle en `MAINTENANCE.md`.

### Mejoras

12. **Validar la accesibilidad con herramientas, no solo con criterio.**
   Pasar axe o Lighthouse, medir contrastes y probar con un lector de pantalla.
   Lo hecho hasta ahora se cuidó al escribir el código, que no es lo mismo que
   estar verificado.
13. Registro estructurado con identificador de correlación por petición.
14. Métricas y alertas por encima del registro.
15. Pruebas de resiliencia: caída de la base de datos, tiempos de espera.
16. Panel de sesiones activas para el usuario.

---

## 11. Evidencia de ejecución

Comprobado en esta auditoría, no supuesto:

| Comprobación | Resultado |
|---|---|
| ESLint | ✅ 0 problemas |
| TypeScript `--noEmit` | ✅ 0 errores |
| Build | ✅ Playground y cliente |
| Unitarios de servidor | ✅ 548/548 |
| Cobertura de servidor | ✅ 99,58 / 98,77 / 98,80 / 99,56 |
| Unitarios de cliente | ✅ 224/224 |
| API contra PostgreSQL | ✅ 154/154 |
| Navegador (Playwright) | ✅ 36/36 *(ejecutado fuera del entorno de auditoría, que no puede descargar Chromium)* |
| `npm audit` cliente y servidor | ✅ 0 vulnerabilidades |
| Búsqueda de secretos en el repositorio | ✅ Sin hallazgos |
| Búsqueda de XSS | ✅ Sin hallazgos |
| Despliegue confirmado en producción | ✅ `dep-dae7sv1t0dsc7395so80`: lanzado, seguido hasta `live` y `/api/health` respondiendo 200 |
| CSP en producción | ✅ `script-src 'self'` sin `'unsafe-inline'`, y el playground cargando `/playground/app.js` |

---

## 12. Qué sería un 10

No es «que pasen los tests».

| Dimensión | Criterio |
|---|---|
| **Seguridad** | Sin vulnerabilidades conocidas; eventos registrados **y vigilados**; límites por cuenta y por origen; rotación de secretos documentada |
| **Arquitectura** | Semántica HTTP correcta; paginación; cada regla de negocio en un solo sitio |
| **Testing** | Cobertura medida y con umbral en las cuatro capas; ningún test que pase con el código roto |
| **Observabilidad** | Registro estructurado, correlación por petición, métricas, alertas |
| **CI/CD** | Despliegue encadenado; rama protegida; acciones fijadas a SHA |
| **Resiliencia** | Degradación controlada, tiempos de espera, rollback probado |

La diferencia entre **«funciona»** y **«está preparado»** es que en el segundo
caso, cuando algo se rompe a las tres de la mañana, hay un registro que dice qué
pasó y una alerta que avisó antes.
