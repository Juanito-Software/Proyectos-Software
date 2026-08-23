import { projectRepository } from '../repositories/project.repository';
import { ApiError } from '../utils/ApiError';
import { AddMemberInput, CreateProjectInput, UpdateProjectInput } from '../dto/project.dto';
import { toPublicDto } from './user.service';

function toProjectDto(project: {
  owner: Parameters<typeof toPublicDto>[0];
  members: { user: Parameters<typeof toPublicDto>[0] }[];
  [key: string]: unknown;
}) {
  return {
    ...project,
    owner: toPublicDto(project.owner),
    members: project.members.map((m) => ({ ...m, user: toPublicDto(m.user) })),
  };
}

export const projectService = {
  create(ownerId: string, input: CreateProjectInput) {
    return projectRepository.create({
      name: input.name,
      description: input.description,
      owner: { connect: { id: ownerId } },
      members: { create: { userId: ownerId, role: 'OWNER' } },
    });
  },

  listForUser(userId: string, page: number, limit: number, search?: string) {
    return projectRepository.findManyForUser(userId, {
      skip: (page - 1) * limit,
      take: limit,
      search,
    });
  },

  async getById(id: string, userId: string) {
    const project = await projectRepository.findById(id);
    if (!project) throw ApiError.notFound('Proyecto no encontrado');

    const isMember = project.ownerId === userId || project.members.some((m: { userId: string }) => m.userId === userId);
    if (!isMember) throw ApiError.forbidden('No tienes acceso a este proyecto');

    return toProjectDto(project);
  },

  async update(id: string, userId: string, input: UpdateProjectInput) {
    await this.assertOwner(id, userId);
    return projectRepository.update(id, input);
  },

  async remove(id: string, userId: string) {
    await this.assertOwner(id, userId);
    await projectRepository.delete(id);
  },

  async addMember(id: string, userId: string, input: AddMemberInput) {
    await this.assertOwner(id, userId);
    return projectRepository.addMember(id, input.userId, input.role);
  },

  async assertOwner(projectId: string, userId: string) {
    const project = await projectRepository.findById(projectId);
    if (!project) throw ApiError.notFound('Proyecto no encontrado');
    if (project.ownerId !== userId) {
      throw ApiError.forbidden('Solo el propietario puede realizar esta acción');
    }
    return project;
  },
};
