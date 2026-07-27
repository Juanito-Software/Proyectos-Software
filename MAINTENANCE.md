# Historial de mantenimiento del repositorio

Registro de operaciones estructurales sobre el repositorio (no sobre el código
de los proyectos).

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

Desactivado el modo debug de Flask en las cuatro aplicaciones que lo tenían
activo. El depurador de Werkzeug permite ejecutar código Python arbitrario
desde el navegador; en dos de ellas se combinaba con `host='0.0.0.0'`, lo que
lo exponía a toda la red local.

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
