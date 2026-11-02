// Error de dominio uniforme para toda la API. Los controladores lo lanzan (o
// lo pasan a next()) y error.middleware.ts lo convierte en una respuesta HTTP
// consistente con el formato { error, details? } que ya espera el cliente.
export class ApiError extends Error {
  /** Código HTTP con el que se responderá. */
  public readonly statusCode: number;
  /** Información adicional para el cliente (p. ej. los fallos de validación por campo). */
  public readonly details?: unknown;

  /**
   * @param statusCode código HTTP de la respuesta
   * @param message    mensaje legible para el usuario; se envía tal cual
   * @param details    datos extra opcionales; se envían en `details`
   */
  constructor(statusCode: number, message: string, details?: unknown) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
    this.name = 'ApiError';
    Error.captureStackTrace(this, this.constructor);
  }

  // Atajos con el código HTTP ya fijado. Los mensajes por defecto son los
  // que ve el usuario si el llamador no da uno propio.

  /** 400: los datos de la petición no son válidos. */
  static badRequest(message: string, details?: unknown) {
    return new ApiError(400, message, details);
  }
  /** 401: falta la sesión o no es válida. */
  static unauthorized(message = 'No autenticado') {
    return new ApiError(401, message);
  }
  /** 403: hay sesión, pero no permiso para esta acción. */
  static forbidden(message = 'No autorizado') {
    return new ApiError(403, message);
  }
  /** 404: el recurso no existe (o no es del usuario, para no revelar que existe). */
  static notFound(message = 'Recurso no encontrado') {
    return new ApiError(404, message);
  }
  /** 409: choca con el estado actual (p. ej. nombre de usuario ya en uso). */
  static conflict(message: string) {
    return new ApiError(409, message);
  }
  /** 500: fallo del servidor que se quiere tratar como error controlado. */
  static internal(message = 'Error interno del servidor', details?: unknown) {
    return new ApiError(500, message, details);
  }
}
