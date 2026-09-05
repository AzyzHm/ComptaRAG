import { Routes, UrlMatchResult, UrlSegment } from '@angular/router';

import { authGuard } from '@core/guards/auth.guard';

function chatRouteMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length === 0) {
    return { consumed: [] };
  }

  if (segments.length === 1) {
    return { consumed: segments, posParams: { chatId: segments[0] } };
  }

  return null;
}

export const CHAT_ROUTES: Routes = [
  {
    matcher: chatRouteMatcher,
    canActivate: [authGuard],
    loadComponent: () => import('./chat.component').then((m) => m.ChatComponent)
  }
];