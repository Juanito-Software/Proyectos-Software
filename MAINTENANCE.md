# Historial de mantenimiento del repositorio

Registro de operaciones estructurales sobre el repositorio (no sobre el código
de los proyectos).

---

## Estado de las alertas de seguridad

- **Dependabot:** 2 abiertas, ambas dependencias transitivas del build de
  Angular sin arreglo disponible (las únicas "correcciones" son retrocesos de
  versión). Se dejan abiertas a propósito para que GitHub las cierre cuando
  Angular actualice.
- **Secret scanning:** 4 alertas revisadas. Una era real (clave de API de
  Google, revocada y restringida a YouTube Data API v3), dos falsos positivos y una de
  código de terceros ya retirado.
- **Code scanning (CodeQL):** 69 alertas agrupadas en nueve familias de
  problemas. Resueltas ocho: modo debug de Flask, exposición de información
  (Java y Python), falta de límite de peticiones, path traversal, XSS,
  criptografía débil, CSRF y enlace de sockets. Pendiente una: validación
  de URL.
- **Credenciales en código:** revisadas y retiradas las de
  `LeaderBoard_Unity` y `unified-chat-widget`. Ninguna quedaba detectable por
  el escáner automático; aparecieron leyendo el código.

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

(Más adelante aparecieron cuatro más, hasta diez: el `IvParameterSpec` y la
generación de claves RSA de HashTools, el SSR de TaskHub Angular y el
`permitAll()` con token de demostración de RadioStack. Todos documentados en sus
respectivas secciones.)

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

**Pendiente** la familia restante: validación de URL.

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
