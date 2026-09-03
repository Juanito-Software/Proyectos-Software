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

describe('límites de longitud', () => {
  /**
   * Los añadió la auditoría: antes se aceptaba una descripción de 50 000
   * caracteres y una búsqueda de 5 000. El techo existía —el límite de 100 kB
   * del cuerpo— pero era un accidente, no una decisión.
   */

  const req = (body: unknown, query: unknown = {}) =>
    ({ body, query }) as unknown as Request;

  it('acepta una descripción de exactamente 5 000', () => {
    expect(createTaskValidator(req({ title: 'x', description: 'a'.repeat(5000) }))).toBeNull();
  });

  it('rechaza una de 5 001', () => {
    const errores = createTaskValidator(req({ title: 'x', description: 'a'.repeat(5001) }));
    expect(errores!.join(' ')).toMatch(/descripción.*5000|5000.*caracteres/i);
  });

  it('el límite también aplica al actualizar', () => {
    expect(updateTaskValidator(req({ description: 'a'.repeat(5001) }))).not.toBeNull();
  });

  it('acepta una búsqueda de exactamente 200', () => {
    expect(filterTasksValidator(req({}, { search: 'a'.repeat(200) }))).toBeNull();
  });

  it('rechaza una de 201', () => {
    // Importa más que la descripción: acaba en un ILIKE con comodines a los dos
    // lados, que no puede usar índice y recorre la tabla entera.
    const errores = filterTasksValidator(req({}, { search: 'a'.repeat(201) }));
    expect(errores!.join(' ')).toMatch(/búsqueda/i);
  });

  it('una búsqueda que no es texto no rompe el validador', () => {
    // Express entrega un array cuando el parámetro se repite en la URL.
    expect(() => filterTasksValidator(req({}, { search: ['a', 'b'] }))).not.toThrow();
  });

  it('el título sigue con su límite de 100', () => {
    expect(createTaskValidator(req({ title: 'a'.repeat(100) }))).toBeNull();
    expect(createTaskValidator(req({ title: 'a'.repeat(101) }))).not.toBeNull();
  });

  it('una descripción que no es texto se rechaza antes de medirla', () => {
    const errores = createTaskValidator(req({ title: 'x', description: 12345 }));
    expect(errores!.join(' ')).toMatch(/debe ser texto/i);
  });

  it('una descripción nula se admite: significa "sin descripción"', () => {
    expect(createTaskValidator(req({ title: 'x', description: null }))).toBeNull();
  });
});

describe('actualización: qué cuenta como "algo que cambiar"', () => {
  const req = (body: unknown) => ({ body }) as unknown as Request;

  it('un cuerpo vacío se rechaza con un mensaje que enumera los campos', () => {
    // Sin esto, un PATCH vacío llegaba al servicio y hacía un UPDATE sin
    // columnas: SQL inválido y un 500.
    const errores = updateTaskValidator(req({}));

    expect(errores!).toHaveLength(1);
    expect(errores![0]).toMatch(/title.*description.*status.*priority.*completed/);
  });

  it('sin cuerpo en absoluto se comporta igual', () => {
    expect(updateTaskValidator(req(undefined))).not.toBeNull();
  });

  it.each([
    ['solo title', { title: 'x' }],
    ['solo description', { description: 'x' }],
    ['solo status', { status: 'completed' }],
    ['solo priority', { priority: 'low' }],
    ['solo completed', { completed: true }],
  ])('%s basta', (_caso, body) => {
    expect(updateTaskValidator(req(body))).toBeNull();
  });

  it('un campo puesto a null cuenta como enviado', () => {
    // `description: null` es "bórrame la descripción", no "no mando nada".
    expect(updateTaskValidator(req({ description: null }))).toBeNull();
  });

  it('un título vacío se rechaza: no es lo mismo que no mandarlo', () => {
    expect(updateTaskValidator(req({ title: '   ' }))!.join(' ')).toMatch(/no puede estar vacío/i);
  });

  it('un título que no es texto se rechaza', () => {
    expect(updateTaskValidator(req({ title: 42 }))).not.toBeNull();
  });

  it('un título de 101 caracteres se rechaza también al actualizar', () => {
    expect(updateTaskValidator(req({ title: 'a'.repeat(101) }))).not.toBeNull();
  });

  it('acumula los errores de varios campos a la vez', () => {
    // El cliente los pinta todos juntos; devolver solo el primero obligaría a
    // corregir de uno en uno.
    const errores = updateTaskValidator(req({ title: '', status: 'inventado', completed: 'sí' }));

    expect(errores!.length).toBeGreaterThanOrEqual(3);
  });

  it('completed solo admite booleanos, no la cadena "true"', () => {
    expect(updateTaskValidator(req({ completed: 'true' }))).not.toBeNull();
    expect(updateTaskValidator(req({ completed: false }))).toBeNull();
  });
});
