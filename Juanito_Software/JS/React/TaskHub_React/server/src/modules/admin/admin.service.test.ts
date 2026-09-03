import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { adminService } from './admin.service.js';
import { usersRepository } from '../users/users.repository.js';
import * as db from '../../config/db.js';
import { ApiError } from '../../utils/api-error.js';

/**
 * Las dos salvaguardas del borrado de usuarios.
 *
 * Existen por lo mismo: que un clic no deje la aplicación sin nadie que pueda
 * administrarla. Hasta ahora solo las tocaba la suite de API, y allí cada una
 * se probaba con **un** caso; aquí se cubren los bordes, que es donde estas
 * reglas se rompen —el penúltimo administrador, el segundo de dos, el usuario
 * que no existe—.
 *
 * El repositorio se sustituye con espías: lo que se prueba es la **regla de
 * negocio**, no el SQL. El SQL lo ejercita `npm run verify` contra PostgreSQL
 * de verdad, y mezclar las dos cosas haría estos tests lentos sin añadir nada.
 */

const ADMIN = { id: 'admin-1', username: 'jefe', role: 'admin' as const };
const NORMAL = { id: 'user-1', username: 'juan', role: 'user' as const };

/** Fila completa tal y como la devuelve el repositorio. */
const fila = (u: typeof ADMIN | typeof NORMAL) => ({
  ...u,
  passwordHash: '$2b$12$hashquenoimporta',
  createdAt: '2026-01-01T00:00:00.000Z',
});

let espias: {
  findById: ReturnType<typeof vi.spyOn>;
  countByRole: ReturnType<typeof vi.spyOn>;
  deleteById: ReturnType<typeof vi.spyOn>;
};

beforeEach(() => {
  vi.spyOn(console, 'warn').mockImplementation(() => {});
  espias = {
    findById: vi.spyOn(usersRepository, 'findById').mockResolvedValue(null),
    countByRole: vi.spyOn(usersRepository, 'countByRole').mockResolvedValue(1),
    deleteById: vi.spyOn(usersRepository, 'deleteById').mockResolvedValue(true),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('un administrador no puede borrarse a sí mismo', () => {
  it('rechaza el borrado con 400', async () => {
    await expect(adminService.removeUser(ADMIN.id, ADMIN.id)).rejects.toMatchObject({
      statusCode: 400,
    });
  });

  it('ni siquiera llega a consultar la base de datos', async () => {
    // La comprobación va primero a propósito: es la más barata y la que más
    // veces se dispara por accidente.
    await adminService.removeUser(ADMIN.id, ADMIN.id).catch(() => {});

    expect(espias.findById).not.toHaveBeenCalled();
    expect(espias.deleteById).not.toHaveBeenCalled();
  });

  it('el mensaje explica el motivo', async () => {
    await expect(adminService.removeUser(ADMIN.id, ADMIN.id)).rejects.toThrow(/propia cuenta/i);
  });
});

describe('el último administrador no se puede borrar', () => {
  it('rechaza con 400 cuando solo queda uno', async () => {
    espias.findById.mockResolvedValue(fila(ADMIN));
    espias.countByRole.mockResolvedValue(1);

    await expect(adminService.removeUser(ADMIN.id, 'otro-admin')).rejects.toMatchObject({
      statusCode: 400,
    });
    expect(espias.deleteById).not.toHaveBeenCalled();
  });

  it('SÍ lo permite cuando quedan dos', async () => {
    // El borde que importa: con dos administradores, borrar uno deja la
    // aplicación administrable. La regla es "no quedarse sin ninguno", no
    // "no borrar administradores".
    espias.findById.mockResolvedValue(fila(ADMIN));
    espias.countByRole.mockResolvedValue(2);

    await expect(adminService.removeUser(ADMIN.id, 'otro-admin')).resolves.toMatchObject({
      id: ADMIN.id,
      username: 'jefe',
    });
    expect(espias.deleteById).toHaveBeenCalledWith(ADMIN.id);
  });

  it('cuenta administradores, no usuarios totales', async () => {
    // Si contara usuarios, una instancia con cien usuarios y un solo
    // administrador dejaría borrarlo.
    espias.findById.mockResolvedValue(fila(ADMIN));
    espias.countByRole.mockResolvedValue(1);

    await adminService.removeUser(ADMIN.id, 'otro-admin').catch(() => {});

    expect(espias.countByRole).toHaveBeenCalledWith('admin');
  });

  it('no cuenta administradores al borrar un usuario normal', async () => {
    // Sería una consulta de más en el caso habitual.
    espias.findById.mockResolvedValue(fila(NORMAL));

    await adminService.removeUser(NORMAL.id, ADMIN.id);

    expect(espias.countByRole).not.toHaveBeenCalled();
    expect(espias.deleteById).toHaveBeenCalledWith(NORMAL.id);
  });
});

describe('usuario inexistente', () => {
  it('responde 404 y no intenta borrar nada', async () => {
    espias.findById.mockResolvedValue(null);

    await expect(adminService.removeUser('no-existe', ADMIN.id)).rejects.toMatchObject({
      statusCode: 404,
    });
    expect(espias.deleteById).not.toHaveBeenCalled();
  });

  it('distingue el 404 del 400 de las salvaguardas', async () => {
    // Los tres caminos de rechazo tienen códigos distintos a propósito: quien
    // usa la API puede saber si el problema es la cuenta o la regla.
    espias.findById.mockResolvedValue(null);

    const capturar = async (objetivo: string, quien: string): Promise<ApiError> => {
      try {
        await adminService.removeUser(objetivo, quien);
        throw new Error('se esperaba un rechazo y no lo hubo');
      } catch (err) {
        return err as ApiError;
      }
    };

    expect((await capturar('x', ADMIN.id)).statusCode).toBe(404);
    expect((await capturar(ADMIN.id, ADMIN.id)).statusCode).toBe(400);
  });
});

describe('borrado correcto', () => {
  it('devuelve id y nombre del usuario borrado', async () => {
    espias.findById.mockResolvedValue(fila(NORMAL));

    await expect(adminService.removeUser(NORMAL.id, ADMIN.id)).resolves.toEqual({
      id: NORMAL.id,
      username: 'juan',
    });
  });

  it('deja rastro en el registro de seguridad', async () => {
    // Borrar una cuenta es de las operaciones que hay que poder reconstruir
    // después: quién la borró y cuándo.
    espias.findById.mockResolvedValue(fila(NORMAL));

    await adminService.removeUser(NORMAL.id, ADMIN.id);

    const linea = (console.warn as unknown as ReturnType<typeof vi.fn>).mock.calls[0][0];
    const registro = JSON.parse(String(linea));

    expect(registro.evento).toBe('cuenta.borrada');
    expect(registro.usuario).toBe('juan');
    expect(registro.borradaPor).toBe(ADMIN.id);
  });

  it('el registro no lleva el hash de la contraseña', async () => {
    espias.findById.mockResolvedValue(fila(NORMAL));

    await adminService.removeUser(NORMAL.id, ADMIN.id);

    const linea = String((console.warn as unknown as ReturnType<typeof vi.fn>).mock.calls[0][0]);
    expect(linea).not.toContain('$2b$');
  });
});

describe('listado de usuarios', () => {
  it('delega en el repositorio sin filtrar nada por su cuenta', async () => {
    const listado = [{ id: '1', username: 'a', role: 'user' as const, createdAt: 'x', taskCount: 3 }];
    const listAll = vi.spyOn(usersRepository, 'listAll').mockResolvedValue(listado);

    await expect(adminService.listUsers()).resolves.toEqual(listado);
    expect(listAll).toHaveBeenCalledTimes(1);
  });
});

describe('estadísticas globales', () => {
  /**
   * El único sitio del servicio que hace SQL directo en lugar de pasar por el
   * repositorio, y traduce `in_progress` (columna) a `inProgress` (JSON). Es un
   * renombrado a mano, exactamente el tipo de cosa que se rompe en silencio: el
   * panel mostraría un cero en lugar del número, sin error en ninguna parte.
   */

  const FILA = {
    users: 12,
    admins: 2,
    tasks: 47,
    pending: 30,
    in_progress: 9,
    completed: 8,
  };

  it('traduce in_progress a inProgress sin perder el valor', async () => {
    vi.spyOn(db, 'query').mockResolvedValue([FILA]);

    const stats = await adminService.globalStats();

    expect(stats.inProgress).toBe(9);
    expect(stats).not.toHaveProperty('in_progress');
  });

  it('devuelve los seis contadores con su valor', async () => {
    vi.spyOn(db, 'query').mockResolvedValue([FILA]);

    await expect(adminService.globalStats()).resolves.toEqual({
      users: 12,
      admins: 2,
      tasks: 47,
      pending: 30,
      inProgress: 9,
      completed: 8,
    });
  });

  it('una instancia recién creada devuelve ceros, no undefined', async () => {
    // Los COUNT(*) siempre devuelven fila, así que el caso vacío es una fila de
    // ceros. Si el servicio hiciera `rows[0] ?? {}` esto no lo detectaría.
    vi.spyOn(db, 'query').mockResolvedValue([
      { users: 0, admins: 0, tasks: 0, pending: 0, in_progress: 0, completed: 0 },
    ]);

    const stats = await adminService.globalStats();

    expect(Object.values(stats).every((v) => v === 0)).toBe(true);
  });

  it('un fallo de la base de datos se propaga tal cual', async () => {
    // No hay nada que traducir aquí: un error de conexión no es un caso de
    // negocio y debe llegar al manejador como 500.
    vi.spyOn(db, 'query').mockRejectedValue(new Error('conexión perdida'));

    await expect(adminService.globalStats()).rejects.toThrow('conexión perdida');
  });

  it('la consulta cuenta admins por rol, no por una lista fija', async () => {
    const query = vi.spyOn(db, 'query').mockResolvedValue([FILA]);

    await adminService.globalStats();

    expect(String(query.mock.calls[0][0])).toContain("role = 'admin'");
  });
});
