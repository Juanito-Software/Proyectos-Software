import { TaskStatus } from '@prisma/client';
import { taskRepository } from '../repositories/task.repository';
import { ApiError } from '../utils/ApiError';
import { CommentDto, CreateCommentInput, CreateTaskInput, TaskDto, UpdateTaskInput } from '../dto/task.dto';
import { toPublicDto } from './user.service';

type RawUser = Parameters<typeof toPublicDto>[0];

function toCommentDto(comment: { author: RawUser } & Omit<CommentDto, 'author'>): CommentDto {
  return { ...comment, author: toPublicDto(comment.author) };
}

function toTaskDto(task: {
  assignee: RawUser | null;
  creator: RawUser | null;
  comments?: (Omit<CommentDto, 'author'> & { author: RawUser })[];
} & Omit<TaskDto, 'assignee' | 'creator' | 'comments'>): TaskDto {
  return {
    ...task,
    assignee: task.assignee ? toPublicDto(task.assignee) : null,
    creator: task.creator ? toPublicDto(task.creator) : null,
    comments: task.comments?.map(toCommentDto),
  };
}

export const taskService = {
  async create(creatorId: string, input: CreateTaskInput) {
    const task = await taskRepository.create({
      title: input.title,
      description: input.description,
      priority: input.priority,
      deadline: input.deadline ? new Date(input.deadline) : undefined,
      project: { connect: { id: input.projectId } },
      creator: { connect: { id: creatorId } },
      assignee: input.assigneeId ? { connect: { id: input.assigneeId } } : undefined,
    });
    return toTaskDto(task);
  },

  async list(filters: { projectId?: string; status?: TaskStatus; assigneeId?: string }, page: number, limit: number) {
    const tasks = await taskRepository.findMany({
      ...filters,
      skip: (page - 1) * limit,
      take: limit,
    });
    return tasks.map(toTaskDto);
  },

  async getById(id: string) {
    const task = await taskRepository.findById(id);
    if (!task) throw ApiError.notFound('Tarea no encontrada');
    return toTaskDto(task);
  },

  async update(id: string, input: UpdateTaskInput) {
    const exists = await taskRepository.findById(id);
    if (!exists) throw ApiError.notFound('Tarea no encontrada');
    const task = await taskRepository.update(id, {
      title: input.title,
      description: input.description,
      status: input.status,
      priority: input.priority,
      deadline: input.deadline === null ? null : input.deadline ? new Date(input.deadline) : undefined,
      assignee:
        input.assigneeId === null
          ? { disconnect: true }
          : input.assigneeId
            ? { connect: { id: input.assigneeId } }
            : undefined,
    });
    return toTaskDto(task);
  },

  async remove(id: string) {
    await this.getById(id);
    await taskRepository.delete(id);
  },

  async addComment(taskId: string, authorId: string, input: CreateCommentInput) {
    await this.getById(taskId);
    const comment = await taskRepository.addComment(taskId, authorId, input.text);
    return toCommentDto(comment);
  },

  async dashboardSummary(userId: string) {
    const grouped = await taskRepository.countByStatusForUser(userId);
    const summary: Record<TaskStatus, number> = { TODO: 0, IN_PROGRESS: 0, IN_REVIEW: 0, DONE: 0 };
    for (const g of grouped) summary[g.status] = g._count;
    return summary;
  },
};
