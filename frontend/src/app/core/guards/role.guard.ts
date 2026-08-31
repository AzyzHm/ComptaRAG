import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from '@core/services/auth.service';
import { Role } from '@core/models/user.model';

export function roleGuard(...roles: Role[]): CanActivateFn {
  return async () => {
    const authService = inject(AuthService);
    const router = inject(Router);

    await authService.ready;

    if (!authService.isAuthenticated()) {
      return router.parseUrl('/login');
    }

    const role = authService.role();
    if (role && roles.includes(role)) {
      return true;
    }

    return router.parseUrl('/');
  };
}
