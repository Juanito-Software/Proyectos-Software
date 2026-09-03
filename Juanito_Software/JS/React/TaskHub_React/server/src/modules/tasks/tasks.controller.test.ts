import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
import { tasksController } from './tasks.controller.js';
import { tasksService } from './tasks.service.js';
import { adminController } from '../admin/admin.controller.js';
import { adminService } from '../admin/admin.service.js';
import { ApiError } from '../../utils/api-error.js';

/**
 * Los controladores de tareas y administración.
 *
 * Son delgados a propósito —leen la petición, llaman al servicio y envuelven la
 * respuesta—, pero concentran dos cosas que sí conviene fijar:
 *
 * 1. **De dónde sale el identificador del usuario.** Siempre de `req.userId`,
 *    que puso el middleware a partir del token, nunca del cuerpo ni de la
 *    URL. Es lo que impide que alguien pida las tareas de otro cambiando un
 *    parámetro.
 * 2. **Que los fallos van a `next()`.** En Express 4 una promesa rechazada no
 *    llega sola al manejador de errores: sin el try/catch, un fallo dejaría la
 *    petición colgada hasta que el cliente se cansara.
 */

const TAREA = {
  id: 'task-1',
  title: 'Comprar pan',
  description: 'En la panadería',
  status: 'pending' as const,
  priority: 'high' as const,
  userId: 'user-1',
  createdAt: '2026-01-01T00:00:00.000Z',
  updatedAt: '2026-01-01T00:00:00.000Z',
  completed: false,
};
const USER = 'user-1';

function respuestaFalsa() {
  const capturado = { status: 200, cuerpo: null as unknown };
  const res = {
    status(c: number) {
      capturado.status = c;
      return this;
    },
    json(b: unknown) {
      capturado.cuerpo = b;
      return this;
    },
  } as unknown as Response;
  return { res, capturado };
}

const peticion = (extra: Partial<Request> = {}) =>
  ({ userId: USER, params: {}, query: {}, body: {}, ...extra }) as unknown as Request;

async function ejecutar(
  metodo: (r: Request, s: Response, n: NextFunction) => Promise<void>,
  req: Request = peticion(),
) {
  const { res, capturado } = respuestaFalsa();
  let error: unknown;
  await metodo(req, res, ((err?: unknown) => {
    error = err;
  }) as NextFunction);
  return { capturado, error };
}

let espias: Record<string, ReturnType<typeof vi.spyOn>>;

beforeEach(() => {
  espias = {
    listForUser: vi.spyOn(tasksService, 'listForUser').mockResolvedValue([TAREA]),
    getById: vi.spyOn(tasksService, 'getById').mockResolvedValue(TAREA),
    create: vi.spyOn(tasksService, 'create').mockResolvedValue(TAREA),
    update: vi.spyOn(tasksService, 'update').mockResolvedValue(TAREA),
    remove: vi.spyOn(tasksService, 'remove').mockResolvedValue(undefined),
    statsForUser: vi.spyOn(tasksService, 'statsForUser').mockResolvedValue({
      total: 1,
      pending: 1,
      inProgress: 0,
      completed: 0,
    }),
    listUsers: vi.spyOn(adminService, 'listUsers').mockResolvedValue([]),
    removeUser: vi.spyOn(adminService, 'removeUser').mockResolvedValue({ id: 'u', username: 'x' }),
    globalStats: vi.spyOn(adminService, 'globalStats').mockResolvedValue({
      users: 2,
      admins: 1,
      tasks: 5,
      pending: 3,
      inProgress: 1,
      completed: 1,
    }),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('el usuario sale SIEMPRE del token', () => {
  it.each([
    ['list', () => ejecutar(tasksController.list), 'listForUser'],
    ['stats', () => ejecutar(tasksController.stats), 'statsForUser'],
  ])('%s pasa req.userId al servicio', async (_caso, accion, metodo) => {
    await accion();
    expect(espias[metodo].mock.calls[0][0]).toBe(USER);
  });

  it('ignora un userId puesto a mano en el cuerpo', async () => {
    // El intento evidente de leer las tareas de otro. El controlador nunca mira
    // el cuerpo para esto.
    await ejecutar(tasksController.list, peticion({ body: { userId: 'victima' } }));

    expect(espias.listForUser).toHaveBeenCalledWith(USER, expect.anything());
  });

  it('ignora también un userId en la cadena de consulta', async () => {
    await ejecutar(tasksController.list, peticion({ query: { userId: 'victima' } }));

    expect(espias.listForUser.mock.calls[0][0]).toBe(USER);
  });

  it('getById, update y remove lo pasan igual', async () => {
    const req = peticion({ params: { id: 'task-1' }, body: { title: 'x' } });

    await ejecutar(tasksController.getById, req);
    await ejecutar(tasksController.update, req);
    await ejecutar(tasksController.remove, req);

    expect(espias.getById).toHaveBeenCalledWith('task-1', USER);
    expect(espias.update).toHaveBeenCalledWith('task-1', USER, { title: 'x' });
    expect(espias.remove).toHaveBeenCalledWith('task-1', USER);
  });
});

describe('lectura de filtros', () => {
  it('traslada los tres cuando son válidos', async () => {
    await ejecutar(
      tasksController.list,
      peticion({ query: { status: 'pending', priority: 'high', search: 'pan' } }),
    );

    expect(espias.listForUser).toHaveBeenCalledWith(USER, {
      status: 'pending',
      priority: 'high',
      search: 'pan',
    });
  });

  it('descarta los valores que no son del catálogo', async () => {
    // El validador ya los habría rechazado con un 400; esto es la segunda
    // barrera, para que un valor inventado nunca llegue a la consulta.
    await ejecutar(
      tasksController.list,
      peticion({ query: { status: 'inventado', priority: 'altísima' } }),
    );

    expect(espias.listForUser).toHaveBeenCalledWith(USER, {});
  });

  it('recorta la búsqueda y descarta la que solo tiene espacios', async () => {
    await ejecutar(tasksController.list, peticion({ query: { search: '  pan  ' } }));
    expect(espias.listForUser).toHaveBeenCalledWith(USER, { search: 'pan' });

    espias.listForUser.mockClear();
    await ejecutar(tasksController.list, peticion({ query: { search: '   ' } }));
    expect(espias.listForUser).toHaveBeenCalledWith(USER, {});
  });
});

describe('códigos de estado', () => {
  it('crear responde 201', async () => {
    const { capturado } = await ejecutar(tasksController.create);
    expect(capturado.status).toBe(201);
  });

  it.each([
    ['list', tasksController.list],
    ['getById', tasksController.getById],
    ['update', tasksController.update],
    ['remove', tasksController.remove],
    ['stats', tasksController.stats],
  ])('%s responde 200', async (_caso, metodo) => {
    const { capturado } = await ejecutar(metodo, peticion({ params: { id: 'task-1' } }));
    expect(capturado.status).toBe(200);
  });

  it('el borrado devuelve el id de lo borrado', async () => {
    const { capturado } = await ejecutar(tasksController.remove, peticion({ params: { id: 'task-9' } }));

    expect(capturado.cuerpo).toMatchObject({ data: { id: 'task-9' } });
  });
});

describe('propagación de errores', () => {
  it.each([
    ['list', 'listForUser', tasksController.list],
    ['getById', 'getById', tasksController.getById],
    ['create', 'create', tasksController.create],
    ['update', 'update', tasksController.update],
    ['remove', 'remove', tasksController.remove],
    ['stats', 'statsForUser', tasksController.stats],
  ])('%s manda el fallo a next(), no lo deja colgado', async (_caso, servicio, metodo) => {
    espias[servicio].mockRejectedValue(ApiError.notFound('Tarea no encontrada'));

    const { error, capturado } = await ejecutar(metodo, peticion({ params: { id: 'x' } }));

    expect((error as ApiError).statusCode).toBe(404);
    expect(capturado.cuerpo).toBeNull();
  });
});

describe('controlador de administración', () => {
  it('el borrado pasa el objetivo y QUIÉN lo pide', async () => {
    // El segundo argumento es lo que permite la salvaguarda de "no puedes
    // borrarte a ti mismo", y sale del token.
    await ejecutar(
      adminController.removeUser,
      peticion({ params: { id: 'objetivo' }, userId: 'admin-1' }),
    );

    expect(espias.removeUser).toHaveBeenCalledWith('objetivo', 'admin-1');
  });

  it('el listado y las estadísticas responden 200 con sus datos', async () => {
    const listado = await ejecutar(adminController.listUsers);
    const stats = await ejecutar(adminController.stats);

    expect(listado.capturado.status).toBe(200);
    expect(stats.capturado.cuerpo).toMatchObject({ data: { users: 2, admins: 1 } });
  });

  it.each([
    ['listUsers', 'listUsers', adminController.listUsers],
    ['removeUser', 'removeUser', adminController.removeUser],
    ['stats', 'globalStats', adminController.stats],
  ])('%s también propaga los fallos', async (_caso, servicio, metodo) => {
    espias[servicio].mockRejectedValue(ApiError.badRequest('no puedes'));

    const { error } = await ejecutar(metodo, peticion({ params: { id: 'x' } }));

    expect((error as ApiError).statusCode).toBe(400);
  });
});
