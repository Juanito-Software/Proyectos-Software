import { describe, it, expect } from 'vitest';
import { ApiError } from '../utils/ApiError';

describe('ApiError', () => {
  it('es una instancia de Error y conserva el stack trace', () => {
    const err = ApiError.badRequest('payload inválido');
    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.name).toBe('ApiError');
    expect(err.stack).toBeDefined();
  });

  it.each([
    ['badRequest', ApiError.badRequest('x'), 400],
    ['unauthorized', ApiError.unauthorized(), 401],
    ['forbidden', ApiError.forbidden(), 403],
    ['notFound', ApiError.notFound(), 404],
    ['conflict', ApiError.conflict('x'), 409],
  ])('%s produce statusCode %i', (_name, err, expected) => {
    expect((err as ApiError).statusCode).toBe(expected);
  });

  it('usa mensajes por defecto cuando no se pasa ninguno', () => {
    expect(ApiError.unauthorized().message).toBe('No autenticado');
    expect(ApiError.forbidden().message).toBe('No autorizado');
    expect(ApiError.notFound().message).toBe('Recurso no encontrado');
  });

  it('permite sobrescribir el mensaje por defecto', () => {
    expect(ApiError.notFound('Tarea no encontrada').message).toBe('Tarea no encontrada');
  });

  it('adjunta details cuando se proporcionan', () => {
    const details = [{ field: 'email', issue: 'formato inválido' }];
    const err = ApiError.badRequest('validación fallida', details);
    expect(err.details).toEqual(details);
  });

  it('deja details como undefined si no se pasa', () => {
    expect(ApiError.conflict('duplicado').details).toBeUndefined();
  });
});
