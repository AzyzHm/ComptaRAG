import { HttpInterceptorFn } from '@angular/common/http';

/**
 * Attaches an auth token to outgoing requests, if one is present.
 * Replace the token source with your real storage strategy.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return next(req);
  }

  const authedRequest = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });

  return next(authedRequest);
};
