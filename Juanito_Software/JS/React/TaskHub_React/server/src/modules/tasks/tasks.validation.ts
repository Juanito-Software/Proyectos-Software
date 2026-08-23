import { ValidatorFn } from '../../middleware/validate.middleware.js';
import { TASK_STATUSES, TASK_PRIORITIES, isTaskStatus, isTaskPriority } from './tasks.types.js';

const STATUS_LIST = TASK_STATUSES.join(', ');
const PRIORITY_LIST = TASK_PRIORITIES.join(', ');

function validateOptionalFields(body: Record<string, unknown>, errors: string[]): void {
  const { description, status, priority, completed } = body;

  if (description !== undefined && description !== null && typeof description !== 'string') {
    errors.push("El campo 'description' debe ser texto");
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
  } else if (title.trim().length > 100) {
    errors.push('El título no puede superar los 100 caracteres');
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
    } else if (title.trim().length > 100) {
      errors.push('El título no puede superar los 100 caracteres');
    }
  }

  validateOptionalFields(body, errors);
  return errors.length > 0 ? errors : null;
};

export const filterTasksValidator: ValidatorFn = (req): string[] | null => {
  const errors: string[] = [];
  const { status, priority } = req.query;

  if (status !== undefined && !isTaskStatus(status)) {
    errors.push(`El filtro 'status' debe ser uno de: ${STATUS_LIST}`);
  }
  if (priority !== undefined && !isTaskPriority(priority)) {
    errors.push(`El filtro 'priority' debe ser uno de: ${PRIORITY_LIST}`);
  }

  return errors.length > 0 ? errors : null;
};
