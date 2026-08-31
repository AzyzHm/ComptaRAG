import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { from, switchMap } from 'rxjs';

import { environment } from '@env/environment';
import { AuthService } from '@core/services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.startsWith(environment.apiBaseUrl)) {
    return next(req);
  }

  const authService = inject(AuthService);

  return from(authService.getIdToken()).pipe(
    switchMap((token) => {
      if (!token) {
        return next(req);
      }
      return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
    })
  );
};
