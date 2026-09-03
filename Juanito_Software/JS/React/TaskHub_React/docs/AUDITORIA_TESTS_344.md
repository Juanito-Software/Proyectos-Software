# Auditoría de los 344 tests tras la migración a access + refresh tokens

Fecha: 3 de septiembre de 2026 · Rama `main` · Base: commit `b6d0989`

Revisión de los 344 tests que existían antes del cambio, uno a uno, para
comprobar que cada uno sigue probando algo cierto sobre la arquitectura actual.

La pregunta no es si pasan, sino si siguen midiendo lo que dicen medir. Un test
puede quedarse en verde y estar comprobando un mecanismo que ya no existe.

## Resumen

| Estado | Tests |
|---|---|
| PASS | 310 |
| BLOCKED | 25 |
| UPDATED | 14 |
Los 25 **BLOCKED** son los de navegador: Playwright no puede descargar Chromium
en el entorno de esta auditoría, así que se han revisado por lectura pero **no
se han ejecutado**. Cinco de ellos están además marcados como UPDATED, por eso
las columnas suman más de 344.

Sin tests **INVALID**, **WEAK**, **REDUNDANT** ni **FAIL**. Ninguno se ha
borrado, desactivado ni debilitado.

## Por qué tan pocos cambios

La migración no cambió el contrato de la aplicación, solo el mecanismo de la
sesión. El cliente sigue mandando `Authorization: Bearer <token>`, la API sigue
respondiendo con el mismo sobre y las tareas, los filtros y la administración
funcionan igual. De ahí que 310 de los 344 no necesitaran tocarse.

Los 14 **UPDATED** se reparten en dos causas:

- **Doce por el cambio de nombre del campo.** El cuerpo de la respuesta pasó de
  `token` a `accessToken`, porque ahora hay dos tipos de credencial y llamar
  «token» a una de las dos sería ambiguo.
- **Uno por el logout**, que dejó de ser un cambio de estado local para
  convertirse en una llamada al servidor.
- **Uno que merece explicación aparte**, abajo.

## El test que se habría quedado en verde midiendo otra cosa

`Token de un usuario inexistente no devuelve datos ajenos` firmaba un JWT a mano
para comprobar que un identificador que no está en la base de datos no devuelve
datos de nadie. Ese JWT no llevaba el claim `typ`, que no existía cuando se
escribió.

Con la política nueva, el middleware corta cualquier token sin `typ` antes de
llegar al repositorio. El test seguía pasando —recibía un 401, no datos ajenos—
pero ya no probaba lo que dice probar: la petición nunca alcanzaba la consulta.
Se añadió el claim para que el token vuelva a llegar hasta el final.

Es exactamente el caso que justifica revisar los tests uno a uno en lugar de
mirar solo el resultado de la suite.

## Un falso positivo detectado al escribir los tests nuevos

El primer test de concurrencia lanzaba dos renovaciones en paralelo con
`Promise.all` y comprobaba que solo una respondiera 200. Pasaba. Pero pasaba
porque el driver de base de datos del entorno de desarrollo solo admite una
conexión y tumbaba la segunda petición con `connection terminated` — no porque
el guardián de la rotación funcionara.

Se sustituyó por una comprobación determinista: dos llamadas seguidas a
`marcarRotado` con el mismo token, de las que la segunda tiene que devolver
`null`. Eso sí prueba el mecanismo, y además funciona en cualquier entorno.

## Tabla completa


### Sin cambios (238 tests)

Ninguno de estos toca la emisión ni la validación de credenciales, así que la migración no los afecta. Todos ejecutados y en verde.

| Archivo | Tipo | Tests | Código probado | Estado |
|---|---|---|---|---|
| `server/.../password-policy.test.ts` | Unitario | 73 | política de contraseñas | **PASS** |
| `server/.../auth.validation.test.ts` | Unitario | 30 | validadores de registro y login | **PASS** |
| `server/.../tasks.validation.test.ts` | Unitario | 25 | validadores de tareas | **PASS** |
| `server/.../tasks.repository.test.ts` | Unitario | 13 | escapado LIKE y campo calculado | **PASS** |
| `server/.../rateLimit.middleware.test.ts` | Unitario | 8 | límite de intentos | **PASS** |
| `client/.../AuthForm.test.jsx` | Componente | 32 | formulario de acceso | **PASS** |
| `client/src/passwordPolicy.test.js` | Componente | 22 | política replicada en cliente | **PASS** |
| `client/.../TaskForm.test.jsx` | Componente | 9 | formulario de tarea | **PASS** |
| `client/.../TaskItem.test.jsx` | Componente | 10 | tarjeta de tarea | **PASS** |
| `client/.../api.test.js` | Componente | 16 | capa de servicios de tareas | **PASS** |

### `server/src/verify.ts` — suite de API contra PostgreSQL

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 239 | POST /api/auth/register | API | **UPDATED** | registro | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 240 | POST /api/auth/login | API | **PASS** | login | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 241 | GET /api/tasks sin token -> 401 con success:false | API | **PASS** | auth.middleware | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 242 | GET /api/tasks (usuario nuevo, vacío) | API | **PASS** | listado | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 243 | POST /api/tasks (válida) -> 201 | API | **PASS** | creación | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 244 | La tarea nace pending/high y completed:false | API | **PASS** | valores por defecto | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 245 | POST /api/tasks (título vacío) -> 400 | API | **PASS** | validación | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 246 | POST /api/tasks (status inválido) -> 400 | API | **PASS** | validación | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 247 | POST /api/tasks (título duplicado) -> 409 | API | **PASS** | índice único | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 248 | GET /api/tasks/:id | API | **PASS** | lectura por id | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 249 | PATCH completed:true traduce a status:completed | API | **PASS** | compatibilidad | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 250 | PATCH status:in-progress deja completed:false | API | **PASS** | compatibilidad | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 251 | GET /api/tasks?status=in-progress | API | **PASS** | filtros SQL | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 252 | GET /api/tasks?priority=low | API | **PASS** | filtros SQL | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 253 | GET /api/tasks?search= (en descripción, sin distinguir mayúsculas) | API | **PASS** | filtros SQL | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 254 | GET /api/tasks?status=inventado -> 400 | API | **PASS** | validación de filtros | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 255 | GET /api/tasks/stats | API | **PASS** | resumen | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 256 | GET /api/system/stats | API | **PASS** | contador | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 257 | GET /playground sirve el playground HTML | API | **PASS** | estáticos | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 258 | Una ruta inexistente de /api/ devuelve 404 en JSON | API | **PASS** | fallback SPA | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 259 | Aislamiento: el otro usuario no ve las tareas | API | **PASS** | filtro por user_id | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 260 | Aislamiento: 404 al leer una tarea ajena | API | **PASS** | filtro por user_id | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 261 | El título duplicado se comprueba por usuario, no globalmente | API | **PASS** | índice compuesto | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 262 | Registro con contraseña de 14 caracteres -> 400 | API | **PASS** | longitud mínima | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 263 | Registro con exactamente 15 caracteres y composición válida -> 201 | API | **PASS** | política | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 264 | Se puede iniciar sesión después de registrarse | API | **PASS** | login | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 265 | Registro con contraseña larga y con espacios -> 201 | API | **PASS** | política | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 266 | Registro sin mayúscula -> 400 | API | **PASS** | composición | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 267 | Registro sin número -> 400 | API | **PASS** | composición | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 268 | Registro sin símbolo -> 400 | API | **PASS** | composición | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 269 | El espacio no cuenta como símbolo -> 400 | API | **PASS** | composición | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 270 | Una frase sin composición ya no basta para registrarse -> 400 | API | **PASS** | composición | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 271 | Registro con contraseña de la lista de bloqueo -> 400 | API | **PASS** | lista de bloqueo | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 272 | Registro con "palabra común + adornos" -> 400 pese a cumplir composición | API | **PASS** | patrones previsibles | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 273 | Registro con la contraseña conteniendo el usuario -> 400 | API | **PASS** | nombre de usuario | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 274 | Registro con más de 72 bytes -> 400, no se recorta en silencio | API | **PASS** | límite de bcrypt | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 275 | Un registro rechazado por la política no crea el usuario | API | **PASS** | transaccionalidad | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 276 | La respuesta del registro no expone contraseña ni hash | API | **PASS** | respuesta pública | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 277 | Una cuenta anterior a la política entra con su contraseña de siempre | API | **PASS** | loginValidator | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 278 | Una cuenta con frase sin composición sigue pudiendo entrar | API | **PASS** | loginValidator | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 279 | La API ignora passwordConfirmation | API | **PASS** | contrato de registro | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 280 | passwordConfirmation no se persiste: no existe tal columna | API | **PASS** | esquema | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 281 | El login funciona con username y password, e ignora la confirmación | API | **PASS** | contrato de login | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 282 | La CSP está presente y restringe el origen por defecto | API | **PASS** | helmet | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 283 | La CSP no bloquea los manejadores onclick del playground | API | **PASS** | scriptSrcAttr | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 284 | La CSP impide cargar la página en un iframe ajeno | API | **PASS** | frameAncestors | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 285 | Se envía X-Content-Type-Options: nosniff | API | **PASS** | helmet | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 286 | Una petición del mismo origen no la bloquea CORS | API | **PASS** | delegado CORS | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 287 | Un origen desconocido no recibe la cabecera | API | **PASS** | delegado CORS | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 288 | Token firmado con otro secreto -> 401 | API | **PASS** | verificación JWT | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 289 | Token caducado -> 401 | API | **PASS** | verificación JWT | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 290 | Token sin firmar con alg:none -> 401 | API | **PASS** | algoritmo explícito | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 291 | Token válido pero sin userId -> 401 | API | **PASS** | auth.middleware | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 292 | Token de un usuario inexistente no devuelve datos ajenos | API | **UPDATED** | auth.middleware + repositorio | Fixture/aserción actualizada | Firmaba un JWT sin `typ`, que ahora el middleware corta antes. Se añadió el claim para que el token siga llegando al repositorio, que es lo que el test dice comprobar. Sin el arreglo habría seguido en verde midiendo otra cosa |
| 293 | Token con formato inválido -> 401 | API | **PASS** | verificación JWT | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 294 | Cargas de inyección SQL se tratan como texto | API | **PASS** | SQL parametrizado | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 295 | Buscar "50%" encuentra ese texto y no todas las tareas | API | **PASS** | escapeLikePattern | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 296 | La tabla tasks sigue intacta tras las cargas de inyección | API | **PASS** | SQL parametrizado | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 297 | Un título con sintaxis SQL se almacena literalmente | API | **PASS** | SQL parametrizado | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 298 | El índice único rechaza el duplicado con mayúsculas y espacios | API | **PASS** | índice LOWER(TRIM()) | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 299 | Registrarse crea un usuario con rol "user", nunca admin | API | **PASS** | auth.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 300 | Mandar role:"admin" al registrarse no concede el rol | API | **PASS** | auth.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 301 | Un usuario normal recibe 403 en /api/admin | API | **PASS** | requireAdmin | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 302 | Sin token, /api/admin devuelve 401 y no 403 | API | **PASS** | orden de middlewares | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 303 | GET /api/admin/users lista a todos con su número de tareas | API | **PASS** | admin.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 304 | El administrador de la semilla existe y entra con rol admin | API | **UPDATED** | seedAdmin + login | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 305 | El listado de administración no expone ningún hash | API | **PASS** | admin.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 306 | Un administrador no puede borrarse a sí mismo | API | **PASS** | admin.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 307 | GET /api/admin/stats devuelve el resumen global | API | **PASS** | admin.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 308 | El administrador borra a otro usuario | API | **PASS** | admin.service | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 309 | DELETE /api/tasks/:id -> 200 con success:true | API | **PASS** | borrado | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 310 | GET tras borrar -> 404 | API | **PASS** | borrado | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 311 | Borrar un usuario arrastra sus tareas (CASCADE) | API | **PASS** | clave foránea | Ninguna | No depende del mecanismo de sesión; sigue alineado |

### `client/src/services/authApi.test.js`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 312 | login: devuelve { user, token } desenvuelto | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 313 | login: manda usuario y contraseña como JSON | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 314 | login: propaga el mensaje del servidor | Componente | **PASS** | services/authApi.js | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 315 | login: no manda la cabecera de autorización | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 316 | register: devuelve el usuario creado con su rol | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 317 | register: llama al endpoint de registro | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |
| 318 | register: propaga el 409 de usuario ya existente | Componente | **PASS** | services/authApi.js | Ninguna | No depende del mecanismo de sesión; sigue alineado |
| 319 | register: usa un mensaje por defecto | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | El cuerpo de la respuesta pasó de `token` a `accessToken` |

### `e2e/taskhub.spec.js` — navegador con Playwright

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 320 | un usuario nuevo puede registrarse y entra directamente | E2E | **UPDATED · BLOCKED** | registro + cookie | Comportamiento nuevo cubierto | El registro ahora deja además la cookie de refresco. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 321 | la sesión sobrevive a recargar la página | E2E | **UPDATED · BLOCKED** | renovación al arrancar | Comportamiento nuevo cubierto | Antes sobrevivía por el token de localStorage; ahora pasa por una renovación real contra la API. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 322 | salir devuelve a la pantalla de acceso | E2E | **UPDATED · BLOCKED** | logout | Comportamiento nuevo cubierto | El logout es ahora una llamada al servidor y no solo un cambio de estado local. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 323 | la confirmación que no coincide impide registrarse | E2E | **BLOCKED** | estado mismatch | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 324 | el campo de confirmación solo existe en el registro | E2E | **BLOCKED** | AuthForm por modo | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 325 | una contraseña demasiado corta no permite registrarse | E2E | **BLOCKED** | validación del navegador | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 326 | una contraseña sin mayúscula no permite registrarse | E2E | **BLOCKED** | validación del navegador | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 327 | una contraseña sin número no permite registrarse | E2E | **BLOCKED** | validación del navegador | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 328 | una contraseña sin símbolo no permite registrarse | E2E | **BLOCKED** | validación del navegador | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 329 | la lista de requisitos se va marcando al escribir | E2E | **BLOCKED** | lista de requisitos | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 330 | una contraseña de exactamente 15 caracteres es válida | E2E | **BLOCKED** | política | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 331 | una contraseña larga y válida deja registrarse y volver a entrar | E2E | **UPDATED · BLOCKED** | ciclo completo | Comportamiento nuevo cubierto | Incluye ahora un logout con revocación en servidor. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 332 | unas credenciales incorrectas muestran error y no dejan entrar | E2E | **BLOCKED** | login fallido | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 333 | crear, ver, completar y eliminar | E2E | **BLOCKED** | ciclo de vida de tarea | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 334 | editar cambia título, estado y prioridad | E2E | **BLOCKED** | edición en línea | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 335 | no deja crear dos tareas con el mismo título | E2E | **BLOCKED** | conflicto 409 | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 336 | filtrar por estado y por texto, y limpiar | E2E | **BLOCKED** | filtros | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 337 | una búsqueda sin resultados muestra el mensaje | E2E | **BLOCKED** | estado vacío | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 338 | un usuario no ve las tareas de otro | E2E | **BLOCKED** | aislamiento | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 339 | se sirve y comparte la sesión con la aplicación | E2E | **UPDATED · BLOCKED** | playground | Comportamiento nuevo cubierto | El playground comparte ahora también la cookie de refresco y renueva por su cuenta. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 340 | sin sesión, el playground pide entrar | E2E | **BLOCKED** | playground | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 341 | el panel de administración no aparece para un usuario normal | E2E | **BLOCKED** | render condicional | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 342 | las rutas de tareas exigen token | E2E | **BLOCKED** | auth.middleware | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 343 | la comprobación de salud responde sin autenticar | E2E | **BLOCKED** | /api/health | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |
| 344 | las cabeceras de seguridad están presentes | E2E | **BLOCKED** | helmet | Ninguna | Sin cambios. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin red. Revisado por lectura |