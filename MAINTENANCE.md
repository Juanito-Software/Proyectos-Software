# Historial de mantenimiento del repositorio

Registro de operaciones estructurales sobre el repositorio (no sobre el código
de los proyectos).

---

## 2026-07-26 — Reducción de superficie de dependencias

Ronda de actualización y limpieza de dependencias en los proyectos mantenidos,
con el objetivo de eliminar vulnerabilidades reales en lugar de silenciarlas.

**Cambios aplicados:**

- `unified-chat-widget`: retirado el soporte de BitChute, DLive, Odysee y
  Trovo (servicios, servidores auxiliares y documentación). La carpeta
  `messages/` deja de versionarse por ser estado de ejecución.
- `Angular/TaskHub/backend`: `bcrypt` actualizado de v5 a v6, lo que elimina
  la cadena `node-pre-gyp` / `node-gyp` / `tar` (48 paquetes menos) que
  arrastraba las vulnerabilidades críticas del proyecto. Compatibilidad de
  hashes entre versiones verificada con el flujo de login.
- `Angular/TaskHub/frontend`: actualizado de Angular 19 a 21 mediante
  `ng update`, en dos saltos mayores verificados por separado, con
  `@angular/material` y `@angular/cdk` alineados. Migrado además al paquete
  `@angular/build`.
- `npm audit fix` aplicado en el resto de proyectos JavaScript mantenidos.
- Cerradas las pull requests de Dependabot que apuntaban a rutas eliminadas
  en la reestructuración.

**Resultado:** de 590 a 385 alertas de Dependabot (−35%), y de 19 a 13
críticas. Toda la reducción procede de correcciones efectivas, no de
descartes.

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
