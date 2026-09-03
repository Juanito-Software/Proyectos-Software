# TaskHub – Gestor de tareas multiusuario

Aplicación full-stack con **React** (frontend), **Express + TypeScript** (backend) y **PostgreSQL**. Cada usuario tiene su propia cuenta y ve únicamente sus tareas: los datos están aislados por usuario a nivel de consulta, no solo en la interfaz.

## Demo en vivo

**[taskhub-react.onrender.com](https://taskhub-react.onrender.com)**

Regístrate con cualquier usuario y contraseña — no hace falta correo ni
verificación, y cada cuenta solo ve sus propias tareas.

- La **aplicación** está en la raíz.
- El **[playground de la API](https://taskhub-react.onrender.com/playground)**
  permite lanzar peticiones reales contra los endpoints y ver las respuestas
  JSON, sin clonar el repositorio. Tiene su propio registro, y comparte sesión
  con la aplicación.

> Está en planes gratuitos (Render + Neon): el servicio se duerme tras 15 minutos sin tráfico, así que **la primera carga puede tardar cerca de un minuto**. Las siguientes van rápidas.

## Estructura del proyecto

```
TaskHub/
├── client/                       # Frontend React (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthForm.jsx      # login y registro, con confirmación
│   │   │   ├── AuthForm.test.jsx      ← 32 tests
│   │   │   ├── TaskForm.jsx      # alta y edición, con estado y prioridad
│   │   │   ├── TaskForm.test.jsx      ← 9 tests
│   │   │   ├── TaskItem.jsx      # tarjeta de tarea con sus distintivos
│   │   │   ├── TaskItem.test.jsx      ← 10 tests
│   │   │   └── TaskList.jsx      # lista, filtros y búsqueda
│   │   ├── context/
│   │   │   ├── AuthContext.jsx   # sesión, renovación automática y logout
│   │   │   └── AuthContext.test.jsx   ← 20 tests
│   │   ├── services/
│   │   │   ├── api.js            # tareas; abre el envoltorio de respuesta
│   │   │   ├── api.test.js            ← 16 tests
│   │   │   ├── api.refresh.test.js    ← 9 tests
│   │   │   ├── authApi.js        # login y registro
│   │   │   └── authApi.test.js        ← 16 tests
│   │   ├── test/setup.js         # limpia DOM y localStorage entre tests
│   │   ├── constants.js          # etiquetas de estado y prioridad, en un solo sitio
│   │   ├── passwordPolicy.js     # réplica de la política; el servidor manda
│   │   ├── passwordPolicy.test.js     ← 22 tests
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js            # build, proxy en desarrollo y umbrales de cobertura
│   └── package.json
├── server/                       # Backend Node.js + TypeScript (Express)
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/             # router · controller · service · JWT
│   │   │   │   ├── password-policy.ts            # política de contraseñas, fuente de verdad
│   │   │   │   ├── password-policy.test.ts       ← 73 tests
│   │   │   │   ├── auth.validation.test.ts       ← 30 tests
│   │   │   │   ├── sessions.repository.ts        # familias de refresco en SQL
│   │   │   │   ├── refresh-token.ts              # generación y hash del refresco
│   │   │   │   ├── token.service.test.ts         ← 19 tests
│   │   │   │   ├── auth.cookie.ts                # cookie HttpOnly del refresco
│   │   │   │   └── auth.cookie.test.ts           ← 12 tests
│   │   │   ├── users/            # repository (SQL) · types (rol user/admin)
│   │   │   ├── tasks/            # router · controller · service · repository
│   │   │   │   ├── tasks.repository.test.ts       ← 13 tests
│   │   │   │   └── tasks.validation.test.ts       ← 25 tests
│   │   │   └── admin/            # router · controller · service (solo rol admin)
│   │   ├── middleware/           # auth · admin · rate limit · validación · errores · logging
│   │   │   └── rateLimit.middleware.test.ts       ← 8 tests
│   │   ├── config/               # env · db (pool) · schema (DDL) · seed-admin
│   │   ├── utils/                # ApiError · ApiResponse
│   │   ├── types/                # express.d.ts (userId en Request)
│   │   ├── public/               # playground de la API (se sirve en /playground)
│   │   ├── app.ts                # fábrica de la app Express
│   │   ├── server.ts             # arranque, semilla del admin y apagado ordenado
│   │   └── verify.ts             # suite end-to-end de la API      ← 109 tests
│   ├── scripts/build-assets.mjs  # copia playground y cliente compilado a dist/
│   ├── vitest.config.ts          # tests unitarios: solo lógica pura, sin BD
│   ├── .env.example              # plantilla de variables de entorno
│   └── package.json
├── e2e/taskhub.spec.js           # end-to-end de navegador          ← 30 tests
├── docs/AUDITORIA_SEGURIDAD.md   # informe de la auditoría de seguridad
├── docs/AUDITORIA_TESTS_229.md   # revisión test a test tras la política de contraseñas
├── docs/AUDITORIA_TESTS_344.md   # revisión test a test tras los refresh tokens
├── eslint.config.js              # lint del servidor (TS) y del cliente (React)
├── playwright.config.js          # arranca el servidor y espera a /api/health
├── .github/workflows/            # pipeline de CI (copia; GitHub lee el de la raíz)
└── README.md
```

Los tests viven **junto al código que prueban** (`TaskForm.jsx` y
`TaskForm.test.jsx` en la misma carpeta), salvo los de navegador, que van en
`e2e/` porque prueban la aplicación entera y no un fichero concreto.

En producción se despliega **un único proceso**: el mismo Express sirve el
cliente React compilado en `/`, el playground en `/playground` y la API en
`/api`.

## Cómo ejecutarlo

### 1. Instalar dependencias

Desde la raíz del proyecto:

```bash
npm run install:all
```

O por separado:

```bash
cd server && npm install
cd ../client && npm install
```

### 1.b Configurar la base de datos

El backend usa **PostgreSQL**. Crea una base de datos vacía y copia la plantilla
de variables de entorno:

```bash
createdb taskhub          # o CREATE DATABASE taskhub; desde psql
cd server
cp .env.example .env      # y edita DATABASE_URL con tu usuario y contraseña
```

Las tablas se crean solas la primera vez que arranca el servidor: el script del
esquema es idempotente, así que no hay que ejecutar migraciones a mano.

### 2. Arrancar servidor y cliente (recomendado)

En una sola terminal:

```bash
npm run dev
```

Arranca el backend (http://localhost:3001) y el frontend (http://localhost:5173). **Ctrl+C detiene ambos procesos** y cierra el servidor correctamente.

### Alternativa: arrancar por separado

```bash
# Terminal 1
npm run server

# Terminal 2
npm run client
```

Si arrancas por separado, pulsa **Ctrl+C** en cada terminal para detenerlos.

## Funcionalidades

- **Login/Registro**: token de acceso JWT de 15 minutos más un token de refresco rotativo en cookie HttpOnly. La sesión se renueva sola y el cierre revoca en el servidor.
- **Lista de tareas**: título, descripción, estado (pendiente / en progreso / completada) y prioridad (baja / media / alta), con distintivos de color. Solo ves tus tareas.
- **Agregar y editar**: el mismo formulario, con selectores de estado y prioridad.
- **Eliminar tarea**: con confirmación.
- **Marcar como completada**: checkbox, como atajo de un clic para el caso más habitual.
- **Filtros y búsqueda**: por estado, por prioridad y por texto en título o descripción. **Los resuelve la API**, no el navegador: viajan como parámetros de consulta y solo llegan las tareas que se piden. La búsqueda espera 300 ms desde la última tecla para no lanzar una petición por carácter.
- **Notificaciones**: mensaje breve al crear o actualizar una tarea.

## API REST (ejemplos)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registro (`username`, `password`) |
| POST | `/api/auth/login` | Login (`username`, `password`) |
| POST | `/api/auth/refresh` | Cambia la cookie de refresco por credenciales nuevas |
| POST | `/api/auth/logout` | Cierra la sesión **en el servidor** |
| POST | `/api/auth/logout-all` | Cierra todas las sesiones del usuario |
| GET | `/api/tasks` | Listar tareas del usuario. Filtros: `?status=`, `?priority=`, `?search=` |
| GET | `/api/tasks/stats` | Resumen del usuario por estado |
| GET | `/api/tasks/:id` | Obtener una tarea |
| POST | `/api/tasks` | Crear tarea |
| PATCH | `/api/tasks/:id` | Actualizar parcial |
| PUT | `/api/tasks/:id` | Actualizar tarea completa |
| DELETE | `/api/tasks/:id` | Eliminar tarea |
| GET | `/api/system/stats` | Uptime, peticiones servidas y versión de Node |
| GET | `/api/health` | Comprobación de vida |
| GET | `/api/admin/users` | Listado de usuarios con su número de tareas · **admin** |
| DELETE | `/api/admin/users/:id` | Borra un usuario y, en cascada, sus tareas · **admin** |
| GET | `/api/admin/stats` | Resumen global de la instancia · **admin** |

Las rutas de tareas requieren cabecera `Authorization: Bearer <accessToken>`. Los títulos deben ser únicos **por usuario** (409 si se repite; dos usuarios distintos sí pueden tener el mismo título).

### Formato de respuesta

Todas las respuestas van envueltas:

```jsonc
// Correcta
{ "success": true, "data": { /* … */ }, "message": "…", "timestamp": "2026-08-23T…" }

// Error
{ "success": false, "error": "Tarea no encontrada", "timestamp": "2026-08-23T…" }
```

### Modelo de tarea

`status` (`pending` · `in-progress` · `completed`) y `priority` (`low` · `medium` · `high`) son la fuente de verdad. El campo `completed` se sigue devolviendo, calculado como `status === 'completed'`, y se acepta como entrada traduciéndolo a `status` — así el checkbox del cliente React sigue funcionando sin cambios. Las tareas guardadas antes de este cambio se normalizan al leerlas, sin script de migración.

## Playground de la API

Una interfaz para lanzar peticiones reales contra todos los endpoints y ver las
respuestas JSON, con filtros, contador de peticiones y uptime.

- En local: **http://localhost:3001/playground**, con el backend arrancado.
- Desplegado: **[taskhub-react.onrender.com/playground](https://taskhub-react.onrender.com/playground)**

### Cómo se entra

Todas las rutas de `/api/tasks` exigen un token, así que el playground pide
sesión antes de dejarte llamar a nada. **No hace falta tener cuenta previa**: la
pantalla que aparece al entrar tiene un enlace para registrarte ahí mismo, y
sirve cualquier usuario y contraseña.

El token se guarda en `localStorage` con la misma clave que usa el cliente
React, así que las dos partes comparten sesión: si ya has entrado en la
aplicación, el playground abre autenticado, y al revés. Si el token caduca
mientras lo usas, vuelve a aparecer la pantalla de acceso sin perder la página.

Desde el playground se sale con el botón de la esquina superior derecha, y hay
un enlace **← Ir a la aplicación** para volver al cliente React.

### Probar los endpoints de administración

Los tres endpoints de `/api/admin` no tienen interfaz propia: se prueban desde
aquí, entrando con la cuenta de administrador definida en `ADMIN_USERNAME`.
Con un usuario normal responden 403, que es justo lo que conviene comprobar.

## Despliegue

El servicio web va en **Render** y la base de datos en **Neon**. Los dos tienen
plan gratuito permanente; el de Render duerme el servicio tras 15 minutos sin
tráfico, así que la primera carga puede tardar cerca de un minuto.

### Configuración del servicio en Render

Como esto vive dentro de un monorepo, hay que apuntar al subdirectorio:

| Campo | Valor |
|-------|-------|
| Repository | `Juanito-Software/Proyectos-Software` |
| Root Directory | `Juanito_Software/JS/React/TaskHub_React` |
| Runtime | Node |
| Build Command | `npm run install:all && npm run build` |
| Start Command | `npm start --prefix server` |
| Instance Type | Free |

`install:all` usa `--include=dev` a propósito: con `NODE_ENV=production`, npm
omite las devDependencies, y ahí están Vite, TypeScript y tsx. Sin ese flag el
build falla con `vite: not found`.

### Variables de entorno en Render

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | La cadena de Neon, con `?sslmode=require` |
| `JWT_SECRET` | Una clave larga y aleatoria, **distinta de la de desarrollo** |
| `NODE_ENV` | `production` |
| `ADMIN_USERNAME` | Opcional. Nombre del administrador |
| `ADMIN_PASSWORD` | Opcional. Mínimo 12 caracteres |

`PORT` no se configura: Render la inyecta y `config/env.ts` la lee.

El build compila el cliente React, luego el servidor, y copia el resultado a
`server/dist/client`. En producción un único proceso Express sirve las tres
cosas: la aplicación en `/`, el playground en `/playground` y la API en `/api`.

## Tests

**453 en total**, repartidos en cuatro capas que prueban cosas distintas:

| Comando | Qué ejecuta | Cuántos | Necesita |
|---------|-------------|---------|----------|
| `npm test` | Unitarios de servidor y cliente | 180 + 134 | Nada |
| `npm run verify` | End-to-end de la API | 109 | PostgreSQL |
| `npm run test:e2e` | Navegador real (Playwright) | 30 | PostgreSQL y `npm run build` |
| `npm run ci` | Lint, tipos, unitarios y build | — | Nada |

Los **unitarios** cubren lógica pura —validadores, escapado de comodines de
`LIKE`, campos calculados, la capa de servicios del cliente y los componentes de
tarea— y corren en milisegundos sin nada instalado.

La **suite de la API** levanta la aplicación en un puerto temporal contra un
esquema de base de datos propio, que se crea al empezar y se destruye al
terminar aunque falle a mitad. Incluye una batería de manipulación de tokens
(firma inválida, caducado, `alg: none`, sin identificador, usuario inexistente)
y cargas de inyección SQL que deben tratarse como texto.

Los **de navegador** son la única capa que comprueba que cliente, API y base de
datos encajan de verdad. La primera vez hay que descargar Chromium:

```bash
npx playwright install chromium
```

#### Salvaguarda: no se pueden ejecutar contra producción

Estos tests **escriben datos reales**: crean usuarios, crean y borran tareas, y
uno de ellos llega a eliminar una cuenta. Como el `.env` de desarrollo apunta a
la base de datos desplegada, ejecutarlos sin pensar dejaba usuarios `e2e-*` en
la aplicación en producción. Pasó, y por eso existe esta protección.

`playwright.config.js` **aborta antes de arrancar nada** si `DATABASE_URL`
apunta a una base de datos gestionada — Neon, Render, Supabase o RDS— y explica
cómo apuntar a una local. La protección está en la herramienta, no en acordarse.

Preparar la base de datos de pruebas, **una sola vez**:

```sql
CREATE DATABASE taskhub_e2e;
```

Y después, en cada terminal donde vayas a lanzarlos:

```bash
set DATABASE_URL=postgresql://usuario:clave@localhost:5432/taskhub_e2e
npm run test:e2e
```

La variable solo vive en esa ventana y tiene prioridad sobre el `.env`, así que
la configuración de desarrollo se queda intacta. En CI no hace falta: allí
`DATABASE_URL` ya apunta al contenedor de PostgreSQL del propio job, que se
destruye al terminar.

Si en algún momento quieres saltarte la protección a propósito —por ejemplo
contra un entorno de pruebas remoto— define `E2E_ALLOW_REMOTE_DB=1`.

Y si quedaran restos de una ejecución antigua:

```sql
DELETE FROM users WHERE username LIKE 'e2e-%';
```

Las tareas asociadas se van solas por el borrado en cascada.

### Qué cubren las 109 comprobaciones de la API

Registro, login, acceso sin token, CRUD completo, validación de campos y de
filtros, título duplicado, traducción `completed` ↔ `status`, los tres filtros,
ambos endpoints de estadísticas, que el playground se sirva, aislamiento entre
usuarios, borrado, que el índice único rechace duplicados aunque cambien
mayúsculas y espacios, y que borrar un usuario arrastre sus tareas.

Más la sesión completa: forma y atributos de la cookie de refresco, rotación,
detección de reutilización con revocación de la familia, tolerancia a
renovaciones simultáneas, logout con revocación en servidor, cierre de todas las
sesiones, y la batería de intentos que deben fallar — un token de acceso usado
como refresco, un refresco usado como token de acceso, y un token de la política
anterior.

**Seguridad:** token firmado con otro secreto, caducado, sin firmar con
`alg: none`, sin identificador de usuario, de un usuario que ya no existe y con
formato inválido — todos deben devolver 401. Y cargas de inyección SQL en el
filtro de búsqueda, que deben tratarse como texto sin romper la consulta.

**Rol de administrador:** que registrarse nunca lo conceda —ni enviando
`role: "admin"` en el cuerpo—, que un usuario normal reciba 403, que sin token
se reciba 401 y no 403, que el administrador de la semilla exista y entre, que
el listado no filtre ningún hash de contraseña, y que un administrador no pueda
borrarse a sí mismo.

## Integración continua y despliegue

### CI — GitHub Actions

Cada push y cada pull request ejecuta ocho jobs en GitHub Actions: lint, tipos,
unitarios del servidor, tests del cliente con cobertura, suite de la API contra
un PostgreSQL real, end-to-end de navegador, build de producción y auditoría de
dependencias. Todos cuelgan de un job final, `ci-ok`, del que puede colgarse la
regla de protección de rama sin tener que enumerar los demás.

El pipeline falla si falla cualquier test, si el build no produce servidor,
playground y cliente, si el lint o los tipos protestan, si la cobertura baja de
los umbrales, o si aparece una vulnerabilidad **alta o crítica**. Las moderadas
y bajas no lo bloquean: con `--audit-level=moderate` estaría en rojo permanente
por dependencias de desarrollo, y un CI siempre en rojo deja de mirarse.

El workflow está en `.github/workflows/taskhub-react-ci.yml`, con una copia en
la raíz del monorepo, que es donde GitHub los busca.

### CD — Render Auto-Deploy

Cada commit a `main` dispara también un despliegue automático en Render, que
instala dependencias, compila cliente y servidor y publica la nueva versión.

**El CI y el despliegue van en paralelo, no encadenados.** Render publica en
cuanto llega el commit, sin esperar al resultado del pipeline, así que un
despliegue puede llegar a producción con los tests en rojo — pasó, y por eso
conviene decirlo.

Es una decisión consciente mientras el proyecto está en desarrollo: poder
desplegar un commit con tests fallando permite depurar en el entorno real.
Encadenarlos es lo correcto cuando la aplicación se estabilice, y se hace
desactivando el auto-deploy y llamando a un *Deploy Hook* de Render desde un
job que dependa de `ci-ok`.

## Sesiones: token de acceso y token de refresco

Hay **dos credenciales con papeles distintos**, y la diferencia entre ellas es
lo que permite revocar una sesión de verdad.

| | Token de acceso | Token de refresco |
|---|---|---|
| Qué es | JWT firmado (HS256) | 32 bytes aleatorios, **no es un JWT** |
| Dura | 15 minutos | 7 días |
| Viaja en | `Authorization: Bearer` | Cookie `HttpOnly` |
| Sirve para | Cualquier ruta protegida | Solo `POST /api/auth/refresh` |
| Se guarda en el servidor | No | Sí, su SHA-256, en `refresh_sessions` |
| Se puede revocar | No hasta que caduque | Sí, al instante |

**Por qué el de refresco no es un JWT.** Si los dos lo fueran, separarlos
dependería de comprobar un claim `typ` en todos los sitios, y olvidarlo en uno
solo bastaría para que un refresco valiera como token de acceso. Siendo bytes
opacos, esa confusión es imposible: el middleware intentaría verificar una firma
que no existe. El claim `typ: 'access'` está igualmente, como segunda barrera.

**Por qué el de acceso dura tan poco.** Un JWT firmado sigue siendo válido hasta
que caduca, aunque se cierre la sesión: no hay forma de retirarlo sin consultar
una lista negra en cada petición, y eso costaría una consulta por llamada. La
respuesta no es la lista negra, es que la ventana sea pequeña. Quince minutos es
el máximo que puede sobrevivir un token robado.

### Rotación y detección de reutilización

Cada renovación **gasta** el token de refresco y entrega otro. La fila vieja se
marca revocada y la nueva nace con el mismo `family_id`, así que una sesión es
la cadena de filas que comparten familia.

Esa cadena es lo que permite distinguir dos cosas que se parecen:

```
Refresco A  →  renovar  →  A revocado, nace B          ← normal
Refresco A  →  renovar otra vez                        ← alguien tiene una copia
                ↓
        se revoca la FAMILIA entera, no solo A
```

Revocar solo el token presentado no serviría de nada: quien pudo copiar A tiene
también B. Por eso cae la cadena completa y la sesión se cierra en todos los
dispositivos que la compartían.

**Con una excepción deliberada.** Dos pestañas del mismo usuario pueden renovar a
la vez con la misma cookie, y eso no es un ataque. Dentro de una ventana de
tolerancia (`REFRESH_GRACE_SECONDS`, 10 por defecto) la segunda se rechaza sin
matar la familia, y el cliente reintenta con la cookie ya rotada. Es un
compromiso explícito: estrecha la detección durante esos segundos a cambio de no
echar a la calle a quien solo tenía dos pestañas abiertas.

La rotación es **atómica**: `UPDATE ... WHERE token_hash = $1 AND revoked_at IS
NULL`. PostgreSQL serializa las escrituras sobre una misma fila, así que de dos
rotaciones simultáneas solo una la encuentra sin revocar. No hace falta
transacción explícita ni bloqueo — una sola sentencia ya lo es.

### Por qué el refresco va en cookie y no en localStorage

Es la credencial que de verdad importa: sirve para emitir tokens de acceso
durante días. `HttpOnly` la deja fuera del alcance de `document.cookie`, así que
un XSS puede llevarse el token de acceso —quince minutos— pero no la llave que
renueva la sesión.

Meter una cookie en una aplicación que no las usaba obliga a mirar **CSRF**, que
es el riesgo clásico de autenticar por cookie. Aquí queda cerrado por tres vías:

1. **`SameSite=Strict`**: el navegador no manda la cookie en peticiones que
   nazcan de otro sitio. Es la defensa principal y hace innecesario un token
   anti-CSRF.
2. **La cookie no autoriza nada.** Ninguna ruta de datos la mira; las protegidas
   exigen la cabecera `Authorization`, que una petición cross-site no puede
   fijar.
3. **`Path=/api/auth`**: ni siquiera se envía al resto de la API.

CORS se queda como estaba, con `credentials: false`. No hace falta relajarlo: en
producción la aplicación, el playground y la API salen del mismo origen, y en
desarrollo Vite hace de proxy, así que el navegador nunca ve una petición
cross-origin.

### Cerrar sesión

`POST /api/auth/logout` revoca la familia **en el servidor**. Antes el logout
solo vaciaba el estado del navegador, y el token seguía siendo válido durante
días para quien tuviera una copia. Cerrar una sesión no toca las demás del mismo
usuario; para eso está `POST /api/auth/logout-all`, que las cierra todas y saca
el identificador del token, nunca del cuerpo de la petición.

### Qué pasó con los tokens de 7 días ya emitidos

**Se invalidaron todos.** Los de la política anterior no llevan el claim
`typ: 'access'`, así que el middleware los rechaza desde el primer despliegue y
todo el mundo tuvo que volver a entrar.

Fue una decisión, no un descuido. Mantenerlos vivos por comodidad habría dejado
abierta durante una semana justo la puerta que este cambio venía a cerrar:
tokens de larga duración imposibles de revocar. Un cierre de sesión molesto es
más barato que eso.

### Variables de entorno

| Variable | Por defecto | Para qué |
|---|---|---|
| `ACCESS_TOKEN_TTL` | `15m` | Duración del token de acceso |
| `REFRESH_TOKEN_TTL` | `7d` | Duración de la sesión sin volver a escribir la contraseña |
| `REFRESH_GRACE_SECONDS` | `10` | Tolerancia para renovaciones simultáneas |
| `JWT_SECRET` | — | Firma del token de acceso. Obligatoria en producción |

## Política de contraseñas

La implementación está en `server/src/modules/auth/password-policy.ts`, que es
la única fuente de verdad: la usan tanto el registro como la semilla del
administrador. El formulario replica las reglas en `client/src/passwordPolicy.js`
para avisar antes de enviar, pero quien decide es el servidor.

La política combina recomendaciones de **NIST SP 800-63B Revisión 4** (julio de
2025) con requisitos propios más estrictos. Conviene no mezclarlos:

| Regla | Valor | Origen |
|---|---|---|
| Longitud mínima | **15 caracteres** | NIST: exige 15 cuando la contraseña es el único factor; los 8 solo valen con MFA, y TaskHub no la tiene |
| Contraseñas largas permitidas | Hasta 72 bytes | NIST pide admitir al menos 64 |
| Sin truncamiento silencioso | Se rechaza, no se recorta | NIST |
| Caracteres permitidos | Todos, espacios incluidos | NIST |
| Almacenamiento | bcrypt con sal | NIST |
| Lista de bloqueo | Contraseñas comunes, caracteres repetidos, secuencias de teclado y el propio nombre de usuario | NIST exige la comprobación; **el contenido concreto de la lista es decisión de TaskHub** |
| **Al menos una mayúscula** | Obligatoria | **Decisión de TaskHub** |
| **Al menos un número** | Obligatorio | **Decisión de TaskHub** |
| **Al menos un símbolo** | Obligatorio | **Decisión de TaskHub** |
| Longitud máxima | 72 **bytes** | **Límite técnico**, no requisito de NIST: bcrypt solo lee los primeros 72 bytes |

**Las tres reglas de composición son más estrictas que NIST, no una lectura de
NIST.** La Revisión 4 no se limita a desaconsejarlas: dice que los verificadores
**no deben** imponerlas. TaskHub las aplica igualmente como requisito de
producto, y este README no pretende justificarlo apelando a la norma.

Lo que sí hay que hacer es asumir el efecto secundario conocido. Obligar a
mezclar tipos de carácter empuja a la gente hacia formas predecibles:
`Password123!`, `Verano2026!`, `P@ssw0rd`. Son las primeras que prueba un ataque
por diccionario, y cumplen los cuatro requisitos sin esfuerzo. Por eso la lista
de bloqueo **cubre expresamente los patrones que la propia regla fomenta**: una
palabra común rodeada de dígitos y símbolos se rechaza aunque cumpla la
composición, y la comprobación deshace antes las sustituciones de estilo *leet*,
de forma que `P@ssword2026!!!` cae igual que `Password2026!!!`. Sin esa
contrapartida, exigir composición dejaría la aplicación menos segura que sin
exigirla.

**Por qué 72 bytes y no 72 caracteres.** bcrypt cuenta bytes. Una contraseña de
72 caracteres con acentos o eñes pasa de los 72 bytes en UTF-8, y bcrypt
descartaría el sobrante sin avisar — justo el truncamiento silencioso que la
norma prohíbe. Medir con `.length` dejaba ese caso pasar.

**Otras decisiones propias de TaskHub, no requisitos de NIST:**

- La lista de bloqueo está **embebida en el código** en lugar de consultar un
  servicio de credenciales filtradas. Para un proyecto de este tamaño, una
  llamada externa en cada registro añadiría latencia y un punto de fallo
  desproporcionados. Conectar una fuente real queda como mejora futura si el
  proyecto llegara a tener usuarios reales.
- El umbral de 4 caracteres para comparar la contraseña con el nombre de
  usuario: por debajo hay demasiados falsos positivos (un usuario "ana"
  rechazaría frases con "semana" o "mañana").
- El espacio **no cuenta como símbolo**. Si contara, cualquier frase con
  espacios cumpliría el requisito sin llevar un solo símbolo y la regla no
  comprobaría nada.

**Usuarios existentes.** La política se aplica **solo al registro**. Quien creó
su cuenta cuando el mínimo era de 8 caracteres, o cuando no se exigía
composición, sigue pudiendo entrar con su contraseña de siempre: el validador
del inicio de sesión no comprueba longitud, composición ni lista de bloqueo.
Hacerlo dejaría fuera a esas cuentas y, además, daría respuestas distintas según
el caso, lo que revela información antes siquiera de comprobar las credenciales.
Hay tests en las capas unitaria y de API que fijan este comportamiento.

No hay ningún mecanismo de cambio de contraseña forzoso, así que tampoco se ha
añadido uno: endurecer la política no invalida nada.

**Confirmación de contraseña.** El registro pide escribir la contraseña dos
veces, pero eso es **asunto del formulario**: se compara en el cliente y no
viaja a la API, que sigue recibiendo solo `username` y `password`. No se
almacena, no se hashea y no existe en la base de datos.

## Administración

Existe un rol `admin` que puede listar usuarios, borrarlos —arrastrando sus
tareas por la clave foránea en cascada— y consultar un resumen global.

**El rol solo se concede por semilla.** Al arrancar, si están definidas
`ADMIN_USERNAME` y `ADMIN_PASSWORD`, ese usuario se crea o se promueve a
administrador. No hay ningún camino desde la API pública hasta el rol: el
registro fuerza `user`, el repositorio no acepta el rol como parámetro y no
existe ningún endpoint para promocionar a nadie. Quien controla las variables
de entorno del despliegue decide quién administra.

Tres decisiones que conviene explicar:

**El rol se lee de la base de datos en cada petición, no del JWT.** Si viajara
dentro del token, retirarle el rol a alguien no surtiría efecto hasta que su
token caducara, hasta siete días después. Cuesta una consulta, pero el permiso
comprobado es siempre el vigente.

**403 y no 404.** En las tareas ajenas se devuelve 404 para no revelar que
existen; aquí no aplica, porque quien pregunta ya está autenticado y la
existencia de una zona de administración no es un secreto.

**Un administrador no puede borrarse a sí mismo ni dejar la instancia sin
administradores.** Las dos comprobaciones existen para que un clic no deje la
aplicación sin nadie que pueda gestionarla.

## Decisiones de diseño

**SQL escrito a mano, sin ORM.** El acceso a datos usa el driver `pg` con
consultas parametrizadas (`$1`, `$2`…). Los valores nunca se concatenan en la
cadena SQL, que es lo que hace imposible la inyección.

**Restricciones en la base de datos, no solo en el código.** El título único por
usuario es un índice sobre `(user_id, LOWER(TRIM(title)))`. El servicio lo
comprueba antes para devolver un 409 con mensaje claro, pero la garantía real la
da el índice: dos peticiones simultáneas ya no pueden colarse entre la
comprobación y la escritura, como sí ocurría con el almacenamiento en ficheros.

**Composición obligatoria, con su contrapartida.** Se exigen mayúscula, número y
símbolo además de los 15 caracteres. Es una decisión de producto más estricta
que NIST, que desaconseja esas reglas por el patrón predecible que provocan; el
patrón se ataja bloqueando expresamente las contraseñas que ese patrón produce.
El detalle está en la sección de política de contraseñas.

**Filtrado en SQL, no en memoria.** Los filtros por estado, prioridad y texto se
resuelven en la consulta, así que solo viajan las filas que se piden. El resumen
por estado se calcula con una única agregación.

## Próximos pasos (opcional)

- **Despliegue**: servicio web en Render y base de datos en Neon.
- ~~**Revocación de sesiones**~~: access tokens de 15 minutos y refresh rotativo con tabla de sesiones.
- ~~**Base de datos real**~~: migrado de ficheros JSON a PostgreSQL.
- ~~**Autenticación**~~: implementado con JWT (login/registro).
- ~~**Asignar tareas a usuarios**~~: cada tarea tiene `userId` y solo se muestran las del usuario.

## Tecnologías

- **Frontend**: React 18, Vite.
- **Backend**: Node.js, Express, **TypeScript** (arquitectura router → controller → service → repository), JWT, bcrypt, express-rate-limit.
- **Base de datos**: PostgreSQL con el driver `pg` y consultas parametrizadas.
