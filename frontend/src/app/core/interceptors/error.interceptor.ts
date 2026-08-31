import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { AuthService } from '@core/services/auth.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((error: unknown) => {
      console.error('[HTTP Error]', error);

      if (error instanceof HttpErrorResponse && error.status === 401) {
        void authService.logout().finally(() => void router.navigate(['/login']));
      }

      return throwError(() => error);
    })
  );
};
