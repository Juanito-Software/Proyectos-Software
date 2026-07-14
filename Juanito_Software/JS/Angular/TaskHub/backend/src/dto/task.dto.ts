import { TaskPriority, TaskStatus } from '@prisma/client';
import { UserPublicDto } from './user.dto';

export interface CreateTaskInput {
  title: string;
  description?: string;
  projectId: string;
  assigneeId?: string;
  priority?: TaskPriority;
  deadline?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigneeId?: string | null;
  deadline?: string | null;
}

export interface CreateCommentInput {
  text: string;
}

export interface CommentDto {
  id: string;
  text: string;
  taskId: string;
  authorId: string;
  author: UserPublicDto;
  createdAt: Date;
}

export interface TaskDto {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  deadline: Date | null;
  projectId: string;
  assigneeId: string | null;
  assignee: UserPublicDto | null;
  creatorId: string;
  creator: UserPublicDto | null;
  createdAt: Date;
  updatedAt: Date;
  comments?: CommentDto[];
}
