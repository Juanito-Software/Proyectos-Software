import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from 'vitest';

vi.mock('../config/prisma', () => ({ prisma: {} }));
vi.mock('@prisma/client', () => ({
  PrismaClient: class {},
  TaskStatus: { TODO: 'TODO', IN_PROGRESS: 'IN_PROGRESS', IN_REVIEW: 'IN_REVIEW', DONE: 'DONE' },
  TaskPriority: { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', URGENT: 'URGENT' },
  Role: { ADMIN: 'ADMIN', MANAGER: 'MANAGER', MEMBER: 'MEMBER' },
}));
vi.mock('../repositories/project.repository', () => ({
  projectRepository: { create: vi.fn(), findManyForUser: vi.fn(), findById: vi.fn() },
}));

import { projectRepository } from '../repositories/project.repository';
import { arrancar, peticion, tokenDe } from './http';

const proyectos = vi.mocked(projectRepository);

let api: Awaited<ReturnType<typeof arrancar>>;
beforeAll(async () => (api = await arrancar()));
afterAll(() => api.cerrar());
beforeEach(() => vi.clearAllMocks());

/**
 * Lo que devuelve la API cuando algo sale mal: `validate` y `errorHandler`.
 *
 * Dos propiedades que un cambio inocente puede romper sin que se note en uso
 * normal: que un dato malo NO llegue a la base de datos, y que un fallo interno
 * NO cuente hacia fuera lo que ha fallado.
 */
describe('validacion (Zod)', () => {
  it('un cuerpo invalido responde 400 con los errores POR CAMPO y no llega al repositorio', async () => {
    const res = await peticion(api.url, 'POST', '/api/projects', {
      token: tokenDe('ana'),
      cuerpo: { name: 'a', description: 'x'.repeat(1001) },
    });

    expect(res.status).toBe(400);
    const cuerpo = await res.json();
    expect(cuerpo.message).toBe('Error de validación');
    // Antes de este test la respuesta era { body: [dos mensajes] }: `flatten()`
    // agrupaba por el envoltorio { body, query, params } de `validate` y el
    // nombre del campo se perdia. El registro del frontend lee `errors` como un
    // objeto por campo.
    expect(Object.keys(cuerpo.errors).sort()).toEqual(['description', 'name']);
    expect(cuerpo.errors.name).toEqual(['El nombre debe tener al menos 2 caracteres']);
    expect(proyectos.create).not.toHaveBeenCalled();
  });

  it('el nombre se guarda recortado: el cuerpo que llega es el ya validado', async () => {
    proyectos.create.mockResolvedValue({ id: 'p1', name: 'Informe', members: [] } as never);

    // `validate` sustituye req.body por el resultado de Zod, que aplica el
    // `.trim()` del esquema. Si dejara el cuerpo original, el trim del
    // validador solo serviria para decidir, no para guardar.
    await peticion(api.url, 'POST', '/api/projects', { token: tokenDe('ana'), cuerpo: { name: '   Informe   ' } });

    expect((proyectos.create.mock.calls[0][0] as { name: string }).name).toBe('Informe');
  });

  it('un JSON mal formado es un 400 del cliente, no un 500 del servidor', async () => {
    // `peticion` serializa el cuerpo; un JSON roto hay que mandarlo a mano.
    const malFormado = await fetch(`${api.url}/api/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${tokenDe('ana')}` },
      body: '{"name": "Informe",',
    });

    expect(malFormado.status).toBe(400);
    expect(proyectos.create).not.toHaveBeenCalled();
  });
});

describe('errores no controlados', () => {
  it('responden 500 con un mensaje generico, sin el detalle interno', async () => {
    proyectos.findManyForUser.mockRejectedValue(
      new Error('connect ECONNREFUSED 10.0.3.7:5432 (user=taskhub password=hunter2)'),
    );

    const res = await peticion(api.url, 'GET', '/api/projects', { token: tokenDe('ana') });

    expect(res.status).toBe(500);
    const texto = await res.text();
    expect(JSON.parse(texto)).toEqual({ message: 'Error interno del servidor' });
    // Ni la IP interna, ni la credencial, ni una traza.
    expect(texto).not.toContain('10.0.3.7');
    expect(texto).not.toContain('hunter2');
    expect(texto).not.toContain('at ');
  });

  it('una ruta que no existe responde 404 en JSON', async () => {
    const res = await peticion(api.url, 'GET', '/api/no-existe', { token: tokenDe('ana') });

    expect(res.status).toBe(404);
    expect(res.headers.get('content-type')).toContain('application/json');
  });
});
