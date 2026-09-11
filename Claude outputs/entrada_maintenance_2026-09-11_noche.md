## 2026-09-11 (noche) — TaskHub_Angular: de cubrir pantallas a tres fallos de seguridad

La tarde terminó con el frontend de Angular en 41 tests. La noche empezó con la
idea de cubrir las dos carpetas que faltaban y acabó en cuatro PR (#90 a #93),
tres de ellas con código de producción: al probar por el efecto, y no por el
estado, los tests fueron destapando fallos que ninguna revisión había visto.

| PR | Qué | Tests en CI |
|---|---|---|
| #90 | Frontend: `features/dashboard` y `features/projects` | frontend 41 → 84 |
| #91 | Backend: autorización de tareas por rol y tests de la capa HTTP | backend 71 → 145 |
| #92 | Backend: tokens y cookies fuera del log de peticiones | backend 145 → 148 |
| #93 | Pantalla para añadir miembros a un proyecto | backend 148 → 162, frontend 84 → 99 |

TaskHub_Angular pasa de 112 a **261 tests** en CI.

### Antes de empezar: un conflicto que ya no existía

La sesión arrancó con una indicación de estado: rama con un conflicto pendiente
en `ci.yml`, a resolver con `git rebase origin/main` y `push --force-with-lease`.
Leer el `.git` lo desmintió. El reflog terminaba en `rebase (finish)`, no había
`rebase-merge/` ni `MERGE_HEAD`, la #88 ya estaba en `main` y el `ci.yml` local
era idéntico byte a byte al del remoto. El *force-push* habría recreado una rama
muerta o lo habría rechazado el *lease*.

Y `git nueva` tal cual también habría fallado: el `main` local era anterior a la
#86, que toca `MAINTENANCE.md`, y ese fichero estaba modificado sin commitear.
Se resolvió con `git stash` → `git nueva` → `git stash pop`. Es el cuarto caso
de «anotado como hecho sin estarlo» de esta lista, esta vez sobre el estado de
git: una descripción de hace una hora tampoco se verifica sola.

### #90 — Frontend: tres cosas que no se ven leyendo los tests

43 tests nuevos. Además de la regla de montaje de la tarde (servicio real más
espía), tres detalles:

- **Navegar de verdad en vez de falsificar la ruta.** `ProjectDetailComponent`
  se monta con `RouterTestingHarness` sobre `/projects/p1`, sin ningún doble de
  `ActivatedRoute`. Un doble con solo `snapshot.paramMap` es justo el tipo de
  doble incompleto que rompe a un tercero, y así el id sale de la URL por el
  mismo camino que en producción.
- **El test de reordenar vio un PUT que la aplicación no hace.** El ayudante que
  simula soltar una tarjeta creaba dos objetos contenedor distintos para la misma
  columna, y el componente decide «misma columna» comparando contenedores por
  identidad (`previousContainer === container`). El fallo era del test, no del
  componente; se habría quedado como una falsa alarma sin leer el mensaje.
- **Los runners de CI están en UTC, y en UTC los fallos de zona horaria no
  existen.** Provocado: cambiar la conversión de la fecha límite a medianoche
  *local* salía verde con `TZ=UTC` y rojo con `TZ=Europe/Madrid`. El test habría
  pasado en CI y fallado en un portátil en Madrid. Ahora fuerza
  `America/Los_Angeles` durante la conversión, y las dos regresiones —escribir
  y leer en hora local— salen rojas también en UTC.

Cada comportamiento se comprobó rompiéndolo a propósito: los 21 cambios ponen
algún test en rojo.

**Encontrado y no arreglado** (no es cobertura, es comportamiento):

- El tablero muestra **como mucho 20 tareas** por proyecto: `listByProject` no
  manda `limit` y el backend aplica 20 por defecto. Sin aviso.
- El dashboard muestra **como mucho 10 proyectos**, por el mismo motivo.
- Si la lista de proyectos falla al cargar, el dashboard dice «No tienes
  proyectos aún» en vez de avisar del error.
- El backend exige nombres y títulos de al menos 2 caracteres; los botones se
  habilitan con 1, y el usuario recibe un «No se pudo crear» genérico.

### #91 — Backend: la cifra de cobertura que callaba el resto

«Cubrir el backend también» empezó por medir, y la medición tenía trampa.
`vitest.config.ts` limitaba la cobertura a `services/` y `utils/`, y con ese
filtro daba un **81 %**. Midiendo todo `src/` salía un **30 %**: middlewares,
controladores, rutas y validadores estaban al 0 %. Es la misma lección que los
249 tests de MetaGPT: una cifra sin procedencia no vale nada. El filtro se amplió
a todo `src/`.

Al leer esa capa apareció el fallo más serio de la noche: **las tareas no
comprobaban la pertenencia al proyecto**. Los proyectos sí (`assertOwner`,
`getById`); las rutas de `/api/tasks` solo exigían estar autenticado. Comprobado
con peticiones HTTP antes de escribir nada, con un token de un usuario ajeno:

```
GET    /api/tasks        200  → tareas de todos los proyectos
GET    /api/tasks/t-a    200
PUT    /api/tasks/t-a    200  → título cambiado
DELETE /api/tasks/t-a    204
```

Con el registro abierto, cualquiera podía crearse una cuenta y leer, editar y
borrar todas las tareas. El peor caso era el listado sin filtros: Prisma ignora
las claves `undefined` del `where`, así que la consulta quedaba vacía.

La política se decidió explícitamente antes de arreglar:

| Rol en el proyecto | Leer | Crear, editar, borrar, comentar |
|---|---|---|
| `OWNER` / `EDITOR` | sí | sí |
| `VIEWER` | sí | 403 |
| ajeno | 403 | 403 |

Los tests se escribieron **antes** del arreglo: 13 de los 33 salieron en rojo
contra el código de entonces, exactamente los del agujero. Cada uno comprueba
dos cosas, el código de estado **y** si la escritura llegó al repositorio: un
403 devuelto después de borrar pasaría un test que solo mirase el estado.

Los tests HTTP levantan la aplicación real con `createApp()` y le hacen
peticiones con el `fetch` de Node; solo se sustituyen los repositorios. Sin
supertest, así que sin dependencias nuevas. Destaparon dos fallos más en
`errorHandler`:

- **Un JSON mal formado respondía 500** —y se registraba como fallo del
  servidor—, porque el error de `express.json()` caía en la rama genérica.
- **Los errores de validación llegaban todos bajo la clave `body`**:
  `flatten()` agrupa por el primer segmento de la ruta, y `validate` envuelve el
  esquema en `{ body, query, params }`. El nombre del campo se perdía.

De 71 a 145 tests, 28 cambios provocados y todos en rojo, cobertura de todo
`src/` del 30 al 85 %.

### #92 — Tokens en el log, destapados por el ruido de los tests

Al ejecutar la suite de #91 en Windows, la salida traía cientos de líneas de
`request completed`, y en ellas se leía `"authorization": "Bearer eyJ…"`,
`"cookie": "refreshToken=…"` y `"set-cookie": "refreshToken=…"`. `pino-http`
escribe las cabeceras completas de cada petición y respuesta **con nivel
`info`, el de producción**.

Primero se convirtió la inferencia en hecho: la aplicación arrancada con
`NODE_ENV=production` escribió, con `"level":30`, el token y la cookie en claro.
Cada token de acceso y cada *refresh token* —válido 7 días— habría quedado en
los logs de un despliegue.

El arreglo tiene un matiz que cuesta una vuelta: **`redact` va en el constructor
de pino, no en las opciones de `pino-http`**, que lo ignora cuando recibe un
logger ya creado, que es lo que hace `app.ts`. Los tests leen la línea JSON real
que se escribiría, con el logger construido por la misma función que usa
producción: contra el logger anterior, 2 de 3 en rojo (el tercero vigila lo
contrario, que no se tape de más). De paso, el log se apaga en los tests: de
cientos de líneas a 9.

Se miró el otro TaskHub: el servidor de TaskHub_React, que sí está desplegado,
no usa `pino`, `morgan` ni `winston`. No le afecta.

**Relación con el estado de arriba:** la familia «registro de secretos en claro»
figura como abordada. Este caso no era una llamada a `log` con una variable, sino
la configuración por defecto de una librería, y apareció leyendo la salida de los
tests, no un listado de alertas. Es el «matiz importante» de esa sección otra vez:
cerrar una familia no garantiza que el patrón no exista en otro sitio.

### #93 — Una pantalla que la API anunciaba y no existía

El README decía «Gestión de miembros por proyecto», y existía el endpoint, pero
no había forma de usarlo desde la aplicación. Tres decisiones explícitas:

- **Por email, no con un desplegable de usuarios.** Responder «no existe ningún
  usuario con ese email» revela qué emails están registrados; se aceptó a
  sabiendas, porque solo lo ve el propietario de un proyecto y el desplegable
  enseñaría a todos los usuarios a cualquiera.
- **Solo `EDITOR` y `VIEWER`.** El validador aceptaba `OWNER`, pero `ownerId`
  es uno solo: un segundo «OWNER» tendría los permisos de un EDITOR con otro
  nombre.
- **Solo ver y añadir.** Quitar miembros y cambiar el rol necesitan endpoints
  que no existen.

La pantalla habría destapado dos fallos el primer día: añadir a alguien que ya
era miembro, o un usuario inexistente, respondía **500**. Eran errores de Prisma
(clave única y clave foránea) que `errorHandler` no reconoce. Ahora son 409 y
404, incluido el caso de dos altas simultáneas que chocan en la base de datos.

Contrato cambiado: `POST /members` recibe `email`, ya no `userId`.

De 21 cambios provocados, **20 en rojo**. El que sobrevive es quitar el
`disabled` del botón «Añadir», que no deja pasar nada porque `add()` comprueba el
email por su cuenta. Se deja anotado en vez de maquillar la cifra. Hubo un
segundo superviviente, quitar la comprobación de `ownerId`, y se cerró con un
test nuevo: el propietario sin fila de miembro.

### Cómo se trabajó, y lo que costó

El shell del equipo sigue sin montar las carpetas (la actualización de Windows
del 8 de septiembre). Esta vez los tests se ejecutaron en un clon del repositorio
en la nube, que tiene salida a npm y PyPI, y los ficheros se escribían después en
la carpeta local. Cuatro cosas que conviene saber para la próxima:

- **Maven Central y `binaries.prisma.sh` están bloqueados** por la política de
  red de ese entorno (403). Java no se puede ejecutar ahí, y los tipos de Prisma
  no se generan, así que el `tsc` del backend se pasó siempre en local antes del
  commit. Antes de descubrirlo se afirmó que había «Java/Maven» a partir de
  `java -version` y `mvn -v`, sin lanzar un `mvn test`: el mismo error de
  anotar sin comprobar, cazado al primer intento real.
- **`.github/workflows/` está protegido contra escritura remota.** Los mínimos
  se subieron a mano con `sed` y número de línea, y el número importa:
  `minimo: 41` aparecía dos veces (línea 306, frontend de Angular; línea 391,
  gym-app), y un `sed` sin línea habría bloqueado la PR de PHP.
- **Los ficheros a más de 7 carpetas de profundidad no se pueden leer desde ese
  entorno**, aunque sí escribir. Para no pisar cambios locales se comparó el
  tamaño con el de `main`, contando los CRLF de los ficheros antiguos.
- **Cada tanda tuvo rama nueva antes de escribir nada**, y se verificó en el
  reflog que la rama salía del último `main` antes de copiar los ficheros.

### Pendiente

- **CV:** las dos variantes dicen **71 tests** para TaskHub_Angular, y el mínimo
  de CI ya es **162 + 99 = 261**. Además dicen **Angular 19**, y el
  `package.json` del frontend declara `@angular/core` `^21.2.19`: hay que
  confirmarlo antes de cambiarlo.
- **Vulnerabilidades:** al hacer push, GitHub informó de «44 vulnerabilities on
  the default branch (16 high, 22 moderate, 6 low)». El estado de arriba dice
  2 alertas de Dependabot abiertas. Sin verificar todavía: hace falta consultar la
  API.
- **Frontend de TaskHub_Angular:** los cuatro comportamientos anotados en #90
  (límites de 20 tareas y 10 proyectos, error de carga mudo, longitud mínima).
- **RadioStack**, con lo ya encontrado leyendo el código:
  - `ChatController` (REST) toma el alias del cuerpo, cuando `ChatWebSocketController`
    lo toma del token precisamente para evitar suplantaciones. Decidido: se
    arregla en la tanda de tests con MockMvc.
  - El paso que cuenta tests de `maven-test` busca `target/surefire-reports` en
    la raíz, y RadioStack es multimódulo: hay que cambiar ese `ls` por un `find`.
  - El comentario de «Java · compilar» dice que sus proyectos no tienen ni una
    clase de test, y RadioStack tiene `LocutorTest`.
  - `radiostack-api` no declara dependencias de test.
  - Como el entorno no ejecuta Java, el runner será el CI sobre una PR borrador.
- **OmniForge y GPTDevTeam**, sin empezar.

---

