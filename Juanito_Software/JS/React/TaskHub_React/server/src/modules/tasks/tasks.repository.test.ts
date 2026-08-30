import { describe, it, expect } from 'vitest';
import { escapeLikePattern, toDto } from './tasks.repository.js';
import type { Task } from './tasks.types.js';

/**
 * Dos funciones puras del repositorio que se pueden probar sin base de datos.
 *
 * `escapeLikePattern` merece especial atención: su ausencia era un bug real
 * (buscar "%" devolvía todas las tareas) que solo se descubrió al escribir un
 * test de regresión de inyección SQL.
 */

describe('escapeLikePattern', () => {
  it('deja intacto el texto normal', () => {
    expect(escapeLikePattern('comprar pan')).toBe('comprar pan');
  });

  it('escapa el comodín % para que se busque literalmente', () => {
    // Sin esto, buscar "50%" devolvía cualquier texto que empezara por 50.
    expect(escapeLikePattern('50%')).toBe('50\\%');
  });

  it('escapa el comodín _ de un solo carácter', () => {
    expect(escapeLikePattern('nombre_archivo')).toBe('nombre\\_archivo');
  });

  it('escapa la barra invertida ANTES que los comodines', () => {
    // El orden importa: si se escaparan primero % y _, la barra que se acaba
    // de añadir se volvería a escapar y el patrón quedaría roto.
    expect(escapeLikePattern('c:\\ruta')).toBe('c:\\\\ruta');
  });

  it('escapa varios comodines a la vez', () => {
    expect(escapeLikePattern('%_%')).toBe('\\%\\_\\%');
  });

  it('una búsqueda de solo % deja de significar "todo"', () => {
    expect(escapeLikePattern('%')).toBe('\\%');
  });

  it('no altera comillas ni punto y coma: de eso se encarga la parametrización', () => {
    const carga = "'; DROP TABLE tasks; --";
    expect(escapeLikePattern(carga)).toBe(carga);
  });

  it('devuelve cadena vacía tal cual', () => {
    expect(escapeLikePattern('')).toBe('');
  });
});

describe('toDto: campo calculado completed', () => {
  const base: Task = {
    id: 'abc',
    title: 'Tarea',
    description: '',
    status: 'pending',
    priority: 'medium',
    userId: 'u1',
    createdAt: '2026-01-01T00:00:00.000Z',
    updatedAt: '2026-01-01T00:00:00.000Z',
  };

  it('completed es true solo cuando el estado es completed', () => {
    expect(toDto({ ...base, status: 'completed' }).completed).toBe(true);
  });

  it('pending da completed false', () => {
    expect(toDto({ ...base, status: 'pending' }).completed).toBe(false);
  });

  it('in-progress da completed false, no true', () => {
    // Este es el caso que rompería el checkbox del cliente si se tratara el
    // estado intermedio como "hecho".
    expect(toDto({ ...base, status: 'in-progress' }).completed).toBe(false);
  });

  it('conserva todos los campos originales', () => {
    const dto = toDto(base);
    expect(dto).toMatchObject(base);
  });

  it('no añade nada más que completed', () => {
    const dto = toDto(base);
    const claves = Object.keys(dto).filter((k) => !(k in base));
    expect(claves).toEqual(['completed']);
  });
});
