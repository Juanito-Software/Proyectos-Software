import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { tasksService } from './tasks.service.js';
import { tasksRepository } from './tasks.repository.js';

/**
 * Las reglas de negocio de las tareas, sin base de datos.
 *
 * Lo que se prueba aquí es la **traducción de errores de PostgreSQL a
 * respuestas HTTP**, que es la parte imposible de forzar de forma fiable
 * contra la base de datos real: el 23505 solo salta si dos peticiones colisionan
 * de verdad, y el 23503 solo si se borra un usuario en el instante justo. Con el
 * repositorio simulado se lanzan a voluntad.
 *
 * Y son las dos traducciones que separan un 409 y un 401 comprensibles de un
 * 500 con el mensaje de PostgreSQL dentro.
 */

const USER = 'user-1';

const TAREA = {
  id: 'task-1',
  title: 'Comprar pan',
  description: 'En la panadería',
  status: 'pending' as const,
  priority: 'high' as const,
  userId: USER,
  createdAt: '2026-01-01T00:00:00.000Z',
  updatedAt: '2026-01-01T00:00:00.000Z',
};

/** Error de PostgreSQL con el código que se quiera. */
const errorPg = (code: string, mensaje = 'error de base de datos') =>
  Object.assign(new Error(mensaje), { code });

let espias: Record<string, ReturnType<typeof vi.spyOn>>;

beforeEach(() => {
  espias = {
    findById: vi.spyOn(tasksRepository, 'findById').mockResolvedValue(TAREA),
    findByTitle: vi.spyOn(tasksRepository, 'findByTitleForUser').mockResolvedValue(null),
    create: vi.spyOn(tasksRepository, 'create').mockResolvedValue(TAREA),
    update: vi.spyOn(tasksRepository, 'update').mockResolvedValue(TAREA),
    delete: vi.spyOn(tasksRepository, 'delete').mockResolvedValue(true),
    findAll: vi.spyOn(tasksRepository, 'findAllByUser').mockResolvedValue([TAREA]),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('traducción de errores de PostgreSQL', () => {
  it('el 23505 al crear se convierte en 409, no en 500', async () => {
    // Salta cuando dos peticiones simultáneas pasan las dos la comprobación
    // previa y chocan en el índice único. Sin traducirlo, la segunda recibiría
    // un 500 cuando lo correcto es el mismo 409 que cualquier otro duplicado.
    espias.create.mockRejectedValue(errorPg('23505', 'duplicate key value'));

    await expect(tasksService.create({ title: 'Comprar pan' }, USER)).rejects.toMatchObject({
      statusCode: 409,
    });
  });

  it('el mensaje del 409 es el mismo que el de la comprobación previa', async () => {
    // Dos caminos distintos, misma experiencia: al usuario le da igual si su
    // duplicado lo detectó el SELECT o el índice.
    const mensajeDelRechazo = async (): Promise<string> => {
      try {
        await tasksService.create({ title: 'Comprar pan' }, USER);
        throw new Error('se esperaba un rechazo y no lo hubo');
      } catch (err) {
        return (err as Error).message;
      }
    };

    espias.findByTitle.mockResolvedValue(TAREA);
    const porComprobacion = await mensajeDelRechazo();

    espias.findByTitle.mockResolvedValue(null);
    espias.create.mockRejectedValue(errorPg('23505'));
    const porIndice = await mensajeDelRechazo();

    expect(porComprobacion).toBe(porIndice);
  });

  it('el 23503 al crear se convierte en 401: la cuenta ya no existe', async () => {
    // Solo puede significar que el usuario se borró con la sesión abierta y su
    // token de acceso sigue vivo. Antes reventaba con un 500.
    espias.create.mockRejectedValue(errorPg('23503', 'violates foreign key constraint'));

    await expect(tasksService.create({ title: 'x' }, USER)).rejects.toMatchObject({
      statusCode: 401,
    });
  });

  it('el 23505 al actualizar también da 409', async () => {
    espias.update.mockRejectedValue(errorPg('23505'));

    await expect(
      tasksService.update('task-1', USER, { title: 'Otro título' }),
    ).rejects.toMatchObject({ statusCode: 409 });
  });

  it('cualquier otro error de base de datos se propaga sin disfrazar', async () => {
    // Traducir lo que no se entiende sería peor: un 409 falso escondería el
    // fallo real y nadie lo miraría.
    espias.create.mockRejectedValue(errorPg('42P01', 'relation "tasks" does not exist'));

    await expect(tasksService.create({ title: 'x' }, USER)).rejects.toThrow(/does not exist/);
  });

  it('un error sin código tampoco se traduce', async () => {
    espias.create.mockRejectedValue(new Error('la red se cayó'));

    await expect(tasksService.create({ title: 'x' }, USER)).rejects.toThrow('la red se cayó');
  });
});

describe('título duplicado', () => {
  it('rechaza con 409 antes de intentar escribir', async () => {
    espias.findByTitle.mockResolvedValue(TAREA);

    await expect(tasksService.create({ title: 'Comprar pan' }, USER)).rejects.toMatchObject({
      statusCode: 409,
    });
    expect(espias.create).not.toHaveBeenCalled();
  });

  it('la comprobación es por usuario, no global', async () => {
    await tasksService.create({ title: 'Comprar pan' }, USER);
    expect(espias.findByTitle).toHaveBeenCalledWith('Comprar pan', USER);
  });

  it('al editar sin cambiar el título no se comprueba el duplicado', async () => {
    // La tarea chocaría consigo misma. Se compara sin distinguir mayúsculas
    // porque el índice único también lo hace.
    await tasksService.update('task-1', USER, { title: 'COMPRAR PAN' });

    expect(espias.findByTitle).not.toHaveBeenCalled();
  });

  it('al editar cambiándolo sí, excluyéndose a sí misma', async () => {
    await tasksService.update('task-1', USER, { title: 'Comprar leche' });

    expect(espias.findByTitle).toHaveBeenCalledWith('Comprar leche', USER, 'task-1');
  });
});

describe('completed y status', () => {
  it('completed:true se traduce a status completed', async () => {
    await tasksService.update('task-1', USER, { completed: true });

    expect(espias.update).toHaveBeenCalledWith('task-1', USER, expect.objectContaining({ status: 'completed' }));
  });

  it('completed:false vuelve a pending', async () => {
    await tasksService.update('task-1', USER, { completed: false });

    expect(espias.update).toHaveBeenCalledWith('task-1', USER, expect.objectContaining({ status: 'pending' }));
  });

  it('si llegan los dos manda status, por ser más expresivo', async () => {
    await tasksService.update('task-1', USER, { status: 'in-progress', completed: true });

    expect(espias.update).toHaveBeenCalledWith(
      'task-1',
      USER,
      expect.objectContaining({ status: 'in-progress' }),
    );
  });

  it('la tarea que sale lleva completed calculado a partir de status', async () => {
    espias.findById.mockResolvedValue({ ...TAREA, status: 'completed' });

    await expect(tasksService.getById('task-1', USER)).resolves.toMatchObject({ completed: true });
  });

  it('in-progress no cuenta como completada', async () => {
    espias.findById.mockResolvedValue({ ...TAREA, status: 'in-progress' });

    await expect(tasksService.getById('task-1', USER)).resolves.toMatchObject({ completed: false });
  });
});

describe('valores por defecto y limpieza', () => {
  it('una tarea nueva nace pendiente y con prioridad media', async () => {
    await tasksService.create({ title: 'Sin más datos' }, USER);

    expect(espias.create).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'pending', priority: 'medium', description: '' }),
      USER,
    );
  });

  it('recorta los espacios del título y de la descripción', async () => {
    await tasksService.create({ title: '  Comprar pan  ', description: '  en la esquina  ' }, USER);

    expect(espias.create).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Comprar pan', description: 'en la esquina' }),
      USER,
    );
  });

  it('solo se envían al repositorio los campos que llegaron', async () => {
    // Mandar `description: undefined` la borraría en una actualización parcial.
    await tasksService.update('task-1', USER, { priority: 'low' });

    expect(espias.update).toHaveBeenCalledWith('task-1', USER, { priority: 'low' });
  });
});

describe('tarea inexistente o ajena', () => {
  it.each([
    ['leer', () => tasksService.getById('x', USER)],
    ['actualizar', () => tasksService.update('x', USER, { title: 'y' })],
  ])('%s una tarea que no existe da 404', async (_caso, accion) => {
    espias.findById.mockResolvedValue(null);

    await expect(accion()).rejects.toMatchObject({ statusCode: 404 });
  });

  it('borrar una que no existe da 404', async () => {
    espias.delete.mockResolvedValue(false);

    await expect(tasksService.remove('x', USER)).rejects.toMatchObject({ statusCode: 404 });
  });

  it('el identificador del usuario viaja SIEMPRE al repositorio', async () => {
    // Es lo que hace que una tarea ajena "no exista" para la consulta. Si
    // alguien dejara de pasarlo, el aislamiento entre usuarios se rompería.
    await tasksService.getById('task-1', USER);
    await tasksService.remove('task-1', USER);
    await tasksService.listForUser(USER);

    expect(espias.findById).toHaveBeenCalledWith('task-1', USER);
    expect(espias.delete).toHaveBeenCalledWith('task-1', USER);
    expect(espias.findAll).toHaveBeenCalledWith(USER, undefined);
  });
});

describe('el título duplicado al ACTUALIZAR', () => {
  /**
   * La comprobación previa del renombrado. Tiene dos detalles que la suite de
   * API no llegaba a distinguir: que la comparación **ignora mayúsculas** y que
   * se **excluye la propia tarea** de la búsqueda. Sin lo segundo, guardar una
   * tarea sin tocar el título daría 409 contra sí misma.
   */

  it('renombrar a un título que ya tiene otra tarea da 409', async () => {
    espias.findByTitle.mockResolvedValue({ ...TAREA, id: 'otra' });

    await expect(
      tasksService.update('task-1', USER, { title: 'Comprar leche' }),
    ).rejects.toMatchObject({ statusCode: 409 });
  });

  it('excluye la propia tarea de la búsqueda', async () => {
    // El tercer argumento es el id a ignorar. Si no se pasara, cualquier
    // guardado sin cambio de título chocaría consigo mismo.
    await tasksService.update('task-1', USER, { title: 'Comprar leche' });

    expect(espias.findByTitle).toHaveBeenCalledWith('Comprar leche', USER, 'task-1');
  });

  it('reescribir el MISMO título con otras mayúsculas no consulta siquiera', async () => {
    // 'comprar PAN' es el mismo título que 'Comprar pan': no hay renombrado que
    // validar y la consulta se ahorra.
    await tasksService.update('task-1', USER, { title: 'comprar PAN' });

    expect(espias.findByTitle).not.toHaveBeenCalled();
  });

  it('el 23505 en la actualización también acaba en 409', async () => {
    // La carrera: dos renombrados simultáneos pasan los dos la comprobación
    // previa y el índice único para al segundo.
    espias.update.mockRejectedValue(errorPg('23505', 'duplicate key value'));

    await expect(
      tasksService.update('task-1', USER, { title: 'Comprar leche' }),
    ).rejects.toMatchObject({ statusCode: 409 });
  });

  it('un error de PostgreSQL que no sea 23505 no se disfraza de 409', async () => {
    espias.update.mockRejectedValue(errorPg('42601', 'syntax error'));

    await expect(
      tasksService.update('task-1', USER, { title: 'x' }),
    ).rejects.toThrow('syntax error');
  });

  it('si la actualización no devuelve fila, es 500 y no un 200 con nada dentro', async () => {
    // No debería ocurrir —la existencia ya se comprobó—, pero devolver
    // `undefined` como si fuera la tarea sería peor que fallar.
    espias.update.mockResolvedValue(null);

    await expect(
      tasksService.update('task-1', USER, { title: 'x' }),
    ).rejects.toMatchObject({ statusCode: 500 });
  });

  it('actualizar una tarea que no existe da 404 antes de tocar nada', async () => {
    espias.findById.mockResolvedValue(null);

    await expect(tasksService.update('fantasma', USER, { title: 'x' })).rejects.toMatchObject({
      statusCode: 404,
    });
    expect(espias.update).not.toHaveBeenCalled();
  });

  it('solo se mandan al repositorio los campos enviados', async () => {
    // Un PATCH que solo trae prioridad no debe reescribir el título ni la
    // descripción con undefined.
    await tasksService.update('task-1', USER, { priority: 'low' });

    expect(espias.update).toHaveBeenCalledWith('task-1', USER, { priority: 'low' });
  });

  it('el título y la descripción se guardan recortados', async () => {
    await tasksService.update('task-1', USER, { title: '  Nuevo  ', description: '  algo  ' });

    expect(espias.update).toHaveBeenCalledWith('task-1', USER, {
      title: 'Nuevo',
      description: 'algo',
    });
  });
});
