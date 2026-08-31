import { Routes } from '@angular/router';

import { authGuard } from '@core/guards/auth.guard';

export const CHAT_ROUTES: Routes = [
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./chat.component').then((m) => m.ChatComponent)
  }
];
