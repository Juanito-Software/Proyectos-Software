// Envoltorio uniforme de respuesta, portado de TaskHub2.
// Todas las respuestas correctas de la API salen por aquí, y todas las de
// error por ApiResponse.error() desde error.middleware.ts. Así el cliente
// siempre puede mirar `success` sin depender del código HTTP.
export class ApiResponse {
  static success<T>(data: T, message?: string) {
    return {
      success: true as const,
      data,
      ...(message ? { message } : {}),
      timestamp: new Date().toISOString(),
    };
  }

  static error(message: string, details?: unknown) {
    return {
      success: false as const,
      error: message,
      ...(details !== undefined ? { details } : {}),
      timestamp: new Date().toISOString(),
    };
  }
}
