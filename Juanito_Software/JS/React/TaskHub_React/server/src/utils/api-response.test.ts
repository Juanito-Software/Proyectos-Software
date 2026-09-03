import { describe, it, expect } from 'vitest';
import { ApiResponse } from './api-response.js';

/**
 * El sobre en el que sale **todo** lo que responde la API.
 *
 * Es el contrato con el cliente: `services/api.js` abre este envoltorio en cada
 * petición y devuelve solo `data`. Si cambiara la forma —que `data` pasara a
 * llamarse `payload`, o que `success` desapareciera— la aplicación entera
 * dejaría de funcionar sin un solo error de compilación, porque el cliente es
 * JavaScript y no comparte tipos con el servidor.
 *
 * De ahí que merezca tests propios aunque el código sean doce líneas.
 */

describe('respuesta correcta', () => {
  it('lleva success:true, los datos y una marca de tiempo', () => {
    const sobre = ApiResponse.success({ id: '1', title: 'Comprar pan' });

    expect(sobre.success).toBe(true);
    expect(sobre.data).toEqual({ id: '1', title: 'Comprar pan' });
    expect(sobre.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T.*Z$/);
  });

  it('incluye el mensaje solo si se pasa', () => {
    expect(ApiResponse.success(null, 'Sesión iniciada')).toHaveProperty('message', 'Sesión iniciada');
    expect(ApiResponse.success(null)).not.toHaveProperty('message');
  });

  it.each([
    ['un array', [{ id: '1' }, { id: '2' }]],
    ['un array vacío', []],
    ['null', null],
    ['un número', 42],
    ['una cadena', 'hola'],
    ['false', false],
    ['cero', 0],
  ])('envuelve %s sin alterarlo', (_caso, datos) => {
    // `false` y `0` importan: un envoltorio escrito con `data || {}` los
    // convertiría en un objeto vacío y el cliente recibiría otra cosa.
    expect(ApiResponse.success(datos).data).toEqual(datos);
  });

  it('no añade campos que el cliente no espera', () => {
    expect(Object.keys(ApiResponse.success({ a: 1 })).sort()).toEqual(['data', 'success', 'timestamp']);
  });

  it('nunca lleva el campo error', () => {
    // El cliente decide por `success`, pero si un sobre correcto arrastrara un
    // `error` cualquier comprobación laxa lo tomaría por un fallo.
    expect(ApiResponse.success({ a: 1 })).not.toHaveProperty('error');
  });
});

describe('respuesta de error', () => {
  it('lleva success:false y el mensaje', () => {
    const sobre = ApiResponse.error('Tarea no encontrada');

    expect(sobre.success).toBe(false);
    expect(sobre.error).toBe('Tarea no encontrada');
    expect(sobre.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T.*Z$/);
  });

  it('incluye los detalles solo si se pasan', () => {
    expect(ApiResponse.error('Error de validación', ['a', 'b'])).toHaveProperty('details', ['a', 'b']);
    expect(ApiResponse.error('x')).not.toHaveProperty('details');
  });

  it('distingue "sin detalles" de "detalles vacíos"', () => {
    // `details: []` es información —la lista vino vacía—; ausencia es otra
    // cosa. Un `if (details)` los habría confundido.
    expect(ApiResponse.error('x', [])).toHaveProperty('details', []);
  });

  it('nunca lleva el campo data', () => {
    expect(ApiResponse.error('x')).not.toHaveProperty('data');
  });

  it('no añade campos inesperados', () => {
    expect(Object.keys(ApiResponse.error('x')).sort()).toEqual(['error', 'success', 'timestamp']);
  });
});

describe('los dos sobres son distinguibles', () => {
  it('success es true o false, nunca ausente', () => {
    // Es el campo del que depende el cliente para decidir, y lo mira antes que
    // el código HTTP.
    expect(ApiResponse.success(null).success).toBe(true);
    expect(ApiResponse.error('x').success).toBe(false);
  });

  it('la marca de tiempo es válida y reciente', () => {
    const momento = new Date(ApiResponse.success(null).timestamp).getTime();
    expect(Number.isNaN(momento)).toBe(false);
    expect(Math.abs(Date.now() - momento)).toBeLessThan(5_000);
  });

  it('los dos sobrescriben serialización a JSON sin perder nada', () => {
    const correcto = JSON.parse(JSON.stringify(ApiResponse.success({ n: 1 }, 'ok')));
    const fallido = JSON.parse(JSON.stringify(ApiResponse.error('mal', ['d'])));

    expect(correcto).toMatchObject({ success: true, data: { n: 1 }, message: 'ok' });
    expect(fallido).toMatchObject({ success: false, error: 'mal', details: ['d'] });
  });
});
