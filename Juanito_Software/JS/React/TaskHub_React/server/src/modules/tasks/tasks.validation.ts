import { ValidatorFn } from '../../middleware/validate.middleware.js';
import { TASK_STATUSES, TASK_PRIORITIES, isTaskStatus, isTaskPriority } from './tasks.types.js';

const STATUS_LIST = TASK_STATUSES.join(', ');
const PRIORITY_LIST = TASK_PRIORITIES.join(', ');

/**
 * Límites de longitud.
 *
 * No son cifras redondas por costumbre, son decisiones sobre para qué sirve
 * cada campo:
 *
 * - **Título, 100.** Ya existía. Es una línea de una lista; más no cabe en la
 *   interfaz sin recortarlo.
 * - **Descripción, 5 000.** Unas dos páginas de texto. Da sitio de sobra para
 *   apuntar el contexto de una tarea y corta muy por debajo de lo que sería un
 *   abuso. Antes no había ninguno: se aceptaban 50 000 caracteres, y el único
 *   techo era el límite de 100 kB del cuerpo, que es un accidente y no una
 *   decisión.
 * - **Búsqueda, 200.** Nadie escribe más de doscientos caracteres para buscar
 *   entre sus propias tareas. Importa más que los otros dos porque el valor
 *   acaba en un `ILIKE '%…%'`, que no puede usar índice y recorre la tabla
 *   entera: una búsqueda larga cuesta trabajo real al servidor.
 */
const MAX_TITLE = 100;
const MAX_DESCRIPTION = 5_000;
const MAX_SEARCH = 200;

function validateOptionalFields(body: Record<string, unknown>, errors: string[]): void {
  const { description, status, priority, completed } = body;

  if (description !== undefined && description !== null && typeof description !== 'string') {
    errors.push("El campo 'description' debe ser texto");
  } else if (typeof description === 'string' && description.length > MAX_DESCRIPTION) {
    errors.push(`La descripción no puede superar los ${MAX_DESCRIPTION} caracteres`);
  }
  if (status !== undefined && status !== null && !isTaskStatus(status)) {
    errors.push(`El campo 'status' debe ser uno de: ${STATUS_LIST}`);
  }
  if (priority !== undefined && priority !== null && !isTaskPriority(priority)) {
    errors.push(`El campo 'priority' debe ser uno de: ${PRIORITY_LIST}`);
  }
  if (completed !== undefined && typeof completed !== 'boolean') {
    errors.push("El campo 'completed' debe ser true o false");
  }
}

export const createTaskValidator: ValidatorFn = (req): string[] | null => {
  const errors: string[] = [];
  const body = (req.body ?? {}) as Record<string, unknown>;
  const { title } = body;

  if (typeof title !== 'string' || !title.trim()) {
    errors.push('El título es obligatorio');
  } else if (title.trim().length > MAX_TITLE) {
    errors.push(`El título no puede superar los ${MAX_TITLE} caracteres`);
  }

  validateOptionalFields(body, errors);
  return errors.length > 0 ? errors : null;
};

export const updateTaskValidator: ValidatorFn = (req): string[] | null => {
  const errors: string[] = [];
  const body = (req.body ?? {}) as Record<string, unknown>;
  const { title, description, status, priority, completed } = body;

  if (
    title === undefined &&
    description === undefined &&
    status === undefined &&
    priority === undefined &&
    completed === undefined
  ) {
    errors.push('Debes enviar al menos un campo para actualizar (title, description, status, priority o completed)');
    return errors;
  }

  if (title !== undefined) {
    if (typeof title !== 'string' || !title.trim()) {
      errors.push('El título no puede estar vacío');
    } else if (title.trim().length > MAX_TITLE) {
      errors.push(`El título no puede superar los ${MAX_TITLE} caracteres`);
    }
  }

  validateOptionalFields(body, errors);
  return errors.length > 0 ? errors : null;
};

export const filterTasksValidator: ValidatorFn = (req): string[] | null => {
  const errors: string[] = [];
  const { status, priority, search } = req.query;

  if (status !== undefined && !isTaskStatus(status)) {
    errors.push(`El filtro 'status' debe ser uno de: ${STATUS_LIST}`);
  }
  if (priority !== undefined && !isTaskPriority(priority)) {
    errors.push(`El filtro 'priority' debe ser uno de: ${PRIORITY_LIST}`);
  }
  // El término de búsqueda acaba en un ILIKE con comodines a ambos lados, que
  // recorre la tabla entera sin poder usar índice. Sin límite, una cadena de
  // miles de caracteres es trabajo regalado para el servidor.
  if (typeof search === 'string' && search.length > MAX_SEARCH) {
    errors.push(`La búsqueda no puede superar los ${MAX_SEARCH} caracteres`);
  }

  return errors.length > 0 ? errors : null;
};
