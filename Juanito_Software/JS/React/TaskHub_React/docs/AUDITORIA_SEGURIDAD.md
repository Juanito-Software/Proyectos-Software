# Auditoría de seguridad y CI/CD — TaskHub_React

Fecha: 30 de agosto de 2026 · Estado: **auditoría, sin cambios aplicados**

---

## FASE 1 — Arquitectura

| # | Aspecto | Hallazgo |
|---|---------|----------|
| 1 | React | **18.3.1**, JSX sin TypeScript |
| 2 | Build | **Vite 8.1.5** (cliente) · **tsc** + script propio (servidor) |
| 3 | Gestor de paquetes | **npm**, tres `package.json` (raíz, server, client) |
| 4 | Backend | **Sí**: Node.js + **TypeScript 5.5** + **Express 4.21**, ESM (`"type": "module"`) |
| 5 | Base de datos | **PostgreSQL** (Neon en producción, local en desarrollo) |
| 6 | ORM | **Ninguno**. Driver `pg` 8.23 con SQL escrito a mano |
| 7 | Consultas SQL | Parametrizadas con marcadores `$1, $2…`. Ver Fase 3 |
| 8 | Autenticación | JWT propio (`jsonwebtoken` 9.0.3) + **bcrypt** 6.0, 10 rondas |
| 9 | Sesiones | **Sin cookies**. Token en `localStorage`, cabecera `Authorization: Bearer` |
| 10 | Secretos | `.env` (dotenv), ignorado por git. `.env.example` sin valores reales |
| 11 | CORS | `app.use(cors())` — **abierto a cualquier origen** |
| 12 | CSRF | **No aplica**: sin cookies de sesión, no hay envío automático de credenciales |
| 13 | Cabeceras HTTP | **Ninguna**. No hay `helmet` ni configuración manual |
| 14 | Logging | `console.log` con método, ruta, estado y duración. No registra cuerpos |
| 15 | Errores | Middleware central; oculta el mensaje interno en producción |
| 16 | Dependencias | 7 de producción en servidor, 2 en cliente. Ver Fase 4 |
| 17 | Tests | **37 comprobaciones** end-to-end en `verify.ts`, script propio sin framework |
| 18 | Lint / typecheck | **ESLint: no existe**. TypeScript `strict: true` solo en servidor |
| 19 | Despliegue | Render (servicio web) + Neon (base de datos), región Frankfurt |
| 20 | CI/CD | **No existe para este proyecto**. El monorepo tiene un `ci.yml` genérico que solo hace `node --check` de sintaxis |

**Arquitectura por capas:** `router → controller → service → repository`. En
producción un único proceso Express sirve el cliente React en `/`, el playground
en `/playground` y la API en `/api`.

---

## FASE 2 — Auditoría de seguridad

### Frontend (React)

| Comprobación | Resultado |
|---|---|
| XSS | **PASS** — cero usos de `dangerouslySetInnerHTML`, `innerHTML`, `eval` o `new Function`. React escapa por defecto |
| URLs controladas por el usuario | **PASS** — no se construyen enlaces con datos de entrada |
| Almacenamiento de tokens | **WARNING** — JWT en `localStorage`, accesible desde JavaScript |
| Secretos en el bundle | **PASS** — ninguna variable `VITE_` en el código |
| Source maps en producción | **PASS** — Vite no los genera salvo que se pidan; no están configurados |
| CSP | **FAIL** — no existe |
| Validación de entrada | **WARNING** — solo `required` de HTML; la validación real está en el servidor |

### Playground (HTML plano — sin escapado automático)

| Comprobación | Resultado |
|---|---|
| Consola de respuestas | **PASS** — usa `createTextNode` y `replaceChildren`, nunca `innerHTML`. Comentado explícitamente en el código |
| Título y descripción de tareas | **PASS** — pasan por `escapeHTML()` |
| `task.status`, `task.priority`, `task.id` | **WARNING** — se interpolan en `innerHTML` sin escapar. No explotable hoy: el estado y la prioridad están restringidos por `CHECK` en la base de datos y el id es un `UUID` generado por Postgres. Depende de invariantes del esquema, no de un escapado |
| Nombre de usuario en la cabecera | **PASS** — `innerText` |
| Mensajes emergentes | **PASS** — `innerText` |

### Backend / API

| Comprobación | Resultado |
|---|---|
| SQL Injection | **PASS** — ver Fase 3 |
| Command Injection | **NOT APPLICABLE** — no se ejecutan comandos del sistema |
| Path Traversal | **PASS** — `sendFile` solo con rutas construidas por el servidor |
| SSRF | **NOT APPLICABLE** — el servidor no hace peticiones salientes |
| CSRF | **NOT APPLICABLE** — sin cookies; el token va en una cabecera que el navegador no añade solo |
| CORS | **FAIL** — `cors()` sin opciones acepta cualquier origen |
| Autenticación | **PASS** — bcrypt con 10 rondas, mismo mensaje de error para usuario inexistente y contraseña incorrecta |
| Autorización | **PASS** — rol comprobado contra la base de datos en cada petición, no desde el JWT |
| IDOR / BOLA | **PASS** — el `user_id` va en el `WHERE` de todas las consultas; un recurso ajeno devuelve 404 |
| Rate limiting | **PASS** — 10 intentos / 15 min en autenticación, 300 / 15 min en el resto |
| Validación de entrada | **PASS** — validadores por ruta, con listas cerradas para estado y prioridad |
| Subida de archivos | **NOT APPLICABLE** — no existe |
| Exposición de datos | **PASS** — el hash nunca sale en las respuestas; hay un test que lo verifica |
| Manejo de errores | **PASS** — mensaje genérico en producción |
| Logging sensible | **PASS** — no se registran cuerpos ni cabeceras |
| Expiración de tokens | **WARNING** — 7 días, sin refresh ni revocación |
| JWT: algoritmo | **WARNING** — `jwt.verify` sin `algorithms` explícito |
| Contraseñas | **WARNING** — mínimo 6 caracteres, sin más requisitos |

### Configuración

| Comprobación | Resultado |
|---|---|
| `.env` ignorado | **PASS** — en el `.gitignore` del proyecto y del monorepo |
| `.env.example` | **PASS** — sin valores reales |
| Secretos en el código | **PASS** — solo una contraseña de prueba en `verify.ts`, que es correcto |
| `JWT_SECRET` por defecto | **FAIL** — ver hallazgo H-1 |
| Docker | **NOT APPLICABLE** — no se usa |
| HTTPS | **PASS** — lo termina Render; la base de datos exige TLS |
| Cabeceras de seguridad | **FAIL** — ninguna |

---

## FASE 3 — Auditoría de SQL

**Consultas analizadas: 16** (9 en `tasks.repository`, 6 en `users.repository`,
1 en `admin.service`), más 6 en la suite de verificación.

**Consultas con SQL Injection: 0.**

Se revisó el flujo completo de cada entrada de usuario:

| Entrada | Recorrido | Veredicto |
|---|---|---|
| `title`, `description` | validador → `$1`, `$2` | Parametrizado |
| `status`, `priority` | validador con **lista cerrada** → `$N` | Doble protección |
| `search` | validador → se envuelve en `%…%` **dentro del array de parámetros**, no en el SQL | Parametrizado. Un `%` o `_` en la búsqueda se trata como texto |
| `id` (rutas) | `$1` | Parametrizado |
| `userId` (del JWT) | `$N` en el `WHERE` de todas las consultas | Parametrizado |
| `username` | `$1` con `LOWER()` | Parametrizado |

**Interpolaciones dentro de cadenas SQL — todas revisadas:**

| Ubicación | Interpola | Origen | Veredicto |
|---|---|---|---|
| `users.repository` | `${COLUMNS}` | Constante del módulo | Seguro |
| `tasks.repository` | `${COLUMNS}` | Constante del módulo | Seguro |
| `tasks.repository:71` | `${conditions.join(' AND ')}` | Cadenas construidas internamente, con `$N` | Seguro |
| `tasks.repository:129` | `${field}` | **Lista blanca** `allowed = ['title','description','status','priority']` | Seguro — es el patrón correcto para SQL estructural |
| `tasks.repository:141` | `${assignments.join(', ')}` | Derivado de la lista blanca | Seguro |
| `db.ts:45` | `${schema}` | Variable de entorno `DB_SCHEMA`, la controla el operador | Seguro |
| `verify.ts:25,450` | `${testSchema}` | `crypto.randomUUID()` | Seguro |

**No hay** `ORDER BY` dinámico, ni `LIMIT/OFFSET` desde el usuario, ni `IN`
construido con concatenación, ni consultas generadas por plantillas.

**Observación positiva:** el campo mutable del `UPDATE` se resuelve con una
lista blanca explícita, que es exactamente lo que hay que hacer cuando el
elemento dinámico es estructural y no puede parametrizarse.

---

## FASE 4 — Dependencias

### Servidor: **0 vulnerabilidades**

### Cliente: **1 vulnerabilidad**

| Severidad | Paquete | Versión vulnerable | Problema | Impacto real | Corregible |
|---|---|---|---|---|---|
| **HIGH** | `nanoid` | `< 3.3.18` | Bucle infinito con generadores personalizados y tamaño cero | **Bajo.** Llega como dependencia transitiva de Vite, se usa solo durante el build y no forma parte del código que se envía al navegador | Sí, sin cambios incompatibles |

### Hallazgo adicional

`server/package.json` y `client/package.json` declaran `"taskhub": "file:.."`,
es decir, el paquete raíz como dependencia de sus propios subpaquetes. Es una
dependencia circular sin propósito, probablemente fruto de un `npm install`
lanzado en el directorio equivocado. No causa fallos hoy, pero ensucia el árbol
y puede dar problemas en instalaciones limpias.

---

## FASE 5 — Tests

**Estado actual: 37 comprobaciones end-to-end**, todas en `server/src/verify.ts`.

| Tipo | Estado |
|---|---|
| End-to-end de API | **37 comprobaciones** contra Postgres real, esquema aislado |
| Unitarios (servidor) | **Ninguno** |
| Unitarios / de componentes (cliente) | **Ninguno** |
| E2E de navegador | **Ninguno** |
| Cobertura | **No medida** |

### Lo que sí está cubierto

Autenticación, autorización por rol, aislamiento entre usuarios, CRUD completo,
validación de campos y filtros, traducción `completed` ↔ `status`, unicidad por
índice, borrado en cascada, que el registro no conceda rol admin y que el
listado de administración no filtre hashes.

### Huecos relevantes

| Hueco | Riesgo |
|---|---|
| **Todo el cliente React** sin un solo test | Alto — es la mitad del producto |
| Funciones puras sin tests unitarios (`normalize`, `resolveStatus`, validadores) | Medio — solo se ejercitan indirectamente vía HTTP |
| Expiración y manipulación de JWT | **Alto** — no se comprueba token caducado, firma inválida ni `alg: none` |
| Rate limiting | Medio — el middleware existe y nunca se ejercita |
| `PUT` | Bajo — solo se prueba `PATCH` |
| Regresión de inyección SQL | Medio — no hay ninguna prueba con carga maliciosa |

**Comparación:** TaskHub_Angular y TaskHub (FastAPI) sí tienen batería de
ataques a JWT. Este proyecto es el único de los tres que no la tiene.

---

## Hallazgos por severidad

| ID | Severidad | Problema | Ubicación |
|---|---|---|---|
| **H-1** | **HIGH** | `JWT_SECRET` tiene valor por defecto, y ese valor está publicado en el repositorio. Si la variable falta en producción, la aplicación arranca igualmente y cualquiera que lea el código puede firmar tokens válidos para cualquier usuario | `config/env.ts:14` |
| **H-2** | **HIGH** | Sin CI: las 37 comprobaciones solo se ejecutan si alguien se acuerda. Nada impide desplegar código que las rompa | — |
| **H-3** | **MEDIUM** | CORS abierto a cualquier origen | `app.ts:40` |
| **H-4** | **MEDIUM** | Sin cabeceras de seguridad: sin `X-Frame-Options` (clickjacking), sin `X-Content-Type-Options`, sin CSP | `app.ts` |
| **H-5** | **MEDIUM** | `jwt.verify` sin restringir el algoritmo | `token.service.ts:17` |
| **H-6** | **MEDIUM** | Sin tests de expiración ni manipulación de tokens | `verify.ts` |
| **H-7** | **MEDIUM** | Cliente React sin ningún test | `client/` |
| **H-8** | **MEDIUM** | `nanoid` con vulnerabilidad alta (impacto real bajo) | `client/` |
| **H-9** | **LOW** | Contraseñas de solo 6 caracteres mínimos | `auth.validation.ts` |
| **H-10** | **LOW** | Sin ESLint en ningún paquete | — |
| **H-11** | **LOW** | Playground interpola `status`, `priority` e `id` sin escapar | `public/index.html:1182` |
| **H-12** | **LOW** | Dependencia circular `taskhub: file:..` | `server/`, `client/` |
| **H-13** | **LOW** | Tokens de 7 días sin revocación posible | `env.ts` |

---

## Nota sobre secretos

**[SECRET DETECTADO]** — Durante las sesiones de configuración se expusieron en
conversación la contraseña de la base de datos de Neon (rotada ya tres veces),
un `JWT_SECRET` generado y la contraseña del administrador. **Deben rotarse
todas**, en el panel de Neon y en las variables de entorno de Render, y no
volver a pasar por ningún canal que no sea el propio panel.

No hay ningún secreto real dentro del repositorio.
