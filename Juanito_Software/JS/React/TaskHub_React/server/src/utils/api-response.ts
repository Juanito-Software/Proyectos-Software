// Envoltorio uniforme de respuesta, portado de TaskHub2.
// Todas las respuestas correctas de la API salen por aquí, y todas las de
// error por ApiResponse.error() desde error.middleware.ts. Así el cliente
// siempre puede mirar `success` sin depender del código HTTP.
export class ApiResponse {
  /**
   * Cuerpo de una respuesta correcta.
   *
   * @param data    carga útil (la tarea, la lista, el usuario...)
   * @param message texto opcional para mostrar al usuario; si no se da, la
   *                clave `message` no aparece
   * @returns `{ success: true, data, message?, timestamp }`
   */
  static success<T>(data: T, message?: string) {
    return {
      success: true as const,
      data,
      ...(message ? { message } : {}),
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Cuerpo de una respuesta de error. Solo lo usa `errorHandler`.
   *
   * @param message mensaje del error, va en la clave `error`
   * @param details datos extra opcionales (p. ej. errores por campo)
   * @returns `{ success: false, error, details?, timestamp }`
   */
  static error(message: string, details?: unknown) {
    return {
      success: false as const,
      error: message,
      ...(details !== undefined ? { details } : {}),
      timestamp: new Date().toISOString(),
    };
  }
}
