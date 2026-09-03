/**
 * Etiquetas de estado y prioridad.
 *
 * Los valores son los que acepta la API; las etiquetas, lo que ve el usuario.
 * Están en un único sitio para que el formulario, la tarjeta de tarea y los
 * filtros no se contradigan entre sí.
 */
export const STATUSES = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in-progress', label: 'En progreso' },
  { value: 'completed', label: 'Completada' },
];

export const PRIORITIES = [
  { value: 'low', label: 'Baja' },
  { value: 'medium', label: 'Media' },
  { value: 'high', label: 'Alta' },
];

/**
 * La política de contraseñas vive en `./passwordPolicy.js`, que además de los
 * límites tiene las reglas de composición y la validación previa al envío.
 *
 * Antes estaba aquí; se movió al crecer, porque unas constantes sueltas no
 * daban sitio a explicar de dónde sale cada regla ni qué parte es de NIST y
 * cuál es decisión propia.
 */

export const statusLabel = (value) =>
  STATUSES.find((s) => s.value === value)?.label ?? value;

export const priorityLabel = (value) =>
  PRIORITIES.find((p) => p.value === value)?.label ?? value;
