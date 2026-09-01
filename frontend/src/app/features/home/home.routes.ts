import { Routes } from '@angular/router';

import { guestGuard } from '@core/guards/auth.guard';

export const HOME_ROUTES: Routes = [
  {
    path: '',
    canActivate: [guestGuard],
    loadComponent: () => import('./home.component').then((m) => m.HomeComponent)
  }
];
