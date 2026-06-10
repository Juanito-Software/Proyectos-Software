export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly success: boolean = false;
  public readonly details: any;

  constructor(statusCode: number, message: string, details?: any) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
    Object.setPrototypeOf(this, new.target.prototype); // restore prototype chain
    Error.captureStackTrace(this, this.constructor);
  }

  public static badRequest(message: string, details?: any): ApiError {
    return new ApiError(400, message, details);
  }

  public static unauthorized(message: string): ApiError {
    return new ApiError(401, message);
  }

  public static forbidden(message: string): ApiError {
    return new ApiError(403, message);
  }

  public static notFound(message: string): ApiError {
    return new ApiError(404, message);
  }

  public static internal(message: string, details?: any): ApiError {
    return new ApiError(500, message, details);
  }
}
