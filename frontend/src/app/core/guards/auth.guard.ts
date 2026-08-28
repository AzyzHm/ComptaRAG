import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from '@core/services/auth.service';

/**
 * Example route guard. Replace `AuthService.isAuthenticated()` with your
 * actual auth check (token presence, session validity, etc.).
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  return router.parseUrl('/');
};
