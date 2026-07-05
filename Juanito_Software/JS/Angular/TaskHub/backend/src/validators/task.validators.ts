import { z } from 'zod';
import { TaskPriority, TaskStatus } from '@prisma/client';

export const createTaskSchema = z.object({
  body: z.object({
    title: z.string().trim().min(2, 'El título debe tener al menos 2 caracteres'),
    description: z.string().trim().max(2000).optional(),
    projectId: z.string().uuid(),
    assigneeId: z.string().uuid().optional(),
    priority: z.nativeEnum(TaskPriority).optional(),
    deadline: z.string().datetime().optional(),
  }),
});

export const updateTaskSchema = z.object({
  body: z.object({
    title: z.string().trim().min(2).optional(),
    description: z.string().trim().max(2000).optional(),
    status: z.nativeEnum(TaskStatus).optional(),
    priority: z.nativeEnum(TaskPriority).optional(),
    assigneeId: z.string().uuid().optional(),
    deadline: z.string().datetime().optional(),
  }),
});

export const createCommentSchema = z.object({
  body: z.object({
    text: z.string().trim().min(1, 'El comentario no puede estar vacío').max(1000),
  }),
});

export const listTasksSchema = z.object({
  body: z.object({}).optional(),
  query: z.object({
    projectId: z.string().uuid().optional(),
    status: z.nativeEnum(TaskStatus).optional(),
    assigneeId: z.string().uuid().optional(),
    page: z.coerce.number().int().positive().default(1),
    limit: z.coerce.number().int().positive().max(100).default(20),
  }),
});
