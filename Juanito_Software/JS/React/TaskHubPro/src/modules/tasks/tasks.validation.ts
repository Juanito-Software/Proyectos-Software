import { Request } from 'express';
import { ValidatorFn } from '../../middleware/validate.middleware';

const VALID_STATUSES = ['pending', 'in-progress', 'completed'];
const VALID_PRIORITIES = ['low', 'medium', 'high'];

export const createTaskValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { title, description, status, priority } = req.body;

  // Title validation
  if (title === undefined || title === null) {
    errors.push("Field 'title' is required.");
  } else if (typeof title !== 'string') {
    errors.push("Field 'title' must be a string.");
  } else {
    const trimmedTitle = title.trim();
    if (trimmedTitle.length < 3) {
      errors.push("Field 'title' must be at least 3 characters long.");
    } else if (trimmedTitle.length > 100) {
      errors.push("Field 'title' must not exceed 100 characters.");
    }
  }

  // Description validation
  if (description === undefined || description === null) {
    errors.push("Field 'description' is required.");
  } else if (typeof description !== 'string') {
    errors.push("Field 'description' must be a string.");
  }

  // Status validation (optional for create)
  if (status !== undefined && status !== null) {
    if (!VALID_STATUSES.includes(status)) {
      errors.push(`Field 'status' must be one of: ${VALID_STATUSES.join(', ')}.`);
    }
  }

  // Priority validation (optional for create)
  if (priority !== undefined && priority !== null) {
    if (!VALID_PRIORITIES.includes(priority)) {
      errors.push(`Field 'priority' must be one of: ${VALID_PRIORITIES.join(', ')}.`);
    }
  }

  return errors.length > 0 ? errors : null;
};

export const updateTaskValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { title, description, status, priority } = req.body;

  // Verify at least one field is provided
  if (
    title === undefined &&
    description === undefined &&
    status === undefined &&
    priority === undefined
  ) {
    errors.push('At least one field (title, description, status, priority) must be provided for updates.');
    return errors;
  }

  // Title validation
  if (title !== undefined && title !== null) {
    if (typeof title !== 'string') {
      errors.push("Field 'title' must be a string.");
    } else {
      const trimmedTitle = title.trim();
      if (trimmedTitle.length < 3) {
        errors.push("Field 'title' must be at least 3 characters long.");
      } else if (trimmedTitle.length > 100) {
        errors.push("Field 'title' must not exceed 100 characters.");
      }
    }
  }

  // Description validation
  if (description !== undefined && description !== null) {
    if (typeof description !== 'string') {
      errors.push("Field 'description' must be a string.");
    }
  }

  // Status validation
  if (status !== undefined && status !== null) {
    if (!VALID_STATUSES.includes(status)) {
      errors.push(`Field 'status' must be one of: ${VALID_STATUSES.join(', ')}.`);
    }
  }

  // Priority validation
  if (priority !== undefined && priority !== null) {
    if (!VALID_PRIORITIES.includes(priority)) {
      errors.push(`Field 'priority' must be one of: ${VALID_PRIORITIES.join(', ')}.`);
    }
  }

  return errors.length > 0 ? errors : null;
};

export const filterTasksValidator: ValidatorFn = (req: Request): string[] | null => {
  const errors: string[] = [];
  const { status, priority } = req.query;

  if (status !== undefined && typeof status === 'string' && !VALID_STATUSES.includes(status)) {
    errors.push(`Filter 'status' must be one of: ${VALID_STATUSES.join(', ')}.`);
  }

  if (priority !== undefined && typeof priority === 'string' && !VALID_PRIORITIES.includes(priority)) {
    errors.push(`Filter 'priority' must be one of: ${VALID_PRIORITIES.join(', ')}.`);
  }

  return errors.length > 0 ? errors : null;
};
