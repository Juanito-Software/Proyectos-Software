import { TaskStatus } from '@prisma/client';
import { taskRepository } from '../repositories/task.repository';
import { ApiError } from '../utils/ApiError';
import { CommentDto, CreateCommentInput, CreateTaskInput, TaskDto, UpdateTaskInput } from '../dto/task.dto';
import { toPublicDto } from './user.service';
import { projectService, READ_ROLES, WRITE_ROLES, ProjectRoleName } from './project.service';

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

/**
 * Carga la tarea y exige al usuario uno de los roles admitidos en SU proyecto.
 *
 * El proyecto se toma de la tarea guardada, nunca de la peticion: si viniera
 * del cuerpo, bastaria con mandar el id de un proyecto propio para tocar una
 * tarea ajena.
 */
async function findTaskWithRole(id: string, userId: string, allowed: readonly ProjectRoleName[]) {
  const task = await taskRepository.findById(id);
  if (!task) throw ApiError.notFound('Tarea no encontrada');
  await projectService.assertProjectRole(task.projectId, userId, allowed);
  return task;
}

export const taskService = {
  async create(creatorId: string, input: CreateTaskInput) {
    await projectService.assertProjectRole(input.projectId, creatorId, WRITE_ROLES);
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

  /**
   * Sin `projectId`, la consulta se limita a los proyectos del usuario en el
   * repositorio (`visibleTo`). Con `projectId`, ademas se comprueba el acceso
   * antes, para responder 403 en vez de una lista vacia que no dice por que.
   */
  async list(
    userId: string,
    filters: { projectId?: string; status?: TaskStatus; assigneeId?: string },
    page: number,
    limit: number,
  ) {
    if (filters.projectId) {
      await projectService.assertProjectRole(filters.projectId, userId, READ_ROLES);
    }
    const tasks = await taskRepository.findMany({
      ...filters,
      visibleTo: userId,
      skip: (page - 1) * limit,
      take: limit,
    });
    return tasks.map(toTaskDto);
  },

  async getById(id: string, userId: string) {
    const task = await findTaskWithRole(id, userId, READ_ROLES);
    return toTaskDto(task);
  },

  async update(id: string, userId: string, input: UpdateTaskInput) {
    await findTaskWithRole(id, userId, WRITE_ROLES);
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

  async remove(id: string, userId: string) {
    await findTaskWithRole(id, userId, WRITE_ROLES);
    await taskRepository.delete(id);
  },

  async addComment(taskId: string, authorId: string, input: CreateCommentInput) {
    await findTaskWithRole(taskId, authorId, WRITE_ROLES);
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
