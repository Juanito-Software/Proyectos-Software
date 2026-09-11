import { projectRepository } from '../repositories/project.repository';
import { userRepository } from '../repositories/user.repository';
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

  /**
   * Añade a un usuario, buscado por email, con rol EDITOR o VIEWER.
   *
   * Los dos casos que antes llegaban como 500 —ya es miembro, o el usuario no
   * existe— se resuelven aqui con 409 y 404. La comprobacion previa no cubre dos
   * altas simultaneas: la segunda llega a insertar y la base de datos la rechaza
   * por la clave unica (P2002), que tambien se traduce a 409.
   *
   * Responder «no existe ningun usuario con ese email» dice que emails estan
   * registrados. Se acepta a sabiendas: solo lo ve el propietario de un proyecto,
   * y la alternativa —listar a todos los usuarios— enseñaria mas.
   */
  async addMember(id: string, ownerId: string, input: AddMemberInput) {
    const project = await this.assertOwner(id, ownerId);

    const user = await userRepository.findByEmail(input.email);
    if (!user) throw ApiError.notFound('No existe ningún usuario con ese email');

    const alreadyMember =
      project.ownerId === user.id || project.members.some((m: { userId: string }) => m.userId === user.id);
    if (alreadyMember) throw ApiError.conflict('Ese usuario ya es miembro del proyecto');

    try {
      const member = await projectRepository.addMember(id, user.id, input.role ?? 'VIEWER');
      return { ...member, user: toPublicDto(member.user) };
    } catch (err) {
      if ((err as { code?: unknown }).code === 'P2002') {
        throw ApiError.conflict('Ese usuario ya es miembro del proyecto');
      }
      throw err;
    }
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
