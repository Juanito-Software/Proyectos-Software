import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  toggleCompleted,
  setAuthToken,
} from './api';

/**
 * La capa de servicios es la frontera entre el cliente y la API. Aquí se
 * comprueban tres cosas que, si se rompen, rompen toda la aplicación sin dar
 * un error claro: que se abre el envoltorio de respuesta, que los filtros
 * viajan como parámetros de consulta, y que los errores se propagan con el
 * mensaje del servidor y no con uno genérico.
 */

function mockFetch(status, body) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
}

const sobre = (data) => ({ success: true, data, timestamp: '2026-01-01T00:00:00.000Z' });

beforeEach(() => {
  setAuthToken('token-de-prueba');
});

describe('request: envoltorio de respuesta', () => {
  it('devuelve data directamente, sin el envoltorio', async () => {
    const tarea = { id: '1', title: 'Comprar pan', completed: false };
    global.fetch = mockFetch(200, sobre(tarea));

    const resultado = await getTask('1');

    // Lo importante: el componente recibe la tarea, no { success, data }.
    expect(resultado).toEqual(tarea);
    expect(resultado.success).toBeUndefined();
  });

  it('devuelve un array cuando la API lista tareas', async () => {
    global.fetch = mockFetch(200, sobre([{ id: '1' }, { id: '2' }]));
    const tareas = await getTasks();
    expect(Array.isArray(tareas)).toBe(true);
    expect(tareas).toHaveLength(2);
  });
});

describe('getTasks: filtros como parámetros de consulta', () => {
  it('no añade parámetros cuando no hay filtros', async () => {
    global.fetch = mockFetch(200, sobre([]));
    await getTasks();
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks', expect.any(Object));
  });

  it('omite los filtros vacíos en lugar de mandarlos en blanco', async () => {
    global.fetch = mockFetch(200, sobre([]));
    await getTasks({ status: '', priority: '', search: '' });
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks', expect.any(Object));
  });

  it('manda status, priority y search cuando tienen valor', async () => {
    global.fetch = mockFetch(200, sobre([]));
    await getTasks({ status: 'pending', priority: 'high', search: 'pan' });

    const url = global.fetch.mock.calls[0][0];
    expect(url).toContain('status=pending');
    expect(url).toContain('priority=high');
    expect(url).toContain('search=pan');
  });

  it('codifica los caracteres especiales de la búsqueda', async () => {
    global.fetch = mockFetch(200, sobre([]));
    await getTasks({ search: '50% & más' });

    const url = global.fetch.mock.calls[0][0];
    // Sin codificar, el & partiría la cadena de consulta en dos parámetros.
    expect(url).not.toContain('50% & más');
    expect(url).toContain('search=');
  });
});

describe('propagación de errores', () => {
  it('lanza el mensaje que devuelve la API, no uno genérico', async () => {
    global.fetch = mockFetch(409, { success: false, error: 'Ya tienes una tarea con este título' });
    await expect(createTask({ title: 'Repetida' })).rejects.toThrow(
      'Ya tienes una tarea con este título',
    );
  });

  it('convierte un 401 en "Sesión expirada" para que el cliente cierre sesión', async () => {
    global.fetch = mockFetch(401, { success: false, error: 'Token inválido o expirado' });
    await expect(getTasks()).rejects.toThrow('Sesión expirada');
  });

  it('usa un mensaje por defecto si la API no manda ninguno', async () => {
    global.fetch = mockFetch(500, { success: false });
    await expect(getTasks()).rejects.toThrow('Error al cargar tareas');
  });

  it('no se rompe si la respuesta no es JSON válido', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error('Unexpected token < in JSON');
      },
    });
    // Un 502 del proxy devuelve HTML: debe salir un error controlado y no el
    // fallo del parser.
    await expect(getTasks()).rejects.toThrow('Error al cargar tareas');
  });
});

describe('cabecera de autorización', () => {
  it('incluye el token cuando está establecido', async () => {
    global.fetch = mockFetch(200, sobre([]));
    await getTasks();

    const { headers } = global.fetch.mock.calls[0][1];
    expect(headers.Authorization).toBe('Bearer token-de-prueba');
  });

  it('no incluye la cabecera si no hay token', async () => {
    setAuthToken(null);
    global.fetch = mockFetch(200, sobre([]));
    await getTasks();

    const { headers } = global.fetch.mock.calls[0][1];
    expect(headers.Authorization).toBeUndefined();
  });
});

describe('verbos y rutas', () => {
  it('createTask hace POST a /api/tasks', async () => {
    global.fetch = mockFetch(201, sobre({ id: '1' }));
    await createTask({ title: 'Nueva' });

    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/tasks');
    expect(options.method).toBe('POST');
    expect(JSON.parse(options.body)).toEqual({ title: 'Nueva' });
  });

  it('updateTask hace PATCH al id concreto', async () => {
    global.fetch = mockFetch(200, sobre({ id: 'abc' }));
    await updateTask('abc', { title: 'Cambiada' });

    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/tasks/abc');
    expect(options.method).toBe('PATCH');
  });

  it('deleteTask hace DELETE al id concreto', async () => {
    global.fetch = mockFetch(200, sobre({ id: 'abc' }));
    await deleteTask('abc');

    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/tasks/abc');
    expect(options.method).toBe('DELETE');
  });

  it('toggleCompleted manda completed, que el servidor traduce a status', async () => {
    global.fetch = mockFetch(200, sobre({ id: 'abc', completed: true, status: 'completed' }));
    await toggleCompleted('abc', true);

    const options = global.fetch.mock.calls[0][1];
    expect(JSON.parse(options.body)).toEqual({ completed: true });
  });
});
