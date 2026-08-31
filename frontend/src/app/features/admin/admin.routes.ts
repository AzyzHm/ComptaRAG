import { Routes } from '@angular/router';

import { roleGuard } from '@core/guards/role.guard';

export const ADMIN_ROUTES: Routes = [
  {
    path: 'users',
    canActivate: [roleGuard('ADMIN', 'SUPER_ADMIN')],
    loadComponent: () => import('./users/admin-users.component').then((m) => m.AdminUsersComponent)
  },
  { path: '', pathMatch: 'full', redirectTo: 'users' }
];
