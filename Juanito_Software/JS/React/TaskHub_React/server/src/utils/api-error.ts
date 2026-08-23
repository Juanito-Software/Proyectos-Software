// Error de dominio uniforme para toda la API. Los controladores lo lanzan (o
// lo pasan a next()) y error.middleware.ts lo convierte en una respuesta HTTP
// consistente con el formato { error, details? } que ya espera el cliente.
export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly details?: unknown;

  constructor(statusCode: number, message: string, details?: unknown) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
    this.name = 'ApiError';
    Error.captureStackTrace(this, this.constructor);
  }

  static badRequest(message: string, details?: unknown) {
    return new ApiError(400, message, details);
  }
  static unauthorized(message = 'No autenticado') {
    return new ApiError(401, message);
  }
  static forbidden(message = 'No autorizado') {
    return new ApiError(403, message);
  }
  static notFound(message = 'Recurso no encontrado') {
    return new ApiError(404, message);
  }
  static conflict(message: string) {
    return new ApiError(409, message);
  }
  static internal(message = 'Error interno del servidor', details?: unknown) {
    return new ApiError(500, message, details);
  }
}
