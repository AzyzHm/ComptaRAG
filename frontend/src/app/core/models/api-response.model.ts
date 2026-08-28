/**
 * Generic envelope for API responses. Adapt to match your backend's
 * actual response shape.
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  statusCode: number;
  message: string;
  details?: unknown;
}
