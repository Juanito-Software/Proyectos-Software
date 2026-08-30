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
 * Política de contraseñas, replicada del servidor.
 *
 * La autoridad es `server/src/modules/auth/password-policy.ts`. Aquí solo se
 * duplican los límites para poder avisar antes de enviar el formulario, porque
 * cliente y servidor son paquetes npm distintos y no comparten módulos.
 *
 * **Si cambian allí, hay que cambiarlos aquí.** Un test end-to-end comprueba
 * que los dos coinciden, así que la desincronización rompe el CI en lugar de
 * pasar desapercibida.
 */
export const MIN_PASSWORD_LENGTH = 15;
export const MAX_PASSWORD_LENGTH = 72;

export const statusLabel = (value) =>
  STATUSES.find((s) => s.value === value)?.label ?? value;

export const priorityLabel = (value) =>
  PRIORITIES.find((p) => p.value === value)?.label ?? value;
