import { HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

/**
 * Centralized HTTP error handling. Extend this to surface toasts,
 * redirect on 401s, log to a monitoring service, etc.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: unknown) => {
      console.error('[HTTP Error]', error);
      return throwError(() => error);
    })
  );
};
