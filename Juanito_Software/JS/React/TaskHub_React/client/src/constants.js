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

export const statusLabel = (value) =>
  STATUSES.find((s) => s.value === value)?.label ?? value;

export const priorityLabel = (value) =>
  PRIORITIES.find((p) => p.value === value)?.label ?? value;
