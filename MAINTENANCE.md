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
  problemas. Resueltas cuatro: modo debug de Flask, exposición de información
  (Java y Python), falta de límite de peticiones y path traversal. Pendientes
  cinco: XSS, criptografía débil, CSRF, enlace de sockets y validación de URL.
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

**Pendientes** las familias restantes: XSS, criptografía débil en un ejercicio
del ciclo formativo, CSRF desactivado, y dos grupos sobre enlace de sockets y
validación de URL.

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
