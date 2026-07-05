// Error de dominio uniforme para toda la API. Los controladores lo lanzan
// y el middleware de errores (errorHandler) lo convierte en una respuesta HTTP.
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
}
