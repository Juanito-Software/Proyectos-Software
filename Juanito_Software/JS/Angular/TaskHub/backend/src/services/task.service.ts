import { TaskStatus } from '@prisma/client';
import { taskRepository } from '../repositories/task.repository';
import { ApiError } from '../utils/ApiError';
import { CreateCommentInput, CreateTaskInput, UpdateTaskInput } from '../dto/task.dto';

export const taskService = {
  create(creatorId: string, input: CreateTaskInput) {
    return taskRepository.create({
      title: input.title,
      description: input.description,
      priority: input.priority,
      deadline: input.deadline ? new Date(input.deadline) : undefined,
      project: { connect: { id: input.projectId } },
      creator: { connect: { id: creatorId } },
      assignee: input.assigneeId ? { connect: { id: input.assigneeId } } : undefined,
    });
  },

  list(filters: { projectId?: string; status?: TaskStatus; assigneeId?: string }, page: number, limit: number) {
    return taskRepository.findMany({
      ...filters,
      skip: (page - 1) * limit,
      take: limit,
    });
  },

  async getById(id: string) {
    const task = await taskRepository.findById(id);
    if (!task) throw ApiError.notFound('Tarea no encontrada');
    return task;
  },

  async update(id: string, input: UpdateTaskInput) {
    await this.getById(id);
    return taskRepository.update(id, {
      ...input,
      deadline: input.deadline ? new Date(input.deadline) : undefined,
    });
  },

  async remove(id: string) {
    await this.getById(id);
    await taskRepository.delete(id);
  },

  async addComment(taskId: string, authorId: string, input: CreateCommentInput) {
    await this.getById(taskId);
    return taskRepository.addComment(taskId, authorId, input.text);
  },

  async dashboardSummary(userId: string) {
    const grouped = await taskRepository.countByStatusForUser(userId);
    const summary: Record<TaskStatus, number> = { TODO: 0, IN_PROGRESS: 0, IN_REVIEW: 0, DONE: 0 };
    for (const g of grouped) summary[g.status] = g._count;
    return summary;
  },
};
