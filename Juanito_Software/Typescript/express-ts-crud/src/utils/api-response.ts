export class ApiResponse {
  public static success<T>(data: T, message?: string) {
    return {
      success: true,
      data,
      ...(message && { message }),
      timestamp: new Date().toISOString()
    };
  }

  public static error(message: string, details?: any) {
    return {
      success: false,
      error: message,
      ...(details && { details }),
      timestamp: new Date().toISOString()
    };
  }
}
