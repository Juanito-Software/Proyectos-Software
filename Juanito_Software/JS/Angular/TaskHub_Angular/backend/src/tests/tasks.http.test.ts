import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from 'vitest';

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../repositories/task.repository', () => ({
  taskRepository: {
    create: vi.fn(),
    findMany: vi.fn(),
    findById: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    addComment: vi.fn(),
    countByStatusForUser: vi.fn(),
  },
}));
vi.mock('../repositories/project.repository', () => ({
  projectRepository: {
    create: vi.fn(),
    findManyForUser: vi.fn(),
    findById: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    addMember: vi.fn(),
    findMembership: vi.fn(),
  },
}));

import { taskRepository } from '../repositories/task.repository';
import { projectRepository } from '../repositories/project.repository';
import { arrancar, peticion, tokenDe, usuarioCrudo } from './http';

/**
 * Quien puede hacer que con las tareas de un proyecto.
 *
 * Hasta este fichero, las rutas de /api/tasks solo exigian estar autenticado:
 * cualquier cuenta —y el registro es libre— podia listar, leer, editar y borrar
 * las tareas de cualquier proyecto. Los proyectos si comprobaban la pertenencia;
 * las tareas no comprobaban nada. Se descubrio con estas mismas peticiones.
 *
 * La politica, decidida el 11 de septiembre de 2026:
 *
 *   | Rol en el proyecto | Leer | Crear, editar, borrar, comentar |
 *   |--------------------|------|---------------------------------|
 *   | OWNER              | si   | si                              |
 *   | EDITOR             | si   | si                              |
 *   | VIEWER             | si   | no -> 403                       |
 *   | ajeno al proyecto  | no   | no -> 403                       |
 *
 * Cada caso comprueba DOS cosas: el codigo de estado y si la escritura llego al
 * repositorio. La segunda es la que importa. Un 403 devuelto DESPUES de borrar
 * seguiria pasando un test que solo mirase el estado.
 */

const P1 = '11111111-1111-4111-8111-111111111111';
const INEXISTENTE = '99999999-9999-4999-8999-999999999999';

const PROYECTO = {
  id: P1,
  name: 'Informe',
  description: null,
  ownerId: 'ana',
  owner: usuarioCrudo('ana'),
  createdAt: new Date('2026-01-01'),
  updatedAt: new Date('2026-01-01'),
  members: [
    { id: 'm1', projectId: P1, userId: 'ana', role: 'OWNER', user: usuarioCrudo('ana') },
    { id: 'm2', projectId: P1, userId: 'eva', role: 'EDITOR', user: usuarioCrudo('eva') },
    { id: 'm3', projectId: P1, userId: 'vic', role: 'VIEWER', user: usuarioCrudo('vic') },
  ],
};

const TAREA = {
  id: 't1',
  title: 'Secreta del proyecto',
  description: null,
  status: 'TODO',
  priority: 'MEDIUM',
  deadline: null,
  projectId: P1,
  assigneeId: null,
  creatorId: 'ana',
  createdAt: new Date('2026-01-01'),
  updatedAt: new Date('2026-01-01'),
  assignee: null,
  creator: usuarioCrudo('ana'),
  comments: [],
  project: { id: P1, ownerId: 'ana' },
};

const tareas = vi.mocked(taskRepository);
const proyectos = vi.mocked(projectRepository);

let api: Awaited<ReturnType<typeof arrancar>>;
beforeAll(async () => (api = await arrancar()));
afterAll(() => api.cerrar());

beforeEach(() => {
  vi.clearAllMocks();
  proyectos.findById.mockImplementation((async (id: string) => (id === P1 ? PROYECTO : null)) as never);
  tareas.findById.mockImplementation((async (id: string) => (id === 't1' ? TAREA : null)) as never);
  tareas.findMany.mockResolvedValue([TAREA] as never);
  tareas.create.mockResolvedValue(TAREA as never);
  tareas.update.mockResolvedValue(TAREA as never);
  tareas.delete.mockResolvedValue(undefined as never);
  tareas.addComment.mockResolvedValue({
    id: 'c1', text: 'hola', taskId: 't1', authorId: 'eva', author: usuarioCrudo('eva'), createdAt: new Date('2026-01-01'),
  } as never);
});

type Escritura = 'create' | 'update' | 'delete' | 'addComment';

const ESCRITURAS: { nombre: string; metodo: string; ruta: string; cuerpo?: unknown; efecto: Escritura; ok: number }[] = [
  { nombre: 'crear tarea', metodo: 'POST', ruta: '/api/tasks', cuerpo: { title: 'Nueva', projectId: P1 }, efecto: 'create', ok: 201 },
  { nombre: 'editar tarea', metodo: 'PUT', ruta: '/api/tasks/t1', cuerpo: { title: 'Pisada' }, efecto: 'update', ok: 200 },
  { nombre: 'borrar tarea', metodo: 'DELETE', ruta: '/api/tasks/t1', efecto: 'delete', ok: 204 },
  { nombre: 'comentar', metodo: 'POST', ruta: '/api/tasks/t1/comments', cuerpo: { text: 'hola' }, efecto: 'addComment', ok: 201 },
];

describe.each(ESCRITURAS)('$nombre ($metodo $ruta)', ({ metodo, ruta, cuerpo, efecto, ok }) => {
  it.each([
    ['alguien ajeno al proyecto', 'bob'],
    ['un VIEWER', 'vic'],
  ])('%s recibe 403 y no escribe nada', async (_quien, usuario) => {
    const res = await peticion(api.url, metodo, ruta, { token: tokenDe(usuario), cuerpo });

    expect(res.status).toBe(403);
    expect(tareas[efecto]).not.toHaveBeenCalled();
  });

  it.each([
    ['el OWNER', 'ana'],
    ['un EDITOR', 'eva'],
  ])('%s puede, y la escritura llega al repositorio', async (_quien, usuario) => {
    const res = await peticion(api.url, metodo, ruta, { token: tokenDe(usuario), cuerpo });

    expect(res.status).toBe(ok);
    expect(tareas[efecto]).toHaveBeenCalledTimes(1);
  });
});

describe('leer una tarea (GET /api/tasks/:id)', () => {
  it('alguien ajeno recibe 403, y la respuesta no lleva nada de la tarea', async () => {
    const res = await peticion(api.url, 'GET', '/api/tasks/t1', { token: tokenDe('bob') });

    expect(res.status).toBe(403);
    // Ni el titulo ni el id del proyecto: un 403 con la tarea dentro seria el
    // mismo agujero con otro codigo de estado.
    const texto = await res.text();
    expect(texto).not.toContain('Secreta del proyecto');
    expect(texto).not.toContain(P1);
  });

  it.each([
    ['un VIEWER', 'vic'],
    ['un EDITOR', 'eva'],
    ['el OWNER', 'ana'],
  ])('%s puede leerla', async (_quien, usuario) => {
    const res = await peticion(api.url, 'GET', '/api/tasks/t1', { token: tokenDe(usuario) });

    expect(res.status).toBe(200);
    expect((await res.json()).title).toBe('Secreta del proyecto');
  });
});

describe('listar tareas (GET /api/tasks)', () => {
  it('de un proyecto ajeno: 403 sin llegar a consultar', async () => {
    const res = await peticion(api.url, 'GET', `/api/tasks?projectId=${P1}`, { token: tokenDe('bob') });

    expect(res.status).toBe(403);
    expect(tareas.findMany).not.toHaveBeenCalled();
  });

  it('de un proyecto propio, un VIEWER las ve', async () => {
    const res = await peticion(api.url, 'GET', `/api/tasks?projectId=${P1}`, { token: tokenDe('vic') });

    expect(res.status).toBe(200);
    expect(tareas.findMany).toHaveBeenCalledWith(expect.objectContaining({ projectId: P1, visibleTo: 'vic' }));
  });

  it('sin projectId, la consulta se restringe a los proyectos del usuario', async () => {
    // Era la peor de las cinco rutas: sin filtros, `where` quedaba vacio y
    // devolvia las tareas de toda la base de datos. Que el filtro llegue de
    // verdad a Prisma lo comprueba task.repository.test.ts.
    const res = await peticion(api.url, 'GET', '/api/tasks', { token: tokenDe('bob') });

    expect(res.status).toBe(200);
    expect(tareas.findMany).toHaveBeenCalledWith(expect.objectContaining({ visibleTo: 'bob' }));
  });
});

describe('lo que no existe', () => {
  it('editar una tarea inexistente: 404 y nada escrito', async () => {
    const res = await peticion(api.url, 'PUT', '/api/tasks/nope', { token: tokenDe('ana'), cuerpo: { title: 'X1' } });

    expect(res.status).toBe(404);
    expect(tareas.update).not.toHaveBeenCalled();
  });

  it('crear en un proyecto inexistente: 404, no un 500 de clave foranea', async () => {
    const res = await peticion(api.url, 'POST', '/api/tasks', {
      token: tokenDe('ana'),
      cuerpo: { title: 'Nueva', projectId: INEXISTENTE },
    });

    expect(res.status).toBe(404);
    expect(tareas.create).not.toHaveBeenCalled();
  });
});

describe('sin token', () => {
  it.each([
    ['GET', '/api/tasks'],
    ['GET', '/api/tasks/t1'],
    ['POST', '/api/tasks'],
    ['PUT', '/api/tasks/t1'],
    ['DELETE', '/api/tasks/t1'],
    ['POST', '/api/tasks/t1/comments'],
    ['GET', '/api/projects'],
    ['GET', '/api/users'],
  ])('%s %s responde 401 sin tocar ningun repositorio', async (metodo, ruta) => {
    const res = await peticion(api.url, metodo, ruta, { cuerpo: metodo === 'GET' || metodo === 'DELETE' ? undefined : {} });

    expect(res.status).toBe(401);
    expect(tareas.findById).not.toHaveBeenCalled();
    expect(tareas.findMany).not.toHaveBeenCalled();
    expect(proyectos.findById).not.toHaveBeenCalled();
    expect(proyectos.findManyForUser).not.toHaveBeenCalled();
  });
});
