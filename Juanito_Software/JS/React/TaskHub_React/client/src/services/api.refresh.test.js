import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { getTasks, setAuthToken, configurarAuth } from './api';

/**
 * Renovación transparente ante un 401.
 *
 * Con tokens de acceso de quince minutos, encontrarse un 401 pasa a ser lo
 * normal y no una excepción: si cada uno echara al usuario al formulario, la
 * sesión se sentiría más corta que antes en lugar de más segura. Lo que se
 * comprueba aquí es que la renovación ocurre sola, que se reintenta una sola
 * vez, y que varias peticiones simultáneas comparten una única renovación.
 *
 * Ese último punto no es un detalle: si cada petición renovara por su cuenta,
 * todas irían con la misma cookie y el servidor tomaría las repetidas por
 * reutilización del token, revocando la sesión entera. La aplicación se
 * cerraría sola al cargar la pantalla.
 */

const sobre = (data) => ({ success: true, data, timestamp: '2026-01-01T00:00:00.000Z' });

/** Respuesta simulada de `fetch`. */
const respuesta = (status, body) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => body,
});

beforeEach(() => {
  setAuthToken('token-caducado');
  configurarAuth({});
});

afterEach(() => {
  configurarAuth({});
  vi.restoreAllMocks();
});

describe('renovación ante un 401', () => {
  it('renueva y repite la petición, que acaba funcionando', async () => {
    global.fetch = vi
      .fn()
      // La petición original se encuentra el token caducado.
      .mockResolvedValueOnce(respuesta(401, { success: false, error: 'Token inválido' }))
      // La renovación entrega credenciales nuevas.
      .mockResolvedValueOnce(respuesta(200, sobre({ accessToken: 'token-nuevo', user: { id: '1' } })))
      // Y el reintento ya pasa.
      .mockResolvedValueOnce(respuesta(200, sobre([{ id: 't1', title: 'Comprar pan' }])));

    const tareas = await getTasks();

    expect(tareas).toHaveLength(1);
    expect(global.fetch).toHaveBeenCalledTimes(3);
    expect(global.fetch.mock.calls[1][0]).toBe('/api/auth/refresh');
  });

  it('el reintento va con el token nuevo, no con el caducado', async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValueOnce(respuesta(401, { success: false }))
      .mockResolvedValueOnce(respuesta(200, sobre({ accessToken: 'token-nuevo' })))
      .mockResolvedValueOnce(respuesta(200, sobre([])));

    await getTasks();

    const cabeceraOriginal = global.fetch.mock.calls[0][1].headers.Authorization;
    const cabeceraReintento = global.fetch.mock.calls[2][1].headers.Authorization;

    expect(cabeceraOriginal).toBe('Bearer token-caducado');
    expect(cabeceraReintento).toBe('Bearer token-nuevo');
  });

  it('avisa al contexto de las credenciales nuevas', async () => {
    // Sin este aviso, React seguiría guardando el token viejo y lo escribiría
    // de vuelta en localStorage en el siguiente render.
    const alRenovar = vi.fn();
    configurarAuth({ alRenovar });

    global.fetch = vi
      .fn()
      .mockResolvedValueOnce(respuesta(401, { success: false }))
      .mockResolvedValueOnce(respuesta(200, sobre({ accessToken: 'token-nuevo', user: { id: '1' } })))
      .mockResolvedValueOnce(respuesta(200, sobre([])));

    await getTasks();

    expect(alRenovar).toHaveBeenCalledWith(
      expect.objectContaining({ accessToken: 'token-nuevo' }),
    );
  });

  it('no reintenta indefinidamente: un segundo 401 se rinde', async () => {
    // Si el servidor devolviera 401 por un motivo que la renovación no arregla,
    // reintentar sin tope dejaría el cliente dando vueltas para siempre.
    global.fetch = vi
      .fn()
      .mockResolvedValueOnce(respuesta(401, { success: false }))
      .mockResolvedValueOnce(respuesta(200, sobre({ accessToken: 'token-nuevo' })))
      .mockResolvedValueOnce(respuesta(401, { success: false }));

    await expect(getTasks()).rejects.toThrow('Sesión expirada');
    expect(global.fetch).toHaveBeenCalledTimes(3);
  });

  it('si la renovación falla, la sesión se da por perdida', async () => {
    const alPerderSesion = vi.fn();
    configurarAuth({ alPerderSesion });

    global.fetch = vi
      .fn()
      .mockResolvedValueOnce(respuesta(401, { success: false }))
      .mockResolvedValueOnce(respuesta(401, { success: false, error: 'Sesión inválida o expirada' }));

    await expect(getTasks()).rejects.toThrow('Sesión expirada');
    expect(alPerderSesion).toHaveBeenCalledTimes(1);
    // No se reintenta la original: no habría con qué.
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('no intenta renovar cuando la petición va bien', async () => {
    global.fetch = vi.fn().mockResolvedValue(respuesta(200, sobre([])));

    await getTasks();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch.mock.calls[0][0]).not.toContain('refresh');
  });

  it('un error que no es 401 no dispara la renovación', async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValue(respuesta(500, { success: false, error: 'Error del servidor' }));

    await expect(getTasks()).rejects.toThrow('Error del servidor');
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});

describe('renovaciones simultáneas', () => {
  /**
   * Servidor simulado.
   *
   * Devuelve 401 a las `caducadas` primeras peticiones de datos, cuenta cuántas
   * veces se llama a la renovación y responde bien a partir de ahí. Tenerlo en
   * un solo sitio evita el enredo de encadenar `mockResolvedValueOnce`.
   */
  function servidorSimulado({ caducadas }) {
    const estado = { renovaciones: 0, pendientes: caducadas };

    global.fetch = vi.fn(async (url) => {
      if (url === '/api/auth/refresh') {
        estado.renovaciones += 1;
        // Un tick de espera para que las peticiones en paralelo coincidan de
        // verdad sobre la misma renovación en curso.
        await new Promise((r) => setTimeout(r, 5));
        return respuesta(200, sobre({ accessToken: `token-${estado.renovaciones}` }));
      }

      if (estado.pendientes > 0) {
        estado.pendientes -= 1;
        return respuesta(401, { success: false });
      }
      return respuesta(200, sobre([]));
    });

    return estado;
  }

  it('tres peticiones que caducan a la vez comparten UNA sola renovación', async () => {
    // El caso que importa. Con una renovación por petición, las dos últimas
    // irían con un token de refresco ya rotado, el servidor lo tomaría por
    // reutilización y revocaría la sesión: la aplicación se cerraría sola al
    // cargar la pantalla.
    const estado = servidorSimulado({ caducadas: 3 });

    await Promise.all([getTasks(), getTasks(), getTasks()]);

    expect(estado.renovaciones).toBe(1);
  });

  it('tras terminar una renovación, una caducidad posterior vuelve a renovar', async () => {
    // La promesa compartida tiene que limpiarse al acabar. Si se quedara
    // guardada, una caducidad más tarde reutilizaría el resultado viejo y el
    // cliente no renovaría nunca más.
    const estado = servidorSimulado({ caducadas: 1 });
    await getTasks();
    expect(estado.renovaciones).toBe(1);

    // Segunda tanda, sobre el mismo módulo ya usado.
    const segundo = servidorSimulado({ caducadas: 1 });
    await getTasks();
    expect(segundo.renovaciones).toBe(1);
  });
});
