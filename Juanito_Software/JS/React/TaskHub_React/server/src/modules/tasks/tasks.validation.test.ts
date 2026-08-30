import { describe, it, expect } from 'vitest';
import type { Request } from 'express';
import { createTaskValidator, updateTaskValidator, filterTasksValidator } from './tasks.validation.js';

/**
 * Los validadores son la primera barrera de la API: deciden qué llega a la
 * capa de negocio. Probarlos aquí, sin levantar servidor ni base de datos,
 * permite cubrir muchos más casos límite de los que compensa recorrer por HTTP.
 */

// Los validadores solo leen body y query, así que basta con un objeto mínimo.
const req = (body: unknown = {}, query: unknown = {}) =>
  ({ body, query }) as unknown as Request;

describe('createTaskValidator', () => {
  it('acepta una tarea con solo el título', () => {
    expect(createTaskValidator(req({ title: 'Comprar pan' }))).toBeNull();
  });

  it('acepta todos los campos válidos a la vez', () => {
    const errores = createTaskValidator(
      req({ title: 'Tarea', description: 'Algo', status: 'in-progress', priority: 'high' }),
    );
    expect(errores).toBeNull();
  });

  it.each([
    ['sin título', {}],
    ['título vacío', { title: '' }],
    ['título de solo espacios', { title: '   ' }],
    ['título que no es texto', { title: 123 }],
    ['título nulo', { title: null }],
  ])('rechaza: %s', (_caso, body) => {
    expect(createTaskValidator(req(body))).not.toBeNull();
  });

  it('rechaza un estado que no existe', () => {
    const errores = createTaskValidator(req({ title: 'X', status: 'casi-hecho' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toContain('status');
  });

  it('rechaza una prioridad que no existe', () => {
    const errores = createTaskValidator(req({ title: 'X', priority: 'urgentísima' }));
    expect(errores).not.toBeNull();
    expect(errores!.join(' ')).toContain('priority');
  });

  it.each(['pending', 'in-progress', 'completed'])('acepta el estado válido %s', (status) => {
    expect(createTaskValidator(req({ title: 'X', status }))).toBeNull();
  });

  it.each(['low', 'medium', 'high'])('acepta la prioridad válida %s', (priority) => {
    expect(createTaskValidator(req({ title: 'X', priority }))).toBeNull();
  });

  it('no se rompe si el cuerpo llega indefinido', () => {
    expect(() => createTaskValidator(req(undefined))).not.toThrow();
  });
});

describe('updateTaskValidator', () => {
  it('acepta una actualización parcial de un solo campo', () => {
    expect(updateTaskValidator(req({ status: 'completed' }))).toBeNull();
  });

  it('acepta el campo completed del cliente antiguo', () => {
    expect(updateTaskValidator(req({ completed: true }))).toBeNull();
  });

  it('rechaza un título vacío si se manda explícitamente', () => {
    expect(updateTaskValidator(req({ title: '   ' }))).not.toBeNull();
  });

  it('rechaza un estado inválido igual que al crear', () => {
    expect(updateTaskValidator(req({ status: 'inventado' }))).not.toBeNull();
  });
});

describe('filterTasksValidator', () => {
  it('acepta que no haya ningún filtro', () => {
    expect(filterTasksValidator(req({}, {}))).toBeNull();
  });

  it('acepta los tres filtros a la vez', () => {
    expect(
      filterTasksValidator(req({}, { status: 'pending', priority: 'low', search: 'pan' })),
    ).toBeNull();
  });

  it('rechaza un estado inventado en la cadena de consulta', () => {
    expect(filterTasksValidator(req({}, { status: 'inventado' }))).not.toBeNull();
  });

  it('rechaza una prioridad inventada en la cadena de consulta', () => {
    expect(filterTasksValidator(req({}, { priority: 'altísima' }))).not.toBeNull();
  });

  it('acepta cualquier texto de búsqueda, incluidos caracteres SQL', () => {
    // La búsqueda no se restringe: el repositorio la parametriza y escapa los
    // comodines. Rechazar comillas aquí impediría buscar textos legítimos.
    expect(filterTasksValidator(req({}, { search: "'; DROP TABLE tasks; --" }))).toBeNull();
  });
});
