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

export type ProjectRoleName = 'OWNER' | 'EDITOR' | 'VIEWER';

/** Leer tareas: cualquier miembro. */
export const READ_ROLES: readonly ProjectRoleName[] = ['OWNER', 'EDITOR', 'VIEWER'];
/** Crear, editar, borrar y comentar tareas: todos menos VIEWER. */
export const WRITE_ROLES: readonly ProjectRoleName[] = ['OWNER', 'EDITOR'];

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

  /**
   * Comprueba que el usuario tiene en el proyecto uno de los roles admitidos y
   * devuelve el que tiene.
   *
   * Es la puerta de todas las operaciones sobre tareas. Hasta que existio, las
   * rutas de /api/tasks solo exigian estar autenticado: cualquier cuenta podia
   * leer, editar y borrar las tareas de cualquier proyecto.
   *
   * El propietario cuenta como OWNER aunque le faltase la fila de miembro, igual
   * que en `getById`: `create` la añade, pero la autoridad es `ownerId`.
   *
   * 404 si el proyecto no existe y 403 si existe y no hay acceso, el mismo
   * criterio que ya seguian `getById` y `assertOwner`.
   */
  async assertProjectRole(projectId: string, userId: string, allowed: readonly ProjectRoleName[]) {
    const project = await projectRepository.findById(projectId);
    if (!project) throw ApiError.notFound('Proyecto no encontrado');

    const role: ProjectRoleName | undefined =
      project.ownerId === userId
        ? 'OWNER'
        : project.members.find((m: { userId: string }) => m.userId === userId)?.role;

    if (!role) throw ApiError.forbidden('No tienes acceso a este proyecto');
    if (!allowed.includes(role)) {
      throw ApiError.forbidden('Tu rol en este proyecto no permite esta acción');
    }
    return role;
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
