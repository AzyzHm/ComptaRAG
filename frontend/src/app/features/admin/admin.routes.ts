import { Routes } from '@angular/router';

import { roleGuard } from '@core/guards/role.guard';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    canActivate: [roleGuard('ADMIN', 'SUPER_ADMIN')],
    loadComponent: () =>
      import('./admin-shell/admin-shell.component').then((m) => m.AdminShellComponent),
    children: [
      {
        path: 'users',
        loadComponent: () =>
          import('./users/admin-users.component').then((m) => m.AdminUsersComponent)
      },
      {
        path: 'logins',
        loadComponent: () =>
          import('./logins/admin-logins.component').then((m) => m.AdminLoginsComponent)
      },
      {
        path: 'usage',
        loadComponent: () =>
          import('./usage/admin-usage.component').then((m) => m.AdminUsageComponent)
      },
      { path: '', pathMatch: 'full', redirectTo: 'users' }
    ]
  }
];
