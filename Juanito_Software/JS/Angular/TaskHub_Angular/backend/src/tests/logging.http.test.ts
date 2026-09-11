import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from 'vitest';
import { Writable } from 'node:stream';

// Las lineas que escribe el logger se guardan aqui en vez de ir a la consola.
const escrito = vi.hoisted(() => ({ lineas: [] as string[] }));

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../services/auth.service', () => ({
  authService: { register: vi.fn(), login: vi.fn(), refresh: vi.fn(), logout: vi.fn() },
}));
// El logger de la aplicacion se sustituye por uno construido con la MISMA
// funcion que usa produccion (createLogger), con nivel `info` —el de
// produccion— y escribiendo en memoria. Si alguien quita la redaccion de
// config/logger.ts, este logger la pierde tambien.
vi.mock('../config/logger', async (importOriginal) => {
  const original = await importOriginal<typeof import('../config/logger')>();
  const destination = new Writable({
    write(chunk, _enc, done) {
      escrito.lineas.push(...chunk.toString().split('\n').filter(Boolean));
      done();
    },
  });
  return { ...original, logger: original.createLogger({ level: 'info', destination }) };
});

import { authService } from '../services/auth.service';
import { arrancar, peticion } from './http';

let api: Awaited<ReturnType<typeof arrancar>>;
beforeAll(async () => (api = await arrancar()));
afterAll(() => api.cerrar());
beforeEach(() => {
  escrito.lineas.length = 0;
  vi.mocked(authService.login).mockResolvedValue({
    user: { id: 'ana' },
    accessToken: 'TOKEN-DE-ACCESO-SECRETO',
    refreshToken: 'REFRESH-TOKEN-SECRETO',
  } as never);
});

/** Espera a que pino-http escriba la linea de la peticion, que va tras la respuesta. */
async function lineaDe(url: string) {
  for (let i = 0; i < 50; i++) {
    const linea = escrito.lineas.find((l) => l.includes(`"url":"${url}"`));
    if (linea) return linea;
    await new Promise((r) => setTimeout(r, 10));
  }
  throw new Error(`No se ha registrado ninguna linea para ${url}: el logger de la app no es el de config/logger.ts`);
}

/**
 * Lo que queda en el log de cada peticion.
 *
 * Antes de este fichero, pino-http escribia las cabeceras completas con nivel
 * `info`, el de produccion: tokens de acceso, cookies y el refresh token recien
 * emitido, en texto plano. Se comprobo arrancando la app con
 * NODE_ENV=production y leyendo la salida.
 *
 * Los tests leen la linea JSON real que se escribiria, no la configuracion.
 */
describe('el log de peticiones no guarda credenciales', () => {
  it('ni el token de acceso ni la cookie de sesion que llegan en la peticion', async () => {
    await peticion(api.url, 'GET', '/health', {
      cabeceras: { Authorization: 'Bearer TOKEN-QUE-LLEGA', Cookie: 'refreshToken=COOKIE-QUE-LLEGA' },
    });

    const linea = await lineaDe('/health');
    expect(linea).not.toContain('TOKEN-QUE-LLEGA');
    expect(linea).not.toContain('COOKIE-QUE-LLEGA');
    const { req } = JSON.parse(linea);
    expect(req.headers.authorization).toBe('[REDACTED]');
    expect(req.headers.cookie).toBe('[REDACTED]');
  });

  it('ni el refresh token que la API emite en set-cookie', async () => {
    const res = await peticion(api.url, 'POST', '/api/auth/login', { cuerpo: { email: 'ana@test.com', password: 'x' } });
    // Control: la cookie SI sale hacia el cliente. Tapar el log no debe tapar la respuesta.
    expect(res.headers.getSetCookie().join()).toContain('REFRESH-TOKEN-SECRETO');

    const linea = await lineaDe('/api/auth/login');
    expect(linea).not.toContain('REFRESH-TOKEN-SECRETO');
    expect(JSON.parse(linea).res.headers['set-cookie']).toBe('[REDACTED]');
  });

  it('y la linea sigue sirviendo para depurar: metodo, ruta y estado', async () => {
    // Tapar de mas tambien es un fallo: un log sin ruta ni estado no ayuda a
    // nadie a entender una incidencia.
    await peticion(api.url, 'GET', '/health', { cabeceras: { Authorization: 'Bearer X' } });

    const { req, res, level } = JSON.parse(await lineaDe('/health'));
    expect(level).toBe(30); // info
    expect(req.method).toBe('GET');
    expect(req.headers['user-agent']).toBeDefined();
    expect(res.statusCode).toBe(200);
  });
});
